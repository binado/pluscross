from __future__ import annotations

import h5py
import numpy as np
import pytest

from pluscross import (
    WaveformCatalog,
    load_catalog,
    save_catalog,
)


def make_catalog(nfreq: int = 8, nsamples: int = 5) -> WaveformCatalog:
    rng = np.random.default_rng(42)
    shape = (nsamples, nfreq)
    return WaveformCatalog(
        frequencies=np.linspace(5.0, 100.0, nfreq),
        plus=rng.standard_normal(shape) + 1j * rng.standard_normal(shape),
        cross=rng.standard_normal(shape) + 1j * rng.standard_normal(shape),
        source_parameters={
            "redshift": rng.uniform(0.0, 2.0, nsamples),
            "luminosity_distance": rng.uniform(100.0, 5000.0, nsamples),
        },
        approximant="IMRPhenomXAS_NRTidalv3",
        minimum_frequency=5.0,
        maximum_frequency=100.0,
        reference_frequency=20.0,
        sampling_frequency=8192.0,
    )


def test_roundtrip_bit_exact(tmp_path):
    catalog = make_catalog()
    path = tmp_path / "catalog.h5"
    save_catalog(path, catalog)
    loaded = load_catalog(path)

    np.testing.assert_array_equal(loaded.frequencies, catalog.frequencies)
    np.testing.assert_array_equal(loaded.plus, catalog.plus)
    np.testing.assert_array_equal(loaded.cross, catalog.cross)
    assert set(loaded.source_parameters) == set(catalog.source_parameters)
    for name, values in catalog.source_parameters.items():
        np.testing.assert_array_equal(loaded.source_parameters[name], values)
    assert loaded.approximant == catalog.approximant
    assert loaded.minimum_frequency == catalog.minimum_frequency
    assert loaded.maximum_frequency == catalog.maximum_frequency
    assert loaded.reference_frequency == catalog.reference_frequency
    assert loaded.sampling_frequency == catalog.sampling_frequency


def test_on_disk_layout(tmp_path):
    """The spec's dataspace dims and complex compound convention, verified raw."""
    catalog = make_catalog(nfreq=8, nsamples=5)
    path = tmp_path / "catalog.h5"
    save_catalog(path, catalog)
    with h5py.File(path, "r") as f:
        plus = f["polarizations/plus"]
        assert plus.shape == (5, 8)  # (nsamples, nfreq) C-order
        assert plus.dtype == np.complex128
        assert plus.compression == "gzip"
        assert f.attrs["format_name"] == "waveform_catalog"
        assert int(f.attrs["format_version"]) == 1
        assert f.attrs["domain"] == "frequency"
        assert f["frequencies"].shape == (8,)
        assert f["source_parameters/redshift"].shape == (5,)


def test_constructor_validates_shapes():
    catalog = make_catalog()
    with pytest.raises(ValueError, match="plus .* cross"):
        WaveformCatalog(
            frequencies=catalog.frequencies,
            plus=catalog.plus,
            cross=catalog.cross[:, :-1],
        )
    with pytest.raises(ValueError, match="frequency axis"):
        WaveformCatalog(
            frequencies=catalog.frequencies[:-1],
            plus=catalog.plus,
            cross=catalog.cross,
        )
    with pytest.raises(ValueError, match="strictly increasing"):
        WaveformCatalog(
            frequencies=catalog.frequencies[::-1],
            plus=catalog.plus,
            cross=catalog.cross,
        )
    with pytest.raises(ValueError, match="redshift"):
        WaveformCatalog(
            frequencies=catalog.frequencies,
            plus=catalog.plus,
            cross=catalog.cross,
            source_parameters={"redshift": np.zeros(3)},
        )


@pytest.mark.parametrize(
    "attr,value,match",
    [
        ("domain", "time", "domain"),
        ("format_version", 2, "format_version"),
        ("format_name", "other", "format_name"),
    ],
)
def test_load_rejects_bad_attrs(tmp_path, attr, value, match):
    path = tmp_path / "catalog.h5"
    save_catalog(path, make_catalog())
    with h5py.File(path, "r+") as f:
        f.attrs[attr] = value
    with pytest.raises(ValueError, match=match):
        load_catalog(path)


def test_load_rejects_missing_attr(tmp_path):
    path = tmp_path / "catalog.h5"
    save_catalog(path, make_catalog())
    with h5py.File(path, "r+") as f:
        del f.attrs["reference_frequency"]
    with pytest.raises(ValueError, match="reference_frequency"):
        load_catalog(path)


def test_load_rejects_missing_dataset(tmp_path):
    path = tmp_path / "catalog.h5"
    save_catalog(path, make_catalog())
    with h5py.File(path, "r+") as f:
        del f["polarizations/cross"]
    with pytest.raises(ValueError, match="polarizations/cross"):
        load_catalog(path)


def test_load_rejects_non_increasing_frequencies(tmp_path):
    path = tmp_path / "catalog.h5"
    save_catalog(path, make_catalog())
    with h5py.File(path, "r+") as f:
        f["frequencies"][...] = f["frequencies"][...][::-1]
    with pytest.raises(ValueError, match="strictly increasing"):
        load_catalog(path)
