# gaze-coding

## Directory Contents
* current_systems_notes/ - contains notes about current gaze estimation systems
* scripts/ - contains all python scripts
    * predict_gaze.py - contains a keras CNN model that predicts the gaze direction using features outputted from OpenFace. Prediction accuracy is about the same as random guessing (~45%).
    * process_video.py - script for processing a video using OpenFace and comparing the output data with hand-coded data
    * standardize_into_gcp.py - script for merging PsychDS standard gaze files into a CSV file that GCP can process

## Project Log
### Spring 2019
* Evaluated different gaze coding platforms on infant videos, decided to proceed with OpenFace
* Set up OpenFace on GCP VM
    * Created Jupyter notebook to act as an interface between the users and OpenFace
* Decided to try to set up OpenGaze on GCP VM
    * OpenGaze builds upon OpenFace, and thus might perform better on infant videos
    * Did not manage to get it working
### Fall 2019
* Tried to set up OpenGaze on GCP VM
    * Couldn'€t get it to work b/c of dependency issues while installing
    * Decided not to use OpenGaze b/c it was too fragile: even if we get it to work, any update would cause it to break again
* Moved back to working with OpenFace
    * Tested OpenFace on some videos from scott-gazecoding
        * Results were no better than random guessing, ~40% accuracy
    * Created CNN that used OpenFace extracted features as input
        * Still just ~40-50% accuracy
    * Concluded that OpenFace output didn't give us any meaningful information for this problem
* Ran GCP's video intelligence API on the videos
