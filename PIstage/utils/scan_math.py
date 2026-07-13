# -*- coding: utf-8 -*-
"""
Created on Fri Jun 27 15:52:09 2025

@author: Dario
"""
# Code\PIstage\utils\scan_math.py


def count_scan_points(x_bounds, y_bounds, z_bounds, step_sizes):
    """
    Calculate the total number of scan points (pixels or voxels)
    in a volume scan based on bounds and step sizes.

    Parameters:
    - x_bounds, y_bounds, z_bounds: (start, end) tuples for each axis
    - step_sizes: (x_step, y_step, z_step)

    Returns:
    - total_points: int
    - (nx, ny, nz): number of points along each axis
    """
    def points_per_axis(start, end, step):
        return int(round((end - start) / step)) + 1

    x_start, x_end = x_bounds
    y_start, y_end = y_bounds
    z_start, z_end = z_bounds
    x_step, y_step, z_step = step_sizes

    nx = points_per_axis(x_start, x_end, x_step)
    ny = points_per_axis(y_start, y_end, y_step)
    nz = points_per_axis(z_start, z_end, z_step)

    total_points = nx * ny * nz
    return total_points, (nx, ny, nz)