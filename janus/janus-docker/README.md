## webrtc-server

[Janus WebRTC Server](https://janus.conf.meetecho.com/)によるストリーミングサーバ  

### ポート
TCPはJanusが提供するWeb API用  
UDPはWebRTC(RTCP/RTP)によるストリーミング通信用  
* 8088/tcp: HTTP(http)
* 8089/tcp: HTTPS(https)
* 8188/tcp: WebSocket(ws)
* 8989/tcp: WebSocket(wss)
* 5002/udp: GStreamer(rtp)

これらのポートは設定ファイルで変更可能  

### 補足
* dockerize経由で設定ファイルに変数展開し、ホスト環境のリソースを直接マウントしないようにした(kubernetes等の分散環境を想定)  
* AWSのElastic IPのように固定IPを1:1で設定できる場合はGATEWAY_IP変数にIPアドレスを指定するようにした  

### TODO
* イメージ軽量化 (alpineイメージ対応)
* TURNサーバとの連携 (STUNだけだと通信不可能な環境用)
* SSL証明書設定
* Janusサーバでのアプリケーション認証
