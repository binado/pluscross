# Repository Guidelines

## Project Structure & Module Organization

This repository defines the `waveform_catalog` HDF5 format and thin IO packages in Python and Julia.

- `SPEC.md` is the source of truth for the on-disk schema.
- `python/` contains the Python package, with implementation in `python/src/pluscross/` and tests in `python/tests/`.
- `julia/PlusCross/` contains the Julia package, with implementation in `src/` and tests in `test/`.
- `tests/cross_language/` contains round-trip checks that verify Python-written catalogs load in Julia and Julia-written catalogs load in Python.

Keep behavior aligned across both language implementations. Changes to schema behavior should update `SPEC.md`, both packages, and cross-language tests together.

## Build, Test, and Development Commands

- `cd python && uv run --extra test pytest tests/` runs the Python test suite with test dependencies.
- `julia --project=julia/PlusCross -e 'using Pkg; Pkg.test()'` runs the Julia package tests from the repository root.
- `tests/cross_language/run.sh` runs the cross-language HDF5 compatibility checks.

For Julia commands executed inside `julia/PlusCross/`, use `julia --project=.`.

## Coding Style & Naming Conventions

Python targets 3.11+ and uses typed dataclasses, `pathlib.Path`, NumPy arrays, and explicit validation errors. Use 4-space indentation, snake_case for functions and variables, and keep public exports listed in `__all__`.

Julia targets 1.10 and uses conventional Julia style: 4-space indentation, snake_case function names, concrete exported API names such as `WaveformCatalog`, and keyword constructors where useful.

Preserve the language-native array layouts: Python polarizations are `(nsamples, nfreq)`, while Julia polarizations are `(nfreq, nsamples)`.

## Testing Guidelines

Add tests next to the affected implementation: `python/tests/test_*.py` for Python and `julia/PlusCross/test/runtests.jl` for Julia. Include negative tests for invalid HDF5 files or shape mismatches when changing validation. Run the cross-language suite for any schema, layout, dtype, compression, or attribute changes.

## Commit & Pull Request Guidelines

Recent commits use concise Conventional Commit prefixes such as `feat:` and `docs:`. Follow that pattern, for example `feat: add catalog metadata validation`.

Pull requests should describe the schema/API impact, list tests run, and call out whether both Python and Julia implementations were updated. Link related issues when available and include sample HDF5 files only when they are small and necessary.
