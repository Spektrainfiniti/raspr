from typing import Any


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

    def add_to_data(self, data : Any):
        """Add information to data in comp."""
        self.__data = data

    def get_ip(self) -> str:
        return self.iface().addr

    def print_data(self) -> Any:
        return self.__data


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
        return self.net.send(data, self.addr, addr)
