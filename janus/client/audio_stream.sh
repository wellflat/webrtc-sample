#!/bin/sh

audio_src=$1
audio_src=../data/long.wav

gst-launch-1.0 \
    filesrc location=$audio_src ! \
    decodebin ! \
    audioresample ! \
    opusenc bitrate=20000 ! \
    rtpopuspay ! udpsink host=127.0.0.1 port=5002 \
#        wavparse ! \
#        audioresample ! \
#    audioresample ! audio/x-raw,channels=1,rate=16000 ! \
