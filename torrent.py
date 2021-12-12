from typing import Any, Dict, Union
from base import Comp, Network, NetworkInterface


class Torrent_File():
    def __init__(self):
        self.__file_name : Union[None, str] = None
        self.__file_size : Union[None, int] = None
        self.__number_shards : Union[None, int] = None
        self.__ip_seed : Union[None, str] = None

    def get_file_name(self) -> Union[None, str]:
        return self.__file_name

    def get_file_size(self) -> Union[None, str]:
        return self.__file_size

    def get_number_shards(self) -> Union[None, str]:
        return self.__number_shards

    def get_ip_seed(self) -> Union[None, str]:
        return self.__ip_seed

    def set_file_name(self, name) -> None:
        self.__file_name = name

    def set_file_size(self, size) -> None:
        self.__file_size = size

    def set_number_shards(self, number_shards) -> None:
        self.__number_shards = number_shards

    def set_ip_seed(self, ip_seed) -> None:
        self.__ip_seed = ip_seed


class NetworkInterface(NetworkInterface):
    def __init__(self):
        super().__init__()

    def torrent_tracker_say_create_torrent_file(self, data : dict, addr : str) -> str:
        if not self.net:
            return "No network"
        return self.net.torrent_tracker_say_create_torrent_file(self.addr, addr, data)

    def download_torrent_file(self, file_name : str, ip_tracker : str) -> Union[str, Torrent_File]:
        if not self.net:
            return "No network"
        return self.net.download_torrent_file(ip_tracker, file_name)

    def download_shard(self, ip_seed : str, file_name : str, number_of_shard : int) -> Any:
        if not self.net:
            return "No network"
        return self.net.download_shard(ip_seed, file_name, number_of_shard)


class Comp(Comp):
    def __init__(self):
        self.__iface : NetworkInterface = NetworkInterface()
        self.__data : Any = None


class Network(Network):
    def __init__(self):
        super().__init__()

    def torrent_tracker_say_create_torrent_file(self, src_addr : str, dst_addr : str, data : dict) -> str:
        if dst_addr in self.__hosts:
            return self.__hosts[dst_addr].create_torrent_file(src_addr, data)
        return "Unknown host"

    def download_torrent_file(self, ip_tracker : str, file_name : str) -> Union[str, Torrent_File]:
        if ip_tracker in self.__hosts:
            return self.__hosts[ip_tracker].get_torrent_file(file_name)
        return "Unknown host"

    def download_shard(self, ip_seed : str, file_name : str, number_of_shard : int) -> Any:
        if ip_seed in self.__hosts:
            return self.__hosts[ip_seed].get_shard(file_name, number_of_shard)
        return "Unknown host"


class Peer(Comp):
    def __init__(self):
        super().__init__()
        self.downloads_files : dict[str, list] = {}

    def download_torrent_file(self, file_name : str, ip_tracker : str) -> Union[str, Torrent_File]:
        if self.ping(ip_tracker) not in ("No network", "Unknown host"):
            return self.iface().download_torrent_file(file_name, ip_tracker)
        return self.ping(ip_tracker)

    def download_file(self, file_name : str, ip_tracker : str) -> str:
        torrent_file = self.download_torrent_file(file_name, ip_tracker)
        if torrent_file != "No torrent file":
            ip_seed = torrent_file.get_ip_seed()
            number_shards = torrent_file.get_number_shards()
            self.downloads_files[file_name] = [0 for _ in range(number_shards)]

            for i in range (number_shards):
                shard = self.download_shard(ip_seed, file_name, i)
                if shard not in ("No network", "Unknown host", "No file"):
                    self.downloads_files[file_name][i] = shard
            return "File saved"
        return "The file is not distributed"

    def download_shard(self, ip_seed : str, file_name : str, number_of_shard : int) -> Any:
        return self.iface().download_shard(ip_seed, file_name, number_of_shard)

    def get_download_files(self) -> Dict[str, list]:
        return self.downloads_files


class Seed(Comp):
    def __init__(self):
        super().__init__()
        self.__pool_files : dict[str, list] = {}

    def seed_data(self, data : dict, ip_tracker : str) -> str:
        if self.ping(ip_tracker) not in ("No network", "Unknown host"):
            self.pool_files()[data["file_name"]] = data["shards"]
            metadata = self.create_metadata_from_data(data)
            return self.iface().torrent_tracker_say_create_torrent_file(metadata, ip_tracker)
        return self.ping(ip_tracker)

    def create_metadata_from_data(self, data : dict) -> dict:
        metadata = {
            "file_name" : data["file_name"],
            "file_size" : data["file_size"],
            "number_shards" : len(data["shards"])
        }
        return metadata

    def pool_files(self) -> Dict[str, list]:
        return self.__pool_files

    def get_shard(self, file_name : str, number_of_shard : int) -> Any:
        if file_name in self.pool_files().keys():
            return self.pool_files()[file_name][number_of_shard]
        return "No file"


class Tracker(Comp):
    def __init__(self):
        super().__init__()
        self.pull_torrent_files : dict[str, Torrent_File] = {}

    def create_torrent_file(self, src_addr : str, data : dict) -> str:
        torrent_file = Torrent_File()
        torrent_file.set_ip_seed(src_addr)
        torrent_file.set_file_name(data["file_name"])
        torrent_file.set_file_size(data["file_size"])
        try:
            torrent_file.set_number_shards(data["number_shards"])
        except:
            torrent_file.set_number_shards(len(data["shards"]))
        self.pull_torrent_files[data["file_name"]] = torrent_file
        return "Torrent file created"

    def get_torrent_file(self, file_name : str) -> Union[str, Torrent_File]:
        if file_name in self.pull_torrent_files.keys():
            return self.pull_torrent_files[file_name]
        return "No torrent file"

    def all_torrent_files(self):
        return self.pull_torrent_files.keys()

