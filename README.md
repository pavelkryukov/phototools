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
all # moves all files
jpegs # moves jpeg files
nefs # moves Nikon raws files
takes # moves all similar and sequntially named photos, so I can keep the best one and remove all others
duplicates # moves all photos which are stored under different name (SHA256-based)
nefs_with_jpg # moves raw+jpg pairs so I can keep only one format
instagram # moves all photos saved by Instagram app
```

To test, unpack testing suite first:

```bash
tar -xf td.tar
```

Archive is needed to preserve filesystem time stamps.
