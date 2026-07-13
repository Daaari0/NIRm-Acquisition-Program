# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:22:52 2025

@author: Dario
"""

# Code\Utilities\plotting.py
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np


def plot_waveform(time_ms, voltages, ylim, volts_label):
    plt.figure(figsize=(10, 4))
    plt.plot(time_ms, voltages, label=f"Input Range: ±{volts_label} V")
    plt.xlabel("Time (ms)")
    plt.ylabel("Signal (mV)")
    plt.title("Captured Waveform – Auto-scaled")
    plt.ylim(ylim)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()

# %% ==2D heatmap at the end of the acquisition ==


def generate_2d_map(coords, averages):
    # Extract X, Y from positions
    coords = [(x, y) for x, y, z in coords]

    # Find grid extents
    x_coords = sorted(set(x for x, _ in coords))
    y_coords = sorted(set(y for _, y in coords))
    x_to_idx = {x: i for i, x in enumerate(x_coords)}
    y_to_idx = {y: i for i, y in enumerate(y_coords)}

    # Initialize 2D map matrix
    avg_map = np.zeros((len(y_coords), len(x_coords)))  # [rows][cols] = [Y][X]

    for (x, y), val in zip(coords, averages):
        i = y_to_idx[y]  # row
        j = x_to_idx[x]  # col
        avg_map[i, j] = val

    # Setup the bounding box (extent) for the plot
    # If a dimension has only 1 point, we artificially give it thickness 
    # so imshow can render a visible 2D ribbon/strip.
    if len(x_coords) == 1:
        x_min, x_max = x_coords[0] - 0.5, x_coords[0] + 0.5
    else:
        x_min, x_max = min(x_coords), max(x_coords)

    if len(y_coords) == 1:
        y_min, y_max = y_coords[0] - 0.5, y_coords[0] + 0.5
    else:
        y_min, y_max = min(y_coords), max(y_coords)

    # Plot
    plt.imshow(avg_map, origin='lower', extent=[x_min, x_max, y_min, y_max],
               aspect='auto', cmap='hot')
    
    plt.xlabel("X [mm]")
    plt.ylabel("Y [mm]")
    plt.title("Average Signal Map")
    plt.colorbar(label='Mean Voltage [mV]')
    
    # Force ticks to show correctly even if there's only 1 coordinate on an axis
    plt.xticks(x_coords)
    plt.yticks(y_coords)
    
    plt.show()

    return x_coords, y_coords, avg_map



# %% == Live scaning track ==

#  SETUP FUNCTION


def initialize_3d_plot(x_bounds, y_bounds, z_bounds):
    def pad_if_flat(bounds):
        start, end = bounds
        if start == end:
            pad = 0.1
            return (start - pad, end + pad)
        return bounds

    x_bounds = pad_if_flat(x_bounds)
    y_bounds = pad_if_flat(y_bounds)
    z_bounds = pad_if_flat(z_bounds)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(*x_bounds)
    ax.set_ylim(*y_bounds)
    ax.set_zlim(*z_bounds)
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Live 3D Scan (Z-colored)")
    plt.ion()
    plt.show()

    # Position the window on screen (for Qt backend)
    manager = plt.get_current_fig_manager()
    try:
        # “Place the window at the top-left corner (x=0), 50 pixels below the top edge (y=50),
        #   and make it 800×600 (width x height) pixels in size.”
        # in set geometry the numbers mean x,y, width, height
        manager.window.setGeometry(0, 50, 400, 300)  # Move to left edge
    except AttributeError:
        print("❗ Plot positioning not supported with this backend.")

    return fig, ax, [], []

#  UPDATE FUNCTION


def update_3d_plot(ax, fig, positions, x, y, z):
    positions.append((x, y, z))
    xs, ys, zs = zip(*positions)
    z_vals = np.array(zs)
    colors = cm.rainbow((z_vals - np.min(z_vals)) / max(np.ptp(z_vals), 1e-6))

    # ax.clear()

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("Live 3D Scan (Z-colored)")
    ax.scatter(xs, ys, zs, c=colors, s=50)

    plt.pause(0.001)

#  CLOSE FUNCTION


def finalize_plot():
    plt.ioff()
    plt.show()

# %% === Live Picoscope signal ===


#  Initialize waveform plot window in a fixed position
def initialize_live_waveform_plot():
    fig, ax = plt.subplots(figsize=(6, 3))
    line, = ax.plot([], [], lw=2)
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Signal (mV)")
    ax.set_title("Live Signal – PicoScope")
    ax.grid(True)
    fig.tight_layout()
    plt.ion()
    plt.show()

    # Try to place it bottom-left
    try:
        manager = plt.get_current_fig_manager()
        manager.window.setGeometry(0, 400, 600, 300)  # Adjust Y depending on your screen
    except AttributeError:
        pass

    return fig, ax, line

#  Update with new data


def update_live_waveform_plot(ax, line, time_ms, voltages):
    ax.set_title("Live Signal")

    # Handle X-axis (time) with 5% padding
    x_min, x_max = min(time_ms), max(time_ms)
    if x_min == x_max:
        delta_x = 0.05 * abs(x_min) if x_min != 0 else 0.01
        x_min -= delta_x
        x_max += delta_x
    else:
        pad_x = 0.05 * (x_max - x_min)
        x_min -= pad_x
        x_max += pad_x
    ax.set_xlim(x_min, x_max)

    # Handle Y-axis (signal) with 5% padding
    y_min, y_max = min(voltages), max(voltages)
    if y_min == y_max:
        delta_y = 0.05 * abs(y_min) if y_min != 0 else 0.01
        y_min -= delta_y
        y_max += delta_y
    else:
        pad_y = 0.05 * (y_max - y_min)
        y_min -= pad_y
        y_max += pad_y
    ax.set_ylim(y_min, y_max)

    line.set_data(time_ms, voltages)
    ax.figure.canvas.draw()
    ax.figure.canvas.flush_events()

    plt.pause(0.01)  # Ensures the plot visibly updates during the scan


#  finalizer


def finalize_waveform_plot():
    plt.ioff()
    plt.show()

# %%