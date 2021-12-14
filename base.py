from typing import Any, Union
from dns_prototype import *
from torrent import *


class Comp:
    """Computer."""

    def __init__(self):
        self.__iface = NetworkInterface()
        self.__torrent_files : dict[str, Torrent_File]= {}
        self.__files : dict = {}
        self.__local_db : Any = None
        self.__all_service = {
            "ST_LIB" : {
                "receive_message" : self.receive_message
            },
            "DNS" : {
                "resolve" : self.resolve,
                "resolve_non_rec" : self.resolveNonRecursive
            },
            "TORRENT" : {
                "get_torrent_file" : self.get_torrent_file,
                "create_torrent_file" : self.create_torrent_file,
                "seed_data" : self.seed_data,
                "download_torrent_file" : self.download_torrent_file,
                "download_file" : self.download_file,
                "get_shard" : self.get_shard
            }
        }

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

    def receive_message(self, params):
        src_ip = params["src_ip"]
        return f"Data from {src_ip} has been received."

    def send(self, msg, addr = None) -> str:
        """Send Data to address."""
        if not addr:
            return self.define_func(msg)
        message = self.create_message(addr, msg)
        return self.iface.send(message)

    def get(self):
        """Get information from host."""
        msg = self.iface.get()
        if msg != "No message":
            return self.define_func(msg[-1])

    def define_func(self, msg):
            service = msg["service"]
            method_str = msg["method"]
            params = msg["params"]
            return self.all_service[service][method_str](params)

    @property
    def ip(self) -> str:
        return self.iface.addr

    def create_message(self, dst_addr, msg):
        msg["params"].update(src_ip = self.ip)
        return [dst_addr, self.ip, msg]

#----------------------------------------------------------------------------------------

    @property
    def dns(self):
        return self.iface.dns

    @property
    def localDb(self) -> Any:
        return self.__local_db

    def set_dns_db(self, db) -> None:
        self.__local_db = db

    def resolve(self, name : dict):
        """Resolve name."""
        name = name["name"]
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

    def resolveNonRecursive(self, name : dict):
        """Resolve name."""
        name_s  = name["name"]
        if self.localDb:
            addr = self.localDb.resolve(name_s)
            if addr:
                return [addr, "IP"]
        if self.dns:
            try:
                if name["type_addr"] == "DNS":
                    return [self.dns, "DNS"]
            except:
                addr = self.iface.resolveNonRecursive(self.dns, name)
                if addr:
                    if self.localDb:
                        self.localDb.add_record(Record(name_s, addr))
                    else:
                        db = DnsDb()
                        db.add_record(Record(name_s, addr))
                        self.set_dns_db(db)
                return addr
        return None

#----------------------------------------------------------------------------------------

    @property
    def torrent_files(self):
        return self.__torrent_files

    @property
    def files(self):
        return self.__files

    def get_torrent_file(self, name : dict):
        try:
            return self.torrent_files[name["name"]]
        except:
            return "No torrent file"

    def create_torrent_file(self, data : dict) -> str:
        torrent_file = Torrent_File()
        torrent_file.set_ip_seed(data["addr"])
        data = data["data"]
        torrent_file.set_file_name(data["file_name"])
        torrent_file.set_file_size(data["file_size"])
        try:
            torrent_file.set_number_shards(data["number_shards"])
        except:
            torrent_file.set_number_shards(len(data["shards"]))
        self.torrent_files[data["file_name"]] = torrent_file
        return "Torrent file created"

    def seed_data(self, data : dict):
        tracker_ip = data["tracker_ip"]
        data = data["data"]
        if self.ping(tracker_ip) not in ("No network", "Unknown host"):
            self.files[data["file_name"]] = data["shards"]
            metadata = self.create_metadata_from_data(data)

            msg = {
                "service" : "TORRENT",
                "method" : "create_torrent_file",
                "params" : {
                    "addr" : self.ip,
                    "data" : metadata
                }
            }

            return self.send(msg, tracker_ip)
        return self.ping(tracker_ip)

    def create_metadata_from_data(self, data : dict) -> dict:
        metadata = {
            "file_name" : data["file_name"],
            "file_size" : data["file_size"],
            "number_shards" : len(data["shards"])
        }
        return metadata

    def download_torrent_file(self, data : dict):
        name = data["name"]
        tracker_ip = data["tracker_ip"]
        msg = {
            "service" : "TORRENT",
            "method" : "get_torrent_file",
            "params" : {
                "name" : name 
            }
        }

        return self.send(msg, tracker_ip)

    def download_file(self, data : dict):
        file_name = data["name"]
        torrent_file = self.download_torrent_file(data)
        if torrent_file != "No torrent file":
            ip_seed = torrent_file.get_ip_seed()
            number_shards = torrent_file.get_number_shards()
            self.files[file_name] = [0 for _ in range(number_shards)]

            for i in range (number_shards):
                shard = self.download_shard(ip_seed, file_name, i)
                if shard not in ("No network", "Unknown host", "No file"):
                    self.files[file_name][i] = shard
            return "File saved"
        return "The file is not distributed"

    def download_shard(self, ip_seed : str, file_name : str, shard_number : int) -> Any:

        msg = {
            "service" : "TORRENT",
            "method" : "get_shard",
            "params" : {
                "name" : file_name,
                "id_shard" : shard_number
            }
        }

        return self.send(msg, ip_seed)

    def get_shard(self, data : dict) -> Any:
        file_name = data["name"]
        shard_number = data["id_shard"]
        if file_name in self.files.keys():
            return self.files[file_name][shard_number]
        return "No file"
    

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
        self.__dns : Union[None, str] = None

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

#----------------------------------------------------------------------------------------

    @property
    def dns(self):
        return self.__dns
    
    def set_dns_server(self, addr : str) -> None:
        """Set DNS server."""
        self.__dns = addr

    def resolve(self, name : str):
        """Resolve name."""
        if not self.net:
            return None

        template = {
            "service" : "DNS",
            "method" : "resolve",
            "params" : {
                "name" : name
            }
        }

        msg = [self.dns, self.addr, template]
        return self.net.add_message_to_pool(msg)

    def resolveNonRecursive(self, dns : str, name):
        """Resolve name."""
        if not self.net:
            return None

        template = {
            "service" : "DNS",
            "method" : "resolve_non_rec",
            "params" : {
                "name" : name["name"],
                "type_addr" : "DNS",
                "addr" : self.dns
            }
        }
        
        msg = [dns, self.addr, template]
        ans = self.net.add_message_to_pool(msg)
        if ans:
            if ans[1] == "IP":
                return ans[0]
            if ans[1] == "DNS":
                addr = self.resolveNonRecursive(ans[0], name)
                return addr
        return ans

#----------------------------------------------------------------------------------------