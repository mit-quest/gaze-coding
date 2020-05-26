# OpenGaze Dockerfile

Dockerfile configured for CUDA 10 + cuDNN 7.5 environment, tested using nvidia-docker2

## Prereqs

In order for the following instructions to work, you need to either be running the following code directly on a Linux/Debian machine with GUI capabilities, or running it on a Lunix/Debian VM that is using X11 forwarding to forward the GUI to your machine.

_\[Note: DISCLAIMER - I myself have only done this using the latter setup; I have not tested this using the former, but I hypothesize that it would theoretically work. I don't have any guarantee, though, so attempt at your own risk. \]_

To set up your Linux/Debian VM with X11 forwarding, you can follow the instructions in this doc: [https://docs.google.com/document/d/1qIyPKCmCBztTqQzTRtrR9zmNq6LPEPk9TxRE939bPDo/edit?usp=sharing](https://docs.google.com/document/d/1qIyPKCmCBztTqQzTRtrR9zmNq6LPEPk9TxRE939bPDo/edit?usp=sharing)

## Build

```bash
docker build -t opengaze-docker .
```
In addition to basic requirements and OpenGaze library, this image also builds tools under /exe (e.g., GazeVisualization)

If you'd like to be able to access the build logs after the build is over, write them to a file while building using the following command instead of the one above:
```bash
docker build -t opengaze-docker . 2>&1 | tee build_logs/[log file name]
```

## Run / Container Setup

In order to be able to use OpenGaze, we want to run a docker container from the image we built with x11 forwarding enabled using the following steps.

First, place all the video files you want to convert into one directory; we’ll be mounting this working directory to the container you make so that you can access the videos in the container.

Then, run
```bash
docker run --name [container name of your choice] \
           --runtime nvidia \
           --hostname $(hostname) \
           -v /tmp/.X11-unix:/tmp/.X11-unix \
           -v [working directory]:/work \
           -e 'DISPLAY=${DISPLAY}' \
           -it -d -P opengaze-docker
```

This will start the docker container. In order to enter the container though, you will need to `ssh` into it.
So, next, find the port to connect to it through:
```bash
docker port [name] 22
```
Then, connect with this command:
```bash
ssh root@localhost -X -p [PORT]
```
It will prompt you for `root@localhost`’s password; simply enter `2477`.

Now, we should be inside of the container. However, X11 will not work quite yet, so we need to fix that. Add a line specifying  `X11UseLocalhost no` to `etc/ssh/sshd_config`, then run:
```bash
sudo service ssh restart
```
That command will have stopped your container and booted you out, so then use the following command to restart it:
```bash
docker start [name]
```
Finally, ssh in again using:
```bash
ssh root@localhost -X -p [PORT]
```
Again, it will prompt you for `root@localhost`’s password; enter the same thing as before: `2477`.

Now that you're inside the docker container again, test that X11 forwarding works with `xeyes`. You should see a pair of googly-esque eyes pop up on your screen.

If you want to leave the container without stopping it, you can use `logout`.

Once you've done the above setup once, as long as you don't stop the container, you should be able to `ssh` into it and pick up where you left off without needing to repeat the process above. Even if you accidentally (or intentionally) stop the container, you should still be able to start it using `docker start` and then enter it using `ssh` without having to repeat the setup process. You should only need to repeat the setup process if you kill the container and have to run another one from the image you built.

## OpenGaze Use

Once inside the container with X11 forwarding set up, you will likely want to use OpenGaze to process some videos. If you followed the first step in the setup instructions, your video files should be accessible in the `/work` directory; feel free to run `ls /work` to confirm that, and verify the path to your video of interest.

Since PATH isn’t always updated properly, we’ll use the direct path to the exe file to run the OpenGaze processing command:
```bash
/opt/OpenGaze/exe/build/bin/GazeVisualization -t video -i [path to video file]
```
This will output a .txt file containing a csv table describing the OpenGaze output. If you would also like to output the OpenGaze debugging video (where it shows you the original video but with a red line that represents the gaze it detected), then run the following command instead
```bash
/opt/OpenGaze/exe/build/bin/GazeVisualization -t video -i [path to video file] -s true
```
_Note: for more info on other optional command-line arguments, go to [https://git.hcics.simtech.uni-stuttgart.de/public-projects/opengaze/-/wikis/Command-line-arguments](https://git.hcics.simtech.uni-stuttgart.de/public-projects/opengaze/-/wikis/Command-line-arguments) _

All of your outputs will end up in the same folder as your input video; they will also follow this naming convention:

**Input video:** 
- `[name].mp4`    _(type extension not important, could be something else)_

**CSV output:** 
- `[name]_gaze_output.txt`

**Debugging video output:**
- `[name]_gaze_video.avi`

When you are done processing your videos, you can type `logout` to exit the docker container.

To access your results from outside of the docker container, simply navigate to the directory you made previously to contain all of your videos; the output files should be there as well, since you mounted that directory to the docker container.

## Understanding the Output

Due to limited or incoherent documentation, we don't exactly know what each component of the OpenGaze text output represents.

Here is the existing documentation: [https://git.hcics.simtech.uni-stuttgart.de/public-projects/opengaze/-/wikis/Output-format](https://git.hcics.simtech.uni-stuttgart.de/public-projects/opengaze/-/wikis/Output-format)

The problem with this is that that documentation lists 18 different categories for one line of data, but when we ran OpenGaze our output only have 14. From deduction and educated guesses, we believe that the output categories (in this order) are:

1. `index` - frame number of input video or camera
2. `face_id` - face identification generated by OpenFace with tracking (although it might misidentify the same face as two different faces)
3. `confidence` - face and facial landmark detection certainty
4. `face_center_3d_x` - x center of face in the camera coordinate system
5. `face_center_3d_y` - y center of face in the camera coordinate system
6. `face_center_3d_z` - z center of face in the camera coordinate system
7. `gaze_2d_x` - x component of the 2D gaze direction vector
8. `gaze_2d_y` - y component of the 2D gaze direction vector
9. `right_eye_3d_x` - x center of right eye in the camera coordinate system
10. `right_eye_3d_y` - y center of right eye in the camera coordinate system
11. `right_eye_3d_z` - z center of right eye in the camera coordinate system
12. `left_eye_3d_x` - x center of left eye in the camera coordinate system
13. `left_eye_3d_y` - y center of left eye in the camera coordinate system
14. `left_eye_3d_z` - z center of left eye in the camera coordinate system

**This is not the official documentation; this is my best guess as to what the categories of the OpenGaze output are given my own investigation.** I wanted to share regardless, though, because I was personally very frustrated by the lack of coherent documentation on the OpenGaze output, and I figured if this can help someone understand the output even a little, that's a plus.
