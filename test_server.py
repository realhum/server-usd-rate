from settings import ADDRESS, PORT
from server import get_usd_rate
import requests
import unittest


class TestServer(unittest.TestCase):
    def test_bad_request(self):
        r = requests.get("http://{}:{}".format(ADDRESS, PORT),
                         json={'usd': -10})
        self.assertEqual(r.status_code, 400)

    def test_media_type(self):
        r = requests.get("http://{}:{}".format(ADDRESS, PORT),
                         data="usd=10")
        self.assertEqual(r.status_code, 415)

    def test_get_request(self):
        data = {'usd': 10}
        r = requests.get("http://{}:{}".format(ADDRESS, PORT),
                         json=data)
        self.assertEqual(r.json()['rub'], 733.092)


class TestRate(unittest.TestCase):
    def test_get_usd_rate(self):
        self.assertEqual(get_usd_rate(), 73.3092)


if __name__ == '__main__':
    unittest.main()
