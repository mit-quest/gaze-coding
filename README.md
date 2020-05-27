# gaze-coding

## Directory Contents
* `current_systems_notes/` - contains notes about current gaze estimation systems
* `scripts/` - contains all python scripts
    * `predict_gaze.py` - contains a keras CNN model that predicts the gaze direction using features outputted from OpenFace. Prediction accuracy is about the same as random guessing (~45%).
    * `process_video.py` - script for processing a video using OpenFace and comparing the output data with hand-coded data
    * `standardize_into_gcp.py` - script for merging PsychDS standard gaze files into a CSV file that GCP can process
* `opengaze-implementation/` - contains all necessary code and scripts to create label TSV predicting gaze prediction from a video file using OpenGaze
    * `convert_opengaze_output.py` - script for converting OpenGaze output into label TSV
    * `make_visualized_comparison.py` - script for creating visualization to compare OpenGaze-created & post-processed label TSV and the original, manually-made label TSV
    * `opengaze-docker/` - contains all the necessary code and instructions for creating a docker container that you can use to run OpenGaze on a gaze video


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
    * Couldn't get it to work b/c of dependency issues while installing
    * Decided not to use OpenGaze b/c it was too fragile: even if we get it to work, any update would cause it to break again
* Moved back to working with OpenFace
    * Tested OpenFace on some videos from scott-gazecoding
        * Results were no better than random guessing, ~40% accuracy
    * Created CNN that used OpenFace extracted features as input
        * Still just ~40-50% accuracy
    * Concluded that OpenFace output didn't give us any meaningful information for this problem
* Ran GCP's video intelligence API on the videos
### Spring 2020
* Tried to use GCP Video Intelligence to create labeling model
    * Tried training on dataset with transitions as their own label
        * Did two versions to try and identify potential bias issues: one with subgroup babies isolated as the testing videos, and one with them mixed in to the training data
        * Both versions had poor accuracy - worse than random guessing
    * Reprocessed original manual labeling data and trained on that
        * Again did two versions to try and identify potential bias issues: one with subgroup babies isolated as the testing videos, and one with them mixed in to the training data
        * Both versions still had poor accuracy - worse than random guessing, and one had 2% accuracy for identifying 'left' - something was clearly wrong
    * Created preprocessed videos using OpenFace for model training, but these were never used
        * Cropped video to just the face of the baby to try and minimize noise
* Pivoted back to trying to use OpenGaze again using docker implementation of OpenGaze
     * Created a new Linux/Debian VM to contain docker
     * Set up X11 forwarding so that OpenGaze could use local machine's GUI since the VM doesn't have one
     * Modified Dockerfile to incorporate root login & X11 forwarding into the docker container
         * Allowed us to successfully run OpenGaze!
     * Did some investigation to understand the output (due to lack of documentation)
     * Wrote a script to take OpenGaze output and convert it into a label TSV
         * Have yet to quantify accuracy, but from looking at the results, it's doing quite well (significantly better than any other attempt so far)
         * In conjunction with the script, this process is fairly uccessful both in segmenting the video & attributing the correct label to the segment
     * Wrote a visualization script to compare the OpenGaze-created label TSV with the original TSV 


