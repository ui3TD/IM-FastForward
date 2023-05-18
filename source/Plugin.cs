using HarmonyLib;
using UnityEngine;
using TMPro;

// Rename the namespace to be descriptive of your mod
namespace FastForward
{

    // Speed up time if you click on the fast forward button twice
    // Point Harmony to the correct method in Assembly-Csharp.dll. The TimeControlButton.OnClick method is where the time
    // control buttons are defined.
    [HarmonyPatch(typeof(TimeControlButton), "OnClick")]
    public class TimeControlButton_OnClick
    {
        // Set up a Prefix patch that runs before the method is run. This method returns false to skip the original method
        // or true to run the original method.
        // The argument __instance accesses the TimeControlButton instance. This is similar to the C# keyword this when used
        // in the original method.
        static bool Prefix(TimeControlButton __instance)
        {
            // Set default output to run the original method
            bool output = true;
            
            // If the fast speed button is clicked AND the time is already at fast speed AND the speed isn't already at 1000
            if (__instance.Type == mainScript._time_state.fast && staticVars.timeState == mainScript._time_state.fast && staticVars.dateTimeAddMinutesPerSecond != 1000)
            {
                // Set the speed to 1000 (5x faster than usual)
                staticVars.dateTimeAddMinutesPerSecond = 1000;
                
                // Change the TimeControls_Fast GUI color to gold
                Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;
                
                // Skip the original method, so that the button doesn't use the default behaviour
                output = false;
            }
            return output;
        }

    }
    
    // Speed up time if the user presses '4'.
    // The Controls.Update method is where hotkeys are defined.
    [HarmonyPatch(typeof(Controls), "Update")]
    public class Controls_Update
    {
        // Set up a Postfix method that runs when the original method is returned. The Postfix should always return void.
        static void Postfix()
        {
            // Terminate method if hotkeys are blocked.
            if (mainScript.IsBlockingHotkeys())
            {
                return;
            }
            
            // On '4' hotkey press
            if (Input.GetKeyDown(KeyCode.Alpha4))
            {
                // Set the time to fast
                Camera.main.GetComponent<mainScript>().Time_SetState(mainScript._time_state.fast);
                
                // Set the speed to 1000
                staticVars.dateTimeAddMinutesPerSecond = 1000;
                
                // Change the TimeControls_Fast GUI color to gold
                Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;
            }
        }
    }
}
