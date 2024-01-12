from enum import Enum


class RGBColorOption(str, Enum):
    BLACK = "black"
    WHITE = "white"
    RED = "red"
    LIME = "lime"
    BLUE = "blue"
    YELLOW = "yellow"
    CYAN = "cyan"
    MAGENTA = "magenta"
    SILVER = "silver"
    GRAY = "gray"
    MAROON = "maroon"
    OLIVE = "olive"
    GREEN = "green"
    PURPLE = "purple"
    TEAL = "teal"
    NAVY = "navy"
    NONE = "none"

    def rgb_values(self):
        rgb_mapping = {
            RGBColorOption.BLACK: "0,0,0",
            RGBColorOption.WHITE: "255,255,255",
            RGBColorOption.RED: "255,0,0",
            RGBColorOption.LIME: "0,255,0",
            RGBColorOption.BLUE: "0,0,255",
            RGBColorOption.YELLOW: "255,255,0",
            RGBColorOption.CYAN: "0,255,255",
            RGBColorOption.MAGENTA: "255,0,255",
            RGBColorOption.SILVER: "192,192,192",
            RGBColorOption.GRAY: "128,128,128",
            RGBColorOption.MAROON: "128,0,0",
            RGBColorOption.OLIVE: "128,128,0",
            RGBColorOption.GREEN: "0,128,0",
            RGBColorOption.PURPLE: "128,0,128",
            RGBColorOption.TEAL: "0,128,128",
            RGBColorOption.NAVY: "0,0,128",
            RGBColorOption.NONE: None,
        }
        if self not in rgb_mapping:
            raise ValueError(f"RGB color {self} is not valid.")

        return rgb_mapping.get(self)

    def __str__(self):
        return self.value
