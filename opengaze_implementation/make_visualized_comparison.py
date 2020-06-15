"""
Created on Wed May 20 14:56:33 2020

@author: mayan and kjin
"""
import numpy as np
import pandas as pd
import sys
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

"""
Takes in a path to a csv and returns 3 lists: one containing the durations of 
the segments,one containing the labels for those segments, and one containing 
the start time of those segments

Args:
    csv (string): path to csv file containing label data
    delimiter (string): the delimiter used in the csv file; default = "\t"
"""


def get_intervals(path_to_csv, delimiter="\t"):

    f = open(path_to_csv)
    lines = f.readlines()
    f.close()

    interval_list = []
    label_list = []
    starts = []

    prev_timestamp = 0
    for i in range(1, len(lines)):

        line = lines[i]
        line_list = line.strip().split(delimiter)
        timestamp = int(line_list[0])
        label = line_list[2].strip()

        interval = timestamp - prev_timestamp
        interval_list.append(interval)
        label_list.append(label)
        starts.append(prev_timestamp)

        prev_timestamp = timestamp

    return interval_list[1:], label_list[:-1], starts[1:]


"""
Takes in a path to a csv and creates a plot of the interval durations for the 
contained label data

Args:
    csv (string): path to csv file containing label data
    fig (matplotlib.axis.Axis): the axis to add the plot to
    name (str): the title of the plot
    delim (string): the delimiter used in the csv file; default = "\t"

"""


def make_visualization(csv, ax, name, delim="\t"):
    durations, labels, times = get_intervals(csv, delim)

    # split the data into left, right, and neither
    left_durations = []
    left_starts = []
    right_durations = []
    right_starts = []
    neither_durations = []
    neither_starts = []
    for i in range(len(durations)):
        if labels[i] == 'left':
            left_durations.append(durations[i])
            left_starts.append(times[i])
        elif labels[i] == 'right':
            right_durations.append(durations[i])
            right_starts.append(times[i])
        else:
            neither_durations.append(durations[i])
            neither_starts.append(times[i])

    # plot each of the left, right, and neither data onto the same horizontal figure
    ax.barh(name, left_durations, left=left_starts, height=1, label='left', color=(0.5, 0.6, 0.9))
    ax.barh(name, right_durations, left=right_starts, height=1, label='right', color=(0.6, 0.8, 0))
    ax.barh(name, neither_durations, left=neither_starts, height=1, label='neither', color=(0.95, 0.5, 0.4))


"""
Takes in CLI arguments (the path to the original data csv, and the path to the 
processed OpenGaze output csv) and creates the plot and saves it locally to
"<OpenGaze_csv_name>_visualization.png"
"""


def main(args):
    # first arg should be path to original csv, second should be path to opengaze csv
    if len(args) < 3:
        print("Not enough arguments")
        return
    else:
        original_csv = args[1]
        opengaze_csv = args[2]

        if not os.path.isfile(original_csv):
            print("Invalid path to original labels")
            return

        if not os.path.isfile(opengaze_csv):
            print("Invalid path to opengaze labels")
            return

        print("Creating Visualization...")
        fig = plt.figure(figsize=(30, 8))
        ax = fig.add_subplot(1, 1, 1)
        ax.invert_yaxis()
        make_visualization(original_csv, ax, "Original Data")
        make_visualization(opengaze_csv, ax, "OpenGaze Data")
        ax.legend(loc='upper right')
        ax.set_xlabel("Time (ms)")
        ax.xaxis.set_major_locator(MultipleLocator(10000))
        ax.xaxis.set_minor_locator(AutoMinorLocator(10))
        ax.tick_params(which='minor', length=2)
        ax.tick_params(axis='x', labelrotation=45)
        name = opengaze_csv[:-4] + "_visualization.png"
        fig.savefig(name)
        print("Done! Saved to '" + name + "'")


if __name__ == "__main__":
    main(sys.argv)
