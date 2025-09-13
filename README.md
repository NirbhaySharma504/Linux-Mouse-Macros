# MouseMaestro: Custom Mouse Macros for Linux

A Python script that uses `evdev` to capture input from a specific mouse (like the Logitech G402), allowing for powerful, custom macros without blocking normal mouse functionality. The script works by creating a virtual mouse device to pass through normal events while intercepting specific combos to run shell commands.

---

## Features

-   **Exclusive Macro Mode**: Normal mouse functions (scrolling, clicking) are blocked while a macro combo is active, preventing accidental actions.
-   **Event Passthrough**: All non-macro mouse events are passed through a virtual device, so your mouse works normally at all times.
-   **Linear Desktop Switching**: Switch virtual desktops without cycling from the last one to the first.
-   **Customizable**: Easily add new macros and change button codes in the configuration section.

### Current Macros
-   **Volume Control**: Hold **Forward Button** + **Scroll Up/Down**
-   **Desktop Switching**: Hold **Back Button** + **Scroll Up/Down**
-   **Media Control (Next/Prev)**: Hold **Back Button** + **Right/Left Click**
-   **Media Control (Play/Pause)**: Hold **Back Button** + **Middle Click**

---

## Requirements

-   Python 3
-   Linux with `evdev` and `uinput` kernel support
-   **Dependencies**:
    -   `evdev` (Python library)
    -   `xdotool` (for desktop switching)
    -   `playerctl` (for media control)
    -   `pactl` (for PulseAudio volume control, usually pre-installed)

---

## Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/your-username/MouseMaestro.git](https://github.com/your-username/MouseMaestro.git)
    cd MouseMaestro
    ```

2.  **Install Dependencies**
    ```bash
    # Python library
    pip install evdev

    # Command-line tools
    sudo apt-get update && sudo apt-get install xdotool playerctl
    ```

3.  **Set Permissions**
    You need to give your user permission to read from input devices and create virtual devices.

    -   **Add user to the `input` group:**
        ```bash
        sudo usermod -aG input $USER
        ```
    -   **Create a `udev` rule for the virtual device:**
        ```bash
        echo 'KERNEL=="uinput", MODE="0660", GROUP="input"' | sudo tee /etc/udev/rules.d/99-uinput.rules
        ```
    -   **Apply the new rules:**
        ```bash
        sudo udevadm control --reload-rules && sudo udevadm trigger
        ```
    -   **Important**: You must **log out and log back in** for the group changes to take effect.

---

## Configuration

Before running, you must configure the script for your specific mouse.

1.  **Find Your Device Path**
    Run the following command to find the stable device path for your mouse:
    ```bash
    ls /dev/input/by-id/
    ```
    Look for the name ending in `-event-mouse`.

2.  **Edit the Script**
    Open `macro_mouse.py` and update the `DEVICE_PATH` variable with the path you found. You can also change the button codes in this section if needed.

---

## Usage

The script can be run directly or as a background service.

### Manual Execution
To test the script, run it directly from your terminal:
```bash
python3 macro_mouse.py
```

### Automatic Start (systemd Service)

To have the script run automatically every time you log in:

1.  **Move the script to a permanent location:**
    ```bash
    sudo mv macro_mouse.py /usr/local/bin/
    sudo chmod +x /usr/local/bin/macro_mouse.py
    ```
2.  **Create the service file:**
    ```bash
    mkdir -p ~/.config/systemd/user/
    nano ~/.config/systemd/user/mouse-macro.service
    ```
3.  **Paste the following configuration into the file:**
    ```ini
    [Unit]
    Description=Custom Mouse Macro Service

    [Service]
    ExecStart=/usr/bin/python3 /usr/local/bin/macro_mouse.py

    [Install]
    WantedBy=default.target
    ```
4.  **Enable and start the service:**
    ```bash
    systemctl --user daemon-reload
    systemctl --user enable --now mouse-macro.service
    ```
    You can check its status with `systemctl --user status mouse-macro.service`.
