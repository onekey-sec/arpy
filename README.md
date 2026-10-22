Arpy
====

This library can be used to access **ar** files from python.

It supports both GNU and BSD formats and exposes the archived files using the standard python **file** interface.

Usage
=====

Standard file usage:
--------------------

With context managers:

```python
with arpy.Archive('file.ar') as ar:
    print("files: %s" % ar.namelist())
    with ar.open('content.txt') as f:
        print(f.read())
```

Via headers for duplicate names:

```python
with arpy.Archive('file.ar') as ar:
    for header in ar.infolist():
        print("file: %s" % header.name)
        with ar.open(header) as f:
            print(f.read())
```

Or directly:

```python
ar = arpy.Archive('file.ar'))
ar.read_all_headers()

# check all available files
ar.archived_files.keys()

# get the contents of the archived file
ar.archived_files[b'some_file'].read()
```

Stream / pipe / ... usage:
--------------------------

```python
ar = arpy.Archive('file.ar'))
for f in ar:
    print("got file name: %s" % f.header.name)
    print("with contents: %s" % f.read())
```


Development
===========

The package is maintained with [uv](https://docs.astral.sh/uv/). If you want to contribute, we recommend you follow these steps:

```sh
git clone https://github.com/onekey-sec/arpy.git
cd arpy
uv sync
uv run pytest
uv run pre-commit install
```

Nix users get the environment from `nix develop` or direnv.

Contributions
=============

All contributions welcome. Just make sure that:

*  tests are provided
*  CI passes on all supported Python versions
*  coverage is close to 100% (currently only missing statements are those depending on python version being used)
