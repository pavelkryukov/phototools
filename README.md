[![Build Status](https://travis-ci.com/pavelkryukov/phototools.svg?branch=master)](https://travis-ci.com/pavelkryukov/phototools)
[![codecov](https://codecov.io/gh/pavelkryukov/phototools/branch/master/graph/badge.svg)](https://codecov.io/gh/pavelkryukov/phototools)

## Photo Tools

A set of tools I use to manipulate with my photo library
The usage is simple:

```python
import phototools as pt
pt.move(pt.generator, "E:\\Photos", "E:\\SortedPhotos")
```

There are different generators:

```python
all           # all files
jpegs         # jpeg files
nefs          # Nikon raws files
takes         # all similar and sequntially named photos, so I can keep the best one and remove all others
duplicates    # all photos which are stored under different name (SHA256-based)
nefs_with_jpg # raw+jpg pairs so I can keep only one format
instagram     # all photos saved by Instagram app
```

To test, unpack testing suite first:

```bash
tar -xf td.tar
```

Archive is needed to preserve filesystem time stamps.
