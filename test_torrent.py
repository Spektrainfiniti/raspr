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
        tracker = Tracker()
        ans = tracker.get_torrent_file("test_info.py")
        self.assertEqual(ans, "No torrent file")

    def test_pool_torrent_files(self):
        tracker = Tracker()
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }
        tracker.create_torrent_file("192.168.0.2", data)
        ans = tracker.get_torrent_file("test_info.py")
        self.assertEqual(ans.get_number_shards(), 5)

    def test_count_torrent_files(self):
        tracker = Tracker()
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }
        tracker.create_torrent_file("192.168.0.2", data)
        ans = tracker.all_torrent_files()
        self.assertEqual(len(ans), 1)

    def test_create_torrent_file_from_seed_in_net(self):
        seed = Seed()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        ans = seed.seed_data(data, "192.168.0.2")
        self.assertEqual(ans, "Torrent file created")

    def test_create_torrent_file_from_seed_not_in_net(self):
        seed = Seed()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        ans = seed.seed_data(data, "192.168.0.3")
        self.assertEqual(ans, "Unknown host")

    def test_seed_files_not_in_net(self):
        seed = Seed()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.3")
        ans = seed.pool_files()
        self.assertEqual(len(ans), 0)

    def test_seed_files_in_net(self):
        seed = Seed()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")
        ans = seed.pool_files()
        self.assertEqual(len(ans), 1)

    def test_pool_torrent_files_after_created_torrent_file(self):
        seed = Seed()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")
        ans = tracker.all_torrent_files()
        self.assertEqual(len(ans), 1)

    def test_safe_torrent_file_from_tracker(self):
        tracker = Tracker()
        peer = Peer()
        net = Network()

        net.add_host(tracker, "192.168.0.1")
        net.add_host(peer, "192.168.0.3")
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }
        tracker.create_torrent_file("192.168.0.2", data)    
        ans = peer.download_torrent_file("test_info.py", "192.168.0.1")
        self.assertEqual(ans.get_file_size(), 1024)

    def test_safe_non_existant_torrent_file_from_tracker(self):
        tracker = Tracker()
        peer = Peer()
        net = Network()

        net.add_host(tracker, "192.168.0.1")
        net.add_host(peer, "192.168.0.3")
        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }
        tracker.create_torrent_file("192.168.0.2", data)    
        ans = peer.download_torrent_file("test.py", "192.168.0.1")
        self.assertEqual(ans, "No torrent file")

    def test_peer_download_torrent_file(self):
        seed = Seed()
        peer = Peer()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")

        ans = peer.download_torrent_file("test_info.py", "192.168.0.2")
        self.assertEqual(ans.get_file_size(), 1024)

    def test_peer_download_non_existant_torrent_file(self):
        seed = Seed()
        peer = Peer()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")

        ans = peer.download_torrent_file("test.py", "192.168.0.2")
        self.assertEqual(ans, "No torrent file")

    def test_download_file(self):
        seed = Seed()
        peer = Peer()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")
        ans = peer.download_file("test_info.py", "192.168.0.2")
        self.assertEqual(ans, "File saved")

    def test_download_non_existant_file(self):
        seed = Seed()
        peer = Peer()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")
        ans = peer.download_file("test.py", "192.168.0.2")
        self.assertEqual(ans, "The file is not distributed")

    def test_peer_downloads_files_after_safed(self):
        seed = Seed()
        peer = Peer()
        tracker = Tracker()
        net = Network()

        net.add_host(seed, "192.168.0.1")
        net.add_host(tracker, "192.168.0.2")
        net.add_host(peer, "192.168.0.3")

        data = {
            "file_name" : "test_info.py",
            "file_size" : 1024,
            "shards" : ["123", "abc", "456", "def", "Ook."]
        }

        seed.seed_data(data, "192.168.0.2")
        peer.download_file("test_info.py", "192.168.0.2")
        ans = peer.get_download_files()
        self.assertEqual(len(ans), 1)

if __name__ == '__main__':
    unittest.main()