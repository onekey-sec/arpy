import io
import unittest

import pytest

import arpy


class SimpleNames(unittest.TestCase):
    def test_not_ar_file(self):
        with pytest.raises(arpy.ArchiveFormatError):
            arpy.Archive(fileobj=io.BytesIO(b"not an ar file"))

    def test_neither_file_not_filename(self):
        with pytest.raises(ValueError):  # noqa: PT011
            arpy.Archive(filename=None, fileobj=None)

    def test_bad_file_header_magic(self):
        bad_ar = (
            b"!<arch>\nfile1/          1364071329  1000  100   100644  15        qq"
        )
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        with pytest.raises(arpy.ArchiveFormatError):
            ar.read_all_headers()

    def test_bad_file_header_short(self):
        bad_ar = b"!<arch>\nfile1/          1364071329  1000"
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        with pytest.raises(arpy.ArchiveFormatError):
            ar.read_all_headers()

    def test_bad_file_header_nums(self):
        bad_ar = (
            b"!<arch>\nfile1/          aaaa071329  1000  100   100644  15        `\n"
        )
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        with pytest.raises(arpy.ArchiveFormatError):
            ar.read_all_headers()

    def test_bad_file_size(self):
        bad_ar = (
            b"!<arch>\nfile1/          1364071329  1000  100   100644  15        `\nabc"
        )
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        ar.read_all_headers()
        f1 = ar.archived_files[b"file1"]
        with pytest.raises(arpy.ArchiveAccessError):
            f1.read()

    def test_bad_table_size(self):
        bad_ar = (
            b"!<arch>\n//                                              10        `\n"
        )
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        with pytest.raises(arpy.ArchiveFormatError):
            ar.read_all_headers()

    def test_bad_table_reference(self):
        bad_ar = (
            b"!<arch>\n//                                               0        `\n"
            b"/9              1297730011  1000  1000  100644  0         `\n"
        )
        ar = arpy.Archive(fileobj=io.BytesIO(bad_ar))
        with pytest.raises(arpy.ArchiveFormatError):
            ar.read_all_headers()


if __name__ == "__main__":
    unittest.main()
