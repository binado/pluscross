# pluscross

A standalone HDF5 format — and thin pure-IO implementations in Python and Julia —
for **catalogs of frequency-domain gravitational-wave waveform polarizations**:
complex `h₊(f)`, `hₓ(f)` per source-parameter sample on a shared frequency axis.

- **[`SPEC.md`](SPEC.md)** — the format definition (v1).
- **[`python/`](python/)** — the `pluscross` Python package (numpy + h5py).
- **[`julia/PlusCross/`](julia/PlusCross/)** — the `PlusCross.jl` Julia package
  (HDF5.jl).
- **[`tests/cross_language/`](tests/cross_language/)** — bit-exact
  python-writes→julia-reads and julia-writes→python-reads round trips.

Both packages expose a `WaveformCatalog` container, per-sample source-parameter
columns, and the five generation attributes, plus save/load functions
implementing the spec verbatim. Polarization arrays use the memory-native batch
layout for each language: Python stores `(nsamples, nfreq)` and batches with
`plus[batch, :]`; Julia stores `(nfreq, nsamples)` and batches with
`plus[:, batch]`. Nothing else: consumers compute derived quantities
(e.g. polarization power `|h₊|² + |hₓ|²`) themselves.

## Format schema

Every file is an HDF5 file with root attributes identifying the format and the
waveform-generation settings:

| Attribute | Value / meaning |
|---|---|
| `format_name` | literal `"waveform_catalog"` |
| `format_version` | integer `1` |
| `domain` | literal `"frequency"` |
| `approximant` | waveform approximant name |
| `minimum_frequency` | generated lower frequency bound in Hz |
| `maximum_frequency` | generated upper frequency bound in Hz |
| `reference_frequency` | phase/spin reference frequency in Hz |
| `sampling_frequency` | implied time-domain sampling frequency in Hz |

Required datasets:

| Object | Shape | Type | Meaning |
|---|---:|---|---|
| `/frequencies` | `(nfreq,)` | `float64` | strictly increasing frequency axis in Hz |
| `/polarizations/plus` | `(nsamples, nfreq)` | `complex128` | complex `h₊(f)` values |
| `/polarizations/cross` | `(nsamples, nfreq)` | `complex128` | complex `hₓ(f)` values |
| `/source_parameters/<name>` | `(nsamples,)` | `float64` | one per-sample source-parameter column |

Complex arrays use the standard h5py/HDF5.jl compound representation with
float64 fields `r` and `i`. On disk the polarization dataspace is
`(nsamples, nfreq)` in C-order dimensions; Python sees that as
`(nsamples, nfreq)`, while Julia sees the same data as `(nfreq, nsamples)`
without transposing.

## Tests

```sh
# Python
cd python && uv run --extra test pytest tests/

# Julia
julia --project=julia/PlusCross -e 'using Pkg; Pkg.test()'

# Cross-language
tests/cross_language/run.sh
```
