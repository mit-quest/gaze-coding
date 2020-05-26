FROM nvidia/cuda:10.0-devel-ubuntu16.04

ENV CUDNN_VERSION 7.5.1.10
LABEL com.nvidia.cudnn.version="${CUDNN_VERSION}"

COPY password.txt /

# cudnn install
RUN apt-get update && apt-get install -y --no-install-recommends \
            libcudnn7=$CUDNN_VERSION-1+cuda10.1 \
            libcudnn7-dev=$CUDNN_VERSION-1+cuda10.1 && \
    apt-mark hold libcudnn7 && \
    rm -rf /var/lib/apt/lists/*

RUN apt-get update \
    && apt-get install -y firefox openssh-server xauth x11-apps \ 
    && mkdir /var/run/sshd \
    && echo 'root:2477' | chpasswd \
    && sed -i 's/PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
    && sed -i "s/^.*X11Forwarding.*$/X11Forwarding yes/" /etc/ssh/sshd_config \
    && sed -i "s/^.*X11UseLocalhost.*$/X11UseLocalhost no/" /etc/ssh/sshd_config 

# requirements for opengaze installation
RUN apt-get update && apt-get install -y \
    sudo \
    git \
    wget \
    vim \
    unzip \
    cmake \
    python-dev \
    python-numpy \
    python-pip \
    python-setuptools \
    python-scipy \
    libopenblas-dev \
    liblapack-dev \
    libgtk2.0-dev \
    pkg-config \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libdc1394-22-dev \
    libprotobuf-dev \
    libleveldb-dev \
    libsnappy-dev \
    libhdf5-serial-dev \
    protobuf-compiler \
    libgflags-dev \
    libgoogle-glog-dev \
    liblmdb-dev \
    libboost-all-dev \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*


# install OpenCV
RUN wget https://github.com/opencv/opencv/archive/3.4.0.zip && \
    unzip 3.4.0.zip && \
    cd opencv-3.4.0 && \
    mkdir -p build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D WITH_TBB=ON -D WITH_CUDA=OFF -D BUILD_SHARED_LIBS=ON .. && \
    make -j4 && \
    make install && \
    cd ../.. && \
    rm 3.4.0.zip && \
    rm -r opencv-3.4.0

# install dlib
RUN wget http://dlib.net/files/dlib-19.13.tar.bz2 && \
    tar xf dlib-19.13.tar.bz2 && \
    cd dlib-19.13 && \
    mkdir -p build && \
    cd build && \
    cmake .. && \
    cmake --build . --config Release && \
    make install && \
    ldconfig && \
    cd ../.. && \
    rm dlib-19.13.tar.bz2 && \
    rm -r dlib-19.13

# install OpenFace 2.0.6
ENV BASE_DIR=/opt

ENV OPENFACE_ROOT=$BASE_DIR/OpenFace
RUN mkdir -p $OPENFACE_ROOT && \
    cd $OPENFACE_ROOT && \
    git -c http.sslVerify=false clone --depth 1 https://github.com/TadasBaltrusaitis/OpenFace.git -b OpenFace_2.0.6 . && \
    bash download_models.sh && \
    mkdir -p build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE .. && \
    make && make install

# install OpenGaze and custom Caffe
ENV OPENGAZE_ROOT=$BASE_DIR/OpenGaze
RUN mkdir -p $OPENGAZE_ROOT && \
    cd $OPENGAZE_ROOT && \
    # Following link no longer works so we used a new one:
    # git -c http.sslVerify=false clone --depth 1 https://git.perceptualui.org/public-projects/opengaze.git . && \    
    git -c http.sslVerify=false clone --depth 1 https://git.hcics.simtech.uni-stuttgart.de/public-projects/opengaze.git . && \
    mkdir -p $OPENGAZE_ROOT/content/caffeModel && \
    cd $OPENGAZE_ROOT/content/caffeModel && \
    wget https://datasets.d2.mpi-inf.mpg.de/MPIIGaze/alexnet_face.prototxt && \
    wget https://datasets.d2.mpi-inf.mpg.de/MPIIGaze/alexnet_face.caffemodel

ENV CAFFE_ROOT=$BASE_DIR/caffe
RUN mkdir -p $CAFFE_ROOT && \
    cd $CAFFE_ROOT && \
    git -c http.sslVerify=false clone --depth 1 https://github.com/BVLC/caffe.git . && \
    cp -r $OPENGAZE_ROOT/caffe-layers/include $CAFFE_ROOT && \
    cp -r $OPENGAZE_ROOT/caffe-layers/src $CAFFE_ROOT && \
    mkdir build && \
    cd build && \
    cmake -DCUDA_ARCH_NAME=Manual -DCUDA_ARCH_BIN="${CUDA_ARCH_BIN}" -DCUDA_ARCH_PTX="${CUDA_ARCH_PTX}" \
    -D CMAKE_INSTALL_PREFIX=/usr/local -D USE_CUDNN=0 -D OPENCV_VERSION=3 -D BLAS=Open .. && \
    make -j4 all && make install && \
    cd ../ && \
    rm -r build

ADD CMakeLists.txt.docker $OPENGAZE_ROOT/CMakeLists.txt

RUN cd $OPENGAZE_ROOT && \
    mkdir -p build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE .. && \
    make && make install

RUN cd $OPENGAZE_ROOT/exe && \
    mkdir -p build && \
    cd build && \
    cmake -D CMAKE_BUILD_TYPE=RELEASE .. && \
    make

# add opengaze bin to PATH
ENV PATH $PATH:$OPENGAZE_ROOT/exe/build/bin

WORKDIR /work

ENV NOTVISIBLE "in users profile"
RUN echo "export VISIBLE=now" >> /etc/profile

EXPOSE 22
#ENTRYPOINT ["sh", "-c", "/usr/sbin/sshd && tail -f /dev/null"]
CMD ["/usr/sbin/sshd", "-D"] 
