using HarmonyLib;
using UnityEngine;
using TMPro;
using System;
using System.Globalization;
using static FastForward.FastForward;

namespace FastForward
{
    /// <summary>
    /// Values and helpers the two patches share.
    /// </summary>
    public class FastForward
    {
        /// <summary>
        /// Name of the in-game variable that holds the speed multiplier. The ModMenus mod stores the slider's value
        /// in it (see assets/JSON/Mod Menu/modmenu.json).
        /// </summary>
        public const string VARID = "FastForward_Multiplier";

        // The speed with no setting or an unreadable one; the same as the Mod Menu slider's default
        public const double DEFAULT_MULTIPLIER = 5d;

        // The game's own fast speed, in in-game minutes per second
        public const double BASE_FAST_SPEED = 200d;

        // A safety limit, not a menu option: the Mod Menu slider stops at 20x, and this caps any value the
        // menu didn't produce (a hand-edited save, an old setting). Each time tick adds speed/4 minutes;
        // above 28.8x a tick spans over a day and skips onNewDay/onNewWeek.
        public const double MAX_MULTIPLIER = 28d;

        // Speeds are doubles, so "already at this speed" allows for rounding
        public const double EPSILON = 0.001d;

        /// <summary>
        /// The speed multiplier from the ModMenus setting, between 1 and MAX_MULTIPLIER.
        /// </summary>
        internal static double GetConfiguredMultiplier()
        {
            // Missing (no ModMenus), unreadable or not a number: the default.
            // InvariantCulture reads "2.5" as two and a half on every PC, whatever its regional number format.
            if (!double.TryParse(variables.Get(VARID), NumberStyles.Float, CultureInfo.InvariantCulture, out double multiplier)
                || double.IsNaN(multiplier) || double.IsInfinity(multiplier))
            {
                multiplier = DEFAULT_MULTIPLIER;
            }

            if (multiplier < 1d)
            {
                multiplier = 1d;
            }
            else if (multiplier > MAX_MULTIPLIER)
            {
                multiplier = MAX_MULTIPLIER;
            }

            return multiplier;
        }

        internal static double GetConfiguredSpeed()
        {
            return BASE_FAST_SPEED * GetConfiguredMultiplier();
        }

        /// <summary>
        /// Switches the game to fast, then raises the speed and colours the fast button gold.
        /// </summary>
        internal static void ApplySuperFast(mainScript main)
        {
            if (main == null)
            {
                return;
            }

            // Use vanilla state transition first so all game-side effects still run as expected.
            main.Time_SetState(mainScript._time_state.fast);
            staticVars.dateTimeAddMinutesPerSecond = GetConfiguredSpeed();
            SetFastButtonColor(mainScript.gold32);
        }

        internal static void SetFastButtonColor(Color32 color)
        {
            // Any of these Unity objects can be missing, so check each step
            if (Camera.main == null)
            {
                return;
            }

            mainScript main = Camera.main.GetComponent<mainScript>();
            if (main == null || main.TimeControls_Fast == null)
            {
                return;
            }

            TextMeshProUGUI fastLabel = main.TimeControls_Fast.GetComponent<TextMeshProUGUI>();
            if (fastLabel != null)
            {
                fastLabel.color = color;
            }
        }
    }

    /// <summary>
    /// Patch class for the TimeControlButton's OnClick method to implement faster time acceleration.
    /// [HarmonyPatch] names the game class and method to patch; nameof makes a renamed method a compile error.
    /// </summary>
    [HarmonyPatch(typeof(TimeControlButton), nameof(TimeControlButton.OnClick))]
    public class TimeControlButton_OnClick
    {
        /// <summary>
        /// Prefix method to enhance the fast forward functionality when clicking the fast forward button twice.
        /// A prefix runs before the game's method.
        /// </summary>
        /// <param name="__instance">The instance of the TimeControlButton being clicked.</param>
        /// <returns>Boolean indicating whether the original method should be executed.</returns>
        public static bool Prefix(TimeControlButton __instance)
        {
            double speed = GetConfiguredSpeed();

            // Under these cases, clicking the time control button should behave as normal:
            // 1. The button being clicked isn't the fast button.
            // 2. The speed isn't currently fast.
            // 3. The speed is already accelerated.
            // Returning true lets the game's method run.
            if (__instance.Type != mainScript._time_state.fast || staticVars.timeState != mainScript._time_state.fast || Math.Abs(staticVars.dateTimeAddMinutesPerSecond - speed) <= EPSILON)
                return true;

            ApplySuperFast(Camera.main != null ? Camera.main.GetComponent<mainScript>() : null);

            // Returning false skips the game's method
            return false;
        }
    }

    /// <summary>
    /// Patch class for the Controls' Update method to implement hotkey-based time acceleration.
    /// </summary>
    [HarmonyPatch(typeof(Controls), nameof(Controls.Update))]
    public class Controls_Update
    {
        /// <summary>
        /// Postfix method to add hotkey functionality for speeding up time when pressing the '4' key.
        /// A postfix runs after the game's method; the game's Update already handles keys 1 to 3.
        /// </summary>
        public static void Postfix()
        {
            // A popup or dialogue is open: hotkeys are off
            if (mainScript.IsBlockingHotkeys())
                return;

            if (Input.GetKeyDown(KeyCode.Alpha4))
            {
                ApplySuperFast(Camera.main != null ? Camera.main.GetComponent<mainScript>() : null);
            }
        }
    }
}
