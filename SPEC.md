# Waveform catalog HDF5 format — version 1

A `waveform_catalog` file stores a catalog of **frequency-domain gravitational-wave
polarizations**: for each of `nsamples` source-parameter draws, the complex strain
polarizations `h₊(f)` and `hₓ(f)` evaluated on one shared frequency axis of length
`nfreq`, together with the per-sample source parameters and the waveform-generation
settings needed to interpret them.

The file stores the fundamental artifact — complex polarizations — rather than any
derived quantity (e.g. polarization power `|h₊|² + |hₓ|²`). Consumers compute
derived quantities themselves.

## Objects

| Object | HDF5 dataspace (C-order dims) | Type | Notes |
|---|---|---|---|
| `/frequencies` | `(nfreq,)` | float64 | explicit frequency axis in Hz; strictly increasing |
| `/polarizations/plus` | `(nsamples, nfreq)` | complex128 | compound `{r, i}`, float64 fields |
| `/polarizations/cross` | `(nsamples, nfreq)` | complex128 | compound `{r, i}`, float64 fields |
| `/source_parameters/<name>` | `(nsamples,)` | float64 | one dataset per parameter column |

## Root attributes

All required.

| Attribute | Type | Value / meaning |
|---|---|---|
| `format_name` | str | literal `"waveform_catalog"` |
| `format_version` | int | `1` |
| `domain` | str | `"frequency"`; loaders MUST reject any other value |
| `approximant` | str | waveform approximant name |
| `minimum_frequency` | float64 | lower bound of the generated band, Hz |
| `maximum_frequency` | float64 | upper bound of the generated band, Hz |
| `reference_frequency` | float64 | phase/spin reference frequency, Hz |
| `sampling_frequency` | float64 | time-domain sampling frequency implied by generation, Hz |

## Conventions

### Complex storage

Complex values are stored as an HDF5 compound type with two float64 fields named
`r` (real part) and `i` (imaginary part). This is the default complex convention
of **both** h5py and HDF5.jl, so either library reads and writes the datasets as
native `complex128` / `ComplexF64` arrays with zero configuration.

### Layout

The on-disk dataspace dims for polarizations are `(nsamples, nfreq)` in C
(row-major) order, i.e. the frequency axis is contiguous. Consequences:

- **h5py / NumPy** (row-major) sees polarization arrays with shape
  `(nsamples, nfreq)` — its natural events-by-frequencies orientation — copy-free.
- **HDF5.jl** (column-major) sees the same bytes as shape `(nfreq, nsamples)` —
  the column-major-friendly frequencies-by-samples orientation — also copy-free.

Neither side transposes.

### Chunking and compression

Polarization datasets are chunked along the sample axis — each chunk holds the
full frequency axis for a bounded number of samples — and gzip-compressed.
Writers choose the chunk sample count (this implementation uses
`min(nsamples, max(1, 2**22 ÷ nfreq))`, targeting ~64 MiB uncompressed chunks);
readers must not rely on a specific chunk shape.

### Load-time validation

Loaders MUST verify, and report errors naming the offending file and object:

- `format_name`, `format_version`, `domain` attributes present with the values above;
- all five physics attributes present;
- `/frequencies` is 1-D;
- `/polarizations/plus` and `/polarizations/cross` are 2-D with identical shape,
  and their frequency-axis length equals `len(frequencies)`;
- every `/source_parameters/<name>` dataset has length `nsamples`.

## Future revisions

The `domain` attribute exists so a later revision can define a time-domain
variant (`domain = "time"`) without a new format name. Any layout change bumps
`format_version`; version-1 loaders reject files with a different version.
