#!/usr/bin/python3
# pyright: reportGeneralTypeIssues=false

import signal
import sys
import time
from types import FrameType
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
from gi.overrides import GLib

# TODO: error handling
class AudioRTPStreamer():

    def __init__(self):
        start = time.perf_counter_ns()

        Gst.init(None)
        self.state = Gst.State.NULL
        element = Gst.ElementFactory.make
        self.filesrc = element('filesrc')
        self.decodebin = element('decodebin')
        self.audioresample = element('audioresample')
        self.opusenc = element('opusenc')
        self.rtpopuspay = element('rtpopuspay')
        self.udpsink = element('udpsink')
        self.set_audio_bitrate()    ## bitrate: default 20000
        self.set_udp_destination()  ## udp destination: default localhost:5002
        self.__build_pipeline()
        self.__prepare_stream()

        signal.signal(signal.SIGTERM, self.__signal_handler)

        end = time.perf_counter_ns()
        print(f'initialize: {(end - start) / 1000000} msec')

    def set_audio_path(self, filepath: str) -> None:
        self.filesrc.set_property('location', filepath)

    def set_audio_bitrate(self, bitrate: int=20000) -> None:
        self.opusenc.set_property('bitrate', bitrate)

    def set_udp_destination(self, host: str='127.0.0.1', port: int=5002) -> None:
        self.udpsink.set_property('host', host)
        self.udpsink.set_property('port', port)

    def run(self) -> None:
        if not self.filesrc.get_property('location'):
            raise FileNotFoundError()
        
        print('play')
        self.state = Gst.State.PLAYING
        self.pipeline.set_state(self.state)
        try:
            self.loop.run()
        except:
            pass

        self.state = Gst.State.NULL
        self.pipeline.set_state(self.state)
        print('stop')

    def pause(self):
        print('pause')
        if self.state == Gst.State.PLAYING:
            self.state = Gst.State.READY
            self.pipeline.set_state(self.state)
    
    # TODO: using GObject signal
    def __signal_handler(self, signum: int, frame: FrameType | None):
        print(f'received: {signum}')
        self.pause()
        self.run()

    def __bus_callback(self, bus: Gst.Bus, message: Gst.Message, loop: GLib.MainLoop):
        if message.type == Gst.MessageType.EOS:
            print('end of stream')
            self.state = Gst.State.READY
            self.pipeline.set_state(self.state)
            #self.set_audio_path('../data/sample.wav')
            print('play')
            self.state = Gst.State.PLAYING
            self.pipeline.set_state(self.state)
            #loop.quit()
        elif message.type == Gst.MessageType.ERROR:
            err, debug = message.parse_error()
            sys.stderr.write("Error: %s: %s\n" % (err, debug))
            self.state = Gst.State.NULL
            self.pipeline.set_state(self.state)
            loop.quit()

    def __build_pipeline(self):
        pipe = Gst.Pipeline.new('audio-rtp-pipeline')
        pipe.add(self.filesrc)
        pipe.add(self.decodebin)
        pipe.add(self.audioresample)
        pipe.add(self.opusenc)
        pipe.add(self.rtpopuspay)
        pipe.add(self.udpsink)
        self.pipeline = pipe

        self.decodebin.connect('pad-added', self.__on_pad_added)

        self.filesrc.link(self.decodebin)
        self.decodebin.link(self.audioresample)
        self.audioresample.link(self.opusenc)
        self.opusenc.link(self.rtpopuspay)
        self.rtpopuspay.link(self.udpsink)

    def __prepare_stream(self):
        self.loop = GLib.MainLoop()
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect('message', self.__bus_callback, self.loop)

    def __on_pad_added(self, src, pad):
        audioresample_pad = self.audioresample.get_static_pad('sink')
        pad.link(audioresample_pad)


if __name__ == '__main__':
    streamer = AudioRTPStreamer()
    wav_filepath = './long.wav'
    wav_filepath = sys.argv[1]
    streamer.set_audio_path(wav_filepath)
    streamer.set_udp_destination('172.23.0.2', 5002)
    streamer.run()
