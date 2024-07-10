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
    -   `Microsoft.NETFramework.ReferenceAssemblies.net46`, version 1.0.3
    -   `UnityEngine.Modules`, version 2019.4.23
9. **Build the Solution:**
To build the solution, select `Build > Build Solution` from the top menu in Visual Studio.

Congratulations, you've created the mod!

### Making Your Own Mod Based on This Mod:
1. **Rename Files:**
Start with this base mod and rename your files within the Visual Studio Solution Explorer.
2. **Configure the Project:**
Open the `FastForward.csproj` file to set your assembly name and mod name. The assembly name is a unique ID for your mod and will be used as the `HarmonyID` in your mod's `info.json` file. It's recommended to use [Reverse Domain Name Notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation).
```xml
<AssemblyName>com.tel.fastforward</AssemblyName>
<ModName>FastForward</ModName>
```
3. **Update Mod Files:**
Modify all your mod's files in the `assets` folder. Set up your `info.json` with the appropriate `Title` and `HarmonyID`.
```json
{
  "Title": "YourModName",
  "Description": "Description of your mod.",
  "Author": "YourName",
  "Version": "1.0",
  "Tags": ["gameplay"],
  "HarmonyID": "com.yourdomain.modname"
}
```
4. **Develop Your Mod:**
Edit the .cs to develop your mod.

### Tips:
- Open `Assembly-CSharp.dll` in [dnSpy](https://github.com/dnSpy/dnSpy/releases/tag/v6.1.8) to explore the game's code and identify what to patch.
- Check out official Harmony documentation [here](https://harmony.pardeike.net/articles/intro.html).
- Check out [this tutorial](https://outward.fandom.com/wiki/Mod_development_guide/Harmony) for more info (ignore the `Awake()` method as IM-HarmonyIntegration handles it automatically).
- Join the [Idol Manager Official Discord](https://discord.com/invite/83ywHbP) to discuss with others in the modding community.
