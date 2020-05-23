[![Build Status](https://travis-ci.com/pavelkryukov/phototools.svg?branch=master)](https://travis-ci.com/pavelkryukov/phototools)
[![codecov](https://codecov.io/gh/pavelkryukov/phototools/branch/master/graph/badge.svg)](https://codecov.io/gh/pavelkryukov/phototools)

# Photo Tools

A set of tools I use to manipulate with my photo library.

### Move and arrange

The following command moves files and puts them in structured manner (`2020/05 May/Filename`).
If destination file exists, no move is performed.

```Python
import phototools as pt
pt.move(pt.generator, src_path="E:\\Photos", dst_path="E:\\SortedPhotos")
```

Different generators may be used to filter specific files:

```python
all                  # all files
jpegs                # jpeg files
nefs                 # Nikon raws files
takes(15)            # all similar and sequntially named photos, so I can keep the best one and remove all others
                     # parameter sets threshold, 1 is to get very similar, 15 is to catch the less similar ones
duplicates           # all photos which are stored under different name (uses SHA256 and timestamp)
duplicates_only_hash # all photos which are stored under different name (only SHA256)
nefs_with_jpg        # raw+jpg pairs so I can keep only one format
instagram            # all photos saved by Instagram app
```

### Testing

Testing is handled with default `unittest` module.

Before running tests, unpack samples:

```bash
tar -xf td.tar
```

Archive is needed to preserve filesystem time stamps.
