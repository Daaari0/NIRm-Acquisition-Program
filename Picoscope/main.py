# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 14:04:43 2025

@author: Dario
"""
import ctypes

from config.settings import (
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
from hardware.setup import initialize_scope
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import adc2mV, assert_pico_ok

import numpy as np
import matplotlib.pyplot as plt
import time
chandle = None
# == Testing picoscope packages structure =


def stage_ready():
    # Replace this with your real trigger check
    return np.random.rand() < 0.05  # Simulates an occasional True


def capture_loop():
    while True:
        # === Begin Acquisition Loop ===
        print("Waiting for stage ready signal...\n")
        if not stage_ready():
            time.sleep(0.3)  # waits 0.3s before checking if stage ready (trigger to measure)
            continue

        print("Stage is ready — capturing waveform...")

        # Loop over input ranges (start from most sensitive)
        for name, volts in available_ranges:
            channel_range = ps.PS5000A_RANGE[name]

            # Set channel
            ps.ps5000aSetChannel(chandle,
                                 ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                                 enabled,
                                 coupling,
                                 channel_range,
                                 analogue_offset)

            # Allocate buffers
            buffer_stream = np.zeros(samples_per_buffer, dtype=np.int16)
            buffer_capture = np.zeros(total_samples, dtype=np.int16)

            ps.ps5000aSetDataBuffers(chandle,
                                     ps.PS5000A_CHANNEL["PS5000A_CHANNEL_A"],
                                     buffer_stream.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
                                     None,
                                     samples_per_buffer,
                                     0,
                                     ratio_mode)

            # Begin streaming
            ps.ps5000aRunStreaming(chandle,
                                   ctypes.byref(sample_interval),
                                   sample_units,
                                   0,
                                   total_samples,
                                   1,
                                   1,
                                   ratio_mode,
                                   samples_per_buffer)

            actualSampleIntervalNs = sample_interval.value * 1000
            next_sample = 0
            auto_stop = False
            was_called = False

            def callback(handle, noOfSamples, startIndex, overflow, triggerAt, triggered, autoStop, param):
                nonlocal next_sample, auto_stop, was_called
                was_called = True
                end = next_sample + noOfSamples
                buffer_capture[next_sample:end] = buffer_stream[startIndex:startIndex+noOfSamples]
                next_sample += noOfSamples
                if autoStop:
                    auto_stop = True

            cb_func = ps.StreamingReadyType(callback)

            while next_sample < total_samples and not auto_stop:
                was_called = False
                ps.ps5000aGetStreamingLatestValues(chandle, cb_func, None)
                if not was_called:
                    time.sleep(0.01)

            # Check for clipping
            max_adc = ctypes.c_int16()
            ps.ps5000aMaximumValue(chandle, ctypes.byref(max_adc))

            peak_adc = np.max(np.abs(buffer_capture))
            if peak_adc >= 32750 and name != "PS5000A_50V":
                print(f"⚠️ Clipping at {volts} V — retrying with higher range...")
                continue  # Try next range

            # Good signal — convert and plot
            voltages = adc2mV(buffer_capture, channel_range, max_adc)

            # Generate time axis in milliseconds
            time_ms = np.linspace(0, total_samples * actualSampleIntervalNs * 1e-6, total_samples)

            # == PLOT PART ==
            # Autoscale Y-axis based on signal intensity
            ymin, ymax = np.min(voltages), np.max(voltages)
            pad = 0.1 * (ymax - ymin) if ymax > ymin else 100
            ylim = (ymin - pad, ymax + pad)

            from utils.plotting import plot_waveform
            plot_waveform(time_ms, voltages, ylim, volts)

            # == STORE VALUE FOR IMAGE ==
            # I could store data/average sigal and save value into a matrix for heatmap instead of plot
            break  # Exit the range loop if capture is successful


def main():
    global chandle
    chandle = initialize_scope()
    print("Scope initialized with handle:", chandle.value)

    # You’ll insert your capture loop or logic here
    try:
        capture_loop()

    except KeyboardInterrupt:
        print("\nLoop interrupted by user.")

    finally:
        ps.ps5000aStop(chandle)
        ps.ps5000aCloseUnit(chandle)
        print("Scope closed.")


if __name__ == "__main__":
    main()