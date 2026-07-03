import{_ as e,c as r,e as o,o as a}from"./app-CqKF9o7V.js";const n={};function i(s,t){return a(),r("div",null,t[0]||(t[0]=[o(`<h1 id="tempo-아키텍처" tabindex="-1"><a class="header-anchor" href="#tempo-아키텍처"><span>Tempo 아키텍처</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>Tempo가 왜 검색 인덱스 없이 오브젝트 스토리지만으로 동작하도록 설계됐는지 이해한다.</li><li>distributor→ingester→블록으로 이어지는 쓰기 경로를 안다.</li><li>trace ID 조회와 TraceQL 검색이라는 두 가지 읽기 경로의 차이를 파악한다.</li><li>블록 포맷(parquet, bloom filter)과 metrics-generator, 배포·스케일링 모델을 익힌다.</li></ul></div><h2 id="_1-tempo-설계-—-오브젝트-스토리지만-사용하는-트레이드오프" tabindex="-1"><a class="header-anchor" href="#_1-tempo-설계-—-오브젝트-스토리지만-사용하는-트레이드오프"><span>1. Tempo 설계 — 오브젝트 스토리지만 사용하는 트레이드오프</span></a></h2><p>로그 스터디에서 다룬 Loki가 &quot;라벨만 인덱싱하고 본문은 청크로 저장&quot;하는 선택을 했듯, <strong>Tempo</strong>는 트레이스 데이터에서 한 단계 더 나아간 선택을 한다. <strong>trace ID를 제외한 어떤 전용 검색 인덱스도 두지 않고</strong>, 모든 trace 데이터를 오브젝트 스토리지(S3/GCS/Azure Blob)에 블록으로만 저장한다.</p><p>이 선택의 근거는 트레이스 데이터의 접근 패턴에 있다. 트레이스는 보통 &quot;이미 trace ID를 알고 있는 상태&quot;(로그나 메트릭의 exemplar에서 trace ID를 얻어 그 trace 하나를 열어보는 것)로 조회되는 경우가 압도적으로 많다. trace ID로 찾을 때는 별도 인덱스 없이도 해시 기반으로 어느 블록에 있을지 좁혀나갈 수 있다. 반면 속성 기반 전문 검색(TraceQL)은 상대적으로 드물게 쓰이며, 필요할 때는 블록을 스캔하는 비용을 감수한다.</p><pre class="mermaid">flowchart TB
    subgraph Traditional[&quot;전통적 트레이싱 백엔드&quot;]
        T1[&quot;Trace 데이터&quot;] --&gt; IDX[&quot;전용 검색 인덱스\\n(Elasticsearch 등)&quot;]
        IDX --&gt; Q1[&quot;쿼리&quot;]
    end
    subgraph TempoDesign[&quot;Tempo&quot;]
        T2[&quot;Trace 데이터&quot;] --&gt; BLK[&quot;블록 (오브젝트 스토리지)&quot;]
        BLK --&gt; BF[&quot;블록별 Bloom filter\\n(trace ID 존재 여부만 확인)&quot;]
        BF --&gt; Q2[&quot;trace ID 조회&quot;]
        BLK --&gt; Q3[&quot;TraceQL 검색\\n(블록 스캔)&quot;]
    end
</pre><p>이 설계는 Loki와 같은 철학적 뿌리를 공유한다. 인덱스를 최소화해 운영 복잡도와 인덱스 비대화(카디널리티) 문제를 원천적으로 피하고, 저장 비용이 저렴한 오브젝트 스토리지에 무제한에 가깝게 데이터를 쌓는다. 대신 검색은 인덱스 기반 시스템보다 느릴 수 있다는 트레이드오프를 받아들인다. 자세한 설계 배경은 <a href="https://grafana.com/docs/tempo/latest/" target="_blank" rel="noopener noreferrer">Tempo 공식 문서</a>를 참고한다.</p><h2 id="_2-쓰기-경로-—-distributor-→-ingester-→-blocks" tabindex="-1"><a class="header-anchor" href="#_2-쓰기-경로-—-distributor-→-ingester-→-blocks"><span>2. 쓰기 경로 — distributor → ingester → blocks</span></a></h2><p>Tempo로 들어오는 span은 <strong>distributor</strong>가 첫 번째로 받는다. distributor는 OTLP, Jaeger, Zipkin 등 여러 프로토콜을 동시에 수신할 수 있고, 각 span을 <code>trace_id</code> 기준 consistent hashing으로 특정 <strong>ingester</strong> 집합에 라우팅한다. 같은 trace에 속한 span은 항상 같은 ingester로 향하도록 보장된다 — 이래야 하나의 trace를 여러 ingester에 흩어놓지 않고 온전히 조립할 수 있다.</p><pre class="mermaid">flowchart LR
    APP[&quot;애플리케이션 / Collector\\n(OTLP)&quot;]
    DIST[&quot;Distributor\\ntrace_id 기준 해싱&quot;]
    ING1[&quot;Ingester 1&quot;]
    ING2[&quot;Ingester 2&quot;]
    ING3[&quot;Ingester 3&quot;]
    WAL[&quot;WAL (로컬 디스크)&quot;]
    HEAD[&quot;Head Block (메모리)&quot;]
    COMPLETE[&quot;Complete Block&quot;]
    OBJ[&quot;오브젝트 스토리지\\n(S3 / GCS / Azure)&quot;]

    APP --&gt; DIST
    DIST --&gt; ING1
    DIST --&gt; ING2
    DIST --&gt; ING3
    ING2 --&gt; WAL
    ING2 --&gt; HEAD
    HEAD --&gt;|&quot;cut 주기 도래&quot;| COMPLETE
    COMPLETE --&gt;|flush| OBJ
</pre><p>ingester는 도착한 span을 먼저 로컬 <strong>WAL(Write-Ahead Log)</strong>에 기록해 프로세스 재시작에도 유실되지 않도록 한 뒤, 메모리의 <strong>head block</strong>에 쌓는다. 설정된 주기(<code>max_block_duration</code>, 기본값 근방 수 분)나 크기 임계값에 도달하면 head block을 <strong>complete block</strong>으로 잘라내고(cut), 이를 오브젝트 스토리지에 업로드한다. 업로드가 끝나면 로컬 사본은 정리된다.</p><p>이 구조 때문에 아주 최근에 들어온 trace는 아직 오브젝트 스토리지에 없고 ingester 메모리에만 있을 수 있다. 읽기 경로가 ingester와 오브젝트 스토리지 양쪽을 함께 조회하는 이유가 여기에 있다.</p><h2 id="_3-읽기-경로-—-trace-by-id-traceql-검색" tabindex="-1"><a class="header-anchor" href="#_3-읽기-경로-—-trace-by-id-traceql-검색"><span>3. 읽기 경로 — trace by ID, TraceQL 검색</span></a></h2><p>Tempo의 읽기는 두 가지 질의 패턴으로 나뉜다.</p><p><strong>trace by ID 조회</strong>는 가장 단순하고 빠른 경로다. querier가 trace_id를 받으면, 아직 flush되지 않은 최근 데이터를 위해 ingester들에 직접 질의하는 동시에, 오브젝트 스토리지의 블록들에 대해서는 <strong>bloom filter</strong>로 &quot;이 블록에 해당 trace_id가 있는가&quot;를 먼저 걸러낸 뒤, 걸린 블록만 다운로드해 실제 데이터를 읽는다.</p><pre class="mermaid">sequenceDiagram
    participant G as Grafana
    participant QF as Query Frontend
    participant Q as Querier
    participant ING as Ingester
    participant OBJ as 오브젝트 스토리지

    G-&gt;&gt;QF: trace_id 조회
    QF-&gt;&gt;Q: 조회 위임
    Q-&gt;&gt;ING: 최근 데이터 질의 (메모리)
    Q-&gt;&gt;OBJ: 블록별 bloom filter 확인
    Note over Q,OBJ: bloom filter가 존재 가능성을&lt;br&gt;가리키는 블록만 다운로드
    OBJ--&gt;&gt;Q: 해당 블록 parquet 데이터
    ING--&gt;&gt;Q: 최근 span
    Q--&gt;&gt;QF: trace 조립 결과 병합
    QF--&gt;&gt;G: 완성된 trace
</pre><p><strong>TraceQL 검색</strong>은 trace_id를 모르는 상태에서 속성 조건으로 trace를 찾는 경로다. 예를 들어 &quot;지난 1시간 동안 <code>http.status_code &gt;= 500</code>이었던 trace를 모두 찾아라&quot; 같은 질의는 해당 시간 범위의 모든 블록을 스캔해야 한다. <strong>query-frontend</strong>가 시간 범위와 블록 단위로 질의를 여러 조각(shard)으로 쪼개 다수의 querier에 병렬로 분산시키고, 각 querier가 담당 블록을 스캔한 결과를 모아 반환한다. TraceQL 문법 자체는 다음 챕터에서 자세히 다룬다.</p><h2 id="_4-블록-포맷·저장-—-parquet-bloom-filter" tabindex="-1"><a class="header-anchor" href="#_4-블록-포맷·저장-—-parquet-bloom-filter"><span>4. 블록 포맷·저장 — parquet, bloom filter</span></a></h2><p>Tempo의 블록은 <strong>Parquet</strong> 컬럼형 포맷(vParquet 계열 인코딩)으로 저장된다. 컬럼형 저장은 &quot;이 속성 값만 훑어서 필터링&quot;하는 TraceQL 검색에 유리하다 — row 전체를 읽지 않고 필요한 컬럼(속성)만 스캔할 수 있기 때문이다. 블록 하나는 대략 다음 요소로 구성된다.</p><table><thead><tr><th>파일</th><th>역할</th></tr></thead><tbody><tr><td><code>meta.json</code></td><td>블록 메타데이터(테넌트, 블록 ID, 시간 범위, 크기, 인코딩 버전)</td></tr><tr><td>데이터 파일 (parquet)</td><td>실제 span·속성 데이터, 컬럼형으로 저장</td></tr><tr><td>bloom filter</td><td>이 블록에 특정 trace_id가 있을 가능성을 빠르게 판별하는 확률적 자료구조</td></tr><tr><td>index (선택)</td><td>trace_id → 블록 내 오프셋 매핑 보조 정보</td></tr></tbody></table><p><strong>bloom filter</strong>는 &quot;이 블록에 trace_id X가 없다&quot;는 것은 확실히 걸러내지만 &quot;있다&quot;는 답은 확률적으로만 맞는(false positive 가능) 자료구조다. false negative가 없다는 성질 덕분에, 실제로 trace가 없는 블록은 다운로드 자체를 건너뛸 수 있어 trace ID 조회를 크게 빠르게 만든다. 블록이 커질수록 bloom filter도 여러 조각(shard)으로 나눠 저장해, 필터 하나를 통째로 읽지 않고도 필요한 조각만 확인하게 최적화한다.</p><p>작은 블록이 계속 쌓이면 오브젝트 스토리지 요청 수가 늘어나 검색 비용이 커진다. <strong>compactor</strong> 컴포넌트가 주기적으로 작은 블록들을 더 큰 블록으로 병합하고, 보존 기간(retention)이 지난 블록을 삭제한다.</p><h2 id="_5-metrics-generator-—-span-metrics-service-graph" tabindex="-1"><a class="header-anchor" href="#_5-metrics-generator-—-span-metrics-service-graph"><span>5. metrics-generator — span metrics, service graph</span></a></h2><p>Tempo는 트레이스 저장소이면서 동시에 <strong>metrics-generator</strong> 컴포넌트를 통해 trace 데이터로부터 메트릭을 실시간으로 파생시킬 수 있다. 저장은 안 하지만 ingester가 받는 span 스트림을 관찰해 두 종류의 메트릭을 생성하고, Prometheus 호환 remote_write로 Mimir/Prometheus에 내보낸다.</p><ul><li><strong>span metrics</strong>: span의 이름·서비스·status를 라벨로 하는 RED 메트릭(Rate, Errors, Duration)을 자동 생성한다. 예를 들어 <code>traces_spanmetrics_calls_total</code>(호출 수), <code>traces_spanmetrics_latency</code>(지연 히스토그램)가 나온다.</li><li><strong>service graph metrics</strong>: span의 kind(<code>CLIENT</code>/<code>SERVER</code>)와 parent/child 관계를 분석해 서비스 간 호출 관계를 <code>traces_service_graph_request_total</code> 같은 메트릭으로 만든다. 이 메트릭으로 Grafana가 서비스 의존 관계 그래프를 자동으로 그릴 수 있다.</li></ul><pre class="mermaid">flowchart LR
    ING[&quot;Ingester\\n(span 스트림)&quot;]
    MG[&quot;metrics-generator&quot;]
    SM[&quot;span metrics\\ntraces_spanmetrics_*&quot;]
    SG[&quot;service graph metrics\\ntraces_service_graph_*&quot;]
    MIMIR[&quot;Mimir / Prometheus\\n(remote_write)&quot;]

    ING --&gt; MG
    MG --&gt; SM
    MG --&gt; SG
    SM --&gt; MIMIR
    SG --&gt; MIMIR
</pre><p>계측 없이도(별도 Prometheus exporter를 붙이지 않아도) 트레이스만 계측되어 있으면 RED 메트릭과 서비스 그래프를 얻을 수 있다는 점이 metrics-generator의 실질적 가치다. 이 메트릭을 다루는 구체적인 쿼리와 exemplar 연계는 <a href="/study/observability/23-traceql-spanmetrics">TraceQL과 span metrics</a> 챕터에서 이어진다.</p><h2 id="_6-배포·스케일링" tabindex="-1"><a class="header-anchor" href="#_6-배포·스케일링"><span>6. 배포·스케일링</span></a></h2><p>Tempo는 Loki·Mimir와 마찬가지로 두 가지 배포 모드를 지원한다.</p><ul><li><strong>모놀리식 모드(monolithic mode)</strong>: 단일 바이너리/프로세스가 distributor·ingester·querier·compactor 역할을 모두 수행한다. 소규모 트래픽이나 개발 환경에 적합하다.</li><li><strong>마이크로서비스 모드(microservices mode)</strong>: distributor, ingester, querier, query-frontend, compactor, metrics-generator를 각각 독립된 워크로드로 분리 배포한다. 컴포넌트별로 트래픽 특성에 맞춰 수평 확장할 수 있다.</li></ul><pre class="mermaid">flowchart TB
    subgraph Stateless[&quot;Stateless (수평 확장 쉬움)&quot;]
        DIST[&quot;Distributor&quot;]
        QF[&quot;Query Frontend&quot;]
        Q[&quot;Querier&quot;]
    end
    subgraph Stateful[&quot;Stateful (샤딩·리텐션 관리 필요)&quot;]
        ING[&quot;Ingester&quot;]
        COMP[&quot;Compactor&quot;]
    end
    RING[&quot;Hash Ring\\n(memberlist gossip)&quot;]

    DIST -.-&gt;|&quot;링 조회&quot;| RING
    ING -.-&gt;|&quot;링 등록&quot;| RING
    DIST --&gt; ING
    QF --&gt; Q
    Q --&gt; ING
</pre><p>distributor와 querier는 상태가 없어 트래픽에 따라 자유롭게 늘리고 줄일 수 있다. 반면 ingester는 최근 데이터를 메모리·로컬 디스크에 들고 있는 상태 저장 컴포넌트라, 스케일 조정 시 데이터 이관을 고려해야 한다. 컴포넌트 간 멤버십과 해시 링 정보는 memberlist gossip 프로토콜로 공유하며, 이는 Mimir·Loki와 동일한 방식이다. 쿠버네티스 위에서의 구체적인 배포는 이 스터디의 운영 심화 파트(Kubernetes 배포 챕터)에서 Loki·Mimir와 함께 다룬다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>Tempo는 전용 검색 인덱스 없이 오브젝트 스토리지의 블록만으로 동작하며, trace ID 조회를 최우선 접근 패턴으로 최적화한다.</li><li>쓰기 경로는 distributor(trace_id 해싱) → ingester(WAL + head block) → 오브젝트 스토리지 업로드 순서로 진행된다.</li><li>trace ID 조회는 bloom filter로 블록을 좁혀 빠르게 처리하고, TraceQL 검색은 query-frontend가 블록 단위로 질의를 쪼개 병렬 스캔한다.</li><li>블록은 Parquet 컬럼형 포맷으로 저장되고, bloom filter가 false negative 없는 확률적 필터로 불필요한 블록 다운로드를 막는다.</li><li>metrics-generator는 trace 데이터에서 span metrics(RED)와 service graph metrics를 실시간 파생시켜 별도 계측 없이 메트릭을 확보하게 해준다.</li><li>모놀리식/마이크로서비스 배포 모드를 지원하며, ingester는 상태 저장 컴포넌트로 스케일링 시 별도 고려가 필요하다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p><a href="/study/observability/23-traceql-spanmetrics">TraceQL과 span metrics</a>에서는 앞서 미리 본 TraceQL 문법과 metrics-generator가 만들어내는 span metrics·service graph metrics를 구체적인 쿼리와 함께 다룬다. 메트릭에서 트레이스로 점프하는 exemplar 연계까지 이어진다.</p>`,35)]))}const l=e(n,[["render",i],["__file","22-tempo-architecture.html.vue"]]),p=JSON.parse('{"path":"/study/observability/22-tempo-architecture.html","title":"Tempo 아키텍처","lang":"en-US","frontmatter":{"title":"Tempo 아키텍처","description":"검색 인덱스를 두지 않고 오브젝트 스토리지만으로 동작하는 Tempo의 설계 철학과, distributor→ingester→블록으로 이어지는 쓰기 경로, trace ID 조회·TraceQL 검색의 읽기 경로, 블록 포맷과 metrics-generator까지 Tempo 아키텍처를 다룬다.","date":"2026-07-02T00:00:00.000Z","tags":["Tempo","Tracing","Architecture"],"prev":"/study/observability/21-opentelemetry","next":"/study/observability/23-traceql-spanmetrics"},"headers":[{"level":1,"title":"Tempo 아키텍처","slug":"tempo-아키텍처","link":"#tempo-아키텍처","children":[{"level":2,"title":"1. Tempo 설계 — 오브젝트 스토리지만 사용하는 트레이드오프","slug":"_1-tempo-설계-—-오브젝트-스토리지만-사용하는-트레이드오프","link":"#_1-tempo-설계-—-오브젝트-스토리지만-사용하는-트레이드오프","children":[]},{"level":2,"title":"2. 쓰기 경로 — distributor → ingester → blocks","slug":"_2-쓰기-경로-—-distributor-→-ingester-→-blocks","link":"#_2-쓰기-경로-—-distributor-→-ingester-→-blocks","children":[]},{"level":2,"title":"3. 읽기 경로 — trace by ID, TraceQL 검색","slug":"_3-읽기-경로-—-trace-by-id-traceql-검색","link":"#_3-읽기-경로-—-trace-by-id-traceql-검색","children":[]},{"level":2,"title":"4. 블록 포맷·저장 — parquet, bloom filter","slug":"_4-블록-포맷·저장-—-parquet-bloom-filter","link":"#_4-블록-포맷·저장-—-parquet-bloom-filter","children":[]},{"level":2,"title":"5. metrics-generator — span metrics, service graph","slug":"_5-metrics-generator-—-span-metrics-service-graph","link":"#_5-metrics-generator-—-span-metrics-service-graph","children":[]},{"level":2,"title":"6. 배포·스케일링","slug":"_6-배포·스케일링","link":"#_6-배포·스케일링","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/observability/22-tempo-architecture.md"}');export{l as comp,p as data};
