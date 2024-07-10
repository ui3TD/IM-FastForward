
<p align="center">
  <img src="source/assets/thumb.png?raw=true" />
</p>

# IM-FastForward
FastForward mod for Idol Manager. Press '4' or click the fast-forward button twice to speed up time 5x faster!

This is a little example mod to demonstrate the capabilities of [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)

# IM-HarmonyIntegration Modding Tutorial

### Pre-requisites: 
- [.NET Framework 4.6](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net46)
- [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)
- [Visual Studio Community Edition](https://visualstudio.microsoft.com/vs/community/) (recommended)

### Getting Started:

1. Clone this git repo to download the source files here. The command will create a `IM-FastForward` folder with all the files downloaded.
```bash
git clone https://github.com/ui3TD/IM-FastForward
```
2. Gather the following key .dll files into a convenient folder:
	1. `0Harmony.dll`: This file is located in the `BepInEx\core` folder of your Idol Manager directory, if you've installed IM-HarmonyIntegration.
	2. `Assembly-CSharp.dll`: This file is located in the `IM_Data\Managed` folder of your Idol Manager directory.
	3. `Assembly-CSharp-firstpass.dll`: This file is located in the `IM_Data\Managed` folder of your Idol Manager directory.
	4. `UnityEngine.UI.dll`: This file is located in the `IM_Data\Managed` folder of your Idol Manager directory.
	5. `Unity.TextMeshPro.dll`: This file is located in the `IM_Data\Managed` folder of your Idol Manager directory.
	6. `DOTween.dll`: This file is located in the `IM_Data\Managed` folder of your Idol Manager directory.

3. Open the .csproj file `FastForward.csproj` to configure your folders.

4. Edit the value between the `ModOutputDir` paths to point to where you want to output your mods. By default it points to a folder called `Mods` alongside the `IM-FastForward` folder.
```xml
<ModOutputDir>$(SolutionDir)\..\..\Mods</ModOutputDir>
```

5. Edit the value between the `dllDir` paths to point to a folder where all your .dll files from step 2 are located. By default it points to a folder called `dll` alongside the `IM-FastForward` folder.
```xml
<dllDir>$(SolutionDir)\..\..\dll</dllDir>
```

6. Open the `FastForward.sln` file in Visual Studio.

7. Check the right Solution Explorer panel

8. Edit the following text in the .csproj file to use the unique ID for your mod. Recommended to use [Reverse Domain Name Notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation).
```xml
<AssemblyName>com.tel.fastforward</AssemblyName>
```
9. Open the .sln file in Visual Studio

10. Check the Solution Explorer to make sure all your .dll files are detected under `Dependencies > Assemblies`. If they aren't then double check steps 2 and 5.

<p align="center">
  <img src="readme%20assets/solution_explorer.jpg?raw=true" />
</p>

11. Check the Solution Explorer to check if required NuGet packages were automatically downloaded under `Dependencies > Packages`. If not, right click `Packages` and click `Manage NuGet Packages...` to search for and install the required NuGet packages.
You can try to run `setup_nuget_packages.bat` to do it automatically.

Required NuGet packages are:
- Microsoft.NETFramework.ReferenceAssemblies.net46, version 1.0.3
- UnityEngine.Modules, version 2019.4.23
 
12. Build the solution by selecting `Build > Build Solution` from the top menu.

Congratulations, you've created the mod!

### Making Your Own Mod
1. Start with this and modify your file names from within the Visual Studio Solution Explorer.

2. Open the .csproj file `FastForward.csproj` to set your assembly name and mod name. The assembly name will later be input into your mod's `info.json` file as the `HarmonyID`. The mod name will be the name of the mod's folder.
```xml
<AssemblyName>com.tel.fastforward</AssemblyName>
<ModName>FastForward</ModName>
```
3. Modify all your mod's files in the `assets` folder. Remember to set up your `info.json` with the appropriate `Title` and `HarmonyID`.
```json
{
  "Title": "FastForward",
  "Description": "Press '4' or click the fast-forward button twice to go faster!",
  "Author": "Tel",
  "Version": "1.2",
  "Tags": ["gameplay"],
  "HarmonyID": "com.tel.fastforward"
}

```
4. Edit the .cs to develop your mod. Check out [this tutorial](https://outward.fandom.com/wiki/Mod_development_guide/Harmony) for more info, but ignore the Awake() method. IM-HarmonyIntegration does it automatically. 



