# pluscross (Python)

Pure-IO implementation of the `waveform_catalog` HDF5 format (see `../SPEC.md`):
catalogs of frequency-domain waveform polarizations.

## Installation

```sh
pip install pluscross
```

From source:

```sh
git clone https://github.com/binado/pluscross
cd pluscross/python
uv sync --extra test
```

```python
import numpy as np

from pluscross import WaveformCatalog, save_catalog, load_catalog

catalog = WaveformCatalog(
    frequencies=np.array([20.0, 30.0, 40.0]),
    plus=np.array([[1.0 + 0.1j, 2.0 + 0.2j, 3.0 + 0.3j]]),
    cross=np.array([[0.5 - 0.1j, 1.0 - 0.2j, 1.5 - 0.3j]]),
    source_parameters={"mass_1": np.array([35.0]), "mass_2": np.array([30.0])},
    approximant="IMRPhenomXAS",
    minimum_frequency=20.0,
    maximum_frequency=40.0,
    reference_frequency=20.0,
    sampling_frequency=4096.0,
)

catalog.save("catalog.h5")
loaded = WaveformCatalog.load("catalog.h5")

loaded.frequencies    # (nfreq,) float64
loaded.plus           # (nsamples, nfreq) complex128
loaded.cross          # (nsamples, nfreq) complex128
loaded.source_parameters  # dict[str, (nsamples,) float64]

save_catalog("copy.h5", loaded)
copy = load_catalog("copy.h5")
copy.source_parameters
```

No derived quantities (e.g. polarization power) are computed here — consumers do
that themselves.

Run tests with `uv run --extra test pytest tests/`.
