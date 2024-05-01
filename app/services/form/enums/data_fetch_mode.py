from enum import Enum


class DataFetchMode(Enum):
    STATIC = "STATIC"
    ONLOAD = "ONLOAD"
    ONCLICK = "ONCLICK"
    ONSEARCH = "ONSEARCH"
