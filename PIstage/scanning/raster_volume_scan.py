# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 12:49:02 2025

@author: Dario
"""

# PIstage/scanning/raster_volume_scan.py
import time

from Utilities.math_functions import decimal_range
from Picoscope.acquisition.capture import auto_capture
from Utilities.plotting import (initialize_3d_plot,
                                        update_3d_plot,
                                        finalize_plot,
                                        initialize_live_waveform_plot,
                                        update_live_waveform_plot,
                                        finalize_waveform_plot)

def run_volume_scan_yield(
                x_bounds, y_bounds, z_bounds,
                step_sizes,
                move_stage,
                chandle,
                min_range_found,
                rise_time_PD=1,
                verbose = False):

    """Performs a 3D serpentine scan.

    Parameters:
    - x_bounds, y_bounds, z_bounds: (start, end) tuples
    - step_sizes: (x_step, y_step, z_step)
    - move_stage: function(axis_label: str, position: float) -> float
    - capture_loop: function(current_pos: dict, target_pos: dict)
    """
    #Unpacking scanning variables
    x_start, x_end = x_bounds
    y_start, y_end = y_bounds
    z_start, z_end = z_bounds
    x_step, y_step, z_step = step_sizes


    if verbose:
        # Initialize live raster plot
        fig, ax, points, _ = initialize_3d_plot(x_bounds, y_bounds, z_bounds)
        # Initialize live Picoscope waveform plot
        fig_wf, ax_wf, line_wf = initialize_live_waveform_plot()
        # pause before starting the make sure the plots are ready
        time.sleep(2)  # time is seconds

    acq_counter = 0
    # Loop over all the stage positions for acquisition
    for z in decimal_range(z_start, z_end, z_step):
        _= move_stage("Z", z)
        for j, y in enumerate(decimal_range(y_start, y_end, y_step)):
            _ = move_stage("Y", y)

            # Bidirectional X scan
            x_line = decimal_range(x_start, x_end, x_step)
            if j % 2 != 0:
                x_line = reversed(list(x_line))
            for x in x_line:
                _ = move_stage("X", x)

                time.sleep(rise_time_PD)  # wait for rise time photodiode (10-90% 19ms on datasheet), but needs around 1s

                print(f"📡 Measuring at X={x:.4f}, Y={y:.4f}, Z={z:.4f}")
                time_value, signal = auto_capture(chandle, min_range_name=min_range_found)  

                acq_counter += 1
                yield time_value, signal, (x, y, z), acq_counter

                if verbose:
                    # During scan, updating live raster track plot
                    update_3d_plot(ax, fig, points, x, y, z)
                    #  and updating live picoscope waveform plot
                    update_live_waveform_plot(ax_wf, line_wf, time_value, signal)

    print('\nAll done.')
    if verbose:
        # After scan, closing plot windows:
        finalize_plot()
        finalize_waveform_plot()
        print('\n you can close the plots and the image will pop up.')