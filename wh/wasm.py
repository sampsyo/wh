import enum
from dataclasses import dataclass

MAGIC = b'\0asm'
VERSION = b'\x01\0\0\0'


class SectionId(enum.IntEnum):
    CUSTOM = 0
    TYPE = 1
    IMPORT = 2
    FUNCTION = 3
    TABLE = 4
    MEMORY = 5
    GLOBAL = 6
    EXPORT = 7
    START = 8
    ELEMENT = 9
    CODE = 10
    DATA = 11
    DATA_COUNT = 12


@dataclass(frozen=True)
class SectionHeader:
    id: SectionId
    size: int
