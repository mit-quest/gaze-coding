# OpenGaze Dockerfile

Dockerfile configured for CUDA 10 + cuDNN 7.5 environment, tested using nvidia-docker2

## Build

```bash
docker build -t opengaze-docker .
```

In addition to basic requirements and OpenGaze library, this image also builds tools under /exe (e.g., GazeVisualization) and add them to PATH.

## Run

In order to run the container image, you can for example

```bash
xhost +local: # this is required to use webcam
docker run -it \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \ # Connect X11 to show GUI
    --device=/dev/video0:/dev/video0 \ # Connect webcam
    --runtime=nvidia \
    --rm opengaze-docker \
    /bin/bash
```

Inside the container, you can test the demo by

```bash
GazeVisualization -d
```

To process pre-recorded videos, you may want to mount local directory and force the same user ID/group as the client side by adding some more options:

```bash
docker run -it \
    --env="DISPLAY=$DISPLAY" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --runtime=nvidia \
    --rm opengaze-docker \
    --user="$(id -u):$(id -g)"\
    --volume="~/work:/work" \
    /bin/bash
```

Then, you can perform gaze estimation on any videos (under ~/work in the above example) by
```bash
GazeVisualization -t video -i test.mov -s
```
