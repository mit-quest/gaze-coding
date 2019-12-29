import pandas as pd
import random
import os

def standardize_files(video_folder, data_path, video_path_prepend, output_csv, stand_func):
    """
    Creates a CSV file that GCP can process by merging PsychDS standard gaze files. Puts the new CSV file
    in the folder data_folder.
    
    Parameters:
        video_folder (String): path to the folder containing all the videos
        data_path (String): path to the folder in which all the PsychDS standard gaze files are in.
        video_path_prepend (String): folder in GCP where the videos are kept (e.g. 'gs://gaze-coding/videos/')
        output_csv (String): name of output CSV file to put newly formatted data (e.g. all.csv)
        stand_func (function): standardization function to use; chosen from standardize, 
                   standardize_multi, and standardize_filter.
    """    
    time_conv = 1/1000 #time conversion factor; time in PsychDS format is in milliseconds, and we want to convert it into seconds
    possible_labels = {"left", "right", "away"}
    
    video_files = os.listdir(video_folder) #list of videos within the folder video_folder
    
    video_paths = []
    labels = []
    start_times = []
    end_times = []
    
    constants = (time_conv, video_path_prepend, possible_labels)
    csv_data = (video_paths, labels, start_times, end_times)
    
    for video_file in video_files:
        video_name = video_file.split('_')[-2]
        data_path = data_path + video_name + '_timecourse_data.tsv'
        data = pd.read_csv(data_path, delimiter="\t")
        video_data = (video_file, data)
        
        stand_func(constants, csv_data, video_data)
    
    #creates the csv file in the same folder as the data
    d = {'video_path': video_paths, 'label': labels, 'start_time': start_times, 'end_time': end_times}
    df_output = pd.DataFrame(data = d)
    df_output.to_csv(data_path + output_csv, index=False, header=False)
    
def standardize(constants, csv_data, video_data):
    """
    Separates the gaze data file of a video based on row.
    
    Parameters:
        constants, csv_data, video_data (tuples): tuples containing the necessary information, as specified
            in the code of standardize_files
    """
    #separates out the variables within each of the tuples
    time_conv, video_path_prepend, possible_labels = constants
    video_paths, labels, start_times, end_times = csv_data
    video_file, data = video_data
    
    #goes through each row in the gaze file (skipping the last one, since the last label is "end")
    for idx in range(len(data)-1):
        row = data.iloc[idx]
        next_row = data.iloc[idx+1]
            
        start_time = round(time_conv * row['Time'], 3)
        end_time = round(time_conv * (next_row['Time'] - 1), 3) #one millisecond before the start time of the next row
        
        #makes sure that the start and end times are valid
        if end_time <= start_time: continue
        #this is the last row with a label, so we will specify the end time as the end of the video
        #(which is denoted by 'inf' in GCP)
        if idx == len(data) - 2:
            end_time = 'inf'
            
        video_paths.append(video_path_prepend + video_file)
        start_times.append(start_time)
        end_times.append(end_time)
        
        #labels anything that is not left, right, or away as None_of_the_above (e.g. peek)
        if row['Trackname'] in possible_labels:
            labels.append(row['Trackname'])
        else:
            labels.append('None_of_the_above')

def standardize_multi(constants, csv_data, video_data):
    """
    Separates the gaze data file of a video into intervals of 1-5 seconds randomly, giving each of 
    
    Parameters:
        constants, csv_data, video_data (tuples): tuples containing the necessary information, as specified
            in the code of standardize_files
    """
    #separates out the variables within each of the tuples
    time_conv, video_path_prepend, possible_labels = constants
    video_paths, labels, start_times, end_times = csv_data
    video_file, data = video_data
    
    video_length = round(data.iloc[len(data)-1]['Time']/1000, 3) #finds video length from the last row (labeled "end")
    start_time = 0 #start time of current interval considering
    idx = 0 #keeps track of current row in gaze data file
    
    while start_time < video_length:
        interval_length = random.randint(1,5)
        
        #find end time of interval
        if start_time + interval_length < video_length:
            #the start time of the next interval is start_time + interval_length, so the end time of the
            #current interval is one millisecond before that
            end_time = start_time + interval_length - 0.001
        else:
            end_time = float('inf')
        
        labels_set = set() #set of labels within the interval
        #find all labels within the interval
        while round(time_conv * data.iloc[idx]['Time'], 3) < end_time and data.iloc[idx]['Trackname'] != 'end':
            #labels anything that is not left, right, or away as None_of_the_above (e.g. peek)
            if data.iloc[idx]['Trackname'] in possible_labels:
                labels_set.add(data.iloc[idx]['Trackname'])
            else:
                labels_set.add('None_of_the_above')
            idx += 1
        
        video_paths.extend([video_path_prepend + video_file] * len(labels_set))
        start_times.extend([start_time] * len(labels_set))
        end_times.extend([end_time if end_time != float('inf') else 'inf'] * len(labels_set))
        labels.extend(list(labels_set))
        
        #next interval start time
        start_time += interval_length