#!/bin/sh

GST_DEBUG_DUMP_DOT_DIR=.

AUDIO_FILE=$1

gst-launch-1.0 \
    filesrc location=$AUDIO_FILE ! \
    decodebin ! \
    audioresample ! \
    opusenc bitrate=20000 ! \
    rtpopuspay ! udpsink host=127.0.0.1 port=5002 \
