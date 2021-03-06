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

import datetime
import glob
import hashlib
import imagehash
import os
import PIL.Image
import pyexiv2
import rawpy
import shutil
import time


# ATTRIBUTE GETTERS

def get_sha256sum(pic):
    h = hashlib.sha256()
    with open(pic, 'rb', buffering=0) as f:
        for b in iter(lambda: f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()


# Returns EXIF metadata
def get_exif(pic, index):
    try:
        with PIL.Image.open(pic) as img:
            if not hasattr(img, '_getexif'):
                return None

            exif = img._getexif()
            if exif is None:
                print("Exif is None for {}".format(pic))
                return None
            else:
                return exif.get(index)
    except IOError:
        return None


# Returns imagehash (see https://pypi.org/project/ImageHash/)
def get_imagehash(pic):
    try:
        if pic.lower().endswith('.orf'):
            with rawpy.imread(pic) as raw:
                return imagehash.dhash(PIL.Image.fromarray(raw.postprocess()))

        with PIL.Image.open(pic) as img:
            return imagehash.dhash(img)
    except IOError:
        print("Could not open {}".format(pic))
        return None


def get_date(pic):
    EXIF_DATE_FORMAT = '%Y:%m:%d %H:%M:%S'
    OS_DATE_FORMAT = "%a %b %d %H:%M:%S %Y"

    # Returns NEF datestamp
    # Taken from
    # https://pascalbrokmeier.de/2018-01-24/2018-01-24-Getting_the_capture_date_in_a_nef_Nikon_raw_file_with_python/
    def get_nef_date(pic):
        with open(pic, 'rb') as raw_chunk:
            raw_chunk.seek(2964)
            capture_date_bin = raw_chunk.read(19)
            return datetime.datetime.strptime(str(capture_date_bin)[2:-1], EXIF_DATE_FORMAT)

    # Returns creation year
    def get_creation_date(file):
        ctime = time.ctime(os.path.getmtime(file))
        return datetime.datetime.strptime(ctime, OS_DATE_FORMAT)

    def get_orf_date(file):
        with pyexiv2.Image(file) as img:
            return datetime.datetime.strptime(img.read_exif()['Exif.Photo.DateTimeOriginal'], EXIF_DATE_FORMAT)

    if pic.lower().endswith('.nef'):
        return get_nef_date(pic)

    if pic.lower().endswith('.orf'):
        return get_orf_date(pic)

    exif = get_exif(pic, 36867)
    if exif is None:
        return get_creation_date(pic)

    return datetime.datetime.strptime(exif, EXIF_DATE_FORMAT)


def time_diff(date1, date2):
    return (date1 - date2).total_seconds()


# Returns true if two images are likely to be a part of carousel panorama
def is_panorama(left_name, right_name):
    if right_name is None:
        return False

    with PIL.Image.open(left_name) as left:
        with PIL.Image.open(right_name) as right:
            (width, height) = left.size
            if height != right.size[1]:  # Different height
                return False

            edges = [(left.getpixel((width - 1, i)), right.getpixel((0, i))) for i in range(height)]
            metric = [((l[0] - r[0]) ** 2 + (l[1] - r[1]) ** 2 + (l[2] - r[2]) ** 2) / 3 for (l, r) in edges]

            return (sum(metric) / height) < 256


# GENERATORS


def get_all_by_extensions(exts, path):
    for ext in exts:
        yield from glob.iglob('{}/**/*.{}'.format(path, ext), recursive=True)


# Returns global paths to all *.jpg files in directory
def jpegs(path):
    return sorted(get_all_by_extensions(['jpg', 'jpeg', 'jpe'], path))


# Returns global paths to all raw files in directory
def raws(path):
    return sorted(get_all_by_extensions(['nef', 'orf'], path))


def all(path):
    yield from jpegs(path)
    yield from raws(path)


def all_hashable(path):
    yield from jpegs(path)
    yield from sorted(get_all_by_extensions(['nef'], path))


# Checks if directory has duplicate files
# Compares only datestamp and SHA, ignores content
# (i.e. ignores photoshoot series)
def duplicates(src_path):
    results = dict()
    for pic in jpegs(src_path):
        d = os.path.getmtime(pic)
        if results.get(d) is not None:
            if get_sha256sum(pic) == get_sha256sum(results.get(d)):
                yield pic
        else:
            results[d] = pic


# Checks if directory has duplicate files
# Compares only SHA, so works slower but more accurately
def duplicates_only_hash(src_path):
    results = set()
    for pic in jpegs(src_path):
        d = get_sha256sum(pic)
        if d in results:
            yield pic
        else:
            results.add(d)


# Move all raw files which have JPG files
# taken in the same second together with JPG files.
# I usually enable raw+JPG mode so I can navigate
# JPG files faster; one archived, they are not
# really needed. This tool helps to filter them out.
def nefs_with_jpg(src_path):
    jpegs_cache = {}
    for raw in raws(src_path):
        date = get_date(raw)
        move_raw = False

        directory = os.path.dirname(raw)
        if directory not in jpegs_cache:
            jpegs_cache[directory] = [(i, get_date(i)) for i in jpegs(directory)]

        for (jpeg, jpeg_date) in jpegs_cache[directory]:
            if date == jpeg_date and os.path.isfile(jpeg):
                move_raw = True
                yield jpeg

        if move_raw:
            yield raw


# Returns whether pic is saved by Instagram or not
def instagram(src_path):
    for pic in jpegs(src_path):
        data = get_exif(pic, 305)
        if isinstance(data, str) and "Instagram" in data:
            yield pic


# Returns all photos which are considered as "takes"
# A "take" is a photo which is very close to the previous one
# Usually that happens with sequence shot and there is no need
# to keep all of the shots, 1 or 2 may be left.
def takes(factor):
    def takes_impl(path, factor):
        is_first = True
        current_hash = None
        current_date = None
        for pic in all_hashable(path):
            new_hash = get_imagehash(pic)
            new_date = get_date(pic)
            if is_first or time_diff(new_date, current_date) > 180 or current_hash - new_hash > factor:
                is_first = False
                current_hash = new_hash
                current_date = new_date
                group_start_pic = pic
                group_start_pic_returned = False
                continue

            if not group_start_pic_returned:
                group_start_pic_returned = True
                yield group_start_pic

            yield pic

    return lambda path: takes_impl(path, factor)


# MOVING CODE


def get_empty_dirs(path):
    result = []
    is_empty = True
    for f in os.listdir(path):
        subdir = os.path.join(path, f)

        # Has a file, therefore not empty
        if not os.path.isdir(subdir):
            is_empty = False
            continue

        d = get_empty_dirs(subdir)

        # If subdirectory has files
        # ‘d' would be an empty list
        # or a list of subsubdirectories;
        # but not a subdirectory name
        if subdir not in d:
            is_empty = False

        result.extend(d)

    # The directory does not have files
    # and all subdirectories do not,
    # so just remove the directory
    if is_empty:
        return [path]

    return result


# Moves generated files to the storage
# The storage will have hiearachied folders like:
# "2010/09 September"
# If file exists already, it is skipped
def move(generator, src_path, dst_path, format='%Y/%m %B'):
    if not os.path.isdir(src_path):
        raise FileNotFoundError(src_path)

    for src in generator(src_path):
        subfolder = get_date(src).strftime(format)
        dst = "{}/{}/{}".format(dst_path, subfolder, os.path.basename(src))
        try:
            if os.path.isfile(dst):
                print('Skip ' + src + ', ' + dst + ' exists')
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
        except OSError:
            print("Could not move {} to {}".format(src, dst))

    for d in get_empty_dirs(src_path):
        os.removedirs(d)
