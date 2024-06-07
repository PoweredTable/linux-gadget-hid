# linux-gadget-hid
Example using linux with a micro-usb as a HID gadget (keyboard)

You will need a device with a microusb host port (e.g. Odroid C1, C2, C4, N2), and recent-enough kernel (>3.19) with support for libcomposite and usb_f_hid. Check that your kernel has support for them (either built-in or as modules):

```bash
zcat /proc/config.gz | egrep -i "libcomposite|usb_f_hid"
```
You should get an output as shown below:
```bash
CONFIG_USB_LIBCOMPOSITE=y
CONFIG_USB_F_HID=y # for me instead of an 'y' its an 'm' and works just fine
```

# Dependencies
  - python3

# How-to
* Edit `create-hid-keyboard.py` and set `VENDOR`, `MANUFACTURER` and `DESCRIPTION` to the strings you want.
* Create the keyboard HID device:
```bash
sudo ./create-hid-keyboard.py
```
Leave this process running (e.g. in the background). You can check on the USB host that the device is recognized as a keyboard when plugging in the USB cable:
```bash
dmesg
...
[ 6377.913325] usb 3-3: new high-speed USB device number 3 using xhci_hcd
[ 6378.062977] usb 3-3: New USB device found, idVendor=16c0, idProduct=0488, bcdDevice= 1.00
[ 6378.062981] usb 3-3: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[ 6378.062984] usb 3-3: Product: Odroid Keyboard HID
[ 6378.062986] usb 3-3: Manufacturer: Gadget
[ 6378.062988] usb 3-3: SerialNumber: fedcba9876543210
[ 6378.065886] input: Gadget Odroid Keyboard HID as /devices/pci0000:00/0000:00:14.0/usb3/3-3/3-3:1.0/0003:16C0:0488.0004/input/input33
[ 6378.129950] hid-generic 0003:16C0:0488.0004: input,hidraw3: USB HID v1.01 Keyboard [Gadget Odroid Keyboard HID] on usb-0000:00:14.0-3/input0
```
# Usage
You can run `hid_keyboard.py` after creating the hid background process and plugging your device into the USB port of the host machine:

```bash
sudo python3 hid_keyboard.py
```

You can also import the `HIDKeyboard` class from `hid_keyboard.py` file and implement it as you wish:

```python
from hid_keyboard import HIDKeyboard

hid = HIDKeyboard()

# sending a whole string
hid.send_string("A string")

# sending a single character
hid.send_char("a")
```

# Troubleshooting
* make sure the kernel has the necessary modules
* make sure the microusb port is in OTG mode (not host) (Set the dr_mode to dr_mode = "peripheral"). You might need to tweak the DTB as described here: https://forum.odroid.com/viewtopic.php?f=139&t=36602
* you can see keystrokes with `evtest` on the USB host device
