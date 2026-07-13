# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:43:27 2025

@author: Dario
"""

# main.py

from hardware.stage_control import connect_stage, move_stage, close_all_stages

if __name__ == "__main__":
    # Connect all axes
    for axis in ['X', 'Y', 'Z']:
        connect_stage(axis)

    var = input('\nwanna move stages? press ENTER')
    # Move them to demo positions
    move_stage('X', 21.0)
    move_stage('Y', 12.0)
    move_stage('Z', 5.0)

    # Shut down
    close_all_stages()
