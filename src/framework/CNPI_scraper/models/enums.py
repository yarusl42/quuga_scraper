from enum import Enum


class Status(Enum):
    PENDING = 'pending'
    ERROR = 'error'
    FAILURE = 'failure'
    DONE = 'done'
    DONEERROR = 'doneerror'
