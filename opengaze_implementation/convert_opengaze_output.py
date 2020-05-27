# -*- coding: utf-8 -*-
"""
Created on Mon May 11 21:54:36 2020

@author: mayan
"""

import csv
import sys
import os
import cv2
import pandas as pd

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
    totalNoFrames = cam.get(cv2.CAP_PROP_FRAME_COUNT);
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
    
    name = path_to_csv[:-4] #remove .txt from file name
    
    list_of_lists = []
    fieldnames = ['Time', 'Duration', 'Trackname', 'Comments']
    
    # Calculate the timestamp using frame duration and frame number, and,
    # depending on the values for confidence, gaze_2d_x, and gaze_2d_y, assign
    # a label to that timestamp. If that label is the same as for the previous 
    # timestamp, ignore it. If it's different, store it along with its timestamp.
    prev_label = None
    for i in range(len(lines)):
        line = lines[i]
        line_list = line.strip().split(",")
        
        frame_num = int(line_list[0])
        face_id = int(line_list[1])
        
        if face_id == 0:
            continue
        
        confidence = float(line_list[2])
        gaze_num_x = float(line_list[6])
        gaze_num_y = float(line_list[7])
        
        # Ignore values with confidence lower than .1
        if confidence <= 0.1:
            continue
        elif confidence > .1:
            
            # If the gaze_2d_y value is small (or negative), that means the
            # baby is likely looking up, so set the label to 'None_of_the_above'
            if gaze_num_y < 1.5:
                label = "None_of_the_above"
                
            # If the gaze_2d_x value is positive, that means the baby is likely
            # looking to the left, so set the label to 'left'
            elif gaze_num_x > 0:
                label = "left"
                
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
    # switches to a new label and then switches back in less than 100 ms, or 
    # when it switches to None_of_the_above and then back to left or right in
    # less than 100ms)
    i=0
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
        # back in less than 100 ms
        if label1 == label3 and label2 != label1:
            if time3 - time2 <= 100:
                list_of_lists.pop(i+1)
                list_of_lists.pop(i+1)
            else:
                i+=1
        # remove instances where it switches to None_of_the_above and then 
        # back to left or right in less than 100ms
        elif label2 == "None_of_the_above" and label1 != label2 and label3 != label2:
            if time3 - time2 <= 100:
                list_of_lists.pop(i+1)
            else:
                i+=1
        else:
            i+=1
    
    # Write out the resulting data to a csv
    list_of_lists.append([int(end_time), 0, "end", "(null)"])
    df = pd.DataFrame(list_of_lists, columns=fieldnames)    
    df.to_csv(name+'_converted.tsv', index=False, sep="\t")
            
"""
Takes in CLI arguments (the path to the original gaze video, and the path to 
the OpenGaze output csv (i.e. [name].txt) and writes the cleaned & converted 
OpenGaze output to a new tsv file ([name]_convertd.tsv) in the same format as
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
            print("Invalid path to output file")
            return
        
        frame_len, duration = get_vid_info(video_path)
        print("Frame length:", frame_len)
        print("\n")
        print("Converting video...")
        convert_csv_file(csv_path, frame_len, duration)
        name = csv_path[:-4] + '_converted.tsv'
        print("Done! Output saved to "+name)
        
                
if __name__== "__main__":
    main(sys.argv)
        
                
            
        