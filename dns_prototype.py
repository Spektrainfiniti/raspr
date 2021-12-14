from typing import Any, Union
from base import Service


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


class DNS(Service):
    def __init__(self) -> None:
        super().__init__()
        self.__local_db = None
        self.__dns = None

    @staticmethod
    def name():
        return "DNS"

    def func(self, src_ip, command, args = None):
        if command == "resolve":
            return self.resolve(args)
        if command =="set_dns":
            return self.set_dns_server(args)
        if command =="set_db":
            return self.set_dns_db(args)
        if command == "resolve_non_rec":
            return self.resolveNonRecursive(src_ip, args)
        return "Error"

    def resolve(self, name):
        ans = self.check_in_local_db(name)
        if not ans:
            if self.dns:
                if not self.comp.iface.net:
                    return None
                ans = self.comp.send(self.dns, "DNS", "resolve", name)
                if ans:
                    if self.local_db:
                        self.local_db.add_record(Record(name, ans))
                    else:
                        self.set_dns_db(DnsDb())
                        self.local_db.add_record(Record(name, ans))

        return ans

    def resolveNonRecursive(self,src_ip, name):
        ans = self.check_in_local_db(name)
        if ans:
            return [ans, "IP"]

        if self.dns:
            if src_ip not in ("self"):
                return [self.dns, "DNS"]

        ans = self.comp.send(self.dns, "DNS", "resolve_non_rec", name)
        if ans:
            if ans[-1] == "IP":
                return ans[0]
            if ans[-1] == "DNS":
                addr = self.comp.send(ans[0], "DNS", "resolve_non_rec", name)
                return addr[0]
        return ans

    def set_dns_server(self, addr):
        self.__dns = addr

    def set_dns_db(self, db):
        self.__local_db = db

    @property
    def local_db(self):
        return self.__local_db

    @property
    def dns(self):
        return self.__dns

    def check_in_local_db(self, name):
        if self.local_db:
            return self.local_db.resolve(name)
        return None
