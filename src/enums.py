import enum


class ResponseCode(enum.Enum):
    SUCCESS = 0
    BAD_REQUEST = 1
    ERROR = 2
    UNAUTHORIZED = 3
    NOT_FOUND = 4


class RequestType(enum.Enum):
    REGISTER = 0
    LOGIN = 1
    MESSAGE = 2
    DOWNLOAD_MESSAGE = 3