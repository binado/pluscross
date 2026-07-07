"""
    WaveformCatalogs

IO for the `waveform_catalog` HDF5 format (see `SPEC.md` at the repo root):
catalogs of frequency-domain waveform polarizations. Complex `h₊`/`hₓ` are stored
on a shared frequency axis together with per-sample source parameters and the
waveform-generation attributes. Pure IO: no derived quantities are computed here.
"""
module WaveformCatalogs

using HDF5

export WaveformCatalog, save_catalog, load_catalog

const FORMAT_NAME = "waveform_catalog"
const FORMAT_VERSION = 1
const DOMAIN_FREQUENCY = "frequency"

"""Target uncompressed chunk size in complex128 elements (~64 MiB)."""
const CHUNK_ELEMENTS = 2^22

"""
    WaveformCatalog

In-memory frequency-domain waveform polarization catalog.

`plus` and `cross` have shape `(nfreq, nsamples)` — frequency axis first,
matching the on-disk frequency-contiguous layout. `source_parameters` is a
`NamedTuple` of `Vector{Float64}` columns of length `nsamples`.
"""
struct WaveformCatalog{P <: NamedTuple}
    frequencies::Vector{Float64}
    plus::Matrix{ComplexF64}
    cross::Matrix{ComplexF64}
    source_parameters::P
    approximant::String
    minimum_frequency::Float64
    maximum_frequency::Float64
    reference_frequency::Float64
    sampling_frequency::Float64

    function WaveformCatalog(
            frequencies::AbstractVector{<:Real},
            plus::AbstractMatrix{<:Complex},
            cross::AbstractMatrix{<:Complex},
            source_parameters::P,
            approximant::AbstractString,
            minimum_frequency::Real,
            maximum_frequency::Real,
            reference_frequency::Real,
            sampling_frequency::Real
    ) where {P <: NamedTuple}
        size(plus) == size(cross) ||
            throw(ArgumentError("plus $(size(plus)) and cross $(size(cross)) shapes differ"))
        size(plus, 1) == length(frequencies) ||
            throw(ArgumentError("polarization frequency axis ($(size(plus, 1))) does not match frequencies ($(length(frequencies)))"))
        n = size(plus, 2)
        for (name, values) in pairs(source_parameters)
            length(values) == n ||
                throw(ArgumentError("source parameter $(name) must have length $(n), got $(length(values))"))
        end
        params = map(v -> Vector{Float64}(v), source_parameters)
        return new{typeof(params)}(
            Vector{Float64}(frequencies),
            Matrix{ComplexF64}(plus),
            Matrix{ComplexF64}(cross),
            params,
            String(approximant),
            Float64(minimum_frequency),
            Float64(maximum_frequency),
            Float64(reference_frequency),
            Float64(sampling_frequency)
        )
    end
end

function WaveformCatalog(;
        frequencies,
        plus,
        cross,
        source_parameters = NamedTuple(),
        approximant,
        minimum_frequency,
        maximum_frequency,
        reference_frequency,
        sampling_frequency
)
    return WaveformCatalog(
        frequencies,
        plus,
        cross,
        source_parameters,
        approximant,
        minimum_frequency,
        maximum_frequency,
        reference_frequency,
        sampling_frequency
    )
end

nfreq(c::WaveformCatalog) = length(c.frequencies)
nsamples(c::WaveformCatalog) = size(c.plus, 2)

"""In-file chunk dims (Julia order): full frequency axis × bounded sample count."""
function _chunk_dims(nf::Int, ns::Int)
    per_chunk = min(ns, max(1, CHUNK_ELEMENTS ÷ max(nf, 1)))
    return (nf, per_chunk)
end

"""
    save_catalog(path, catalog)

Write `catalog` to `path` in waveform_catalog format v1.
"""
function save_catalog(path::AbstractString, catalog::WaveformCatalog)
    h5open(path, "w") do f
        a = attributes(f)
        a["format_name"] = FORMAT_NAME
        a["format_version"] = Int64(FORMAT_VERSION)
        a["domain"] = DOMAIN_FREQUENCY
        a["approximant"] = catalog.approximant
        a["minimum_frequency"] = catalog.minimum_frequency
        a["maximum_frequency"] = catalog.maximum_frequency
        a["reference_frequency"] = catalog.reference_frequency
        a["sampling_frequency"] = catalog.sampling_frequency

        write(f, "frequencies", catalog.frequencies)
        pol = create_group(f, "polarizations")
        chunk = _chunk_dims(nfreq(catalog), nsamples(catalog))
        for (name, data) in (("plus", catalog.plus), ("cross", catalog.cross))
            # Julia's (nfreq, nsamples) column-major matrix lands on disk as the
            # spec's (nsamples, nfreq) C-order dataspace with no transpose.
            dset = create_dataset(
                pol, name, ComplexF64, size(data); chunk = chunk, deflate = 3)
            write(dset, data)
        end
        params = create_group(f, "source_parameters")
        for (name, values) in pairs(catalog.source_parameters)
            write(params, String(name), values)
        end
    end
    return nothing
end

function _require_attr(a, name::AbstractString, label::AbstractString)
    haskey(a, name) ||
        throw(ArgumentError("$(label): missing required attribute '$(name)'"))
    return read(a[name])
end

function _require_dataset(f, key::AbstractString, label::AbstractString)
    haskey(f, key) ||
        throw(ArgumentError("$(label): missing required object '$(key)'"))
    return f[key]
end

"""
    load_catalog(path) -> WaveformCatalog

Read a waveform_catalog v1 file into a [`WaveformCatalog`](@ref).
"""
function load_catalog(path::AbstractString)
    label = basename(path)
    h5open(path, "r") do f
        a = attributes(f)
        format_name = String(_require_attr(a, "format_name", label))
        format_name == FORMAT_NAME ||
            throw(ArgumentError("$(label): format_name is '$(format_name)', expected '$(FORMAT_NAME)'"))
        version = Int(_require_attr(a, "format_version", label))
        version == FORMAT_VERSION ||
            throw(ArgumentError("$(label): format_version is $(version), expected $(FORMAT_VERSION)"))
        domain = String(_require_attr(a, "domain", label))
        domain == DOMAIN_FREQUENCY ||
            throw(ArgumentError("$(label): domain is '$(domain)', expected '$(DOMAIN_FREQUENCY)'"))
        approximant = String(_require_attr(a, "approximant", label))
        minimum_frequency = Float64(_require_attr(a, "minimum_frequency", label))
        maximum_frequency = Float64(_require_attr(a, "maximum_frequency", label))
        reference_frequency = Float64(_require_attr(a, "reference_frequency", label))
        sampling_frequency = Float64(_require_attr(a, "sampling_frequency", label))

        frequencies = Vector{Float64}(read(_require_dataset(f, "frequencies", label)))
        plus = Matrix{ComplexF64}(read(_require_dataset(f, "polarizations/plus", label)))
        cross = Matrix{ComplexF64}(read(_require_dataset(
            f, "polarizations/cross", label)))

        param_keys = Symbol[]
        param_vecs = Vector{Float64}[]
        if haskey(f, "source_parameters")
            g = f["source_parameters"]
            for k in keys(g)
                push!(param_keys, Symbol(k))
                push!(param_vecs, Vector{Float64}(read(g[k])))
            end
        end
        source_parameters = NamedTuple{Tuple(param_keys)}(Tuple(param_vecs))

        try
            return WaveformCatalog(
                frequencies,
                plus,
                cross,
                source_parameters,
                approximant,
                minimum_frequency,
                maximum_frequency,
                reference_frequency,
                sampling_frequency
            )
        catch err
            err isa ArgumentError &&
                throw(ArgumentError("$(label): $(err.msg)"))
            rethrow()
        end
    end
end

end # module
