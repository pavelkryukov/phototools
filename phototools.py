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
import shutil
import time

### ATTRIBUTE GETTERS

def get_sha256sum(pic):
    h = hashlib.sha256()
    with open(pic, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

# Returns EXIF metadata
def get_exif(pic, index):
    try:
        with PIL.Image.open(pic) as img:
            return img._getexif().get(index) if hasattr(img, '_getexif') else None
    except:
        return None

# Returns imagehash (see https://pypi.org/project/ImageHash/)
def get_imagehash(pic):
    try:
        with PIL.Image.open(pic) as img:
            try:
                return imagehash.dhash(img)
            except:
                print ("Could not hash {}".format(pic))
                return None
    except:
        print ("Could not open {}".format(pic))
        return None

### GENERATORS

# Returns global paths to all *.jpg files in directory
def jpegs(path):
    return sorted(glob.iglob(path + '/**/*.jpg', recursive=True))

# Returns global paths to all *.nef files in directory
def nefs(path):
    return sorted(glob.iglob(path + '/**/*.nef', recursive=True))

def all(path):
    yield from jpegs(path)
    yield from nefs(path)

# Checks if directory has duplicate files
# Compares only datestamp and SHA, ignores content
# (i.e. ignores photoshoot series)
def duplicates(src_path):
    results = dict()
    n = 0
    for pic in jpegs(src_path):
        if (n % 100) == 0:
            print ('photos loaded: ' + str(n))
        d = os.path.getmtime(pic)
        if results.get(d) is not None:
            if get_sha256sum(pic) == get_sha256sum(results.get(d)):
                yield pic
        results[d] = pic
        n += 1

# Move all NEF files which have JPG files
# taken in the same second together with JPG files.
# I usually enable NEF+JPG mode so I can navigate
# JPG files faster; one archived, they are not
# really needed. This tool helps to filter them out.
def nefs_with_jpg(src_path):
    jpegs_cache = { }
    for nef in nefs(src_path):
        print (nef)
        date = get_date(nef)
        move_nef = False

        directory = os.path.dirname(nef)
        if not directory in jpegs_cache:
            jpegs_cache[directory] = [(i, get_date(i)) for i in get_jpegs(directory)]

        for (jpeg, jpeg_date) in jpegs_cache[directory]:
            if date == jpeg_date and os.path.isfile(jpeg):
                move_nef = True
                yield jpeg

        if move_nef:
            yield nef

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
        for pic in jpegs(path):
            new_hash = get_imagehash(pic)
            if is_first or current_hash - new_hash > factor:
                is_first = False
                current_hash = new_hash
                group_start_pic = pic
                group_start_pic_returned = False
                continue

            if not group_start_pic_returned:
                group_start_pic_returned = True
                yield group_start_pic

            yield pic

    return lambda path: takes_impl(path, factor)

### MOVING CODE

# Returns destination pic
def get_new_name(pic, dst_path):
    def get_date(pic):
        # Returns NEF datestamp
        # Taken from
        # https://pascalbrokmeier.de/2018-01-24/2018-01-24-Getting_the_capture_date_in_a_nef_Nikon_raw_file_with_python/
        def get_nef_date(pic):
            with open(pic, 'rb') as raw_chunk:
                raw_chunk.seek(2964)
                capture_date_bin = raw_chunk.read(19)
                return str(capture_date_bin)[2:-1]

        # Returns creation year
        def get_creation_date(file):
            ctime = time.ctime(os.path.getmtime(file))
            return datetime.datetime.strptime(ctime, "%a %b %d %H:%M:%S %Y").strftime('%Y:%m:%d %H:%M:%S')

        if pic.lower().endswith('.nef'):
            return get_nef_date(pic)

        exif_date = get_exif(pic, 36867)
        return get_creation_date(pic) if exif_date is None else exif_date

    subfolder = datetime.datetime.strptime(get_date(pic), '%Y:%m:%d %H:%M:%S').strftime('%Y/%m %B')
    return "{}/{}/{}".format(dst_path, subfolder, os.path.basename(pic))

# Moves generated files to the storage
# The storage will have hiearachied folders like:
# "2010/09 September"
# If file exists already, it is skipped
def move(generator, src_path, dst_path):
    for src in generator(src_path):
        dst = get_new_name(src, dst_path)
        try:
            if os.path.isfile(dst):
                print ('Skip ' + src + ', ' + dst + ' exists')
            else:
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
        except:
            print ("Could not move {} to {}".format(src, dst))
