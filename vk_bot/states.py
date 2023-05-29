from enum import Enum, auto


class State(Enum):
    CHECK_USER = auto()
    WAIT_FILE = auto()
    PROCESS_FILE = auto()
    PRINT_SETTINGS = auto()
    WAIT_EXTRA_SETTINGS = auto()
    CHECK_LIMIT = auto()
    CANT_PRINT = auto()
    CHECK_DONE = auto()
    CHOOSE_PRINTER = auto()
    CHANGE_BAN = auto()
    ADMIN_MODE = auto()
    CHANGE_LIMIT = auto()
    ADD_PAPER = auto()
    HELP = auto()
    ASK_INFO = auto()
    ASK_COPIES = auto()
    CLEAR_QUEUE = auto()
    ACTIVE_SESSION = auto()
    REGISTRATION = auto()
