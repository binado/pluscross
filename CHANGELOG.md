# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0]

### Added

- Optional `compression` parameter on `save_catalog` (and Python
  `WaveformCatalog.save`) to opt into an HDF5 compression filter, for example
  `compression="gzip"`.

### Changed

- Polarization datasets are now written uncompressed by default. Complex
  frequency-domain strains barely compress, so gzip previously dominated I/O
  time for negligible size gains. Pass `compression="gzip"` to restore the old
  behavior. Existing gzip-compressed files remain readable via `load_catalog`.

## [0.1.0] - 2026-07-08

### Added

- `waveform_catalog` HDF5 format v1: frequency-domain waveform polarization
  catalogs with complex `h_plus`/`h_cross` on a shared frequency axis,
  per-sample source parameters, and waveform-generation attributes (see
  `SPEC.md`).
- `pluscross` Python package: `WaveformCatalog`, `save_catalog`,
  `load_catalog`, `frequency_array`. Polarizations are `(nsamples, nfreq)`.
- `PlusCross` Julia package: `WaveformCatalog`, `save_catalog`,
  `load_catalog`, `frequency_array`, `nfreq`, `nsamples`. Polarizations are
  `(nfreq, nsamples)`.
- Cross-language round-trip tests verifying Python-written catalogs load in
  Julia and vice versa.
