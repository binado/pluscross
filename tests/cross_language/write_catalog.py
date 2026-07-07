"""Write the reference catalog with the Python package: ``write_catalog.py <path>``."""

import sys

from reference import reference_catalog

from pluscross import save_catalog

save_catalog(sys.argv[1], reference_catalog())
print(f"wrote {sys.argv[1]}")
