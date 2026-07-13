# NIRm-Acquisition-Program
Automated NIR-SWIR microscopy data acquisition program. Synchronizes a PicoScope 5444D oscilloscope with PI translation stages across the 3D axes. Features dynamic background voltage scaling, a photodiode settling delay, and multi-format data export routines.

# NIR-SWIR Microscopy Acquisition Pipeline

An automated data acquisition suite designed for a Near-Infrared / Short-Wave Infrared (NIR-SWIR) microscopy based on a raster scan. The software orchestrates hardware control, background calibration, spatial raster scanning, and multi-tiered data logging into a unified pipeline.

## System Architecture

The project is structured into modular sub-packages:
* **Picoscope**: Manages hardware initialization, low-level streaming buffer allocation, and dynamic voltage range adjustment to prevent signal clipping.
* **PIstage**: Interfaces with Physik Instrumente (PI) translation stages to handle coordinate positioning and axis homing.
* **Utilities**: Provides shared math functions, file export management, and graphical rendering engines.

## Key Features

* **Dynamic Gain Auto-Scaling**: Samples background noise levels pre-scan to automatically assign the optimal oscilloscope voltage range for maximum signal sensitivity.
* **Transient Delay Stabilization**: Implements an adjustable dwell time after physical stage movements to allow photodiode sensor outputs to settle before waveform capturing.
* **Memory-Efficient Streaming**: Utilizes a low-level C-compatible callback framework to stream and append raw digitizer data continuously without buffer overflows.
* **Flexible Data Export**: Supports exporting both compressed coordinate-averaged matrices and full time-resolved raw voltage vectors on a per-pixel basis.

## Core Prerequisites

* Python 3.x
* PicoSDK (Official driver package from Pico Technology)
* PI Python SDK (pipython)
* NumPy
* Matplotlib

## Operational Workflow

1. Open `main_v2_1.py` to configure spatial boundaries (`x_bounds`, `y_bounds`, `z_bounds`), step sizes, and the photodiode dwell time (`rise_time_PD`).
2. Run `main_v2_1.py` from the console terminal.
3. Respond to the interactive prompt to determine if raw waveform CSV exporting is required.
4. Allow the stage to move to its safe background position, then press ENTER to run the voltage calibration scan.
5. Review the pre-computed grid voxel counts and duration estimation, then press ENTER to begin the live serpentine acquisition.
6. Upon completion or user interruption, save the generated 2D intensity heatmap data when prompted.
