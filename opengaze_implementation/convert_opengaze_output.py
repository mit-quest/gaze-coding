import csv
import sys
import os
import cv2
import pandas as pd
import statistics
import numpy as np
import numpy.polynomial.polynomial as poly

from scipy import stats
from scipy.signal import find_peaks
from matplotlib import pyplot as plt

"""
Takes in the path to the original gaze video and uses cv2 to calculate the
duration of each frame (in milliseconds) and the total length of the video
(in milliseconds)
Args:
    path_to_video (string): the path to the original gaze video
"""


def get_vid_info(path_to_video):
    cam = cv2.VideoCapture(path_to_video)
    fps = cam.get(cv2.CAP_PROP_FPS)
    totalNoFrames = cam.get(cv2.CAP_PROP_FRAME_COUNT)
    durationInSeconds = float(totalNoFrames) / float(fps)

    print("Frame rate (fps):", fps)
    print("Duration (s):", durationInSeconds)
    seconds_per_frame = 1.0/fps
    milliseconds_per_frame = 1000 * seconds_per_frame
    durationInMilliseconds = durationInSeconds * 1000
    return milliseconds_per_frame, durationInMilliseconds


"""
Takes in the path to the OpenGaze output file, the length of each frame
(in milliseconds), and the total duration of the corresponding video
(in milliseconds), and translates that data into label data that indicates
each time that the gaze direction changes, and what it changes to (either
left, right, or None_of_the_above)
Args:
    path_to_csv (string): the path to the OpenGaze output file
    frame_length (float): the duration of each frame (in milliseconds)
    end_time (float): the duration of the corresponding video (in milliseconds)

"""


def convert_csv_file(path_to_csv, frame_length, end_time):

    f = open(path_to_csv)
    lines = f.readlines()
    f.close()

    name = path_to_csv[:-4]  # remove .txt from file name

    list_of_lists = []
    fieldnames = ['Time', 'Duration', 'Trackname', 'Comments']

    # Initial cleanup: Exclude entries that correspond to an OpenGaze bug pattern.
    # (The pattern is four zero-confidence entries sandwiched between two
    # nonzero-confidence entries)
    clean_lines = []
    i = 0
    while(i < len(lines)-4):
        line = lines[i]
        line_list = line.strip().split(",")
        confidence = float(line_list[2])

        if confidence == 0:
            follows_pattern = True
            for j in range(3):
                next_confidence = float(lines[i+j].strip().split(",")[2])
                if next_confidence != 0:
                    follows_pattern = False
            fourth_confidence = float(lines[i+4].strip().split(",")[2])
            if fourth_confidence == 0:
                follows_pattern = False
            if follows_pattern:
                i += 4
                continue  # skip these 4 buggy entries
        clean_lines.append(line)
        i += 1

    # Calculate the thresholds used to assign labels:
    gaze_2d_x_data = get_column_as_list(clean_lines, 6)
    gaze_2d_y_data = get_column_as_list(clean_lines, 7)
    x_away_lower_bound, x_away_upper_bound = find_x_bounds(gaze_2d_x_data)
    y_away_upper_bound = get_boundary_value(-1.5, gaze_2d_y_data)

    # Calculate the timestamp using the frame duration and frame number, and,
    # depending on the values for confidence, gaze_2d_x, and gaze_2d_y, assign
    # a label to that timestamp. If that label is the same as for the previous
    # timestamp, ignore it. If it's different, store it along with its timestamp.
    prev_label = None
    for i in range(len(clean_lines)):
        line = clean_lines[i]
        line_list = line.strip().split(",")

        frame_num = int(line_list[0])
        gaze_num_x = float(line_list[6])
        gaze_num_y = float(line_list[7])
        confidence = float(line_list[2])

        # If the confidence is 0 and was not already filtered out, that likely
        # means that the baby is looking away (and thus no face is detected).
        # Note that this label is incorrect in the case that the baby is looking
        # left or right, but OpenGaze was just not able to detect a face or gaze.
        if confidence == 0:
            label = "none"

        # If the gaze_2d_y value is small (or negative), that means the
        # baby is likely looking up, so set the label to 'None_of_the_above'
        # "small" is calculated using the mean and stdev of gaze_num_y
        elif gaze_num_y < max(y_away_upper_bound, 0):
            label = "away"

        elif gaze_num_x < x_away_lower_bound or gaze_num_x > x_away_upper_bound:
            label = "away"

        # If the gaze_2d_x value is positive, that means the baby is likely
        # looking to the left, so set the label to 'left'
        elif gaze_num_x > (x_away_lower_bound + x_away_upper_bound)/2:
            label = "left"
            # OpenGaze tends to predict right-looking gazes as a left vector, so
            # this threshold helps to correct left vectors that are close to vertical
            # and very long.
            if gaze_num_x < 0.45 and gaze_num_y/gaze_num_x > 4:
                label = "right"

        # If the gaze_2d_x value is negative, that means the baby is likely
        # looking to the right, so set the label to 'right'
        else:
            label = "right"

        # Only store labels that differ from the previous label
        if label != prev_label:
            time = int(round((frame_num-1) * frame_length))
            list_of_lists.append([time, 0, label, "(null)"])
            prev_label = label

    # Clean the data further by removing very quick switches (i.e. when it
    # switches to a new label and then switches back in less than 250 ms, or
    # when it switches to None_of_the_above and then back to left or right in
    # less than 250)
    i = 0
    while(i < len(list_of_lists)-2):
        row1 = list_of_lists[i]
        row2 = list_of_lists[i+1]
        row3 = list_of_lists[i+2]

        label1 = row1[2]
        label2 = row2[2]
        label3 = row3[2]

        time2 = row2[0]
        time3 = row3[0]

        # remove instances where it switches to a new label and then switches
        # back in less than 250 ms
        if label1 == label3 and label2 != label1:
            if time3 - time2 <= 250:
                list_of_lists.pop(i+1)
                list_of_lists.pop(i+1)
            else:
                i += 1
        # remove instances where it switches to None_of_the_above and then
        # back to left or right in less than 250 ms
        elif label2 == "None_of_the_above" and label1 != label2 and label3 != label2:
            if time3 - time2 <= 250:
                list_of_lists.pop(i+1)
            else:
                i += 1
        else:
            i += 1

    # Write out the resulting data to a csv
    list_of_lists.append([int(end_time), 0, "end", "(null)"])
    df = pd.DataFrame(list_of_lists, columns=fieldnames)
    df.to_csv(name+'_converted_MOD3.tsv', index=False, sep="\t")


"""
Calculate the upper and lower  "away" thresholds for the gaze_num_x component.
Args:
    input_data (list of floats): gaze_num_x data
"""


def find_x_bounds(input_data):
    # First bin data into buckets, where bins have size `step`
    start = round(min(input_data), 1)
    stop = round(max(input_data), 1)
    step = 0.15
    bin_left_edges = [round(start + step * i, 2) for i in range(round((stop - start) / step + 2))]
    counts, _ = np.histogram(input_data, bin_left_edges)

    # Threshold based on the count of samples in each bin
    maximum_samples = len(input_data) * 0.005
    indices_above_max = [i for i in range(len(counts)) if counts[i] > maximum_samples]
    lower_index = min(indices_above_max)
    upper_index = max(indices_above_max)

    # Find the midpoints of each bin, and get the data values at the thresholds
    x_data = [round(bin_edge + step / 2, 3) for bin_edge in bin_left_edges][:-1]
    return x_data[lower_index], x_data[upper_index]


"""
Gets the column of a csv file and returns it as a list of floats, omitting
OpenGaze's error outputs.
Args:
    csv_lines (list of strings): the list of strings corresponding to a csv file;
        all strings must be convertible to floats
    column_index (int): the index of the target column to convert
"""


def get_column_as_list(csv_lines, column_index):
    column_values = []
    for line in csv_lines:
        line_list = line.strip().split(",")
        value = float(line_list[column_index])
        if abs(value) < 1e10:  # omit OpenGaze's error outputs from our calculations
            column_values.append(float(value))

    return column_values


"""
Calculates the raw score corresponding to a z-score of a sequence.
Args:
    z_score (float): the desired z-score
    input_data (list of floats): the sequence in which to find the raw score
"""


def get_boundary_value(z_score, input_data):
    mean = statistics.mean(input_data)
    stdev = statistics.stdev(input_data)
    return stdev * z_score + mean


"""
Takes in CLI arguments (the path to the original gaze video, and the path to
the raw OpenGaze output csv (i.e. [name].txt) and writes the cleaned & converted
OpenGaze output to a new tsv file ([name]_converted.tsv) in the same format as
the original, manually labeled gaze data
"""


def main(args):

    # first arg should be path to video, second should be path to output file
    if len(args) < 3:
        print("Not enough arguments")
        return
    else:
        video_path = args[1]
        csv_path = args[2]

        if not os.path.isfile(video_path):
            print("Invalid path to video")
            return

        if not os.path.isfile(csv_path):
            print("Invalid path to OpenGaze output file")
            return

        frame_len, duration = get_vid_info(video_path)
        print("Frame length:", frame_len)
        print("\n")
        print("Converting video...")
        convert_csv_file(csv_path, frame_len, duration)
        name = csv_path[:-4] + '_converted.tsv'
        print("Done! Output saved to "+name)


if __name__ == "__main__":
    main(sys.argv)
