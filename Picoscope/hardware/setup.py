# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 14:56:59 2025

@author: Dario
"""

# hardware/setup.py

import ctypes
from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok
# from config.settings import resolution #this is for main inside the folder Picoscope
from Picoscope.config.settings import resolution


def initialize_scope():
    # Instantiate a blank 16-bit signed integer to store the hardware handle reference returned by the driver API
    chandle = ctypes.c_int16()
    # Establish a USB connection link to the PicoScope with the chosen vertical ADC resolution bit depth
    status = ps.ps5000aOpenUnit(ctypes.byref(chandle), None, resolution)

    # Intercept specific API status warning codes that dictate power state discrepancies
    # Code 282 corresponds to PICO_POWER_SUPPLY_NOT_CONNECTED (using dual-headed USB cable without DC transformer)
    # Code 286 corresponds to PICO_USB3_POWER_REQUEST_INVALID (device requires explicit software instruction to configure power rail routing)
    if status in [282, 286]:
        # Issue a command override to force the oscilloscope to change its power source and run on available USB current
        ps.ps5000aChangePowerSource(chandle, status)
    else:
        # Enforce standard SDK checking to throw an exception immediately if any other hardware initialization error occurs
        assert_pico_ok(status)

    return chandle