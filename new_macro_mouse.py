import evdev
import os
import subprocess

# --- CONFIGURATION ---
DEVICE_PATH = "/dev/input/by-id/usb-Logitech_Gaming_Mouse_G402_6D7D10685551-event-mouse"
FORWARD_BUTTON_CODE = 277
BACK_BUTTON_CODE = 278
LEFT_CLICK_CODE = 272
RIGHT_CLICK_CODE = 273
MIDDLE_CLICK_CODE = 274    # Default for BTN_MIDDLE
SCROLL_CODE = 8

# --- DO NOT EDIT BELOW THIS LINE ---

def run_command(command):
    subprocess.Popen(command, shell=True)

device = None
ui = None

try:
    device = evdev.InputDevice(DEVICE_PATH)
    capabilities = {
        evdev.ecodes.EV_REL: [evdev.ecodes.REL_X, evdev.ecodes.REL_Y, evdev.ecodes.REL_WHEEL],
        evdev.ecodes.EV_KEY: [
            evdev.ecodes.BTN_LEFT, evdev.ecodes.BTN_RIGHT, evdev.ecodes.BTN_MIDDLE,
            FORWARD_BUTTON_CODE, BACK_BUTTON_CODE
        ]
    }
    ui = evdev.UInput(capabilities, name='virtual-g402-macro-mouse')

    print(f"Successfully listening to {device.name}")
    print("Virtual mouse created. Grabbing physical device...")
    device.grab()

    is_back_pressed = False
    is_forward_pressed = False

    for event in device.read_loop():
        is_macro_event = False

        # --- MACRO DETECTION ---
        if is_forward_pressed and event.type == evdev.ecodes.EV_REL and event.code == SCROLL_CODE:
            is_macro_event = True
            if event.value == 1: run_command("pactl set-sink-volume @DEFAULT_SINK@ +5%")
            else: run_command("pactl set-sink-volume @DEFAULT_SINK@ -5%")
        
        elif is_back_pressed:
            if event.type == evdev.ecodes.EV_REL and event.code == SCROLL_CODE:
                is_macro_event = True
                if event.value == 1: run_command("CURRENT=$(xdotool get_desktop); NUM_DESKTOPS=$(xdotool get_num_desktops); if [ $CURRENT -lt $(($NUM_DESKTOPS - 1)) ]; then xdotool set_desktop $(($CURRENT + 1)); fi")
                else: run_command("CURRENT=$(xdotool get_desktop); if [ $CURRENT -gt 0 ]; then xdotool set_desktop $(($CURRENT - 1)); fi")
            
            elif event.type == evdev.ecodes.EV_KEY and event.value == 1:
                is_macro_event = True # Assume it's a macro unless proven otherwise
                if event.code == RIGHT_CLICK_CODE: run_command("playerctl next")
                elif event.code == LEFT_CLICK_CODE: run_command("playerctl previous")
                elif event.code == MIDDLE_CLICK_CODE: run_command("playerctl play-pause")
                else: is_macro_event = False # It was a different key, not a macro

        # --- STATE TRACKING ---
        if event.type == evdev.ecodes.EV_KEY and event.code in [FORWARD_BUTTON_CODE, BACK_BUTTON_CODE]:
            is_macro_event = True
            if event.value in [1, 2]:
                if event.code == FORWARD_BUTTON_CODE: is_forward_pressed = True
                elif event.code == BACK_BUTTON_CODE: is_back_pressed = True
            elif event.value == 0:
                if event.code == FORWARD_BUTTON_CODE: is_forward_pressed = False
                elif event.code == BACK_BUTTON_CODE: is_back_pressed = False

        # --- EVENT FORWARDING ---
        if not is_macro_event:
            ui.write_event(event)
            ui.syn()

except KeyboardInterrupt:
    print("\nExiting by user request.")
except Exception as e:
    print(f"An error occurred: {e}")
finally:
    print("Cleaning up...")
    if device and device.fd != -1:
        try:
            device.ungrab()
        except OSError as e:
            if e.errno != 22: print(f"Error during ungrab: {e}")
    if ui:
        ui.close()
