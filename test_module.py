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

    def test_get_imagehash(self):
        self.assertIsNone(pt.get_imagehash("td/not_an_image.txt"))

    def test_get_new_name(self):
        self.assertEqual(pt.get_new_name("td/plain/chess.jpg",  "output"),  "output/2013/08 August/chess.jpg")
        self.assertEqual(pt.get_new_name("td/plain/balloon.nef", "output"), "output/2016/11 November/balloon.nef")
        self.assertEqual(pt.get_new_name("td/plain/jewel2.jpg",  "output"), "output/2016/11 November/jewel2.jpg")

    def test_simple(self):
        self.assertFileListEqual(pt.nefs("td/plain"),  ["td/plain/balloon.nef"])
        self.assertFileListEqual(pt.jpegs("td/plain"), ["td/plain/chess.jpg", "td/plain/jewel2.jpg"])
        self.assertFileListEqual(pt.all("td/plain"),   ["td/plain/chess.jpg", "td/plain/jewel2.jpg", "td/plain/balloon.nef"])

    def test_takes(self):
        self.assertFileListEqual(pt.takes(5)("td/takes"), [])
        self.assertFileListEqual(pt.takes(15)("td/takes"), ["td/takes/jewel1.jpg", "td/takes/jewel3.jpg"])

    def test_duplcates(self):
        self.assertFileListEqual(pt.duplicates("td"), ["td/takes/jewel1.jpg"])

    def test_instagram(self):
        self.assertFileListEqual(pt.instagram("td"), ["td/panorama/left.jpg", "td/panorama/right.jpg", "td/plain/chess.jpg"])

    def test_nefs_with_jpg(self):
        self.assertFileListEqual(pt.nefs_with_jpg("td"), [])

    def test_panorama(self):
        self.assertTrue(pt.is_panorama("td/panorama/left.jpg", "td/panorama/right.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/right.jpg", "td/panorama/right.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/right.jpg", "td/panorama/left.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/left.jpg", None))
        self.assertFalse(pt.is_panorama("td/panorama/left.jpg", "td/plain/jewel2.jpg"))