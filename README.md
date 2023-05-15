<p align="center">
  <img src="mod%20assets/thumb.png?raw=true" />
</p>

# IM-FastForward
FastForward mod for Idol Manager. Press '4' or click the fast-forward button twice to speed up time 5x faster!

This is a little example mod to demonstrate the ability of [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)

# IM-HarmonyIntegration Modding Tutorial

### Pre-requisites: 
- [.NET Framework 4.6](https://dotnet.microsoft.com/en-us/download/dotnet-framework/net46)
- [IM-HarmonyIntegration](https://github.com/ui3TD/IM-HarmonyIntegration)
- [Visual Studio Community Edition](https://visualstudio.microsoft.com/vs/community/) installed for .Net desktop development

### Instructions:

1. Download the source files here to use as a template
2. Edit the following text in the .csproj file to point to your Assembly-CSharp.dll, and 0Harmony.dll. Other libraries like Unity.TextMeshPro are not required but can be added on an as-needed basis. Assembly-CSharp.dll is in the IM_Data/Managed folder of Idol Manager. 0Harmony.dll is in the BepInEx/core folder of IM-HarmonyIntegration.
```xml
    <ItemGroup>
	    <Reference Include="Assembly-CSharp">
		    <HintPath>dll\Assembly-CSharp.dll</HintPath>
	    </Reference>
	    <Reference Include="Harmony">
		    <HintPath>dll\0Harmony.dll</HintPath>
	    </Reference>
	    <Reference Include="Unity.TextMeshPro">
		    <HintPath>dll\Unity.TextMeshPro.dll</HintPath>
	    </Reference>
    </ItemGroup>
```
3. Edit the following text in the .csproj file to use the unique ID for your mod. Recommended to use [Reverse Domain Name Notation](https://en.wikipedia.org/wiki/Reverse_domain_name_notation).
```xml
<AssemblyName>com.tel.fastforward</AssemblyName>
```
4. Open the .sln file in Visual Studio
5. Edit Plugin.cs to develop your mod. Feel free to change names of all of the files/folders and classes/methods for your mod. Check out [this tutorial](https://outward.fandom.com/wiki/Mod_development_guide/Harmony) for more info, but ignore the part about the Awake() method. IM-HarmonyIntegration does it for you automatically. If you have issues referencing .NET Framework 4.6, open the commandline (cmd), navigate to the folder in commandline, and run net46_setup.sh to download .NET 4.6 directly to your solution. 
6. Build the solution. 
7. Find the .dll file in bin/Debug to include in your mod
8. Add the HarmonyID field with your unique mod ID to your mod's info.json. This will let IM-HarmonyIntegration find your file.
```json
"HarmonyID": "com.tel.fastforward"
```


