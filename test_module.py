import unittest
import phototools as pt
from unittest import mock

class FileSystemTest(unittest.TestCase):
    def setUp(self):
        self.all_files = [
            "td/plain/chess.jpg",
            "td/plain/jewel2.jpg",
            "td/plain/balloon.nef",
            "td/plain/nuthatch.orf"
        ]
        self.assertFilesExist()

    def tearDown(self):
        self.assertFilesExist()

    def assertFilesExist(self):
        from os import path
        for file in self.all_files:
            self.assertTrue(path.isfile(file), "'{}' must exist, make sure you unpacked the archive".format(file))

    def assertFileListEqual(self, list1, list2):
        import itertools
        import os
        for (a, b) in itertools.zip_longest(list1, list2):
            self.assertFalse(a is None, '{} has no match'.format(b))
            self.assertFalse(b is None, '{} has no match'.format(a))
            self.assertTrue(os.path.samefile(a, b), '{} and {} are different files'.format(a, b))

class TestAttributes(FileSystemTest):
    def test_get_imagehash(self):
        self.assertIsNone(pt.get_imagehash("td/not_an_image.txt"))
#       self.assertIsNotNone(pt.get_imagehash("td/plain/nuthatch.orf"))

    def test_date(self):
        self.assertEqual(pt.get_date("td/plain/chess.jpg").strftime("%Y %B"), "2013 August")
        self.assertEqual(pt.get_date("td/plain/jewel2.jpg").strftime("%Y %B"), "2016 November")
        self.assertEqual(pt.get_date("td/plain/balloon.nef").strftime("%Y %B"), "2016 November")
        self.assertEqual(pt.get_date("td/plain/nuthatch.orf").strftime("%Y %B"),"2019 October")
        
    def test_time_diff(self):
        time1 = pt.get_date("td/takes/jewel1.jpg")
        time2 = pt.get_date("td/plain/jewel2.jpg")
        time3 = pt.get_date("td/takes/jewel3.jpg")
        self.assertEqual(time1, time2)
        self.assertEqual(pt.time_diff(time2, time1), 0)
        self.assertEqual(pt.time_diff(time3, time1), 1)

    def test_panorama(self):
        self.assertTrue(pt.is_panorama("td/panorama/left.jpg", "td/panorama/right.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/right.jpg", "td/panorama/right.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/right.jpg", "td/panorama/left.jpg"))
        self.assertFalse(pt.is_panorama("td/panorama/left.jpg", None))
        self.assertFalse(pt.is_panorama("td/panorama/left.jpg", "td/plain/jewel2.jpg"))

class TestGenerators(FileSystemTest):
    def test_simple(self):
        self.assertFileListEqual(pt.raws("td/plain"),  ["td/plain/balloon.nef", "td/plain/nuthatch.orf"])
        self.assertFileListEqual(pt.jpegs("td/plain"), ["td/plain/chess.jpg", "td/plain/jewel2.jpg"])
        self.assertFileListEqual(pt.all("td/plain"),   self.all_files)

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

class TestMovers(FileSystemTest):
    def setUp(self):
        from os import path
        super(TestMovers, self).setUp()
        self.new_files = [
            'new/td/2013/August/chess.jpg',
            'new/td/2016/November/jewel2.jpg',
            'new/td/2016/November/balloon.nef',
            'new/td/2019/October/nuthatch.orf'
        ]
        self.new_dirs = [path.dirname(x) for x in self.new_files]

    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('os.makedirs')
    @mock.patch('shutil.move')
    def test_move(self, mock_move, mock_makedirs, mock_isfile):
        pt.move(pt.all, "td/plain", "new/td", format='%Y/%B')

        move_args = list(zip(*mock_move.call_args_list))[0]
        dirs_args = [args[0] for args in list(zip(*mock_makedirs.call_args_list))[0]]

        self.assertFileListEqual([args[0] for args in move_args], self.all_files)
        self.assertEqual([args[1] for args in move_args], self.new_files)
        self.assertEqual(dirs_args, self.new_dirs)

    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch('shutil.move')
    def test_move_nothing(self, mock_move, mock_makedirs, mock_isfile):
        pt.move(pt.all, "td/plain", "new/td")

        self.assertFalse(mock_makedirs.call_args_list)
        self.assertFalse(mock_move.call_args_list)
