import io
import unittest

import pytest

import arpy

from . import SAMPLES_PATH


class SimpleNames(unittest.TestCase):
    def test_single_name(self):
        ar = arpy.Archive((SAMPLES_PATH / "normal.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [b"short"]
        assert len(ar.headers) == 1
        ar.close()

    def test_header_description(self):
        ar = arpy.Archive((SAMPLES_PATH / "normal.ar").as_posix())
        header = ar.read_next_header()
        assert repr(header).startswith("<ArchiveFileHeader")
        ar.close()

    def test_empty_ar(self):
        ar = arpy.Archive((SAMPLES_PATH / "empty.ar").as_posix())
        ar.read_all_headers()
        assert not list(ar.archived_files.keys())
        assert len(ar.headers) == 0
        ar.close()

    def test_symbols(self):
        ar = arpy.Archive((SAMPLES_PATH / "sym.ar").as_posix())
        syms = ar.read_next_header()
        assert syms is not None
        assert syms.type == arpy.HEADER_GNU_SYMBOLS
        assert syms.size == 4
        ao = ar.read_next_header()
        assert ao is not None
        assert ao.type == arpy.HEADER_NORMAL
        assert ao.size == 0
        assert ao.name == b"a.o"
        ar.close()

    def test_windows(self):
        ar = arpy.Archive((SAMPLES_PATH / "windows.ar").as_posix())
        file_header = ar.read_next_header()
        assert file_header is not None
        assert file_header.gid is None
        assert file_header.uid is None
        ar.close()

    def test_fileobj(self):
        data = (SAMPLES_PATH / "normal.ar").read_bytes()
        ar = arpy.Archive(fileobj=io.BytesIO(data))
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [b"short"]
        assert len(ar.headers) == 1
        ar.close()


class ArchiveIteration(unittest.TestCase):
    def test_iteration(self):
        ar = arpy.Archive((SAMPLES_PATH / "normal.ar").as_posix())
        ar_iterator = iter(ar)
        short = ar_iterator.next()
        assert short.header.name == b"short", short.header.name
        with pytest.raises(StopIteration):
            ar_iterator.next()
        ar.close()


if __name__ == "__main__":
    unittest.main()
