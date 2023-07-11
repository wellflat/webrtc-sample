# Ubuntu 22.04 LTS
FROM ubuntu:jammy AS builder
ENV DEBIAN_FRONTEND=noninteractive

# Multi stage build, build phase
WORKDIR /build

# global dependencies
RUN \
  apt-get update && \
  apt-get install -y \
    git \
    pkg-config \
    libtool \
    automake \
    autoconf \
    cmake

# usrsctp
RUN \
  git clone https://github.com/sctplab/usrsctp && \
  cd usrsctp && \
  git reset --hard 579e6dea765c593acaa8525f6280b85868c866fc && \
  cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr/local . && \
  make -j$(nproc) && \
  make install

# libnice
RUN \
  apt-get update && \
  apt-get install -y \
    libssl-dev \
    libglib2.0-dev \
    python3 \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    ninja-build \
    gtk-doc-tools && \
  pip3 install meson

RUN \
  git clone --branch 0.1.18 https://gitlab.freedesktop.org/libnice/libnice.git && \
  cd libnice && \
  meson builddir && \
  ninja -C builddir && \
  ninja -C builddir install

# libsrtp
RUN \
  apt-get update && \
  apt-get install -y \
    libssl-dev

RUN \
  git clone --branch v2.3.0 https://github.com/cisco/libsrtp.git && \
  cd libsrtp && \
  ./configure --prefix=/usr/local --enable-openssl && \
  make -j$(nproc) shared_library && \
  make install

# janus-gateway
RUN \
  apt-get update && \
  apt-get install -y \
    build-essential \
    libwebsockets-dev \
    libssl-dev \
    libglib2.0-dev \
    libmicrohttpd-dev \
    libjansson-dev \
    libsofia-sip-ua-dev \
    libopus-dev \
    libogg-dev \
    libavcodec-dev \
    libavformat-dev \
    libavutil-dev \
    libcurl4-openssl-dev \
    liblua5.3-dev \
    libconfig-dev \
    gengetopt

RUN \
  git clone https://github.com/meetecho/janus-gateway.git
RUN cd ./janus-gateway && \
  sh autogen.sh && \
  ./configure --prefix=/opt/janus \
    --enable-post-processing \
    --disable-rabbitmq \
    --disable-mqtt \
    --disable-nanomsg \
    --disable-gelf-event-handler

RUN cd ./janus-gateway && \
  make -j$(nproc) && \
  make install && \
  make configs

# dockerize
RUN \
  apt-get update && \
  apt-get install -y \
    wget

ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Multi stage build, package phase
FROM ubuntu:jammy
ARG janus_uid=999
ARG ulimit_nofile_soft=524288
ARG ulimit_nofile_hard=1048576

# runtime dependencies of janus-gateway
RUN \
  apt-get update && \
  apt-get install -y \
    libwebsockets16 \
    libssl3 \
    libglib2.0-0 \
    libmicrohttpd12 \
    libjansson4 \
    libsofia-sip-ua-glib3 \
    libopus0 \
    libogg0 \
    libavcodec58 \
    libavformat58 \
    libavutil56 \
    libcurl4 \
    liblua5.3-0 \
    libconfig9 && \
 rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local /usr/local
COPY --from=builder /opt/janus /opt/janus

# ulimits
RUN \
  echo ":${janus_uid}	soft	nofile	${ulimit_nofile_soft}" > /etc/security/limits.conf && \
  echo ":${janus_uid}	hard	nofile	${ulimit_nofile_hard}" >> /etc/security/limits.conf

RUN groupadd -g ${janus_uid} janus && useradd -r -u ${janus_uid} -g janus janus

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ADD conf /conf

# Start the Janus gateway server
ENV LD_LIBRARY_PATH=/opt/janus/lib/janus:/usr/local/lib:/usr/local/lib/x86_64-linux-gnu
CMD ./entrypoint.sh
