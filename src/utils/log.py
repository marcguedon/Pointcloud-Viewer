from enum import Enum


class Log(Enum):
    SUCCESS = "green"
    INFO = "black"
    WARNING = "orange"
    ERROR = "red"

    def __str__(self):
        return self.name
