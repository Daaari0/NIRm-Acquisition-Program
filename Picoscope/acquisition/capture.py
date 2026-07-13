# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 15:18:38 2025

@author: Dario
"""
# Picoscope/acquisition/capture.py

import ctypes
import numpy as np
import time
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import adc2mV

from Picoscope.config.settings import (
    available_ranges,
    sample_interval_us,
    samples_per_buffer,
    num_buffers,
    total_samples,
    resolution,
    enabled,
    coupling,
    analogue_offset,
    ratio_mode,
    sample_interval,
    sample_units
)


def auto_capture(chandle, min_range_name=None):
    """
    Captures a waveform using the lowest non-clipping input range,
    starting optionally from a provided minimum range name.
    """
    # Look up the index of the suggested starting range in the configuration list "available_ranges"
    if min_range_name:
        start_idx = next((i for i, (n, _) in enumerate(available_ranges) if n == min_range_name), 0)
    else:
        start_idx = 0

    # Iteratively test ranges from the selected minimum index upward to find the optimal gain
    for name, volts in available_ranges[start_idx:]:
        channel_range = ps.PS5000A_RANGE[name]

        # Apply the current vertical scale  settings to physical Channel A on the scope
        ps.ps5000aSetChannel(
            chandle,
            ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
            enabled,
            coupling,
            channel_range,
            analogue_offset
        )

        # Allocate memory arrays: buffer_stream acts as a rolling block cache, buffer_capture stores the final compiled run
        buffer_stream = np.zeros(samples_per_buffer, dtype=np.int16)
        buffer_capture = np.zeros(total_samples, dtype=np.int16)

        # Bind the rolling memory buffer to the hardware driver API via a low-level C pointer
        ps.ps5000aSetDataBuffers(
            chandle,
            ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
            buffer_stream.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            None,
            samples_per_buffer,
            0,
            ratio_mode
        )

        # Launch the continuous streaming on the hardware unit
        ps.ps5000aRunStreaming(
            chandle,
            ctypes.byref(sample_interval),
            sample_units,
            0,
            total_samples,
            1,
            1,
            ratio_mode,
            samples_per_buffer
        )

        # Convert the actual sampling interval returned by the hardware from microseconds to nanoseconds
        actualSampleIntervalNs = sample_interval.value * 1000
        next_sample = 0
        auto_stop = False
        was_called = False

        # Define the inner event callback that fires when the driver's buffer fills with new samples
        def callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
            nonlocal next_sample, auto_stop, was_called
            was_called = True
            end = next_sample + noOfSamples
            # Slice and append data from the rolling stream block into the global capture array
            buffer_capture[next_sample:end] = buffer_stream[startIndex:startIndex+noOfSamples]
            next_sample += noOfSamples
            if autoStop:
                auto_stop = True

        # Wrap the Python callback into a strict C-compatible function pointer type
        cb_func = ps.StreamingReadyType(callback)

        # Poll the driver loop continuously until the target sample size is fully collected
        while next_sample < total_samples and not auto_stop:
            was_called = False
            # Force the driver to process current hardware values and trigger the callback
            ps.ps5000aGetStreamingLatestValues(chandle, cb_func, None)
            # Yield CPU execution briefly if no new samples were delivered in the polling pass
            if not was_called:
                time.sleep(0.01)

        # Retrieve the maximum possible raw Analog-to-Digital Converter value for scaling calculations
        max_adc = ctypes.c_int16()
        ps.ps5000aMaximumValue(chandle, ctypes.byref(max_adc))
        peak_adc = np.max(np.abs(buffer_capture))


        # Check if the signal saturated the ADC limits (32768 maximum, clipping flag set safely at 32750)
        if peak_adc >= 32750 and name != "PS5000A_50V":
            print(f"⚠️ Clipping at {volts} V — retrying with higher range...")
            continue  # Try next range

        # Convert raw counts to physical voltage values using the hardware's dynamic calibration range
        voltages = np.array(adc2mV(buffer_capture, channel_range, max_adc))
        # Build an equivalent parallel time vector in milliseconds using nanosecond interval steps
        time_ms = np.linspace(0, total_samples * actualSampleIntervalNs * 1e-6, total_samples)

        print(f"✅ Signal captured using range: {volts} V")
        return time_ms, voltages

    # Throw an exception if even the hardware's maximum attenuation limit saturates completely
    raise RuntimeError("❌ All input ranges clipped — signal too strong.")


def suggest_min_range_from_signal(peak_mv, safety_factor=1.5):
    """
    Given a peak voltage in millivolts, return the name of the smallest
    input range that is likely to capture it without clipping.

    Parameters:
    - peak_mv: float, peak of background signal in mV
    - safety_factor: multiplier to avoid being too close to the range limit

    Returns:
    - str: name of suggested input range (e.g. 'PS5000A_2V')
    """
    # Magnify the peak reading by a safety buffer to prevent edge noise from causing clips
    adjusted_mv = peak_mv * safety_factor
    
    # Scan the range configuration arrays to pick the most tightly bounded scale
    for name, volts in available_ranges:
        if volts * 1000 >= adjusted_mv:
            return name

    return "PS5000A_50V"  # fallback in case signal is very large