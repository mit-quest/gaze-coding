import numpy as np
import pandas as pd
import sys
import os

"""
Accuracy is calculated by comparing the actual and predicted label at each
millisecond across the length of the original video.
"""


def calculate_accuracies(original_path, truth_path, prediction_path, ms_per_frame, save_name):
    f = open(original_path)
    lines = f.readlines()
    f.close()

    # Calculate the length of the original video in ms
    length_in_frames = lines[-1].split(",")[0]
    length_in_ms = round(float(length_in_frames) * ms_per_frame)

    # Create dictionaries that map each millisecond to the labels [truth, predicted]
    # at that time for each ms in the length of the video.
    truth_dict = parse_tsv_to_dict(truth_path, length_in_ms)
    prediction_dict = parse_tsv_to_dict(prediction_path, length_in_ms)

    # Create dictionaries for each truth label that map each label to
    # the number of times that label is predicted with that truth label
    left_predictions = {"left": 0, "right": 0, "away": 0}
    right_predictions = {"left": 0, "right": 0, "away": 0}
    away_predictions = {"left": 0, "right": 0, "away": 0}

    for t in range(length_in_ms):
        truth_label = truth_dict[t]
        predicted_label = prediction_dict[t]

        if truth_label == "left":
            left_predictions[predicted_label] += 1
        elif truth_label == "right":
            right_predictions[predicted_label] += 1
        else:
            away_predictions[predicted_label] += 1

    total_left_truth = sum(left_predictions.values())
    total_right_truth = sum(right_predictions.values())
    total_away_truth = sum(away_predictions.values())

    row_fieldnames = ["Truth", "Correct prediction", "Confused with", "Proportion of video"]
    row_left = ["left",
                "left: {:.0%}".format(left_predictions["left"]/total_left_truth),
                "right: {:.0%}".format(left_predictions["right"]/total_left_truth) +
                " / away: {:.0%}".format(left_predictions["away"]/total_left_truth),
                "{:.0%}".format(total_left_truth/length_in_ms)]
    row_right = ["right",
                 "right: {:.0%}".format(right_predictions["right"]/total_right_truth),
                 "left: {:.0%}".format(right_predictions["left"]/total_right_truth) +
                 " / away: {:.0%}".format(right_predictions["away"]/total_right_truth),
                 "{:.0%}".format(total_right_truth/length_in_ms)]
    row_away = ["away",
                "away: {:.0%}".format(away_predictions["away"]/total_away_truth),
                "left: {:.0%}".format(away_predictions["left"]/total_away_truth) +
                " / right: {:.0%}".format(away_predictions["right"]/total_away_truth),
                "{:.0%}".format(total_away_truth/length_in_ms)]

    df = pd.DataFrame([row_left, row_right, row_away], columns=row_fieldnames)
    df.to_csv(save_name, index=False, sep="\t")


"""
Convert a time/label tsv to a dictionary with keys being the time (in ms)
for each ms in length_in_ms, and values being the corresponding label at that time.
Args:
    file_path (string): path to the labels file (original or OpenGaze)
"""


def parse_tsv_to_dict(file_path, length_in_ms, delimiter='\t'):
    f = open(file_path)
    lines = f.readlines()[1:]  # ignore the header line
    f.close()

    # Parse the timestamp and label columns of the raw tsv into a dict
    timestamp_to_label = dict()
    for line in lines:
        entries = line.split(delimiter)
        timestamp_to_label[int(entries[0])] = entries[2]

    # Convert the timestamps dict into a continuous time dict, with a
    # [time: label] entry for each ms in the video
    time_to_label = dict()
    current_label = 'away'
    for t in range(length_in_ms):
        # update the current label when there is a time stamp
        if t in timestamp_to_label:
            current_label = timestamp_to_label[t]
        # map time to label, converting all labels that aren't "left" or "right" to "away"
        time_to_label[t] = current_label if current_label == "left" or current_label == "right" else "away"

    return time_to_label


"""
Determine the label at a given time for one of the time/trackname mappings.
Args:
    time (int): target time (in ms)
    mapping (dict): desired mapping from timestamps to tracknames, as generated
        by parse_tsv_to_dict
"""


def get_label(time, mapping):
    trackname = 'none'
    for start in mapping.keys():
        if time >= start:
            trackname = mapping[start]
        else:
            break

    return trackname


"""
Takes in CLI arguments and calculates the accuracy of the predicted labels.
Outputs the accuracy to the terminal and saves a copy locally to
<OpenGaze_labels_name>_accuracy.tsv
"""


def main(original_path, truth_path, prediction_path, ms_per_frame):
    if not os.path.isfile(original_path):
        print("Invalid path to original labels")
        return

    if not os.path.isfile(truth_path):
        print("Invalid path to opengaze labels")
        return

    if not os.path.isfile(prediction_path):
        print("Invalid path to opengaze labels")
        return

    name = prediction_path[: -4] + "_accuracy.tsv"
    calculate_accuracies(original_path, truth_path, prediction_path, ms_per_frame, name)
    print("Done! Saved to '" + name + "'")


if __name__ == "__main__":
    import argparse
    import sys

    argparser = argparse.ArgumentParser(sys.argv[0])
    argparser.add_argument(
        'original_path',
        type=str,
        help='The path to the original OpenGaze output txt/csv file.')
    argparser.add_argument(
        'truth_path',
        type=str,
        help='The path to the label (truth) tsv.')
    argparser.add_argument(
        'prediction_path',
        type=str,
        help='The path to the label predictions (OpenGaze) tsv.')
    argparser.add_argument(
        'ms_per_frame',
        type=float,
        nargs='?',
        default=33.3333,
        help='The length of 1 frame in the original video, in milliseconds. (default is 33.3333 ms)')

    main(**argparser.parse_args().__dict__)
