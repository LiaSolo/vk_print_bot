from enum import Enum, auto


class State(Enum):
    CHECK_USER = auto()
    WAIT_FOR_FILE = auto()
    PROCESS_FILE = auto()
    PRINT_SETTINGS = auto()
    WAIT_EXTRA_SETTINGS = auto()
    CHECK_LIMIT = auto()
    CANT_PRINT = auto()
    LIMIT_OK = auto()
    CHOOSE_PRINTER = auto()
    CHANGE_BAN = auto()
    ADMIN_MODE = auto()
    CHANGE_LIMIT = auto()
    ADD_PAPER = auto()
    HELP = auto()
    MAINTENANCE = auto()
    ASK_INFO = auto()
    ASK_COPIES = auto()
    CLEAR_QUEUE = auto()
