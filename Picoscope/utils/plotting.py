# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 15:22:52 2025

@author: Dario
"""

# utils/plotting.py
import matplotlib.pyplot as plt


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