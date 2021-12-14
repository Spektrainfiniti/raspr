from typing import Union
from base import Service


class Torrent_File:
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


class TORRENT(Service):
    def __init__(self) -> None:
        super().__init__()
        self.__files = {}
        self.__torrent_files = {}

    @property
    def files(self):
        return self.__files

    @property
    def torrent_files(self):
        return self.__torrent_files

    @staticmethod
    def name():
        return "TORRENT"

    def func(self, src_ip, command, args = None):
        if command == "get_torrent_file":
            return self.get_torrent_file(args)
        if command == "create_torrent_file":
            return self.create_torrent_file(args)
        if command == "all_torrent_files":
            return self.torrent_files
        if command == "seed":
            return self.seed_data(args)
        if command == "all_files":
            return self.files
        if command == "download_torrent_file":
            return self.download_torrent_file(args)
        if command == "download_file":
            return self.download_file(args)
        if command == "get_shard":
            return self.get_shard(args)
        return "Error"

    def get_torrent_file(self, name):
        try:
            return self.torrent_files[name]
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

        params = {
            "addr" : self.comp.ip,
            "data" : data
        }
        if self.comp.ping(tracker_ip) not in ("No network", "Unknown host"):
            ans = self.comp.send(tracker_ip, "TORRENT", "create_torrent_file", params)
            self.files[data["file_name"]] = data["shards"]
            return ans
        return self.comp.ping(tracker_ip)

    def download_torrent_file(self, data : dict):
        tracker_ip = data["tracker_ip"]
        file_name = data["name"]
        return self.comp.send(tracker_ip, "TORRENT", "get_torrent_file", file_name)

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

    def download_shard(self, ip_seed, file_name, i):
        params = {
            "name" : file_name,
            "id" : i
        }
        return self.comp.send(ip_seed, "TORRENT", "get_shard", params)

    def get_shard(self, data : dict):
        file_name = data["name"]
        shard_number = data["id"]
        if file_name in self.files.keys():
            return self.files[file_name][shard_number]
        return "No file"

