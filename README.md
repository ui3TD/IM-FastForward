<p align="center">
  <img src="source/assets/thumb.png?raw=true" />
</p>

# IM-FastForward
FastForward mod for Idol Manager. This mod speeds up the game's time by 5x when you press '4' or click the fast-forward button twice!

This is a little example mod to demonstrate the capabilities of [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)

# IM-HarmonyIntegration Modding Tutorial

### Pre-requisites: 
Ensure you have the following prerequisites installed to develop and run the mod:
- [.NET Framework 4.6](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net46)
- [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)
- [Visual Studio Community Edition](https://visualstudio.microsoft.com/vs/community/) (recommended)

### Getting Started by Recreating This Mod:

1. **Clone the Repository:**
Download the source files by cloning this git repository. The command will create an `IM-FastForward` folder with all the files downloaded.
```bash
git clone https://github.com/ui3TD/IM-FastForward
```
2. **Gather Important .dll Files:**
Collect the following key .dll files from your Idol Manager installation directory and place them in a convenient folder such as a folder called `dll` alongside the `IM-FastForward` folder:
	1. `0Harmony.dll`: Located in the `BepInEx\core` folder.
	2. `Assembly-CSharp.dll`: Located in the `IM_Data\Managed` folder.
	3. `Assembly-CSharp-firstpass.dll`: Located in the `IM_Data\Managed` folder.directory.
	4. `UnityEngine.UI.dll`: Located in the `IM_Data\Managed` folder.
	5. `Unity.TextMeshPro.dll`: Located in the `IM_Data\Managed` folder.
	6. `DOTween.dll`: Located in the `IM_Data\Managed` folder.
3. **Open and Configure the Project:**
Open the `FastForward.csproj` file in Visual Studio.
4. **Set Output Directory:**
Change the `<ModOutputDir>` path to where you want your mod files to be output. By default, it points to a folder called `Mods` alongside the `IM-FastForward` folder.
```xml
<ModOutputDir>$(SolutionDir)\..\..\Mods</ModOutputDir>
```
5. **Set DLL Directory:**
Change the `<dllDir>` path to the folder where you placed your .dll files. By default, it points to a folder called `dll` alongside the `IM-FastForward` folder.
```xml
<dllDir>$(SolutionDir)\..\..\dll</dllDir>
```
6. **Open the Solution File:**
Double-click the `FastForward.sln` file to open it in Visual Studio.
7. **Check Dependencies:**
In the Solution Explorer, ensure all your .dll files are detected under `Dependencies > Assemblies`. If they are not listed, verify steps 2 and 5.
<p align="center">
  <img src="readme%20assets/solution_explorer.jpg?raw=true" />
</p>

8. **Check NuGet Packages:**
 Ensure required NuGet packages are installed. If they are not automatically downloaded, you can try running `setup_nuget_packages.bat` to install the packages. Otherwise, right-click `Packages` under `Dependencies` in the Solution Explorer and select `Manage NuGet Packages...` to search for and install the required packages:
    -   Package: `Microsoft.NETFramework.ReferenceAssemblies.net46`
    Version: 1.0.3
    Source: http://api.nuget.org/v3/index.json
    -   `UnityEngine.Modules`
    Version: 2019.4.23
    Source: https://nuget.bepinex.dev/v3/index.json
9. **Build the Solution:**
To build the solution, select `Build > Build Solution` from the top menu in Visual Studio.

Congratulations, you've created the mod!

### Making Your Own Mod Based on This Mod:
1. **Enable Debug Console:** 
Edit the `Idol Manager\BepInEx\config\BepInEx.cfg` file. Under `[Logging.Console]`, set `Enabled = true`. This will allow you to see the debug console when you run Idol Manager.
2. **Rename Files:**
Start with this base mod and rename your files within the Visual Studio Solution Explorer.
3. **Configure the Mod Info:**
Open the .csproj file to input all of your mod information. The .csproj file is set up to automatically generate the mod `info.json` file. For `HarmonyID`, it's recommended to use [Reverse Domain Name Notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation) so that the ID is unique and organized.
```xml
<ModName>YourModName</ModName>
<HarmonyID>com.yourdomain.modname</HarmonyID>
<ModDescription>Input your mod description here</ModDescription>
<Authors>YourName</Authors>
<Version>1.0.0</Version>
<Tags>["gameplay"]</Tags>
```
4. **Update Mod Files:**
Modify all your mod's files in the `assets` folder. As noted in Step 2, the `info.json` will be automatically generated.
5. **Develop Your Mod:**
Edit the .cs to develop your mod.

### Tips:
- Open `Assembly-CSharp.dll` in [dnSpy](https://github.com/dnSpy/dnSpy/releases/tag/v6.1.8) to explore the game's code and identify what to patch.
- Check out the official Harmony documentation [here](https://harmony.pardeike.net/articles/intro.html).
- [This](https://www.youtube.com/watch?v=WmuOjlhulyo) is a great Youtube tutorial introducing Harmony.
- Join the [Idol Manager Official Discord](https://discord.com/invite/83ywHbP) to discuss with others in the modding community.
