from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from collections import UserDict


@dataclass(order=True, frozen=True)
class Transaction:
    """Class for a unified transaction"""
    reference: str
    timestamp: datetime
    transaction_type: str
    sum: float
    osnd: str
    sender_account: str
    sender_name: str


class Stats(UserDict, metaclass=ABCMeta):
    """Base class for all the Stats."""
    @property
    def accounts(self):
        return self.data.keys()

    @abstractmethod
    def transactions(self, account, real=True, done=True):
        pass
