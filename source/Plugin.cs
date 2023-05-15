using HarmonyLib;
using UnityEngine;
using TMPro;

namespace FastForward
{

    [HarmonyPatch(typeof(TimeControlButton), "OnClick")]
    public class TimeControlButton_OnClick
    {
        // Speed up time if you click on the fast forward button twice
        static bool Prefix(TimeControlButton __instance)
        {
            bool output = true;
            if (__instance.Type == mainScript._time_state.fast && staticVars.timeState == mainScript._time_state.fast && staticVars.dateTimeAddMinutesPerSecond != 1000)
            {
                staticVars.dateTimeAddMinutesPerSecond = 1000;
                Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;

                output = false;
            }
            return output;
        }

    }

    [HarmonyPatch(typeof(Controls), "Update")]
    public class Controls_Update
    {
        // Speed up time if you click 4 hotkey
        static void Postfix()
        {
            if (mainScript.IsBlockingHotkeys())
            {
                return;
            }
            if (Input.GetKeyDown(KeyCode.Alpha4))
            {
                Camera.main.GetComponent<mainScript>().Time_SetState(mainScript._time_state.fast);
                staticVars.dateTimeAddMinutesPerSecond = 1000;
                Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;
            }
        }
    }
}
