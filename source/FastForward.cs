using HarmonyLib;
using UnityEngine;
using TMPro;
using static FastForward.FastForward;

namespace FastForward
{
    /// <summary>
    /// Class to hold information used throughout the project.
    /// </summary>
    public class FastForward
    {
        /// <summary>
        /// Name of an ingame variable to hold the speed multiplier, for integration with the ModMenus mod.
        /// </summary>
        public const string VARID = "FastForward_Multiplier";

        /// <summary>
        /// Default value of the speed multiplier.
        /// </summary>
        public const string DEFAULT_VAR = "5";
    }

    /// <summary>
    /// Patch class for the TimeControlButton's OnClick method to implement faster time acceleration.
    /// </summary>
    [HarmonyPatch(typeof(TimeControlButton), "OnClick")]
    public class TimeControlButton_OnClick
    {
        /// <summary>
        /// Prefix method to enhance the fast forward functionality when clicking the fast forward button twice.
        /// </summary>
        /// <param name="__instance">The instance of the TimeControlButton being clicked.</param>
        /// <returns>Boolean indicating whether the original method should be executed.</returns>
        public static bool Prefix(TimeControlButton __instance)
        {
            // Get the speed multiplier from the ingame variable (if ModMenus mod is used). If it's null then use the default value.
            double mult = double.Parse(variables.Get(VARID) ?? DEFAULT_VAR);

            // Calculated the speed after the multiplier.
            double speed = 200 * mult;

            // Under these cases, clicking the time control button should behave as normal
            // (return true to abort the patch and execute the rest of the method)
            if (__instance.Type != mainScript._time_state.fast || staticVars.timeState != mainScript._time_state.fast || staticVars.dateTimeAddMinutesPerSecond == speed)
                return true;

            // Otherwise, set the new speed
            staticVars.dateTimeAddMinutesPerSecond = speed;

            // Set the color of the UI component
            Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;

            // return false to not execute the original method
            return false;
        }

    }

    /// <summary>
    /// Patch class for the Controls' Update method to implement hotkey-based time acceleration.
    /// </summary>
    [HarmonyPatch(typeof(Controls), "Update")]
    public class Controls_Update
    {
        /// <summary>
        /// Postfix method to add hotkey functionality for speeding up time when pressing the '4' key.
        /// </summary>
        public static void Postfix()
        {
            // If something is blocking hotkeys then abort the patch
            if (mainScript.IsBlockingHotkeys())
                return;

            // If the '4' key is detected
            if (Input.GetKeyDown(KeyCode.Alpha4))
            {
                // Get the multiplier from the in-game variable, with the default
                double mult = double.Parse(variables.Get(VARID) ?? DEFAULT_VAR);

                // Calculate the speed
                double speed = 200 * mult;

                // Activate the fast time control button
                Camera.main.GetComponent<mainScript>().Time_SetState(mainScript._time_state.fast);

                // Set the new speed
                staticVars.dateTimeAddMinutesPerSecond = speed;

                // Set the color of the UI component
                Camera.main.GetComponent<mainScript>().TimeControls_Fast.GetComponent<TextMeshProUGUI>().color = mainScript.gold32;
            }
        }
    }
}
