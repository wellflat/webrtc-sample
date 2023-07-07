#!/usr/bin/python3

import sys
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GLib, GObject, Gst
import time


Gst.init(None)
element = Gst.ElementFactory.make
webrtcbin = element('webrtcbin')
webrtcbin.set_property('stun-server', 'stun://stun.l.google.com:19302')
print(webrtcbin)
