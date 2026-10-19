---
title: "브라우저 밖 WebRTC: 디바이스 구현"
description: "브라우저가 대신해 주던 캡처·인코딩·패킷화·연결 관리를 디바이스에서 직접 조립한다. libwebrtc·Pion·GStreamer webrtcbin·aiortc·KVS C SDK 선택지, Jetson·Raspberry Pi 하드웨어 인코더 파이프라인, webrtcbin과 Pion 예제, 임베디드 배포 체크리스트를 다룬다."
date: 2026-10-19
tags: [WebRTC, Embedded, GStreamer, Pion, Jetson, RaspberryPi]
prev: /study/webrtc/12-topology-sfu
next: /study/webrtc/14-whip-whep
---

# 브라우저 밖 WebRTC: 디바이스 구현

::: info 학습 목표
- 디바이스에서 WebRTC를 구현할 때 브라우저가 숨겨 주던 책임(캡처·인코딩·혼잡 대응·재연결)이 무엇인지 안다.
- libwebrtc·Pion·GStreamer webrtcbin·aiortc·libdatachannel·KVS C SDK의 언어·라이선스·장단점을 비교해 요구사항에 맞는 스택을 고른다.
- 카메라(V4L2/CSI) → 하드웨어 인코더(`nvv4l2h264enc`, `v4l2h264enc`) → RTP 패킷화 → WebRTC로 이어지는 파이프라인과 보드별 요소 이름을 안다.
- GStreamer webrtcbin의 시그널(`on-negotiation-needed`, `on-ice-candidate`)과 액션 시그널로 협상을 구현하고, Pion으로 H.264 트랙을 송출하는 Go 프로그램 골격을 이해한다.
- CPU·메모리·크로스컴파일·시계 동기·키 저장·watchdog 재시작을 담은 임베디드 배포 체크리스트를 적용한다.
:::

## 1. 브라우저가 숨겨 주던 것들

브라우저에서 WebRTC 송신은 `getUserMedia()` → `addTrack()` 두 줄이면 끝난다. 그 아래에서 브라우저는 카메라를 열고, 색 공간을 변환하고, 인코더를 고르고, 대역폭 추정에 맞춰 비트레이트를 바꾸고, PLI가 오면 키프레임을 만들고, 네트워크가 바뀌면 ICE를 다시 돈다. 농기계·로봇에 달린 카메라에는 브라우저가 없으므로 이 일을 전부 직접 조립해야 한다.

| 영역 | 브라우저가 해 주던 것 | 디바이스에서 직접 할 일 |
|---|---|---|
| 캡처 | `getUserMedia()`, 권한 UI | V4L2(`/dev/videoN`)나 CSI 카메라 드라이버를 열고 포맷·해상도·프레임레이트 협상 |
| 인코딩 | SW/HW 인코더 자동 선택 | 보드 HW 인코더를 직접 구성. 프로파일·키프레임 간격·SPS/PPS 반복 설정 |
| 품질 적응 | GCC·TWCC 추정 → 인코더 비트레이트·해상도 자동 조정 (09장) | 스택이 추정값을 주더라도 HW 인코더에 반영하는 연결은 직접 구현 |
| 손실 복구 | NACK·PLI 처리, 키프레임 즉시 생성 | PLI를 받아 인코더에 "다음 프레임 IDR" 명령을 전달 |
| 연결 | ICE·DTLS-SRTP·SCTP, ICE restart | 스택이 제공하지만 실패 감지·재시도 정책은 애플리케이션 몫 |
| 시그널링 | (원래도 표준 없음, 03장) | WSS/MQTT 클라이언트, 재연결, 인증 토큰 갱신 |
| 생명주기 | 탭을 닫으면 끝 | 무인으로 수개월 동작. 크래시·행(hang)·카메라 분리 시 자동 복구 |

디바이스 쪽의 전형적인 역할도 정해 두자. 디바이스는 보통 <strong>영상은 송신만(sendonly)</strong>, 제어는 DataChannel(11장)이나 MQTT로 <strong>양방향</strong>이다. 오디오는 마이크 송신만 하거나 아예 없다. 운영자 음성을 농기계 스피커로 내보내는 양방향 오디오가 필요해지는 순간 에코 캔슬이 필요해지고, 이것이 스택 선택을 크게 바꾼다(2절).

## 2. 구현 선택지 비교

디바이스용 WebRTC 스택은 "어디까지 해 주는가"가 제각각이다. 미디어 캡처·인코딩까지 포함하는 것(libwebrtc, GStreamer)과, WebRTC 프로토콜 스택만 제공하고 미디어는 밖에서 받는 것(Pion, libdatachannel)으로 나뉜다. 언어·라이선스는 2026년 10월 기준 각 저장소 표기다.

| 선택지 | 언어 | 라이선스 | 장점 | 단점 | 잘 맞는 경우 |
|---|---|---|---|---|---|
| <strong>libwebrtc</strong> (Chromium의 WebRTC 엔진) | C++ | BSD-3-Clause | 브라우저와 같은 엔진 — 혼잡 제어, 오디오 처리(에코 캔슬·잡음 억제), 지터 버퍼 품질이 가장 검증됨. 네이티브 프레임 트랜스포머 등 API가 풍부 | depot_tools·gn·ninja 빌드 체계가 무겁고 바이너리가 큼. HW 인코더 연동은 인코더 인터페이스를 직접 구현해야 함. 내부 API 변경이 잦음 | 양방향 오디오가 핵심, 안드로이드·iOS 앱, 리소스가 넉넉한 디바이스 |
| <strong>Pion</strong> | Go | MIT | 순수 Go라 `GOOS/GOARCH`만 바꾸면 크로스컴파일 끝. RTP/RTCP를 interceptor로 세밀하게 제어. SFU·서버에도 널리 쓰임 | 캡처·인코딩은 범위 밖 (GStreamer·FFmpeg와 조합). GC 일시정지·메모리 사용량 관리 필요 | Go 백엔드 팀, 커스텀 시그널링·라우팅, 엣지 게이트웨이 |
| <strong>GStreamer webrtcbin</strong> | C (GObject; Python·Rust 등 바인딩) | LGPL (GStreamer) | 캡처 → HW 인코더 → 패킷화 → WebRTC를 한 파이프라인으로. 보드 벤더(NVIDIA·Raspberry Pi)가 HW 요소를 GStreamer로 제공 | 시그널링 직접 구현. 대역폭 추정을 인코더 비트레이트에 잇는 일은 직접 하거나 `webrtcsink`(gst-plugins-rs)를 써야 함. 파이프라인 디버깅 난도 | Jetson·Raspberry Pi처럼 GStreamer가 1급 시민인 보드 |
| <strong>aiortc</strong> | Python (asyncio) | BSD-3-Clause | 코드가 짧고 읽기 쉬움. OpenCV·AI 추론 파이프라인과 연결이 쉬움 | 코덱 처리를 소프트웨어로 하므로 임베디드 CPU에 부담. HW 인코더 경로가 기본 제공되지 않음 | PoC, 테스트용 가짜 디바이스·뷰어, 서버 측 AI 처리 |
| <strong>libdatachannel</strong> | C++ (C API 제공) | MPL-2.0 | 가벼운 WebRTC·DataChannel 구현. 미디어 트랙과 H.264 등 RTP 패킷화기 제공 | 캡처·인코딩, 대역폭 추정의 인코더 반영은 직접 | 바이너리 크기에 민감한 C/C++ 디바이스 |
| <strong>KVS WebRTC C SDK</strong> | C | Apache-2.0 | AWS KVS 시그널링·관리형 STUN/TURN과 통합. OpenSSL/mbedTLS·libsrtp·usrsctp·libwebsockets 의존성을 함께 빌드하며 크로스컴파일을 고려해 설계 | KVS 시그널링에 묶인 P2P 구조. 다른 시그널링을 쓰려면 SDK 내부를 고쳐야 함 | AWS 기반 디바이스 영상 플랫폼 → [19장](/study/webrtc/19-kvs-c-sdk) |

어떤 스택을 고를지 판단 흐름으로 정리하면 다음과 같다.

![디바이스 WebRTC 스택 선택 흐름 — AWS KVS 시그널링·TURN을 그대로 쓰면 KVS WebRTC C SDK(19장), 아니면 양방향 오디오(에코 캔슬)가 핵심일 때 libwebrtc, 아니면 보드 HW 인코더가 GStreamer 요소로 제공될 때 GStreamer webrtcbin(또는 webrtcsink, Go 팀이면 Pion + appsink도 대안), 아니면 PoC·테스트 클라이언트일 때 aiortc, 모두 아니면 Pion(Go)이나 libdatachannel(C++)에 외부 인코더를 붙이는 순서로 내려가는 결정 트리](/images/study-webrtc/13-stack-choice-light.png)
![디바이스 WebRTC 스택 선택 흐름 — AWS KVS 시그널링·TURN을 그대로 쓰면 KVS WebRTC C SDK(19장), 아니면 양방향 오디오(에코 캔슬)가 핵심일 때 libwebrtc, 아니면 보드 HW 인코더가 GStreamer 요소로 제공될 때 GStreamer webrtcbin(또는 webrtcsink, Go 팀이면 Pion + appsink도 대안), 아니면 PoC·테스트 클라이언트일 때 aiortc, 모두 아니면 Pion(Go)이나 libdatachannel(C++)에 외부 인코더를 붙이는 순서로 내려가는 결정 트리](/images/study-webrtc/13-stack-choice-dark.png)

몇 가지 보충이다.

- <strong>"미디어는 GStreamer, 프로토콜은 다른 스택"이 흔한 조합이다.</strong> KVS C SDK의 GStreamer 샘플도, Pion으로 만든 디바이스 에이전트도 결국 GStreamer `appsink`(또는 자식 프로세스 stdout)에서 인코딩된 H.264를 받아 WebRTC 스택에 넘긴다. HW 인코더를 가장 쉽게 쓰는 길이 GStreamer이기 때문이다.
- <strong>libwebrtc는 "브라우저 품질"이 필요할 때만</strong> 고른다. 영상 송신만 하는 카메라에 libwebrtc를 넣으면 빌드 체계 유지비가 장점을 압도하기 쉽다. 반대로 운영자와 현장 작업자가 음성으로 대화해야 한다면 에코 캔슬을 직접 만드는 비용이 더 크다.
- <strong>시그널링이 스택 선택을 제약한다.</strong> KVS C SDK는 KVS 시그널링 프로토콜(18장)을 내장하고, WHIP(14장)으로 SFU에 붙는다면 HTTP 클라이언트만 있으면 된다. 자체 WebSocket 시그널링(03장)이라면 어떤 스택이든 직접 붙인다.

## 3. 디바이스 미디어 파이프라인 — 카메라에서 RTP까지

어떤 스택을 고르든 미디어 경로의 모양은 같다.

![디바이스 안에서 카메라(V4L2 /dev/video0 또는 CSI) → 변환·스케일(nvvidconv) → HW 인코더(nvv4l2h264enc / v4l2h264enc) → h264parse(AU 정렬·SPS/PPS) → RTP 패킷화(FU-A·STAP-A) → WebRTC 스택(ICE·DTLS-SRTP)으로 이어지고 단계 사이 데이터가 raw YUY2/NV12, NVMM NV12, H.264 Annex-B, AU, RTP로 바뀌며, 운영자 브라우저로 SRTP를 보내고 RTCP를 받아 WebRTC 스택이 PLI/FIR은 키프레임 강제로, REMB/TWCC 추정은 비트레이트 조정으로 HW 인코더에 되돌려 주는 피드백 루프 그림](/images/study-webrtc/13-device-pipeline-light.png)
![디바이스 안에서 카메라(V4L2 /dev/video0 또는 CSI) → 변환·스케일(nvvidconv) → HW 인코더(nvv4l2h264enc / v4l2h264enc) → h264parse(AU 정렬·SPS/PPS) → RTP 패킷화(FU-A·STAP-A) → WebRTC 스택(ICE·DTLS-SRTP)으로 이어지고 단계 사이 데이터가 raw YUY2/NV12, NVMM NV12, H.264 Annex-B, AU, RTP로 바뀌며, 운영자 브라우저로 SRTP를 보내고 RTCP를 받아 WebRTC 스택이 PLI/FIR은 키프레임 강제로, REMB/TWCC 추정은 비트레이트 조정으로 HW 인코더에 되돌려 주는 피드백 루프 그림](/images/study-webrtc/13-device-pipeline-dark.png)

단계별로 보면 다음과 같다.

1. <strong>캡처</strong>: USB(UVC) 카메라는 V4L2 장치(`/dev/video0`)로 보이고 `v4l2src`로 연다. 원시 YUY2를 주거나 MJPEG을 주는 카메라가 많고, 일부는 H.264를 직접 내보내기도 한다. CSI 카메라는 보드 ISP를 거쳐야 하므로 Jetson은 `nvarguscamerasrc`(Argus), Raspberry Pi는 `libcamerasrc`(libcamera)를 쓴다.
2. <strong>변환·스케일</strong>: 인코더가 받는 포맷(대개 NV12)으로 바꾸고 해상도를 맞춘다. CPU에서 `videoconvert`·`videoscale`로 하면 720p30에서도 코어 하나를 쉽게 잡아먹으므로, Jetson은 `nvvidconv`로 하드웨어 버퍼(`memory:NVMM`)에서 처리한다.
3. <strong>인코딩</strong>: 하드웨어 H.264 인코더. 보드별 요소 이름은 아래 표에 정리했다.
4. <strong>파싱</strong>: `h264parse`가 바이트 스트림을 액세스 유닛(AU, 한 프레임) 단위로 정렬하고, 필요하면 SPS/PPS를 끼워 넣는다.
5. <strong>RTP 패킷화</strong>: NAL 유닛을 MTU에 맞게 FU-A로 쪼개거나 작은 NAL을 STAP-A로 묶는다(08장). GStreamer에서는 `rtph264pay`가, Pion·libdatachannel에서는 스택 내부 패킷화기가 한다.
6. <strong>WebRTC 전송</strong>: ICE로 경로를 잡고 DTLS-SRTP로 암호화해 보낸다.

### 보드별 요소

| 보드 | CSI 캡처 | USB 캡처 | 변환 | H.264 HW 인코더 | 주의 |
|---|---|---|---|---|---|
| Jetson (Xavier, Orin NX, AGX Orin 등) | `nvarguscamerasrc` | `v4l2src`, `nvv4l2camerasrc` | `nvvidconv` (NVMM 버퍼) | `nvv4l2h264enc` (H.265는 `nvv4l2h265enc`) | Jetson Orin Nano는 HW 인코더가 없어 소프트웨어 인코딩이 기본(NVIDIA 문서의 "Software Encode in Orin Nano" 항목) |
| Raspberry Pi 4 이하 | `libcamerasrc` | `v4l2src` | 필요 시 `videoconvert` | `v4l2h264enc` (V4L2 M2M 장치) | 출력 caps에 level을 명시해야 협상되는 경우가 있음 |
| Raspberry Pi 5 | `libcamerasrc` | `v4l2src` | 필요 시 `videoconvert` | 없음 | Raspberry Pi 백서 기준 libx264 소프트웨어 인코딩으로 1080p30 실시간 가능(저지연 모드에서 코어 하나의 약 60%) |
| 범용 x86·기타 | — | `v4l2src` | `videoconvert` | (보드별 상이) | SW 폴백: `x264enc tune=zerolatency speed-preset=ultrafast` |

<strong>Raspberry Pi 5에 하드웨어 H.264 인코더가 없다</strong>는 점은 하드웨어 선정 단계에서 놓치기 쉬운 함정이다. Pi 4에서 잘 돌던 `v4l2h264enc` 파이프라인이 Pi 5에서는 요소 자체가 없어 실패한다. Jetson도 Orin Nano를 고르면 같은 상황이 된다. 카메라 여러 대를 인코딩해야 한다면 보드 데이터시트에서 인코더 유무와 동시 세션 수를 먼저 확인한다.

### WebRTC용 인코더 설정

WebRTC는 녹화용 인코딩과 요구가 다르다. 다음 설정을 기본값으로 삼는다.

- <strong>프로파일은 (Constrained) Baseline부터</strong>: 브라우저 호환성이 가장 넓고 B-프레임이 없다. WebRTC의 H.264는 B-프레임을 전제하지 않으므로(재정렬 지연이 생긴다) Main/High를 쓰더라도 B-프레임은 꺼야 한다. SDP의 `profile-level-id`와 실제 비트스트림이 맞는지도 확인한다(08장).
- <strong>SPS/PPS를 IDR마다 반복</strong>: 늦게 붙은 뷰어나 패킷 손실 후 복구하는 뷰어가 SPS/PPS 없이 IDR만 받으면 디코딩하지 못한다. Jetson은 `insert-sps-pps=true`, Pi는 `repeat_sequence_header=1`, GStreamer 패킷화기는 `rtph264pay config-interval=-1`.
- <strong>키프레임 간격은 짧게, 그리고 요청 시 즉시</strong>: 주기적 IDR(예: 1~2초)은 새 뷰어의 첫 화면 대기 시간을 결정한다. 더 중요한 것은 PLI/FIR을 받았을 때 <strong>즉시</strong> IDR을 만드는 경로다. GStreamer에서는 패킷화기·webrtcbin이 키프레임 요청을 업스트림 force-key-unit 이벤트로 올려 보내고 HW 인코더 요소가 이를 처리한다. 파이프라인 밖(자식 프로세스 등)에 인코더가 있으면 이 경로가 끊긴다(5절).
- <strong>CBR 또는 상한 있는 VBR</strong>: LTE 업링크에서 VBR 순간 피크는 지연과 손실로 직결된다. Jetson은 `control-rate=1`(CBR).
- <strong>비트레이트의 런타임 변경</strong>: 대역폭 추정에 따라 비트레이트를 바꾸려면 인코더가 동작 중 속성 변경을 지원해야 한다. 보드·드라이버 버전마다 다르므로 실제로 `bitrate` 속성을 바꿔 가며 출력 비트레이트가 따라오는지 확인해 둔다.

WebRTC를 붙이기 전에 인코더 단독으로 먼저 검증한다. 파이프라인이 `fakesink`까지 안정적으로 돌고, `tegrastats`(Jetson)나 `top`으로 CPU가 낮게 유지되는지 확인하는 것이 첫 단계다.

```bash
# Jetson — USB 카메라 → NVMM 변환 → HW H.264 (CBR 2 Mbps, Baseline, 2초 IDR)
gst-launch-1.0 -e v4l2src device=/dev/video0 ! \
  'video/x-raw,width=1280,height=720,framerate=30/1' ! \
  nvvidconv ! 'video/x-raw(memory:NVMM),format=NV12' ! \
  nvv4l2h264enc bitrate=2000000 control-rate=1 profile=0 \
    insert-sps-pps=true idrinterval=60 iframeinterval=60 maxperf-enable=true ! \
  h264parse ! 'video/x-h264,stream-format=byte-stream,alignment=au' ! \
  fakesink sync=false

# Raspberry Pi 4 — CSI 카메라 → V4L2 M2M HW 인코더
gst-launch-1.0 -e libcamerasrc ! \
  'video/x-raw,width=1280,height=720,framerate=30/1,format=NV12' ! \
  v4l2h264enc extra-controls="controls,repeat_sequence_header=1,h264_i_frame_period=60,video_bitrate=2000000" ! \
  'video/x-h264,level=(string)4' ! \
  h264parse ! fakesink sync=false
```

## 4. GStreamer webrtcbin

`webrtcbin`은 gst-plugins-bad의 `webrtc` 플러그인에 들어 있는 요소로, PeerConnection 하나를 GStreamer 요소로 구현한다(GStreamer 1.14부터). 송신할 RTP는 요청 패드(`sink_%u`)로 밀어 넣고, 수신 미디어는 `pad-added`로 생기는 src 패드로 나온다. JSEP 동작은 W3C API와 거의 일대일로 대응한다.

| W3C API | webrtcbin |
|---|---|
| `onnegotiationneeded` | 시그널 `on-negotiation-needed` |
| `onicecandidate` | 시그널 `on-ice-candidate` (mline index, candidate 문자열) |
| `createOffer()` / `createAnswer()` | 액션 시그널 `create-offer` / `create-answer` (결과는 `GstPromise`) |
| `setLocalDescription()` / `setRemoteDescription()` | 액션 시그널 `set-local-description` / `set-remote-description` |
| `addIceCandidate()` | 액션 시그널 `add-ice-candidate` |
| `createDataChannel()` / `ondatachannel` | 액션 시그널 `create-data-channel` / 시그널 `on-data-channel` |
| `iceServers` | 속성 `stun-server`, `turn-server`, 액션 시그널 `add-turn-server` |
| `bundlePolicy` | 속성 `bundle-policy` |
| `getStats()` | 액션 시그널 `get-stats` |

파이프라인은 3절의 인코더 체인 끝에 `rtph264pay`와 `webrtcbin`을 붙인 모양이다.

```c
#define PIPELINE_DESC \
  "webrtcbin name=webrtc bundle-policy=max-bundle " \
  "  stun-server=stun://stun.l.google.com:19302 " \
  "v4l2src device=/dev/video0 ! video/x-raw,width=1280,height=720,framerate=30/1 ! " \
  "nvvidconv ! video/x-raw(memory:NVMM),format=NV12 ! " \
  "nvv4l2h264enc bitrate=2000000 control-rate=1 profile=0 insert-sps-pps=true " \
  "  idrinterval=60 iframeinterval=60 maxperf-enable=true ! " \
  "h264parse ! rtph264pay config-interval=-1 pt=96 ! " \
  "application/x-rtp,media=video,encoding-name=H264,payload=96 ! webrtc. "
```

시그널을 연결하는 C 코드의 골격이다. 디바이스가 offer를 만드는 쪽(offerer)인 경우다.

```c
#include <gst/gst.h>
#include <gst/sdp/sdp.h>
#define GST_USE_UNSTABLE_API
#include <gst/webrtc/webrtc.h>

static GstElement *pipe, *webrtc;

/* 시그널링 전송은 앱이 구현한다 (03장의 WebSocket 등). 스레드 안전해야 한다 */
void signaling_send_sdp(const char *type, const char *sdp);
void signaling_send_ice(guint mline_index, const char *candidate);

static void on_offer_created(GstPromise *promise, gpointer user_data) {
  GstWebRTCSessionDescription *offer = NULL;
  const GstStructure *reply = gst_promise_get_reply(promise);
  gst_structure_get(reply, "offer", GST_TYPE_WEBRTC_SESSION_DESCRIPTION, &offer, NULL);
  gst_promise_unref(promise);

  GstPromise *p = gst_promise_new();
  g_signal_emit_by_name(webrtc, "set-local-description", offer, p);
  gst_promise_interrupt(p);
  gst_promise_unref(p);

  gchar *text = gst_sdp_message_as_text(offer->sdp);
  signaling_send_sdp("offer", text);
  g_free(text);
  gst_webrtc_session_description_free(offer);
}

static void on_negotiation_needed(GstElement *element, gpointer user_data) {
  GstPromise *promise = gst_promise_new_with_change_func(on_offer_created, NULL, NULL);
  g_signal_emit_by_name(webrtc, "create-offer", NULL, promise);
}

static void on_ice_candidate(GstElement *element, guint mline_index,
                             gchar *candidate, gpointer user_data) {
  signaling_send_ice(mline_index, candidate);
}

/* 시그널링에서 answer를 받았을 때 */
void on_remote_answer(const char *sdp_text) {
  GstSDPMessage *sdp = NULL;
  gst_sdp_message_new_from_text(sdp_text, &sdp);
  GstWebRTCSessionDescription *answer =
      gst_webrtc_session_description_new(GST_WEBRTC_SDP_TYPE_ANSWER, sdp);

  GstPromise *p = gst_promise_new();
  g_signal_emit_by_name(webrtc, "set-remote-description", answer, p);
  gst_promise_interrupt(p);
  gst_promise_unref(p);
  gst_webrtc_session_description_free(answer);
}

/* 시그널링에서 원격 후보를 받았을 때 */
void on_remote_ice(guint mline_index, const char *candidate) {
  g_signal_emit_by_name(webrtc, "add-ice-candidate", mline_index, candidate);
}

int main(int argc, char *argv[]) {
  gst_init(&argc, &argv);
  pipe = gst_parse_launch(PIPELINE_DESC, NULL);
  webrtc = gst_bin_get_by_name(GST_BIN(pipe), "webrtc");

  /* PLAYING 전에 연결해야 첫 negotiation-needed를 놓치지 않는다 */
  g_signal_connect(webrtc, "on-negotiation-needed", G_CALLBACK(on_negotiation_needed), NULL);
  g_signal_connect(webrtc, "on-ice-candidate", G_CALLBACK(on_ice_candidate), NULL);

  gst_element_set_state(pipe, GST_STATE_PLAYING);
  g_main_loop_run(g_main_loop_new(NULL, FALSE));
  return 0;
}
```

이 코드가 만드는 메시지 흐름을 시퀀스로 그리면 다음과 같다.

![webrtcbin·앱 코드(C)·시그널링 서버·브라우저 네 라이프라인 시퀀스 — webrtcbin이 on-negotiation-needed를 내면 앱이 create-offer를 호출하고 GstPromise 응답으로 offer를 받아 set-local-description 후 시그널링 서버를 거쳐 브라우저로 offer를 보내며, on-ice-candidate가 반복될 때마다 후보를 브라우저로 전달하고, 브라우저의 answer를 받아 set-remote-description, 브라우저 후보를 받아 add-ice-candidate를 호출한 뒤 webrtcbin과 브라우저 사이에 ICE 연결 확인 → DTLS 핸드셰이크 → SRTP 미디어가 흐르는 그림](/images/study-webrtc/13-webrtcbin-sequence-light.png)
![webrtcbin·앱 코드(C)·시그널링 서버·브라우저 네 라이프라인 시퀀스 — webrtcbin이 on-negotiation-needed를 내면 앱이 create-offer를 호출하고 GstPromise 응답으로 offer를 받아 set-local-description 후 시그널링 서버를 거쳐 브라우저로 offer를 보내며, on-ice-candidate가 반복될 때마다 후보를 브라우저로 전달하고, 브라우저의 answer를 받아 set-remote-description, 브라우저 후보를 받아 add-ice-candidate를 호출한 뒤 webrtcbin과 브라우저 사이에 ICE 연결 확인 → DTLS 핸드셰이크 → SRTP 미디어가 흐르는 그림](/images/study-webrtc/13-webrtcbin-sequence-dark.png)

실전에서 부딪히는 지점이다.

- <strong>콜백은 GStreamer 내부 스레드에서 불린다.</strong> `on-negotiation-needed`, `on-ice-candidate`, promise 콜백은 메인 루프가 아닌 스트리밍·작업 스레드에서 호출된다. 시그널링 전송 함수가 스레드 안전하지 않다면 `g_main_context_invoke()`로 메인 루프에 넘기거나 큐를 둔다.
- <strong>디바이스가 answerer인 경우</strong>: KVS처럼 뷰어(브라우저)가 offer를 보내는 구조(17장)라면 `on-negotiation-needed`에서 offer를 만들지 않는다. offer 수신 → `set-remote-description` → `create-answer` → `set-local-description` → answer 전송 순서로 바꾼다. webrtcbin은 offer의 m-line을 이미 링크된 sink 패드의 트랜시버와 짝지으므로, 파이프라인이 PLAYING에 들어가 패드가 링크된 뒤에 offer를 적용한다.
- <strong>대역폭 적응은 자동이 아니다.</strong> webrtcbin은 PeerConnection 프로토콜을 구현하지만, 대역폭 추정 결과를 `nvv4l2h264enc`의 `bitrate`에 반영하는 일은 애플리케이션이 해야 한다. LTE 위의 농기계라면 이 루프가 없을 때 망이 나빠지는 순간 지연이 수 초로 쌓인다.
- <strong>`webrtcsink`라는 상위 대안</strong>: gst-plugins-rs(Rust)의 `webrtcsink`는 webrtcbin 위에 시그널링 프로토콜, 인코더 선택, 혼잡 제어(대역폭 추정 → 인코더 비트레이트)를 묶어 둔 요소다. 자체 시그널링에 묶일 필요가 없다면 출발점으로 검토할 만하다. WHIP 송출용 요소는 14장에서 다룬다.

## 5. Pion 최소 예제 — H.264 트랙 송출

Pion은 캡처·인코딩을 하지 않으므로 "인코딩된 H.264를 어디선가 받아 트랙에 쓰는" 구조가 된다. 가장 단순한 형태는 GStreamer를 자식 프로세스로 띄워 stdout으로 Annex-B 바이트 스트림을 받고, Pion의 `h264reader`로 NAL 단위로 잘라 `TrackLocalStaticSample`에 쓰는 것이다. 패킷화(FU-A·STAP-A), SRTP, RTCP는 Pion이 처리한다.

```go
package main

import (
	"errors"
	"io"
	"log"
	"os/exec"
	"strings"
	"time"

	"github.com/pion/rtcp"
	"github.com/pion/webrtc/v4"
	"github.com/pion/webrtc/v4/pkg/media"
	"github.com/pion/webrtc/v4/pkg/media/h264reader"
)

// Jetson 예시. Raspberry Pi 4는 인코더 부분을 libcamerasrc / v4l2h264enc로 바꾼다
const gstPipeline = "v4l2src device=/dev/video0 ! video/x-raw,width=1280,height=720,framerate=30/1 " +
	"! nvvidconv ! video/x-raw(memory:NVMM),format=NV12 " +
	"! nvv4l2h264enc bitrate=2000000 control-rate=1 profile=0 insert-sps-pps=true idrinterval=30 iframeinterval=30 " +
	"! h264parse ! video/x-h264,stream-format=byte-stream,alignment=au ! fdsink fd=1"

const fps = 30

func main() {
	pc, err := webrtc.NewPeerConnection(webrtc.Configuration{
		ICEServers: []webrtc.ICEServer{{URLs: []string{"stun:stun.l.google.com:19302"}}},
	})
	must(err)

	track, err := webrtc.NewTrackLocalStaticSample(
		webrtc.RTPCodecCapability{
			MimeType:    webrtc.MimeTypeH264,
			ClockRate:   90000,
			SDPFmtpLine: "level-asymmetry-allowed=1;packetization-mode=1;profile-level-id=42e01f",
		},
		"video", "farm-cam-01",
	)
	must(err)

	sender, err := pc.AddTrack(track)
	must(err)
	go readRTCP(sender) // RTCP를 읽어 줘야 NACK 등 interceptor가 동작한다

	pc.OnICECandidate(func(c *webrtc.ICECandidate) {
		if c != nil {
			sendCandidate(c.ToJSON()) // trickle ICE
		}
	})
	pc.OnConnectionStateChange(func(s webrtc.PeerConnectionState) {
		log.Println("connection state:", s)
		// failed: ICE restart 또는 PeerConnection 재생성 (6절)
	})

	// 뷰어(브라우저)가 offer, 디바이스가 answer
	must(pc.SetRemoteDescription(receiveOffer()))
	answer, err := pc.CreateAnswer(nil)
	must(err)
	must(pc.SetLocalDescription(answer))
	sendAnswer(*pc.LocalDescription())

	go func() {
		for c := range receiveCandidates() {
			must(pc.AddICECandidate(c))
		}
	}()

	must(pumpCamera(track))
}

// 인코더 출력(Annex-B)을 AU 단위로 묶어 트랙에 쓴다
func pumpCamera(track *webrtc.TrackLocalStaticSample) error {
	// -q: gst-launch의 상태 메시지가 stdout(영상 스트림)에 섞이지 않게 한다
	cmd := exec.Command("gst-launch-1.0", append([]string{"-q"}, strings.Fields(gstPipeline)...)...)
	stdout, err := cmd.StdoutPipe()
	if err != nil {
		return err
	}
	if err := cmd.Start(); err != nil {
		return err
	}
	defer cmd.Process.Kill()

	reader, err := h264reader.NewReader(stdout)
	if err != nil {
		return err
	}
	frameDuration := time.Second / fps
	var au []byte
	for {
		nal, err := reader.NextNAL()
		if errors.Is(err, io.EOF) {
			return errors.New("encoder pipeline exited")
		}
		if err != nil {
			return err
		}
		au = append(au, 0x00, 0x00, 0x00, 0x01)
		au = append(au, nal.Data...)
		// 슬라이스 NAL이 오면 한 프레임이 끝난 것으로 본다 (프레임당 슬라이스 1개 가정)
		switch nal.UnitType {
		case h264reader.NalUnitTypeCodedSliceIdr, h264reader.NalUnitTypeCodedSliceNonIdr:
			if err := track.WriteSample(media.Sample{Data: au, Duration: frameDuration}); err != nil {
				return err
			}
			au = nil
		}
	}
}

func readRTCP(sender *webrtc.RTPSender) {
	for {
		pkts, _, err := sender.ReadRTCP()
		if err != nil {
			return
		}
		for _, p := range pkts {
			switch p.(type) {
			case *rtcp.PictureLossIndication, *rtcp.FullIntraRequest:
				// 키프레임 요청. 자식 프로세스 인코더에는 전달할 길이 없다 (아래 설명)
				log.Println("keyframe requested")
			}
		}
	}
}

// 시그널링은 03장의 WebSocket 서버 등으로 구현한다 (여기서는 시그니처만)
func receiveOffer() webrtc.SessionDescription           { panic("implement signaling") }
func sendAnswer(webrtc.SessionDescription)              {}
func sendCandidate(webrtc.ICECandidateInit)             {}
func receiveCandidates() <-chan webrtc.ICECandidateInit { return nil }

func must(err error) {
	if err != nil {
		log.Fatal(err)
	}
}
```

코드의 각 결정에는 이유가 있다.

- <strong>SPS/PPS + 슬라이스를 한 샘플로 묶는다.</strong> `WriteSample`은 샘플마다 `Duration`만큼 RTP 타임스탬프를 전진시키고, 샘플의 마지막 패킷에 marker 비트를 세운다. NAL마다 따로 쓰면 SPS·PPS도 "한 프레임"으로 취급돼 타임스탬프가 어긋난다. Annex-B start code를 붙여 AU 하나로 넘기면 Pion의 H.264 패킷화기가 start code로 다시 쪼개 SPS·PPS를 STAP-A로 묶어 보낸다.
- <strong>`idrinterval=30`(1초)로 짧게 잡은 이유</strong>: 연결이 붙기 전에 쓴 샘플은 버려진다. 뷰어는 연결 후 첫 IDR이 와야 화면을 그리는데, 이 구조에서는 PLI를 받아도 인코더에 IDR을 요청할 수 없으므로 주기적 IDR이 유일한 복구 수단이다. 대신 IDR이 잦을수록 같은 비트레이트에서 화질이 떨어진다.
- <strong>그래서 실서비스에서는 인코더를 프로세스 안으로 들인다.</strong> go-gst 같은 GStreamer 바인딩이나 cgo로 `appsink`에서 직접 프레임을 받으면, PLI를 받았을 때 업스트림으로 force-key-unit 이벤트를 보낼 수 있고 대역폭 추정값으로 인코더 `bitrate`도 바꿀 수 있다. V4L2 인코더를 직접 다룬다면 `V4L2_CID_MPEG_VIDEO_FORCE_KEY_FRAME` 컨트롤로 키프레임을 강제한다.
- <strong>크로스컴파일이 한 줄이다.</strong> Pion은 cgo 없이 순수 Go로 작성돼 있어 x86 개발 PC에서 바로 ARM 바이너리를 만든다(인코더 프로세스 연동만 하고 cgo를 쓰지 않는 한).

```bash
GOOS=linux GOARCH=arm64 CGO_ENABLED=0 go build -trimpath -ldflags="-s -w" -o cam-agent .
scp cam-agent jetson:/usr/local/bin/
```

## 6. 임베디드 제약 체크리스트

데스크톱에서 잘 돌던 코드가 현장 장비에서 무너지는 이유는 대부분 아래 표에 있다.

| 항목 | 왜 문제인가 | 점검·대응 |
|---|---|---|
| <strong>CPU</strong> | SW 인코딩·색 변환은 ARM 코어를 금방 포화시킨다. SRTP 암호화도 공짜가 아니고, P2P면 뷰어 수만큼 암호화 세션이 늘어난다(12장) | HW 인코더 필수, 변환도 HW(`nvvidconv`). `/proc/cpuinfo`의 `Features`에 `aes`가 있는지 확인(ARMv8 Crypto Extensions — Raspberry Pi 4의 BCM2711에는 없어 AES가 소프트웨어로 돈다). 뷰어 수 상한 또는 SFU 오프로드. `tegrastats`·`top`으로 부하 상태에서 측정 |
| <strong>메모리</strong> | PeerConnection마다 NACK 재전송 버퍼·지터 버퍼·SCTP 버퍼가 붙는다. Go는 GC 여유분까지 필요하다. OOM killer가 에이전트를 죽이면 영상이 끊긴다 | 뷰어 수 상한, systemd `MemoryMax=`, Go는 `GOMEMLIMIT`로 GC를 상한에 맞춤. 장시간 소크 테스트로 누수 확인 |
| <strong>열</strong> | 여름철 밀폐 함체 안의 보드는 스로틀링으로 인코더 프레임레이트가 떨어진다 | 온도·클럭을 텔레메트리로 수집(Jetson `tegrastats`). 방열 설계, 고온 시 해상도·프레임레이트 단계적 하향 |
| <strong>크로스컴파일</strong> | 개발 PC(x86)와 디바이스(arm64)가 다르다 | Go(Pion): `GOOS/GOARCH` + `CGO_ENABLED=0`. KVS C SDK: `CC`/`CXX`와 `BUILD_OPENSSL_PLATFORM`·`BUILD_LIBSRTP_HOST_PLATFORM`·`BUILD_LIBSRTP_DESTINATION_PLATFORM` 지정(19장). GStreamer: 보드 BSP(JetPack, Raspberry Pi OS) 패키지를 쓰거나 Yocto/Buildroot 이미지에 포함. libwebrtc: sysroot와 gn 인자(`target_cpu="arm64"`)로 빌드 — 가장 어렵다 |
| <strong>시계 동기(NTP)</strong> | RTC 배터리가 없는 보드는 부팅 직후 1970년이나 마지막 저장 시각으로 시작한다. 그러면 WSS 시그널링의 TLS 인증서 검증(`notBefore`)이 실패하고, KVS의 SigV4 서명은 시각 오차로 거부되며(22장), TURN 시간제한 자격증명(07장)도 만료로 판정된다 | chrony/systemd-timesyncd + 에이전트 유닛에 `After=time-sync.target`(`systemd-time-wait-sync.service` 활성화). 농기계는 GNSS 수신기가 있으므로 gpsd + chrony로 GPS 시각을 시간원으로 추가하면 셀룰러가 안 되는 현장에서도 시계를 맞출 수 있다 |
| <strong>인증서·키 저장</strong> | 디바이스 신원 키(IoT X.509 등)가 유출되면 장비 사칭이 가능하다. DTLS 인증서는 세션마다 만들 수 있지만 생성 비용이 있다 | 신원 키는 TPM·보안 요소(secure element)에 두거나 최소한 파일 권한 0600 + 전용 사용자. DTLS용은 RSA보다 생성이 빠른 ECDSA P-256(Pion은 `Configuration.Certificates`를 비우면 ECDSA 인증서를 생성). 인증서 회전 절차를 OTA와 함께 설계(IoT 인증서는 [AWS IoT Core 포스트](/posts/tech/2025-06-27-iot) 참고) |
| <strong>watchdog 재시작</strong> | 무인 장비는 크래시보다 "살아 있지만 영상이 안 나가는" 행(hang)이 더 위험하다 | systemd `Restart=always` + `WatchdogSec=`로 헬스 신호가 끊기면 재시작. 헬스 신호는 프로세스 생존이 아니라 <strong>프레임이 실제로 흐를 때만</strong> 보낸다. 보드 하드웨어 watchdog(`/etc/systemd/system.conf`의 `RuntimeWatchdogSec=`)으로 커널 행까지 대비 |
| <strong>연결 복구</strong> | LTE 셀 변경·IP 변경으로 ICE가 끊긴다. 카메라 USB가 진동으로 순간 분리되기도 한다 | `disconnected` 유예 후 ICE restart, `failed`면 PeerConnection 재생성(06장). 시그널링 지수 백오프 재연결. GStreamer 버스 `ERROR`/`EOS` 감지 시 파이프라인 재구성 |
| <strong>네트워크</strong> | CGNAT 뒤 LTE는 직접 연결이 잘 안 된다. VPN·LTE 구간은 MTU가 작다 | TURN(UDP·TCP·TLS 443) 준비(05·07장). 패킷 크기를 1200바이트 안팎으로 유지하는 스택 기본값을 바꾸지 않는다 |
| <strong>원격 진단</strong> | 현장 장비에는 `chrome://webrtc-internals`가 없다 | 스택의 통계 API(Pion `pc.GetStats()`, webrtcbin `get-stats`)를 주기적으로 수집해 서버로 전송. 로그 레벨을 원격으로 바꿀 수 있게(15장) |

watchdog은 systemd 유닛과 애플리케이션 헬스 신호를 함께 설계한다.

```ini
# /etc/systemd/system/cam-agent.service
[Unit]
Description=Farm camera WebRTC agent
Wants=network-online.target time-sync.target
After=network-online.target time-sync.target

[Service]
Type=notify
ExecStart=/usr/local/bin/cam-agent
Restart=always
RestartSec=3
WatchdogSec=30
MemoryMax=512M
Environment=GOMEMLIMIT=400MiB
User=camagent

[Install]
WantedBy=multi-user.target
```

```go
import (
	"time"

	"github.com/coreos/go-systemd/v22/daemon"
)

// 준비 완료 알림 후, 최근 프레임이 실제로 나갈 때만 watchdog을 갱신한다
func superviseHealth(lastFrameAt func() time.Time) {
	daemon.SdNotify(false, daemon.SdNotifyReady)
	ticker := time.NewTicker(10 * time.Second) // WatchdogSec(30s)의 1/3
	defer ticker.Stop()
	for range ticker.C {
		if time.Since(lastFrameAt()) < 15*time.Second {
			daemon.SdNotify(false, daemon.SdNotifyWatchdog)
		}
		// 프레임이 멈추면 신호를 끊는다 → systemd가 30초 후 재시작
	}
}
```

`lastFrameAt`은 5절의 `pumpCamera`에서 `WriteSample`이 성공할 때마다 갱신하는 타임스탬프다. 인코더 프로세스가 멈추든, 카메라가 빠지든, 고루틴이 교착되든 "프레임이 안 나간다"는 하나의 증상으로 감지해 재시작한다. 같은 원리로 시그널링 연결 끊김이 일정 시간 이상 지속될 때도 신호를 끊을지 정책을 정해 둔다.

::: tip 핵심 정리
- 디바이스 WebRTC는 브라우저가 숨겨 주던 캡처·인코딩·키프레임 요청 처리·비트레이트 적응·무인 복구를 직접 조립하는 일이다.
- 미디어까지 해 주는 스택(libwebrtc, GStreamer webrtcbin)과 프로토콜만 해 주는 스택(Pion, libdatachannel)이 있고, AWS 기반이면 KVS C SDK(19장)가 시그널링·TURN까지 묶어 준다. 실무에서는 "HW 인코딩은 GStreamer, 프로토콜은 다른 스택" 조합이 흔하다.
- 파이프라인은 V4L2/CSI 캡처 → HW 변환 → HW 인코더(Jetson `nvv4l2h264enc`, Pi 4 `v4l2h264enc`) → `h264parse` → RTP 패킷화 → WebRTC. Raspberry Pi 5와 Jetson Orin Nano에는 HW H.264 인코더가 없다.
- 인코더는 Baseline·B-프레임 없음·IDR마다 SPS/PPS·CBR이 기본이고, PLI → 즉시 IDR, 대역폭 추정 → 비트레이트 루프를 반드시 연결한다.
- webrtcbin은 `on-negotiation-needed`·`on-ice-candidate` 시그널과 `create-offer`·`set-*-description`·`add-ice-candidate` 액션 시그널로 JSEP를 구현하며, 콜백이 내부 스레드에서 불린다는 점에 주의한다.
- Pion은 `TrackLocalStaticSample`에 AU 단위로 `WriteSample`하면 패킷화를 맡아 주고, 순수 Go라 크로스컴파일이 쉽다. 자식 프로세스 인코더는 키프레임 요청을 받을 수 없으므로 실서비스에서는 인코더를 프로세스 안으로 들인다.
- 현장 배포는 CPU(AES 가속 여부)·메모리 상한·열·크로스컴파일·NTP/GNSS 시계·키 저장·프레임 기반 watchdog까지 체크리스트로 관리한다.
:::

## 다음 챕터

[WHIP/WHEP와 스트리밍](/study/webrtc/14-whip-whep)에서는 시그널링을 HTTP 요청 하나로 표준화한 WHIP(퍼블리시)와 WHEP(시청)를 다룬다. POST SDP → 201 Location → PATCH trickle → DELETE 흐름, OBS·GStreamer의 WHIP 송출, 기존 RTMP/HLS 파이프라인과의 관계, 1:N 방송 설계를 살펴본다.
