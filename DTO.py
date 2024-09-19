import json
from dataclasses import dataclass
from decimal import Decimal


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


@dataclass
class DTOExchangeRatesGET:
    id: int = None
    baseCurrency: DTOCurrencyGet = None
    targetCurrency: DTOCurrencyGet = None
    rate: Decimal = None

    def to_dict(self):
        return {
            "id": self.id,
            "baseCurrency": self.baseCurrency.to_dict(),
            "targetCurrency": self.targetCurrency.to_dict(),
            "rate": self.rate
        }


@dataclass
class DTOExchangeRatesPOST:
    baseCurrency: int
    targetCurrency: int
    rate: Decimal

@dataclass
class DTOExchangeRatesPUTCH:
    baseCurrency: str
    targetCurrency: str
    rate: Decimal