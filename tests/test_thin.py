import unittest

import arpy

from . import SAMPLES_PATH


# Test thin archive support
class Thin(unittest.TestCase):
    thin_file_name = b"CMakeFiles/ext_lib_normal.dir/ext_lib.c.o"
    thin_ar_name = "thin.ar"

    def get_file_content(self):
        input_path = SAMPLES_PATH / self.thin_file_name.decode()
        return input_path.read_bytes()

    def test_list(self):
        ar = arpy.Archive((SAMPLES_PATH / self.thin_ar_name).as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [self.thin_file_name]
        assert len(ar.headers) == 3  # Symbols, GNUtable, archive
        ar.close()

    def test_content(self):
        ar = arpy.Archive((SAMPLES_PATH / self.thin_ar_name).as_posix())
        ar.read_all_headers()
        arpy_entry = ar.archived_files[self.thin_file_name]
        real_content = self.get_file_content()
        arpy_content = arpy_entry.read()
        assert real_content == arpy_content
        assert len(real_content) == arpy_entry.header.size
        ar.close()

    def test_content_offset_preserving(self):
        ar = arpy.Archive((SAMPLES_PATH / self.thin_ar_name).as_posix())
        ar.read_all_headers()
        arpy_entry = ar.archived_files[self.thin_file_name]
        real_content = self.get_file_content()
        arpy_content = arpy_entry.read(10)
        arpy_content += arpy_entry.read(20)
        arpy_content += arpy_entry.read()
        assert real_content == arpy_content
        assert len(real_content) == arpy_entry.header.size
        ar.close()


if __name__ == "__main__":
    unittest.main()
