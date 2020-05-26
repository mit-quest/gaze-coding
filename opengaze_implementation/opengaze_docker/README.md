# OpenGaze Dockerfile

Dockerfile configured for CUDA 10 + cuDNN 7.5 environment, tested using nvidia-docker2

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

All of your outputs will end up in the same folder as your input video; they will also follow this naming convention:

Input video: 
- `[name].mp4`    _(type extension not important, could be something else)_
CSV output: 
- `[name]_gaze_output.txt`
Debugging video output: 
- `[name]_gaze_video.avi`

When you are done processing your videos, you can type `logout` to exit the docker container.

To access your results from outside of the docker container, simply navigate to the directory you made previously to contain all of your videos; the output files should be there as well, since you mounted that directory to the docker container.