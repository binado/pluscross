"""Frequency-axis helpers, independent of the ``waveform_catalog`` IO format."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

__all__ = ["frequency_array"]


def frequency_array(
    *,
    sampling_frequency: float,
    duration: float,
    minimum_frequency: float,
    maximum_frequency: float,
) -> tuple[NDArray[np.float64], NDArray[np.bool_]]:
    """Build the 0-to-Nyquist frequency axis and an in-band mask.

    Returns ``(frequencies, in_band_mask)``: ``frequencies`` runs from 0 Hz to
    the Nyquist frequency (``sampling_frequency / 2``) in steps of
    ``1 / duration``, and ``in_band_mask`` is ``True`` where
    ``minimum_frequency <= frequencies <= maximum_frequency``.

    ``duration * sampling_frequency`` must be an even integer (the number of
    time-domain samples), so the grid spacing is exactly ``1 / duration`` and
    the last frequency lands exactly on the Nyquist frequency.
    """
    if sampling_frequency <= 0.0:
        raise ValueError(
            f"sampling_frequency must be positive, got {sampling_frequency}"
        )
    if duration <= 0.0:
        raise ValueError(f"duration must be positive, got {duration}")
    nyquist_frequency = sampling_frequency / 2.0
    if not (0.0 <= minimum_frequency <= maximum_frequency <= nyquist_frequency):
        raise ValueError(
            "expected 0 <= minimum_frequency <= maximum_frequency <= "
            f"nyquist_frequency ({nyquist_frequency}), got "
            f"minimum_frequency={minimum_frequency}, "
            f"maximum_frequency={maximum_frequency}"
        )

    n_samples_exact = duration * sampling_frequency
    n_samples = round(n_samples_exact)
    tolerance = 4.0 * np.finfo(np.float64).eps * max(1.0, abs(n_samples_exact))
    if abs(n_samples_exact - n_samples) > tolerance:
        raise ValueError(
            "duration * sampling_frequency must be an integer number of "
            f"samples, got duration={duration}, "
            f"sampling_frequency={sampling_frequency} "
            f"({n_samples_exact} samples)"
        )
    if n_samples % 2 != 0:
        raise ValueError(
            "duration * sampling_frequency must be an even integer so the "
            "frequency grid reaches the Nyquist frequency exactly, got "
            f"{n_samples} samples (duration={duration}, "
            f"sampling_frequency={sampling_frequency})"
        )

    frequencies = np.fft.rfftfreq(n_samples, d=1.0 / sampling_frequency)
    in_band_mask = (frequencies >= minimum_frequency) & (
        frequencies <= maximum_frequency
    )
    return frequencies, in_band_mask
