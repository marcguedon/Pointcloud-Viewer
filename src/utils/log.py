from enum import Enum


class Log(Enum):
    SUCCESS = 0
    INFO = 1
    WARNING = 2
    ERROR = 3

    def __str__(self):
        return self.name
