from typing import Any

class Comp:
    """Computer."""

    def __init__(self):
        self.__iface = NetworkInterface()
        self.__all_service = {}
        self.add_service(ST_LIB())

    def add_service(self, srv):
        self.all_service[srv.name()] = srv.func
        srv.set_comp(self)

    @property
    def all_service(self):
        return self.__all_service
    
    @property
    def iface(self) -> Any:
        """Return network interface."""
        return self.__iface

    def ping(self, addr : str) -> str:
        """Send ping to address."""
        return self.iface.ping(addr)

    def send(self, addr, name, command, args=None) -> str:
        """Send Data to address."""
        message = {
            "service" : name,
            "method" : command,
            "params" : args
        }
        if addr == "self":
            return self.define_func(addr, message)
        return self.iface.send([addr, self.ip, message])

    def get(self):
        """Get information from host."""
        msg = self.iface.get()
        if msg != "No message":
            return self.define_func(msg[1], msg[-1])

    def define_func(self, src_ip, msg):
            service = msg["service"]
            method_str = msg["method"]
            params = msg["params"]
            return self.all_service[service](src_ip, method_str, params)

    @property
    def ip(self) -> str:
        return self.iface.addr


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


class Service:

    def __init__(self) -> None:
        self.__comp = None

    def set_comp(self, comp):
        self.__comp = comp

    @property
    def comp(self):
        return self.__comp


class ST_LIB(Service):

    @staticmethod
    def name():
        return "ST_LIB"

    def func(self,src_ip, command, args = None):
        if command == "receive_message":
            return self.receive_message(src_ip, args)

    def receive_message(self, src_ip, params):
        return f"Data from {src_ip} has been received."

