from abc import ABCMeta, abstractmethod
from .stats import Stats


class Puller(metaclass=ABCMeta):
    """
    The base class for all the pullers.
    In order to implement a new puller one need to create
    a file under the puller directory. The name of the file should
    be the same like name in the config. The class should be named `Puller`.
    """
    def __init__(self):
        self.stats = None

    @abstractmethod
    async def pull(self):
        pass


class Pusher(metaclass=ABCMeta):
    """
    The base class for all the pushers.
    In order to implement a new puller one need to create
    a file under the puller directory. The name of the file should
    be the same like name in the config. The class should be named `Pusher`.
    """
    @abstractmethod
    async def push(self, stats: Stats, **kwargs):
        pass
