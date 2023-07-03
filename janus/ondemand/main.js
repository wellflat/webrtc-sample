
const startButton = document.querySelector('#startButton');
const stopButton = document.querySelector('#stopButton');
const audioStream = document.querySelector('#audioStream');
const infoText = document.querySelector('#info');
startButton.addEventListener('click', start);
stopButton.addEventListener('click', stop);


function start() {
  startButton.disabled = "disabled";
  Janus.init({
    debug: true,
    dependencies: Janus.useDefaultDependencies(),
    callback: () => {
        connect(getServerHost(true));
    }
  });
}

function stop() {
  startButton.disabled = null;
  stopStream(streaming);
}

function connect(host) {
  const janus = new Janus({
    server: host,
    success: () => {
      infoText.innerHTML = '';
      attachPlugin(janus);
    },
    error: (error) => {
      Janus.error('Failed to connect to janus server', error)
      infoText.innerHTML = '<p>Failed to connect to janus server '+ error + '</p>';
    },
    destroyed: () => {
      window.location.reload()
    }
  });
}

let streaming = null;
function attachPlugin(janus) {
   janus.attach({
    plugin: "janus.plugin.streaming",
    opaqueId: 'thisisopaqueid',
    success: (plugin) => {
      Janus.log("Plugin attached! (" + plugin.getPlugin() + ", id=" + plugin.getId() + ")");
      //updateStreamsList(plugin);
      streaming = plugin;
      startStream(streaming);
    },
    error: (error) => {
      Janus.error('Error attaching plugin... ', error)
    },
    onmessage: (msg, jsep) => {
      Janus.log('got a message', msg);
      if (msg && msg.result) {
        Janus.log(msg.result)
      } else if (msg && msg.error) {
        Janus.error(msg.error)
      }
      if (jsep) {
        Janus.log("Handling SDP as well...", jsep);
        const stereo = (jsep.sdp.indexOf("stereo=1") !== -1);
        streaming.createAnswer({
          jsep: jsep,
          tracks: [ { type: 'data' } ],
          media: { audioSend: false, videoSend: false },
          customizeSdp: (jsep) => {
            if(stereo && jsep.sdp.indexOf("stereo=1") === -1) {
              jsep.sdp = jsep.sdp.replace("useinbandfec=1", "useinbandfec=1;stereo=1");
            }
          },
          success: (jsep) => {
            console.log('success', jsep);
            streaming.send({ message: { request: "start" }, jsep: jsep });
          },
          error: (error) => {
            Janus.error("WebRTC error", error);
          }
        });
      }
    },
    onremotetrack: (track, mid, on, metadata) => {
      // mid: 'a' or 'v'
      Janus.log('remote track (mid=' + mid + ') ' + (on ? "added" : "removed")
               + (metadata ? " (" + metadata.reason + ") ": "") + ":", track)
      if (!on) return;
      stream = new MediaStream([track]);
      if (track.muted === false) {
        if (track.kind === 'audio') {
          Janus.log("Created remote audio stream:", stream);
          Janus.attachMediaStream(audioStream, stream);
          audioStream.play();
          audioStream.volume = 0.5;
        } else {
          // nothing
        }
      }
    },
    oncleanup: () => {
      Janus.log('oncleanup');
      //streaming = null;
    }
  })
}

function startStream(streaming) {
  const streamId = 3; // [3] mu-law file source (music) (on demand)
  const body = { request: 'watch', id: streamId };
  streaming.send({ message: body });

}

function stopStream(streaming) {
  const body = { request: "stop" };
  streaming.send({ message: body });
  //streaming.hangup();
}

function updateStreamsList(streaming) {
  let body = { request: "list" };
  streaming.send({
    message: body,
    success: (result) => {
      if(result['list']) {
        const streamList = result['list'];
        for(let mp in streamList) {
          Janus.log("  >> [" + streamList[mp]["id"] + "] " + streamList[mp]["description"] + " (" + streamList[mp]["type"] + ")");
        }
      }

    },
  });
}

function getServerHost(useWs = false) {
  var server = null;
  if(window.location.protocol === 'http:') {
    infoText.innerHTML = "not support http"
    if(useWs) {
      server = "ws://" + window.location.hostname + ":8188/";
    } else {
      server = "http://" + window.location.hostname + ":8088/janus";
    }
  } else {
    if(useWs) {
      server = "wss://" + window.location.hostname + ":8989/";
    } else {
      server = "https://" + window.location.hostname + ":8089/janus";
    }
  }
  return server;
}
