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

# Returns global paths to all *.jpg files in directory
def get_jpegs(path):
    return glob.iglob(path + '/**/*.jpg', recursive=True)

# Returns global paths to all *.nef files in directory
def get_nefs(path):
    return glob.iglob(path + '/**/*.nef', recursive=True)

# Converts data to paths
def date_to_path(data):
    return datetime.datetime.strptime(data, '%Y:%m:%d %H:%M:%S').strftime('%Y/%m %B')

# Returns EXIF datestamp
def get_exif_date(pic):
    try:
        img = PIL.Image.open(pic)
    except:
        return None
    
    if not hasattr(img, '_getexif'):
        return None
    exif_data = img._getexif()
    return exif_data.get(36867)

# Returns NEF datestamp
# Taken from
# https://pascalbrokmeier.de/2018-01-24/2018-01-24-Getting_the_capture_date_in_a_nef_Nikon_raw_file_with_python/
def get_nef_date(pic):
    raw_chunk = open(pic, 'rb')
    raw_chunk.seek(2964)
    capture_date_bin = raw_chunk.read(19)
    return str(capture_date_bin)[2:-1]

def get_date(pic):
    return get_nef_date(pic) if pic.lower().endswith('.nef') else get_exif_date(pic)

# Returns destination filename
def get_new_name(pic, dst_path):
    date = get_date(pic)
    if date is not None:
        return "{}/{}/{}".format(dst_path, date_to_path(date), os.path.basename(pic))

def sha256sum(filename):
    h = hashlib.sha256()
    with open(filename, 'rb', buffering=0) as f:
        for b in iter(lambda : f.read(128*1024), b''):
            h.update(b)
    return h.hexdigest()

# Move a single file
def move_file(src, dst_path):
    dst = get_new_name(src, dst_path)
    if os.path.isfile(dst):
        print ('Skip ' + src + ', ' + dst + ' exists')
    else:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
               
# Checks if directory has duplicate files
# Compares only datestamp and SHA, ignores content
# (i.e. ignores photoshoot series)
def check_duplicates(path):
    results = dict()
    n = 0
    for pic in get_jpegs(path):
        import PIL.Image
        if (n % 100) == 0:
            print ('photos loaded: ' + str(n))
        d = get_data(pic)
        if results.get(d) is not None:
            if sha256sum(pic) == sha256sum(results.get(d)):
                print (pic + ' and ' + results.get(d) + ' are same files')
        results[d] = pic
        n += 1

# Returns imagehash (see https://pypi.org/project/ImageHash/)
def get_imagehash(pic):
    try:
        img = PIL.Image.open(pic)
    except:
        return None

    return imagehash.dhash(img)

# Returns all photos which are considered as "takes"
# A "take" is a photo which is very close to the previous one
# Usually that happens with sequence shot and there is no need
# to keep all of the shots, 1 or 2 may be left.
def get_takes(path):
    is_first = True
    for pic in get_jpegs(path):
        new_hash = get_imagehash(pic)
        if is_first or current_hash - new_hash > 5:      
            is_first = False
            current_hash = new_hash
            group_start_pic = pic
            group_start_pic_returned = False
            continue

        if not group_start_pic_returned:
            group_start_pic_returned = True
            yield group_start_pic
            
        yield pic

# Moves all "takes" to destination
def move_all_takes(src_path, dst_path):
    for pic in get_takes(src_path):
        move_file(pic, dst_path)
        
# Moves files from an SD card to the storage
# The storage will have hiearachied folders like:
# "2010/09 September"
# If file exists already, it is skipped
def move_all_files(src_path, dst_path):
    for pic in get_jpegs(src_path):
        move_file(pic, dst_path)
    for pic in get_nefs(src_path):
        move_file(pic, dst_path)
