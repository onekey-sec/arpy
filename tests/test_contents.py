import io
import unittest

import pytest

import arpy

from . import SAMPLES_PATH


class ArContents(unittest.TestCase):
    def test_archive_contents(self):
        ar = arpy.Archive((SAMPLES_PATH / "contents.ar").as_posix())
        ar.read_all_headers()
        f1_contents = ar.archived_files[b"file1"].read()
        f2_contents = ar.archived_files[b"file2"].read()
        assert f1_contents == b"test_in_file_1\n"
        assert f2_contents == b"test_in_file_2\n"
        ar.close()


class ArZipLike(unittest.TestCase):
    def setUp(self):
        self.ar = arpy.Archive((SAMPLES_PATH / "contents.ar").as_posix())

    def test_listnames(self):
        assert self.ar.namelist() == [b"file1", b"file2"]
        self.ar.close()

    def test_listheaders(self):
        headers = self.ar.infolist()
        assert len(headers) == 2
        assert headers[0].name == b"file1"
        assert headers[1].name == b"file2"

    def test_openname(self):
        f = self.ar.open(b"file1")
        assert f.header.name == b"file1"

    def test_openname_fail(self):
        with pytest.raises(KeyError):
            self.ar.open(b"xxxx")

    def test_openheader(self):
        header = self.ar.infolist()[0]
        f = self.ar.open(header)
        assert f.header.name == b"file1"

    def test_openheader_fail(self):
        content = b"file1/          1364071329  1000  100   100644  5000      `\n"
        with pytest.raises(KeyError):
            self.ar.open(arpy.ArchiveFileHeader(content, 0))


class ArContext(unittest.TestCase):
    def test_context(self):
        with arpy.Archive((SAMPLES_PATH / "contents.ar").as_posix()) as ar:
            assert isinstance(ar, arpy.Archive)
            with ar.open(b"file1") as f:
                assert isinstance(f, arpy.ArchiveFileData)


class ArContentsSeeking(unittest.TestCase):
    def setUp(self):
        self.ar = arpy.Archive((SAMPLES_PATH / "contents.ar").as_posix())
        self.ar.read_all_headers()

        self.f1 = self.ar.archived_files[b"file1"]

    def tearDown(self):
        self.ar.close()

    def test_content_opens_at_zero(self):
        assert self.f1.tell() == 0

    def test_seek_absolute(self):
        contents_before = self.f1.read()
        pos = self.f1.seek(0)
        assert pos == 0
        contents_after = self.f1.read()
        pos = self.f1.seek(3)
        assert pos == 3
        contents_shifted = self.f1.read()
        assert contents_after == contents_before
        assert contents_shifted == contents_before[3:]

    def test_seek_relative(self):
        contents_before = self.f1.read()
        self.f1.seek(1)
        pos = self.f1.seek(1, 1)
        assert pos == 2
        contents_after = self.f1.read()
        assert contents_after == contents_before[2:]

    def test_seek_from_end(self):
        contents_before = self.f1.read()
        pos = self.f1.seek(-4, 2)
        assert pos == 11
        contents_after = self.f1.read()
        assert contents_after == contents_before[-4:]

    def test_seek_failure(self):
        with pytest.raises(arpy.ArchiveAccessError):
            self.f1.seek(10, 10)

    def test_seek_position_failure(self):
        with pytest.raises(arpy.ArchiveAccessError):
            self.f1.seek(-1)

    def test_check_seekable(self):
        assert self.f1.seekable()


class NonSeekableIO(io.BytesIO):
    def seek(self, *args):  # noqa: ARG002
        raise io.UnsupportedOperation("underlying stream is not seekable")

    def seekable(self):
        return False

    def force_seek(self, *args):
        io.BytesIO.seek(self, *args)


class ArContentsNoSeeking(unittest.TestCase):
    def setUp(self):
        big_archive = NonSeekableIO()
        big_archive.write(b"!<arch>\n")
        big_archive.write(
            b"file1/          1364071329  1000  100   100644  5000      `\n"
        )
        big_archive.write(b" " * 5000)
        big_archive.write(
            b"file2/          1364071329  1000  100   100644  2         `\n"
        )
        big_archive.write(b"xx")
        big_archive.force_seek(0)
        self.big_archive = big_archive

    def test_stream_read(self):
        # make sure all contents can be read without seeking
        ar = arpy.Archive(fileobj=self.big_archive)
        f = ar.next()
        contents = f.read()
        assert f.header.name == b"file1"
        assert contents == b" " * 5000
        f = ar.next()
        contents = f.read()
        assert f.header.name == b"file2"
        assert contents == b"xx"
        ar.close()

    def test_stream_skip_file(self):
        # make sure skipping contents is possible without seeking
        ar = arpy.Archive(fileobj=self.big_archive)
        f = ar.next()
        assert f.header.name == b"file1"
        f = ar.next()
        contents = f.read()
        assert f.header.name == b"file2"
        assert contents == b"xx"
        ar.close()

    def test_seek_fail(self):
        ar = arpy.Archive(fileobj=self.big_archive)
        f1 = ar.next()
        ar.next()
        with pytest.raises(arpy.ArchiveAccessError):
            f1.read()
        ar.close()

    def test_check_seekable(self):
        ar = arpy.Archive(fileobj=self.big_archive)
        f1 = ar.next()
        assert not f1.seekable()
        ar.close()


if __name__ == "__main__":
    unittest.main()
