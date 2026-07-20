import{_ as e,c as n,e as l,o as a}from"./app-J_vrPzUq.js";const i="/images/study-observability/29-log-pipeline-light.png",c="/images/study-observability/29-log-pipeline-dark.png",o="/images/study-observability/29-clustering-sequence-light.png",p="/images/study-observability/29-clustering-sequence-dark.png",r={};function d(t,s){return a(),n("div",null,s[0]||(s[0]=[l(`<h1 id="alloy-파이프라인-구성" tabindex="-1"><a class="header-anchor" href="#alloy-파이프라인-구성"><span>Alloy 파이프라인 구성</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li><code>prometheus.scrape</code> → <code>prometheus.remote_write</code> 체인으로 메트릭 파이프라인을 구성한다.</li><li><code>loki.source.*</code> → <code>loki.process</code> → <code>loki.write</code> 체인으로 로그 파이프라인을 구성하고 파싱 스테이지를 이해한다.</li><li><code>otelcol.receiver</code> → <code>processor</code> → <code>exporter</code> 체인으로 트레이스 파이프라인을 구성한다.</li><li><code>otelcol.processor.tail_sampling</code>으로 Alloy 안에서 tail-based sampling을 적용하는 방법을 익힌다.</li><li><code>pyroscope.scrape</code>/<code>pyroscope.ebpf</code>로 계측·무계측 프로파일 파이프라인을 구성한다.</li><li>clustering이 스크레이프 타깃을 레플리카 간에 어떻게 분배하는지 이해한다.</li></ul></div><h2 id="_1-메트릭-파이프라인-—-prometheus-scrape-→-prometheus-remote-write" tabindex="-1"><a class="header-anchor" href="#_1-메트릭-파이프라인-—-prometheus-scrape-→-prometheus-remote-write"><span>1. 메트릭 파이프라인 — prometheus.scrape → prometheus.remote_write</span></a></h2><p>메트릭 파이프라인의 뼈대는 <a href="/study/observability/05-prometheus-architecture">Prometheus 스크레이핑</a>의 개념을 그대로 컴포넌트로 옮긴 것이다. <code>discovery.kubernetes</code>로 타깃을 찾고, <code>discovery.relabel</code>로 라벨을 다듬은 뒤, <code>prometheus.scrape</code>가 실제로 긁고, <code>prometheus.remote_write</code>가 Mimir로 밀어넣는다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">discovery.kubernetes &quot;pods&quot; {</span>
<span class="line">  role = &quot;pod&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">discovery.relabel &quot;app_pods&quot; {</span>
<span class="line">  targets = discovery.kubernetes.pods.targets</span>
<span class="line"></span>
<span class="line">  rule {</span>
<span class="line">    source_labels = [&quot;__meta_kubernetes_pod_annotation_prometheus_io_scrape&quot;]</span>
<span class="line">    action        = &quot;keep&quot;</span>
<span class="line">    regex         = &quot;true&quot;</span>
<span class="line">  }</span>
<span class="line">  rule {</span>
<span class="line">    source_labels = [&quot;__meta_kubernetes_namespace&quot;]</span>
<span class="line">    target_label  = &quot;namespace&quot;</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">prometheus.scrape &quot;app&quot; {</span>
<span class="line">  targets         = discovery.relabel.app_pods.output</span>
<span class="line">  forward_to      = [prometheus.remote_write.mimir.receiver]</span>
<span class="line">  scrape_interval = &quot;30s&quot;</span>
<span class="line">  job_name        = &quot;app-metrics&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">prometheus.remote_write &quot;mimir&quot; {</span>
<span class="line">  endpoint {</span>
<span class="line">    url = &quot;https://mimir.example.com/api/v1/push&quot;</span>
<span class="line"></span>
<span class="line">    queue_config {</span>
<span class="line">      capacity          = 10000</span>
<span class="line">      max_shards        = 50</span>
<span class="line">      max_samples_per_send = 2000</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>prometheus.scrape</code>는 여러 <code>forward_to</code> 대상을 가질 수 있어 하나의 스크레이프 결과를 로컬 Prometheus와 Mimir 양쪽으로 동시에 보낼 수도 있다. <code>queue_config</code>는 원본 Prometheus의 remote_write 큐 설정과 동일한 파라미터를 그대로 노출하므로, <a href="/study/observability/12-tsdb-remote-write">TSDB와 remote_write</a>에서 다룬 백프레셔 튜닝 지식을 그대로 적용할 수 있다.</p><h2 id="_2-로그-파이프라인-—-loki-source-→-loki-process-→-loki-write" tabindex="-1"><a class="header-anchor" href="#_2-로그-파이프라인-—-loki-source-→-loki-process-→-loki-write"><span>2. 로그 파이프라인 — loki.source.* → loki.process → loki.write</span></a></h2><p>로그는 소스 컴포넌트(<code>loki.source.file</code>, <code>loki.source.kubernetes</code>, <code>loki.source.journal</code> 등)로 원본 라인을 받고, <code>loki.process</code>에서 스테이지 체인으로 파싱·라벨링한 뒤, <code>loki.write</code>로 내보낸다. 이 흐름은 <a href="/study/observability/18-logql">LogQL</a> 쿼리가 전제하는 라벨·구조를 파이프라인 단계에서 미리 만들어주는 과정이다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">discovery.relabel &quot;pod_logs&quot; {</span>
<span class="line">  targets = discovery.kubernetes.pods.targets</span>
<span class="line"></span>
<span class="line">  rule {</span>
<span class="line">    source_labels = [&quot;__meta_kubernetes_namespace&quot;]</span>
<span class="line">    target_label  = &quot;namespace&quot;</span>
<span class="line">  }</span>
<span class="line">  rule {</span>
<span class="line">    source_labels = [&quot;__meta_kubernetes_pod_container_name&quot;]</span>
<span class="line">    target_label  = &quot;container&quot;</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">loki.source.kubernetes &quot;pods&quot; {</span>
<span class="line">  targets    = discovery.relabel.pod_logs.output</span>
<span class="line">  forward_to = [loki.process.parse.receiver]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">loki.process &quot;parse&quot; {</span>
<span class="line">  stage.json {</span>
<span class="line">    expressions = {</span>
<span class="line">      level   = &quot;level&quot;,</span>
<span class="line">      message = &quot;msg&quot;,</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  stage.labels {</span>
<span class="line">    values = {</span>
<span class="line">      level = &quot;level&quot;,</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  stage.drop {</span>
<span class="line">    source = &quot;level&quot;</span>
<span class="line">    value  = &quot;debug&quot;</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  forward_to = [loki.write.default.receiver]</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">loki.write &quot;default&quot; {</span>
<span class="line">  endpoint {</span>
<span class="line">    url = &quot;https://loki.example.com/loki/api/v1/push&quot;</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>stage.json</code>으로 JSON 로그를 파싱하고, <code>stage.labels</code>로 파싱 결과 중 라벨로 승격할 값만 골라낸다. 라벨은 인덱스 비용을 직접 좌우하므로(<a href="/study/observability/16-loki-architecture">Loki 아키텍처</a> 참고), <code>message</code>처럼 카디널리티가 높은 필드는 절대 라벨로 승격하지 않고 로그 본문에 그대로 둔다. <code>stage.drop</code>처럼 파이프라인 단계에서 노이즈 로그를 걸러내면 Loki에 도달하는 볼륨 자체를 줄여 저장 비용을 낮출 수 있다.</p><p><img src="`+i+'" alt="로그 파이프라인 흐름 — discovery.kubernetes(Pod 로그 소스) → loki.source.kubernetes → loki.process(stage.json → stage.labels → stage.drop) → loki.write → Loki로 이어지는 컴포넌트 체인"><img src="'+c+`" alt="로그 파이프라인 흐름 — discovery.kubernetes(Pod 로그 소스) → loki.source.kubernetes → loki.process(stage.json → stage.labels → stage.drop) → loki.write → Loki로 이어지는 컴포넌트 체인"></p><h2 id="_3-트레이스-파이프라인-—-otelcol-receiver-→-processor-→-exporter" tabindex="-1"><a class="header-anchor" href="#_3-트레이스-파이프라인-—-otelcol-receiver-→-processor-→-exporter"><span>3. 트레이스 파이프라인 — otelcol.receiver → processor → exporter</span></a></h2><p>트레이스는 <code>otelcol.*</code> 계열로 구성한다. <a href="/study/observability/21-opentelemetry">OpenTelemetry</a> SDK가 보낸 OTLP를 <code>otelcol.receiver.otlp</code>가 받고, 프로세서 체인을 거쳐 <code>otelcol.exporter.otlp</code>가 Tempo로 내보낸다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">otelcol.receiver.otlp &quot;default&quot; {</span>
<span class="line">  grpc {</span>
<span class="line">    endpoint = &quot;0.0.0.0:4317&quot;</span>
<span class="line">  }</span>
<span class="line">  http {</span>
<span class="line">    endpoint = &quot;0.0.0.0:4318&quot;</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  output {</span>
<span class="line">    traces = [otelcol.processor.batch.default.input]</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">otelcol.processor.batch &quot;default&quot; {</span>
<span class="line">  timeout     = &quot;5s&quot;</span>
<span class="line">  send_batch_size = 1024</span>
<span class="line"></span>
<span class="line">  output {</span>
<span class="line">    traces = [otelcol.processor.tail_sampling.default.input]</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">otelcol.exporter.otlp &quot;tempo&quot; {</span>
<span class="line">  client {</span>
<span class="line">    endpoint = &quot;tempo.example.com:4317&quot;</span>
<span class="line">    tls {</span>
<span class="line">      insecure = false</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>otelcol.receiver.otlp</code>가 gRPC(4317)와 HTTP(4318) 두 프로토콜을 동시에 열어두는 것은 OTel Collector와 동일한 관례다. <code>output</code> 블록으로 다음 컴포넌트의 <code>input</code>을 직접 참조하는 것이 <a href="/study/observability/28-alloy-overview">1장</a>에서 본 컴포넌트 그래프 방식이다.</p><h2 id="_4-alloy에서의-tail-sampling-—-otelcol-processor-tail-sampling" tabindex="-1"><a class="header-anchor" href="#_4-alloy에서의-tail-sampling-—-otelcol-processor-tail-sampling"><span>4. Alloy에서의 tail sampling — otelcol.processor.tail_sampling</span></a></h2><p><a href="/study/observability/20-distributed-tracing-basics">분산 트레이싱 기초</a>와 <a href="/study/observability/21-opentelemetry">OpenTelemetry</a>에서 다룬 head sampling(SDK 단에서 확률적으로 미리 결정)과 tail sampling(모든 스팬을 모아 트레이스 완성 후 결정)의 구분을 떠올려보면, tail sampling은 반드시 트레이스 전체 스팬을 한 곳에서 모을 수 있는 중앙 집중 지점이 필요하다. Alloy를 게이트웨이 형태로 배치해 이 역할을 맡기는 것이 실무에서 가장 흔한 tail sampling 구성이다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">otelcol.processor.tail_sampling &quot;default&quot; {</span>
<span class="line">  decision_wait            = &quot;10s&quot;</span>
<span class="line">  num_traces               = 100000</span>
<span class="line">  expected_new_traces_per_sec = 500</span>
<span class="line"></span>
<span class="line">  policy {</span>
<span class="line">    name = &quot;errors&quot;</span>
<span class="line">    type = &quot;status_code&quot;</span>
<span class="line"></span>
<span class="line">    status_code {</span>
<span class="line">      status_codes = [&quot;ERROR&quot;]</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  policy {</span>
<span class="line">    name = &quot;slow-requests&quot;</span>
<span class="line">    type = &quot;latency&quot;</span>
<span class="line"></span>
<span class="line">    latency {</span>
<span class="line">      threshold_ms = 500</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  policy {</span>
<span class="line">    name = &quot;baseline-sample&quot;</span>
<span class="line">    type = &quot;probabilistic&quot;</span>
<span class="line"></span>
<span class="line">    probabilistic {</span>
<span class="line">      sampling_percentage = 10</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line"></span>
<span class="line">  output {</span>
<span class="line">    traces = [otelcol.exporter.otlp.tempo.input]</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>decision_wait</code>(여기서는 10초) 동안 같은 trace ID를 가진 스팬을 모으고, 그 시간이 지나면 정책 목록을 순서대로 평가해 채택 여부를 결정한다. 정책은 OR로 결합되므로 — 에러거나(errors), 느리거나(slow-requests), 아니면 10% 확률로(baseline-sample) — 셋 중 하나라도 맞으면 트레이스 전체가 채택된다. 이 방식은 정상 트레이스는 대부분 버리면서도 &quot;문제가 있었던&quot; 트레이스는 놓치지 않는 실전 샘플링 전략이다.</p><div class="hint-container warning"><p class="hint-container-title">decision_wait와 게이트웨이 레플리카 수의 관계</p><p>tail sampling은 트레이스의 모든 스팬이 같은 Alloy 인스턴스에 도달해야 정확히 동작한다. 게이트웨이를 여러 레플리카로 수평 확장하면 로드밸런서가 같은 trace ID의 스팬을 서로 다른 레플리카로 흩뿌릴 수 있고, 그러면 각 레플리카가 불완전한 스팬 집합만 보고 판단해 샘플링이 왜곡된다. 이를 막으려면 트레이스 ID 기준 로드밸런싱(<code>otelcol.exporter.loadbalancing</code>)을 앞단에 둬 같은 trace ID가 항상 같은 레플리카로 가도록 고정해야 한다.</p></div><h2 id="_5-프로파일-파이프라인-—-pyroscope-scrape-pyroscope-ebpf" tabindex="-1"><a class="header-anchor" href="#_5-프로파일-파이프라인-—-pyroscope-scrape-pyroscope-ebpf"><span>5. 프로파일 파이프라인 — pyroscope.scrape / pyroscope.ebpf</span></a></h2><p>프로파일은 두 갈래로 나뉜다. 애플리케이션이 <a href="/study/observability/25-pyroscope-architecture">Pyroscope</a> SDK로 직접 프로파일을 노출하면 <code>pyroscope.scrape</code>가 주기적으로 긁어오고, 계측 없이 커널 레벨에서 샘플링하려면 <code>pyroscope.ebpf</code>를 쓴다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">// 계측 기반: 애플리케이션이 /debug/pprof 류의 엔드포인트를 노출</span>
<span class="line">pyroscope.scrape &quot;app&quot; {</span>
<span class="line">  targets    = discovery.relabel.app_pods.output</span>
<span class="line">  forward_to = [pyroscope.write.default.receiver]</span>
<span class="line"></span>
<span class="line">  profiling_config {</span>
<span class="line">    profile.cpu {</span>
<span class="line">      enabled = true</span>
<span class="line">    }</span>
<span class="line">    profile.memory {</span>
<span class="line">      enabled = true</span>
<span class="line">    }</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">// 무계측 기반: eBPF로 전체 노드의 프로세스를 샘플링</span>
<span class="line">pyroscope.ebpf &quot;node&quot; {</span>
<span class="line">  forward_to = [pyroscope.write.default.receiver]</span>
<span class="line"></span>
<span class="line">  targets = discovery.relabel.app_pods.output</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">pyroscope.write &quot;default&quot; {</span>
<span class="line">  endpoint {</span>
<span class="line">    url = &quot;https://pyroscope.example.com&quot;</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>pyroscope.scrape</code>는 애플리케이션 코드에 심볼 정보가 남아 있어 라인 단위까지 정밀하지만 계측이 필요하고, <code>pyroscope.ebpf</code>는 계측 없이 노드의 모든 프로세스를 대상으로 CPU 프로파일을 샘플링할 수 있는 대신 심볼 해석 정밀도가 상대적으로 낮다. 이 트레이드오프는 <a href="/study/observability/26-profile-types-ebpf">프로파일 타입과 eBPF</a>에서 더 깊게 다룬다. <code>pyroscope.ebpf</code>는 커널 기능(perf_event_open)에 의존하므로 DaemonSet으로 배치하고 <code>hostPID: true</code>, 적절한 capability(<code>SYS_ADMIN</code> 또는 <code>PERFMON</code>+<code>BPF</code>)를 부여해야 동작한다.</p><h2 id="_6-clustering과-타깃-분배" tabindex="-1"><a class="header-anchor" href="#_6-clustering과-타깃-분배"><span>6. clustering과 타깃 분배</span></a></h2><p>메트릭·로그·프로파일 스크레이프 파이프라인을 모두 StatefulSet 게이트웨이로 운영한다면, 타깃 목록을 레플리카끼리 나눠야 각 인스턴스의 부하가 균등해진다. Alloy clustering을 켜면 <code>prometheus.scrape</code>, <code>pyroscope.scrape</code> 같은 <strong>타깃 기반(target-based)</strong> 컴포넌트가 자동으로 이 분배에 참여한다.</p><div class="language-alloy line-numbers-mode" data-highlighter="prismjs" data-ext="alloy" data-title="alloy"><pre><code><span class="line">alloy {</span>
<span class="line">  clustering {</span>
<span class="line">    enabled = true</span>
<span class="line">  }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><img src="`+o+'" alt="clustering 타깃 분배 시퀀스 — discovery.kubernetes가 타깃 200개를 발견해 Alloy Cluster(3 replica)로 전달하면 컨시스턴트 해싱으로 alloy-0(1~67)·alloy-1(68~134)·alloy-2(135~200)에 소유권을 분배하고 각 레플리카가 자기 몫만 Mimir로 remote_write하며 alloy-1 다운 시 나머지가 재해싱해 흡수"><img src="'+p+'" alt="clustering 타깃 분배 시퀀스 — discovery.kubernetes가 타깃 200개를 발견해 Alloy Cluster(3 replica)로 전달하면 컨시스턴트 해싱으로 alloy-0(1~67)·alloy-1(68~134)·alloy-2(135~200)에 소유권을 분배하고 각 레플리카가 자기 몫만 Mimir로 remote_write하며 alloy-1 다운 시 나머지가 재해싱해 흡수"></p><p>각 레플리카는 전체 타깃 목록을 동일하게 discovery로 받지만, 클러스터 멤버십을 기준으로 컨시스턴트 해싱을 적용해 &quot;이 타깃은 내 몫이 아니다&quot;라고 판단되면 스킵한다. 그 결과 중복 스크레이프 없이 부하가 나뉘고, 레플리카 하나가 사라지면 나머지가 자동으로 그 몫을 흡수한다. 반대로 DaemonSet으로 배치한 노드 로컬 컴포넌트(<code>loki.source.file</code>, <code>pyroscope.ebpf</code>)는 애초에 &quot;이 노드는 이 인스턴스가 담당&quot;이라는 배치 자체가 분배 역할을 하므로 clustering이 필요 없다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>메트릭은 <code>discovery.kubernetes</code> → <code>discovery.relabel</code> → <code>prometheus.scrape</code> → <code>prometheus.remote_write</code> 체인으로 구성한다.</li><li>로그는 <code>loki.source.*</code>로 받아 <code>loki.process</code>의 스테이지 체인(<code>stage.json</code>, <code>stage.labels</code>, <code>stage.drop</code>)으로 다듬고 <code>loki.write</code>로 내보낸다.</li><li>트레이스는 <code>otelcol.receiver.otlp</code> → <code>otelcol.processor.batch</code> → <code>otelcol.exporter.otlp</code> 체인이 기본형이다.</li><li><code>otelcol.processor.tail_sampling</code>은 정책을 OR로 결합해 에러·지연·확률 샘플을 함께 채택하며, 완전한 트레이스가 모이려면 trace ID 기준 로드밸런싱이 전제돼야 한다.</li><li>프로파일은 계측 기반 <code>pyroscope.scrape</code>와 무계측 <code>pyroscope.ebpf</code> 중 정밀도·운영 부담을 저울질해 고른다.</li><li>clustering은 타깃 기반 스크레이프 컴포넌트에만 적용되며, 컨시스턴트 해싱으로 타깃을 레플리카 간에 자동 재분배한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>Alloy 파이프라인을 직접 조립할 수 있게 됐다면, 이제 &quot;그럼 순수 OpenTelemetry Collector와 뭐가 다른가&quot;라는 질문에 답할 차례다. <a href="/study/observability/30-collector-vs-alloy">Collector vs Alloy</a>에서는 두 도구의 관계와 역사, 신호 지원·clustering 기능 비교, 구성 방식 차이, 선택 기준과 마이그레이션 경로를 다룬다.</p>',32)]))}const v=e(r,[["render",d],["__file","29-alloy-pipelines.html.vue"]]),m=JSON.parse('{"path":"/study/observability/29-alloy-pipelines.html","title":"Alloy 파이프라인 구성","lang":"en-US","frontmatter":{"title":"Alloy 파이프라인 구성","description":"prometheus.scrape부터 loki.process, otelcol.processor.tail_sampling, pyroscope.ebpf까지 신호별 Alloy 컴포넌트 체인을 실전 설정으로 조립하고, clustering이 스크레이프 타깃을 여러 레플리카에 분배하는 방식을 다룬다.","date":"2026-07-02T00:00:00.000Z","tags":["Observability","Alloy","Pipeline","Sampling"],"prev":"/study/observability/28-alloy-overview","next":"/study/observability/30-collector-vs-alloy"},"headers":[{"level":1,"title":"Alloy 파이프라인 구성","slug":"alloy-파이프라인-구성","link":"#alloy-파이프라인-구성","children":[{"level":2,"title":"1. 메트릭 파이프라인 — prometheus.scrape → prometheus.remote_write","slug":"_1-메트릭-파이프라인-—-prometheus-scrape-→-prometheus-remote-write","link":"#_1-메트릭-파이프라인-—-prometheus-scrape-→-prometheus-remote-write","children":[]},{"level":2,"title":"2. 로그 파이프라인 — loki.source.* → loki.process → loki.write","slug":"_2-로그-파이프라인-—-loki-source-→-loki-process-→-loki-write","link":"#_2-로그-파이프라인-—-loki-source-→-loki-process-→-loki-write","children":[]},{"level":2,"title":"3. 트레이스 파이프라인 — otelcol.receiver → processor → exporter","slug":"_3-트레이스-파이프라인-—-otelcol-receiver-→-processor-→-exporter","link":"#_3-트레이스-파이프라인-—-otelcol-receiver-→-processor-→-exporter","children":[]},{"level":2,"title":"4. Alloy에서의 tail sampling — otelcol.processor.tail_sampling","slug":"_4-alloy에서의-tail-sampling-—-otelcol-processor-tail-sampling","link":"#_4-alloy에서의-tail-sampling-—-otelcol-processor-tail-sampling","children":[]},{"level":2,"title":"5. 프로파일 파이프라인 — pyroscope.scrape / pyroscope.ebpf","slug":"_5-프로파일-파이프라인-—-pyroscope-scrape-pyroscope-ebpf","link":"#_5-프로파일-파이프라인-—-pyroscope-scrape-pyroscope-ebpf","children":[]},{"level":2,"title":"6. clustering과 타깃 분배","slug":"_6-clustering과-타깃-분배","link":"#_6-clustering과-타깃-분배","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/observability/29-alloy-pipelines.md"}');export{v as comp,m as data};
