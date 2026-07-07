# Deterministic reference catalog, mirrored exactly by `reference.py`.
# All values are dyadic rationals or small integers so both languages construct
# bit-identical float64 arrays without sharing an RNG. `k`/`j` below are the
# 0-based frequency/sample indices of the spec.

using WaveformCatalogs

const NFREQ = 16
const NSAMPLES = 7

function reference_catalog()
    plus = [ComplexF64(j * NFREQ + k, k - j) for k in 0:(NFREQ - 1), j in 0:(NSAMPLES - 1)]
    cross = [ComplexF64(0.5 * (j * NFREQ + k), -(k + j))
             for k in 0:(NFREQ - 1), j in 0:(NSAMPLES - 1)]
    return WaveformCatalog(;
        frequencies = [5.0 + 0.25 * k for k in 0:(NFREQ - 1)],
        plus = plus,
        cross = cross,
        source_parameters = (
            luminosity_distance = [100.0 + 62.5 * j for j in 0:(NSAMPLES - 1)],
            redshift = [0.125 * j for j in 0:(NSAMPLES - 1)]
        ),
        approximant = "IMRPhenomXAS_NRTidalv3",
        minimum_frequency = 5.0,
        maximum_frequency = 8.75,
        reference_frequency = 20.0,
        sampling_frequency = 8192.0
    )
end
