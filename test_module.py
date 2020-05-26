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
#       self.assertIsNotNone(pt.get_imagehash("td/plain/nuthatch.orf"))

    def test_date(self):
        time1 = pt.get_date("td/takes/jewel1.jpg")
        time2 = pt.get_date("td/plain/jewel2.jpg")
        time3 = pt.get_date("td/takes/jewel3.jpg")
        self.assertEqual(time1, time2)
        self.assertEqual(pt.time_diff(time2, time1), 0)
        self.assertEqual(pt.time_diff(time3, time1), 1)

    def test_get_new_name(self):
        self.assertEqual(pt.get_date("td/plain/chess.jpg").strftime("%Y %B"), "2013 August")
        self.assertEqual(pt.get_date("td/plain/jewel2.jpg").strftime("%Y %B"), "2016 November")
        self.assertEqual(pt.get_date("td/plain/balloon.nef").strftime("%Y %B"), "2016 November")
        self.assertEqual(pt.get_date("td/plain/nuthatch.orf").strftime("%Y %B"),"2019 October")

    def test_simple(self):
        self.assertFileListEqual(pt.raws("td/plain"),  ["td/plain/balloon.nef", "td/plain/nuthatch.orf"])
        self.assertFileListEqual(pt.jpegs("td/plain"), ["td/plain/chess.jpg", "td/plain/jewel2.jpg"])
        self.assertFileListEqual(pt.all("td/plain"),   ["td/plain/chess.jpg", "td/plain/jewel2.jpg", "td/plain/balloon.nef", "td/plain/nuthatch.orf"])

    def test_takes(self):
        self.assertFileListEqual(pt.takes(5)("td/takes"), [])
        self.assertFileListEqual(pt.takes(15)("td/takes"), ["td/takes/jewel1.jpg", "td/takes/jewel3.jpg"])

    def test_duplcates(self):
        self.assertFileListEqual(pt.duplicates("td"), ["td/takes/jewel1.jpg"])
        self.assertFileListEqual(pt.duplicates_only_hash("td"), ["td/takes/jewel1.jpg"])

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