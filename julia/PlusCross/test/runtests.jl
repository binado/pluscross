using Test
using HDF5
using PlusCross

function make_catalog(; nfreq = 8, nsamples = 5)
    return WaveformCatalog(;
        frequencies = collect(range(5.0, 100.0; length = nfreq)),
        plus = randn(nfreq, nsamples) .+ im .* randn(nfreq, nsamples),
        cross = randn(nfreq, nsamples) .+ im .* randn(nfreq, nsamples),
        source_parameters = (
            redshift = rand(nsamples) .* 2.0,
            luminosity_distance = 100.0 .+ rand(nsamples) .* 4900.0
        ),
        approximant = "IMRPhenomXAS_NRTidalv3",
        minimum_frequency = 5.0,
        maximum_frequency = 100.0,
        reference_frequency = 20.0,
        sampling_frequency = 8192.0
    )
end

@testset "round trip is bit-exact" begin
    catalog = make_catalog()
    mktempdir() do dir
        path = joinpath(dir, "catalog.h5")
        save_catalog(path, catalog)
        loaded = load_catalog(path)
        @test loaded.frequencies == catalog.frequencies
        @test loaded.plus == catalog.plus
        @test loaded.cross == catalog.cross
        # HDF5 groups iterate alphabetically, so key order may differ from the
        # saved NamedTuple; the spec attaches no meaning to parameter order.
        @test Set(keys(loaded.source_parameters)) == Set(keys(catalog.source_parameters))
        for k in keys(catalog.source_parameters)
            @test loaded.source_parameters[k] == catalog.source_parameters[k]
        end
        @test loaded.approximant == catalog.approximant
        @test loaded.minimum_frequency == catalog.minimum_frequency
        @test loaded.maximum_frequency == catalog.maximum_frequency
        @test loaded.reference_frequency == catalog.reference_frequency
        @test loaded.sampling_frequency == catalog.sampling_frequency
    end
end

@testset "on-disk layout matches the spec" begin
    catalog = make_catalog(nfreq = 8, nsamples = 5)
    mktempdir() do dir
        path = joinpath(dir, "catalog.h5")
        save_catalog(path, catalog)
        h5open(path, "r") do f
            # HDF5.jl reports dims in Julia (column-major) order; the C-order
            # dataspace on disk is the reverse, i.e. (nsamples, nfreq).
            @test size(f["polarizations/plus"]) == (8, 5)
            @test eltype(f["polarizations/plus"]) == ComplexF64
            @test size(f["frequencies"]) == (8,)
            @test size(f["source_parameters/redshift"]) == (5,)
            a = attributes(f)
            @test read(a["format_name"]) == "waveform_catalog"
            @test read(a["format_version"]) == 1
            @test read(a["domain"]) == "frequency"
        end
    end
end

@testset "constructor validates shapes" begin
    c = make_catalog()
    @test_throws ArgumentError WaveformCatalog(
        c.frequencies, c.plus, c.cross[:, 1:(end - 1)], NamedTuple(),
        c.approximant, 5.0, 100.0, 20.0, 8192.0)
    @test_throws ArgumentError WaveformCatalog(
        c.frequencies[1:(end - 1)], c.plus, c.cross, NamedTuple(),
        c.approximant, 5.0, 100.0, 20.0, 8192.0)
    @test_throws ArgumentError WaveformCatalog(
        reverse(c.frequencies), c.plus, c.cross, NamedTuple(),
        c.approximant, 5.0, 100.0, 20.0, 8192.0)
    @test_throws ArgumentError WaveformCatalog(
        c.frequencies, c.plus, c.cross, (redshift = zeros(3),),
        c.approximant, 5.0, 100.0, 20.0, 8192.0)
end

@testset "loader rejects invalid files" begin
    catalog = make_catalog()
    mktempdir() do dir
        for (attr, value) in
            (("domain", "time"), ("format_version", Int64(2)),
                ("format_name", "other"))
            path = joinpath(dir, "bad_$(attr).h5")
            save_catalog(path, catalog)
            h5open(path, "r+") do f
                delete_attribute(f, attr)
                attributes(f)[attr] = value
            end
            @test_throws ArgumentError load_catalog(path)
        end

        path = joinpath(dir, "missing_attr.h5")
        save_catalog(path, catalog)
        h5open(path, "r+") do f
            delete_attribute(f, "reference_frequency")
        end
        @test_throws ArgumentError load_catalog(path)

        path = joinpath(dir, "missing_dataset.h5")
        save_catalog(path, catalog)
        h5open(path, "r+") do f
            delete_object(f, "polarizations/cross")
        end
        @test_throws ArgumentError load_catalog(path)

        path = joinpath(dir, "bad_frequencies.h5")
        save_catalog(path, catalog)
        h5open(path, "r+") do f
            delete_object(f, "frequencies")
            write(f, "frequencies", reverse(catalog.frequencies))
        end
        @test_throws ArgumentError load_catalog(path)
    end
end

@testset "frequency_array" begin
    @testset "values" begin
        frequencies, in_band_mask = frequency_array(;
            sampling_frequency = 8.0, duration = 4.0,
            minimum_frequency = 1.0, maximum_frequency = 3.0)
        @test frequencies == collect(0:16) .* 0.25
        @test in_band_mask == ((frequencies .>= 1.0) .& (frequencies .<= 3.0))
    end

    @testset "reaches nyquist when n_samples is even" begin
        sampling_frequency = 8192.0
        frequencies, _ = frequency_array(;
            sampling_frequency = sampling_frequency, duration = 4.0,
            minimum_frequency = 0.0, maximum_frequency = sampling_frequency / 2)
        @test frequencies[end] == sampling_frequency / 2
    end

    @testset "in-band mask boundaries are inclusive" begin
        frequencies, in_band_mask = frequency_array(;
            sampling_frequency = 8.0, duration = 4.0,
            minimum_frequency = 1.0, maximum_frequency = 3.0)
        @test in_band_mask[findfirst(==(1.0), frequencies)]
        @test in_band_mask[findfirst(==(3.0), frequencies)]
        @test !in_band_mask[findfirst(==(0.75), frequencies)]
        @test !in_band_mask[findfirst(==(3.25), frequencies)]
    end

    @testset "rejects invalid inputs" begin
        @test_throws ArgumentError frequency_array(;
            sampling_frequency = 0.0, duration = 4.0,
            minimum_frequency = 1.0, maximum_frequency = 3.0)
        @test_throws ArgumentError frequency_array(;
            sampling_frequency = 8.0, duration = 0.0,
            minimum_frequency = 1.0, maximum_frequency = 3.0)
        @test_throws ArgumentError frequency_array(;
            sampling_frequency = 8.0, duration = 4.0,
            minimum_frequency = -1.0, maximum_frequency = 3.0)
        @test_throws ArgumentError frequency_array(;
            sampling_frequency = 8.0, duration = 4.0,
            minimum_frequency = 3.0, maximum_frequency = 1.0)
        @test_throws ArgumentError frequency_array(;
            sampling_frequency = 8.0, duration = 4.0,
            minimum_frequency = 1.0, maximum_frequency = 5.0)
    end
end
