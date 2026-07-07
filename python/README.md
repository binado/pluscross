# pluscross (Python)

Pure-IO implementation of the `waveform_catalog` HDF5 format (see `../SPEC.md`):
catalogs of frequency-domain waveform polarizations.

```python
from pluscross import WaveformCatalog, save_catalog, load_catalog

catalog = load_catalog("catalog.h5")
catalog.frequencies    # (nfreq,) float64
catalog.plus           # (nsamples, nfreq) complex128
catalog.cross          # (nsamples, nfreq) complex128
catalog.source_parameters  # dict[str, (nsamples,) float64]
```

No derived quantities (e.g. polarization power) are computed here — consumers do
that themselves.

Run tests with `uv run --extra test pytest tests/`.
