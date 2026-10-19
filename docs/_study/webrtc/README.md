---
title: "WebRTC와 AWS 관리형 WebRTC"
description: "WebRTC의 원리(시그널링·SDP·ICE·TURN·RTP·DTLS-SRTP·DataChannel)에서 출발해 KVS WebRTC, Amazon Chime SDK, IVS Real-Time까지 디바이스 원격 영상·제어 관점으로 정리한 스터디."
date: 2026-10-19
tags: [WebRTC, ICE, STUN, TURN, SFU, AWS, Kinesis Video Streams, Chime SDK, IVS]
---

# WebRTC와 AWS 관리형 WebRTC

<strong>WebRTC(Web Real-Time Communication)</strong>는 브라우저와 네이티브 앱이 플러그인 없이 서로 실시간으로 영상·음성·임의 데이터를 주고받게 하는 표준 기술이다. W3C가 JavaScript API를, IETF가 ICE·SRTP·DTLS·SCTP 같은 프로토콜 스택을 정의한다. 핵심은 가능하면 두 피어가 서버를 거치지 않고 직접 UDP로 연결해 지연을 수백 ms 이하로 낮추는 데 있다.

이 스터디는 카메라가 달린 디바이스(농기계·로봇)의 영상을 운영자 브라우저로 보고 원격으로 제어하는 시나리오를 기준으로 삼는다. 원리 → 프로토콜 → 아키텍처 → AWS 관리형 서비스 순서로 이어지며, 마지막 캡스톤에서 전체를 하나의 플랫폼 설계로 묶는다. 대상은 TCP/UDP/HTTP/WebSocket 기초가 있는 백엔드 개발자다. 개념 나열보다 "왜 그런가 · 트레이드오프 · 운영 함정 · 실전 코드와 설정"에 무게를 둔다.

이 스터디에서 배우는 것:

- <strong>WebRTC 기초</strong>: 기존 스트리밍과 비교한 WebRTC의 위치, 핵심 API, 시그널링 서버 설계
- <strong>연결 수립</strong>: SDP와 Offer/Answer, NAT의 동작, STUN, ICE 후보 쌍, TURN 릴레이
- <strong>미디어와 데이터 전송</strong>: RTP/RTCP와 코덱, 혼잡 제어와 지연 예산, DTLS-SRTP 보안, DataChannel
- <strong>아키텍처와 운영</strong>: Mesh·SFU·MCU 토폴로지, 브라우저 밖 디바이스 구현, WHIP/WHEP, getStats 기반 디버깅
- <strong>AWS KVS WebRTC</strong>: 시그널링 채널 구조와 API, 디바이스 C SDK, 뷰어·백엔드, 인제스트와 저장, 운영·보안·비용
- <strong>Chime SDK·IVS</strong>: SFU 기반 관리형 서비스의 모델과 한계, 디바이스 영상 플랫폼 적합성
- <strong>캡스톤</strong>: 농기계 원격 영상·제어 플랫폼의 전체 설계

## 전체 구조

두 피어가 시그널링 서버로 SDP와 ICE 후보를 교환하고, STUN/TURN의 도움으로 연결 경로를 찾는다. 경로가 확정되면 미디어는 SRTP, 데이터는 SCTP로 DTLS 위에서 암호화되어 직접 흐른다. 직접 연결이 불가능하면 TURN 릴레이가 대신 중계한다.

![WebRTC 구조 개관 — 브라우저 피어와 디바이스 피어가 각각 미디어(SRTP)·DataChannel(SCTP)·DTLS·ICE·UDP 층을 쌓고, 시그널링 서버로 SDP와 ICE 후보를 교환하며, STUN/TURN 서버로 주소를 발견하고, 두 피어 사이 P2P 경로로 미디어와 데이터를 직접 주고받되 실패 시 릴레이를 거치는 구조](/images/study-webrtc/readme-overview-light.png)
![WebRTC 구조 개관 — 브라우저 피어와 디바이스 피어가 각각 미디어(SRTP)·DataChannel(SCTP)·DTLS·ICE·UDP 층을 쌓고, 시그널링 서버로 SDP와 ICE 후보를 교환하며, STUN/TURN 서버로 주소를 발견하고, 두 피어 사이 P2P 경로로 미디어와 데이터를 직접 주고받되 실패 시 릴레이를 거치는 구조](/images/study-webrtc/readme-overview-dark.png)

## 학습 로드맵

![학습 로드맵 — S1 WebRTC 기초(01~03) → S2 연결 수립(04~07) → S3 미디어와 데이터 전송(08~11) → S4 아키텍처와 운영(12~15) → S5 AWS 개관과 KVS 기초(16~18) → S6 KVS 구현과 운영(19~22) → S7 Chime SDK·IVS(23~24) → S8 캡스톤(25) 순서로 이어지는 체인](/images/study-webrtc/readme-roadmap-light.png)
![학습 로드맵 — S1 WebRTC 기초(01~03) → S2 연결 수립(04~07) → S3 미디어와 데이터 전송(08~11) → S4 아키텍처와 운영(12~15) → S5 AWS 개관과 KVS 기초(16~18) → S6 KVS 구현과 운영(19~22) → S7 Chime SDK·IVS(23~24) → S8 캡스톤(25) 순서로 이어지는 체인](/images/study-webrtc/readme-roadmap-dark.png)

## 전체 목차

### WebRTC 기초 (01~03)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 01 | [왜 WebRTC인가](/study/webrtc/01-why-webrtc) | 실시간 미디어 요구와 HLS·RTMP·WebSocket 대비 지연, 표준화 역사 |
| 02 | [WebRTC API 한눈에](/study/webrtc/02-webrtc-api) | getUserMedia, RTCPeerConnection 생명주기, loopback 예제 |
| 03 | [시그널링](/study/webrtc/03-signaling) | 표준이 없는 이유, WebSocket 시그널링 서버 설계와 보안 |

### 연결 수립 — SDP·NAT·ICE·TURN (04~07)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 04 | [SDP와 Offer/Answer(JSEP)](/study/webrtc/04-sdp-jsep) | SDP 읽기, 코덱 협상, Perfect Negotiation |
| 05 | [NAT와 STUN](/study/webrtc/05-nat-stun) | NAT 매핑·필터링, STUN, UDP 홀펀칭, CGNAT |
| 06 | [ICE](/study/webrtc/06-ice) | 후보 종류와 우선순위, 후보 쌍 검사, Trickle ICE, ICE restart |
| 07 | [TURN](/study/webrtc/07-turn) | 릴레이 동작, 시간제한 credential, coturn 배치와 비용 |

### 미디어와 데이터 전송 (08~11)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 08 | [RTP/RTCP와 코덱](/study/webrtc/08-rtp-codecs) | RTP 헤더, RTCP 피드백, 비디오·오디오 코덱, 패킷화 |
| 09 | [품질 제어와 지연 예산](/study/webrtc/09-quality-latency) | 손실 복구, 혼잡 제어, glass-to-glass 지연 분해 |
| 10 | [보안: DTLS-SRTP](/study/webrtc/10-dtls-srtp) | DTLS 핸드셰이크, fingerprint 검증, 신뢰 모델 |
| 11 | [DataChannel](/study/webrtc/11-datachannel) | SCTP 옵션 조합, 흐름 제어, 원격 제어 명령 채널 설계 |

### 아키텍처와 운영 (12~15)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 12 | [토폴로지: Mesh·SFU·MCU](/study/webrtc/12-topology-sfu) | 토폴로지 비교, Simulcast·SVC, 오픈소스 SFU, E2EE |
| 13 | [브라우저 밖 WebRTC: 디바이스 구현](/study/webrtc/13-native-webrtc) | libwebrtc·Pion·GStreamer, 하드웨어 인코더, 임베디드 제약 |
| 14 | [WHIP/WHEP와 스트리밍](/study/webrtc/14-whip-whep) | HTTP 기반 표준 시그널링과 1:N 방송 설계 |
| 15 | [모니터링과 디버깅](/study/webrtc/15-monitoring-debugging) | getStats 핵심 지표, webrtc-internals, 장애 체크리스트 |

### AWS 관리형 WebRTC — 개관과 KVS (16~22)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 16 | [AWS 관리형 WebRTC 서비스 지도](/study/webrtc/16-aws-landscape) | KVS·Chime SDK·IVS 비교와 선택 기준 |
| 17 | [KVS WebRTC 아키텍처](/study/webrtc/17-kvs-architecture) | 시그널링 채널, Master/Viewer, 관리형 STUN/TURN, 할당량 |
| 18 | [KVS 시그널링 API 상세](/study/webrtc/18-kvs-signaling-api) | 엔드포인트·ICE 설정 조회, SigV4 WSS, 메시지 포맷 |
| 19 | [디바이스 측 구현: KVS C SDK](/study/webrtc/19-kvs-c-sdk) | C SDK 샘플 흐름, IoT Credential Provider, 크로스 컴파일 |
| 20 | [뷰어·백엔드 구현](/study/webrtc/20-kvs-viewer-backend) | JS SDK 뷰어, 자격증명 발급 방식, 채널 프로비저닝 |
| 21 | [WebRTC 인제스트와 저장](/study/webrtc/21-kvs-ingestion-storage) | Video Streams 기본, 저장 세션, 녹화와 실시간 시청 설계 |
| 22 | [KVS 운영·보안·비용](/study/webrtc/22-kvs-operations) | 최소 권한 IAM, 메트릭, TURN 비용, 흔한 장애 |

### AWS 관리형 WebRTC — Chime SDK·IVS (23~24)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 23 | [Amazon Chime SDK](/study/webrtc/23-chime-sdk) | SFU 회의 모델, Media Pipelines, 디바이스 플랫폼 적합성 |
| 24 | [Amazon IVS Real-Time Streaming](/study/webrtc/24-ivs-real-time) | Stage·Participant Token, Composition, WHIP 퍼블리시 |

### 캡스톤 (25)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 25 | [캡스톤: 농기계 원격 영상·제어 플랫폼](/study/webrtc/25-capstone-farm-platform) | 요구사항에서 아키텍처·시퀀스·장애·비용까지 통합 설계 |

### 부록

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 부록 | [용어집](/study/webrtc/appendix-glossary) | WebRTC·AWS 관리형 서비스 핵심 용어 정리 |
| 부록 | [참고 자료](/study/webrtc/appendix-references) | RFC·W3C·AWS 공식 문서 링크 |

## 관련 글

- [WebSocket 과 SSE](/posts/tech/2025-07-20-ssewebsocket): 시그널링 전송 수단으로 쓰는 WebSocket과 SSE 비교
- [AWS IoT Core 완전 정복 - Shadow, 인증, Job까지](/posts/tech/2025-06-27-iot): 디바이스 인증서와 자격증명 발급의 기반
- [MQTT 프로토콜과 AWS IoT 적용](/posts/tech/2025-08-13-mqtt): DataChannel과 역할을 나누는 제어 채널
