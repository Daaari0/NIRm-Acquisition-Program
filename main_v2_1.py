# -*- coding: utf-8 -*-
"""
Created on Tue Jul  1 08:58:52 2025
Modified on Thu Jun 26 13:03:19 2025
@author: Dario
"""


#%% modules and libraries

import numpy as np
import time
from Picoscope.hardware.setup import initialize_scope
from Picoscope.acquisition.capture import auto_capture, suggest_min_range_from_signal
from Picoscope.config.settings import time_window_sec
from picosdk.ps5000a import ps5000a as ps
from PIstage.hardware.stage_control import connect_stage, move_stage, close_all_stages
from PIstage.utils.scan_math import count_scan_points
from PIstage.scanning.raster_volume_scan import run_volume_scan_yield
from Utilities.math_functions import format_duration
from Utilities.plotting import generate_2d_map
from Utilities.input_manager import ask_User, select_folder
from Utilities.data_export import export_data_to_csv, save_data

chandle = None
times, signals, positions , averages = [], [], [], []

#%% Main software definition

def main():
    global chandle
    global times, signals, positions

    # Variable that allows live update
    verbose = False #True/False #TODO: decide to make an user input or not

    # === User-defined scan bounds ===
    '''
    #Camera comparison variables

    x_camera=29.05
    y_camera=26.20
    z_camera=35.2849
    camera_resolution = 1*10**(-3)#expressed in mm #20um but magnifyed 20x by objective, thus 1um
    resolution_reducer=4
    padding= - 0.150 #0.080
    
    x_bounds = (y_camera - 0.160 +padding, y_camera + 0.160 -padding) #for center at 25.2 
    y_bounds = (x_camera - 0.128 +padding, x_camera + 0.128 -padding) #for center at 27.1
    z_bounds = (z_camera, z_camera)
    step_sizes = (camera_resolution*resolution_reducer, camera_resolution*resolution_reducer, 0.1)
    '''

    # Normal scanning variables
    x_bounds = (13, 14)
    y_bounds = (26, 27)
    z_bounds = (34.68, 34.68)
    step_sizes = (1, 1, 0.1)

    # === User-defined acquisition variables ===
    rise_time_PD = 1  # dwell time before acquisition for PD stabilization, (10-90% 19ms on datasheet), but needs around 1s

    # === Picoscope time configuration ===
    # NOTE: these variables are defined in Picoscope.config.settings
    '''
    sample_interval_us = 50
    samples_per_buffer = 1000*5*2
    num_buffers = 1
    total_samples = samples_per_buffer * num_buffers
    time_window_sec = total_samples*sample_interval_us * 10**(-6)
    # Promax oscilloscope used to take 3040 points, 50us interval. ->  0.152s time window
    '''

    #%% ============= start initialization ==============

    # User-option for saving raw data at each pixel
    want_save_raw_data = ask_User('Do you wan to save raw data, as full signals vs time as .csv?')
    if want_save_raw_data:
        print('\nSelect the folder where to save the raw data...')
        folder_path = select_folder()

    #Initializing the picoscope
    chandle = initialize_scope()
    print("✅Scope initialized with handle:", chandle.value)

    # Connect all axes
    for axis in ['X', 'Y', 'Z']:
        connect_stage(axis)
        
    move_stage('Z', 20) #move stage to be out of focus, focal plane is normally around 36

    input('Press ENTER to check baground level (not focusing on sample)')

    # Determine an appropriate starting scale based on background signal
    # Do a quick background scan at a safe large scale
    _, bg_signal = auto_capture(chandle, min_range_name="PS5000A_1V")
    bg_peak = np.max(np.abs(bg_signal))

    # Suggest best minimum range based on that signal
    start_range = suggest_min_range_from_signal(bg_peak)
    print(f"🔍 Background peak = {bg_peak:.2f} mV → Suggested start range: {start_range}")


    #%% === Main logic for stage movement and capture ===
    try:
        # Calculation grid dimensions
        total_points, (nx, ny, nz) = count_scan_points(x_bounds, y_bounds, z_bounds, step_sizes)
        print(f"🔢 Total scan points: {total_points} ({nx} × {ny} × {nz})")

        # Compute and print an estimation of the acquisition time
        time_image_acq = total_points * (0.011 + time_window_sec + rise_time_PD) *1.1 #+10% for scale search
        print(f"🔢 Total time acquisition: {format_duration(time_image_acq)} at least. \n\t It does not consider multiple loops for scale optimization ")
        _ = input('\nDo you want to proceed? press ENTER, otherwise Ctl+C ')


        # === Volume Scan Loop ===
        print('Measuring...')
        start = time.perf_counter()  # counting time acquisition

        for t, s, p, counter in run_volume_scan_yield(
                                            x_bounds, y_bounds, z_bounds, #in run_volume_scan_yield there is the live updates of plots
                                            step_sizes,
                                            move_stage,
                                            chandle=chandle,
                                            min_range_found=start_range,
                                            rise_time_PD = rise_time_PD,
                                            verbose = verbose):

            #This function yields the results at each cycle
            positions.append(p) # dictionary of x, y and z positions

            # Storing the average of the signal in an array
            averages.append(np.mean(np.array(s)))


            #Saving the raw data as positions, time, signal in a csv for each pixel
            if want_save_raw_data:
                export_data_to_csv(folder_path=folder_path, position=p, time=t, signal=s, counter=counter, total_points=total_points)


            print(f'Acquisition completion {counter/total_points*100:.2f} %')

        # END LOOP ACQUISITION
        # = Printing the time spent for acquisition =
        end = time.perf_counter()  # measuring the end of the period of time
        elapsed = end - start
        print(f"⏳ Elapsed time: {format_duration(elapsed)} ")


        # === Visualization, storing and Analysis ===
        generate_2d_map(positions, averages)


        want_save_data = ask_User('Do you wan to save IMG-data?')
        if want_save_data:
            save_data(positions, averages)


    except KeyboardInterrupt:
        print("\nLoop interrupted by user.\n")

        want_save_data = ask_User('Do you wan to save IMG-data anyway?')
        if want_save_data:
            save_data(positions, averages)


    finally:
        # Picoscope shut down
        ps.ps5000aStop(chandle)
        ps.ps5000aCloseUnit(chandle)
        print("PicoScope closed.")

        # Stage Shut down
        close_all_stages()
        print("\n\t✅ Finished.")


if __name__ == "__main__":
    print('\n\t\t****************************************************')
    print('\n\t\tWelcome to the NIR-SWIR Microscope Acquisition Code!\n')
    print('\t\t****************************************************\n')

    main()