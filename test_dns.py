from dns_prototype import *
import unittest


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


class TestDns(unittest.TestCase):
    def test_no_local_dns_db(self):
        comp = Comp()
        ans = comp.resolve("narfu.ru")
        self.assertEqual(ans, None)

    def test_no_anwser_in_local_db(self):
        comp = Comp()
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(db)
        self.assertIsNone(comp.resolve("narfu.com"))

    def test_answer_in_local_db(self):
        comp = Comp()
        db = DnsDb()
        db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(db)
        ans = comp.resolve("narfu.ru")
        self.assertEqual(ans, "192.168.0.1")

    def test_answer_from_dns_server_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("192.192.192.192")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "168.168.168.168"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "10.10.10.10")
        net.add_host(server, "192.192.192.192")

        ans = comp.resolve("ya.ru")
        self.assertEqual(ans, "168.168.168.168")

    def test_answer_from_dns_server_non_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("192.192.192.192")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "168.168.168.168"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "10.10.10.10")
        net.add_host(server, "192.192.192.192")

        ans = comp.resolveNonRecursive("ya.ru")
        self.assertEqual(ans, "168.168.168.168")

    def test_wrong_addr_of_dns_server(self):
        comp = Comp()
        comp.set_dns_db(DnsDb())
        comp.iface().set_dns_server("10.20.30.45")

        net = Network()
        net.add_host(comp, "11.12.13.14")

        ans = comp.resolve("ya.ru")
        self.assertIsNone(ans)

    def test_resolve_unknown_name_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "1.2.3.4"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("10.20.30.40")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "2.3.4.5"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "11.12.13.14")
        net.add_host(server, "10.20.30.40")

        ans = comp.resolve("ya.com")
        self.assertIsNone(ans)

    def test_resolve_unknown_name_non_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "1.2.3.4"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("10.20.30.40")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "2.3.4.5"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "11.12.13.14")
        net.add_host(server, "10.20.30.40")

        ans = comp.resolveNonRecursive("ya.com")
        self.assertIsNone(ans)
    
    def test_main_dns_resolve_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "1.2.3.4"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("10.20.30.40")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "2.3.4.5"))
        server.set_dns_db(server_db)
        server.iface().set_dns_server("20.30.40.50")

        main_server = Comp()
        main_server_local_db = DnsDb()
        main_server_local_db.add_record(Record("ya.com", "3.4.5.6"))
        main_server.set_dns_db(main_server_local_db)

        net = Network()
        net.add_host(comp, "11.12.13.14")
        net.add_host(server, "10.20.30.40")
        net.add_host(main_server, "20.30.40.50")

        ans = comp.resolve("ya.com")
        self.assertEqual(ans, "3.4.5.6")

    def test_main_dns_resolve_non_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "1.2.3.4"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("10.20.30.40")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "2.3.4.5"))
        server.set_dns_db(server_db)
        server.iface().set_dns_server("20.30.40.50")

        main_server = Comp()
        main_server_local_db = DnsDb()
        main_server_local_db.add_record(Record("ya.com", "3.4.5.6"))
        main_server.set_dns_db(main_server_local_db)

        net = Network()
        net.add_host(comp, "11.12.13.14")
        net.add_host(server, "10.20.30.40")
        net.add_host(main_server, "20.30.40.50")

        ans = comp.resolveNonRecursive("ya.com")
        self.assertEqual(ans, "3.4.5.6")

    def test_caching_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("192.192.192.192")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "168.168.168.168"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "10.10.10.10")
        net.add_host(server, "192.192.192.192")

        comp.resolve("ya.ru")
        ans = comp.localDb().num_records()
        self.assertEqual(ans, 2)

    def test_caching_non_recursive(self):
        comp = Comp()
        local_db = DnsDb()
        local_db.add_record(Record("narfu.ru", "192.168.0.1"))
        comp.set_dns_db(local_db)
        comp.iface().set_dns_server("192.192.192.192")

        server = Comp()
        server_db = DnsDb()
        server_db.add_record(Record("ya.ru", "168.168.168.168"))
        server.set_dns_db(server_db)

        net = Network()
        net.add_host(comp, "10.10.10.10")
        net.add_host(server, "192.192.192.192")

        comp.resolveNonRecursive("ya.ru")
        ans = comp.localDb().num_records()
        self.assertEqual(ans, 2)


if __name__ == '__main__':
    unittest.main()
