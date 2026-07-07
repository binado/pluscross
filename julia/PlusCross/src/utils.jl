"""
    frequency_array(; sampling_frequency, duration, minimum_frequency, maximum_frequency)

Build the 0-to-Nyquist frequency axis and an in-band mask.

Returns `(frequencies, in_band_mask)`: `frequencies` runs from 0 Hz to the
Nyquist frequency (`sampling_frequency / 2`) in steps of `1 / duration`, and
`in_band_mask` is `true` where
`minimum_frequency <= frequencies <= maximum_frequency`.

`duration * sampling_frequency` must be an even integer (the number of
time-domain samples), so the grid spacing is exactly `1 / duration` and the
last frequency lands exactly on the Nyquist frequency.
"""
function frequency_array(;
        sampling_frequency::Real,
        duration::Real,
        minimum_frequency::Real,
        maximum_frequency::Real
)
    sampling_frequency > 0 ||
        throw(ArgumentError("sampling_frequency must be positive, got $(sampling_frequency)"))
    duration > 0 || throw(ArgumentError("duration must be positive, got $(duration)"))
    nyquist_frequency = sampling_frequency / 2
    0 <= minimum_frequency <= maximum_frequency <= nyquist_frequency ||
        throw(ArgumentError("expected 0 <= minimum_frequency <= maximum_frequency <= nyquist_frequency ($(nyquist_frequency)), got minimum_frequency=$(minimum_frequency), maximum_frequency=$(maximum_frequency)"))

    n_samples_exact = duration * sampling_frequency
    n_samples = round(Int, n_samples_exact)
    tolerance = 4 * eps(Float64) * max(1.0, abs(n_samples_exact))
    abs(n_samples_exact - n_samples) <= tolerance ||
        throw(ArgumentError("duration * sampling_frequency must be an integer number of samples, got duration=$(duration), sampling_frequency=$(sampling_frequency) ($(n_samples_exact) samples)"))
    iseven(n_samples) ||
        throw(ArgumentError("duration * sampling_frequency must be an even integer so the frequency grid reaches the Nyquist frequency exactly, got $(n_samples) samples (duration=$(duration), sampling_frequency=$(sampling_frequency))"))

    nf = n_samples ÷ 2 + 1
    d = 1 / sampling_frequency
    val = 1 / (n_samples * d)
    frequencies = collect(0:(nf - 1)) .* val
    in_band_mask = (frequencies .>= minimum_frequency) .& (frequencies .<= maximum_frequency)
    return frequencies, in_band_mask
end
