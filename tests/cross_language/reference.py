"""Deterministic reference catalog, mirrored exactly by ``reference.jl``.

All values are dyadic rationals or small integers so both languages construct
bit-identical float64 arrays without sharing an RNG. Indices below are 0-based:
``j`` runs over samples and ``k`` over frequencies.
"""

from __future__ import annotations

import numpy as np

from pluscross import WaveformCatalog

NFREQ = 16
NSAMPLES = 7


def reference_catalog() -> WaveformCatalog:
    j = np.arange(NSAMPLES)[:, None]
    k = np.arange(NFREQ)[None, :]
    return WaveformCatalog(
        frequencies=5.0 + 0.25 * np.arange(NFREQ),
        plus=(j * NFREQ + k) + 1j * (k - j),
        cross=0.5 * (j * NFREQ + k) - 1j * (k + j),
        source_parameters={
            "redshift": 0.125 * np.arange(NSAMPLES),
            "luminosity_distance": 100.0 + 62.5 * np.arange(NSAMPLES),
        },
        approximant="IMRPhenomXAS_NRTidalv3",
        minimum_frequency=5.0,
        maximum_frequency=8.75,
        reference_frequency=20.0,
        sampling_frequency=8192.0,
    )
