from abc import ABC, abstractmethod


class DatabaseConnector(ABC):


    @abstractmethod
    def __init__(self, connection_string: str):
        pass


@abstractmethod
def do_work(self, xml_request: str) -> str:
    pass
