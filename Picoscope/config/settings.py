# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 14:55:34 2025

@author: Dario
"""

# Code\Picoscope\config\settings.py
import ctypes
from picosdk.ps5000a import ps5000a as ps

# Supported input ranges in order (name, full-scale volts)
available_ranges = [
    ("PS5000A_50MV", 0.05),
    ("PS5000A_100MV", 0.1),
    ("PS5000A_200MV", 0.2),
    ("PS5000A_500MV", 0.5),
    ("PS5000A_1V", 1.0),
    ("PS5000A_2V", 2.0),
    ("PS5000A_5V", 5.0),
    ("PS5000A_10V", 10.0),
    ("PS5000A_20V", 20.0),
    ("PS5000A_50V", 50.0),
]


# Streaming configuration
sample_interval_us = 50
samples_per_buffer = 1000*5*2
num_buffers = 1
total_samples = samples_per_buffer * num_buffers
time_window_sec = total_samples*sample_interval_us * 10**(-6)
# oscilloscope useed to take 3040 points, 50us interval. ->  0.152s time window


# Capture and device settings
resolution = ps.PS5000A_DEVICE_RESOLUTION["PS5000A_DR_12BIT"]
coupling = ps.PS5000A_COUPLING["PS5000A_DC"]
sample_units = ps.PS5000A_TIME_UNITS["PS5000A_US"]
sample_interval = ctypes.c_int32(sample_interval_us)

ratio_mode = ps.PS5000A_RATIO_MODE["PS5000A_RATIO_MODE_NONE"]
analogue_offset = 0.0
enabled = 1