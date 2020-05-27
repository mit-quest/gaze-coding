# OpenGaze Implementation

This directory contains all necessary scripts and tools in order to use OpenGaze to create a fairly accurate label tsv for a video of a person (or baby)

## Directory Contents

- `convert_opengaze_output.py` takes in two CLI args: the path to the original gaze video and the path to the OpenGaze output csv, and writes the cleaned & converted OpenGaze output to a new tsv file in the same format as manual labeling data
- `make_visualized_comparison.py` takes in two CLI args: the path to the original label tsv and the path to the OpenGaze-produced label tsv, and creates a figure visualizing the duration of segments for different types of labels throughout the video. The figure contains two plots: one for the original tsv and one for the OpenGaze-produced tsv, and the resulting image is saved to 'visualization.png'
- `opengaze-docker/` contains all the necessary code and instructions for creating a docker container that you can use to run OpenGaze on a gaze video

