from typing import Any, Union
from base import Comp as com, Network as net, NetworkInterface as netint


class NetworkInterface(netint):
    def __init__(self):
        super().__init__()
        self.dns : Union[None, str] = None

    def set_dns_server(self, addr : str) -> None:
        """Set DNS server."""
        self.dns = addr

    def resolve(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if not self.net:
            return None
        return self.net.resolve(self.dns, name)

    def resolveNonRecursive(self, dns : str, name : str) -> Union[None, str]:
        """Resolve name."""
        if not self.net:
            return "No network"
        ans = self.net.resolveNonRecursive(dns, name)
        if ans:
            if ans[1] == "IP":
                return ans[0]
            if ans[1] == "DNS":
                ans = self.resolveNonRecursive(ans[0], name)
                return ans[0]
        return ans


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


class Comp(com):
    def __init__(self):
        self.__iface = NetworkInterface()
        self.__local_db : Union[None, DnsDb] = None
        self.__data : Any = None
    
    def localDb(self) -> Union[None, DnsDb]:
        return self.__local_db

    def set_dns_db(self, db : DnsDb) -> None:
        self.__local_db = db

    def resolve(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if self.__local_db:
            addr = self.__local_db.resolve(name)
            if addr:
                return addr
        addr = self.iface().resolve(name)
        if addr:
            self.localDb().add_record(Record(name, addr))
        return addr

    def resolveNonRecursive(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if self.__local_db:
            addr = self.__local_db.resolve(name)
            if addr:
                return addr
        if self.dns():
            ans = self.__iface.resolveNonRecursive(self.dns(), name)
            if ans != "No network" and ans:
                self.localDb().add_record(Record(name, ans))
            return ans
        return None

    def dns(self):
        return self.iface().dns


class Network(net):
    #Recursive DNS
    def resolve(self, dns_addr : str, name : str) -> Union[None, str]:
        try:
            return self.__hosts[dns_addr].resolve(name)
        except KeyError:
            return None

    #NonRecursive DNS
    def resolveNonRecursive(self, dns_addr : str, name : str) -> Union[None, str]:
        if self.__hosts[dns_addr].resolveNonRecursive(name):
            addr = self.__hosts[dns_addr].resolveNonRecursive(name)
            if addr: 
                return [addr, "IP"]
        if  self.__hosts[dns_addr].dns():
            return [self.__hosts[dns_addr].dns(), "DNS"]
        return None
