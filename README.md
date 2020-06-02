![Python application](https://github.com/pavelkryukov/phototools/workflows/Python%20application/badge.svg)
[![codecov](https://codecov.io/gh/pavelkryukov/phototools/branch/master/graph/badge.svg)](https://codecov.io/gh/pavelkryukov/phototools)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/pavelkryukov/phototools.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/pavelkryukov/phototools/alerts/)

# Photo Tools

A set of tools I use to manipulate with my photo library.

### Move and arrange

The following command moves files and puts them in structured manner.
If destination file exists, no move is performed.

```python
import phototools as pt
pt.move(generator=pt.all, src_path="E:\\Photos", dst_path="E:\\SortedPhotos", format='%Y/%m %B')
```

`format` defines folders structure: `%Y/%m %B` => `2020/05 May/Filename`.

To filter specific files, you may use different generators:

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
Unpack samples before running tests (archive preserves filesystem timestamps).

```bash
tar -xf td.tar
python -m unittest -b
```

