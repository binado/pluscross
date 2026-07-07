# Write the reference catalog with the Julia package: `julia write_catalog.jl <path>`.
include(joinpath(@__DIR__, "reference.jl"))

save_catalog(ARGS[1], reference_catalog())
println("wrote $(ARGS[1])")
