"""Check a catalog file against the reference: ``check_catalog.py <path>``.

Asserts bit-exact equality of frequencies, polarizations, and source
parameters, and exact equality of all attributes.
"""

import sys

import numpy as np
from reference import reference_catalog

from pluscross import load_catalog

expected = reference_catalog()
loaded = load_catalog(sys.argv[1])

np.testing.assert_array_equal(loaded.frequencies, expected.frequencies)
np.testing.assert_array_equal(loaded.plus, expected.plus)
np.testing.assert_array_equal(loaded.cross, expected.cross)
assert set(loaded.source_parameters) == set(expected.source_parameters)
for name, values in expected.source_parameters.items():
    np.testing.assert_array_equal(loaded.source_parameters[name], values)
assert loaded.approximant == expected.approximant
assert loaded.minimum_frequency == expected.minimum_frequency
assert loaded.maximum_frequency == expected.maximum_frequency
assert loaded.reference_frequency == expected.reference_frequency
assert loaded.sampling_frequency == expected.sampling_frequency
print(f"OK: {sys.argv[1]} matches the reference catalog bit-exactly (python reader)")
