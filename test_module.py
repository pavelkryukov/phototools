import unittest
import phototools as pt

class TestPhototools(unittest.TestCase):
    def assertFileListEqual(self, list1, list2):
        import itertools
        import os
        for (a, b) in itertools.zip_longest(list1, list2):
            self.assertFalse(a is None, '{} has no match'.format(b))
            self.assertFalse(b is None, '{} has no match'.format(a))
            self.assertTrue(os.path.samefile(a, b), '{} and {} are different files'.format(a, b))

    def test_get_new_name(self):
        self.assertEqual(pt.get_new_name("td/plain/chess.jpg",  "output"),  "output/2013/08 August/chess.jpg")
        self.assertEqual(pt.get_new_name("td/plain/balloon.nef", "output"), "output/2016/11 November/balloon.nef")
        self.assertEqual(pt.get_new_name("td/plain/jewel2.jpg",  "output"), "output/2016/11 November/jewel2.jpg")

    def test_instagram(self):
        self.assertFileListEqual(pt.instagram("td"), ["td/plain/chess.jpg"])

    def test_get_lists(self):
        self.assertFileListEqual(pt.nefs("td/plain"),  ["td/plain/balloon.nef"])
        self.assertFileListEqual(pt.jpegs("td/plain"), ["td/plain/chess.jpg", "td/plain/jewel2.jpg"])
        self.assertFileListEqual(pt.all("td/plain"),   ["td/plain/chess.jpg", "td/plain/jewel2.jpg", "td/plain/balloon.nef"])

    def test_get_takes_5(self):
        pt.config.TAKE_SIMILARITY_FACTOR = 5
        self.assertFileListEqual(pt.takes("td/takes"), [])

    def test_get_takes_15(self):
        pt.config.TAKE_SIMILARITY_FACTOR = 15
        self.assertFileListEqual(pt.takes("td/takes"), ["td/takes/jewel1.jpg", "td/takes/jewel3.jpg"])

    def test_get_duplcates(self):
        self.assertFileListEqual(pt.duplicates("td"), ["td/takes/jewel1.jpg"])