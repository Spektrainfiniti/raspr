<<<<<<< HEAD
from typing import Any, Union
from dns_prototype import *
from torrent import Torrent_File
=======
from typing import Any
>>>>>>> parent of 583c0bf (Fix)


class Comp:
    """Computer."""

    def __init__(self):
        self.__iface : NetworkInterface = NetworkInterface()
        self.__data : Any = None

    def iface(self) -> Any:
        """Return network interface."""
        return self.__iface

    def ping(self, addr : str) -> str:
        """Send ping to address."""
        return self.iface().ping(addr)

    def send(self, data : Any, addr : str) -> str:
        """Send Data to address."""
        return self.iface().send(data, addr)

    def get(self, data : Any, src : str) -> str:
        """Get information from host."""
        self.add_to_data(data)
        return f"Data from {src} has been received."

<<<<<<< HEAD
    def create_message(self, dst_addr, type_msg, msg):
        return [dst_addr, self.ip, type_msg, msg]

#-------------------------------------------------------------------------------------------------------------------

    @property
    def dns(self):
        return self.iface.dns

    @property
    def localDb(self) -> Any:
        return self.__local_db

    def set_dns_db(self, db) -> None:
        self.__local_db = db

    def resolve(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if self.localDb:
            addr = self.localDb.resolve(name)
            if addr:
                return addr
        addr = self.iface.resolve(name)
        if addr:
            if self.localDb:
                self.localDb.add_record(Record(name, addr))
            else:
                db = DnsDb()
                db.add_record(Record(name, addr))
                self.set_dns_db(db)
        return addr

    def resolveNonRecursive(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if self.localDb:
            addr = self.localDb.resolve(name)
            if addr:
                return addr
        if self.dns:
            addr = self.__iface.resolveNonRecursive(self.dns, name)
            if addr:
                if type(addr) == list:
                    addr = addr[0]
                if self.localDb:
                    self.localDb.add_record(Record(name, addr))
                else:
                    db = DnsDb()
                    db.add_record(Record(name, addr))
                    self.set_dns_db(db)
            return addr
        return None
#-------------------------------------------------------------------------------------------------------------------
=======
    def add_to_data(self, data : Any):
        """Add information to data in comp."""
        self.__data = data

    def get_ip(self) -> str:
        return self.iface().addr

    def print_data(self) -> Any:
        return self.__data
>>>>>>> parent of 583c0bf (Fix)


class Network:
    """Network represents net."""

    def __init__(self):
        self.__hosts : dict[str, Comp]= {}

    def add_host(self, comp : Comp, addr : str) -> None:
        """Add host to net."""
        self.__hosts[addr] = comp
        comp.iface().setup(self, addr)

    def ping(self, src : str, dst : str) -> str:
        """Ping sends ping to host."""
        if dst in self.__hosts:
            return f"ping from {src} to {dst}"

        return "Unknown host"

    def send(self, data : Any, src : str, dst : str) -> str:
        """Data sends source to destination."""
        if dst in self.__hosts:
            return self.__hosts[dst].get(data, src)

        return "Unknown host"

    def number_hosts(self) -> int:
        return len(self.__hosts)


class NetworkInterface:
    """Network interface."""

    def __init__(self):
        self.net : Network = None
        self.addr : str = None

    def setup(self, net : Network , addr : str) -> None:
        """Set net and address to interface."""
        self.net = net
        self.addr = addr

    def ping(self, addr : str) -> str:
        """Send ping to address."""
        if not self.net:
            return "No network"
        return self.net.ping(self.addr, addr)

    def send(self, data : Any, addr : str):
        """Send Data to address."""
        if not self.net:
            return "No network"
<<<<<<< HEAD
        return self.net.add_message_to_pool(msg)

    def get(self):
        if not self.net:
            return "No network"
        if self.net.message_to(self.addr) > 0:
            message = self.net.message_pool[self.addr][-1]
            return message
        return "No message"

#-------------------------------------------------------------------------------------------------------------------

    @property
    def dns(self):
        return self.__dns
    
    def set_dns_server(self, addr : str) -> None:
        """Set DNS server."""
        self.__dns = addr

    def resolve(self, name : str) -> Union[None, str]:
        """Resolve name."""
        if not self.net:
            return None
        msg = [self.dns, self.addr, "resolve", name]
        return self.net.add_message_to_pool(msg)

    def resolveNonRecursive(self, dns : str, name : str):
        """Resolve name."""
        if not self.net:
            return None
        msg = [dns, self.addr, "resolve_non_rec", name]
        ans = self.net.add_message_to_pool(msg)
        self.ant.append(ans)
        if ans:
            if ans[1] == "IP":
                return [ans[0]]
            if ans[1] == "DNS":
                addr = self.resolveNonRecursive(ans[0], name)
                return addr[0]
        return ans

#-------------------------------------------------------------------------------------------------------------------
=======
        return self.net.send(data, self.addr, addr)
>>>>>>> parent of 583c0bf (Fix)
