"""Checks the mod's files before publishing. Needs no game DLLs.

  - the csproj values that go into info.json are valid: <Tags> is a JSON array of
    strings and <JSONLoadOrder> a whole number (the build checks this too)
  - source/assets/steam description.txt has a [h3]Changelog[/h3] line for the csproj
    <Version> (a 1.0.0 mod may have no changelog yet)
  - that line fits the Workshop change-note box (100 characters after "- ")
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
CHANGELOG_LIMIT = 100  # the Workshop change-note box cuts off after this many characters


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
    _, found, changelog = description.partition("[h3]Changelog[/h3]")
    if not found:
        if props["Version"] != "1.0.0":
            problems.append("no [h3]Changelog[/h3] in steam description.txt")
        return problems
    match = re.search(r"^- {}: .*$".format(re.escape(props["Version"])), changelog, re.M)
    if not match:
        problems.append("no changelog line for version " + props["Version"])
    elif len(match.group(0)) - 2 > CHANGELOG_LIMIT:
        problems.append("changelog line over {} characters: {}".format(CHANGELOG_LIMIT, match.group(0)))
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
