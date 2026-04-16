import{_ as a,c as e,e as s,o as n}from"./app-CtpBQ_kQ.js";const l={};function i(r,t){return n(),e("div",null,t[0]||(t[0]=[s(`<h1 id="에이전트-간-소통-—-레지스트리-훅-방식" tabindex="-1"><a class="header-anchor" href="#에이전트-간-소통-—-레지스트리-훅-방식"><span>에이전트 간 소통 — 레지스트리 훅 방식</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>에이전트 없는 라우팅 구조에서 발생하는 두 가지 핵심 문제를 설명할 수 있다.</li><li>레지스트리 기반 통신 방식이 다른 방식 대비 왜 채택되었는지 근거를 설명할 수 있다.</li><li>TeamCreate 중복 방지 흐름과 훅의 역할을 순서대로 설명할 수 있다.</li><li>stale 에이전트 감지 기준과 처리 방법을 설명할 수 있다.</li></ul></div><h2 id="_1-핵심-문제-오케스트레이터는-누구에게-말을-거는가" tabindex="-1"><a class="header-anchor" href="#_1-핵심-문제-오케스트레이터는-누구에게-말을-거는가"><span>1. 핵심 문제: 오케스트레이터는 누구에게 말을 거는가</span></a></h2><p>에이전트 시스템을 처음 설계할 때 빠지기 쉬운 함정이 있다. Orchestrator가 작업을 위임하려 할 때, 어디로 보내야 하는지 알 수 없다는 것이다.</p><p><strong>문제 1: 라우팅 불가</strong></p><p>Orchestrator가 &quot;dev 에이전트에게 이 작업을 보내라&quot;고 결정했다고 가정한다. 그런데 dev 에이전트가 현재 실행 중인지, 어떤 ID를 가지는지, 활성 상태인지 알 방법이 없다. Orchestrator는 추측에 의존하거나 매번 새로 만들게 된다.</p><p><strong>문제 2: TeamCreate 중복 호출</strong></p><p>dev 에이전트가 이미 실행 중인데도 Orchestrator가 TeamCreate(type=&quot;dev&quot;)를 다시 호출한다. 같은 역할의 에이전트가 중복 생성되면 작업이 분산되거나 충돌한다.</p><p>두 문제의 공통 원인은 에이전트 레지스트리가 없다는 것이다.</p><pre class="mermaid">flowchart TD
    O[Orchestrator] --&gt;|&quot;dev 에이전트에게 보내야 한다&quot;| Q{dev 에이전트가&lt;br&gt;어디 있는가?}
    Q --&gt;|&quot;모른다&quot;| C1[TeamCreate dev 호출]
    Q --&gt;|&quot;기억한다&quot;| C2[이전 ID로 SendMessage]
    C1 --&gt;|&quot;이미 존재하면&quot;| Dup[중복 에이전트 생성&lt;br&gt;작업 충돌 발생]
    C2 --&gt;|&quot;에이전트가 종료됐으면&quot;| Dead[메시지 유실&lt;br&gt;응답 없음]
</pre><h2 id="_2-세-가지-통신-방식-비교" tabindex="-1"><a class="header-anchor" href="#_2-세-가지-통신-방식-비교"><span>2. 세 가지 통신 방식 비교</span></a></h2><p>세 가지 설계 방식을 검토했다.</p><p><strong>방식 A (채택): 에이전트 레지스트리</strong></p><p>에이전트가 생성될 때 중앙 레지스트리에 등록한다. Orchestrator는 레지스트리를 조회해 대상 에이전트의 ID를 얻은 뒤 통신한다.</p><p><strong>방식 B: 트리거 기반 훅</strong></p><p>특정 이벤트가 발생하면 미리 등록한 훅이 해당 에이전트를 깨운다. 이벤트 정의가 명확할 때 유효하지만, 복잡한 라우팅 조건에는 적합하지 않다.</p><p><strong>방식 C: 브로드캐스트 + 훅 필터</strong></p><p>Orchestrator가 전체에 메시지를 뿌리고, 각 에이전트가 자신에게 해당하는 메시지를 훅으로 필터링한다. 단순하지만 불필요한 메시지가 모든 에이전트에 전달된다.</p><table><thead><tr><th>기준</th><th>방식 A (레지스트리)</th><th>방식 B (트리거 훅)</th><th>방식 C (브로드캐스트)</th></tr></thead><tbody><tr><td>복잡도</td><td>중간</td><td>낮음</td><td>낮음</td></tr><tr><td>확장성</td><td>높음</td><td>낮음</td><td>중간</td></tr><tr><td>디버깅 난이도</td><td>낮음 (레지스트리 조회)</td><td>중간</td><td>높음 (메시지 추적 어려움)</td></tr><tr><td>중복 방지</td><td>가능</td><td>불가</td><td>불가</td></tr><tr><td>stale 감지</td><td>가능</td><td>불가</td><td>불가</td></tr></tbody></table><p>방식 A를 채택한 이유는 다음과 같다. 에이전트 ID를 레지스트리에서 항상 조회하므로 Orchestrator가 에이전트 상태를 기억할 필요가 없다. 중복 생성과 stale 감지를 같은 메커니즘으로 처리할 수 있으며, 레지스트리 파일을 직접 확인하여 현재 상태를 디버깅할 수 있다.</p><h2 id="_3-레지스트리-아키텍처-방식-a" tabindex="-1"><a class="header-anchor" href="#_3-레지스트리-아키텍처-방식-a"><span>3. 레지스트리 아키텍처 (방식 A)</span></a></h2><h3 id="파일-구조" tabindex="-1"><a class="header-anchor" href="#파일-구조"><span>파일 구조</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">~/.claude/</span>
<span class="line">└── registry/</span>
<span class="line">    ├── team-a/agents.json</span>
<span class="line">    ├── team-b/agents.json</span>
<span class="line">    └── default/agents.json</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>레지스트리는 전역 위치(<code>~/.claude/registry/</code>)에 존재하지만 팀별로 디렉터리를 분리한다. 전역에 두는 이유는 훅 프로세스가 어느 작업 디렉터리에서 실행되더라도 동일한 레지스트리에 접근할 수 있어야 하기 때문이다. 팀별로 분리하는 이유는 서로 다른 Squad가 동일한 역할명(예: dev)의 에이전트를 각자 운영할 수 있어야 하기 때문이다.</p><h3 id="agents-json-형식" tabindex="-1"><a class="header-anchor" href="#agents-json-형식"><span>agents.json 형식</span></a></h3><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span></span>
<span class="line">  <span class="token property">&quot;dev&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;id&quot;</span><span class="token operator">:</span> <span class="token string">&quot;abc123&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;status&quot;</span><span class="token operator">:</span> <span class="token string">&quot;active&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;created_at&quot;</span><span class="token operator">:</span> <span class="token string">&quot;2026-04-16T10:00:00Z&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;last_ping&quot;</span><span class="token operator">:</span> <span class="token string">&quot;2026-04-16T10:04:30Z&quot;</span></span>
<span class="line">  <span class="token punctuation">}</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;verifier&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;id&quot;</span><span class="token operator">:</span> <span class="token string">&quot;def456&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;status&quot;</span><span class="token operator">:</span> <span class="token string">&quot;active&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;created_at&quot;</span><span class="token operator">:</span> <span class="token string">&quot;2026-04-16T10:01:00Z&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;last_ping&quot;</span><span class="token operator">:</span> <span class="token string">&quot;2026-04-16T10:04:55Z&quot;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><ul><li><code>id</code>: SendMessage 호출 시 사용하는 에이전트 식별자.</li><li><code>status</code>: <code>active</code> | <code>stale</code> | <code>terminated</code>.</li><li><code>created_at</code>: 에이전트 생성 시각. 중복 감지 시 참고한다.</li><li><code>last_ping</code>: 마지막 활동 시각. stale 판정 기준이다.</li></ul><h2 id="_4-teamcreate-중복-방지-흐름" tabindex="-1"><a class="header-anchor" href="#_4-teamcreate-중복-방지-흐름"><span>4. TeamCreate 중복 방지 흐름</span></a></h2><p>Orchestrator가 TeamCreate를 호출하면 PreToolUse 훅이 발동한다. 훅은 레지스트리를 조회해 동일 역할의 에이전트가 이미 존재하는지 확인한 뒤 처리를 결정한다.</p><pre class="mermaid">sequenceDiagram
    participant O as Orchestrator
    participant H as PreToolUse 훅
    participant R as Registry
    participant T as TeamCreate

    O-&gt;&gt;H: TeamCreate(type=&quot;dev&quot;) 호출
    H-&gt;&gt;R: registry/default/agents.json 조회
    alt dev 에이전트 존재 (active)
        R--&gt;&gt;H: id: &quot;abc123&quot;
        H--&gt;&gt;O: 차단 — 기존 id &quot;abc123&quot; 반환
        O-&gt;&gt;O: SendMessage(&quot;abc123&quot;, 작업)
    else dev 에이전트 없음
        R--&gt;&gt;H: 항목 없음
        H-&gt;&gt;T: TeamCreate 허용
        T--&gt;&gt;H: 새 에이전트 id: &quot;xyz789&quot; 생성
        H-&gt;&gt;R: registry에 dev 항목 등록
        H--&gt;&gt;O: id &quot;xyz789&quot; 반환
        O-&gt;&gt;O: SendMessage(&quot;xyz789&quot;, 작업)
    end
</pre><p>훅이 TeamCreate를 차단하면 Orchestrator는 새 에이전트를 만들지 않고, 레지스트리에서 반환받은 기존 ID로 즉시 SendMessage를 호출한다. Orchestrator는 에이전트가 새로 만들어졌는지, 기존 것을 재사용했는지 알 필요가 없다.</p><h2 id="_5-stale-에이전트-감지" tabindex="-1"><a class="header-anchor" href="#_5-stale-에이전트-감지"><span>5. Stale 에이전트 감지</span></a></h2><h3 id="stale-정의" tabindex="-1"><a class="header-anchor" href="#stale-정의"><span>stale 정의</span></a></h3><p><code>last_ping</code>이 임계값(기본 5분) 이상 갱신되지 않은 에이전트를 stale로 판정한다. stale 에이전트는 응답하지 않을 가능성이 높으므로 재생성 대상이 된다.</p><h3 id="stale-감지-및-처리-흐름" tabindex="-1"><a class="header-anchor" href="#stale-감지-및-처리-흐름"><span>stale 감지 및 처리 흐름</span></a></h3><ol><li>PreToolUse 훅이 레지스트리에서 dev 항목을 발견한다.</li><li><code>last_ping</code>과 현재 시각의 차이를 계산한다.</li><li>차이가 임계값 이상이면 stale로 판정한다.</li><li>stale 항목을 레지스트리에서 삭제한다.</li><li>TeamCreate를 허용하여 새 에이전트를 생성한다.</li><li>새 항목을 레지스트리에 등록한다.</li></ol><div class="hint-container warning"><p class="hint-container-title">stale 임계값 설정 기준</p><p>임계값이 너무 짧으면 정상 작동 중인 에이전트를 stale로 오판한다. 임계값이 너무 길면 실제로 종료된 에이전트를 오래 유지한다. 팀 작업 특성에 따라 조정하되, 에이전트가 가장 오래 응답하지 않는 정상 케이스(예: 긴 빌드 작업)를 기준으로 설정한다.</p></div><h3 id="last-ping-갱신-방법" tabindex="-1"><a class="header-anchor" href="#last-ping-갱신-방법"><span>last_ping 갱신 방법</span></a></h3><p>에이전트가 도구를 사용할 때마다 PostToolUse 훅이 발동한다. 훅은 해당 에이전트의 <code>last_ping</code>을 현재 시각으로 갱신한다. 에이전트가 작업 중인 동안에는 stale로 판정되지 않는다.</p><pre class="mermaid">sequenceDiagram
    participant E as Executor(dev)
    participant H as PostToolUse 훅
    participant R as Registry

    E-&gt;&gt;E: 도구 실행 (예: 파일 쓰기)
    E-&gt;&gt;H: PostToolUse 이벤트 발생
    H-&gt;&gt;R: dev.last_ping = 현재 시각으로 갱신
    R--&gt;&gt;H: 갱신 완료
    Note over E,R: 에이전트가 활동하는 한&lt;br&gt;stale 판정되지 않는다
</pre><h2 id="_6-완전한-소통-흐름" tabindex="-1"><a class="header-anchor" href="#_6-완전한-소통-흐름"><span>6. 완전한 소통 흐름</span></a></h2><p>Orchestrator가 작업을 위임하는 전체 흐름을 처음부터 끝까지 정리한다.</p><pre class="mermaid">sequenceDiagram
    participant O as Orchestrator
    participant PH as PreToolUse 훅
    participant R as Registry
    participant TC as TeamCreate
    participant E as Executor(dev)
    participant V as Verifier

    O-&gt;&gt;PH: TeamCreate(type=&quot;dev&quot;) 요청
    PH-&gt;&gt;R: 레지스트리 조회
    alt 에이전트 없거나 stale
        PH-&gt;&gt;TC: TeamCreate 허용
        TC--&gt;&gt;PH: id: &quot;abc123&quot;
        PH-&gt;&gt;R: 레지스트리 등록
    else 에이전트 active
        PH-&gt;&gt;R: 기존 id 조회
    end
    PH--&gt;&gt;O: id: &quot;abc123&quot; 반환
    O-&gt;&gt;E: SendMessage(&quot;abc123&quot;, 작업 내용)
    E-&gt;&gt;E: 작업 실행
    Note over E,R: PostToolUse 훅으로&lt;br&gt;last_ping 갱신
    E--&gt;&gt;O: 결과물 + 증거 반환
    O-&gt;&gt;V: 결과물 전달 (동일 방식으로 Verifier ID 조회)
    V--&gt;&gt;O: 완료 선언 또는 피드백
</pre><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>레지스트리가 없으면 Orchestrator는 에이전트 위치를 알 수 없고, 중복 생성과 메시지 유실이 반복된다.</li><li>PreToolUse 훅이 TeamCreate를 가로채 레지스트리를 조회하고, 중복이면 차단하고 기존 ID를 반환한다.</li><li>stale 에이전트는 <code>last_ping</code> 임계값 초과로 감지하며, 감지 즉시 삭제하고 재생성을 허용한다.</li><li>PostToolUse 훅이 에이전트 활동마다 <code>last_ping</code>을 갱신하여 정상 에이전트가 stale 판정되는 것을 방지한다.</li><li>Orchestrator는 에이전트 상태를 기억하지 않는다. 항상 레지스트리를 조회해 ID를 얻는다.</li></ul><p>다음 챕터: <a href="/study/ai-agent-workflow/04-registry-hook">CH4. TypeScript 레지스트리 훅 구현</a></p></div>`,44)]))}const p=a(l,[["render",i],["__file","03-communication.html.vue"]]),c=JSON.parse('{"path":"/study/ai-agent-workflow/03-communication.html","title":"CH3. 에이전트 간 소통 — 레지스트리 훅 방식","lang":"en-US","frontmatter":{"title":"CH3. 에이전트 간 소통 — 레지스트리 훅 방식","description":"오케스트레이터가 어떻게 올바른 에이전트를 찾고 통신하는가. 레지스트리 설계와 두 가지 핵심 문제를 해결한다","date":"2026-04-16T00:00:00.000Z","tags":["AI","Agent","Registry","Hook","Communication"]},"headers":[{"level":1,"title":"에이전트 간 소통 — 레지스트리 훅 방식","slug":"에이전트-간-소통-—-레지스트리-훅-방식","link":"#에이전트-간-소통-—-레지스트리-훅-방식","children":[{"level":2,"title":"1. 핵심 문제: 오케스트레이터는 누구에게 말을 거는가","slug":"_1-핵심-문제-오케스트레이터는-누구에게-말을-거는가","link":"#_1-핵심-문제-오케스트레이터는-누구에게-말을-거는가","children":[]},{"level":2,"title":"2. 세 가지 통신 방식 비교","slug":"_2-세-가지-통신-방식-비교","link":"#_2-세-가지-통신-방식-비교","children":[]},{"level":2,"title":"3. 레지스트리 아키텍처 (방식 A)","slug":"_3-레지스트리-아키텍처-방식-a","link":"#_3-레지스트리-아키텍처-방식-a","children":[{"level":3,"title":"파일 구조","slug":"파일-구조","link":"#파일-구조","children":[]},{"level":3,"title":"agents.json 형식","slug":"agents-json-형식","link":"#agents-json-형식","children":[]}]},{"level":2,"title":"4. TeamCreate 중복 방지 흐름","slug":"_4-teamcreate-중복-방지-흐름","link":"#_4-teamcreate-중복-방지-흐름","children":[]},{"level":2,"title":"5. Stale 에이전트 감지","slug":"_5-stale-에이전트-감지","link":"#_5-stale-에이전트-감지","children":[{"level":3,"title":"stale 정의","slug":"stale-정의","link":"#stale-정의","children":[]},{"level":3,"title":"stale 감지 및 처리 흐름","slug":"stale-감지-및-처리-흐름","link":"#stale-감지-및-처리-흐름","children":[]},{"level":3,"title":"last_ping 갱신 방법","slug":"last-ping-갱신-방법","link":"#last-ping-갱신-방법","children":[]}]},{"level":2,"title":"6. 완전한 소통 흐름","slug":"_6-완전한-소통-흐름","link":"#_6-완전한-소통-흐름","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/03-communication.md"}');export{p as comp,c as data};
