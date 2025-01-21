---
categories: "devOps"
tag: ["kafka", "streams"]
title: "[Kafka] 카프카 스트림즈로 집계하기"
description: "카프카 스트림에서 사용한 메서드 정리"
teaser: "kafka"
---

# 0. kafka Config

```java
@Configuration
@EnableKafka
class KafkaStreamConfig {

    @Autowired lateinit var streamArticleService: StreamArticleService

    @Value("\${spring.kafka.streams.bootstrap-servers}")
    private val bootstrapServers: String = "localhost:9092"
    @Value("\${spring.kafka.streams.application-id}")
    private val applicationId: String = "web-stomp-dev"
    @Value("\${spring.kafka.streams.topic-name}")
    private val topicName: String = "refine-article-dev"

    private val props = mapOf(
        StreamsConfig.BOOTSTRAP_SERVERS_CONFIG to bootstrapServers,
        StreamsConfig.APPLICATION_ID_CONFIG to applicationId, //1 
        StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG to Serdes.String()::class.java,
        StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG to Serdes.String()::class.java
    )

    @Bean
    fun kafkaStreams(): KafkaStreams {
        val prop = Properties().apply {
            putAll(props)
        }

        val streamsBuilder = StreamsBuilder()
        val stream: KStream<String, String> = streamsBuilder.stream(topicName)
        stream.setHandler( // 2
            streamArticleService
        )

        val topology = streamsBuilder.build() //3

        val kafkaStreams = KafkaStreams(topology, prop)

        kafkaStreams.start()

        return kafkaStreams
    }
}
```

1. application-id : 동일한 애플리케이션 ID를 가진 인스턴스들이 같은 Consumer Group을 형성하고 이를 통해 토픽의 파티션들을 인스턴스들 간에 분배합니다.

2. setHandler : 필터처리를 위한 커스텀 메서드

3. topology :  Kafka Streams에서 데이터 처리 흐름을 정의하는 그래프입니다. 각각의 처리 단계(노드)와 그들 간의 연결(엣지)을 포함합니다.

   1. 토폴로지 시각화 (디버깅용) -> println(topology.describe())

   2. ```
      Sub-topology: 0
          Source: KSTREAM-SOURCE-0000000000 (topics: [test-topic])
            --> KSTREAM-MAP-0000000001
          Processor: KSTREAM-MAP-0000000001 (stores: [])
            --> test-store-repartition-filter
            <-- KSTREAM-SOURCE-0000000000
          Processor: test-store-repartition-filter (stores: [])
            --> test-store-repartition-sink
            <-- KSTREAM-MAP-0000000001
          Sink: test-store-repartition-sink (topic: test-store-repartition)
            <-- test-store-repartition-filter
            
            ...
      ```

# 1. setHandler()

```java
fun KStream<String, String>.setHandler(
    streamArticleService: StreamArticleService
) {

    this.map { _, value -> //1
        val article = objectMapper.readValue<Article>(value)
        KeyValue.pair(article.groupBy(), article)
    }.groupByKey( //2
        Grouped.with(
            Serdes.String(), 
            JsonSerde(Article::class.java) 
        )
    ).windowedBy( //3
        TimeWindows.ofSizeWithNoGrace(Duration.ofMinutes(1))
    ).aggregate( //4
        { mutableListOf() }, 
        { key, newer, accumulator ->
            accumulator.apply {
                add(newer)  
            }
        },
        buildWindowPersistentStore() //5
    ).suppress( //6
        Suppressed.untilWindowCloses(Suppressed.BufferConfig.unbounded())
    ).toStream()
        .foreach { key, value ->
            streamArticleService.streamToRealTimeSubscribers(value) //7
        }
}

// Article 리스트를 위한 커스텀 Serde
class ArticleListSerde : Serde<MutableList<Article>> {
    override fun serializer(): Serializer<MutableList<Article>> {
        return Serializer { _, data ->
            objectMapper.writeValueAsBytes(data)
        }
    }

    override fun deserializer(): Deserializer<MutableList<Article>> {
        return Deserializer { _, data ->
            objectMapper.readValue(data, object : TypeReference<MutableList<Article>>() {})
        }
    }
}

// 단일 Article을 위한 JsonSerde
class JsonSerde<T>(private val type: Class<T>) : Serde<T> {
    override fun serializer(): Serializer<T> {
        return Serializer { _, data ->
            objectMapper.writeValueAsBytes(data)
        }
    }

    override fun deserializer(): Deserializer<T> {
        return Deserializer { _, data ->
            objectMapper.readValue(data, type)
        }
    }
}

private fun buildWindowPersistentStore(): Materialized<String, MutableList<Article>, WindowStore<Bytes, ByteArray>> {

    return Materialized.`as`<String, MutableList<Article>, WindowStore<Bytes, ByteArray>>(WindowStore::class.java.name)
        .withKeySerde(Serdes.String())
        .withValueSerde(ArticleListSerde())
        .withRetention(Duration.ofMinutes(10))  // 10분 보존


}
```

1. map 으로 새로운 key, value 를 만듭니다. 

   - 현재 key 는 null 이고 value 는 Article 객체입니다.
   - Article 의 articleId 를 Key 로 사용합니다.

2. groupByKey 로 같은 키를 가진 레코드들을 하나의 그룹으로 모읍니다.

   - 내부적으로 데이터를 재파티셔닝(repartitioning)할 수 있습니다. 즉, 같은 키를 가진 모든 레코드가 같은 파티션으로 이동합니다.
   - 이를 위해서 Serdes 를 지정합니다. (Serialize/Deserialize)
   - 그러면 내부적으로 토픽을 다시 만들고 토픽의 파티션에 넣습니다. 처음 주어지는 키를 그대로 사용하면 groupByKey 에 인자를 넣을 필요는 없습니다.

3. windowedBy 는 1분 동안 집계한다는 뜻입니다. 그리고 noGrace 로 1분 이후에는 기다리지 않습니다.

   1. TimeWindows:

      - 고정된 시간 간격으로 데이터를 그룹화

      - 예: 1분마다의 집계

   1. SlidingWindows

      - 겹치는 윈도우로 데이터를 그룹화

      - 예: 5분 윈도우를 1분마다 이동

   1. SessionWindows

      - 비활성 기간을 기준으로 세션을 구분

      - 예: 5분 동안 활동이 없으면 새로운 세션 시작

   1. JoinWindows

      - 스트림 조인 작업에 사용

      - 지정된 시간 범위 내의 데이터 조인

4. aggregate 로 집계합니다.

   - mutableListOf() : 집계 초기값입니다. 여기에 값이 하나씩 더해집니다.
   - key : key 값
   - newer : 집계 대상
   - accumulator : 집계된 값들
   - add(newer)  : 어떻게 집계하는지입니다. accumulator 에 newer 을 add 합니다.

5.  Kafka Streams의 상태 저장소(State Store)를 구성하는 메서드입니다. 윈도우 별로 집계된 데이터를 저장하고 장애 발생 시 복구를 위한 상태를 보존합니다. RocksDB를 기본 저장소 엔진으로 사용합니다. 그래서 애플리케이션을 껐다가 켜도 `application.id`가 같으면 이전 상태를 유지합니다.

   - `Materialized.as()`

     - 상태 저장소의 이름 지정
     - 여기서는 WindowStore 클래스 이름을 사용

   - - 제네릭 타입 `<String, MutableList<Article>, WindowStore<Bytes, ByteArray>>`

     - String: 키의 타입

     - MutableList<Article>: 값의 타입

     - WindowStore<Bytes, ByteArray>: 저장소의 타입

   - Serde 설정

     - `.withKeySerde(Serdes.String())`: 키를 위한 직렬화/역직렬화 설정
     - `.withValueSerde(ArticleListSerde())`: Article 리스트를 위한 직렬화/역직렬화 설정

   - `.withRetention(Duration.ofMinutes(10))`:

     - 상태 저장소의 데이터 보존 기간을 설정

     - 10분이 지난 데이터는 자동으로 삭제됨

     - 메모리 관리에 중요한 역할

6. supress 는 Kafka Streams에서 윈도우 기반 연산의 출력을 제어하는 메서드입니다.

   - `untilWindowCloses`

     - 윈도우가 완전히 닫힐 때까지 모든 출력을 버퍼에 보관

     - 윈도우가 닫힐 때 한 번에 결과를 출력

   - `BufferConfig.unbounded()`

     - 버퍼 크기에 제한을 두지 않음

7. 마지막으로 group 화된 articles 를 서비스로 보내어 처리합니다. 여기선 STOMP 엔드포인트로 publish 합니다.