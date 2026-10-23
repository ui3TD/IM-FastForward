"""Run FastForward's in-game tests with IM-InGameTests.

Builds the mod in Release (which puts it in the game's Mods folder) and this test project
(which puts it next to the runner plugin), then runs IM-InGameTests' run_ingame_tests.py with
only this mod loaded and in scope. The game opens, runs the tests and closes by itself; keep
Steam running. Every argument is passed to the runner.

    python tests/InGameTests.FastForward/run.py
    python tests/InGameTests.FastForward/run.py --allow-input --sound   # watch and listen

Needs IM-InGameTests next to this repo, or its folder in the IM_INGAMETESTS environment variable.
"""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
RUNNER = Path(os.environ.get("IM_INGAMETESTS", REPO.parent / "IM-InGameTests")) / "run_ingame_tests.py"

# The mod under test: its folder name in the game's Mods folder, and its HarmonyID.
MOD_FOLDER = "FastForward"
HARMONY_ID = "com.tel.fastforward"


def find_game_dir():
    """The game folder, found by the runner script from your Steam libraries."""
    spec = importlib.util.spec_from_file_location("run_ingame_tests", RUNNER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.find_game_dir()


def build(project: Path, *props: str) -> bool:
    print(f"Building {project.name} ...", flush=True)
    result = subprocess.run(["dotnet", "build", str(project), "-c", "Release", "-nologo", "-v", "q", *props],
                            capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout[-4000:], result.stderr[-2000:])
    return result.returncode == 0


def main() -> int:
    if not RUNNER.is_file():
        print(f"IM-InGameTests not found at {RUNNER.parent}; clone it next to this repo or set IM_INGAMETESTS.")
        return 2
    game_dir = find_game_dir()
    if game_dir is None:
        print("Idol Manager not found.")
        return 2

    if not build(REPO / "source" / "FastForward.csproj"):
        return 2
    if not build(HERE / "InGameTests.FastForward.csproj", f"-p:GameDir={game_dir}"):
        return 2
    return subprocess.call([sys.executable, str(RUNNER), "--load", MOD_FOLDER, "--scope", HARMONY_ID, *sys.argv[1:]])


if __name__ == "__main__":
    sys.exit(main())
