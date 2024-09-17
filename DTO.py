from dataclasses import dataclass


@dataclass
class DTOCurrencyGet:
    id: int = None
    name: str = None
    code: str = None
    sign: str = None

    def to_dict(self):
        return self.__dict__


@dataclass
class DTOCurrencyPOST:
    id: int = None
    name: str = None
    code: str = None
    sign: str = None

    def to_dict(self):
        return self.__dict__