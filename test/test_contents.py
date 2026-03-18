import arpy
import unittest
import os
import io
from unittest.mock import patch, mock_open, call


def make_archive(entries):
	archive = io.BytesIO()
	archive.write(b"!<arch>\n")
	for name, data in entries:
		header = "{:<16}{:<12}{:<6}{:<6}{:<8}{:<10}`\n".format(
			name.decode('ascii') + '/',
			1364071329,
			1000,
			100,
			"100644",
			len(data),
		).encode('ascii')
		archive.write(header)
		archive.write(data)
		if len(data) % 2:
			archive.write(b"\n")
	archive.seek(0)
	return archive


class ArContents(unittest.TestCase):
	def test_archive_contents(self):
		ar = arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar'))
		ar.read_all_headers()
		f1_contents = ar.archived_files[b'file1'].read()
		f2_contents = ar.archived_files[b'file2'].read()
		self.assertEqual(b'test_in_file_1\n', f1_contents)
		self.assertEqual(b'test_in_file_2\n', f2_contents)
		ar.close()

	def test_extract(self):
		m = mock_open()
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			with patch('arpy.open', m):
				with patch('os.makedirs') as m_makedirs:
					ar.extract(b'file1', '/foobar')

		m_makedirs.assert_called_once_with(b'/foobar', exist_ok=True)
		m.assert_called_once_with(b'/foobar/file1', 'wb')
		m().write.assert_called_once_with(b'test_in_file_1\n')
		m().__exit__.assert_called_once_with(None, None, None)

	def test_extract_byte_path(self):
		m = mock_open()
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			with patch('arpy.open', m):
				with patch('os.makedirs') as m_makedirs:
					ar.extract(b'file1', b'/foobar')

		m_makedirs.assert_called_once_with(b'/foobar', exist_ok=True)
		m.assert_called_once_with(b'/foobar/file1', 'wb')
		m().write.assert_called_once_with(b'test_in_file_1\n')
		m().__exit__.assert_called_once_with(None, None, None)

	def test_extract_preserves_member_subdirectories(self):
		m = mock_open()
		with arpy.Archive(fileobj=make_archive([(b'dir/file', b'test')])) as ar:
			with patch('arpy.open', m):
				with patch('os.makedirs') as m_makedirs:
					ar.extract(b'dir/file', '/foobar')

		m_makedirs.assert_called_once_with(b'/foobar/dir', exist_ok=True)
		m.assert_called_once_with(b'/foobar/dir/file', 'wb')
		m().write.assert_called_once_with(b'test')

	def test_extract_rewinds_member_before_copying(self):
		m = mock_open()
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			ar.open(b'file1').read(4)
			with patch('arpy.open', m):
				with patch('os.makedirs'):
					ar.extract(b'file1', '/foobar')
					ar.extract(b'file1', '/barbaz')

		m().write.assert_has_calls([
			call(b'test_in_file_1\n'),
			call(b'test_in_file_1\n'),
		])

	def test_extractall(self):
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			with patch.object(ar, 'extract') as m_extract:
				ar.extractall('/foobar')

		m_extract.assert_has_calls([
			call(b'file1', '/foobar'),
			call(b'file2', '/foobar'),
		], any_order=True)

	def test_extractall2(self):
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			with patch.object(ar, 'extract') as m_extract:
				ar.extractall('/foobar', [b'file2'])

		m_extract.assert_called_once_with(b'file2', '/foobar')

class ArZipLike(unittest.TestCase):
	def setUp(self):
		self.ar = arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar'))

	def test_listnames(self):
		self.assertEqual([b'file1', b'file2'], self.ar.namelist())
		self.ar.close()

	def test_listheaders(self):
		headers = self.ar.infolist()
		self.assertEqual(2, len(headers))
		self.assertEqual(b'file1', headers[0].name)
		self.assertEqual(b'file2', headers[1].name)

	def test_openname(self):
		f = self.ar.open(b'file1')
		self.assertEqual(b'file1', f.header.name)

	def test_openname_fail(self):
		self.assertRaises(KeyError, self.ar.open, b'xxxx')

	def test_openheader(self):
		header = self.ar.infolist()[0]
		f = self.ar.open(header)
		self.assertEqual(b'file1', f.header.name)

	def test_openheader_fail(self):
		content = b"file1/          1364071329  1000  100   100644  5000      `\n"
		self.assertRaises(KeyError, self.ar.open, arpy.ArchiveFileHeader(content, 0))


class ArContext(unittest.TestCase):
	def test_context(self):
		with arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar')) as ar:
			self.assertIsInstance(ar, arpy.Archive)
			with ar.open(b'file1') as f:
				self.assertIsInstance(f, arpy.ArchiveFileData)


class ArContentsSeeking(unittest.TestCase):
	def setUp(self):
		self.ar = arpy.Archive(os.path.join(os.path.dirname(__file__), 'contents.ar'))
		self.ar.read_all_headers()

		self.f1 = self.ar.archived_files[b'file1']

	def tearDown(self):
		self.ar.close()

	def test_content_opens_at_zero(self):
		self.assertEqual(0, self.f1.tell())

	def test_seek_absolute(self):
		contents_before = self.f1.read()
		pos = self.f1.seek(0)
		self.assertEqual(pos, 0)
		contents_after = self.f1.read()
		pos = self.f1.seek(3)
		self.assertEqual(pos, 3)
		contents_shifted = self.f1.read()
		self.assertEqual(contents_before, contents_after)
		self.assertEqual(contents_before[3:], contents_shifted)

	def test_seek_relative(self):
		contents_before = self.f1.read()
		self.f1.seek(1)
		pos = self.f1.seek(1, 1)
		self.assertEqual(pos, 2)
		contents_after = self.f1.read()
		self.assertEqual(contents_before[2:], contents_after)

	def test_seek_from_end(self):
		contents_before = self.f1.read()
		pos = self.f1.seek(-4, 2)
		self.assertEqual(pos, 11)
		contents_after = self.f1.read()
		self.assertEqual(contents_before[-4:], contents_after)

	def test_seek_failure(self):
		self.assertRaises(arpy.ArchiveAccessError, self.f1.seek, 10, 10)

	def test_seek_position_failure(self):
		self.assertRaises(arpy.ArchiveAccessError, self.f1.seek, -1)

	def test_check_seekable(self):
		self.assertTrue(self.f1.seekable())


class NonSeekableIO(io.BytesIO):
	def seek(self, *args):
		raise io.UnsupportedOperation("underlying stream is not seekable")

	def seekable(self):
		return False

	def force_seek(self, *args):
		io.BytesIO.seek(self, *args)


class ArContentsNoSeeking(unittest.TestCase):
	def setUp(self):
		big_archive = NonSeekableIO()
		big_archive.write(b"!<arch>\n")
		big_archive.write(b"file1/          1364071329  1000  100   100644  5000      `\n")
		big_archive.write(b" "*5000)
		big_archive.write(b"file2/          1364071329  1000  100   100644  2         `\n")
		big_archive.write(b"xx")
		big_archive.force_seek(0)
		self.big_archive = big_archive

	def test_stream_read(self):
		# make sure all contents can be read without seeking
		ar = arpy.Archive(fileobj=self.big_archive)
		f = ar.next()
		contents = f.read()
		self.assertEqual(b'file1', f.header.name)
		self.assertEqual(b' '*5000, contents)
		f = ar.next()
		contents = f.read()
		self.assertEqual(b'file2', f.header.name)
		self.assertEqual(b'xx', contents)
		ar.close()

	def test_stream_skip_file(self):
		# make sure skipping contents is possible without seeking
		ar = arpy.Archive(fileobj=self.big_archive)
		f = ar.next()
		self.assertEqual(b'file1', f.header.name)
		f = ar.next()
		contents = f.read()
		self.assertEqual(b'file2', f.header.name)
		self.assertEqual(b'xx', contents)
		ar.close()

	def test_seek_fail(self):
		ar = arpy.Archive(fileobj=self.big_archive)
		f1 = ar.next()
		ar.next()
		self.assertRaises(arpy.ArchiveAccessError, f1.read)
		ar.close()

	def test_check_seekable(self):
		ar = arpy.Archive(fileobj=self.big_archive)
		f1 = ar.next()
		self.assertFalse(f1.seekable())
		ar.close()

if __name__ == "__main__":
	unittest.main()
