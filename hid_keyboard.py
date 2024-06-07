import logging
import time
from re import sub


class HIDKeyboard:
    """
    Emulate a keyboard using Human Interface Device (HID) protocol.
    """
    SIMPLE_CHARS = {'a': 0x04, 'b': 0x05, 'c': 0x06, 'd': 0x07, 'e': 0x08, 'f': 0x09, 'g': 0x0A,
                    'h': 0x0B, 'i': 0x0C, 'j': 0x0D, 'k': 0x0E, 'l': 0x0F, 'm': 0x10, 'n': 0x11,
                    'o': 0x12, 'p': 0x13, 'q': 0x14, 'r': 0x15,  's': 0x16, 't': 0x17, 'u': 0x18,
                    'v': 0x19, 'w': 0x1A, 'x': 0x1B, 'y': 0x1C, 'z': 0x1D, '1': 0x1E, '2': 0x1F,
                    '3': 0x20, '4': 0x21, '5': 0x22,   '6': 0x23, '7': 0x24, '8': 0x25, '9': 0x26,
                    '0': 0x27, ' ': 0x2C, '-': 0x2D, '=': 0x2E, '[': 0x2F, ']': 0x30, '\\': 0x31,
                    '#': 0x32, ';': 0x33, '\'': 0x34,  '`': 0x35, ',': 0x36, '.': 0x37, '/': 0x38}

    SHIFT_CHARS = {'A': 0x04, 'B': 0x05, 'C': 0x06, 'D': 0x07, 'E': 0x08, 'F': 0x09, 'G': 0x0A,
                   'H': 0x0B, 'I': 0x0C,  'J': 0x0D, 'K': 0x0E, 'L': 0x0F, 'M': 0x10, 'N': 0x11,
                   'O': 0x12, 'P': 0x13, 'Q': 0x14, 'R': 0x15, 'S': 0x16, 'T': 0x17, 'U': 0x18,
                   'V': 0x19, 'W': 0x1A, 'X': 0x1B, 'Y': 0x1C, 'Z': 0x1D, '!': 0x1E,  '@': 0x1F,
                   '#': 0x20, '$': 0x21, '%': 0x22, '^': 0x23, '&': 0x24, '*': 0x25, '(': 0x26,
                   ')': 0x27, '_': 0x2D, '+': 0x2E, '{': 0x2F, '}': 0x30, '|': 0x31, '~': 0x32,
                   ':': 0x33, '"': 0x34, '<': 0x36,  '>': 0x37, '?': 0x38}

    COMMAND_KEYS = {'ENTER': 0x28, 'ESCAPE': 0x29, 'BACKSPACE': 0x2A, 'TAB': 0x2B, 'SPACE': 0x2C, 'CAPS_LOCK': 0x39,
                    'F1': 0x3A, 'F2': 0x3B, 'F3': 0x3C, 'F4': 0x3D, 'F5': 0x3E, 'F6': 0x3F, 'F7': 0x40, 'F8': 0x41,
                    'F9': 0x42, 'F10': 0x43, 'F11': 0x44, 'F12': 0x45, 'PRINT': 0x46, 'SCROLL_LOCK': 0x47,
                    'PAUSE': 0x48, 'INSERT': 0x49, 'HOME': 0x4A, 'PAGE_UP': 0x4B, 'DELETE': 0x4C, 'END': 0x4D,
                    'PAGE_DOWN': 0x4E, 'RIGHT_ARROW': 0x4F, 'LEFT_ARROW': 0x50, 'DOWN_ARROW': 0x51, 'UP_ARROW': 0x52,
                    'LEFT_CONTROL': 0xE0, 'LEFT_SHIFT': 0xE1, 'LEFT_ALT': 0xE2, 'LEFT_GUI': 0xE3, 'RIGHT_CONTROL': 0xE4,
                    'RIGHT_SHIFT': 0xE5, 'RIGHT_ALT': 0xE6, 'RIGHT_GUI': 0xE7}

    MODIFIER_KEY = {'LEFT_CONTROL': 0x01, 'LEFT_SHIFT': 0x02, 'LEFT_ALT': 0x04,
                    'LEFT_GUI': 0x08, 'RIGHT_CONTROL': 0x10,
                    'RIGHT_SHIFT': 0x20, 'RIGHT_ALT': 0x40, 'RIGHT_GUI ': 0x80}

    def __init__(self, typing_delay: float = 0, device='/dev/hidg0'):
        """
        Initialize the HIDKeyboard.

        Args:
            typing_delay (float, optional): Delay between sending each character. Defaults to 0.
            device (str, optional): Path to the HID device. Defaults to '/dev/hidg0'.
        """
        self.typing_delay = typing_delay
        self.device = device

    def send_string(self, string: str):
        """
        Send a string of characters as keystrokes.

        Args:
            string (str): The string to be sent as keystrokes.
        """
        characters = str(string.strip())
        list_string = list(characters)
        for character in list_string:
            self.send_char(character)

    def send_char(self, character: str):
        """
        Send a single character as a keystroke.

        Args:
            character (str): The character to be sent as a keystroke.
        """
        report = bytearray(8)

        if character in self.SIMPLE_CHARS:
            report[2] = self.SIMPLE_CHARS[character]

        elif character in self.SHIFT_CHARS:
            report[0] = self.MODIFIER_KEY['LEFT_SHIFT']
            report[2] = self.SHIFT_CHARS[character]

        else:
            logging.warning("unable to send unlisted character %r", character)
            return

        self._write_report_to_dev(report)
        self._release_all_keys()
        time.sleep(self.typing_delay)

    def send_commands(self, commands: str):
        commands = commands.strip()

        report = bytearray(8)

        commands = sub('(.*)CONTROL', 'LEFT_CONTROL', commands)
        commands = sub('(.*)CTRL', 'LEFT_CONTROL', commands)
        commands = sub('(.*)SHIFT', 'LEFT_SHIFT', commands)
        commands = sub('(.*)ALT', 'LEFT_ALT', commands)
        commands = sub('(.*)GUI', 'LEFT_GUI', commands)
        commands = sub('(.*)WIN', 'LEFT_GUI', commands)
        commands = sub('(.*)WINDOWS', 'LEFT_GUI', commands)

        word_count = len(commands.split())

        if word_count != 1:
            logging.warning("unable to send multiple command at a time")
            return

        if commands in self.COMMAND_KEYS:
            report[2] = self.COMMAND_KEYS[commands]
        else:
            logging.warning("unable to send unlisted command %r", commands)
            return

        self._write_report_to_dev(report)
        self._release_all_keys()
        time.sleep(self.typing_delay)


    def _release_all_keys(self):
        """Release all keys."""
        self._write_report_to_dev(bytearray(8))

    def _write_report_to_dev(self, report: bytearray):
        """
        Write the report to the HID device.

        Args:
            report (bytearray): The report to be written to the HID device.
        """
        with open(self.device, 'rb+') as file_handler:
            file_handler.write(report)

if __name__ == "__main__":
    hid = HIDKeyboard()
    while 1:
        hid.send_string("A very s1mpl3 ex@mple")
        time.sleep(3)