---
title: "카프카 에러 - InvalidRecordException"
date: 2025-09-01
tags:
  - kafka
description: "카프카 운영 중에 생겨난 에러"
---

# 문제 상황

사내에서 디바이스에서 보내는 로그 데이터를 읽는 데 메시지 브로커로 카프카를 사용하고 있습니다. 그러면서 카프카 스트림즈도 함께 활용하고 있는데 다음과 같은 에러와 함께 스트림즈 앱이 멈췄습니다.

```
025-09-01T11:58:31.969+09:00 ERROR 1 --- [stream-processors] [read-1-producer] o.a.k.s.p.internals.RecordCollectorImpl : stream-thread [streams-app-d3bb6af2-e3c2-4ad0-b829-f2196d7b5ee3-StreamThread-1] stream-task [0_2] Error encountered sending record to topic streams-app-last-seen-store-changelog for task 0_2 due to: log-streams 
September 01, 2025 at 11:58 org.apache.kafka.common.InvalidRecordException: Timestamp 1756424749729 of message with offset 0 is out of range. The timestamp should be within [1756609111968, 1756781911968] log-streams September 01, 2025 at 11:58 Exception handler choose to FAIL the processing, no more records would be sent. log-streams 
September 01, 2025 at 11:58 org.apache.kafka.common.InvalidRecordException: Timestamp 1756424749729 of message with offset 0 is out of range. The timestamp should be within [1756609111968, 1756781911968] log-streams
```

Kafka Streams 앱이 토픽(streams-app-last-seen-store-changelog)에 데이터를 쓰려고 할 때, 레코드에 붙은 타임스탬프가 브로커가 허용하는 범위를 벗어났다는 이유로 거부되고 있는 상황이었습니다.
그 결과 StreamsException 이 발생하면서 Exception handler choose to FAIL the processing 으로 전체 스트림이 ERROR 상태로 전환돼서 종료되었습니다.

## 문제 원인

일차적인 원인은 **streams 서버가 "꺼졌다가 켜져서"**였습니다. 당장 실시간 데이터를 활용하고 있지 않기 때문에 서버가 업데이트될 떄 잠깐 꺼졌다가 켜지는 상황은 리소스 절약을 위해서도 어느정도 허용하고 있었습니다. 하지만 ECS 인스턴스가 제대로 스케일 인/아웃이 되지 않아서 streams 서버가 다시 켜지는 시간이 수 분 이상이 되었습니다.

