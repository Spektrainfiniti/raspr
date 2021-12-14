import unittest
from base import *
from dns_prototype import *

class TestRecord(unittest.TestCase):
    def test_record(self):
        rec = Record("narfu.ru", "192.168.0.1")

        ans = rec.get_addr()
        self.assertEqual(ans, "192.168.0.1")

        ans = rec.get_name()
        self.assertEqual(ans, "narfu.ru")


class TestDNS_DB(unittest.TestCase):
    def test_empty_db(self):
        db = DnsDb()
        ans = db.num_records()
        self.assertEqual(ans, 0)

    def test_db(self):
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        ans = db.num_records()
        self.assertEqual(ans, 1)

    def test_resolve_name_known(self):
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        ans = db.resolve("narfu.ru")
        self.assertEqual(ans, "192.168.0.1")

    def test_resolve_name_unknown(self):
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        ans = db.resolve("bfu.ru")
        self.assertIsNone(ans)

    def test_same_addresses_differ_names(self):
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        raised = False
        try:
            db.add_record(Record("29.ru", "192.168.0.1"))
        except ValueError:
            raised = True

        self.assertTrue(raised)


class TestDNS(unittest.TestCase):
    def test_no_local_dns_db(self):
        comp = Comp()
        comp.add_service(DNS())
        ans = comp.send("self", "DNS", "resolve", "narfu.ru")
        self.assertIsNone(ans)

    def test_no_anwser_in_local_db(self):
        comp = Comp()
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.add_service(DNS())
        comp.send("self", "DNS", "set_db", db)
        ans = comp.send("self", "DNS", "resolve", "narfu.com")

        self.assertIsNone(ans)

    def test_answer_in_local_db(self):
        comp = Comp()
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.add_service(DNS())
        comp.send("self", "DNS", "set_db", db)

        ans = comp.send("self", "DNS", "resolve", "narfu.ru")
        self.assertEqual(ans, "192.168.0.1")

    def test_resolve_in_local_db_and_dns(self):
        comp = Comp()
        server = Comp()
        net = Network()

        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "10.120.10.120"))

        comp.add_service(DNS())
        comp.send("self", "DNS", "set_db", local_db)
        comp.send("self", "DNS", "set_dns", "192.168.0.2")
        

        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")


        ans = comp.send("self", "DNS", "resolve", "narfu.ru")
        self.assertEqual(ans, "10.120.10.120")

    def test_answer_from_non_existant_dns_server_recursive(self):
        comp = Comp()
        server = Comp()
        net = Network()
        comp.add_service(DNS())
        server.add_service(DNS())

        server_db = DnsDb()
        server_db.add_record(Record("narfu.ru", "10.120.10.120"))

        comp.send("self", "DNS", "set_dns", "192.168.0.3")
        server.send("self", "DNS", "set_db", server_db)
        
        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")

        ans = comp.send("self", "DNS", "resolve", "narfu.ru")
        self.assertEqual(ans, "Unknown host")

    def test_answer_from_dns_server_recursive(self):
        comp = Comp()
        server = Comp()
        net = Network()
        comp.add_service(DNS())
        server.add_service(DNS())

        server_db = DnsDb()
        server_db.add_record(Record("narfu.ru", "10.120.10.120"))

        comp.send("self", "DNS", "set_dns", "192.168.0.2")
        server.send("self", "DNS", "set_db", server_db)
        
        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")

        ans = comp.send("self", "DNS", "resolve", "narfu.ru")
        self.assertEqual(ans, "10.120.10.120")

    def test_answer_from_dns_server_non_recursive(self):
        comp = Comp()
        comp.add_service(DNS())
        server = Comp()
        server.add_service(DNS())
        net = Network()

        server_db = DnsDb()
        server_db.add_record(Record("narfu.ru", "10.120.10.120"))
        comp.send("self", "DNS", "set_dns", "192.168.0.2")
        server.send("self", "DNS", "set_db", server_db)
        
        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")

        ans = comp.send("self", "DNS", "resolve_non_rec", "narfu.ru")
        self.assertEqual(ans, "10.120.10.120")

    def test_answer_from_non_existant_dns_server_non_recursive(self):
        comp = Comp()
        comp.add_service(DNS())
        server = Comp()
        server.add_service(DNS())
        net = Network()

        server_db = DnsDb()
        server_db.add_record(Record("narfu.ru", "10.120.10.120"))
        comp.send("self", "DNS", "set_dns", "192.168.0.3")
        server.send("self", "DNS", "set_db", server_db)
        

        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")

        ans = comp.send("self", "DNS", "resolve_non_rec", "narfu.ru")
        self.assertEqual(ans, "Unknown host")

    def test_main_dns_resolve_recursive(self):
        comp = Comp()
        comp.add_service(DNS())
        server = Comp()
        server.add_service(DNS())
        main_server = Comp()
        main_server.add_service(DNS())
        net = Network()

        local_db = DnsDb()
        server_db = DnsDb()
        main_server_db = DnsDb()

        local_db.add_record(Record("narfu.ru", "10.120.10.120"))
        server_db.add_record(Record("ya.ru", "10.10.10.10"))
        main_server_db.add_record(Record("29.ru", "100.100.100.100"))

        comp.send("self", "DNS", "set_db", local_db)
        server.send("self", "DNS", "set_db", server_db)
        main_server.send("self", "DNS", "set_db", main_server_db)

        comp.send("self", "DNS", "set_dns", "192.168.0.2")
        server.send("self", "DNS", "set_dns", "192.168.0.3")

        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")
        net.add_host(main_server, "192.168.0.3")

        ans = comp.send("self", "DNS", "resolve", "29.ru")
        self.assertEqual(ans, "100.100.100.100")

    def test_main_dns_resolve_non_recursive(self):
        comp = Comp()
        comp.add_service(DNS())
        server = Comp()
        server.add_service(DNS())
        main_server = Comp()
        main_server.add_service(DNS())
        net = Network()

        local_db = DnsDb()
        server_db = DnsDb()
        main_server_db = DnsDb()

        local_db.add_record(Record("narfu.ru", "10.120.10.120"))
        server_db.add_record(Record("ya.ru", "10.10.10.10"))
        main_server_db.add_record(Record("29.ru", "100.100.100.100"))

        comp.send("self", "DNS", "set_db", local_db)
        server.send("self", "DNS", "set_db", server_db)
        main_server.send("self", "DNS", "set_db", main_server_db)

        comp.send("self", "DNS", "set_dns", "192.168.0.2")
        server.send("self", "DNS", "set_dns", "192.168.0.3")

        net.add_host(comp, "192.168.0.1")
        net.add_host(server, "192.168.0.2")
        net.add_host(main_server, "192.168.0.3")

        ans = comp.send("self", "DNS", "resolve_non_rec", "29.ru")
        self.assertEqual(ans, "100.100.100.100")


if __name__ == '__main__':
    unittest.main()