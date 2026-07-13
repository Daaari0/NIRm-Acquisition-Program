# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 14:30:03 2025

@author: Dario
"""
# Code\Utilities\input_manager.py
import tkinter as tk
from tkinter import filedialog


def select_folder():
    # Initialize the Tkinter root and hide the root window
    root = tk.Tk()
    root.withdraw()

    # Ask the user to select a folder
    folder_selected = filedialog.askdirectory(title="Select Folder to Save File")

    # Optional: show the selected folder (for debugging)
    print(f"Folder selected: {folder_selected}")

    return folder_selected

def ask_User(question):

    while True:
        yesORnot = input(question+'\t(y/n):\t')
        answer = yesORnot_to_boolean(yesORnot)
        if answer is not None:
            break  # Break the loop if a valid choice is made
    return answer


def yesORnot_to_boolean(yesORnot):
    if yesORnot == 'Y' or yesORnot == 'y':
        boolean_choice = True
        print('\n\tYou declared you want to.')
    elif yesORnot == 'n' or yesORnot == 'N':
        boolean_choice = False
        print('\n\tYou declared you DON\'T want to.')
    else:
        boolean_choice = None
        print('\n\tInvalid input. Please enter Y/y or N/n.')
    return boolean_choice