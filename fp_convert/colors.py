"""
Module to retrieve color specs of named standard colors.
"""

import json
import os
from pathlib import Path

colordefs_file_path = Path(
    Path(os.path.abspath(__file__)).parent, "resources", "colordefs.json"
)


class Color:
    """
    Class to retrieve color specs of named standard colors.
    """

    with open(colordefs_file_path) as colordefs_file:
        colordefs = json.load(colordefs_file)

    def __init__(self, name: str):
        """
        Initialize the color from the content colordefs.json.

        Parameters:
        -----------
        name: str
            The name of the color. It should be the standard name of the color,
            all in lower case English alphabets.
        """
        if name not in Color.colordefs["colors"]:
            raise ValueError(f"Color {name} not found in color definitions.")

        self.name = name
        self.rgbval = Color.colordefs["colors"][name][1]
        self.htmlval = Color.colordefs["colors"][name][3]
        self.description = Color.colordefs["colors"][name][4]

    def get_rgbval(self):
        """
        Get the RGB color values.
        """
        return self.rgbval

    def get_htmlval(self):
        """
        Get the HTML color values.
        """
        return self.htmlval

    def get_description(self):
        """
        Get the descriptive name of the color.
        """
        return self.description

    def get_hexval(self):
        """
        Get the color value string formatted in hexadecimal.
        """
        return f"0x{self.htmlval[1:]}"
