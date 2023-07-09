# Ubuntu 22.04 LTS
FROM ubuntu:jammy AS build
ENV DEBIAN_FRONTEND=noninteractive

# Multi stage build, Build phase
# Create workdir
RUN mkdir /build

# Install global build dependencies
RUN \
  apt-get update && \
  apt-get install -y \
    git \
    pkg-config \
    libtool \
    automake \
    autoconf \
    cmake

# Build usrsctp from sources
RUN \
  cd /build && \
  git clone https://github.com/sctplab/usrsctp && \
  cd usrsctp && \
  git reset --hard 579e6dea765c593acaa8525f6280b85868c866fc && \
  cmake -DCMAKE_INSTALL_PREFIX:PATH=/usr/local . && \
  make -j$(nproc) && \
  make install

# Install build dependencies of libnice
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

# Build libnice from sources as one shipped with ubuntu is a bit outdated
RUN \
  cd /build && \
  git clone --branch 0.1.18 https://gitlab.freedesktop.org/libnice/libnice.git && \
  cd libnice && \
  meson builddir && \
  ninja -C builddir && \
  ninja -C builddir install

# Install build dependencies of libsrtp
RUN \
  apt-get update && \
  apt-get install -y \
    libssl-dev

# Build libsrtp from sources as one shipped with ubuntu does not support AES-GCM profiles
# This needs to use /usr or /usr/local as a prefix.
# See https://github.com/meetecho/janus-gateway/issues/2019
# See https://github.com/meetecho/janus-gateway/issues/2024
RUN \
  cd /build && \
  git clone --branch v2.3.0 https://github.com/cisco/libsrtp.git && \
  cd libsrtp && \
  ./configure --prefix=/usr/local --enable-openssl && \
  make -j$(nproc) shared_library && \
  make install

# Install build dependencies of janus-gateway
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

# Build janus-gateway from sources
RUN \
  cd /build && \
  git clone https://github.com/meetecho/janus-gateway.git
RUN cd /build/janus-gateway && \
  sh autogen.sh && \
  ./configure --prefix=/opt/janus \
    --enable-post-processing \
    --disable-rabbitmq \
    --disable-mqtt \
    --disable-nanomsg \
    --disable-gelf-event-handler

RUN cd /build/janus-gateway && \
  make -j$(nproc) && \
  make install && \
  make configs

# Install dependencies of dockerize
RUN \
  apt-get update && \
  apt-get install -y \
    wget

# Install dockerize
ENV DOCKERIZE_VERSION v0.6.1
RUN wget https://github.com/jwilder/dockerize/releases/download/$DOCKERIZE_VERSION/dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && tar -C /usr/local/bin -xzvf dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz \
    && rm dockerize-linux-amd64-$DOCKERIZE_VERSION.tar.gz

# Multi stage build, Package phase
FROM ubuntu:jammy
ARG janus_uid=999
ARG ulimit_nofile_soft=524288
ARG ulimit_nofile_hard=1048576

# Install runtime dependencies of janus-gateway
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

# Copy all things that were built
COPY --from=build /usr/local /usr/local
COPY --from=build /opt/janus /opt/janus

# Set ulimits
RUN \
  echo ":${janus_uid}	soft	nofile	${ulimit_nofile_soft}" > /etc/security/limits.conf && \
  echo ":${janus_uid}	hard	nofile	${ulimit_nofile_hard}" >> /etc/security/limits.conf

# Do not run as root unless necessary
RUN groupadd -g ${janus_uid} janus && useradd -r -u ${janus_uid} -g janus janus

# Copy entrypoint and config templates
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ADD conf /conf

# Start the gateway
ENV LD_LIBRARY_PATH=/opt/janus/lib/janus:/usr/local/lib:/usr/local/lib/x86_64-linux-gnu
CMD ./entrypoint.sh
