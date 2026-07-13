# -*- coding: utf-8 -*-
"""
Created on Thu Jun 26 08:14:46 2025

@author: Dario
"""
# Code\Utilities


def decimal_range(start, stop, increment):
    if start > stop:
        # I need to substract the increment, so I change its sign
        increment *= -1
        while start >= stop:  # opposite consition in case of "negative" direction
            yield start
            start += increment
    else:
        # Otherwise I add the increament up as it is (positive)
        while start <= stop:
            yield start
            start += increment



def format_duration(seconds):
    seconds = int(round(seconds))

    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}min {secs}s" if secs else f"{minutes}min"
    elif seconds < 86400:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}min" if minutes else f"{hours}h"
    else:
        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        return f"{days}d {hours}h" if hours else f"{days}d"