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
docker run -it \
    --env="DISPLAY=$DISPLAY" \ 
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \ # Connect X11 to show GUI
    --device=/dev/video0:/dev/video0 \ # Connect webcam
    --volume="~/work:/work" \ # Mount working directory
    --user="$(id -u):$(id -g)" \ # Use the client ID/Group
    --runtime=nvidia \
    --rm opengaze-docker \
    /bin/bash
```
