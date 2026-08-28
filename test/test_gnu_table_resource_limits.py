import io
import tracemalloc

import pytest

import arpy

from . import SAMPLES_PATH

MAX_PEAK_MEMORY_MULTIPLIER = 10


def assert_memory_is_bounded(peak_memory: int, input_size: int) -> None:
    assert peak_memory < input_size * MAX_PEAK_MEMORY_MULTIPLIER, (
        f"parsing a {input_size}-byte GNU name table allocated "
        f"{peak_memory} bytes at peak"
    )


def ar_header(name: bytes, size: int) -> bytes:
    return b"".join(
        (
            name.ljust(16),
            b"0".ljust(12),
            b"0".ljust(6),
            b"0".ljust(6),
            b"0".ljust(8),
            str(size).encode().ljust(10),
            b"`\n",
        )
    )


def test_repeated_gnu_table_reference_reuses_resolved_name():
    """Repeated GNU offsets must not retain a filename copy per header."""
    table = b"a-long-gnu-name-that-needs-a-table/\n"
    archive_data = b"!<arch>\n" + ar_header(b"//", len(table)) + table
    archive_data += ar_header(b"/0", 0) * 2

    with arpy.Archive(fileobj=io.BytesIO(archive_data)) as ar:
        headers = ar.infolist()

    assert headers[0].name is headers[1].name


@pytest.mark.parametrize(
    "filename,table_size",
    [
        ("gnu_separator_table.ar", 4097),
        ("gnu_null_separator_table.ar", 4097),
    ],
)
def test_read_all_headers_bounds_memory_for_separator_table_sample(
    filename: str, table_size: int
):
    """The public archive-reading path must be safe for an untrusted fixture."""
    archive_path = SAMPLES_PATH / filename

    with arpy.Archive(archive_path.as_posix()) as ar:
        tracemalloc.start()
        ar.read_all_headers()
        _, peak_memory = tracemalloc.get_traced_memory()
        tracemalloc.stop()

    assert_memory_is_bounded(peak_memory, table_size)
