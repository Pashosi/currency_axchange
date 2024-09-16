from dataclasses import dataclass

@dataclass
class DTOCurrencyGet:
    id: int
    name: str
    code: str
    sign: str

    def to_dict(self):
        return self.__dict__