# Check a catalog file against the reference: `julia check_catalog.jl <path>`.
# Asserts bit-exact equality of frequencies, polarizations, and source
# parameters, and exact equality of all attributes.
include(joinpath(@__DIR__, "reference.jl"))

expected = reference_catalog()
loaded = load_catalog(ARGS[1])

@assert loaded.frequencies == expected.frequencies
@assert loaded.plus == expected.plus
@assert loaded.cross == expected.cross
@assert Set(keys(loaded.source_parameters)) == Set(keys(expected.source_parameters))
for k in keys(expected.source_parameters)
    @assert loaded.source_parameters[k] == expected.source_parameters[k]
end
@assert loaded.approximant == expected.approximant
@assert loaded.minimum_frequency == expected.minimum_frequency
@assert loaded.maximum_frequency == expected.maximum_frequency
@assert loaded.reference_frequency == expected.reference_frequency
@assert loaded.sampling_frequency == expected.sampling_frequency
println("OK: $(ARGS[1]) matches the reference catalog bit-exactly (julia reader)")
