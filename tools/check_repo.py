"""Checks the mod's files before publishing. Needs no game DLLs.

  - the csproj values that go into info.json are valid: <Tags> is a JSON array of
    strings and <JSONLoadOrder> a whole number (the build checks this too)
  - source/assets/steam description.txt has a [h3]Changelog[/h3] whose first line is the
    csproj <Version> (a 1.0.0 mod may have no changelog yet)
  - that line fits the Workshop change-note box (100 characters after "- ")
  - the changelog is newest first and keeps only the newest 5 entries plus every major
    version (1.0.0, 2.0.0, ...)
  - the description has no double quote, which SteamCMD can't upload

Usage:
    python tools/check_repo.py
"""

import glob
import json
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MOD_DIR = os.path.join(REPO, "source")
CHANGELOG_HEADING = "[h3]Changelog[/h3]"
CHANGELOG_LIMIT = 100  # the Workshop change-note box cuts off after this many characters
CHANGELOG_RECENT = 5  # the changelog keeps this many newest entries, plus every major version
CHANGELOG_LINE_RE = re.compile(r"^- (\d+)\.(\d+)\.(\d+): ")


def read_csproj(mod_dir, optional=()):
    """Returns (csproj path, props). <ModName> and <Version> are required; names in optional are None if missing."""
    projects = glob.glob(os.path.join(mod_dir, "*.csproj"))
    if len(projects) != 1:
        sys.exit("Expected one .csproj in " + mod_dir)
    with open(projects[0], encoding="utf-8-sig") as f:
        text = f.read()
    props = {}
    for name in ("ModName", "Version") + tuple(optional):
        match = re.search(r"<{0}>([^<]+)</{0}>".format(name), text)
        if not match and name in ("ModName", "Version"):
            sys.exit("No <{}> in {}".format(name, projects[0]))
        props[name] = match.group(1).strip() if match else None
    return projects[0], props


def changelog_version(line):
    """Returns (major, minor, patch) of a "- <version>: ..." changelog line, or None."""
    match = CHANGELOG_LINE_RE.match(line)
    return tuple(int(g) for g in match.groups()) if match else None


def is_major(version):
    """1.0.0, 2.0.0, ...; 0.x versions are pre-release, not major versions."""
    return version[0] >= 1 and version[1:] == (0, 0)


def trim_changelog(lines):
    """Sorts changelog lines newest first and keeps the newest CHANGELOG_RECENT plus every major version."""
    ordered = sorted(lines, key=changelog_version, reverse=True)
    return [line for i, line in enumerate(ordered) if i < CHANGELOG_RECENT or is_major(changelog_version(line))]


def check_mod(mod_dir):
    problems = []
    _, props = read_csproj(mod_dir, optional=("Tags", "JSONLoadOrder"))
    try:
        tags = json.loads(props["Tags"] or "")
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError
    except ValueError:
        problems.append("<Tags> is not a JSON array of strings: {}".format(props["Tags"]))
    if not re.fullmatch(r"[+-]?\d+", props["JSONLoadOrder"] or ""):
        problems.append("<JSONLoadOrder> is not a whole number: {}".format(props["JSONLoadOrder"]))

    assets = os.path.join(mod_dir, "assets")
    names = [n for n in os.listdir(assets) if n.lower() == "steam description.txt"]
    if not names:
        return problems + ["no assets/steam description.txt"]
    with open(os.path.join(assets, names[0]), encoding="utf-8-sig") as f:
        description = f.read().replace("\r\n", "\n")
    if '"' in description:
        problems.append("steam description.txt has a double quote; SteamCMD can't upload it")
    _, found, changelog = description.partition(CHANGELOG_HEADING)
    if not found:
        if props["Version"] != "1.0.0":
            problems.append("no {} in steam description.txt".format(CHANGELOG_HEADING))
        return problems
    lines = [line for line in changelog.strip().split("\n") if line.strip()]
    bad = [line for line in lines if not changelog_version(line)]
    if bad:
        return problems + ["changelog line is not '- <version>: ...': " + bad[0]]
    first = lines[0] if lines else ""
    if not first.startswith("- {}: ".format(props["Version"])):
        problems.append("first changelog line is not version {}: {}".format(props["Version"], first))
    elif len(first) - 2 > CHANGELOG_LIMIT:
        problems.append("changelog line over {} characters: {}".format(CHANGELOG_LIMIT, first))
    if lines != trim_changelog(lines):
        problems.append("changelog must be newest first with only the newest 5 entries plus major versions")
    return problems


def main():
    problems = check_mod(MOD_DIR)
    for problem in problems:
        print(problem)
    if problems:
        sys.exit(1)
    print("Mod OK.")


if __name__ == "__main__":
    main()
