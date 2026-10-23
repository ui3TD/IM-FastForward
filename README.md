<p align="center">
  <img src="readme assets/header.jpg?raw=true" />
</p>

# IM-FastForward

FastForward is a small mod for Idol Manager. Press `4`, or click the fast-forward button a second time, and
time runs 5 times faster than the game's fast speed. With the [ModMenus](https://steamcommunity.com/sharedfiles/filedetails/?id=3283314791)
mod installed, a slider sets the speed from 1x to 20x.

This repo is a starting point for writing your own Harmony mods for Idol Manager with
[IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration). It has the mod, a build setup that
deploys straight to the game, and unit tests. [Tel-Mod-Library](https://github.com/ui3TD/Tel-Mod-Library)
uses the same setup for many more mods, so look there for bigger examples.

## What you need

- Idol Manager with [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration) installed.
- The [.NET SDK](https://dotnet.microsoft.com/download) (version 8 or later). It builds the mod for the
  game's .NET Framework 4.6 without installing that framework.
- An editor: [Visual Studio Community](https://visualstudio.microsoft.com/vs/community/), or
  [VS Code](https://code.visualstudio.com/) with the C# Dev Kit extension.

## Set up

1. Clone the repo:
   ```bash
   git clone https://github.com/ui3TD/IM-FastForward
   ```
2. Make a folder called `dll` next to the `IM-FastForward` folder, and copy these files into it from the
   game's folder (in Steam, right-click Idol Manager, then Manage > Browse local files).

   | File | Where it is in the game's folder | Needed for |
   |---|---|---|
   | `Assembly-CSharp.dll` | `IM_Data\Managed` | Building the mod and the tests |
   | `Assembly-CSharp-firstpass.dll` | `IM_Data\Managed` | Building the mod and the tests |
   | `UnityEngine.UI.dll` | `IM_Data\Managed` | Building the mod and the tests |
   | `Unity.TextMeshPro.dll` | `IM_Data\Managed` | Building the mod and the tests |
   | `DOTween.dll` | `IM_Data\Managed` | Building the mod and the tests |
   | `0Harmony.dll` | `BepInEx\core` | Building the mod and the tests |
   | `MonoMod.Utils.dll` | `BepInEx\core` | The tests only |
   | `MonoMod.RuntimeDetour.dll` | `BepInEx\core` | The tests only |
   | `Mono.Cecil.dll` | `BepInEx\core` | The tests only |
   | `UnityEngine.CoreModule.dll` | `UnstrippedLibs` (not `IM_Data\Managed`, whose copy is missing code the tests run) | The tests only |
   | `UnityEngine.SharedInternalsModule.dll` | `UnstrippedLibs` | The tests only |
   | `UnityEngine.InputLegacyModule.dll` | `IM_Data\Managed` | The tests only |
   | `UnityEngine.UnityWebRequestModule.dll` | `IM_Data\Managed` | The tests only |
   | `Unity.ResourceManager.dll` | `IM_Data\Managed` | The tests only |
   | `Steamworks.NET.dll` | `IM_Data\Managed` | The tests only |

   To keep the DLLs somewhere else, set the environment variable `IDOL_MANAGER_GAME_DLLS` to that folder.
   Never commit these DLLs: they belong to the game.

## Build

```bash
dotnet build source/FastForward.csproj -c Release
```

The build puts the mod straight into the game's Mods folder,
`%USERPROFILE%\AppData\LocalLow\Glitch Pitch\Idol Manager\Mods\FastForward\`:

- `com.tel.fastforward.dll`, the compiled mod. IM-HarmonyIntegration loads the DLL named after the mod's
  HarmonyID.
- everything in `source/assets/`, with its subfolders;
- `info.json`, written from the values in `FastForward.csproj`.

Start the game, turn the mod on in the Mods screen, and load a save.

Build options:

- `-p:DeployToGame=false` builds without copying anything into the game.
- `-p:ModOutputDir=<folder>` deploys to another folder instead of the game's Mods folder.
- `-c Debug` builds without treating warnings as errors. Release builds stop on any warning, because they
  are the ones you publish.

To see log messages while the game runs, open `BepInEx\config\BepInEx.cfg` in the game's folder and set
`Enabled = true` under `[Logging.Console]`. A console window opens with the game, and it shows messages
from Harmony, IM-HarmonyIntegration and anything your mod writes with `Debug.Log`. The same messages are
saved to `BepInEx\LogOutput.log`.

## How the mod works

All the code is in `source/FastForward.cs`. It has two Harmony patches. Each one is a class with a
`[HarmonyPatch]` attribute that names the game's class and method:

```csharp
[HarmonyPatch(typeof(TimeControlButton), nameof(TimeControlButton.OnClick))]
public class TimeControlButton_OnClick
```

`nameof` turns the method's name into text. If the game renamed the method, the build would fail instead
of the patch failing in the game. The build compiles against a copy of the game's code with every member
made public, so `nameof` works on private methods too.

- **`TimeControlButton_OnClick.Prefix`** runs before the game's `OnClick`. When the fast button is clicked
  while the game is already at its fast speed, it raises the speed and returns `false`, which stops the
  game's own `OnClick` from running. In every other case it returns `true`, and the game handles the click
  as usual.
- **`Controls_Update.Postfix`** runs after the game's `Update`, which already handles the keys `1` to `3`.
  When `4` is pressed and no popup or dialogue is open, it switches to fast and raises the speed.

The speed comes from the in-game variable `FastForward_Multiplier`. The ModMenus mod stores its slider's
value there. Without ModMenus the variable doesn't exist, and the mod uses 5x.

The files in `source/assets/` are copied into the mod's folder as they are:

- `JSON/Mod Menu/modmenu.json` tells ModMenus to show a slider for `FastForward_Multiplier`.
- `JSON/Constants/constants.json` adds the slider's label text to the game's text list.
- `thumb.png` is the picture the game shows in its Mods screen and uploads to the Workshop.
- `steam description.txt` is the text for the mod's Workshop page (see Publishing below).

## Make your own mod

1. Copy this repo, or fork it on GitHub.
2. Rename `source/FastForward.csproj` and `source/FastForward.cs`, and update the project's path in
   `FastForward.sln`.
3. Change the values at the top of the csproj. Each one fills in a field of `info.json`:

   | csproj property | `info.json` field | What it is |
   |---|---|---|
   | `ModName` | `Title` | The mod's name in the game. It is also the name of the mod's folder. |
   | `HarmonyID` | `HarmonyID` | A name no other mod uses, such as `com.yourname.modname`. The DLL is named after it. |
   | `ModDescription` | `Description` | The text under the mod's name in the game. |
   | `Authors` | `Authors` | Your name. |
   | `Version` | `Version` | The mod's version. |
   | `Tags` | `Tags` | A JSON list of Workshop tags, like `["gameplay"]`. |
   | `JSONLoadOrder` | `JSONLoadOrder` | Only for the JSON Load Order mod; leave it at 0. |

   Change `ModName` and `HarmonyID` before you build your own mod. If they stay the same, your build
   replaces FastForward in the game.
4. Replace the files in `source/assets/` with your mod's files. The folders in `assets` match the folders
   the game reads in a mod.
5. Write your patches. To find what to patch, open `Assembly-CSharp.dll` in [ILSpy](https://github.com/icsharpcode/ILSpy)
   and read the game's code.

Version numbers have three parts:

- The first number goes up when an update could break something that worked before, such as a removed
  setting or a feature that now works differently.
- The second number goes up when an update adds something and everything old still works.
- The third number goes up for a fix.

Each version gets one line under `[h3]Changelog[/h3]` at the bottom of `steam description.txt`. Keep the
line, counted from the version number, to 100 characters or fewer: the game's change-note box for Workshop
updates cuts off after 100 characters.

## Tests

```bash
dotnet test tests/FastForward.Tests
```

The tests compile the mod's source into the test project, so running them never deploys the mod. They run
on your PC, outside the game.

### Patch target tests

`PatchTargetTests.cs` has two tests worth copying into any mod:

- `AllPatchTargetsExistInGame` checks that every game method the mod patches exists.
- `AllPatchesApplyToGame` asks Harmony to apply every patch to the real game code, which catches mistakes
  such as a patch parameter that doesn't match the game method's parameters.

`tests/Common/PatchTargetAssert.cs` does the work; the test file only names the mod's namespace.

`ModMenuTests.cs` checks that the code's default speed and the ModMenus slider's default are the same.

### Behaviour tests (advanced)

The other tests run the patches and check what they do: one click, two clicks, the `4` key, blocked
hotkeys, and odd speed settings. That is harder than it sounds, because parts of Unity (`Camera.main`,
`Input`, `GetComponent`, text colours) only work inside the running game.

`TestGame.cs` solves this with `Seams`. It uses Harmony's reverse patching to make copies of the patch
methods, the mod's helpers and the game's `Time_SetState`. In those copies, every call into Unity is
redirected to a small stand-in: `Camera.main` returns a fake camera, `Input.GetKeyDown` reports the keys
the test pressed, and text colours are recorded instead of drawn. The tests then call the copies.

Two things to know when you write tests like these:

- Game components can't be created with `new` outside Unity, so `Seams.Component<T>()` creates empty
  objects and the tests fill in only the fields the code reads.
- Unity's `==` says every fake object is null and equal to every other one. Compare fakes with
  `ReferenceEquals` or `is null`.

## Publishing

The game uploads mods to the Steam Workshop itself:

1. Build in Release.
2. In the game's Mods screen, find your mod and click **Upload**. The game uploads the mod's folder, with
   the title, description and tags from `info.json` and `thumb.png` as the picture. A first upload is
   private.
3. On the mod's Steam Workshop page, paste in the text from `steam description.txt` and make the mod
   public.

For an update, raise `Version`, add a changelog line, build, and click **Upload update** in the Mods
screen. Paste the new changelog line into its change-note box.

Never publish `.pdb` files. They contain the full paths of the files on your PC, including your Windows
user name. The build keeps those paths out of the DLL.

## Tips

- The game runs [HarmonyX](https://github.com/BepInEx/HarmonyX), a version of Harmony. The
  [Harmony documentation](https://harmony.pardeike.net/articles/intro.html) covers prefixes, postfixes,
  transpilers and special parameters such as `__instance`.
- HarmonyX rejects a patch parameter that names a game parameter starting with `__`. Ask for it by
  position instead: `__0` is the first parameter, `__1` the second.
- The public copy of the game's code is only for names. When the mod runs, private members are still
  private, so read and write them with Harmony's `AccessTools` or `Traverse`.
- Join the [Idol Manager Official Discord](https://discord.com/invite/83ywHbP) to talk with other modders.
