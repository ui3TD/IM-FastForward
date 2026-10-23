"""Build the mod and publish it to its Steam Workshop item.

Uploads the content, title, full description and change note in one step with
SteamCMD, so nothing is copy-pasted and the game does not need to be open:

    title       <ModName> from source/*.csproj
    description source/assets/steam description.txt (BBCode, as shown on Steam)
    change note the "- <Version>: ..." line under [h3]Changelog[/h3] in that file
    content     a Release build in a clean staging folder (%TEMP%/<repo folder>-workshop/<ModName>),
                never the game's Mods folder, which may hold a Debug build or stale assets
    preview     thumb.png in that folder

With --description-only, only the title and description are updated: nothing is
built, and the content, preview and change note on Steam stay as they are.

Publishing is refused unless the mod's files are committed and pushed to GitHub,
so the Workshop always matches the published source.

The Workshop item is the csproj's <WorkshopID>. With --new, a mod with no
<WorkshopID> yet is published as a new item, unlisted, and the new item's id is
written into the csproj (commit that change). SteamCMD can't set tags, so add
them on the item's page. After uploading, the item is read back from the public
Steam Web API and its description compared with the local one.

One-time setup: install SteamCMD (default C:\\steamcmd\\steamcmd.exe, or set
STEAMCMD) and log in once with `steamcmd +login <user> +quit` to cache the
Steam Guard approval. Without --user or STEAM_USER, the one account SteamCMD
has cached is used.

Usage:
    python tools/publish_workshop.py [--user USER] [--description-only] [--new] [--dry-run]
"""

import argparse
import getpass
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

from check_repo import MOD_DIR, REPO, check_mod, read_csproj

APP_ID = "821880"
STAGING = os.path.join(tempfile.gettempdir(), os.path.basename(REPO) + "-workshop")
# Files outside the mod's folder that go into its build.
SHARED_PATHS = ["Directory.Build.props", "Mod.BeforeSdk.targets", "NuGet.Config"]
DEFAULT_STEAMCMD = os.environ.get("STEAMCMD", r"C:\steamcmd\steamcmd.exe")
DETAILS_API = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"

# Steam Workshop limits.
MAX_TITLE = 128
MAX_DESCRIPTION = 8000

# SteamCMD's visibility values: 0 public, 1 friends only, 2 private, 3 unlisted.
UNLISTED = "3"


def read_props(new=False):
    csproj, props = read_csproj(MOD_DIR, optional=("WorkshopID",))
    if new and props["WorkshopID"]:
        sys.exit("{} already has <WorkshopID> {}; publish without --new.".format(csproj, props["WorkshopID"]))
    if not new and not props["WorkshopID"]:
        sys.exit("No <WorkshopID> in {}. For a mod that is already on the Workshop, add the id from its "
                 "Workshop URL; for a first upload, use --new. (FastForward itself is published from "
                 "Tel-Mod-Library, so don't publish it from this repo.)".format(csproj))
    return csproj, props


def created_id(vdf_path):
    """The id SteamCMD writes back into the VDF after creating an item; None if it didn't."""
    with open(vdf_path, encoding="utf-8", errors="replace") as f:
        match = re.search(r'"publishedfileid"\s+"(\d+)"', f.read())
    return match.group(1) if match and match.group(1) != "0" else None


def write_workshop_id(csproj, workshop_id):
    """Writes the id into an empty <WorkshopID>, or adds the property after <Version>."""
    with open(csproj, encoding="utf-8-sig") as f:
        text = f.read()
    tag = "<WorkshopID>{}</WorkshopID>".format(workshop_id)
    updated, count = re.subn(r"<WorkshopID>\s*</WorkshopID>|<WorkshopID\s*/>", tag, text)
    if count == 0:
        updated, count = re.subn(r"^([ \t]*)(<Version>[^<]*</Version>)(\r?\n)", r"\1\2\3\1" + tag + r"\3", text, count=1, flags=re.M)
    if count != 1:
        sys.exit("Couldn't write {} into {}; add it by hand.".format(tag, csproj))
    with open(csproj, "w", encoding="utf-8", newline="") as f:
        f.write(updated)


def read_description():
    assets = os.path.join(MOD_DIR, "assets")
    names = [n for n in os.listdir(assets) if n.lower() == "steam description.txt"]
    if not names:
        sys.exit("No steam description.txt in " + assets)
    with open(os.path.join(assets, names[0]), encoding="utf-8-sig") as f:
        return f.read().replace("\r\n", "\n").strip()


def change_note(description, version):
    _, found, changelog = description.partition("[h3]Changelog[/h3]")
    if not found:
        sys.exit("No [h3]Changelog[/h3] section in the steam description.")
    match = re.search(r"^- {}:\s*(.+)$".format(re.escape(version)), changelog, re.MULTILINE)
    if not match:
        sys.exit("No '- {}: ...' line in the changelog; add one before publishing.".format(version))
    return match.group(1).strip()


def clean_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)


def build(csproj, out_dir):
    """Builds in Release and deploys into out_dir instead of the game's Mods folder."""
    # ModOutputDir is a global property here, so it overrides Directory.Build.props.
    subprocess.run(["dotnet", "build", csproj, "-c", "Release", "-nologo", "-p:ModOutputDir=" + out_dir], check=True)


def check_built(props, out_dir):
    """Exits unless out_dir/<ModName> holds the csproj's version, its DLL, every asset and thumb.png. Returns that folder."""
    built = os.path.join(out_dir, props["ModName"])
    info_path = os.path.join(built, "info.json")
    if not os.path.isfile(info_path):
        sys.exit("Build did not produce " + info_path)
    with open(info_path, encoding="utf-8-sig") as f:
        info = json.load(f)
    if info.get("Version") != props["Version"]:
        sys.exit("info.json is version {}, csproj is {}.".format(info.get("Version"), props["Version"]))
    dll = os.path.join(built, info["HarmonyID"] + ".dll")
    if not os.path.isfile(dll):
        sys.exit("No DLL at " + dll)
    assets = os.path.join(MOD_DIR, "assets")
    for root, _, files in os.walk(assets):
        for name in files:
            rel = os.path.relpath(os.path.join(root, name), assets)
            if not os.path.isfile(os.path.join(built, rel)):
                sys.exit("Asset {} missing from the build".format(rel))
    if not os.path.isfile(os.path.join(built, "thumb.png")):
        sys.exit("No thumb.png in " + built)
    check_machine_neutral(built)
    return built


def check_machine_neutral(folder):
    """Exits if any file under folder holds this PC's user name, which would publish it."""
    user = getpass.getuser()
    pattern = re.compile(r"(?<![A-Za-z]){}(?![A-Za-z])".format(re.escape(user)).encode(), re.IGNORECASE)
    wide = [s.encode("utf-16-le") for s in (user, user.lower(), user.capitalize())]
    for root, _, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)
            with open(path, "rb") as f:
                data = f.read()
            if pattern.search(data) or any(w in data for w in wide):
                sys.exit("{} holds data specific to this PC; refusing to publish it.".format(path))


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), check=True, capture_output=True, text=True).stdout.strip()


def check_pushed(paths):
    """Exits unless paths are committed and HEAD is on GitHub."""
    if git("status", "--porcelain", "--", *paths):
        sys.exit("Uncommitted changes in {}; commit and push them first.".format(", ".join(paths)))
    git("fetch", "--quiet", "origin")
    if not git("branch", "-r", "--contains", "HEAD"):
        sys.exit("HEAD is not pushed to origin; push it first.")


def vdf_string(value):
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def write_vdf(fields):
    lines = ['"workshopitem"', "{"]
    lines += ["\t{} {}".format(vdf_string(k), vdf_string(v)) for k, v in fields.items()]
    lines.append("}")
    fd, path = tempfile.mkstemp(suffix=".vdf", prefix="workshop_")
    with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return path, "\n".join(lines)


def cached_user(steamcmd):
    """The account SteamCMD has a cached login for, if it has exactly one."""
    try:
        with open(os.path.join(os.path.dirname(steamcmd), "config", "config.vdf"), encoding="utf-8", errors="replace") as f:
            text = f.read()
    except OSError:
        return None
    block = re.search(r'"Accounts"\s*\{(.*?)\n\t*\}', text, re.S)
    names = re.findall(r'^\s*"([^"]+)"\s*\n\s*\{', block.group(1), re.M) if block else []
    return names[0] if len(names) == 1 else None


def upload(steamcmd, user, vdf_path):
    if not os.path.isfile(steamcmd):
        sys.exit("SteamCMD not found at {}; install it or set STEAMCMD.".format(steamcmd))
    # stdin stays attached so SteamCMD can ask for a password or Steam Guard code if the login has expired.
    proc = subprocess.Popen([steamcmd, "+login", user, "+workshop_build_item", vdf_path, "+quit"],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, errors="replace")
    assert proc.stdout is not None
    output = []
    for line in proc.stdout:
        print(line, end="")
        output.append(line)
    proc.wait()
    text = "".join(output)
    if "ERROR" in text or "Success." not in text:
        sys.exit("SteamCMD did not report success; the Workshop item may not have been updated.")


def fetch_details(workshop_id):
    """The Workshop item's details from the public Steam Web API (result 1 = found)."""
    data = urllib.parse.urlencode({"itemcount": 1, "publishedfileids[0]": workshop_id}).encode()
    with urllib.request.urlopen(DETAILS_API, data, timeout=30) as response:
        return json.load(response)["response"]["publishedfiledetails"][0]


def verify(workshop_id, title, description):
    # The public API can lag the upload by a few seconds.
    details = {}
    for _ in range(3):
        try:
            details = fetch_details(workshop_id)
        except Exception as e:
            print("Could not read the item back from Steam ({}); check the page manually.".format(e))
            return
        remote = details.get("description", "").replace("\r\n", "\n").strip()
        if remote == description and details.get("title") == title:
            print("Verified: Steam shows the new title and description.")
            return
        time.sleep(5)
    if details.get("result") != 1:
        print("Steam did not return the item (an unlisted or private item isn't public); check the page manually.")
    else:
        print("WARNING: Steam's title or description differs from the local one; check the page.")


def main():
    parser = argparse.ArgumentParser(description=(__doc__ or "").partition("\n")[0])
    parser.add_argument("--user", default=os.environ.get("STEAM_USER"), help="Steam login (default: STEAM_USER)")
    parser.add_argument("--steamcmd", default=DEFAULT_STEAMCMD)
    parser.add_argument("--dry-run", action="store_true", help="print the upload instead of running it")
    parser.add_argument("--description-only", action="store_true",
                        help="update only the title and description; no build, content, preview or change note")
    parser.add_argument("--new", action="store_true",
                        help="publish a mod with no <WorkshopID> as a new, unlisted item and write its id into the csproj")
    args = parser.parse_args()
    if args.new and args.description_only:
        sys.exit("--new publishes everything; it can't be combined with --description-only.")

    csproj, props = read_props(args.new)
    problems = check_mod(MOD_DIR)
    if problems:
        sys.exit("Fix these first:\n" + "\n".join(problems))
    description = read_description()
    note = None if args.description_only else change_note(description, props["Version"])
    if len(props["ModName"]) > MAX_TITLE:
        sys.exit("Title is over {} characters.".format(MAX_TITLE))
    if len(description) > MAX_DESCRIPTION:
        sys.exit("Description is {} characters; Steam allows {}.".format(len(description), MAX_DESCRIPTION))

    # Check before building so a build isn't wasted; a dry run only warns.
    try:
        check_pushed([os.path.relpath(MOD_DIR, REPO)] + SHARED_PATHS)
    except SystemExit as e:
        if not args.dry_run:
            raise
        print("WARNING: " + str(e))
    fields = {
        "appid": APP_ID,
        "publishedfileid": "0" if args.new else props["WorkshopID"],
        "title": props["ModName"],
        "description": description,
    }
    if args.new:
        fields["visibility"] = UNLISTED
    if not args.description_only:
        # Start clean so files removed from the mod's assets don't linger.
        clean_dir(STAGING)
        build(csproj, STAGING)
        content_dir = check_built(props, STAGING)
        # Forward slashes keep paths free of VDF escapes; Windows accepts them.
        fields["contentfolder"] = content_dir.replace("\\", "/")
        fields["previewfile"] = os.path.join(content_dir, "thumb.png").replace("\\", "/")
        fields["changenote"] = "{}: {}".format(props["Version"], note)

    vdf_path, vdf_text = write_vdf(fields)
    try:
        what = "the description of" if args.description_only else props["Version"] + " of"
        if args.new:
            print("Publishing {} {} as a new, unlisted Workshop item".format(what, props["ModName"]))
        else:
            print("Publishing {} {} to https://steamcommunity.com/sharedfiles/filedetails/?id={}".format(
                what, props["ModName"], props["WorkshopID"]))
        if args.dry_run:
            print(vdf_text)
            return
        user = args.user or cached_user(args.steamcmd)
        if not user:
            sys.exit("No Steam login; pass --user or set STEAM_USER.")
        upload(args.steamcmd, user, vdf_path)
        if args.new:
            workshop_id = created_id(vdf_path)
            if not workshop_id:
                sys.exit("SteamCMD didn't report the new item's id; find it under your Workshop items and add it to the csproj.")
            write_workshop_id(csproj, workshop_id)
            props["WorkshopID"] = workshop_id
            print("Created https://steamcommunity.com/sharedfiles/filedetails/?id={} (unlisted); "
                  "wrote <WorkshopID> into {}. Commit it, and add the tags on the item's page.".format(workshop_id, csproj))
    finally:
        os.remove(vdf_path)
    verify(props["WorkshopID"], props["ModName"], description)


if __name__ == "__main__":
    main()
