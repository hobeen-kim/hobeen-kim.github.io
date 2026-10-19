---
title: "참고 자료"
description: "WebRTC 스터디에서 인용한 W3C·IETF 표준과 RFC, AWS KVS·Chime SDK·IVS·IoT 공식 문서, SDK 저장소, 디버깅 도구를 카테고리별로 모은 링크 모음."
date: 2026-10-19
tags: [WebRTC, References]
prev: /study/webrtc/appendix-glossary
next: false
---

# 참고 자료

스터디를 마친 뒤 더 깊이 파고들 수 있는 표준 문서와 공식 문서를 카테고리별로 모았다. 1차 출처는 언제나 표준 원문과 AWS 공식 문서이므로 그것부터 둔다. 본문에서 인용한 링크와 본문 작성에 쓴 사실 확인 자료의 링크만 실었다.

## W3C 표준

- [WebRTC 1.0 (W3C)](https://www.w3.org/TR/webrtc/) — RTCPeerConnection·RTCDataChannel 등 브라우저 API 명세. 현행 Recommendation이다.
- [WebRTC 표준 이력 (W3C)](https://www.w3.org/standards/history/webrtc/) — Recommendation 발행·재발행 이력

## IETF 표준과 RFC

연결 수립, 미디어, 보안, 데이터 채널, 기타 순서로 정리했다. 괄호의 장 링크는 본문에서 해당 RFC를 다룬 곳이다.

### 개요와 연결 수립

- [RFC 8825 - WebRTC Overview](https://www.rfc-editor.org/rfc/rfc8825) — WebRTC 프로토콜 묶음(RFC 8825~8835)의 개요
- [RFC 9429 - JSEP](https://www.rfc-editor.org/rfc/rfc9429) — Offer/Answer 기반 세션 수립 모델. 기존 RFC 8829를 대체한다.
- [RFC 8866 - SDP: Session Description Protocol](https://www.rfc-editor.org/rfc/rfc8866) — 세션 기술 형식인 SDP의 문법과 필드 ([04장장](/study/webrtc/04-sdp-jsep))
- [RFC 9143 - Negotiating Media Multiplexing Using the Session Description Protocol (SDP)](https://www.rfc-editor.org/rfc/rfc9143) — BUNDLE로 여러 미디어를 하나의 전송에 다중화하는 협상 ([04장장](/study/webrtc/04-sdp-jsep))
- [RFC 4787 - Network Address Translation (NAT) Behavioral Requirements for Unicast UDP](https://www.rfc-editor.org/rfc/rfc4787) — NAT 매핑·필터링 동작 분류 ([05장장](/study/webrtc/05-nat-stun))
- [RFC 8489 - STUN](https://www.rfc-editor.org/rfc/rfc8489) — Binding 요청과 XOR-MAPPED-ADDRESS
- [RFC 8656 - TURN](https://www.rfc-editor.org/rfc/rfc8656) — 릴레이 할당·퍼미션·채널 바인딩
- [RFC 8445 - ICE](https://www.rfc-editor.org/rfc/rfc8445) — 후보 수집·우선순위·연결 확인 절차
- [RFC 8838 - Trickle ICE](https://www.rfc-editor.org/rfc/rfc8838) — 후보를 점진적으로 교환하는 방식
- [RFC 7675 - Session Traversal Utilities for NAT (STUN) Usage for Consent Freshness](https://www.rfc-editor.org/rfc/rfc7675) — 연결 후 주기적으로 송신 동의를 확인하는 Consent Freshness ([06장장](/study/webrtc/06-ice))
- [RFC 9725 - WHIP](https://www.rfc-editor.org/rfc/rfc9725) — HTTP 기반 WebRTC 인제스트 프로토콜
- [draft-ietf-wish-whep](https://datatracker.ietf.org/doc/draft-ietf-wish-whep/) — WHEP 드래프트. 작성 시점 기준 아직 draft 단계다.

### 미디어

- [RFC 3550 - RTP: A Transport Protocol for Real-Time Applications](https://www.rfc-editor.org/rfc/rfc3550) — RTP·RTCP의 기본 정의 ([08장장](/study/webrtc/08-rtp-codecs))
- [RFC 4585 - Extended RTP Profile for Real-time Transport Control Protocol (RTCP)-Based Feedback (RTP/AVPF)](https://www.rfc-editor.org/rfc/rfc4585) — NACK·PLI 같은 RTCP 피드백 메시지 ([09장장](/study/webrtc/09-quality-latency))
- [RFC 8888 - RTP Control Protocol (RTCP) Feedback for Congestion Control](https://www.rfc-editor.org/rfc/rfc8888) — 혼잡 제어용 RTCP 피드백 형식 ([09장장](/study/webrtc/09-quality-latency))
- [RFC 6184 - RTP Payload Format for H.264 Video](https://www.rfc-editor.org/rfc/rfc6184) — H.264 영상의 RTP 패킷화 방식 ([08장장](/study/webrtc/08-rtp-codecs))
- [RFC 7742 - WebRTC Video Processing and Codec Requirements](https://www.rfc-editor.org/rfc/rfc7742) — WebRTC 필수 비디오 코덱 요구 사항 ([08장장](/study/webrtc/08-rtp-codecs))
- [RFC 7874 - WebRTC Audio Codec and Processing Requirements](https://www.rfc-editor.org/rfc/rfc7874) — WebRTC 필수 오디오 코덱 요구 사항 ([08장장](/study/webrtc/08-rtp-codecs))
- [draft-holmer-rmcat-transport-wide-cc-extensions-01](http://www.ietf.org/id/draft-holmer-rmcat-transport-wide-cc-extensions-01) — transport-wide-cc RTP 헤더 확장(TWCC) 드래프트

### 보안

- [RFC 8827 - WebRTC Security Architecture](https://www.rfc-editor.org/rfc/rfc8827) — WebRTC 보안 모델과 위협 분석 ([10장장](/study/webrtc/10-dtls-srtp))
- [RFC 3711 - The Secure Real-time Transport Protocol (SRTP)](https://www.rfc-editor.org/rfc/rfc3711) — RTP 미디어 암호화·인증 ([10장장](/study/webrtc/10-dtls-srtp))
- [RFC 5764 - Datagram Transport Layer Security (DTLS) Extension to Establish Keys for the Secure Real-time Transport Protocol (SRTP)](https://www.rfc-editor.org/rfc/rfc5764) — DTLS 핸드셰이크로 SRTP 키를 교환하는 DTLS-SRTP ([10장장](/study/webrtc/10-dtls-srtp))
- [RFC 7983 - Multiplexing Scheme Updates for Secure Real-time Transport Protocol (SRTP) Extension for Datagram Transport Layer Security (DTLS)](https://www.rfc-editor.org/rfc/rfc7983) — 한 포트에서 STUN·DTLS·SRTP를 구분하는 다중화 규칙 ([10장장](/study/webrtc/10-dtls-srtp))
- [RFC 9605 - Secure Frame (SFrame): Lightweight Authenticated Encryption for Real-Time Media](https://www.rfc-editor.org/rfc/rfc9605) — SFU 구간에서도 유지되는 프레임 단위 종단간 암호화 ([12장장](/study/webrtc/12-topology-sfu))

### 데이터 채널

- [RFC 8831 - WebRTC Data Channels](https://www.rfc-editor.org/rfc/rfc8831) — 데이터 채널 전송 모델 ([11장장](/study/webrtc/11-datachannel))
- [RFC 8832 - WebRTC Data Channel Establishment Protocol](https://www.rfc-editor.org/rfc/rfc8832) — DCEP로 채널을 여는 절차 ([11장장](/study/webrtc/11-datachannel))
- [RFC 8261 - Datagram Transport Layer Security (DTLS) Encapsulation of SCTP Packets](https://www.rfc-editor.org/rfc/rfc8261) — DTLS 위에 SCTP를 싣는 방식 ([11장장](/study/webrtc/11-datachannel))

## webrtc.org RTP 헤더 확장

본문 SDP 예제의 `a=extmap` 줄에 등장하는 URI이다. 문서로 열리는 URL이 아니라 확장 식별자이므로, 의미는 본문 [04장](/study/webrtc/04-sdp-jsep)과 [08장](/study/webrtc/08-rtp-codecs)에서 확인한다.

- `http://www.webrtc.org/experiments/rtp-hdrext/abs-send-time` — 절대 송신 시각
- `http://www.webrtc.org/experiments/rtp-hdrext/playout-delay` — 재생 지연 힌트
- `http://www.webrtc.org/experiments/rtp-hdrext/video-content-type` — 비디오 콘텐츠 유형
- `http://www.webrtc.org/experiments/rtp-hdrext/video-timing` — 프레임 단계별 타이밍
- `http://www.webrtc.org/experiments/rtp-hdrext/color-space` — 색 공간 정보

## 브라우저 API·명세 자료

- [WebRTC API (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API) — 브라우저 WebRTC API 전반의 개요와 가이드
- [Perfect negotiation 패턴 (MDN)](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API/Perfect_negotiation) — Offer 충돌(glare)을 처리하는 협상 패턴
- [Identifiers for WebRTC's Statistics API (W3C)](https://www.w3.org/TR/webrtc-stats/) — getStats() 통계 식별자 명세
- [webrtc.org](https://webrtc.org/) — 구글 주도 WebRTC 프로젝트 공식 사이트
- [WebRTC samples](https://webrtc.github.io/samples/) — 브라우저 API별 동작 예제 모음

## 오픈소스 구현

- [coturn](https://github.com/coturn/coturn) — 오픈소스 TURN/STUN 서버
- [pion/webrtc](https://github.com/pion/webrtc) — Go로 구현한 WebRTC
- [aiortc](https://github.com/aiortc/aiortc) — Python asyncio 기반 WebRTC·ORTC 구현
- [mediasoup](https://mediasoup.org/) — Node.js·Rust 기반 SFU 라이브러리
- [Janus WebRTC Server](https://janus.conf.meetecho.com/) — 플러그인 구조의 범용 WebRTC 서버
- [LiveKit](https://github.com/livekit/livekit) — 오픈소스 실시간 미디어 스택(SFU)
- [GStreamer webrtcbin](https://gstreamer.freedesktop.org/documentation/webrtc/index.html) — GStreamer의 WebRTC 엘리먼트

## 오픈소스 SDK 저장소

- [amazon-kinesis-video-streams-webrtc-sdk-c](https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-c/blob/main/README.md) — 디바이스용 KVS WebRTC C SDK ([19장](/study/webrtc/19-kvs-c-sdk))
- [amazon-kinesis-video-streams-webrtc-sdk-js](https://github.com/awslabs/amazon-kinesis-video-streams-webrtc-sdk-js/blob/master/README.md) — 브라우저 뷰어용 JS SDK ([20장](/study/webrtc/20-kvs-viewer-backend))

## 도구·디버깅

- [webrtc-dump-importer](https://fippo.github.io/webrtc-dump-importer/) — chrome://webrtc-internals 덤프를 그래프로 보는 도구 ([15장](/study/webrtc/15-monitoring-debugging))

## AWS KVS WebRTC

- [KVS WebRTC 동작 방식](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-how-it-works.html) — 시그널링 채널과 Master/Viewer 모델 개요
- [요구 사항](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-requirements.html) — 시스템 요구 사항
- [서비스 한도](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-limits.html) — 채널당 뷰어 수 등 할당량
- [가용 리전](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/availability.html) — 리전별 지원 현황
- [CloudWatch 모니터링](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-monitoring-cw.html) — 메트릭 목록
- [API 엔드포인트](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/api-endpoint.html) — WebSocket 시그널링 엔드포인트 API
- [ConnectAsMaster](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/ConnectAsMaster.html) — Master 접속용 WSS API
- [SendSdpOffer](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/SendSdpOffer.html) — SDP Offer 전송 메시지
- [SendSdpAnswer](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/SendSdpAnswer.html) — SDP Answer 전송 메시지
- [Disconnect](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/Disconnect.html) — 연결 종료
- [WebSocket 메시지 수신 API](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/async-message-reception-api.html) — 비동기 수신 메시지 형식
- [ConnectAsViewer](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-websocket-apis3.html) — Viewer 접속용 WSS API
- [SendIceCandidate](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/kvswebrtc-websocket-apis5.html) — ICE 후보 전송 메시지
- [CreateSignalingChannel](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_CreateSignalingChannel.html) — 시그널링 채널 생성
- [UpdateSignalingChannel](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_UpdateSignalingChannel.html) — 채널 설정 갱신
- [ChannelInfo](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_ChannelInfo.html) — 채널 정보 구조
- [SingleMasterConfiguration](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_SingleMasterConfiguration.html) — 메시지 TTL 설정
- [GetSignalingChannelEndpoint](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_GetSignalingChannelEndpoint.html) — 프로토콜별 엔드포인트 조회
- [GetIceServerConfig](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_signaling_GetIceServerConfig.html) — 관리형 TURN 자격증명 발급
- [IceServer](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_signaling_IceServer.html) — ICE 서버 응답 구조
- [AWS CLI get-ice-server-config](https://docs.aws.amazon.com/cli/latest/reference/kinesis-video-signaling/get-ice-server-config.html) — CLI 레퍼런스
- [KVS 서비스 엔드포인트·할당량](https://docs.aws.amazon.com/general/latest/gr/akv.html) — 리전별 엔드포인트와 한도
- [KVS Video Streams 요금](https://aws.amazon.com/kinesis/video-streams/pricing/) — WebRTC·스트림 과금 항목

## AWS KVS WebRTC 인제스트와 저장

- [WebRTC 인제스트 개요](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/webrtc-ingestion.html) — 시그널링 채널과 Video Stream 연동
- [인제스트 시작하기](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/getting-started-ingestion.html) — 인제스트·저장 기능 소개
- [인제스트 미디어 시청](https://docs.aws.amazon.com/kinesisvideostreams-webrtc-dg/latest/devguide/ingestion-view-media.html) — 저장된 미디어 재생
- [UpdateMediaStorageConfiguration](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_UpdateMediaStorageConfiguration.html) — 채널과 스트림 연결
- [JoinStorageSession](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_webrtc_JoinStorageSession.html) — 마스터 저장 세션 참여
- [JoinStorageSessionAsViewer](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/API_webrtc_JoinStorageSessionAsViewer.html) — 뷰어 저장 세션 참여

## AWS IoT

- [AWS IoT 자격증명 직접 접근 인가](https://docs.aws.amazon.com/iot/latest/developerguide/authorizing-direct-aws.html) — Credential Provider와 role alias
- [KVS와 IoT 연동](https://docs.aws.amazon.com/kinesisvideostreams/latest/dg/how-iot.html) — 디바이스 인증서로 KVS 접근

## Amazon Chime SDK

- [Chime SDK 제품 페이지](https://aws.amazon.com/chime/chime-sdk/) — 서비스 개요
- [Chime SDK 기능](https://aws.amazon.com/chime/chime-sdk/features/) — 기능 목록
- [Chime SDK 요금](https://aws.amazon.com/chime/chime-sdk/pricing/) — 과금 모델
- [Chime 지원 변경 공지](https://aws.amazon.com/blogs/messaging-and-targeting/update-on-support-for-amazon-chime/) — Amazon Chime 앱 종료와 Chime SDK 유지
- [Chime SDK 리전](https://docs.aws.amazon.com/chime-sdk/latest/dg/chime-sdk-meetings-regions.html) — 미팅 리전
- [미팅 만들기](https://docs.aws.amazon.com/chime-sdk/latest/dg/create-mtgs.html) — 서버 측 미팅 생성 절차
- [Meetings SDK](https://docs.aws.amazon.com/chime-sdk/latest/dg/meetings-sdk.html) — 클라이언트 SDK 개요
- [클라이언트 라이브러리](https://docs.aws.amazon.com/chime-sdk/latest/dg/mtgs-sdk-client-lib.html) — 플랫폼별 SDK
- [Media Pipelines](https://docs.aws.amazon.com/chime-sdk/latest/dg/media-pipelines.html) — 녹화·라이브 커넥터 등 미디어 파이프라인
- [서비스 엔드포인트·할당량](https://docs.aws.amazon.com/general/latest/gr/chime-sdk.html) — 한도 확인
- [CreateMeeting](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_CreateMeeting.html) — 미팅 생성 API
- [CreateAttendee](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_CreateAttendee.html) — 참가자 생성 API
- [CreateMeetingWithAttendees](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_CreateMeetingWithAttendees.html) — 미팅과 참가자 동시 생성
- [Attendee](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_Attendee.html) — 참가자 데이터 구조
- [AttendeeFeatures](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_AttendeeFeatures.html) — 참가자별 기능 제한
- [VideoFeatures](https://docs.aws.amazon.com/chime-sdk/latest/APIReference/API_meeting-chime_VideoFeatures.html) — 비디오 해상도 제한
- [SIP 미디어 애플리케이션 가용성 변경](https://docs.aws.amazon.com/chime-sdk/latest/ag/sip-applications-service-change.html) — Chime SDK SIP 미디어 애플리케이션의 제공 범위 변경 안내

## Amazon IVS Real-Time Streaming

- [IVS Real-Time란?](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/what-is.html) — Stage 기반 서비스 개요
- [IVS 기능](https://aws.amazon.com/ivs/features/) — 기능 목록
- [IVS 요금](https://aws.amazon.com/ivs/pricing/) — 과금 모델
- [서비스 할당량](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/service-quotas.html) — 한도
- [IVS 엔드포인트·할당량](https://docs.aws.amazon.com/general/latest/gr/ivs.html) — 리전별 정보
- [웹 퍼블리시·구독](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/web-publish-subscribe.html) — 브라우저 SDK 사용법
- [브로드캐스트 SDK](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/broadcast.html) — 모바일 퍼블리시
- [스트림 인제스트](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/rt-stream-ingest.html) — WHIP/RTMP 인제스트
- [OBS WHIP 지원](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/obs-whip-support.html) — OBS에서 Stage로 퍼블리시
- [CreateParticipantToken](https://docs.aws.amazon.com/ivs/latest/RealTimeAPIReference/API_CreateParticipantToken.html) — 참가자 토큰 발급 API
- [서버 측 합성](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/server-side-composition.html) — Composition 개요
- [서버 측 합성 상세](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/ssc-overview.html) — 구성 요소 설명
- [참가자 개별 녹화](https://docs.aws.amazon.com/ivs/latest/RealTimeUserGuide/rt-individual-participant-recording.html) — 녹화 방식

## 가격 데이터

- [Amazon Kinesis Video 가격 JSON (ap-northeast-2)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonKinesisVideo/current/ap-northeast-2/index.json) — 서울 리전 단가 원본
- [Amazon Kinesis Video 가격 JSON (us-east-1)](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonKinesisVideo/current/us-east-1/index.json) — 버지니아 리전 단가 원본
- [Amazon Chime 가격 JSON](https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonChimeServices/current/index.json) — Chime SDK 단가 원본

## 블로그 내부 관련 글

- [WebSocket 과 SSE](/posts/tech/2025-07-20-ssewebsocket) — 시그널링 전송 수단 비교
- [AWS IoT Core 완전 정복 - Shadow, 인증, Job까지](/posts/tech/2025-06-27-iot) — IoT 인증서와 자격증명
- [MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt) — 제어 채널 비교
