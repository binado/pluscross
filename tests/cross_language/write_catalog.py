"""Write the reference catalog with the Python package: ``write_catalog.py <path>``."""

import sys

from reference import reference_catalog

from waveform_catalog import save_waveform_catalog

save_waveform_catalog(sys.argv[1], reference_catalog())
print(f"wrote {sys.argv[1]}")
