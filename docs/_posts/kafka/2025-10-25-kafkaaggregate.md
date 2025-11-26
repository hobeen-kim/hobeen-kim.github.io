---
title: "kafka stream 으로 집계하기 (windowBy, suppress)"
date: 2025-10-25
tags:
  - kafka
  - stream
description: "windowBy 와 suppress 사용방법 알기"
---

<Header/>

[[toc]]

# 1. kafka streams

kafka streams 는 Apache Kafka 개발 프로젝트에서 공식적으로 제공되는 스트림 프로세싱 프레임워크다. Kafka 토픽에 쌓이는 이벤트(메시지)를 실시간으로 읽고 필터, 변환, 집계, 조인, 윈도우 연산 등을 수행해서 다시 Kafka 토픽이나 외부 시스템(DB, 캐시 등)에 결과를 내보낼 수 있다.

## 1.2 집계

kafka streams 를 사용하면서 다음과 같은 사용이 생길 수 있다.

> t ~ t + 10초 간의 데이터의 평균 구하기
>
> 예를 들어서 10초 동안의 자동차 속도 평균을 구하기

이럴 때 집계 연산과 windowBy, suppress 를 사용할 수 있다.

# 2. 데이터 집계하기

다음과 같은 자동차의 데이터가 토픽으로 들어온다고 가정해보자

```kotlin
data class Log (
    val carId: String,
    val speed: Int,
)
```

그리고 **10초마다 속도의 평균이 50 이 넘는지 확인하는 로직**을 작성하려면 다음과 같이 코드를 작성할 수 있다.

**MergedLog**

집계되는 공간을 정의한다. log 가 들어오면 `addSpeed()` 로 MergedLog 에 집계된다.

```kotlin
data class MergedLog (
    var carId: String,
    var meanSpeed: Double,
    val speeds: MutableList<Int> = mutableListOf(),
    var isViolated: Boolean = false,
    var startTime: LocalDateTime? = null,
    var endTime: LocalDateTime? = null,
) {
    companion object {
        fun empty(): MergedLog {
            return MergedLog(carId = "emp", meanSpeed = 0.0)
        }
    }

    @JsonIgnore
    fun isEmpty(): Boolean {
        return carId == "emp"
    }

    fun init(log: Log): MergedLog {
        this.carId = log.carId
        addSpeed(log.speed)
        return this
    }

    fun addSpeed(speed: Int): MergedLog {
        meanSpeed = (meanSpeed * speeds.size + speed) / (speeds.size + 1)
        speeds.add(speed)
        return this
    }

    fun finish(start: Instant, end: Instant): MergedLog {
        this.startTime = LocalDateTime.ofInstant(start, ZoneId.of("Asia/Seoul"))
        this.endTime = LocalDateTime.ofInstant(end, ZoneId.of("Asia/Seoul"))
        if(meanSpeed > 50.0) { isViolated = true }
        return this
    }
}
```

**Topology**

```kotlin
@Configuration
class Topology {
    private val logSerde: Serde<Log> = JsonSerde(Log::class.java)
    private val mergedLogSerde: Serde<MergedLog> = JsonSerde(MergedLog::class.java)

    @Bean
    fun carLogTopology(streamsBuilder: StreamsBuilder): KStream<String, MergedLog> {
        val source: KStream<String, MergedLog> = streamsBuilder
            .stream("car-log", Consumed.with(Serdes.String(), logSerde)) //car-log 를 consume 한다. key,value 는 String, Log 타입이다.
            .groupByKey() //key 로 grouping 한다.
            .windowedBy(TimeWindows.ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(2))) //window 는 10초, 지연 2초 허용.
            .aggregate(
                { MergedLog.empty() }, // MergedLog 생성
                { _: String, log: Log, aggregate: MergedLog ->
                    if (aggregate.isEmpty()) aggregate.init(log) //최초 생성 시에는 aggregate 에 log 를 넣어준다.
                    else aggregate.addSpeed(log.speed) //두번째부터 aggregate 에 그 다음 log 의 스피드를 더한다.
                },
                buildLogMergedWindowStore() // 윈도우 집계를 위해 (key, window) 별 MergedLog 상태를 저장하는 RocksDB 기반 state store 설정
            )
            .suppress(Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded())) // window 가 끝날 때까지 emit 을 supress 한다. 윈도우가 닫힐 때까지 모든 결과를 메모리에 쌓다가 한 번에 내보내는 구조
            .toStream()
            .map { windowedKey, mergedLog ->
                val window = windowedKey.window()
                val finished = mergedLog.finish(window.startTime(), window.endTime())
                KeyValue(windowedKey.key(), finished)
            } // Windowed<String>, MergedLog 를 String, MergedLog 로 변경한다. Windowed 는 윈도우 정보를 담고 있다.

        source.to("car-log-merged", Produced.with(Serdes.String(), mergedLogSerde)) //car-log-merged

        return source
    }

    private fun buildLogMergedWindowStore(): Materialized<String, MergedLog, WindowStore<Bytes, ByteArray>> { //이 store 에는 (key + window)별 MergedLog 상태가 저장
        return Materialized.`as`<String, MergedLog, WindowStore<Bytes, ByteArray>>("car-log-merged-window-store")
            .withKeySerde(Serdes.String())
            .withValueSerde(mergedLogSerde)
            .withRetention(Duration.ofMinutes(1))
            .withCachingEnabled()
    }
}
```

# 3. windowedBy

`windowedBy`는 **KStream → KGroupedStream → 윈도우 기반 집계** 할 때 쓰는 설정이다.

```kotlin
.stream("car-log", ...)
.groupByKey()
.windowedBy(TimeWindows.ofSizeWithNoGrace(Duration.ofSeconds(10)))
.aggregate(...)
```

여기서 쓸 수 있는 윈도우 타입은 크게 3가지다.

1. **TimeWindows** (타임 윈도우, tumbling/hopping)
2. **SessionWindows** (세션 윈도우)
3. **SlidingWindows** (슬라이딩 윈도우)

## 3.1 TimeWindows

**시간 구간을 고정된 크기로 자르는 윈도우**다. 대표적인 팩토리 메서드들은 다음과 같다.

```kotlin
TimeWindows.ofSizeWithNoGrace(size: Duration)
TimeWindows.ofSizeAndGrace(size: Duration, grace: Duration)
```

### 주요 옵션 및 개념

1. **size (윈도우 크기)**

   - `Duration.ofSeconds(10)` → 0~10, 10~20, 20~30 … 이런 식으로 나뉨
   - 기본은 **tumbling window** (겹치지 않는 윈도우)

2. **grace (지연 허용 시간)**

   - 이벤트 타임 기준으로 **“윈도우 끝난 후 얼마까지 늦게 도착해도 집계에 넣어줄 것인가”**
   - `ofSizeWithNoGrace()` → **지연 허용 0** → 윈도우 종료 시점 이후에 도착한 이벤트는 드랍
   - `ofSizeAndGrace(10초, 5초)` →
     - 윈도우 0~10초
     - **원래 종료 시각 + 5초까지** 들어온 이벤트는 반영
     - 그 이후는 late record로 취급 (드랍되거나, 별도 처리)

3. **hopping window (`advanceBy`)**
   
    - 크기는 10초인데 5초마다 새 윈도우를 시작하는 식이다.
    
   ```kotlin
   TimeWindows
       .ofSizeAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))
       .advanceBy(Duration.ofSeconds(5))
   ```
   
   - 윈도우 구간: 0~10, 5~15, 10~20, 15~25 … (서로 겹침)
    - **한 이벤트가 여러 윈도우에 들어갈 수 있다.**
   
4. **Retention (Materialized 와 같이 씀)**

   ```kotlin
   .withRetention(Duration.ofMinutes(1))
   ```

   - 내부 state store에 **윈도우 상태를 얼마나 오래 유지할지**
   - 최소 조건: `retention >= windowSize + grace`
   - 너무 크게 잡으면 디스크 사용량이 커지고 리밸런스/복구 시간도 길어짐

## 3.2 SessionWindows – 사용자/디바이스 활동 세션 단위

**특정 시간 동안 이벤트가 없으면 세션이 끊기고, 다시 이벤트가 오면 새 세션 시작**이라는 개념이다.

```kotlin
SessionWindows
    .with(Duration.ofMinutes(5))   // inactivity gap
    .grace(Duration.ofMinutes(1))  // 지연 허용
```

- inactivity gap = **이 시간 이상 이벤트가 없으면 세션 종료**
- 세션 윈도우는 **시작 시간/종료 시간이 가변적**(고정 크기 X)
- 주로 **사용자 세션, 접속 세션, 특정 장비의 활동 구간** 같은 걸 집계할 때 사용

## 3.3 SlidingWindows – 두 이벤트 사이의 시간 차 기반

**두 이벤트의 타임스탬프 차이가 일정 시간 이내일 때 같은 윈도우로 본다**는 개념이다.

```kotlin
SlidingWindows.ofTimeDifferenceWithNoGrace(Duration.ofSeconds(10))
SlidingWindows.ofTimeDifferenceAndGrace(Duration.ofSeconds(10), Duration.ofSeconds(5))
```

- max time difference = 두 이벤트 사이 허용 시간 차
- 주로 **stream-stream join**이나 **최근 N초 안에 같은 키에서 어떤 패턴이 나왔냐**같은 데 쓰임
- 일반적인 단일 스트림 집계도 가능하지만, TimeWindows보다 설정이 더 복잡한 편이다.

예시는 다음과 같다.

`SlidingWindows.ofTimeDifferenceWithNoGrace(Duration.ofSeconds(10))` 일 때 다음과 같이 1초 간격으로 이벤트가 들어온다고 하자.

> 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ... 20

그러면 SlidingWindows 가 emit 할 때 아래와 같이 집계된다.

> - [1]
> - [1, 2]
> - [1, 2, 3]
> - ...
> - [1, 2, 3 ... 10]
> - [2, 3, 4, ... 11]
> - [3, 4, ,5 ... 12]
> - ...
> - [11, 12, 13 ... 20]

# 4. suppress

aggregate()/count() 등은 KTable 을 반환하고, 이건 변경될 때마다 중간 결과가 계속 흘러나온다. suppress 는 **KTable 에서 나오는 업데이트들을 바로 내보내지 않고, 조건이 충족될 때까지 버퍼에 모아두었다가 한 번에(또는 특정 규칙에 따라) 내보내는 기능**이다.

## 4.1 suppressed.untilWindowCloses(BufferConfig)

- 윈도우 기반 KTable 전용
- **윈도우가 완전히 닫힐 때까지(= window end + grace 지나기 전까지) 결과를 숨긴다**
- 즉, **최종 결과(final result)만 emit**하는 패턴

예시:

```kotlin
.suppress(
    Suppressed.untilWindowCloses(
        Suppressed.BufferConfig
            .maxBytes(100L * 1024 * 1024)  // 100MB
            .emitEarlyWhenFull()
    )
)
```

## 4.2 Suppressed.untilTimeLimit(duration, BufferConfig)

- 일반 KTable에도 사용할 수 있다.
- **특정 시간(stream time) 동안 모았다가 한 번에 내보내기**
- 5초 단위로 변경분을 배치처럼 내보내자 와 같이 사용 가능

```kotlin
.suppress(
    Suppressed.untilTimeLimit(
        Duration.ofSeconds(5),
        Suppressed.BufferConfig.maxRecords(1000)
    )
)
```

##4.3 BufferConfig 옵션

`BufferConfig`는 suppression 시 **어디까지 쌓아둘지, 넘치면 어떻게 할지**를 정하는 설정이다.

1. **용량 설정**

   ```kotlin
   Suppressed.BufferConfig.unbounded()         // 제한 없음 (위험)
   Suppressed.BufferConfig.maxRecords(n: Long) // 레코드 개수 기준 제한
   Suppressed.BufferConfig.maxBytes(n: Long)   // 바이트 기준 제한
   ```

   - `unbounded()`는 **OOM / 디스크 폭주 위험**이 있어서 실서비스에서는 추천되지 않는다.
   - 보통 `maxBytes` 또는 `maxRecords`로 제한 두는 게 좋음
   - 둘을 같이 쓰면 **둘 중 하나라도 넘어가면 full로 판단**

2. **버퍼가 가득 찼을 때 행동**

   ```kotlin
   .shutDownWhenFull()   // 에러 던지고 애플리케이션 종료
   .emitEarlyWhenFull()  // 아직 조건(윈도우 close 등)이 안 돼도 지금까지 쌓인 것 먼저 내보냄
   ```

   - **`shutDownWhenFull()`**
     - 데이터 손실을 막는 대신, 서비스가 죽어버림
   - **`emitEarlyWhenFull()`**
     - 서비스는 계속 살리고, suppression의 완벽한 final-only 보장은 깨질 수 있음 (일부 중간 결과가 먼저 emit될 수 있음)

**실무에서 많이 쓰는 패턴 예시**

```kotlin
.suppress(
    Suppressed.untilWindowCloses(
        Suppressed.BufferConfig
            .maxBytes(100L * 1024 * 1024) // 100MB 정도
            .emitEarlyWhenFull()
    )
)
```

# 5. state store

State Store 는 Kafka Streams가 **상태**를 저장하기 위한 로컬 저장소이다. 대부분 RocksDB + 메모리 캐시, 필요하면 changelog 토픽으로 복구 가능한 구조이다. 여기서 상태(state)란

- window 집계 결과 (ex. 10초 동안의 평균 속도)
- count, sum 등의 누적 값
- join할 때 필요한 lookup 테이블
- KTable의 현재 값

등을 말한다. Kafka Streams는 단순히 메시지가 하나 들어오면 바로 변환해서 내보내기만 하는 게 아니라, **과거 데이터까지 고려해야 하는 연산**을 해야하기 때문이다. State Store 는 실제로 **로컬 디스크에 RocksDB**로 저장되지만 그 앞단에 **메모리 캐시**가 있어서 자주 쓰는 키는 메모리에서 접근 가능하다. 그리고 **changelog 토픽**에 state 변경 사항을 계속 기록한다.

> changelog 으로 인스턴스가 죽었다 살아나도 **changelog를 다시 읽어서 RocksDB를 재구성**할 수 있음

## 5.1 `aggregate` 쪽 스토리지

```kotlin
.groupByKey()
.windowedBy(...)
.aggregate(
    { MergedLog.empty() },
    { key, log, agg -> ... },
    buildLogMergedWindowStore()
)
```

aggregate 쪽 스토리지는

- 키: `Windowed<String>` (key + window 정보)
- 값: `MergedLog` (지금까지 합산된 상태)

으로 저장된다. 즉, **이 key가 이 윈도우(예: 12:00~12:10)에서 현재까지 어떤 상태인가?**를 저장하는 공간이다. 해당 정보는 `buildLogMergedWindowStore()` 에서 만든 **WindowStore** 안에 저장된다.

> `aggregate`는 **비즈니스 상태(MergedLog)**를
>  **로컬 RocksDB state store + changelog 토픽**에 저장한다.

여기서 저장된 값은 **“윈도우별 최신 집계 상태” 자체**다.

## 5.2 `suppress` 쪽 스토리지

```kotlin
.aggregate(...)
.suppress(Suppressed.untilWindowCloses(BufferConfig...))
```

`aggregate()`의 결과는 **KTable** 인데, KTable은 상태가 바뀔 때마다 **변경 이벤트(change)**를 아래로 흘려보낸다. 예를 들어 한 윈도우 안에서 같은 key로 로그가 여러 번 들어오면,

- 첫 번째 기록: `MergedLog(speed=30)`
- 두 번째 기록: `MergedLog(speed=30+40)`
- 세 번째 기록: `MergedLog(speed=30+40+50)`

이런 식으로 중간중간 업데이트들이 downstream으로 계속 보내지는 구조이다. `kTable.suppress(...)`는 이 업데이트들을 **바로 내보내지 말고 모아둔다**.

### 저장되는 값

이 저장소에는 KTable에서 나오는 **변경 이벤트들**이 저장된다. (즉, 이 key/window의 값이 이렇게 바뀌었음이라는 레코드들) 하지만 `aggregate` state store 와 중요한 차이는, aggregate 에서는 **최신 상태만** 저장(MergedLog 현재 값)한다면, `suppress`의 버퍼는 **다운스트림으로 아직 내보내지 않은 최신 값 한 개의 레코드들**을 저장하다가 조건(윈도우가 닫힘, 시간 제한 등)이 되면 이 레코드들을 한 번에 방출한다.

즉, aggregate state store 에 저장된 값이 바뀔 때마다 나오는 **변경 이벤트**를 자체 버퍼 state store(RocksDB + 캐시)에 쌓아두고, 조건 충족 시에만 KStream 으로 내보낸다.

## 5.3 state store 정리

- **aggregate의 state store**
  - 목적: **집계 상태(MergedLog)를 유지**
  - 위치: **로컬 RocksDB + changelog 토픽**
  - 내용: 지금 이 key/window의 최종(현재) 상태가 뭐냐
- **suppress의 state store**
  - 목적: **아직 내보내지 않은 결과들을 버퍼링**
  - 위치: **별도 RocksDB + 메모리 캐시**
  - 내용: 아직 downstream으로 emit하지 않은 변경 이벤트들





<Footer/>
