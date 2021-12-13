from typing import Union

class Record:
    """Single DNS record."""

    def __init__(self, name : str, addr : str):
        self.__name = name
        self.__addr = addr

    def get_name(self) -> str:
        return self.__name

    def get_addr(self) -> str:
        return self.__addr


class DnsDb:
    """DNS database."""

    def __init__(self):
        self.__records : dict[str, Record] = {}
        self.__addrs : dict[str, bool] = {}

    def num_records(self) -> int:
        """Return number of records."""
        return len(self.__records)

    def add_record(self, record : Record) -> None:
        """Add record."""
        self.__check_record(record)
        self.__records[record.get_name()] = record

    def resolve(self, name : str) -> Union[None, str]:
        """Return IP address by name."""
        try:
            return self.__records[name].get_addr()
        except KeyError:
            return None

    def __check_record(self, record : Record) -> None:
        if record.get_addr() in self.__addrs:
            raise ValueError("Duplicated address")
        self.__addrs[record.get_addr()] = True
