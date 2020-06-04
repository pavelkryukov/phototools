#!/usr/bin/python3
#
# Copyright (c) 2020 Pavel I. Kryukov
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

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
        self.directories = [
            'td/plain/empty_dir',
            'td/plain/empty',
            'td/plain/empty/empty',
            'td/plain/empty/empty2',
        ]
        self.assertFilesExist()

    def tearDown(self):
        self.assertFilesExist()

    def assertFilesExist(self):
        from os import path
        for file in self.all_files:
            self.assertTrue(path.isfile(file), "'{}' must exist, make sure you unpacked the archive".format(file))
        for d in self.directories:
            self.assertTrue(path.isdir(d), "'{}' must exist, make sure you unpacked the archive".format(d))

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
        self.assertEqual(pt.get_date("td/plain/chess.jpg").strftime("%Y %B"),    "2013 August")
        self.assertEqual(pt.get_date("td/plain/jewel2.jpg").strftime("%Y %B"),   "2016 November")
        self.assertEqual(pt.get_date("td/plain/balloon.nef").strftime("%Y %B"),  "2016 November")
        self.assertEqual(pt.get_date("td/plain/nuthatch.orf").strftime("%Y %B"), "2019 October")

    def test_time_diff(self):
        time1 = pt.get_date("td/takes/jewel1.jpg")
        time2 = pt.get_date("td/plain/jewel2.jpg")
        time3 = pt.get_date("td/takes/jewel3.jpg")
        self.assertEqual(time1, time2)
        self.assertEqual(pt.time_diff(time2, time1), 0)
        self.assertEqual(pt.time_diff(time3, time1), 1)

    def test_time_diff_different_formats(self):
        orf_time = pt.get_date("td/takes/zanaves.orf")
        jpg_time = pt.get_date("td/takes/zanaves.jpg")
        self.assertEqual(orf_time, jpg_time)

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
        self.assertFileListEqual(pt.nefs_with_jpg("td"), ["td/takes/zanaves.jpg", "td/takes/zanaves.orf"])


class TestMovers(FileSystemTest):
    def get_arguments_list(self, mock, index):
        return [args[index] for args in list(zip(*mock.call_args_list))[0]]

    @mock.patch('os.removedirs')
    @mock.patch('os.path.isfile', return_value=False)
    @mock.patch('os.makedirs')
    @mock.patch('shutil.move')
    def test_move(self, mock_move, mock_makedirs, mock_isfile, mock_removedirs):
        import os
        pt.move(pt.all, "td/plain", "new/td", format='%Y/%B')

        new_files = [
            'new/td/2013/August/chess.jpg',
            'new/td/2016/November/jewel2.jpg',
            'new/td/2016/November/balloon.nef',
            'new/td/2019/October/nuthatch.orf'
        ]
        new_dirs = [os.path.dirname(x) for x in new_files]

        self.assertFileListEqual(self.get_arguments_list(mock_move, 0), self.all_files)
        self.assertEqual(self.get_arguments_list(mock_move, 1), new_files)
        self.assertEqual(self.get_arguments_list(mock_makedirs, 0), new_dirs)
        self.assertFileListEqual(sorted(self.get_arguments_list(mock_removedirs, 0)), ['td/plain/empty', 'td/plain/empty_dir'])

    @mock.patch('os.removedirs')
    @mock.patch('os.path.isfile', return_value=True)
    @mock.patch('os.makedirs')
    @mock.patch('shutil.move')
    def test_move_nothing(self, mock_move, mock_makedirs, mock_isfile, mock_removedirs):
        pt.move(pt.all, "td", "new/td")

        self.assertFalse(mock_makedirs.call_args_list)
        self.assertFalse(mock_move.call_args_list)
        self.assertFileListEqual(sorted(self.get_arguments_list(mock_removedirs, 0)), ['td/plain/empty', 'td/plain/empty_dir'])

    def test_move_non_a_folder(self):
        with self.assertRaises(FileNotFoundError):
            pt.move(pt.all, "not_exists", "new/td")
