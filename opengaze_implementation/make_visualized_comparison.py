# -*- coding: utf-8 -*-
"""
Created on Wed May 20 14:56:33 2020

@author: mayan
"""

import pandas as pd
import sys
import os
import matplotlib.pyplot as plt

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
    fig (matplotlib.pyplot.figure): the figure to add the plot to
    fig_num (int): the number of the plot
    name (str): the title of the plot
    delim (string): the delimiter used in the csv file; default = "\t"

"""
def make_visualization(csv, fig, fig_num, name, delim="\t"):
    durations, labels, times = get_intervals(csv, delim)
    left = []
    right = []
    none = []
    bottom=[]
    
    for i in range(len(labels)):
        label = labels[i]
        duration = durations[i]
        
        if label == "left":
            left.append(-1 * duration)
            right.append(0)
            none.append(0)
            bottom.append(0)
        elif label == "right":
            left.append(0)
            right.append(duration)
            none.append(0)
            bottom.append(0)
        else:
            left.append(0)
            right.append(0)
            none.append(duration)
            bottom.append(-1 * duration/2)  
            #bottom.append(0)
            
    ax = fig.add_subplot(1, 2, fig_num)
    ax.barh(list(range(len(times))), right, height=1, left=bottom, label=times, color='green')
    ax.barh(list(range(len(times))), left, height=1, left=bottom, label=times, color='blue')
    ax.barh(list(range(len(times))), none, height=1, left=bottom, label=times, color='red')
    ax.invert_yaxis()
    ax.set_title(name)
    ax.set_ylabel("Transition Number")
    ax.set_xlabel("Duration of Segment")
    ax.legend(['right', 'left', 'None of the above'])

"""
Takes in CLI arguments (the path to the original data csv, and the path to the 
processed OpenGaze output csv) and creates the plot and saves it as "visualization.png"
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
        fig = plt.figure(figsize=(16, 16))
        make_visualization(original_csv, fig, 1, "Original Data")
        make_visualization(opengaze_csv, fig, 2, "OpenGaze Data")
        fig.savefig("visualization.png")
        print("Done! Saved to 'visualization.png'")
                
if __name__== "__main__":
    main(sys.argv)