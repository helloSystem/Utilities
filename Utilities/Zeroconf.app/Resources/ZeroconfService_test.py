import unittest
from zeroconf import ZeroconfService

class TestCommandReader(unittest.TestCase):
    def test_1(self):
        service = ZeroconfService("foo server", "_http._tcp", "foo.local", "80")

        self.assertEqual(service.name, "foo server")
        self.assertEqual(service.service_type, "_http._tcp")
        self.assertEqual(service.hostname_with_domain, "foo.local")
        self.assertEqual(service.port, "80")
        self.assertEqual(service.url, "http://foo.local:80")
        self.assertEqual(service.__repr__(), "_http._tcp on foo.local:80")

if __name__ == "__main__":
    unittest.main()
