import{_ as s,c as e,e as a,o as t}from"./app-BoV2bUm_.js";const l={};function p(o,n){return t(),e("div",null,n[0]||(n[0]=[a(`<h1 id="로깅과-트레이싱" tabindex="-1"><a class="header-anchor" href="#로깅과-트레이싱"><span>로깅과 트레이싱</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>컨테이너 로그가 어떻게 저장되고 <code>kubectl logs</code>가 무엇을 읽는지, 노드 레벨 로깅의 구조와 한계를 이해한다.</li><li>클러스터 레벨 로깅 아키텍처를 EFK와 Loki 두 접근으로 비교한다.</li><li>Fluent Bit·Fluentd 같은 로그 수집 에이전트가 DaemonSet으로 어떻게 동작하는지 익힌다.</li><li>OpenTelemetry 기반 분산 트레이싱의 개념과 컨텍스트 전파를 다룬다.</li></ul></div><h2 id="_1-컨테이너-로그-구조와-노드-레벨-로깅" tabindex="-1"><a class="header-anchor" href="#_1-컨테이너-로그-구조와-노드-레벨-로깅"><span>1. 컨테이너 로그 구조와 노드 레벨 로깅</span></a></h2><p>쿠버네티스 로깅의 출발점은 단순하다. 컨테이너가 표준 출력(<code>stdout</code>)과 표준 에러(<code>stderr</code>)로 쓴 내용을 컨테이너 런타임이 노드의 파일로 기록한다. <code>kubectl logs</code>는 그 파일을 kubelet을 통해 읽어오는 것뿐이다. 전체 개념은 <a href="https://kubernetes.io/docs/concepts/cluster-administration/logging/" target="_blank" rel="noopener noreferrer">Logging Architecture 문서</a>에 정리돼 있다.</p><pre class="mermaid">flowchart LR
    app[&quot;컨테이너\\nstdout/stderr&quot;]
    runtime[&quot;컨테이너 런타임\\n(containerd)&quot;]
    file[&quot;/var/log/pods/...\\n.log 파일&quot;]
    kubelet[&quot;kubelet&quot;]
    kubectl[&quot;kubectl logs&quot;]
    app --&gt; runtime --&gt; file
    kubelet --&gt; file
    kubectl --&gt; kubelet
</pre><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 노드에서 실제 로그 파일 위치</span></span>
<span class="line"><span class="token comment"># /var/log/pods/&lt;namespace&gt;_&lt;pod&gt;_&lt;uid&gt;/&lt;container&gt;/0.log</span></span>
<span class="line"></span>
<span class="line">kubectl logs my-pod <span class="token parameter variable">-c</span> my-container          <span class="token comment"># 특정 컨테이너</span></span>
<span class="line">kubectl logs my-pod <span class="token parameter variable">--previous</span>               <span class="token comment"># 재시작 전 컨테이너의 로그</span></span>
<span class="line">kubectl logs <span class="token parameter variable">-f</span> my-pod <span class="token parameter variable">--tail</span><span class="token operator">=</span><span class="token number">100</span>            <span class="token comment"># 실시간 추적, 마지막 100줄부터</span></span>
<span class="line">kubectl logs <span class="token parameter variable">-l</span> <span class="token assign-left variable">app</span><span class="token operator">=</span>my-app --max-log-requests<span class="token operator">=</span><span class="token number">10</span>   <span class="token comment"># 라벨로 여러 Pod</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이 방식이 <strong>노드 레벨 로깅</strong>이다. kubelet은 로그 파일을 로테이션하고(기본적으로 컨테이너당 일정 크기·개수 제한), 컨테이너가 삭제되면 그 로그도 함께 사라진다.</p><div class="hint-container warning"><p class="hint-container-title">노드 레벨 로깅의 근본 한계</p><p>노드 레벨 로깅에는 영속성이 없다. Pod가 evict되거나 노드가 죽으면 로그가 함께 사라진다. 로그 로테이션으로 오래된 로그도 지워진다. 그래서 디버깅을 과거로 거슬러 올라가려면 로그를 클러스터 외부의 중앙 저장소로 내보내는 <strong>클러스터 레벨 로깅</strong>이 반드시 필요하다.</p></div><p>또 하나 중요한 원칙은 애플리케이션이 <strong>로그를 파일이 아니라 stdout/stderr로 내보내야</strong> 한다는 것이다(<a href="https://12factor.net/logs" target="_blank" rel="noopener noreferrer">Twelve-Factor App</a>의 로그 원칙). 컨테이너 안에서 파일로 쓰면 수집 경로 밖에 놓여 사라진다.</p><h2 id="_2-클러스터-로깅-아키텍처-—-efk와-loki" tabindex="-1"><a class="header-anchor" href="#_2-클러스터-로깅-아키텍처-—-efk와-loki"><span>2. 클러스터 로깅 아키텍처 — EFK와 Loki</span></a></h2><p>노드 레벨 로그를 모아 중앙에서 검색·보관하는 것이 클러스터 레벨 로깅이다. 쿠버네티스는 이 기능을 내장하지 않으므로 별도 스택을 구성한다. 가장 흔한 두 갈래가 EFK와 Loki다.</p><p><strong>EFK 스택.</strong> Elasticsearch(저장·색인) + Fluentd/Fluent Bit(수집) + Kibana(시각화). 모든 로그 라인을 전문(full-text) 색인하므로 임의 필드로 강력하게 검색할 수 있다. 대신 색인 비용이 커서 저장소·메모리 요구가 높다.</p><p><strong>Loki 스택.</strong> Grafana Loki(저장) + Promtail/Fluent Bit(수집) + Grafana(시각화). Loki는 &quot;로그 본문은 색인하지 않고 라벨만 색인한다&quot;는 발상으로 설계됐다. Prometheus와 같은 라벨 모델을 써서 메트릭·로그를 한 Grafana에서 같은 라벨로 묶어 볼 수 있다. 저장 비용이 낮지만, 전문 검색 대신 라벨로 좁힌 뒤 grep 식으로 본문을 훑는다.</p><table><thead><tr><th>기준</th><th>EFK (Elasticsearch)</th><th>Loki</th></tr></thead><tbody><tr><td>색인 방식</td><td>로그 본문 전체 색인</td><td>라벨만 색인</td></tr><tr><td>검색 성격</td><td>임의 필드 전문 검색 강력</td><td>라벨로 좁힌 뒤 본문 스캔</td></tr><tr><td>저장 비용</td><td>높음</td><td>낮음</td></tr><tr><td>메트릭 연계</td><td>별도</td><td>Prometheus 라벨과 동일 모델</td></tr><tr><td>질의 언어</td><td>Lucene / KQL</td><td>LogQL</td></tr></tbody></table><pre class="mermaid">flowchart TB
    subgraph nodes[&quot;각 노드&quot;]
        agent[&quot;수집 에이전트\\n(DaemonSet)&quot;]
    end
    subgraph efk[&quot;EFK 경로&quot;]
        es[&quot;Elasticsearch&quot;]
        kib[&quot;Kibana&quot;]
        es --&gt; kib
    end
    subgraph loki[&quot;Loki 경로&quot;]
        lk[&quot;Loki&quot;]
        gr[&quot;Grafana&quot;]
        lk --&gt; gr
    end
    agent --&gt;|&quot;전문 색인&quot;| es
    agent --&gt;|&quot;라벨만 색인&quot;| lk
</pre><p>선택 기준은 단순하다. 임의 필드로 정밀하게 파고드는 검색이 핵심이면 EFK, 비용 효율과 메트릭·로그 통합 뷰가 중요하면 Loki가 유리하다.</p><h2 id="_3-로그-수집-에이전트-—-fluent-bit와-fluentd" tabindex="-1"><a class="header-anchor" href="#_3-로그-수집-에이전트-—-fluent-bit와-fluentd"><span>3. 로그 수집 에이전트 — Fluent Bit와 Fluentd</span></a></h2><p>수집 에이전트는 거의 항상 <strong>DaemonSet</strong>으로 배포된다. 모든 노드에 하나씩 떠서 그 노드의 <code>/var/log/pods</code> 아래 로그 파일을 tail하고, 파싱·필터·풍부화를 거쳐 백엔드로 전송한다.</p><p><strong>Fluentd</strong>는 루비/C 혼합으로 만들어진 성숙한 수집기로 플러그인 생태계가 방대하다. <strong>Fluent Bit</strong>는 C로 작성된 경량 버전으로 메모리 사용이 훨씬 적어, 노드마다 떠야 하는 DaemonSet에 적합하다. 실무에서는 노드 에이전트로 Fluent Bit를 쓰고, 무거운 가공이 필요할 때 중앙에 Fluentd 애그리게이터를 두는 조합이 흔하다.</p><pre class="mermaid">flowchart LR
    f1[&quot;/var/log/pods/*.log&quot;]
    parser[&quot;파서\\n(JSON·정규식)&quot;]
    filter[&quot;필터\\n쿠버네티스 메타데이터 추가&quot;]
    out[&quot;출력\\n(ES / Loki)&quot;]
    f1 --&gt;|&quot;tail&quot;| parser --&gt; filter --&gt; out
</pre><p>핵심 단계는 <strong>쿠버네티스 메타데이터 풍부화</strong>다. 로그 파일 경로에서 Pod·네임스페이스·컨테이너 이름을 뽑고, apiserver를 질의해 라벨·어노테이션을 붙인다. 이 덕분에 나중에 &quot;네임스페이스 prod, app=checkout 라벨의 로그만&quot; 같은 필터가 가능해진다.</p><div class="language-ini line-numbers-mode" data-highlighter="prismjs" data-ext="ini" data-title="ini"><pre><code><span class="line"><span class="token comment"># Fluent Bit 설정 예시</span></span>
<span class="line"><span class="token section"><span class="token punctuation">[</span><span class="token section-name selector">INPUT</span><span class="token punctuation">]</span></span></span>
<span class="line">    Name              tail</span>
<span class="line">    Path              /var/log/containers/*.log</span>
<span class="line">    Parser            cri</span>
<span class="line">    Tag               kube.*</span>
<span class="line"></span>
<span class="line"><span class="token section"><span class="token punctuation">[</span><span class="token section-name selector">FILTER</span><span class="token punctuation">]</span></span></span>
<span class="line">    Name              kubernetes</span>
<span class="line">    Match             kube.*</span>
<span class="line">    Merge_Log         On</span>
<span class="line">    Keep_Log          Off</span>
<span class="line"></span>
<span class="line"><span class="token section"><span class="token punctuation">[</span><span class="token section-name selector">OUTPUT</span><span class="token punctuation">]</span></span></span>
<span class="line">    Name              loki</span>
<span class="line">    Match             kube.*</span>
<span class="line">    Host              loki.logging.svc</span>
<span class="line">    <span class="token key attr-name">Labels            job</span><span class="token punctuation">=</span><span class="token value attr-value">fluentbit, $kubernetes[&#39;namespace_name&#39;]</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>수집 위치를 노드 에이전트가 아니라 애플리케이션 사이드카로 둘 수도 있지만, 노드당 하나의 DaemonSet 에이전트가 자원 효율과 운영 단순성에서 표준이다. 사이드카는 같은 Pod 안 여러 컨테이너가 서로 다른 로그 파일을 쓰는 특수 상황에 보조적으로 쓴다.</p><h2 id="_4-로그의-구조화와-상관관계" tabindex="-1"><a class="header-anchor" href="#_4-로그의-구조화와-상관관계"><span>4. 로그의 구조화와 상관관계</span></a></h2><p>로그를 중앙에 모으는 것만으로는 부족하다. 분산 시스템에서 한 요청은 여러 서비스를 거치므로, 흩어진 로그를 하나의 요청으로 묶는 <strong>상관관계(correlation)</strong>가 중요하다.</p><p>첫째, <strong>구조화 로깅</strong>이다. 평문 대신 JSON으로 로그를 내보내면 수집기가 필드를 그대로 색인하고, 백엔드에서 필드 기준 검색·집계가 쉬워진다.</p><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span><span class="token property">&quot;level&quot;</span><span class="token operator">:</span><span class="token string">&quot;error&quot;</span><span class="token punctuation">,</span><span class="token property">&quot;ts&quot;</span><span class="token operator">:</span><span class="token string">&quot;2026-06-15T10:00:00Z&quot;</span><span class="token punctuation">,</span><span class="token property">&quot;trace_id&quot;</span><span class="token operator">:</span><span class="token string">&quot;a1b2c3&quot;</span><span class="token punctuation">,</span><span class="token property">&quot;msg&quot;</span><span class="token operator">:</span><span class="token string">&quot;db timeout&quot;</span><span class="token punctuation">,</span><span class="token property">&quot;service&quot;</span><span class="token operator">:</span><span class="token string">&quot;checkout&quot;</span><span class="token punctuation">,</span><span class="token property">&quot;user_id&quot;</span><span class="token operator">:</span><span class="token string">&quot;42&quot;</span><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><p>둘째, <strong>trace_id 전파</strong>다. 모든 로그 라인에 같은 요청의 <code>trace_id</code>를 심으면, 로그와 트레이스를 같은 ID로 묶어 &quot;이 느린 트레이스에서 어떤 에러 로그가 났나&quot;를 한 번에 추적할 수 있다. 이것이 다음 절의 분산 트레이싱과 로그를 연결하는 다리다.</p><pre class="mermaid">flowchart LR
    req[&quot;요청 trace_id=a1b2c3&quot;]
    s1[&quot;gateway 로그\\ntrace_id=a1b2c3&quot;]
    s2[&quot;checkout 로그\\ntrace_id=a1b2c3&quot;]
    s3[&quot;payment 로그\\ntrace_id=a1b2c3&quot;]
    req --&gt; s1 --&gt; s2 --&gt; s3
    s1 &amp; s2 &amp; s3 --&gt; view[&quot;같은 trace_id로\\n전 구간 로그 조회&quot;]
</pre><p>구조화 + trace_id가 갖춰지면, 로그는 단순 텍스트 더미에서 질의 가능한 데이터로 바뀐다.</p><h2 id="_5-분산-트레이싱과-opentelemetry" tabindex="-1"><a class="header-anchor" href="#_5-분산-트레이싱과-opentelemetry"><span>5. 분산 트레이싱과 OpenTelemetry</span></a></h2><p>메트릭은 &quot;얼마나&quot;, 로그는 &quot;무슨 일이&quot;를 말하지만, 마이크로서비스에서 &quot;요청이 어느 서비스에서 느려졌나&quot;는 <strong>분산 트레이싱</strong>이 답한다. 한 요청이 거치는 모든 서비스 호출을 하나의 <strong>트레이스(trace)</strong>로, 각 구간을 <strong>스팬(span)</strong>으로 기록한다.</p><p><strong>OpenTelemetry(OTel)</strong>는 트레이스·메트릭·로그를 표준 방식으로 생성·수집하는 벤더 중립 표준이자 도구 모음이다. 계측 라이브러리로 애플리케이션에서 스팬을 만들고, <strong>OpenTelemetry Collector</strong>가 이를 받아 가공·배치 후 백엔드(Jaeger, Tempo 등)로 보낸다. 쿠버네티스에서 <a href="https://kubernetes.io/docs/concepts/cluster-administration/system-traces/" target="_blank" rel="noopener noreferrer">트레이싱은 컨트롤플레인 컴포넌트 자체에도 적용</a>할 수 있다.</p><p>핵심 메커니즘은 <strong>컨텍스트 전파</strong>다. 서비스 A가 B를 호출할 때 trace_id와 span_id를 HTTP 헤더(W3C <code>traceparent</code>)에 실어 넘긴다. B는 그 부모 컨텍스트를 이어받아 자식 스팬을 만든다. 이렇게 ID가 전 구간 연결돼 하나의 트레이스로 조립된다.</p><pre class="mermaid">sequenceDiagram
    participant C as Client
    participant G as Gateway
    participant O as Order
    participant P as Payment
    C-&gt;&gt;G: 요청 (새 trace 시작)
    Note over G: span: gateway\\ntraceparent 생성
    G-&gt;&gt;O: traceparent 헤더 전파
    Note over O: span: order (부모=gateway)
    O-&gt;&gt;P: traceparent 헤더 전파
    Note over P: span: payment (부모=order)
    P--&gt;&gt;O: 응답
    O--&gt;&gt;G: 응답
    G--&gt;&gt;C: 응답
    Note over G,P: 모든 span을 OTel Collector로 → 하나의 trace 조립
</pre><p>쿠버네티스에 OTel Collector는 보통 DaemonSet(노드 로컬 수신) 또는 Deployment(중앙 게이트웨이)로 배포한다. 계측 코드를 손대지 않고도 사이드카 자동 계측을 주입하는 <a href="https://github.com/open-telemetry/opentelemetry-operator" target="_blank" rel="noopener noreferrer">OpenTelemetry Operator</a>도 널리 쓰인다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token comment"># OTel Collector 파이프라인 개념</span></span>
<span class="line"><span class="token key atrule">receivers</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">otlp</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">protocols</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">grpc</span><span class="token punctuation">:</span></span>
<span class="line"><span class="token key atrule">processors</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">batch</span><span class="token punctuation">:</span></span>
<span class="line"><span class="token key atrule">exporters</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">otlp/tempo</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">endpoint</span><span class="token punctuation">:</span> tempo.tracing.svc<span class="token punctuation">:</span><span class="token number">4317</span></span>
<span class="line"><span class="token key atrule">service</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">pipelines</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">traces</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">receivers</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>otlp<span class="token punctuation">]</span></span>
<span class="line">      <span class="token key atrule">processors</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>batch<span class="token punctuation">]</span></span>
<span class="line">      <span class="token key atrule">exporters</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>otlp/tempo<span class="token punctuation">]</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>메트릭·로그·트레이스 세 신호를 같은 라벨·같은 trace_id로 묶으면 관측성의 세 기둥이 하나로 연결된다. Grafana에서 메트릭 이상 → 해당 시점 로그 → 그 로그의 trace_id로 트레이스까지 한 흐름으로 내려가는 것이 이상적인 디버깅 동선이다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>컨테이너 로그는 stdout/stderr가 노드 파일로 기록된 것이며, <code>kubectl logs</code>는 그 파일을 kubelet 통해 읽는다 — 노드 레벨 로깅은 영속성이 없다.</li><li>클러스터 레벨 로깅은 EFK(본문 전문 색인, 강력한 검색)와 Loki(라벨만 색인, 저비용·메트릭 통합)로 갈린다.</li><li>수집 에이전트는 DaemonSet으로 배포되며 Fluent Bit(경량)·Fluentd(가공)가 표준, 쿠버네티스 메타데이터 풍부화가 핵심 단계다.</li><li>구조화 로깅과 trace_id 전파가 흩어진 로그를 질의 가능한 데이터로 만들고 트레이스와 연결한다.</li><li>OpenTelemetry는 트레이스·메트릭·로그의 벤더 중립 표준으로, 컨텍스트 전파(traceparent)로 요청을 전 구간 하나의 트레이스로 조립한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p>메트릭·로그·트레이스로 관측성을 갖췄다면, 이제 실제로 무언가 고장 났을 때 그 신호들로 문제를 진단하는 절차가 필요하다. 다음 챕터 <a href="/study/kubernetes/42-troubleshooting">트러블슈팅</a>에서는 Pod·노드·네트워크·컨트롤플레인 문제를 단계적으로 진단하는 방법과 <code>kubectl debug</code>·임시 컨테이너 활용을 다룬다.</p>`,41)]))}const r=s(l,[["render",p],["__file","41-logging-tracing.html.vue"]]),c=JSON.parse('{"path":"/study/kubernetes/41-logging-tracing.html","title":"로깅과 트레이싱","lang":"en-US","frontmatter":{"title":"로깅과 트레이싱","description":"컨테이너 로그의 구조와 노드 레벨 로깅의 한계, EFK·Loki로 대표되는 클러스터 로깅 아키텍처, Fluent Bit·Fluentd 같은 로그 수집 에이전트의 동작, 그리고 OpenTelemetry 기반 분산 트레이싱까지 관측성의 로그·트레이스 축을 깊게 다룬다.","date":"2026-06-15T00:00:00.000Z","tags":["Kubernetes","Logging","Tracing","EFK","Loki","OpenTelemetry","Observability"],"prev":"/study/kubernetes/40-metrics-monitoring","next":"/study/kubernetes/42-troubleshooting"},"headers":[{"level":1,"title":"로깅과 트레이싱","slug":"로깅과-트레이싱","link":"#로깅과-트레이싱","children":[{"level":2,"title":"1. 컨테이너 로그 구조와 노드 레벨 로깅","slug":"_1-컨테이너-로그-구조와-노드-레벨-로깅","link":"#_1-컨테이너-로그-구조와-노드-레벨-로깅","children":[]},{"level":2,"title":"2. 클러스터 로깅 아키텍처 — EFK와 Loki","slug":"_2-클러스터-로깅-아키텍처-—-efk와-loki","link":"#_2-클러스터-로깅-아키텍처-—-efk와-loki","children":[]},{"level":2,"title":"3. 로그 수집 에이전트 — Fluent Bit와 Fluentd","slug":"_3-로그-수집-에이전트-—-fluent-bit와-fluentd","link":"#_3-로그-수집-에이전트-—-fluent-bit와-fluentd","children":[]},{"level":2,"title":"4. 로그의 구조화와 상관관계","slug":"_4-로그의-구조화와-상관관계","link":"#_4-로그의-구조화와-상관관계","children":[]},{"level":2,"title":"5. 분산 트레이싱과 OpenTelemetry","slug":"_5-분산-트레이싱과-opentelemetry","link":"#_5-분산-트레이싱과-opentelemetry","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/kubernetes/41-logging-tracing.md"}');export{r as comp,c as data};
