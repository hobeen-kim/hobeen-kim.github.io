---
title: "품질 제어와 지연 예산"
description: "NACK·PLI/FIR·FEC/RED로 손실을 복구하는 방법, GCC·TWCC·REMB 혼잡 제어와 대역폭 추정, setParameters·degradationPreference로 비트레이트를 적응시키는 방법, 캡처부터 렌더까지의 glass-to-glass 지연 분해와 jitterBufferTarget·키프레임 간격, 디바이스 LTE 업링크 튜닝을 다룬다."
date: 2026-10-19
tags: [WebRTC, Congestion Control, GCC, NACK, FEC, Latency]
prev: /study/webrtc/08-rtp-codecs
next: /study/webrtc/10-dtls-srtp
---

# 품질 제어와 지연 예산

::: info 학습 목표
- 손실 복구 세 갈래(NACK/RTX 재전송, PLI/FIR 키프레임 요청, FEC/RED 선제 중복)의 동작과 비용을 비교하고, RTT·손실 패턴에 따라 고를 수 있다.
- GCC가 지연 기반 추정과 손실 기반 추정을 어떻게 결합하는지, TWCC(송신측 추정)와 REMB(수신측 추정)가 무엇이 다른지 설명할 수 있다.
- `RTCRtpSender.setParameters`로 maxBitrate·scaleResolutionDownBy·maxFramerate를 조정하고, degradationPreference로 "해상도냐 프레임레이트냐"를 정할 수 있다.
- glass-to-glass 지연을 캡처·인코딩·패킷화·네트워크·지터 버퍼·디코드·렌더 단계로 분해해 측정하고, jitterBufferTarget과 키프레임 간격이 지연과 회복 시간에 주는 영향을 안다.
- LTE 업링크 디바이스에서 시작 비트레이트와 해상도 사다리를 설계할 수 있다.
:::

## 1. 손실 복구 ① — NACK/RTX와 PLI/FIR

[08장](/study/webrtc/08-rtp-codecs)에서 본 것처럼 RTP는 스스로 재전송하지 않는다. 패킷이 빠졌을 때 WebRTC가 쓸 수 있는 대응은 세 갈래다.

| 전략 | 방법 | 추가 지연 | 대역폭 비용 | 잘 맞는 상황 |
|---|---|---|---|---|
| 재전송 (ARQ) | 수신측이 NACK, 송신측이 RTX로 다시 보냄 | 약 1 RTT | 잃은 만큼만 | RTT가 지터 버퍼 여유보다 작을 때 |
| 새로 고침 요청 | 수신측이 PLI/FIR, 송신측이 키프레임 생성 | RTT + 키프레임 인코딩·전송 | 키프레임 한 장 (크다) | 재전송으로 못 살린 비디오 |
| 선제 중복 (FEC/RED) | 송신측이 미리 여분을 함께 보냄 | 거의 없음 | 항상 수십 % 추가 | RTT가 크고 무작위 손실이 있을 때 (2절) |

### NACK과 RTX

수신측은 sequence number에 구멍이 생기면 <strong>Generic NACK</strong>(RFC 4585, RTCP RTPFB FMT=1)을 보낸다. NACK의 FCI는 PID(16비트, 잃은 첫 seq)와 BLP(16비트 비트마스크, 그 뒤 16개 중 잃은 것)로 이뤄져, FCI 하나로 최대 17개 패킷을 한 번에 요청할 수 있다.

송신측은 최근에 보낸 패킷을 히스토리 버퍼에 들고 있다가 요청받은 패킷을 다시 보낸다. 이때 원래 스트림에 그대로 다시 넣지 않고 <strong>RTX</strong>(RFC 4588)라는 별도 스트림으로 보낸다. RTX 패킷은 다른 PT(`a=rtpmap:97 rtx/90000`, `a=fmtp:97 apt=96`)와 다른 SSRC(`a=ssrc-group:FID`)를 쓰고, 페이로드 앞 2바이트에 원래 sequence number(OSN)를 담는다. 따로 두는 이유는 재전송이 원래 스트림의 손실·지터 통계를 오염시키지 않게 하고, 재전송과 원본을 명확히 구분하기 위해서다.

NACK이 효과를 보려면 시간 계산이 맞아야 한다. 재전송 패킷은 손실 감지 후 대략 <strong>1 RTT 뒤</strong>에 도착한다. 그 프레임이 지터 버퍼에서 꺼내질 시각까지 도착하지 못하면 재전송은 헛수고다. 그래서 수신측 구현은 NACK을 쓸 때 RTT를 고려해 지터 버퍼 목표 지연을 늘리기도 한다. 즉 <strong>NACK은 지연을 대가로 화질을 산다</strong>. 같은 도시 안의 유선망(RTT 수십 ms 이하)에서는 거의 공짜에 가깝지만, LTE를 거치고 먼 리전의 TURN을 경유해 RTT가 200 ms를 넘으면 NACK 대기만으로 영상이 눈에 띄게 늦어진다.

송신측 히스토리 버퍼 크기도 디바이스에서는 신경 써야 한다. 예를 들어 KVS WebRTC C SDK는 RTP 패킷을 롤링 버퍼에 보관해 NACK에 응답하는데, 기본값은 버퍼 3초, MTU 1,200바이트, 예상 최대 비트레이트 비디오 5 Mbps·오디오 1 Mbps 기준으로 용량을 잡는다. 메모리를 줄이려고 `configureTransceiverRollingBuffer`로 버퍼를 지나치게 작게 잡으면, 망이 나빠 NACK이 몰릴 때 응답할 패킷이 이미 사라져 영상이 끊긴다고 SDK 문서가 경고한다. 버퍼는 "RTT 여러 번 + 재시도 횟수"를 덮을 만큼은 있어야 한다.

오디오에는 브라우저 기본 SDP에서 보통 `nack`이 붙지 않는다. 오디오 패킷은 20 ms마다 오고 지터 버퍼가 짧아 재전송을 기다릴 여유가 적기 때문이다. 오디오는 손실 은닉(PLC)과 Opus 인밴드 FEC, RED(2절)로 버틴다.

### PLI와 FIR

재전송으로도 살리지 못한 패킷이 있으면 비디오 디코더는 그 프레임을 디코딩할 수 없다. 더 큰 문제는 그 뒤의 P 프레임들이 모두 이 프레임을 (직간접으로) 참조한다는 점이다. 참조 체인이 끊기면 다음 키프레임이 올 때까지 화면이 멈추거나 깨진다. 이때 수신측은 송신측에 키프레임을 요청한다.

| 메시지 | 규격 | RTCP 형식 | 의미 | 쓰임 |
|---|---|---|---|---|
| PLI (Picture Loss Indication) | RFC 4585 | PSFB FMT=1, FCI 없음 | "그림을 잃었다" | 손실·디코딩 오류 후 복구. 브라우저의 주된 요청 |
| FIR (Full Intra Request) | RFC 5104 | PSFB FMT=4, 시퀀스 번호 포함 | "디코더를 새로 고쳐라" | 새 참가자 합류, MCU의 소스 전환 등. SDP `ccm fir` |

![손실 복구 시퀀스 — 디바이스가 P 프레임 #100을 보낸 뒤 #101의 일부 패킷이 손실되면, A 경우는 브라우저가 NACK(RTCP RTPFB FMT=1)을 보내고 디바이스가 RTX로 재전송해 지터 버퍼 기한 안에 도착하면 약 1 RTT 추가 지연으로 정상 재생되고, B 경우는 재전송도 실패해 #101 디코딩이 불가하고 이후 P 프레임 참조가 깨져 화면이 정지하므로 브라우저가 PLI(RTCP PSFB FMT=1)를 보내고 디바이스가 IDR을 강제 생성해 P 프레임 수 배 크기의 FU-A 패킷 버스트로 보낸 뒤에야 디코딩이 재개되는 흐름](/images/study-webrtc/09-pli-recovery-light.png)
![손실 복구 시퀀스 — 디바이스가 P 프레임 #100을 보낸 뒤 #101의 일부 패킷이 손실되면, A 경우는 브라우저가 NACK(RTCP RTPFB FMT=1)을 보내고 디바이스가 RTX로 재전송해 지터 버퍼 기한 안에 도착하면 약 1 RTT 추가 지연으로 정상 재생되고, B 경우는 재전송도 실패해 #101 디코딩이 불가하고 이후 P 프레임 참조가 깨져 화면이 정지하므로 브라우저가 PLI(RTCP PSFB FMT=1)를 보내고 디바이스가 IDR을 강제 생성해 P 프레임 수 배 크기의 FU-A 패킷 버스트로 보낸 뒤에야 디코딩이 재개되는 흐름](/images/study-webrtc/09-pli-recovery-dark.png)

PLI 복구에는 숨은 비용이 있다. 키프레임은 P 프레임보다 몇 배에서 열 배 이상 크다. 손실 직후, 즉 망이 이미 힘든 순간에 큰 버스트를 밀어 넣으므로 이 키프레임이 다시 손실되면 또 PLI가 오는 악순환이 생길 수 있다. 화면 정지 시간은 "손실 감지 + NACK 재시도 대기 + PLI 전달 + IDR 인코딩 + IDR 전송 + 디코딩"의 합이다. 이 시간을 줄이는 키프레임 간격 설계는 6절에서 다룬다.

디바이스 스택이 PLI/FIR에 반응하지 않으면 뷰어는 다음 주기 키프레임까지 멈춘 화면을 본다. KVS WebRTC C SDK처럼 PLI·FIR을 <strong>콜백으로만 알려주는</strong> 스택에서는, 그 콜백에서 인코더에 키프레임을 강제하는 코드를 애플리케이션이 직접 넣어야 한다(6절 코드, [19장](/study/webrtc/19-kvs-c-sdk)).

## 2. 손실 복구 ② — FEC와 RED

재전송은 RTT만큼 늦다. RTT가 크거나 지연 예산이 빠듯하면, 손실을 예상하고 <strong>여분을 미리 보내는</strong> 방법이 낫다. 수신측은 재전송을 기다리지 않고 여분으로 즉시 복원한다. 대신 손실이 없어도 여분의 대역폭을 항상 쓴다.

| 방식 | 규격 | 원리 | 보호 대상 | 오버헤드 | 브라우저 현황 |
|---|---|---|---|---|---|
| RED | RFC 2198 | 이전 프레임의 인코딩 사본을 현재 패킷에 함께 담음 | 주로 오디오 (`audio/red`) | 중복 1단계면 오디오 비트레이트가 2배 가까이 | Chrome 지원. 기본은 Opus 뒤 순위라 꺼져 있고, 우선순위를 올려 켠다 |
| ULPFEC | RFC 5109 | 여러 패킷의 XOR 패리티를 별도 패킷으로 전송 (RED로 감싸 보냄) | 비디오 | 손실률에 맞춰 가변 | libwebrtc 지원 (`red`·`ulpfec`) |
| FlexFEC | RFC 8627 | 행·열 2차원 XOR 패리티, 별도 SSRC 스트림 (`ssrc-group:FEC-FR`) | 비디오 | 가변, 연속 손실에 강함 | 구현은 있으나 브라우저 기본 활성화는 아님 |
| Opus 인밴드 FEC | RFC 6716 (LBRR) | 이전 프레임의 저비트레이트 사본을 다음 패킷 안에 삽입 | 오디오 | 같은 비트레이트 예산 안에서 본 음질을 깎음 | `useinbandfec=1`이 브라우저 기본 fmtp |

### 운영에서 알아둘 점

- <strong>H.264 + NACK이면 ULPFEC는 꺼진다</strong>: libwebrtc 송신측은 picture ID가 없는 페이로드(H.264 등)에서 NACK과 ULPFEC를 함께 쓰면, 수신측이 스트림 완결 여부를 판단하려고 FEC 패킷까지 재전송받아야 해서 대역폭 낭비라며 ULPFEC를 비활성화한다. VP8·VP9에서는 함께 쓴다. 디바이스가 H.264를 보낸다면 비디오 손실 대응은 사실상 NACK + PLI 조합이 된다.
- <strong>혼잡 손실에 FEC를 더하면 불난 데 기름을 붓는다</strong>: 손실 원인이 큐 넘침(혼잡)이면 FEC 오버헤드가 혼잡을 키운다. FEC는 무선 구간처럼 혼잡과 무관한 <strong>무작위 손실</strong>에 효과적이다. libwebrtc는 FEC 비율을 손실률과 대역폭 추정에 맞춰 조절하고 그 오버헤드를 추정치에서 뺀다. 직접 구현하는 스택이라면 같은 원칙을 지켜야 한다.
- <strong>Opus 인밴드 FEC는 인코더가 손실을 알아야 켜진다</strong>: 인코더에 예상 손실률이 주어져야 LBRR을 넣는다. 브라우저는 RTCP 수신 보고를 보고 자동 조절한다.

오디오 RED는 브라우저가 지원 목록에 `audio/red`를 노출하는 경우, 코덱 우선순위에서 Opus보다 앞에 두는 방식으로 켠다. 상대 스택이 RED를 모르면 협상에서 자연히 빠지고 Opus가 선택된다.

```js
// Prefer RED-wrapped Opus for audio when the browser exposes it.
const audioTr = pc.getTransceivers().find(t => t.receiver.track.kind === 'audio');
const { codecs } = RTCRtpReceiver.getCapabilities('audio');
const isRed = c => c.mimeType.toLowerCase() === 'audio/red';
if (codecs.some(isRed)) {
  audioTr.setCodecPreferences([...codecs.filter(isRed), ...codecs.filter(c => !isRed(c))]);
}
```

정리하면 선택 기준은 RTT와 손실 패턴이다. RTT가 작으면 NACK이 가장 효율적이고, RTT가 크고 무작위 손실이 있으면 FEC가 지연 없이 복원하며, 오디오는 인밴드 FEC·RED·PLC 조합으로, 비디오에서 다 실패하면 PLI로 키프레임을 받는다.

## 3. 혼잡 제어 — GCC, TWCC, REMB

### 왜 지연을 보고 혼잡을 판단하는가

TCP는 커널이 혼잡 제어를 해주지만 RTP over UDP는 아무도 해주지 않는다. 송신측이 망 용량보다 많이 보내면 경로 어딘가의 큐가 차고, 결국 넘쳐 손실이 난다. 문제는 그 순서다. 손실보다 <strong>큐잉 지연 증가가 먼저</strong> 온다. 특히 LTE 모뎀과 기지국, 가정용 공유기는 버퍼가 깊어서(bufferbloat) 손실이 나기 전까지 수백 ms의 지연이 쌓이기도 한다. 손실만 보고 속도를 줄이면 이미 영상이 1초 늦은 뒤다. 실시간 미디어의 혼잡 제어가 <strong>지연 변화</strong>를 1차 신호로 쓰는 이유다.

### GCC: 지연 기반 + 손실 기반

브라우저(libwebrtc)가 쓰는 알고리즘의 원형은 <strong>GCC(Google Congestion Control)</strong>이고, IETF RMCAT 워킹그룹 초안(draft-ietf-rmcat-gcc-02)으로 정리됐다. RFC가 되지는 못하고 만료된 초안이지만 구조를 이해하는 데는 충분하다.

![GCC 개념 — 송신측의 인코더와 페이서가 transport-cc 확장이 붙은 RTP를 네트워크로 보내면 수신측이 패킷별 도착 시각을 기록해 TWCC 피드백(RTCP RTPFB FMT=15)으로 돌려주고, 송신측의 지연 기반 추정기(도착 시간 필터 → 과사용 감지(적응 임계값) → 레이트 제어(증가·유지·감소))가 A를, 수신 보고(RR)의 손실률을 받은 손실 기반 추정기(손실 2% 미만 ×1.05, 2~10% 유지, 10% 초과 ×(1-0.5p))가 As를 계산해 min(A, As)를 목표 비트레이트로 인코더와 페이서에 적용하는 구조](/images/study-webrtc/09-gcc-light.png)
![GCC 개념 — 송신측의 인코더와 페이서가 transport-cc 확장이 붙은 RTP를 네트워크로 보내면 수신측이 패킷별 도착 시각을 기록해 TWCC 피드백(RTCP RTPFB FMT=15)으로 돌려주고, 송신측의 지연 기반 추정기(도착 시간 필터 → 과사용 감지(적응 임계값) → 레이트 제어(증가·유지·감소))가 A를, 수신 보고(RR)의 손실률을 받은 손실 기반 추정기(손실 2% 미만 ×1.05, 2~10% 유지, 10% 초과 ×(1-0.5p))가 As를 계산해 min(A, As)를 목표 비트레이트로 인코더와 페이서에 적용하는 구조](/images/study-webrtc/09-gcc-dark.png)

<strong>지연 기반 추정기</strong>는 세 단계로 동작한다.

1. <strong>도착 시간 필터</strong>: 패킷 묶음 사이의 "도착 간격 − 송신 간격"을 잰다. 이 값이 계속 양수면 큐가 차오르고 있다는 뜻이다. 초안은 칼만 필터로 이 추세를 추정한다.
2. <strong>과사용 감지</strong>: 추정한 추세를 임계값과 비교해 과사용(overuse)·정상·저사용(underuse) 신호를 낸다. 임계값은 고정이 아니라 상황에 따라 적응한다. 고정 임계값이면 TCP 같은 손실 기반 흐름과 경쟁할 때 일방적으로 밀려나기 때문이다.
3. <strong>레이트 제어</strong>: 증가·유지·감소 상태 기계다. 정상이면 늘리고(수렴점에서 멀면 초당 최대 8% 곱셈 증가, 가까우면 덧셈 증가), 과사용이면 <strong>실제 수신 비트레이트의 0.85배</strong>로 줄이며, 저사용이면 큐가 빠질 때까지 유지한다.

<strong>손실 기반 추정기</strong>는 단순하다. 손실률 p가 2% 미만이면 추정치를 1.05배로 올리고, 2~10%면 유지하며, 10%를 넘으면 `As × (1 − 0.5p)`로 깎는다. 2% 정도의 손실은 무선 구간에서 늘 있으므로 무시한다는 설계다.

최종 목표 비트레이트는 <strong>두 추정치 중 작은 값</strong>이다. 이 값이 인코더의 목표 비트레이트와 페이서의 전송 속도가 된다. 페이서는 인코더가 한꺼번에 내놓는 패킷(특히 키프레임)을 시간축에 펴서 보내 순간 버스트가 큐를 채우지 않게 한다. 또 망에 여유가 있는지 확인하려고 패딩이나 RTX로 짧은 프로브 버스트를 보내 추정치를 빠르게 끌어올린다.

::: info 초안과 실제 구현의 차이
현재 libwebrtc는 초안의 칼만 필터 대신 선형 회귀 기반 trendline 추정기를 쓰고, 손실 기반 추정도 개선판으로 바뀌는 등 계속 진화하고 있다. 위 수치(8%, 0.85, 2%/10%)는 구조를 이해하기 위한 초안 기준 값이며, 특정 브라우저 버전의 동작과 정확히 일치한다고 가정하면 안 된다.
:::

### TWCC vs REMB: 누가 추정하는가

지연 기반 추정을 어디서 하느냐에 따라 두 방식이 있다.

| 항목 | REMB | TWCC (transport-wide CC) |
|---|---|---|
| 추정 위치 | <strong>수신측</strong> | <strong>송신측</strong> |
| 필요한 헤더 확장 | abs-send-time | transport-wide-cc (트랜스포트 공통 시퀀스 번호) |
| RTCP 피드백 | PSFB FMT=15(AFB) + 'REMB' 식별자. 추정 비트레이트 숫자 하나 | RTPFB FMT=15. 패킷별 수신 여부와 도착 시각 |
| SDP | `a=rtcp-fb:96 goog-remb` | `a=rtcp-fb:96 transport-cc` |
| 송신측이 아는 것 | 결과 숫자만 | 원자료. 지연·손실을 직접 분석하고 페이싱·프로빙·FEC와 결합 |
| 규격 지위 | 만료된 개인 초안 | 만료된 개인 초안 (IETF 표준 대안은 RFC 8888) |
| 현황 | 레거시. 일부 SFU·디바이스 스택이 아직 사용 | 브라우저 기본 |

송신측 추정이 유리한 이유는 정보의 위치다. 언제 어떤 패킷을 얼마나 보냈는지, 어느 것이 프로브이고 RTX이고 FEC인지는 송신측만 정확히 안다. 알고리즘을 개선할 때도 송신측만 바꾸면 되므로, 수신측 브라우저 버전과 무관하게 디바이스·서버 쪽에서 혼잡 제어를 진화시킬 수 있다. IETF는 TWCC와 비슷한 역할의 표준 피드백 형식으로 RFC 8888(RTCP Feedback for Congestion Control)을 만들었지만, 브라우저 실사용은 여전히 TWCC가 주류다.

어느 쪽이 협상됐는지는 SDP의 `a=rtcp-fb`와 `a=extmap`으로 확인한다. 추정 결과는 브라우저가 송신측일 때 `getStats()`의 `candidate-pair.availableOutgoingBitrate`와 `outbound-rtp.targetBitrate`로 볼 수 있다([15장](/study/webrtc/15-monitoring-debugging)).

### 디바이스가 송신측일 때

농기계·로봇 시나리오에서 영상 송신측은 디바이스다. 혼잡 제어는 <strong>송신측 스택</strong>이 해야 하므로 디바이스 스택이 무엇을 제공하는지가 중요하다.

| 디바이스 스택 | 대역폭 추정 | 인코더 반영 |
|---|---|---|
| libwebrtc 네이티브 (Android·Linux) | GCC 내장 | 자동 (브라우저와 동일) |
| Pion (Go) | `pion/interceptor`의 GCC 구현으로 송신측 추정 | 목표 비트레이트 변경 콜백에서 애플리케이션이 인코더 설정 |
| GStreamer `webrtcsink`·`rtpgccbwe` (gst-plugins-rs) | GCC 계열 혼잡 제어 제공 | 요소가 인코더 비트레이트까지 조절 |
| KVS WebRTC C SDK | 혼잡 제어 관련 콜백 제공 | <strong>애플리케이션이 직접</strong> 인코더 비트레이트 조절 ([19장](/study/webrtc/19-kvs-c-sdk)) |

마지막 경우처럼 "추정은 스택, 반영은 앱"인 구조에서는 7절의 사다리 로직을 직접 구현해야 한다. 추정치를 무시하고 고정 비트레이트로 보내는 디바이스가 현장에서 가장 흔한 품질 문제의 원인이다.

## 4. 비트레이트 적응 — setParameters와 degradationPreference

대역폭 추정은 "망이 허락하는 상한"을 정한다. 그 안에서 "얼마나, 어떤 모양으로 보낼지"는 애플리케이션이 정할 수 있다. 브라우저(또는 네이티브 libwebrtc)가 송신측일 때 쓰는 표준 API가 `RTCRtpSender.setParameters`다. 실제 송신 비트레이트는 대략 `min(대역폭 추정, maxBitrate)`가 된다. 재협상(SDP 교환) 없이 즉시 적용된다는 점이 장점이다.

| 파라미터 | 위치 | 단위 | 의미 |
|---|---|---|---|
| `maxBitrate` | `encodings[i]` | bps | 이 인코딩의 비트레이트 상한 (IP/UDP 오버헤드 제외) |
| `scaleResolutionDownBy` | `encodings[i]` | 배율 (≥ 1.0) | 2.0이면 가로·세로 각각 절반 |
| `maxFramerate` | `encodings[i]` | fps | 프레임레이트 상한 |
| `active` | `encodings[i]` | boolean | false면 이 인코딩 송신 중단 (SSRC는 유지) |
| `degradationPreference` | 최상위 | 문자열 | 대역폭·CPU가 모자랄 때 무엇을 먼저 희생할지 |

```js
// Cap the outgoing video without renegotiation.
async function applyVideoProfile(sender, { maxBitrate, scale, maxFramerate, preference }) {
  const params = sender.getParameters();          // must start from getParameters()
  if (!params.encodings || params.encodings.length === 0) params.encodings = [{}];
  const enc = params.encodings[0];
  enc.maxBitrate = maxBitrate;                     // bps, upper bound on top of BWE
  enc.scaleResolutionDownBy = scale;               // >= 1.0
  enc.maxFramerate = maxFramerate;                 // fps
  if (preference) params.degradationPreference = preference;
  await sender.setParameters(params);
}

const sender = pc.getSenders().find(s => s.track?.kind === 'video');
await applyVideoProfile(sender, {
  maxBitrate: 800_000,       // 800 kbps
  scale: 2.0,                // 1280x720 capture -> 640x360 encode
  maxFramerate: 20,
  preference: 'maintain-framerate',
});
```

`getParameters()`가 돌려준 객체를 고쳐서 넘겨야 한다. 내부의 `transactionId`로 "방금 읽은 값을 고친 것"인지 확인하기 때문이다. 인코딩 개수나 `rid`처럼 바꿀 수 없는 값을 건드리면 `InvalidModificationError`, `scaleResolutionDownBy`에 1.0 미만을 넣으면 `RangeError`가 난다. MDN은 일부 브라우저에서 `scaleResolutionDownBy`·`maxBitrate` 지원이 불완전했던 경우를 언급하며, 적용 후 `getParameters()`로 다시 읽어 확인하고 안 되면 `track.applyConstraints({ height })`로 캡처 해상도를 낮추는 폴백을 보여준다.

### degradationPreference: 해상도냐 프레임레이트냐

대역폭이나 CPU가 모자라면 인코더는 무언가를 희생해야 한다. 같은 비트레이트에서 해상도를 낮추면 프레임당 비트가 늘어 화질(블록 노이즈)이 지켜지고, 프레임레이트를 낮추면 움직임이 끊기는 대신 한 장 한 장은 선명하다.

| 값 | 희생하는 것 | 맞는 영상 |
|---|---|---|
| `maintain-framerate` | 해상도 | 원격 주행·조작 영상. 움직임의 연속성이 판단에 중요 |
| `maintain-resolution` | 프레임레이트 | 작물·부품 상태 점검, 계기판·문자 판독 |
| `balanced` | 둘 다 조금씩 (기본값) | 일반 화상 통화 |
| `maintain-framerate-and-resolution` | 둘 다 지키고 화질(양자화)만 희생 | 최근 규격에 추가된 값 |

MDN 호환성 데이터 기준으로 `setParameters`의 `degradationPreference`는 Chrome 83, Firefox 138, Safari 12.1부터 지원한다. `degradationPreference`를 지정하지 않으면 트랙의 `contentHint`가 기본 동작에 영향을 준다. `'motion'`이면 프레임레이트 유지 쪽, `'detail'`이나 `'text'`면 해상도 유지 쪽으로 동작한다.

```js
videoTrack.contentHint = 'motion';   // remote driving camera
// inspectionTrack.contentHint = 'detail';
```

실제로 무엇 때문에 품질이 제한되고 있는지는 `outbound-rtp.qualityLimitationReason`(`bandwidth`·`cpu`·`other`·`none`)과 `qualityLimitationDurations`로 확인한다. `cpu`가 자주 보이면 비트레이트가 아니라 인코딩 부하가 병목이다.

::: tip 디바이스 → 브라우저 시나리오에서는
`setParameters`는 <strong>송신측</strong> API다. 디바이스가 영상을 보내고 브라우저가 받는 구조에서 브라우저의 `setParameters`는 운영자 마이크·카메라 같은 상향 트랙에만 작용한다. 디바이스 영상에 같은 조절을 하려면 디바이스 쪽 인코더를 직접 조절해야 한다(7절). 운영자가 "점검 모드(해상도 우선)" / "주행 모드(프레임레이트 우선)" 버튼을 누르면 DataChannel로 디바이스에 프로파일 변경 명령을 보내는 설계가 자연스럽다([11장](/study/webrtc/11-datachannel)).
:::

## 5. glass-to-glass 지연 예산과 jitterBufferTarget

<strong>glass-to-glass 지연</strong>은 카메라 렌즈(유리)에 빛이 들어온 순간부터 운영자 모니터(유리)에 그 장면이 표시되는 순간까지의 시간이다. 네트워크 RTT만 보면 놓치는 부분이 많다. 지연은 파이프라인 전 단계에 흩어져 있다.

![glass-to-glass 지연 분해 — 디바이스의 캡처(센서 노출·ISP·드라이버 버퍼 15~50ms), 인코딩(HW 5~30ms), 패킷화·페이싱(1~20ms), 망의 네트워크(LTE 업링크·인터넷, TURN 경유 시 증가 30~150ms), 브라우저의 지터 버퍼(20~200ms), 디코딩(5~30ms), 렌더(합성·vsync·디스플레이 15~50ms) 일곱 단계와, 720p30·LTE·HW 인코더 예시에서 30·15·5·60·50·10·30ms로 합계 약 200ms가 되는 비례 막대](/images/study-webrtc/09-glass-to-glass-light.png)
![glass-to-glass 지연 분해 — 디바이스의 캡처(센서 노출·ISP·드라이버 버퍼 15~50ms), 인코딩(HW 5~30ms), 패킷화·페이싱(1~20ms), 망의 네트워크(LTE 업링크·인터넷, TURN 경유 시 증가 30~150ms), 브라우저의 지터 버퍼(20~200ms), 디코딩(5~30ms), 렌더(합성·vsync·디스플레이 15~50ms) 일곱 단계와, 720p30·LTE·HW 인코더 예시에서 30·15·5·60·50·10·30ms로 합계 약 200ms가 되는 비례 막대](/images/study-webrtc/09-glass-to-glass-dark.png)

그림의 범위는 감을 잡기 위한 <strong>대략적인 값</strong>이다. 하드웨어·드라이버·망 상태에 따라 크게 달라지므로 반드시 실측해야 한다. 단계별로 무엇이 지연을 만들고 무엇으로 줄이는지 정리하면 다음과 같다.

| 단계 | 지연 원인 | 줄이는 손잡이 |
|---|---|---|
| 캡처 | 노출 시간(어두우면 길어짐), ISP 처리, V4L2 버퍼 큐 깊이 | 프레임레이트 올리기, 캡처 버퍼 개수 줄이기, 자동 노출 상한 |
| 인코딩 | 인코더 내부 버퍼, lookahead, B 프레임 | HW 인코더, zerolatency 계열 설정, B 프레임·lookahead 끄기 |
| 패킷화·페이싱 | 큰 프레임을 페이서가 펴서 보내는 시간 | 키프레임 크기 제한(VBV), 적절한 비트레이트 |
| 네트워크 | 전파 지연, LTE 스케줄링, 큐잉, TURN 우회 | 가까운 TURN 리전, UDP 우선([07장](/study/webrtc/07-turn)), 혼잡 제어로 큐 비우기 |
| 지터 버퍼 | 지터 흡수, NACK 대기, 립싱크 정렬 | 망 안정화, jitterBufferTarget, 오디오 동기화 분리 |
| 디코딩 | 디코더 버퍼, SW 디코딩 | 브라우저 HW 디코딩, 적정 해상도 |
| 렌더 | 브라우저 합성, vsync 대기, 모니터 입력 지연 | 고주사율 모니터, 저지연 디스플레이 모드 |

인코더·디코더·렌더처럼 줄이기 어려운 고정 비용이 100 ms 가까이 되는 경우가 많다. 그래서 실질적인 튜닝 대상은 <strong>네트워크와 지터 버퍼</strong>, 그리고 캡처 버퍼처럼 설정 하나로 수십 ms가 바뀌는 곳이다.

### 측정 방법

1. <strong>화면 촬영법</strong>: 밀리초 단위 시계를 띄운 화면을 디바이스 카메라로 찍고, 그 시계와 운영자 브라우저 화면을 나란히 놓고 한 장의 사진으로 찍는다. 두 시계의 차이가 glass-to-glass 지연이다. 가장 원시적이지만 모든 단계를 포함하는 유일한 방법이다.
2. <strong>requestVideoFrameCallback 메타데이터</strong>: 원격 WebRTC 비디오에서 프레임별로 `captureTime`(RTCP SR로 추정한 캡처 시각), `receiveTime`(인코딩된 프레임 수신 시각), `expectedDisplayTime`을 준다. 송신측이 SR의 NTP↔RTP 매핑을 올바르게 보내야 의미 있는 값이 나온다([08장](/study/webrtc/08-rtp-codecs) 5절).
3. <strong>getStats 분해</strong>: `candidate-pair.currentRoundTripTime / 2`로 단방향 망 지연을 어림하고, `inbound-rtp`의 `jitterBufferDelay / jitterBufferEmittedCount`(지터 버퍼), `totalDecodeTime / framesDecoded`(디코딩)로 수신측 단계를 나눈다.

```js
// Per-frame latency breakdown in the viewer (fields appear only where supported).
const video = document.querySelector('video');
function onFrame(now, meta) {
  if (meta.captureTime !== undefined && meta.receiveTime !== undefined) {
    const toReceive = meta.receiveTime - meta.captureTime;           // capture + encode + network
    const toDisplay = meta.expectedDisplayTime - meta.captureTime;   // full estimate to display
    console.log(`capture→receive ${toReceive.toFixed(0)} ms, capture→display ${toDisplay.toFixed(0)} ms`);
  }
  video.requestVideoFrameCallback(onFrame);
}
video.requestVideoFrameCallback(onFrame);
```

`captureTime`은 송수신 시계 차이를 RTT 기반으로 보정한 <strong>추정치</strong>라서 절대값보다 추세를 보는 용도로 쓴다. 모니터링 체계와 지표 수집은 [15장](/study/webrtc/15-monitoring-debugging)에서 다룬다.

### jitterBufferTarget

`RTCRtpReceiver.jitterBufferTarget`은 애플리케이션이 지터 버퍼가 미디어를 얼마나 붙잡아 두기를 원하는지 밀리초로 알려주는 속성이다.

- <strong>범위</strong>: 0 이상 4000 ms 이하. 음수나 4000 초과는 `RangeError`다.
- <strong>힌트일 뿐이다</strong>: 브라우저는 망 상태와 메모리 제약 안에서 자기가 제공할 수 있는 범위로 실제 목표를 정한다. 속성 값을 읽어도 실제 목표가 아니라 내가 설정한 값이 돌아온다. 효과는 `inbound-rtp`의 `jitterBufferTargetDelay / jitterBufferEmittedCount` 추이를 `jitterBufferMinimumDelay`와 비교해 확인한다.
- <strong>동기화된 오디오·비디오</strong>는 두 수신기의 값 중 큰 쪽이 양쪽에 적용된다.
- <strong>지원</strong>: MDN 호환성 데이터 기준 Chrome 124, Firefox 115, Safari 27부터 지원하며, 2026년 9월에 주요 브라우저 공통 지원(Baseline)에 들어갔다. 그 전에는 Chrome 전용 비표준 `playoutDelayHint`가 비슷한 역할을 했다.

```js
const videoReceiver = pc.getReceivers().find(r => r.track.kind === 'video');
if ('jitterBufferTarget' in RTCRtpReceiver.prototype) {
  videoReceiver.jitterBufferTarget = 400;   // ms: favor smoothness on a monitoring wall
}
```

용도는 둘로 갈린다. <strong>관제 화면처럼 보기만 하는 경우</strong>에는 값을 올려 끊김을 줄이는 쪽이 유리하다. 약간 늦어도 매끄러운 편이 낫다. <strong>원격 조작 화면</strong>에서는 기본 적응형 동작에 맡기거나 낮은 값을 주되, 브라우저가 망 상태상 필요한 최소 버퍼보다 더 낮춰 준다는 보장은 없다는 점을 기억한다. 조작 지연을 줄이는 근본 대책은 지터 자체를 줄이는 것(혼잡 제어가 큐를 비우게 하기, 안정된 망 경로)이다.

## 6. GOP·키프레임 간격과 PLI 회복 시간

GOP(Group of Pictures)는 키프레임에서 다음 키프레임까지의 프레임 묶음이다. 키프레임 간격을 어떻게 잡느냐는 세 가지를 동시에 흔든다. <strong>비트레이트 효율, 손실 회복 시간, 새 뷰어의 첫 화면 시간</strong>이다.

### 키프레임의 크기를 계산해 보면

1.5 Mbps, 30 fps라면 프레임당 평균 약 6.25 KB다. 키프레임이 평균 프레임의 8배라고 하면 약 50 KB, 즉 400 kbit다. 1.5 Mbps 링크로 이걸 보내는 데만 <strong>약 270 ms</strong>가 걸린다. 페이서는 이 버스트를 펴서 보내야 하고, 그동안 뒤따르는 P 프레임은 기다린다. 키프레임이 자주 오면 이런 지연·버스트가 주기적으로 반복되고, LTE처럼 여유 없는 업링크에서는 그 순간마다 손실이나 지연 스파이크가 생긴다.

### 간격별 트레이드오프

| 설정 | 장점 | 단점 | 맞는 경우 |
|---|---|---|---|
| 짧은 GOP (약 1초) | 회복 상한이 짧다, 새 뷰어가 빨리 화면을 본다 | 비트레이트 효율 저하, 주기적 버스트 | 다수 뷰어가 수시로 붙는 스트림, PLI를 못 쓰는 경로 |
| 중간 GOP (2~4초) + PLI 대응 | 효율과 회복의 균형 | PLI 처리 구현 필요 | <strong>디바이스 → 브라우저의 무난한 기본값</strong> |
| 긴 GOP / 요청 시에만 | 효율 최대 | 회복을 전적으로 PLI에 의존. PLI가 유실되면 오래 멈춤 | 브라우저 간 통화(libwebrtc는 주기 키프레임을 매우 드물게 두고 PLI·FIR에 의존한다) |
| 인트라 리프레시 | 키프레임 버스트 없이 몇 프레임에 걸쳐 화면을 점진 갱신 | 인코더 지원 필요, 디코더 시작에는 여전히 IDR이 필요 | 대역폭이 빠듯한 업링크의 보조 수단 |

브라우저 디코더는 디코딩을 시작할 때 IDR을 기다리므로, 인트라 리프레시를 쓰더라도 새 뷰어 합류나 PLI 때는 IDR을 보내야 한다.

### 뷰어가 여럿이면: 키프레임 폭풍

KVS WebRTC처럼 P2P 구조에서는 뷰어마다 PeerConnection이 따로 있지만, 디바이스는 보통 <strong>인코더 하나의 출력을 모든 뷰어에게 나눠</strong> 보낸다. 그러면 한 뷰어가 보낸 PLI 때문에 생긴 키프레임이 모든 뷰어에게 간다. 망이 나쁜 뷰어 셋이 번갈아 PLI를 보내면 키프레임이 연달아 생기고, 키프레임 버스트가 업링크를 더 혼잡하게 만들어 다시 손실과 PLI를 부르는 악순환이 생긴다. 새 뷰어 합류도 같은 문제다. 바로 화면을 보여주려면 IDR을 강제해야 하는데, 그 비용을 기존 뷰어 모두가 나눠 낸다.

대책은 <strong>키프레임 요청 합치기(rate limit)</strong>다. 일정 시간 안에 들어온 PLI·FIR·합류 요청은 IDR 하나로 처리한다. 키프레임 하나가 모든 뷰어를 동시에 복구하므로 손해가 없다. GStreamer 인코더라면 다음과 같이 구현할 수 있다.

```c
#include <gst/gst.h>
#include <gst/video/video.h>

#define MIN_IDR_INTERVAL (1000 * GST_MSECOND)

static GstClockTime last_idr = GST_CLOCK_TIME_NONE;

/* Called (from a single RTCP/callback thread) whenever any viewer sends PLI/FIR
 * or a new viewer joins. One IDR serves every viewer sharing this encoder. */
void request_keyframe(GstElement *encoder)
{
    GstClockTime now = gst_util_get_timestamp();
    if (GST_CLOCK_TIME_IS_VALID(last_idr) && now - last_idr < MIN_IDR_INTERVAL)
        return;                                   /* coalesce bursts of requests */
    last_idr = now;

    /* all_headers=TRUE: emit SPS/PPS together with the IDR */
    gst_element_send_event(encoder,
        gst_video_event_new_upstream_force_key_unit(GST_CLOCK_TIME_NONE, TRUE, 0));
}
```

요청을 합치다 보면 막 복구 중이던 뷰어가 다음 IDR을 조금 더 기다릴 수 있지만, 수신측은 복구될 때까지 PLI를 반복해 보내므로 결국 다음 IDR로 복구된다. 간격 값은 RTT와 키프레임 전송 시간(위 계산의 270 ms 같은 값)보다 길게 잡는다. 뷰어가 많아지면 뷰어별 인코더(CPU 비용)나 SFU([12장](/study/webrtc/12-topology-sfu))로 구조를 바꾸는 것이 근본 대책이다.

## 7. 디바이스 업링크(LTE) 튜닝

농기계·로봇의 영상은 대부분 LTE(또는 5G) 업링크로 나간다. LTE 업링크는 다음 특성 때문에 유선과 전혀 다르게 다뤄야 한다.

- <strong>용량이 크게 흔들린다</strong>: 신호 세기, 셀 부하, 이동 속도에 따라 같은 장소에서도 수백 kbps에서 수 Mbps 이상까지 오간다. 농지처럼 기지국에서 먼 곳은 셀 가장자리라 특히 낮다.
- <strong>핸드오버</strong>: 이동 중 셀이 바뀌면 순간적인 지연 급증이나 버스트 손실이 생긴다.
- <strong>깊은 버퍼</strong>: 모뎀·기지국 버퍼가 깊어 과송신하면 손실보다 지연이 먼저 수백 ms씩 쌓인다(3절의 bufferbloat).
- <strong>업링크가 다운링크보다 훨씬 좁다</strong>: 스마트폰 기준 체감 속도와 업링크 실제 용량은 다르다.
- <strong>P2P면 뷰어 수만큼 업링크가 늘어난다</strong>: KVS WebRTC처럼 P2P 구조에서는 뷰어 3명에게 1.5 Mbps씩 보내면 업링크 4.5 Mbps가 필요하다([16장](/study/webrtc/16-aws-landscape)). 인코더를 공유하면 가장 나쁜 뷰어의 추정치에 맞춰 인코딩해야 한다.

### 시작 비트레이트: 낮게 시작해서 올린다

연결 직후에는 대역폭 추정치가 없다. libwebrtc는 이 초기값(시작 비트레이트)을 기본 300 kbps로 두고, 프로빙으로 빠르게 끌어올린다. 브라우저 송신 영상이 처음 몇 초 흐릿하다가 선명해지는 이유다.

인코더 비트레이트를 애플리케이션이 직접 정하는 디바이스 스택이라면 같은 원칙을 따른다. <strong>최대 화질로 시작하지 않는다.</strong> 4 Mbps로 시작했는데 실제 업링크가 1 Mbps라면 첫 몇 초 동안 큐가 넘쳐 손실이 나고, 그 손실이 PLI와 키프레임을 불러 더 넘친다. 운영자는 연결하자마자 깨진 화면을 본다. 640×360 정도의 중간 단계, 500 kbps 안팎에서 시작해 추정치가 확인되면 올리는 편이 첫인상과 안정성 모두에 낫다.

### 해상도 사다리

H.264 하드웨어 인코더 기준의 출발점 예시다. libwebrtc가 Simulcast 계층에 쓰는 기본 비트레이트도 비슷한 범위다. 실제 값은 장면(정지한 실내 vs 흔들리는 들판)과 인코더 품질에 따라 다르므로 현장 영상으로 조정한다.

| 단계 | 해상도 @ fps | 비트레이트 범위 | 비고 |
|---|---|---|---|
| L4 | 1280×720 @ 30 | 1.5~2.5 Mbps | 신호 좋은 정지·저속 상태 |
| L3 | 960×540 @ 30 | 0.8~1.2 Mbps | |
| L2 | 640×360 @ 30 | 0.4~0.7 Mbps | <strong>시작 단계</strong> |
| L1 | 640×360 @ 15 | 0.25~0.4 Mbps | 점검 영상이면 해상도 유지가 낫다 |
| L0 | 320×180 @ 15 | 0.1~0.2 Mbps | 최저 생존 모드 |

설계 원칙은 다음과 같다.

- <strong>추정치를 다 쓰지 않는다</strong>: 오디오(Opus 24~32 kbps), RTX 재전송, 헤더 오버헤드를 위해 추정치의 70~85% 정도를 인코더 목표로 쓴다.
- <strong>내릴 때는 빠르게, 올릴 때는 천천히</strong>: 추정치가 현재 단계 최소값 아래로 떨어지면 즉시 내리고, 다음 단계로 올릴 여유가 수 초~10초 이상 유지될 때만 올린다. 그래야 단계가 오르내리며 진동하지 않는다.
- <strong>해상도 변경은 비싸다</strong>: H.264에서 해상도가 바뀌면 새 SPS와 IDR이 필요하다. 단계 안에서는 비트레이트만 바꾸고, 해상도 변경은 드물게 한다.
- <strong>시나리오에 맞는 축을 고른다</strong>: 주행 영상은 프레임레이트를 지키고 해상도를 내리며, 점검 영상은 해상도를 지키고 프레임레이트를 내린다(4절의 degradationPreference와 같은 판단).

대역폭 추정 콜백을 받아 인코더를 조절하는 로직을 C로 쓰면 다음과 같다. 추정치가 어디서 오는지(TWCC 콜백, REMB 값 등)는 스택마다 다르다.

```c
#include <gst/gst.h>

typedef struct { int width, height, fps, min_kbps, max_kbps; } Step;

static const Step LADDER[] = {
    { 320, 180, 15,  100,  200},
    { 640, 360, 15,  250,  400},
    { 640, 360, 30,  400,  700},
    { 960, 540, 30,  800, 1200},
    {1280, 720, 30, 1500, 2500},
};
#define N_STEPS ((int)(sizeof(LADDER) / sizeof(LADDER[0])))

static int cur = 2;               /* start at 640x360@30, not at the top */
static guint64 up_since_ms = 0;   /* when headroom for the next step was first seen */

/* Pipeline-specific: change capture/scale caps and force an IDR. */
void apply_resolution(const Step *s);

/* Called on every bandwidth estimate from the WebRTC stack. */
void on_bandwidth_estimate(GstElement *encoder, guint64 now_ms, guint32 est_bps)
{
    int target_kbps = (int)(est_bps * 0.8 / 1000);   /* headroom for audio, RTX, headers */

    if (cur > 0 && target_kbps < LADDER[cur].min_kbps) {
        cur--;                                        /* step down immediately */
        up_since_ms = 0;
        apply_resolution(&LADDER[cur]);
    } else if (cur + 1 < N_STEPS && target_kbps > LADDER[cur + 1].min_kbps * 1.2) {
        if (up_since_ms == 0)
            up_since_ms = now_ms;
        if (now_ms - up_since_ms > 10000) {           /* step up after 10 s of headroom */
            cur++;
            up_since_ms = 0;
            apply_resolution(&LADDER[cur]);
        }
    } else {
        up_since_ms = 0;
    }

    int kbps = CLAMP(target_kbps, LADDER[cur].min_kbps, LADDER[cur].max_kbps);
    g_object_set(encoder, "bitrate", (guint) kbps, NULL);   /* x264enc: kbit/s */
}
```

`apply_resolution`은 파이프라인마다 구현이 다르다. capsfilter의 caps를 바꿔 재협상하는 방식이 되는 인코더도 있고, 하드웨어 인코더에 따라서는 파이프라인 일부를 재시작해야 하는 경우도 있다. 비트레이트 속성의 이름과 단위도 인코더마다 다르다(`x264enc`는 kbps, Jetson `nvv4l2h264enc`는 bps).

### LTE 업링크 점검표

- 대역폭 추정을 실제로 인코더에 반영하는가 (고정 비트레이트 송신 금지)
- 시작 단계가 최상위가 아닌가 (중간 단계에서 시작)
- 내림은 빠르게, 올림은 느리게 히스테리시스가 있는가
- 키프레임 간격 2~4초 + PLI 대응 + 요청 합치기가 있는가 (6절)
- SPS/PPS가 IDR마다 반복되는가 ([08장](/study/webrtc/08-rtp-codecs))
- TURN이 필요하면 UDP 릴레이와 가까운 리전을 쓰는가. TCP/TLS 릴레이는 헤드 오브 라인 블로킹으로 지연이 튄다 ([07장](/study/webrtc/07-turn))
- 패킷 크기가 1,200바이트 이하인가 (LTE·VPN 경로의 작은 MTU)
- 뷰어 수 × 비트레이트가 업링크에 들어가는가, 넘으면 뷰어 제한이나 SFU를 검토했는가
- 브라우저 측 `qualityLimitationReason`, `availableOutgoingBitrate`, `nackCount`, `pliCount`, `retransmittedBytesSent`를 수집하는가 ([15장](/study/webrtc/15-monitoring-debugging))

::: tip 핵심 정리
- 손실 복구는 NACK/RTX(약 1 RTT 지연, 잃은 만큼만 비용), PLI/FIR(키프레임 버스트), FEC/RED(지연 없음, 상시 오버헤드) 세 갈래다. RTT가 작으면 NACK, 크고 무작위 손실이면 FEC, 비디오가 끝내 깨지면 PLI다.
- libwebrtc는 H.264 + NACK에서 ULPFEC를 끈다. 디바이스 H.264 영상의 손실 대응은 사실상 NACK + PLI이고, 송신측 히스토리 버퍼가 충분해야 NACK에 응답할 수 있다.
- GCC는 지연 기반 추정(도착 시간 필터 → 과사용 감지 → AIMD 레이트 제어)과 손실 기반 추정(2%/10% 임계)의 최솟값을 목표 비트레이트로 쓴다. TWCC는 송신측이, REMB는 수신측이 추정하며 브라우저 기본은 TWCC다.
- `setParameters`로 maxBitrate·scaleResolutionDownBy·maxFramerate를 재협상 없이 조절하고, degradationPreference로 주행 영상은 프레임레이트, 점검 영상은 해상도를 지킨다.
- glass-to-glass 지연은 캡처·인코딩·패킷화·네트워크·지터 버퍼·디코드·렌더의 합이고, LTE 예시에서 대략 200 ms 안팎이다. 실측하고, 튜닝은 네트워크·지터 버퍼·캡처 버퍼에 집중한다. jitterBufferTarget은 0~4000 ms 힌트다.
- 키프레임 간격은 2~4초 + PLI 대응이 무난하고, 인코더를 공유하는 다중 뷰어에서는 키프레임 요청을 합쳐 키프레임 폭풍을 막는다.
- LTE 업링크는 낮게 시작해 올리고, 해상도 사다리와 히스테리시스로 추정치를 인코더에 반영한다.
:::

## 다음 챕터

[보안: DTLS-SRTP](/study/webrtc/10-dtls-srtp)에서는 이 장까지 다룬 RTP·RTCP 패킷이 어떻게 암호화되는지, DTLS 핸드셰이크와 `a=fingerprint` 검증으로 SRTP 키를 도출하는 과정과 시그널링 무결성에 기대는 WebRTC의 신뢰 모델을 다룬다.
