# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 15:50:21 2025

@author: Dario
"""

# Code\Utilities\data_export.py

import csv
import os
import numpy as np
from Utilities.input_manager import select_folder


def save_to_csv(x, y, z, average_signal, filename='output.csv'):
    # Ensure all inputs are the same length
    length = len(x)
    assert all(len(arr) == length for arr in [y, z, average_signal]), "All arrays must be the same length"

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['x', 'y', 'z', 'average_signal'])  # Header
        for i in range(length):
            writer.writerow([x[i], y[i], z[i], average_signal[i]])

    print(f"✅ Data saved to {filename}")


def save_data(coords, averages):
    folderpath = select_folder()  # 'C:/Users/Dario/OneDrive - IQS/Documentos/Dario/Università/0.LECCE_Triennale/02.PROGRAMMAZIONE_linguaggi_programmi/PHYTON/Code for IQS/6. Microscope 2.0 - Camera n Picoscope n Stage/Code/data_test'
    filename = 'IMG_output' + '.csv'

    # Convert to arrays
    x = np.array([item[0] for item in coords])
    y = np.array([item[1] for item in coords])
    z = np.array([item[2] for item in coords])

    save_to_csv(x, y, z, averages, filename=folderpath + '/' + filename)

def export_data_to_csv(folder_path, position, time, signal, counter, total_points):
    """Exports a single point's scan data to an auto-numbered CSV file named 'data_xxxxx.csv'.
    The time and signal arrays are saved as parallel columns.
    """
    # Determine padding length based on total_points (e.g., 5000 -> 4 digits)
    padding_length = len(str(total_points))
    
    # Format the current index with leading zeros
    current_index = counter - 1 # to make it start from 0 instead of 1
    suffix = f"{current_index:0{padding_length}d}"
    
    # Construct the final full system path
    filename = os.path.join(folder_path, f"data_{suffix}.csv")

    # Unpack coordinates
    x, y, z = position

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write the column headers
        writer.writerow(["X", "Y", "Z", "Time (ms)", "Signal (mV)"])

        # Loop through both arrays simultaneously to write them as columns
        for i, (t, v) in enumerate(zip(time, signal)):
                    if i == 0:
                        # First row: include the coordinates
                        row = [
                            round(x, 4),
                            round(y, 4),
                            round(z, 4),
                            f"{t:.6f}",
                            f"{v:.6f}"
                        ]
                    else:
                        # Subsequent rows: leave coordinate columns empty
                        row = [
                            "", 
                            "", 
                            "", 
                            f"{t:.6f}",
                            f"{v:.6f}"
                        ]
                    writer.writerow(row)

    print(f"✅ Scan data exported to {filename}")