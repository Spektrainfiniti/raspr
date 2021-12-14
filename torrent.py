from typing import Union


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