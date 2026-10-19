---
title: "WebRTC 인제스트와 저장"
description: "KVS Video Streams의 스트림·프래그먼트·보존 기간·HLS/DASH·GetClip을 먼저 정리하고, 시그널링 채널을 스트림에 연결하는 저장 모드(UpdateMediaStorageConfiguration, JoinStorageSession, JoinStorageSessionAsViewer)의 구조·흐름·코덱 제약과, 녹화와 실시간 시청을 함께 설계하는 세 가지 방식을 비교한다."
date: 2026-10-19
tags: [WebRTC, AWS, KinesisVideoStreams, Recording, HLS]
prev: /study/webrtc/20-kvs-viewer-backend
next: /study/webrtc/22-kvs-operations
---

# WebRTC 인제스트와 저장

::: info 학습 목표
- KVS Video Streams의 스트림·프래그먼트·보존 기간·PutMedia·HLS/DASH·GetClip이 각각 무엇이고 어떻게 맞물리는지 설명할 수 있다.
- 저장 모드를 켜면 P2P가 사라지고 모든 피어가 AWS의 storage 세션에 붙는다는 구조 변화를 이해한다.
- `UpdateMediaStorageConfiguration` → `JoinStorageSession` → SDP 교환으로 이어지는 흐름과, 이때 offer를 보내는 쪽이 바뀌는 이유를 안다.
- `JoinStorageSessionAsViewer`의 한도(viewer 3명, 오디오만 송신)와 코덱 제약(H.264 + Opus)을 설계에 반영할 수 있다.
- "P2P 시청 + 병행 녹화", "저장 모드", "Producer SDK PutMedia만" 세 방식을 지연·업링크·비용 기준으로 고를 수 있다.
:::

## 1. KVS Video Streams 기본: 스트림·프래그먼트·재생

앞 장까지 다룬 KVS WebRTC는 "시그널링 채널"이라는 리소스를 중심으로 돌아갔다. 이 장의 주제인 저장은 이름이 비슷한 다른 리소스, <strong>Kinesis Video Stream</strong>(이하 스트림)에 미디어를 쌓는 일이다. 같은 Kinesis Video Streams 서비스 안에 있지만 둘은 ARN부터 다르다(`channel/…` vs `stream/…`). 저장 모드를 이해하려면 스트림이 어떻게 생겼는지부터 알아야 한다. [17장](/study/webrtc/17-kvs-architecture)에서 KVS Video Streams와 WebRTC의 관계를 짚었으니, 여기서는 저장에 필요한 만큼 스트림 쪽을 자세히 본다.

![KVS Video Streams 모델. 왼쪽 농기계 카메라가 Producer SDK(kvssink)로 PutMedia 장기 연결을 열어 MKV를 보내고, 가운데 스트림 안에는 F1001부터 F1007까지 프래그먼트가 시간순으로 쌓이며 보존 기간 밖의 F1001은 만료된다. 오른쪽에는 GetDataEndpoint로 엔드포인트를 조회한 뒤 쓰는 소비 API 네 가지(HLS/DASH, GetClip, GetMedia, GetImages)가 있다](/images/study-webrtc/21-kvs-stream-model-light.png)
![KVS Video Streams 모델. 왼쪽 농기계 카메라가 Producer SDK(kvssink)로 PutMedia 장기 연결을 열어 MKV를 보내고, 가운데 스트림 안에는 F1001부터 F1007까지 프래그먼트가 시간순으로 쌓이며 보존 기간 밖의 F1001은 만료된다. 오른쪽에는 GetDataEndpoint로 엔드포인트를 조회한 뒤 쓰는 소비 API 네 가지(HLS/DASH, GetClip, GetMedia, GetImages)가 있다](/images/study-webrtc/21-kvs-stream-model-dark.png)

### 스트림과 데이터 보존 기간

스트림은 `CreateStream`으로 만든다. 이름은 계정·리전 안에서 유일해야 하고(1~256자, `[a-zA-Z0-9_.-]+`), 저장 데이터는 KMS 키로 암호화된다(지정하지 않으면 `aws/kinesisvideo` 관리형 키). 운영에서 가장 중요한 속성은 <strong>`DataRetentionInHours`</strong>다.

| 값 | 의미 |
|---|---|
| 0 (기본값) | 스트림이 데이터를 저장하지 않는다. 소비자는 서비스 호스트 버퍼에 남은 프래그먼트만 읽을 수 있고, 이 버퍼는 <strong>5분 또는 200 MB</strong> 중 먼저 닿는 한도에서 비워진다 |
| 1 이상 | 지정한 시간만큼 보존한다. 최솟값은 1시간이고, Producer SDK 한도 표의 최대 보존 기간은 10년이다 |

보존 기간 0은 "실시간으로 흘려보내기만 하는 스트림"이다. 아래에서 볼 HLS·GetClip은 모두 <strong>보존 기간이 0보다 커야</strong> 동작하고, 저장 모드 연결도 보존 기간이 0인 스트림에는 `NoDataRetentionException`으로 거절된다. 녹화가 목적이라면 보존 기간부터 정해야 한다. 농기계 작업 영상이라면 "사고 조사에 필요한 기간"(예: 7일=168시간)처럼 업무 요구에서 숫자를 끌어낸다. 보존 기간이 곧 저장 비용이기 때문이다.

### 프래그먼트: 스트림의 저장·조회 단위

스트림에 쌓이는 단위는 프레임이 아니라 <strong>프래그먼트</strong>다. 프래그먼트는 다른 프래그먼트에 의존하지 않고 홀로 디코딩할 수 있는 프레임 묶음이라서, 보통 키프레임(IDR)에서 시작한다. Producer SDK가 보내는 MKV에서는 클러스터 하나가 프래그먼트 하나가 되고, "클러스터 길이가 곧 프래그먼트 길이"다. 키프레임 간격 2초로 인코딩하면 프래그먼트도 2초가 된다.

KVS는 받은 프래그먼트마다 메타데이터를 붙인다.

- <strong>프래그먼트 번호</strong>: KVS가 부여하는 고유하고 증가하는 번호
- <strong>`server_timestamp`</strong>: KVS가 프래그먼트를 받기 시작한 시각
- <strong>`producer_timestamp`</strong>: 생산자가 그 프래그먼트를 녹화하기 시작한 시각. 요청 헤더의 시작 시각과 프래그먼트 타임코드로 계산한다

이 두 타임스탬프 덕분에 "트랙터가 14:03:20에 찍은 장면"(producer 기준)과 "클라우드가 14:03:21에 받은 장면"(server 기준)을 구분해서 조회할 수 있다. 디바이스 시계가 틀리면 producer 기준 조회가 엉뚱한 구간을 돌려주므로, 디바이스 시간 동기화([13장](/study/webrtc/13-native-webrtc))는 저장에서도 중요하다.

PutMedia 기준 프래그먼트 한도는 다음과 같다. 대부분 조정할 수 없는 값(hard)이라 인코더 설정을 이 안에 맞춰야 한다.

| 항목 | 한도 |
|---|---|
| 프래그먼트 길이 | 최소 1초, 최대 20초 |
| 프래그먼트 크기 | 최대 50 MB |
| 트랙 수 | 최대 3개(조정 가능) |
| 초당 프래그먼트 | 스트림당 최대 5개 |
| 데이터 속도 | 스트림당 12.5 MB/s(100 Mbps, 조정 가능) |

### PutMedia와 Producer SDK

스트림에 쓰는 데이터 플레인 API가 <strong>`PutMedia`</strong>다. 특징이 일반 REST API와 많이 다르다.

- 먼저 `GetDataEndpoint`(`APIName=PUT_MEDIA`)로 스트림별 엔드포인트를 받아 그쪽으로 보낸다.
- 프래그먼트마다 요청을 새로 여는 방식이 아니다. 한 HTTP 연결을 길게 열어 두고 chunked transfer encoding으로 MKV를 계속 흘려보낸다. 스트림당 동시 `PutMedia` 연결은 1개이고, 두 번째 연결은 `ConnectionLimitExceededException`을 받는다.
- 같은 연결로 프래그먼트마다 ACK가 돌아온다. `Buffering`(첫 바이트 수신) → `Received`(프래그먼트 전체 수신) → `Persisted`(보존 저장 완료) 순서이고, 문제가 있으면 `Error`(오류 코드 포함)가 온다. 데이터가 끊기면 `Idle`을 보내다가 마지막 수신 후 30초가 지나면 연결을 닫는다.
- 생산자는 `Persisted` ACK를 받기 전까지 그 프래그먼트를 버퍼에 들고 있어야 한다. 네트워크가 잠깐 끊겨도 녹화가 이어지는 이유가 이 버퍼와 재전송이다.

API 레퍼런스는 이 작업을 AWS SDK for Java에서만 쓸 수 있다고 적는다. 실무에서는 `PutMedia`를 직접 부르지 않고 <strong>Producer SDK</strong>(C++, Java/Android, 임베디드용 C)를 쓴다. Producer SDK가 MKV 패키징, 프래그먼트 버퍼(content store), ACK 처리, 연결 재수립과 토큰 갱신(SDK 한도 표상 최대 연결 시간 45분 안에서 교체)을 대신해 준다. 디바이스에서는 C++ Producer SDK에 들어 있는 GStreamer 플러그인 `kvssink`가 가장 손쉬운 경로다.

```bash
# 카메라 → H.264 하드웨어/소프트웨어 인코더 → kvssink(PutMedia)
# 자격증명은 환경변수(AWS_ACCESS_KEY_ID 등)나 IoT 인증서 속성으로 넘긴다(19장 참고)
gst-launch-1.0 -e v4l2src device=/dev/video0 \
  ! videoconvert ! video/x-raw,format=I420,width=1280,height=720,framerate=30/1 \
  ! x264enc bframes=0 key-int-max=60 bitrate=2000 tune=zerolatency \
  ! video/x-h264,stream-format=avc,alignment=au,profile=baseline \
  ! kvssink stream-name="tractor-001-rec" storage-size=128 aws-region="${AWS_REGION}"
```

`key-int-max=60`(30fps 기준 2초)이 곧 프래그먼트 길이를 정한다. `stream-format=avc`는 HLS 재생 요건(AVC 형식 codec private data)을 맞추기 위한 것이다. Jetson이나 Raspberry Pi라면 `x264enc` 자리에 하드웨어 인코더 엘리먼트를 넣는다([13장](/study/webrtc/13-native-webrtc)).

### 재생: HLS/DASH 세션 URL, GetClip, GetMedia

스트림을 읽는 길은 용도에 따라 갈린다. 모두 `GetDataEndpoint`로 API별 엔드포인트를 먼저 받는다(`GET_HLS_STREAMING_SESSION_URL`, `GET_DASH_STREAMING_SESSION_URL`, `GET_CLIP`, `GET_MEDIA`, `GET_IMAGES` 등).

| API | 결과물 | 주 용도 | 주요 한도 |
|---|---|---|---|
| `GetHLSStreamingSessionURL` / `GetDASHStreamingSessionURL` | 세션 토큰이 든 재생 URL | 브라우저·플레이어 시청 | 호출 25 TPS(스트림당), 세션 만료 300~43,200초 |
| `GetClip` | 일반 MP4 파일 | 사고 구간 다운로드·공유 | 앞에서부터 100 MB 또는 200 프래그먼트 |
| `GetMedia` | MKV 스트림(프래그먼트 메타데이터 포함) | 실시간 분석 파이프라인 | 스트림당 동시 연결 3개 |
| `GetImages` | 지정 간격 프레임 이미지 | 썸네일·이미지 분석 | 요청당 최대 100장 |

HLS 세션 URL에서 알아둘 점은 다음과 같다.

- <strong>`PlaybackMode`</strong>가 라이브와 온디맨드를 가른다. `LIVE`는 최신 프래그먼트가 들어올 때마다 플레이리스트가 갱신되고(플레이어는 1초 간격으로 다시 받는 것이 권장), `ON_DEMAND`는 요청 구간의 프래그먼트 전체가 담긴 고정 플레이리스트를 한 번만 받는다. `LIVE_REPLAY`는 과거 시각부터 시작해 라이브처럼 이어 붙이는 모드라서 "이벤트 감지 시점부터 재생 + 이후 라이브"에 맞다.
- `LIVE`는 최근 30초 안에 프래그먼트가 없으면 `ResourceNotFoundException`을 낸다. 디바이스가 꺼진 채널의 "라이브 보기" 버튼이 404를 내는 이유다.
- 반환 URL에는 암호화된 세션 토큰이 들어 있다. 문서는 이 토큰을 AWS 자격증명처럼 보호하라고 하고, 한 URL을 여러 플레이어가 공유하면 스로틀링될 수 있다고 한다. 백엔드가 요청마다 짧은 `Expires`로 새로 발급해 주는 구조가 맞다.
- 비디오는 H.264(AVC) 또는 H.265(HEVC) codec private data, 오디오는 AAC여야 한다. 재생 구간 중간에 트랙 구성이 바뀌면(비디오만 → 비디오+오디오) 재생이 실패한다.
- `ContainerFormat` 기본값은 `FRAGMENTED_MP4`다. `MPEG_TS`는 구형 플레이어 호환용이고 대역폭·비용이 5~25% 더 든다.
- 라이브 플레이리스트의 프래그먼트 수(`MaxMediaPlaylistFragmentResults`)는 기본 5, 권장 3~10이다. 많을수록 끊김이 줄고 지연이 늘어난다. HLS 지연은 "프래그먼트 길이 × 플레이어가 쌓는 프래그먼트 수"에 비례하므로 보통 수 초 단위다. WebRTC의 1초 미만과는 급이 다르다.

HLS 세션 수 자체에는 한도가 없다. 대신 스트림마다 초당 <strong>프래그먼트 메타데이터 10,000점, 프래그먼트 미디어 500점</strong> 할당량을 여러 API가 나눠 쓴다. 문서 예시로 1초 프래그먼트·오디오+비디오·`MaxMediaPlaylistFragmentResults=5`인 라이브 HLS는 약 250개 세션까지 버틴다. 농기계 영상을 수백 명이 동시에 볼 일은 드물지만, 대시보드가 썸네일용으로 `GetImages`를 남발하면 같은 할당량을 깎아 먹는다는 점은 기억해 둔다.

백엔드에서 녹화 구간 재생 URL을 발급하는 코드는 다음 정도다.

```js
// Node.js (AWS SDK v3) — 운영자가 요청한 구간의 ON_DEMAND HLS URL 발급
import { KinesisVideoClient, GetDataEndpointCommand } from '@aws-sdk/client-kinesis-video';
import {
  KinesisVideoArchivedMediaClient,
  GetHLSStreamingSessionURLCommand,
} from '@aws-sdk/client-kinesis-video-archived-media';

const region = process.env.AWS_REGION;
const kv = new KinesisVideoClient({ region });

export async function issueReplayUrl(streamName, start, end) {
  const { DataEndpoint } = await kv.send(new GetDataEndpointCommand({
    StreamName: streamName,
    APIName: 'GET_HLS_STREAMING_SESSION_URL',
  }));
  const media = new KinesisVideoArchivedMediaClient({ region, endpoint: DataEndpoint });
  const { HLSStreamingSessionURL } = await media.send(new GetHLSStreamingSessionURLCommand({
    StreamName: streamName,
    PlaybackMode: 'ON_DEMAND',
    HLSFragmentSelector: {
      FragmentSelectorType: 'PRODUCER_TIMESTAMP',
      TimestampRange: { StartTimestamp: start, EndTimestamp: end },
    },
    ContainerFormat: 'FRAGMENTED_MP4',
    DiscontinuityMode: 'ON_DISCONTINUITY',
    Expires: 900, // 15분. 토큰이 든 URL이므로 짧게
  }));
  return HLSStreamingSessionURL; // 브라우저는 hls.js 또는 Safari 네이티브로 재생
}
```

CLI로는 같은 흐름을 이렇게 확인한다.

```bash
export AWS_REGION=us-west-2   # 예시 리전

# 1) 7일 보존 스트림 생성
aws kinesisvideo create-stream --stream-name tractor-001-rec \
  --data-retention-in-hours 168 --media-type "video/h264"

# 2) HLS 세션 URL (라이브)
EP=$(aws kinesisvideo get-data-endpoint --stream-name tractor-001-rec \
  --api-name GET_HLS_STREAMING_SESSION_URL --query DataEndpoint --output text)
aws kinesis-video-archived-media get-hls-streaming-session-url \
  --endpoint-url "$EP" --stream-name tractor-001-rec --playback-mode LIVE

# 3) 사고 구간 MP4 클립 (마지막 인자가 저장할 파일)
EP=$(aws kinesisvideo get-data-endpoint --stream-name tractor-001-rec \
  --api-name GET_CLIP --query DataEndpoint --output text)
aws kinesis-video-archived-media get-clip --endpoint-url "$EP" \
  --stream-name tractor-001-rec \
  --clip-fragment-selector 'FragmentSelectorType=SERVER_TIMESTAMP,TimestampRange={StartTimestamp=2026-10-19T05:00:00Z,EndTimestamp=2026-10-19T05:02:00Z}' \
  incident.mp4
```

정리하면, 같은 스트림 하나로 라이브(HLS `LIVE`)와 온디맨드(HLS/DASH `ON_DEMAND`, `GetClip`)를 모두 처리한다. 차이는 지연이다.

| 구분 | 라이브(HLS/DASH `LIVE`) | 온디맨드(`ON_DEMAND`, `GetClip`) | WebRTC(P2P 또는 저장 세션) |
|---|---|---|---|
| 지연 | 수 초 | 해당 없음(과거 구간) | 1초 미만 |
| 시청자 규모 | 스트림 할당량 범위에서 다수 | 다수 | P2P 10명(조정 가능), 저장 세션 3명 |
| 양방향 | 불가 | 불가 | 가능 |
| 원격 조작에 쓸 수 있나 | 아니다 | 아니다 | 그렇다 |

## 2. 저장 모드의 구조: 채널을 스트림에 연결한다

KVS WebRTC의 <strong>WebRTC ingestion and storage</strong> 기능(이 스터디에서는 "저장 모드")은 WebRTC로 들어온 미디어를 위 스트림에 바로 저장한다. 문서는 이를 "sub 1-second latency 스트리밍과 클라우드 수집·저장을 함께" 제공하는 기능이라고 표현한다. 방법은 시그널링 채널 하나를 스트림 하나에 연결하는 것이다.

여기서 가장 중요한 사실은 <strong>연결을 켜는 순간 토폴로지가 바뀐다</strong>는 점이다. `UpdateMediaStorageConfiguration` API 문서 원문은 이렇다.

> If StorageStatus is enabled, direct peer-to-peer (master-viewer) connections no longer occur. Peers connect directly to the storage session.

![기본 모드와 저장 모드의 미디어 경로 비교. 왼쪽 기본 모드에서는 시그널링 채널이 SDP와 ICE만 중계하고, 디바이스(master)가 viewer 1·2·3에게 각각 SRTP를 직접 보내 업링크가 viewer 수에 비례한다. 오른쪽 저장 모드에서는 디바이스가 H.264+Opus를 AWS의 storage 세션으로 한 번만 올리고, storage 세션이 최대 3명의 viewer에게 영상을 복제하고 오디오를 믹싱해 보내며, 동시에 Video Stream에 H.264+AAC로 저장해 HLS/DASH 다수 시청으로 이어진다](/images/study-webrtc/21-storage-topology-light.png)
![기본 모드와 저장 모드의 미디어 경로 비교. 왼쪽 기본 모드에서는 시그널링 채널이 SDP와 ICE만 중계하고, 디바이스(master)가 viewer 1·2·3에게 각각 SRTP를 직접 보내 업링크가 viewer 수에 비례한다. 오른쪽 저장 모드에서는 디바이스가 H.264+Opus를 AWS의 storage 세션으로 한 번만 올리고, storage 세션이 최대 3명의 viewer에게 영상을 복제하고 오디오를 믹싱해 보내며, 동시에 Video Stream에 H.264+AAC로 저장해 HLS/DASH 다수 시청으로 이어진다](/images/study-webrtc/21-storage-topology-dark.png)

[16장](/study/webrtc/16-aws-landscape)과 [17장](/study/webrtc/17-kvs-architecture)에서 "KVS WebRTC는 SFU가 아니라 P2P"라고 강조했다. 그 설명은 기본 모드에 대해서만 맞다. 저장 모드에서는 AWS 네트워크 안의 <strong>storage 세션</strong>이 미디어 경로 한가운데에 들어온다. `JoinStorageSessionAsViewer` 문서 표현으로는 storage 세션이 "mixing, duplicating, and routing the media"를 맡는다. 즉 저장 모드는 한도가 매우 작은(viewer 3명) 관리형 미디어 서버처럼 동작한다. 그 대가로 다음 제약이 한꺼번에 붙는다.

| 항목 | 기본 모드(P2P) | 저장 모드 |
|---|---|---|
| 미디어 경로 | master ↔ viewer 직결, 안 되면 TURN relay | 모든 피어 ↔ storage 세션 |
| viewer 수 | 채널당 10(조정 가능) | 세션당 3(조정 불가) |
| viewer 송신 | 비디오·오디오 모두 가능 | 오디오(Opus)만, 선택 |
| 코덱 | 협상으로 결정(VP8/H.264/Opus 등) | 비디오 H.264, 오디오 Opus |
| 세션 수명 | 시그널링 연결 최대 1시간 | storage 세션 최대 1시간, idle 3분 |
| offer를 보내는 쪽 | viewer | storage 세션 |
| 디바이스 업링크 | viewer 수 × 비트레이트 | 1회 |

### 연결 전 준비

1. <strong>보존 기간이 0보다 큰 스트림</strong>을 만든다. 0이면 연결 단계에서 `NoDataRetentionException`이 난다.
2. 채널 하나에는 스트림 하나가 대응한다. 이미 다른 리소스에 매핑된 스트림이나 채널을 다시 쓰면 `ResourceInUseException`이 난다. 이때는 `DescribeMediaStorageConfiguration`(채널 → 스트림)과 `DescribeMappedResourceConfiguration`(스트림 → 채널)으로 현재 매핑을 확인하라고 문서가 안내한다.
3. 할당량을 확인한다. <strong>저장 설정이 켜진 채널(Media Storage Channels)은 계정당 기본 100개</strong>(조정 가능)다. 농기계 300대 전부에 저장 모드를 켜려면 증설 요청부터 해야 한다.

### CLI로 연결하고 확인하기

```bash
export AWS_REGION=us-west-2   # 예시 리전. 저장 모드 지원 리전은 아래 주의 참고
CHANNEL_ARN=$(aws kinesisvideo describe-signaling-channel --channel-name tractor-001 \
  --query ChannelInfo.ChannelARN --output text)
STREAM_ARN=$(aws kinesisvideo describe-stream --stream-name tractor-001-rec \
  --query StreamInfo.StreamARN --output text)

# 채널 → 스트림 연결 (이 순간부터 이 채널에서 P2P는 일어나지 않는다)
aws kinesisvideo update-media-storage-configuration \
  --channel-arn "$CHANNEL_ARN" \
  --media-storage-configuration StreamARN="$STREAM_ARN",Status=ENABLED

# 확인
aws kinesisvideo describe-media-storage-configuration --channel-arn "$CHANNEL_ARN"
# {
#     "MediaStorageConfiguration": {
#         "StreamARN": "arn:aws:kinesisvideo:us-west-2:123456789012:stream/tractor-001-rec/1760000000000",
#         "Status": "ENABLED"
#     }
# }

# 스트림 쪽에서 역으로 어느 채널에 매핑됐는지 확인
aws kinesisvideo describe-mapped-resource-configuration --stream-arn "$STREAM_ARN"

# 다시 P2P로 되돌리기
aws kinesisvideo update-media-storage-configuration \
  --channel-arn "$CHANNEL_ARN" \
  --media-storage-configuration Status=DISABLED
```

`UpdateMediaStorageConfiguration`은 계정 10 TPS, 리소스당 5 TPS(조정 불가)다. 디바이스 등록 배치에서 수백 개 채널을 한꺼번에 바꾸려면 속도 제한을 걸어야 한다.

::: warning 모드 전환은 디바이스 쪽 동작까지 바꾼다
저장 모드는 서버 설정 하나로 끝나지 않는다. 디바이스는 연결할 때 채널이 저장 모드인지 보고 `JoinStorageSession`을 호출해야 하고, 브라우저 viewer도 offer를 보내는 대신 받는 쪽으로 동작이 바뀐다(3절, 4절). KVS C SDK 샘플은 연결(fetch) 때마다 `DescribeMediaStorageConfiguration`을 호출해 저장 상태를 확인하고, 상태가 바뀌면 엔드포인트 캐시를 무효화한다(`SIGNALING_API_CALL_CACHE_TYPE_FILE_EXCEPT_DESCRIBE_MEDIA` 정책). 따라서 운영 중에 모드를 바꾸면 디바이스가 재연결해야 반영된다고 보는 것이 안전하다.
:::

::: warning 서울 리전 지원 여부
WebRTC 리전 표에는 서울(ap-northeast-2)이 있지만, ingestion만 따로 정리한 리전 표는 문서에 없다. Price List API의 서울 항목에 `APN2-WebRTCRecording`·`APN2-WebRTCViewer` SKU가 있어 서울에서도 과금 항목이 존재한다는 간접 근거는 있으나, 공식 문서에서 서울의 저장 모드 지원을 명시한 문장은 확인하지 못했다(2026-10-19 기준). 도입 전에 대상 리전 콘솔에서 직접 확인한다.
:::

## 3. JoinStorageSession: master가 저장 세션에 붙는 흐름

저장 모드에서 디바이스(master)가 하는 일은 기본 모드와 비슷하면서 순서가 다르다. 핵심 API는 webrtc-storage API(버전 2018-05-10)의 <strong>`JoinStorageSession`</strong>이다.

![JoinStorageSession과 JoinStorageSessionAsViewer 시퀀스. ① master 참여 단계에서 디바이스는 시그널링 WSS 엔드포인트에 ConnectAsMaster로 붙고 WEBRTC 엔드포인트에 JoinStorageSession(channelArn)을 호출한다. 그러면 storage 세션이 시그널링을 거쳐 senderClientId 없는 SDP_OFFER를 보내고, 디바이스는 correlationId를 붙인 SDP_ANSWER로 답한 뒤 ICE 후보를 trickle로 교환한다(storage 쪽 후보는 relay만). 이어 디바이스가 H.264 sendonly와 Opus를 SRTP로 보내면 storage 세션이 H.264+AAC로 Video Stream에 저장한다. ② viewer 참여 단계에서 운영자 브라우저는 ConnectAsViewer(clientId)와 JoinStorageSessionAsViewer(channelArn, clientId)를 호출하고, storage 세션이 보낸 SDP_OFFER에 video recvonly answer로 답한 뒤 영상과 믹싱 오디오를 받고 선택적으로 Opus 오디오를 보낸다. ③ 세션이 1시간 한도에 닿아 종료되면 디바이스는 시그널링을 재연결하고 JoinStorageSession을 다시 호출한다](/images/study-webrtc/21-join-storage-sequence-light.png)
![JoinStorageSession과 JoinStorageSessionAsViewer 시퀀스. ① master 참여 단계에서 디바이스는 시그널링 WSS 엔드포인트에 ConnectAsMaster로 붙고 WEBRTC 엔드포인트에 JoinStorageSession(channelArn)을 호출한다. 그러면 storage 세션이 시그널링을 거쳐 senderClientId 없는 SDP_OFFER를 보내고, 디바이스는 correlationId를 붙인 SDP_ANSWER로 답한 뒤 ICE 후보를 trickle로 교환한다(storage 쪽 후보는 relay만). 이어 디바이스가 H.264 sendonly와 Opus를 SRTP로 보내면 storage 세션이 H.264+AAC로 Video Stream에 저장한다. ② viewer 참여 단계에서 운영자 브라우저는 ConnectAsViewer(clientId)와 JoinStorageSessionAsViewer(channelArn, clientId)를 호출하고, storage 세션이 보낸 SDP_OFFER에 video recvonly answer로 답한 뒤 영상과 믹싱 오디오를 받고 선택적으로 Opus 오디오를 보낸다. ③ 세션이 1시간 한도에 닿아 종료되면 디바이스는 시그널링을 재연결하고 JoinStorageSession을 다시 호출한다](/images/study-webrtc/21-join-storage-sequence-dark.png)

### 단계별로 보기

1. <strong>엔드포인트 받기</strong>: `GetSignalingChannelEndpoint`에 `Protocols`로 `WSS`·`HTTPS`와 함께 <strong>`WEBRTC`</strong>를 요청한다. `WEBRTC` 엔드포인트가 `JoinStorageSession`을 보낼 곳이다. 저장 설정이 없는 채널에 `WEBRTC`를 요청하면 `InvalidArgumentException`이 난다.

   ```bash
   aws kinesisvideo get-signaling-channel-endpoint --channel-arn "$CHANNEL_ARN" \
     --single-master-channel-endpoint-configuration Protocols=WSS,HTTPS,WEBRTC,Role=MASTER
   ```

2. <strong>시그널링 연결</strong>: 기본 모드와 똑같이 WSS 엔드포인트에 `ConnectAsMaster`로 붙는다. storage 세션의 offer와 ICE 후보도 이 시그널링 채널로 온다.
3. <strong>`JoinStorageSession` 호출</strong>: `WEBRTC` 엔드포인트로 `POST /joinStorageSession`, 본문은 `{"channelArn": "..."}`이다. 필드 이름이 소문자 `c`로 시작한다는 점을 문서가 따로 강조한다(컨트롤 플레인 API의 `ChannelARN`과 다르다). 성공하면 본문 없는 200이 온다.

   ```bash
   WEBRTC_EP=https://...   # 1번 응답의 WEBRTC ResourceEndpoint
   aws kinesis-video-webrtc-storage join-storage-session \
     --endpoint-url "$WEBRTC_EP" --channel-arn "$CHANNEL_ARN"
   ```

4. <strong>storage 세션이 offer를 보낸다</strong>: 호출 직후 storage 세션이 시그널링 채널을 통해 master에게 SDP offer를 보낸다. master는 answer를 보내고 ICE 후보를 교환한다.
5. <strong>미디어 송출과 저장</strong>: 연결이 서면 master가 보내는 H.264 + Opus를 storage 세션이 받아 스트림에 H.264 + AAC로 저장한다. 이후 그 스트림은 1절의 HLS/DASH, `GetImages` 등으로 그대로 소비할 수 있다.

### 누가 offer를 보내는가: controlling 역할의 이동

[04장](/study/webrtc/04-sdp-jsep)과 [06장](/study/webrtc/06-ice)에서 offer를 보낸 쪽이 ICE controlling 역할을 맡는다고 했다. KVS 기본 모드에서는 viewer가 offer를 보내고 master는 answer만 한다. 저장 모드에서는 <strong>storage 세션이 controlling peer</strong>가 된다. 트러블슈팅 문서의 정리는 이렇다.

- master는 원래도 controlled였으므로 그대로 controlled다.
- viewer는 controlling에서 <strong>controlled로 바뀐다</strong>. 즉 브라우저 viewer 코드가 offer를 만드는 대신 받은 offer에 answer해야 한다.
- `JoinStorageSession`이든 `JoinStorageSessionAsViewer`든, 호출한 쪽은 모두 SDP answer로 응답하고 storage 세션과 ICE 후보를 교환해야 한다.

기존 P2P용 master 코드를 거의 그대로 쓸 수 있는 이유가 여기에 있다. offer를 받아 answer하는 흐름이 같기 때문이다. 다만 세부 차이가 몇 가지 있다.

| 차이 | 내용 | 코드에서 할 일 |
|---|---|---|
| `senderClientId` 없음 | storage 세션이 보낸 시그널링 메시지에는 `senderClientId` 필드가 없다. P2P master는 항상 이 값을 받는다 | `senderClientId`로 PeerConnection을 찾는 맵이 null 키를 처리하게 한다 |
| 후보에 `sdpMid` 없음 | storage 세션의 ICE 후보에는 `sdpMid` 속성이 없다 | 문자열을 후보 객체로 바꾸는 로직이 `sdpMid` 부재를 견디는지 점검한다 |
| 후보가 offer보다 먼저 올 수 있음 | 시그널링 전달이 비동기라 순서가 뒤바뀔 수 있다 | 대기열에 쌓았다가 offer를 처리한 뒤 `addIceCandidate`로 일괄 추가한다 |
| relay 후보만 옴 | storage 세션은 AWS 네트워크 안에 있어 `relay`(TURN) 후보만 보낸다. 참가자 쪽 지명(nominated) 후보는 `srflx` 또는 `relay`, 원격 후보는 항상 `relay`다 | 디바이스에서 TURN(UDP/TCP 443)으로 나가는 길이 열려 있어야 한다 |
| host 후보 불필요 | 연결 시간을 줄이려면 `host` 후보를 보내지 말라고 권장한다. Trickle ICE는 필수다 | `onicecandidate`에서 `host` 타입을 걸러 낸다 |
| answer 거절 피드백 | answer에 `correlationId`를 넣으면 거절 시 `statusResponse`가 온다 | 항상 `correlationId`를 넣고 `statusResponse`를 로그로 남긴다 |

answer가 코덱이나 방향 때문에 거절되면 다음 같은 `statusResponse`가 온다(문서 예시).

```json
{
  "correlationId": "1700186220273",
  "errorType": "InvalidArgumentException",
  "statusCode": "400",
  "success": false
}
```

이 응답은 `correlationId`를 넣었을 때만 받을 수 있다. 넣지 않으면 연결이 조용히 안 되는 것처럼 보인다.

### 세션 규칙과 한도

- <strong>세션당 비디오 생산 장치는 1개</strong>다. 둘 이상이 `JoinStorageSession`을 호출하면 가장 최근 요청이 이긴다. master 중복 접속과 같은 규칙이므로, 같은 채널 이름을 쓰는 디바이스 두 대가 서로를 밀어내는 사고에 주의한다.
- `JoinStorageSession`은 <strong>멱등이 아니다</strong>. 재시도도 새 호출로 치고, 호출할 때마다 offer가 한 번씩 온다. 타임아웃 재시도를 공격적으로 걸면 offer가 겹쳐 온다.
- 할당량: 호출 빈도는 계정 50 TPS·채널 2 TPS, <strong>세션 최대 1시간(조정 불가)</strong>, idle timeout 3분(조정 불가), 비트레이트 1 Mbps(조정 가능).
- 비트레이트 1 Mbps는 기본값 기준으로 꽤 빡빡하다. 720p 30fps를 H.264로 1 Mbps 안에 맞추거나, 더 필요하면 Service Quotas에서 증설을 요청한다.
- S3 이미지 전달과 알림(notifications)은 저장 모드에서 지원하지 않는다. `GetImages` 같은 기존 기능은 쓸 수 있다.

1시간 한도 처리는 KVS C SDK 샘플 코드의 주석이 잘 보여 준다. 저장 모드(`useMediaStorage = TRUE`)에서 세션이 정리되면 시그널링을 끊고 다시 연결하며, 이 재연결이 `JoinStorageSession` 호출로 이어진다.

```c
// amazon-kinesis-video-streams-webrtc-sdk-c samples/common/Common.c 발췌(요약)
// 저장 모드 샘플은 채널 설정에서 이 플래그를 켠다
pSampleConfiguration->channelInfo.useMediaStorage = TRUE;

// 세션 정리 루프 안
if (sessionFreed && pSampleConfiguration->channelInfo.useMediaStorage && ...) {
    // In the WebRTC Media Storage Ingestion Case the backend will terminate the session after
    // 1 hour.  The SDK needs to make a new JoinSession Call in order to receive a new offer ...
    CHK_STATUS(signalingClientDisconnectSync(pSampleConfiguration->signalingClientHandle));
    CHK_STATUS(signalingClientFetchSync(pSampleConfiguration->signalingClientHandle));
    CHK_STATUS(signalingClientConnectSync(pSampleConfiguration->signalingClientHandle)); // → JoinSession
}
```

같은 파일에는 "WebRTC ingestion 모드는 현재 재협상(re-negotiation)을 지원하지 않는다"는 주석도 있다. 저장 세션에서 두 번째 offer는 재협상이 아니라 새 ICE로 다시 붙는 경로이고 새 PeerConnection을 기대한다. 그래서 해상도를 바꾸려고 트랙을 교체하는 식의 재협상 로직은 저장 모드에서 쓰지 않는 편이 안전하다.

샘플은 C SDK에 이미 들어 있다. `kvsWebrtcStorageAudioVideoMaster`, `kvsWebrtcStorageVideoOnlyMaster`와 각각의 GStreamer 버전(`testsrc`, `devicesrc`, `rtspsrc` 입력)이다. 기존 RTSP 카메라를 저장 모드로 올리는 가장 빠른 길은 `kvsWebrtcStorage…GstSample <channelName> rtspsrc "rtsp://..."`다. ingestion 문서의 SDK 링크는 아직 `Release-WebRTC-Streams-Ingestion-Public-Preview` 브랜치를 가리키지만 C SDK `main` README에는 storage 기능과 샘플이 들어가 있으니 `main`(v1.20.0, 2026-08 릴리스 기준)을 기준으로 삼는다.

## 4. 저장 세션의 viewer: JoinStorageSessionAsViewer

저장 모드에서 운영자 브라우저는 <strong>`JoinStorageSessionAsViewer`</strong>로 세션에 참여한다. 요청 본문은 `{ "channelArn": "...", "clientId": "..." }`다.

### 문서가 정한 동작

- viewer는 녹화 에이전트(storage 세션)를 거쳐 master의 <strong>실시간 영상</strong>을 받고, 같은 경로로 <strong>양방향 오디오</strong>에 참여한다.
- viewer가 보낸 오디오는 master를 포함한 다른 모든 피어에게 전달되고, 스트림에 저장되는 미디어에도 섞인다. "운영자 음성 지시가 녹화에 남는다"는 뜻이라, 감사 기록으로는 장점이고 개인정보 측면에서는 고지 대상이다.
- viewer는 <strong>비디오 트랙을 보낼 수 없다</strong>. 오디오(Opus)를 선택적으로 보내거나 아무 트랙도 보내지 않는다.
- viewer는 master가 아니라 storage 세션에 직접 붙는다. storage 세션이 미디어를 믹싱·복제·라우팅한다.
- master가 없으면 viewer끼리는 서로의 소리를 들을 수 없다. viewer 오디오는 master가 storage 세션에 연결돼 있는 동안에만 저장된다.

### 한도

| 항목 | 값 |
|---|---|
| 세션당 최대 viewer | 3 (조정 불가) |
| master 없이 viewer가 머무를 수 있는 시간 | 최대 3분 |
| viewer 세션 최대 시간 | 1시간 (조정 불가) |
| viewer idle timeout | 1분 (조정 불가) |
| 끊긴 viewer의 할당량 점유 | 1분. 그 안에 <strong>같은 Client ID</strong>로 재참여하면 추가 할당량을 쓰지 않는다 |

마지막 줄이 실무에서 중요하다. 브라우저 탭을 새로 고칠 때마다 `clientId`를 랜덤으로 만들면, 새로 고침 한 번에 1분 동안 자리 하나가 사라진다. 세 명 한도에서 두 번만 새로 고쳐도 다른 운영자가 못 들어온다. `clientId`는 "운영자 ID + 디바이스 ID"처럼 <strong>사람·탭 단위로 안정적인 값</strong>으로 만들어야 한다. Client ID 설계 원칙은 [18장](/study/webrtc/18-kvs-signaling-api)에서 다뤘다.

### 브라우저 viewer 코드

기본 모드 viewer 코드([20장](/study/webrtc/20-kvs-viewer-backend))와 비교하면 세 군데가 다르다. `WEBRTC` 엔드포인트를 추가로 받고, 시그널링이 열리면 offer 대신 `JoinStorageSessionAsViewer`를 호출하며, `sdpOffer` 이벤트에서 answer한다.

```js
import { KinesisVideoClient, GetSignalingChannelEndpointCommand } from '@aws-sdk/client-kinesis-video';
import { KinesisVideoSignalingClient, GetIceServerConfigCommand } from '@aws-sdk/client-kinesis-video-signaling';
import {
  KinesisVideoWebRTCStorageClient,
  JoinStorageSessionAsViewerCommand,
} from '@aws-sdk/client-kinesis-video-webrtc-storage';
import { SignalingClient, Role } from 'amazon-kinesis-video-streams-webrtc';

// credentials: 20장의 백엔드가 발급한, 이 채널 ARN으로 좁힌 임시 자격증명
export async function joinStorageAsViewer({ region, channelARN, clientId, credentials, videoEl }) {
  const kv = new KinesisVideoClient({ region, credentials });
  const { ResourceEndpointList } = await kv.send(new GetSignalingChannelEndpointCommand({
    ChannelARN: channelARN,
    SingleMasterChannelEndpointConfiguration: {
      Protocols: ['WSS', 'HTTPS', 'WEBRTC'],
      Role: 'VIEWER',
    },
  }));
  const ep = Object.fromEntries(ResourceEndpointList.map((e) => [e.Protocol, e.ResourceEndpoint]));

  const sig = new KinesisVideoSignalingClient({ region, credentials, endpoint: ep.HTTPS });
  const { IceServerList } = await sig.send(new GetIceServerConfigCommand({ ChannelARN: channelARN, ClientId: clientId }));
  const iceServers = [
    { urls: `stun:stun.kinesisvideo.${region}.amazonaws.com:443` },
    ...IceServerList.map((s) => ({ urls: s.Uris, username: s.Username, credential: s.Password })),
  ];

  const pc = new RTCPeerConnection({ iceServers });
  pc.addTransceiver('video', { direction: 'recvonly' });      // viewer는 비디오 송신 불가
  const mic = await navigator.mediaDevices.getUserMedia({ audio: true }).catch(() => null);
  if (mic) pc.addTransceiver(mic.getAudioTracks()[0], { direction: 'sendrecv' }); // Opus, 선택
  else pc.addTransceiver('audio', { direction: 'recvonly' });
  pc.ontrack = (e) => { videoEl.srcObject = e.streams[0] ?? new MediaStream([e.track]); };

  const signaling = new SignalingClient({
    channelARN, channelEndpoint: ep.WSS, clientId, role: Role.VIEWER, region, credentials,
    systemClockOffset: kv.config.systemClockOffset,
  });

  const pending = [];          // offer보다 먼저 도착한 후보 대기열
  let remoteSet = false;

  signaling.on('open', async () => {
    // P2P처럼 offer를 만들지 않는다. storage 세션에게 "offer를 보내라"고 요청한다
    const storage = new KinesisVideoWebRTCStorageClient({ region, credentials, endpoint: ep.WEBRTC });
    await storage.send(new JoinStorageSessionAsViewerCommand({ channelArn: channelARN, clientId }));
  });

  signaling.on('sdpOffer', async (offer) => {   // storage 세션이 보낸 offer (senderClientId 없음)
    await pc.setRemoteDescription(offer);
    remoteSet = true;
    for (const c of pending.splice(0)) await pc.addIceCandidate(c);
    await pc.setLocalDescription(await pc.createAnswer());
    signaling.sendSdpAnswer(pc.localDescription, undefined, `answer-${Date.now()}`);
  });

  signaling.on('iceCandidate', async (candidate) => {
    if (!remoteSet) pending.push(candidate);
    else await pc.addIceCandidate(candidate);
  });

  pc.onicecandidate = ({ candidate }) => {
    if (!candidate || candidate.type === 'host') return;   // host 후보는 보내지 않는다(권장)
    signaling.sendIceCandidate(candidate, undefined, `ice-${Date.now()}`);
  };

  signaling.on('statusResponse', (s) => console.warn('storage session rejected', s));
  signaling.open();
  return { pc, signaling };
}
```

storage 세션에서 온 ICE 후보에는 `sdpMid`가 없다는 점을 다시 확인한다. 사용하는 SDK 버전이 후보 문자열을 `RTCIceCandidate`로 바꾸는 과정에서 이 부재를 어떻게 처리하는지 확인하고, 문제가 있으면 이 지점에 보정 로직을 넣는다. 공식 샘플은 "PeerConnection 맵에 아직 연결이 없으면 대기열에 넣고, offer를 받아 PeerConnection을 만든 뒤 대기열을 비운다"는 방식을 쓴다. 위 코드의 `pending`이 그 역할이다.

viewer answer의 방향도 정해져 있다. H.264 비디오는 `recvonly`, Opus 오디오는 `recvonly` 또는 `sendrecv`여야 한다. master는 H.264 `sendonly`, Opus `sendonly` 또는 `sendrecv`다. 조건이 맞지 않으면 `correlationId`를 넣은 경우 400 `statusResponse`가 온다.

## 5. 코덱과 미디어 제약

저장 모드는 받은 미디어를 스트림 포맷으로 다시 포장해야 하므로 협상 여지가 거의 없다. `JoinStorageSession` 문서 기준 제약을 한 표에 모으면 다음과 같다.

| 항목 | 요구 사항 |
|---|---|
| 비디오 코덱 | H.264 |
| 지원 H.264 프로파일 | constrained-baseline, baseline, main, high, constrained-high, progressive-high |
| 최대 해상도 | SQFHD(1920×1920) |
| 오디오 코덱 | Opus |
| 저장 결과 | H.264 비디오 + AAC 오디오(오디오는 서버가 변환) |
| viewer 송신 | 오디오(Opus)만, 선택 |
| 비트레이트 | 세션 1 Mbps(조정 가능) |
| 트랙 구성 | 문서상 "audio and video tracks are currently required" |

설계에 영향을 주는 지점을 짚어 본다.

- <strong>VP8·H.265 디바이스는 그대로 못 쓴다.</strong> KVS C SDK는 P2P에서 VP8과 H.265(샘플 인자 기준)도 다루지만, 저장 모드는 H.264만 받는다. 트러블슈팅 문서가 거절 원인을 설명하며 Opus + VP8 answer 예시를 보여 주는 것도 이 때문이다. 4K 카메라라면 1920×1920 이하로 내려 인코딩해야 한다.
- <strong>프로파일은 넓게 허용된다.</strong> Jetson 하드웨어 인코더의 high 프로파일 출력도 목록 안에 있다. 반대로 브라우저 viewer가 받는 영상도 H.264이므로, H.264 디코딩을 못 하는 환경이 viewer로 들어오는 경우는 고려하지 않아도 된다.
- <strong>오디오가 필수인지는 단정하기 어렵다.</strong> API 문서는 "Both audio and video tracks are currently required for WebRTC ingestion"이라고 적는다. 그런데 C SDK `main` 브랜치에는 `kvsWebrtcStorageVideoOnlyMaster` 샘플이 있고, 이 샘플 소스는 비디오를 `sendonly`로 보내면서 오디오 트랜시버를 `recvonly`로 붙인다(`addSendOnlyVideoRecvOnlyAudioTransceivers`). 즉 SDP에 오디오 m-line은 있지만 디바이스가 오디오를 보내지는 않는 구성이다. 한편 트러블슈팅 문서는 master의 Opus 방향을 `sendonly` 또는 `sendrecv`로 적는다. 문서끼리 맞지 않으므로, 마이크 없는 카메라라면 대상 리전에서 VideoOnly 샘플로 실제 저장·재생까지 검증하고 나서 결정한다. 확실히 하려면 무음 Opus 트랙을 보내는 방법도 있다.
- <strong>저장 결과는 HLS 요건을 자동으로 맞춘다.</strong> 1절에서 HLS는 H.264(AVC) + AAC를 요구한다고 했는데, 저장 모드의 결과물이 정확히 그 조합이다. Opus → AAC 변환을 디바이스가 하지 않아도 된다는 점은 Producer SDK 경로 대비 장점이다. Producer SDK 경로에서는 디바이스가 AAC로 인코딩하거나, 오디오를 빼야 HLS로 재생된다.
- <strong>B-프레임은 끈다.</strong> WebRTC 경로 전반의 원칙([08장](/study/webrtc/08-rtp-codecs))대로 저지연 인코딩에서는 B-프레임을 쓰지 않는다.

## 6. 녹화 + 실시간 시청 설계 비교

이제 "농기계 영상을 운영자가 실시간으로 보고, 동시에 녹화도 남긴다"는 요구를 세 가지 방식으로 비교한다.

- <strong>A. P2P 시청 + 병행 녹화</strong>: 실시간 시청은 기본 모드 KVS WebRTC(P2P)로 하고, 같은 인코더 출력을 `tee`로 나눠 Producer SDK(`kvssink`)로 별도 스트림에 `PutMedia`한다.
- <strong>B. 저장 모드</strong>: 이 장에서 다룬 WebRTC ingestion. 한 번 올리면 storage 세션이 viewer 분배와 저장을 함께 한다.
- <strong>C. Producer SDK PutMedia만</strong>: WebRTC 없이 스트림에만 올리고, 시청은 HLS/DASH `LIVE`로 한다.

| 기준 | A. P2P 시청 + 병행 PutMedia | B. 저장 모드 | C. PutMedia만 |
|---|---|---|---|
| 실시간 지연 | 1초 미만(P2P) | 1초 미만(저장 세션 경유) | 수 초(HLS/DASH) |
| 실시간 시청자 | 채널당 10(조정 가능) | 세션당 3(조정 불가) + HLS 다수 | HLS로 다수(스트림 할당량 범위) |
| 디바이스 업링크 | PutMedia 1회 + P2P viewer 수만큼 | 1회 | 1회 |
| 양방향 오디오 | P2P로 가능 | storage 세션이 믹싱 | 불가 |
| DataChannel(원격 제어) | P2P로 가능 | 문서에 언급 없음(미확인) | 불가 |
| 녹화 코덱 | 디바이스가 정함(HLS 재생은 H.264/H.265 + AAC) | H.264 + AAC 고정 | 디바이스가 정함 |
| 네트워크 단절 시 녹화 | Producer SDK 버퍼가 재전송(버퍼 크기만큼) | 문서에 디바이스 측 버퍼·재전송 언급이 없다. 실시간 경로이므로 끊긴 구간은 남지 않는다고 보는 게 안전하다 | Producer SDK 버퍼가 재전송 |
| 세션 수명 관리 | 시그널링 1시간 재연결 | 시그널링 + storage 세션 1시간 재참여 | Producer SDK가 토큰·연결 교체 |
| 디바이스 구현 | WebRTC SDK + Producer SDK 두 개 | WebRTC SDK 하나 | Producer SDK 하나 |
| 시간당 과금 구조(us-east-1) | PutMedia 수집 GB·저장 + P2P 쪽(채널·메시지·TURN) | 녹화 분당 $0.0034 + 실시간 viewer 분당 $0.003 | 수집 GB·저장·HLS 소비 GB |

### 비용 감각 잡기

과금 구조가 완전히 다르므로 숫자로 한 번 비교해 둔다. 가격은 22장과 같은 출처(Price List API, 2026-09-30 게시분, us-east-1)다. 스트림 저장 요금($0.023/GB-월)과 HLS 소비 요금($0.0119/GB)은 KVS 가격 페이지 예시에 나온 us-east-1 값이다.

농기계 1대가 하루 8시간, 한 달 30일 작업하고 2 Mbps로 녹화한다고 하자(월 240시간).

| 항목 | 계산 | 월 비용 |
|---|---|---|
| B. 녹화 분 | 240시간 × 60분 × $0.0034 | $48.96 |
| B. 운영자 1명이 매일 1시간 실시간 시청 | 30시간 × 60분 × $0.003 | $5.40 |
| C. 수집 | 2 Mbps × 3,600초 = 0.9 GB/시간 → 216 GB × $0.0085 | $1.84 |
| C. 저장(7일 보존) | 하루 7.2 GB × 7일 ≈ 50.4 GB 상시 보관 × $0.023 | $1.16 |

녹화만 놓고 보면 B가 C보다 한 자릿수 이상 비싸다. 다만 B의 분당 요금에 스트림 저장(GB-월) 요금이 포함되는지, 별도로 붙는지는 가격 페이지 본문에 WebRTC ingestion 항목이 렌더링되지 않아 확인하지 못했다. 실제 도입 전에는 소규모로 켜 보고 청구 내역(Cost Explorer의 사용 유형)으로 검증한다. A는 C의 비용에 P2P 쪽 비용(22장의 활성 채널·메시지·TURN)이 더해진다.

### 어떤 경우에 무엇을 고르나

- <strong>상시 녹화 + 가끔 실시간 시청 + 원격 조작</strong>(농기계 플랫폼의 일반적인 모습): A가 기본값이다. 녹화는 싸고 끊김에 강한 PutMedia가 맡고, 실시간 시청과 DataChannel 제어는 P2P가 맡는다. 단점은 시청 중에 업링크가 "PutMedia + viewer 수"만큼 늘어난다는 점이다. LTE 업링크가 빠듯하면 시청 중에는 P2P 비트레이트를 낮추거나 viewer를 1~2명으로 제한한다.
- <strong>업링크가 매우 좁고 실시간 시청과 녹화가 같은 시간대에만 필요</strong>: B가 맞다. 디바이스는 한 번만 올리고, 운영자 3명까지 1초 미만으로 보면서 그 장면이 그대로 저장된다. 운영자 음성 지시까지 녹화에 섞여 남는다는 점도 B만의 성질이다. 대신 1시간 재참여, H.264 고정, 1 Mbps 기본 한도, 분당 요금을 받아들여야 한다. 원격 조작 명령은 DataChannel 대신 MQTT 제어 채널([11장](/study/webrtc/11-datachannel))로 분리하는 편이 안전하다.
- <strong>실시간성이 필요 없는 감시·기록</strong>: C로 충분하다. 운영자는 몇 초 늦은 HLS로 보고, 사고가 나면 `GetClip`으로 MP4를 내려받는다. 가장 싸고 단순하다.
- <strong>event 기반 녹화</strong>: A의 변형으로, 디바이스가 평소에는 로컬(SD 카드)에 링 버퍼로 녹화하다가 충돌 감지·비상 정지 같은 이벤트가 나면 그 전후 구간만 PutMedia로 올리는 방식도 있다. PutMedia가 실시간뿐 아니라 일괄(오프라인) 전송도 지원하므로 가능하다. 저장 비용과 업링크를 함께 줄인다.

SFU를 직접 운영해 서버에서 녹화하는 방식([12장](/study/webrtc/12-topology-sfu)의 녹화 아키텍처)과 비교하면, B는 "viewer 3명까지인 관리형 SFU + 녹화기"를 빌려 쓰는 셈이다. 수십 명이 실시간으로 같은 영상을 봐야 한다면 B의 한도로는 부족하므로 IVS Real-Time([24장](/study/webrtc/24-ivs-real-time))이나 WHIP 기반 방송 구조([14장](/study/webrtc/14-whip-whep))를 검토한다. 캡스톤([25장](/study/webrtc/25-capstone-farm-platform))은 상시 녹화가 아니라 사건 구간 녹화가 요구사항이라, 위 event 기반 녹화 변형(로컬 링 버퍼 + 사건 구간 업로드)을 기본으로 하고 기체 파손 위험이 큰 모드에서만 A를 켜는 구성을 다룬다.

::: tip 핵심 정리
- 저장의 실체는 Kinesis Video Stream이다. 보존 기간(`DataRetentionInHours`)이 0이면 저장도, HLS도, `GetClip`도, 저장 모드 연결도 안 된다.
- 스트림의 단위는 키프레임에서 시작하는 프래그먼트(1~20초)이고, producer/server 타임스탬프로 조회한다. 쓰기는 Producer SDK(`kvssink`)의 장기 `PutMedia` 연결, 읽기는 HLS/DASH(`LIVE`/`LIVE_REPLAY`/`ON_DEMAND`)·`GetClip`·`GetMedia`·`GetImages`다.
- `UpdateMediaStorageConfiguration`으로 채널을 스트림에 연결하면 P2P가 사라지고 모든 피어가 storage 세션에 붙는다. "KVS WebRTC = P2P"는 기본 모드에만 맞는 말이다.
- 저장 모드에서는 storage 세션이 offer를 보낸다. master는 `JoinStorageSession`, viewer는 `JoinStorageSessionAsViewer`를 호출한 뒤 answer한다. 메시지에 `senderClientId`가 없고, 후보는 relay만 오며, Trickle ICE가 필수다.
- 제약: H.264 + Opus(저장은 H.264 + AAC), 최대 1920×1920, viewer 3명(오디오만 송신), 세션 1시간·idle 3분, 비트레이트 1 Mbps(조정 가능), 저장 채널 기본 100개. 오디오 필수 여부는 API 문서와 C SDK VideoOnly 샘플이 엇갈리므로 직접 검증한다.
- 녹화 비용은 PutMedia가 저장 모드보다 훨씬 싸다. 농기계처럼 상시 녹화 + 가끔 시청 + 원격 조작이면 "P2P 시청 + 병행 PutMedia"가 기본값이고, 저장 모드는 업링크가 좁고 시청과 녹화가 같은 시간대일 때 고른다.
:::

## 다음 챕터

[KVS 운영·보안·비용](/study/webrtc/22-kvs-operations)에서는 디바이스·운영자·백엔드별 IAM 최소 권한 정책, 채널 수명관리와 태그, CloudWatch 메트릭, 비용 구조와 TURN 비용 최적화, 할당량 관리, 그리고 시계 오차·자격증명 만료·1시간 연결 한도 같은 흔한 장애를 다룬다.
