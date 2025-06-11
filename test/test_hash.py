import unittest

from utils.hash import hash_url

class TestHashUrlFunctions(unittest.TestCase):
    def test_whatsapp_url(self):
        url = "https://web.whatsapp.com/"
        expected = "47359004657585"
        result = hash_url(url)
        self.assertEqual(result, expected)

    def test_reddit_url(self):
        url = "https://www.reddit.com/"
        expected = "47359719085711"
        result = hash_url(url)
        self.assertEqual(result, expected)

    def test_wikipedia_url(self):
        url = "https://en.wikipedia.org/wiki/Main_Page"
        expected = "47359216927712"
        result = hash_url(url)
        self.assertEqual(result, expected)