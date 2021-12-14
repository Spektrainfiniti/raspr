from base import *
from torrent import *
import unittest


class TestTorrentFile(unittest.TestCase):
    def test_empty_file(self):
        file = Torrent_File()
        ans = file.get_file_name()
        self.assertIsNone(ans)

    def test_file(self):
        file = Torrent_File()
        file.set_file_name("test_info.py")
        file.set_file_size(1024)
        ans = file.get_file_name()
        self.assertEqual(ans, "test_info.py")


class Test_Tracker(unittest.TestCase):
    def test_empty_pool_torrent_files(self):
        tracker = Comp()
        tracker.add_service(TORRENT())
        ans = tracker.send("self", "TORRENT", "get_torrent_file", "test_info.py")
        self.assertEqual(ans, "No torrent file")

    def test_pool_torrent_files(self):
        tracker = Comp()
        tracker.add_service(TORRENT())

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params = {
                "addr" : "192.168.0.2",
                "data" : data
            }

        tracker.send("self", "TORRENT", "create_torrent_file", params)
        
        ans = tracker.send("self", "TORRENT", "get_torrent_file", "test_info.py")
        self.assertEqual(ans.get_number_shards(), 5)

    def test_count_torrent_files(self):
        tracker = Comp()
        tracker.add_service(TORRENT())

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params = {
                "addr" : "192.168.0.2",
                "data" : data
            }

        tracker.send("self", "TORRENT", "create_torrent_file", params)
        ans = tracker.send("self", "TORRENT", "all_torrent_files")
        self.assertEqual(len(ans), 1)

    def test_create_torrent_file_from_seed_in_net(self):
        seed = Comp()
        seed.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        ans = seed.send("self", "TORRENT", "seed", params)
        self.assertEqual(ans, "Torrent file created")

    def test_create_torrent_file_from_seed_not_in_net(self):
        seed = Comp()
        seed.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.3",
                "data" : data
            }

        ans = seed.send("self", "TORRENT", "seed", params)
        self.assertEqual(ans, "Unknown host")

    def test_seed_files_not_in_net(self):
        seed = Comp()
        seed.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.3",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", params)
        ans = seed.send("self", "TORRENT", "all_files")
        self.assertEqual(len(ans), 0)

    def test_seed_files_in_net(self):
        seed = Comp()
        seed.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", params)
        ans = seed.send("self", "TORRENT", "all_files")
        self.assertEqual(len(ans), 1)

    def test_pool_torrent_files_after_created_torrent_file(self):
        seed = Comp()
        seed.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", params)
        ans = tracker.send("self", "TORRENT", "all_torrent_files")
        self.assertEqual(len(ans), 1)

    def test_safe_torrent_file_from_tracker(self):
        tracker = Comp()
        tracker.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        net = Network()

        net.add_host(tracker, "192.168.0.1")
        net.add_host(peer, "192.168.0.3")
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "addr" : "192.168.0.2",
                "data" : data
            }

        tracker.send("self", "TORRENT", "create_torrent_file", params)

        params =  {
                "tracker_ip" : "192.168.0.1",
                "name" : "test_info.py"
            }

        ans = peer.send("self", "TORRENT", "download_torrent_file", params)
        self.assertEqual(ans.get_file_size(), 1024)

    def test_safe_non_existant_torrent_file_from_tracker(self):
        tracker = Comp()
        tracker.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        net = Network()

        net.add_host(tracker, "192.168.0.1")
        net.add_host(peer, "192.168.0.3")
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "addr" : "192.168.0.2",
                "data" : data
            }

        tracker.send("self", "TORRENT", "create_torrent_file", params)

        params =  {
                "tracker_ip" : "192.168.0.1",
                "name" : "test.py"
            }

        ans = peer.send("self", "TORRENT", "download_torrent_file", params)
        self.assertEqual(ans, "No torrent file")

    def test_peer_download_torrent_file(self):
        seed = Comp()
        seed.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", params)

        params =  {
                "tracker_ip" : "192.168.0.2",
                "name" : "test_info.py"
            }

        ans = peer.send("self", "TORRENT", "download_torrent_file", params)
        self.assertEqual(ans.get_file_size(), 1024)

    def test_peer_download_non_existant_torrent_file(self):
        seed = Comp()
        seed.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        params =  {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", params)

        params =  {
                "tracker_ip" : "192.168.0.2",
                "name" : "test.py"
            }

        ans = peer.send("self", "TORRENT", "download_torrent_file", params)
        self.assertEqual(ans, "No torrent file")

    def test_download_file(self):
        seed = Comp()
        seed.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        msg1 = {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", msg1)
    
        msg2 = {
                "tracker_ip" : "192.168.0.2",
                "name" : "test_info.py"
            }

        ans = peer.send("self", "TORRENT", "download_file", msg2)
        self.assertEqual(ans, "File saved")

    def test_download_non_existant_file(self):
        seed = Comp()
        seed.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        msg1 = {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }
        seed.send("self", "TORRENT", "seed", msg1)
    
        msg2 ={
                "tracker_ip" : "192.168.0.2",
                "name" : "test.py"
            }

        ans = peer.send('self', 'TORRENT', "download_file", msg2)
        self.assertEqual(ans, "The file is not distributed")

    def test_peer_downloads_files_after_safed(self):
        seed = Comp()
        seed.add_service(TORRENT())
        peer = Comp()
        peer.add_service(TORRENT())
        tracker = Comp()
        tracker.add_service(TORRENT())
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        msg1 = {
                "tracker_ip" : "192.168.0.2",
                "data" : data
            }

        seed.send("self", "TORRENT", "seed", msg1)
    
        msg2 = {
                "tracker_ip" : "192.168.0.2",
                "name" : "test_info.py"
            }

        peer.send("self", "TORRENT", "download_file", msg2)
        ans = peer.send("self", "TORRENT", "all_files")
        self.assertEqual(len(ans), 1)


if __name__ == '__main__':
    unittest.main()