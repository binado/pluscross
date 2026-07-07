# waveform-catalog

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

## Tests

```sh
# Python
cd python && uv run --extra test pytest tests/

# Julia
julia --project=julia/PlusCross -e 'using Pkg; Pkg.test()'

# Cross-language
tests/cross_language/run.sh
```
