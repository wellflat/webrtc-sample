#!/bin/sh


gst-launch-1.0 \
    webrtcbin name=webrtcbin bundle-policy=max-bundle latency=100 stun-server=stun://stun.l.google.com:19302 \
        videotestsrc is-live=true \
         ! videoconvert \
         ! queue \
         ! vp8enc target-bitrate=10240000 deadline=1 \
         ! rtpvp8pay \
         ! application/x-rtp,media=video,encoding-name=VP8,payload=96 \
         ! webrtcbin. \
        audiotestsrc is-live=true \
         ! audioconvert \
         ! audioresample \
         ! queue \
         ! opusenc \
         ! rtpopuspay \
         ! application/x-rtp,media=audio,encoding-name=OPUS,payload=97 \
         ! webrtcbin.
