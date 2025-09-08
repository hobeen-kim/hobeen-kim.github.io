---
title: "도커에서 카프카 접근하기"
date: 2025-01-18
tags:
  - kafka
  - docker
description: "도커에서 카프카 연결하는 방법"
---

<Header/>

[[toc]]

# 0. 문제 상황

- Local 에서 카프카 실행 (localhost:9092)

- docker (python) 으로 카프카에 produce (host.docker.internal:9092), 하지만 timeout 에러

  - ```
    KafkaTimeoutError: Batch for TopicPartition(topic='raw-article', partition=1) containing 1 record(s) expired: 30 seconds have passed since batch creation plus linger time
    ```

# 1. 문제 원인

- kafka 는 어떤 서버와 연결할지 advertised.listeners 를 가지고 있으며 기본은 localhost 다.
- docker 에서는 host.docker.internal 로 접근하므로 해당 도메인도 열어줘야 한다.

# 2. kafka 설정

- ~/kafka/kafka_2.13-3.9.0/config/server.properties 에 echo 를 통해 설정 추가한다.

```
echo "listeners=LOCAL://localhost:9092,DOCKER://localhost:29092" >> ~/kafka/kafka_2.13-3.9.0/config/server.properties
echo "advertised.listeners=LOCAL://localhost:9092,DOCKER://host.docker.internal:29092" >> ~/kafka/kafka_2.13-3.9.0/config/server.properties
echo "listener.security.protocol.map=LOCAL:PLAINTEXT,DOCKER:PLAINTEXT" >> ~/kafka/kafka_2.13-3.9.0/config/server.properties
echo "inter.broker.listener.name=LOCAL" >> ~/kafka/kafka_2.13-3.9.0/config/server.properties
```

## 2.1 설정 설명

- listeners
  - Kafka 브로커가 **실제로 바인딩하는** 네트워크 인터페이스와 포트
  - localhost:9092 와 localhost:29092 에서만 연결을 수신한다. 생산자와 소비자는 해당 도메인으로 접근해야 한다. 즉 로컬에서만 접근할 수 있다. 0.0.0.0 으로 하면 퍼블릭하게 접근할 수 있다는 뜻이다.
- advertised.listeners 
  - Kafka가 클라이언트에게 **알려주는** 연결 주소로 클라이언트가 실제로 연결할 때 사용하는 주소다. 
  - 로컬 클라이언트와 도커 클라이언트는 `localhost:9092` 또는  `host.docker.internal:29092`로 접속해야 한다.
- listener.security.protocol.map
  - 리스너가 어떤 보안 프로토콜을 사용할지 정의하는 설정
    - PLAINTEXT: 암호화되지 않은 일반 TCP 연결
    - SSL: SSL/TLS 암호화 통신
    - SASL_PLAINTEXT: SASL 인증 (암호화 없음)
    - SASL_SSL: SASL 인증 + SSL 암호화
  - LOCAL:PLAINTEXT  이면 LOCAL 을 사용하는 도메인은 PLAINTEXT 를 사용한다는 뜻이다.
- inter.broker.listener.name
  - Kafka 브로커들 간의 내부 통신에 사용할 리스너를 지정하는 설정
  - LOCAL 이므로 localhost:9092 를 사용한다는 뜻이다

# 2.2 참고사항

- advertised.listeners 을 설정할 때 포트가 겹치면 안된다. 나는 9092 와 29092 로 나눴다.
- kafka 가 실행안된다면 `~/kafka/kafka_2.13-3.9.0/logs/server.log` 에서 로그를 확인할 수 있다.

# Ref.

[https://stackoverflow.com/questions/62213671/how-to-solve-kafka-errors-kafkatimeouterror-kafkatimeouterror-failed-to-update](https://stackoverflow.com/questions/62213671/how-to-solve-kafka-errors-kafkatimeouterror-kafkatimeouterror-failed-to-update)

<Footer/>
