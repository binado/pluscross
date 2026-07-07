from __future__ import annotations

import numpy as np
import pytest

from pluscross import frequency_array


def test_frequency_array_values():
    frequencies, in_band_mask = frequency_array(
        sampling_frequency=8.0,
        duration=4.0,
        minimum_frequency=1.0,
        maximum_frequency=3.0,
    )
    np.testing.assert_array_equal(
        frequencies, [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75,
                      2.0, 2.25, 2.5, 2.75, 3.0, 3.25, 3.5, 3.75, 4.0]
    )
    np.testing.assert_array_equal(
        in_band_mask,
        (frequencies >= 1.0) & (frequencies <= 3.0),
    )


def test_frequency_array_reaches_nyquist_when_n_samples_even():
    sampling_frequency = 8192.0
    frequencies, _ = frequency_array(
        sampling_frequency=sampling_frequency,
        duration=4.0,
        minimum_frequency=0.0,
        maximum_frequency=sampling_frequency / 2.0,
    )
    assert frequencies[-1] == sampling_frequency / 2.0


def test_in_band_mask_boundaries_are_inclusive():
    frequencies, in_band_mask = frequency_array(
        sampling_frequency=8.0,
        duration=4.0,
        minimum_frequency=1.0,
        maximum_frequency=3.0,
    )
    assert in_band_mask[list(frequencies).index(1.0)]
    assert in_band_mask[list(frequencies).index(3.0)]
    assert not in_band_mask[list(frequencies).index(0.75)]
    assert not in_band_mask[list(frequencies).index(3.25)]


@pytest.mark.parametrize(
    "kwargs,match",
    [
        (
            dict(sampling_frequency=0.0, duration=4.0,
                 minimum_frequency=1.0, maximum_frequency=3.0),
            "sampling_frequency",
        ),
        (
            dict(sampling_frequency=8.0, duration=0.0,
                 minimum_frequency=1.0, maximum_frequency=3.0),
            "duration",
        ),
        (
            dict(sampling_frequency=8.0, duration=4.0,
                 minimum_frequency=-1.0, maximum_frequency=3.0),
            "minimum_frequency",
        ),
        (
            dict(sampling_frequency=8.0, duration=4.0,
                 minimum_frequency=3.0, maximum_frequency=1.0),
            "minimum_frequency",
        ),
        (
            dict(sampling_frequency=8.0, duration=4.0,
                 minimum_frequency=1.0, maximum_frequency=5.0),
            "maximum_frequency",
        ),
        (
            # 0.25 * 10 = 2.5 samples: not an integer.
            dict(sampling_frequency=10.0, duration=0.25,
                 minimum_frequency=1.0, maximum_frequency=5.0),
            "integer number of samples",
        ),
        (
            # 0.3 * 10 = 3 samples: an odd integer.
            dict(sampling_frequency=10.0, duration=0.3,
                 minimum_frequency=1.0, maximum_frequency=5.0),
            "even integer",
        ),
    ],
)
def test_frequency_array_rejects_invalid_inputs(kwargs, match):
    with pytest.raises(ValueError, match=match):
        frequency_array(**kwargs)
