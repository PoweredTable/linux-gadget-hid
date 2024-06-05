"""
Module: create-hid-keyboard

This module provides functions to set up a USB gadget device for an Odroid Keyboard HID.

It includes functions to write values to device files, set up the USB gadget device,
clean up resources used by the device, and run the setup asynchronously.

This module is designed to be run as a standalone script in the background
and is not intended to be imported.

"""
import sys
import os
import shutil
import pwd
import asyncio
import atexit

VENDOR = "Gadget"
MANUFACTURER = VENDOR
DESCRIPTION = "Odroid Keyboard HID"

HID_DEV_NAME = "odroidc4_hid"
VENDOR_ID = 0x16c0
PRODUCT_ID = 0x0488
SERIAL_NUMBER = "fedcba9876543210"

REPORT_LENGTH = "8"
REPORT_DESC = bytes([
    0x05, 0x01,  # Usage Page (Generic Desktop Ctrls)
    0x09, 0x06,  # Usage (Keyboard)
    0xA1, 0x01,  # Collection (Application)
    0x05, 0x07,  # Usage Page (Keyboard/Keypad)
    0x19, 0xE0,  # Usage Minimum (0xE0)
    0x29, 0xE7,  # Usage Maximum (0xE7)
    0x15, 0x00,  # Logical Minimum (0)
    0x25, 0x01,  # Logical Maximum (1)
    0x75, 0x01,  # Report Size (1)
    0x95, 0x08,  # Report Count (8)
    0x81, 0x02,  # Input (Data,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x95, 0x01,  # Report Count (1)
    0x75, 0x08,  # Report Size (8)
    0x81, 0x03,  # Input (Const,Var,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0x95, 0x05,  # Report Count (5)
    0x75, 0x01,  # Report Size (1)
    0x05, 0x08,  # Usage Page (LEDs)
    0x19, 0x01,  # Usage Minimum (Num Lock)
    0x29, 0x05,  # Usage Maximum (Kana)
    0x91, 0x02,  # Output (Data,Var,Abs)
    0x95, 0x01,  # Report Count (1)
    0x75, 0x03,  # Report Size (3)
    0x91, 0x03,  # Output (Const,Var,Abs)
    0x95, 0x06,  # Report Count (6)
    0x75, 0x08,  # Report Size (8)
    0x15, 0x00,  # Logical Minimum (0)
    0x25, 0x65,  # Logical Maximum (101)
    0x05, 0x07,  # Usage Page (Keyboard/Keypad)
    0x19, 0x00,  # Usage Minimum (0x00)
    0x29, 0x65,  # Usage Maximum (0x65)
    0x81, 0x00,  # Input (Data,Array,Abs,No Wrap,Linear,Preferred State,No Null Position)
    0xC0,  # End Collection
])

DEV_KERNEL_PATH = f"/sys/kernel/config/usb_gadget/{HID_DEV_NAME}"


def write_to_dev_kernel_file(dev_file, value, write_mode="w"):
    """
    Write a value to the device kernel file.

    Parameters
    ----------
    dev_file
        The path to the device file.
    value
        The value to write to the file.
    write_mode : str, optional
        The mode to open the file in ('w' for write, 'wb' for binary write), by default 'w'.
    """
    dev_file = os.path.join(DEV_KERNEL_PATH, dev_file)
    with open(dev_file, write_mode, encoding="utf-8") as fd:
        fd.write(value)


def setup():
    """
    Set up the USB gadget device.
    """
    os.makedirs(os.path.join(DEV_KERNEL_PATH, "strings/0x409"), exist_ok=True)
    os.makedirs(os.path.join(DEV_KERNEL_PATH, "configs/c.1/strings/0x409"), exist_ok=True)
    os.makedirs(os.path.join(DEV_KERNEL_PATH, "functions/hid.usb0"), exist_ok=True)

    write_to_dev_kernel_file("idVendor", f"0x{VENDOR_ID:04x}")
    write_to_dev_kernel_file("idProduct", f"0x{PRODUCT_ID:04x}")
    write_to_dev_kernel_file("bcdDevice", "0x0100")
    write_to_dev_kernel_file("bcdUSB", "0x0200")

    write_to_dev_kernel_file("strings/0x409/serialnumber", SERIAL_NUMBER)
    write_to_dev_kernel_file("strings/0x409/manufacturer", MANUFACTURER)
    write_to_dev_kernel_file("strings/0x409/product", DESCRIPTION)

    write_to_dev_kernel_file("configs/c.1/strings/0x409/configuration", f"Config 1 : {DESCRIPTION}")
    write_to_dev_kernel_file("configs/c.1/MaxPower", "250")

    write_to_dev_kernel_file("functions/hid.usb0/protocol", "1")
    write_to_dev_kernel_file("functions/hid.usb0/subclass", "1")
    write_to_dev_kernel_file("functions/hid.usb0/report_length", REPORT_LENGTH)
    write_to_dev_kernel_file("functions/hid.usb0/report_desc", REPORT_DESC, "wb")

    os.symlink(
        os.path.join(DEV_KERNEL_PATH, "functions/hid.usb0"),
        os.path.join(DEV_KERNEL_PATH, "configs/c.1/hid.usb0"),
        target_is_directory=True
    )

    write_to_dev_kernel_file("UDC", '\r\n'.join(os.listdir("/sys/class/udc")))


async def setup_and_run():
    """
    Set up the USB gadget device and keep the event loop running.
    """
    atexit.register(cleanup)
    setup()
    while True:
        await asyncio.sleep(1)  # Keep the event loop running


def cleanup():
    """
    Clean up resources used by the USB gadget device.
    """
    udc_path = os.path.join(DEV_KERNEL_PATH, "UDC")
    if os.path.exists(udc_path):
        with open(udc_path, "w", encoding="utf-8") as fd:
            fd.truncate()

        shutil.rmtree(DEV_KERNEL_PATH, ignore_errors=True)


def main():
    """
    Main function to set up and run the USB gadget device.
    """
    user_curr = pwd.getpwuid(os.getuid())
    if os.getuid() != 0:
        print("[KEYBOARD-HID] Attempting to run as <root>")
        c = os.system(f"/usr/bin/sudo /usr/bin/su root -c '{sys.executable} {' '.join(sys.argv)}'")
        sys.exit(c)

    print(f"[KEYBOARD-HID] Running as <{user_curr.pw_name}>")
    asyncio.run(setup_and_run())


if __name__ == "__main__":
    main()
