from enum import Enum


class Risk(str, Enum):
    READ = "read"
    WRITE = "write"
    SENSITIVE = "sensitive"
    DESTRUCTIVE = "destructive"


def requires_approval(risk: Risk) -> bool:
    return risk != Risk.READ
