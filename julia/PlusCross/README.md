# PlusCross.jl

Pure-IO implementation of the `waveform_catalog` HDF5 format (see
`../../SPEC.md`): catalogs of frequency-domain waveform polarizations.

```julia
using PlusCross

catalog = WaveformCatalog(;
    frequencies = [20.0, 30.0, 40.0],
    plus = reshape(ComplexF64[
        1.0 + 0.1im,
        2.0 + 0.2im,
        3.0 + 0.3im,
    ], :, 1),
    cross = reshape(ComplexF64[
        0.5 - 0.1im,
        1.0 - 0.2im,
        1.5 - 0.3im,
    ], :, 1),
    source_parameters = (mass_1 = [35.0], mass_2 = [30.0]),
    approximant = "IMRPhenomXAS",
    minimum_frequency = 20.0,
    maximum_frequency = 40.0,
    reference_frequency = 20.0,
    sampling_frequency = 4096.0
)

save_catalog("catalog.h5", catalog)
loaded = load_catalog("catalog.h5")

loaded.frequencies         # nfreq-element Vector{Float64}
loaded.plus                # (nfreq, nsamples) Matrix{ComplexF64}
loaded.cross               # (nfreq, nsamples) Matrix{ComplexF64}
loaded.source_parameters   # NamedTuple of nsamples-element Vector{Float64}
```

Julia stores polarization matrices as `(nfreq, nsamples)`, so sample batches are
selected with `loaded.plus[:, batch]`. No derived quantities (for example,
polarization power) are computed here; consumers do that themselves.

Run tests with:

```sh
julia --project=. -e 'using Pkg; Pkg.test()'
```
