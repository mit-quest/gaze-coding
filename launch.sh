xhost +local:

docker run -it \
    --user="$(id -u):$(id -g)"\
    --env="DISPLAY=$DISPLAY" \
    --volume="$(pwd)/work:/work" \
    --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
    --device=/dev/video0:/dev/video0 \
    --runtime=nvidia \
    --rm opengaze \
    /bin/bash
