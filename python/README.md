# waveform-catalog (Python)

Pure-IO implementation of the `waveform_catalog` HDF5 format (see `../SPEC.md`):
catalogs of frequency-domain waveform polarizations.

```python
from waveform_catalog import WaveformCatalog, save_waveform_catalog, load_waveform_catalog

catalog = load_waveform_catalog("catalog.h5")
catalog.frequencies    # (nfreq,) float64
catalog.plus           # (nfreq, nsamples) complex128
catalog.cross          # (nfreq, nsamples) complex128
catalog.source_parameters  # dict[str, (nsamples,) float64]
```

No derived quantities (e.g. polarization power) are computed here — consumers do
that themselves.

Run tests with `uv run --extra test pytest tests/`.
