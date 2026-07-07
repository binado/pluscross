"""IO for the ``waveform_catalog`` HDF5 format (see SPEC.md at the repo root).

Stores catalogs of frequency-domain waveform polarizations: complex ``h_plus`` /
``h_cross`` on a shared frequency axis, per-sample source parameters, and the
waveform-generation attributes. Pure IO: no derived quantities are computed here.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import h5py
import numpy as np
from numpy.typing import NDArray

from .utils import frequency_array

__all__ = ["WaveformCatalog", "save_catalog", "load_catalog", "frequency_array"]

FORMAT_NAME = "waveform_catalog"
FORMAT_VERSION = 1
DOMAIN_FREQUENCY = "frequency"

#: Target uncompressed chunk size in complex128 elements (~64 MiB).
_CHUNK_ELEMENTS = 2**22


@dataclass(frozen=True)
class WaveformCatalog:
    """In-memory frequency-domain waveform polarization catalog.

    ``plus`` and ``cross`` have shape ``(nsamples, nfreq)`` — sample axis
    first, matching the on-disk C-order layout.
    """

    frequencies: NDArray[np.float64]
    plus: NDArray[np.complex128]
    cross: NDArray[np.complex128]
    source_parameters: dict[str, NDArray[np.float64]] = field(default_factory=dict)
    approximant: str = ""
    minimum_frequency: float = 0.0
    maximum_frequency: float = 0.0
    reference_frequency: float = 0.0
    sampling_frequency: float = 0.0

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "frequencies", np.asarray(self.frequencies, dtype=np.float64)
        )
        object.__setattr__(self, "plus", np.asarray(self.plus, dtype=np.complex128))
        object.__setattr__(self, "cross", np.asarray(self.cross, dtype=np.complex128))
        object.__setattr__(
            self,
            "source_parameters",
            {
                name: np.asarray(values, dtype=np.float64)
                for name, values in self.source_parameters.items()
            },
        )
        _validate_arrays(
            self.frequencies, self.plus, self.cross, self.source_parameters
        )

    @property
    def nfreq(self) -> int:
        return self.frequencies.shape[0]

    @property
    def nsamples(self) -> int:
        return self.plus.shape[0]

    def save(self, path: str | Path) -> None:
        """Write this catalog to ``path`` in waveform_catalog format v1."""
        save_catalog(path, self)

    @classmethod
    def load(cls, path: str | Path) -> WaveformCatalog:
        """Read a waveform_catalog v1 file into a catalog."""
        return load_catalog(path)


def _validate_arrays(
    frequencies: NDArray[np.float64],
    plus: NDArray[np.complex128],
    cross: NDArray[np.complex128],
    source_parameters: dict[str, NDArray[np.float64]],
    label: str = "WaveformCatalog",
) -> None:
    if frequencies.ndim != 1:
        raise ValueError(f"{label}: frequencies must be one-dimensional")
    if frequencies.shape[0] > 1 and not np.all(np.diff(frequencies) > 0.0):
        raise ValueError(f"{label}: frequencies must be strictly increasing")
    if plus.ndim != 2 or cross.ndim != 2:
        raise ValueError(f"{label}: plus and cross must be two-dimensional")
    if plus.shape != cross.shape:
        raise ValueError(
            f"{label}: plus {plus.shape} and cross {cross.shape} shapes differ"
        )
    if plus.shape[1] != frequencies.shape[0]:
        raise ValueError(
            f"{label}: polarization frequency axis ({plus.shape[1]}) does not "
            f"match frequencies ({frequencies.shape[0]})"
        )
    nsamples = plus.shape[0]
    for name, values in source_parameters.items():
        if values.ndim != 1 or values.shape[0] != nsamples:
            raise ValueError(
                f"{label}: source parameter {name!r} must be 1-D with length "
                f"{nsamples}, got shape {values.shape}"
            )


def _chunks(nsamples: int, nfreq: int) -> tuple[int, int]:
    """On-disk C-order chunk shape: full frequency rows for a bounded sample count."""
    per_chunk = min(nsamples, max(1, _CHUNK_ELEMENTS // max(nfreq, 1)))
    return (per_chunk, nfreq)


def save_catalog(path: str | Path, catalog: WaveformCatalog) -> None:
    """Write ``catalog`` to ``path`` in waveform_catalog format v1."""
    nsamples, nfreq = catalog.plus.shape
    with h5py.File(path, "w") as f:
        f.attrs["format_name"] = FORMAT_NAME
        f.attrs["format_version"] = np.int64(FORMAT_VERSION)
        f.attrs["domain"] = DOMAIN_FREQUENCY
        f.attrs["approximant"] = catalog.approximant
        f.attrs["minimum_frequency"] = np.float64(catalog.minimum_frequency)
        f.attrs["maximum_frequency"] = np.float64(catalog.maximum_frequency)
        f.attrs["reference_frequency"] = np.float64(catalog.reference_frequency)
        f.attrs["sampling_frequency"] = np.float64(catalog.sampling_frequency)

        f.create_dataset("frequencies", data=catalog.frequencies)
        pol = f.create_group("polarizations")
        chunks = _chunks(nsamples, nfreq)
        for name, data in (("plus", catalog.plus), ("cross", catalog.cross)):
            pol.create_dataset(
                name,
                data=np.ascontiguousarray(data),
                chunks=chunks,
                compression="gzip",
            )
        params = f.create_group("source_parameters")
        for name, values in catalog.source_parameters.items():
            params.create_dataset(name, data=values)


def _require_attr(f: h5py.File, name: str, label: str) -> str | int | float:
    if name not in f.attrs:
        raise ValueError(f"{label}: missing required attribute {name!r}")
    value = f.attrs[name]
    if isinstance(value, bytes):
        return value.decode()
    if isinstance(value, (str, int, float, np.integer, np.floating)):
        # np.integer/np.floating satisfy int()/float(); plain cast for typing.
        return value  # type: ignore[return-value]
    raise ValueError(f"{label}: attribute {name!r} has unsupported type")


def _require_dataset(f: h5py.File, key: str, label: str) -> h5py.Dataset:
    if key not in f:
        raise ValueError(f"{label}: missing required object {key!r}")
    obj = f[key]
    if not isinstance(obj, h5py.Dataset):
        raise ValueError(f"{label}: {key!r} is not a dataset")
    return obj


def load_catalog(path: str | Path) -> WaveformCatalog:
    """Read a waveform_catalog v1 file into a :class:`WaveformCatalog`."""
    label = Path(path).name
    with h5py.File(path, "r") as f:
        format_name = str(_require_attr(f, "format_name", label))
        if format_name != FORMAT_NAME:
            raise ValueError(f"{label}: format_name is {format_name!r}, "
                             f"expected {FORMAT_NAME!r}")
        version = int(_require_attr(f, "format_version", label))
        if version != FORMAT_VERSION:
            raise ValueError(
                f"{label}: format_version is {version}, expected {FORMAT_VERSION}"
            )
        domain = str(_require_attr(f, "domain", label))
        if domain != DOMAIN_FREQUENCY:
            raise ValueError(
                f"{label}: domain is {domain!r}, expected {DOMAIN_FREQUENCY!r}"
            )
        approximant = str(_require_attr(f, "approximant", label))
        physics = {
            name: float(_require_attr(f, name, label))
            for name in (
                "minimum_frequency",
                "maximum_frequency",
                "reference_frequency",
                "sampling_frequency",
            )
        }

        frequencies = np.asarray(_require_dataset(f, "frequencies", label)[...])
        plus = np.asarray(_require_dataset(f, "polarizations/plus", label)[...])
        cross = np.asarray(_require_dataset(f, "polarizations/cross", label)[...])
        source_parameters: dict[str, NDArray[np.float64]] = {}
        if "source_parameters" in f:
            group = f["source_parameters"]
            if not isinstance(group, h5py.Group):
                raise ValueError(f"{label}: 'source_parameters' is not a group")
            for name in (str(k) for k in group):
                source_parameters[name] = np.asarray(
                    _require_dataset(f, f"source_parameters/{name}", label)[...]
                )

    _validate_arrays(frequencies, plus, cross, source_parameters, label=label)
    return WaveformCatalog(
        frequencies=frequencies,
        plus=plus,
        cross=cross,
        source_parameters=source_parameters,
        approximant=approximant,
        **physics,
    )
