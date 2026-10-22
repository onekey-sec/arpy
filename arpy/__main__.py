import sys

from arpy import Archive

ar = Archive(sys.argv[1])
ar.read_all_headers()

for key in ar.archived_files:
    print(key)  # noqa: T201
