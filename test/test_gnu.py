import unittest

import arpy

from . import SAMPLES_PATH


class GNUExtendedNames(unittest.TestCase):
    def test_single_name(self):
        ar = arpy.Archive((SAMPLES_PATH / "gnu_single_name.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length"
        ]
        assert len(ar.headers) == 2
        ar.close()

    def test_single_name_64(self):
        ar = arpy.Archive((SAMPLES_PATH / "gnu_single_name_64.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length"
        ]
        assert len(ar.headers) == 2
        ar.close()

    def test_multi_name_with_space(self):
        ar = arpy.Archive((SAMPLES_PATH / "gnu_multi_names.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length",
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length_with_space ",
        ]
        assert len(ar.headers) == 3
        ar.close()

    def test_multi_name_with_null_separator(self):
        ar = arpy.Archive((SAMPLES_PATH / "msvc_lib.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length",
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length_with_space ",
        ]
        assert len(ar.headers) == 3
        ar.close()

    def test_mixed_names(self):
        ar = arpy.Archive((SAMPLES_PATH / "gnu_mixed.ar").as_posix())
        ar.read_all_headers()
        assert list(ar.archived_files.keys()) == [
            b"a_very_long_name_for_the_gnu_type_header_so_it_can_overflow_the_standard_name_length",
            b"short",
        ]
        assert len(ar.headers) == 3
        ar.close()


if __name__ == "__main__":
    unittest.main()
