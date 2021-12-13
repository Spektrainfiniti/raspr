from typing import Any, Union
from dns_prototype import *
from torrent import Torrent_File


class Comp:
    """Computer."""

    def __init__(self):
        self.__iface = NetworkInterface()
        self.__data : Any = None
        self.__local_db : Any = None
    
    @property
    def iface(self) -> Any:
        """Return network interface."""
        return self.__iface

    def ping(self, addr : str) -> str:
        """Send ping to address."""
        return self.iface.ping(addr)

    def send(self, addr : str, type_msg, msg) -> str:
        """Send Data to address."""
        message = self.create_message(addr,type_msg, msg)
        return self.iface.send(message)

    def get(self):
        """Get information from host."""
        msg = self.iface.get()
        if msg != "No message":
            if msg[2] == "text":
                return f"Data from {msg[1]} has been received."
            elif msg[2] == "resolve":
                return self.resolve(msg[-1])
            elif msg[2] == "resolve_non_rec":
                name = msg[-1]
                if self.localDb:
                    addr = self.localDb.resolve(name)
                    if addr:
                        return [addr, "IP"]
                if self.dns:
                    return [self.dns, "DNS"]
                return None

    @property
    def ip(self) -> str:
        return self.iface.addr

    @property
    def data(self) -> Any:
        return self.__data

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


class Network:
    """Network represents net."""

    def __init__(self):
        self.__hosts : dict[str, Comp]= {}
        self.message_pool : dict[str, list]= {}

    def add_host(self, comp : Comp, addr : str) -> None:
        """Add host to net."""
        self.__hosts[addr] = comp
        comp.iface.setup(self, addr)
        self.message_pool[addr] = []

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

    def add_message_to_pool(self, msg):
        try:
            self.message_pool[msg[0]].append(msg)
        except KeyError:
            return "Unknown host"
        if msg[0] in self.__hosts:
            ans = self.__hosts[msg[0]].get()
            self.message_pool[msg[0]].pop()
            return ans
        return "Message added in pool"

    def number_hosts(self) -> int:
        return len(self.__hosts)

    def message_to(self, addr):
        return len(self.message_pool[addr])


class NetworkInterface:
    """Network interface."""

    def __init__(self):
        self.net : Network = None
        self.addr : str = None
        self.__dns : Union[None, str] = None
        self.ant = []

    def setup(self, net : Network , addr : str) -> None:
        """Set net and address to interface."""
        self.net = net
        self.addr = addr

    def ping(self, addr : str) -> str:
        """Send ping to address."""
        if not self.net:
            return "No network"
        return self.net.ping(self.addr, addr)

    def send(self, msg : list):
        """Send Data to address."""
        if not self.net:
            return "No network"
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
