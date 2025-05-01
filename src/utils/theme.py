from enum import Enum


class Theme(Enum):
    DARK_MODE = "#1E1E1E"  # Dark gray
    LIGHT_MODE = "#FFFFFF"  # White

    def __str__(self):
        return self.name
