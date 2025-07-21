from enum import Enum

class Header(Enum):
    ACK = 0x0A
    DATA = 0x0D
    SYNC = 0x0F
