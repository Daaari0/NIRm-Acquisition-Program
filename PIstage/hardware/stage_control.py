# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:41:14 2025

@author: Dario
"""

# hardware/stage_control.py

from pipython import GCSDevice, pitools
# this line is for the main inside the folder PIstage
# from config.settings import CONTROLLERNAME, STAGE_SERIALS, STAGE_MODEL, REFERENCE_MODE
from PIstage.config.settings import CONTROLLERNAME, STAGE_SERIALS, STAGE_MODEL, REFERENCE_MODE

# Store all connected stage devices by label
stage_devices = {}


def connect_stage(axis_label):
    """Connect and reference a single axis (X, Y, or Z)."""
    # Extract the unique hardware serial number mapping to the specified target identifier
    serial = STAGE_SERIALS[axis_label]
    # Initialize an instance of the Physik Instrumente General Command Set (GCS) device interface
    device = GCSDevice(CONTROLLERNAME)
    # Establish a physical USB communication link to the motor controller using its serial ID
    device.ConnectUSB(serialnum=serial)
    # Run the core initialization sequence to define the stage model parameters and perform a homing (calibration) routine
    pitools.startup(device, stages=[STAGE_MODEL], refmodes=[REFERENCE_MODE])
    # Cache the active connection handle in the global dictionary registry for runtime tracking
    stage_devices[axis_label] = device
    print(f"✅ {axis_label}-axis connected and referenced.")
    return device


def move_stage(axis_label, position_mm, speed=2):
    """Move the specified axis to the given position in mm at a certain speed, 2mm/s if not specified."""
    # Retrieve the active GCS handle from the connection registry mapping to the target label
    stage = stage_devices.get(axis_label)
    if stage is None:
        raise ValueError(f"No stage connected for axis '{axis_label}'")
    axis = 1  # PI controllers default to axis 1 for single-axis stages, each axis has its controller.
    # Send a absolute positioning command to drive the stage to the targeted millimeter coordinate
    stage.MOV(axis, position_mm)
    stage.VEL(axis, speed)  # set speed
    pitools.waitontarget(stage, axes=axis)  # waits to get to target before next command
    # Query the physical encoder to read and confirm the current final position of the hardware stage
    pos = stage.qPOS(axis)[axis]
    print(f"\n📍 {axis_label}-axis now at {pos:.3f} mm")
    return pos


def close_all_stages():
    """Close all connected stage devices."""
    for label, dev in stage_devices.items():
        dev.CloseConnection()
        print(f"\t🔌 {label}-axis disconnected.")