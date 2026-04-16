import{_ as e,c as n,e as a,o as i}from"./app-BrjBGS_5.js";const l={};function r(o,t){return i(),n("div",null,t[0]||(t[0]=[a(`<h1 id="ch0-전체-플로우-—-지시에서-완료까지" tabindex="-1"><a class="header-anchor" href="#ch0-전체-플로우-—-지시에서-완료까지"><span>CH0. 전체 플로우 — 지시에서 완료까지</span></a></h1><p>에이전트 시스템을 처음 설계하면 &quot;어떤 에이전트가 어떤 순서로 무엇을 하는가&quot;가 불분명하다. 이 챕터는 지시 한 줄이 어떻게 구체적인 결과물이 되는지 전체 흐름을 한눈에 보여준다. 이후 챕터들은 이 흐름의 각 구간을 상세히 다룬다.</p><h2 id="학습-목표" tabindex="-1"><a class="header-anchor" href="#학습-목표"><span>학습 목표</span></a></h2><ul><li>지시에서 완료까지의 전체 플로우를 설명할 수 있다.</li><li>PDCA 사이클이 에이전트 워크플로우에 어떻게 매핑되는지 이해한다.</li><li>각 역할(Orchestrator / Executor / Verifier)이 언제 무엇을 하는지 파악한다.</li></ul><h2 id="전체-플로우-한눈에-보기" tabindex="-1"><a class="header-anchor" href="#전체-플로우-한눈에-보기"><span>전체 플로우 한눈에 보기</span></a></h2><pre class="mermaid">flowchart TD
    A[사용자 지시] --&gt; B[Orchestrator&lt;br&gt;지시 구체화 + 분해]
    B --&gt; C[plans/ 문서 작성&lt;br&gt;목표 · DRI · 완료 기준]
    C --&gt; D[Registry 조회&lt;br&gt;가용 에이전트 확인]
    D --&gt; E[Executor 위임&lt;br&gt;SendMessage]
    E --&gt; F[Executor 구현&lt;br&gt;파일 수정 · 코드 작성]
    F --&gt; G[implementations/ 작성&lt;br&gt;증거 포함]
    G --&gt; H[Verifier 검증&lt;br&gt;완료 기준 충족 여부]
    H -- 미달 --&gt; F
    H -- 통과 --&gt; I[Orchestrator 완료 선언&lt;br&gt;사용자에게 보고]
    I --&gt; J[Act 루프&lt;br&gt;wisdom/ 업데이트 + 에이전트 정의 개선]
    J -.-&gt;|다음 사이클| B
</pre><p>지시는 Orchestrator가 받는다. Orchestrator는 지시를 구체화하고, 작업 단위로 분해하고, 각 단위에 DRI를 배분한다. 분해 결과는 <code>plans/</code> 문서에 기록된다. Registry에서 가용 에이전트를 확인하고, Executor에게 <code>SendMessage</code>로 위임한다. Executor는 구현 후 <code>implementations/</code> 문서에 증거를 남긴다. Verifier가 기준 충족 여부를 검증하고, 통과하면 Orchestrator가 완료를 선언한다. 완료 후에는 Act 루프가 실행되어 <code>wisdom/</code>을 업데이트하고 에이전트 정의 파일을 개선한다.</p><h2 id="pdca-사이클-매핑" tabindex="-1"><a class="header-anchor" href="#pdca-사이클-매핑"><span>PDCA 사이클 매핑</span></a></h2><p>에이전트 워크플로우는 PDCA(Plan-Do-Check-Act) 사이클의 구현이다.</p><pre class="mermaid">flowchart LR
    P[&quot;Plan&lt;br&gt;Orchestrator&lt;br&gt;지시 구체화&lt;br&gt;plans/ 작성&quot;]
    D[&quot;Do&lt;br&gt;Executor&lt;br&gt;구현&lt;br&gt;implementations/ 작성&quot;]
    C[&quot;Check&lt;br&gt;Verifier&lt;br&gt;완료 기준 검증&lt;br&gt;피드백 반환&quot;]
    A[&quot;Act&lt;br&gt;Orchestrator&lt;br&gt;wisdom/ 업데이트&lt;br&gt;에이전트 정의 개선&quot;]

    P --&gt; D --&gt; C --&gt; A --&gt; P
</pre><table><thead><tr><th>PDCA</th><th>에이전트</th><th>문서</th><th>챕터</th></tr></thead><tbody><tr><td>Plan</td><td>Orchestrator</td><td>plans/</td><td>CH2, CH6</td></tr><tr><td>Do</td><td>Executor</td><td>implementations/</td><td>CH2, CH6</td></tr><tr><td>Check</td><td>Verifier</td><td>implementations/ 검토</td><td>CH2, CH7</td></tr><tr><td>Act</td><td>Orchestrator</td><td>wisdom/, 에이전트 정의 파일</td><td>CH1, CH5, CH6</td></tr></tbody></table><p>PDCA에서 가장 자주 생략되는 단계는 Act다. 에이전트가 완료를 선언하고 끝내면 같은 실수가 반복된다. Act 루프가 작동해야 다음 사이클에서 더 나은 결과가 나온다.</p><h2 id="단계별-상세-설명" tabindex="-1"><a class="header-anchor" href="#단계별-상세-설명"><span>단계별 상세 설명</span></a></h2><h3 id="plan-—-지시-구체화" tabindex="-1"><a class="header-anchor" href="#plan-—-지시-구체화"><span>Plan — 지시 구체화</span></a></h3><p>Orchestrator가 사용자의 지시를 받으면 바로 실행하지 않는다. 먼저 질문한다.</p><ul><li>완료 기준이 명확한가?</li><li>어떤 에이전트가 DRI인가?</li><li>완료 기준을 어떻게 검증할 것인가?</li></ul><p>이 세 가지가 확정되면 <code>plans/</code> 문서를 작성한다. plans 없이 Executor에 위임하면 나중에 &quot;이게 맞냐&quot;는 재작업이 발생한다.</p><div class="hint-container info"><p class="hint-container-title">관련 챕터</p><ul><li><a href="/study/ai-agent-workflow/01-core-principles">CH1. 대원칙</a> — Question Every Assumption: 지시를 받기 전에 전제를 먼저 의심한다.</li><li><a href="/study/ai-agent-workflow/02-agent-design">CH2. 에이전트 설계</a> — DRI 배분 원칙</li></ul></div><h3 id="do-—-구현과-증거-수집" tabindex="-1"><a class="header-anchor" href="#do-—-구현과-증거-수집"><span>Do — 구현과 증거 수집</span></a></h3><p>Executor는 plans/ 문서를 읽고 시작한다. 완료 기준이 기록되어 있기 때문에 &quot;무엇을 만들어야 하는가&quot;가 명확하다.</p><p>구현 중 중요한 결정이 내려지면 <code>decisions/</code>에 ADR을 작성한다. 예상치 못한 문제가 발생하면 <code>wisdom/</code>에 기록한다. 구현이 완료되면 <code>implementations/</code>에 증거를 남긴다.</p><div class="hint-container info"><p class="hint-container-title">관련 챕터</p><ul><li><a href="/study/ai-agent-workflow/03-communication">CH3. 에이전트 간 소통</a> — Registry 조회 + SendMessage 위임</li><li><a href="/study/ai-agent-workflow/06-documentation">CH6. 문서화 체계</a> — implementations/ 작성 규칙</li></ul></div><h3 id="check-—-검증" tabindex="-1"><a class="header-anchor" href="#check-—-검증"><span>Check — 검증</span></a></h3><p>Verifier는 <code>implementations/</code>와 <code>plans/</code>를 함께 읽는다. implementations에 기록된 증거가 plans에 명시된 완료 기준을 충족하는지 비교한다.</p><p>구두 확인이나 Executor의 자기 선언은 검증이 아니다. 파일 경로, 커밋 해시, 테스트 결과 같은 객관적 증거가 기준을 충족해야 통과다.</p><div class="hint-container info"><p class="hint-container-title">관련 챕터</p><ul><li><a href="/study/ai-agent-workflow/07-constitution">CH7. 에이전트 헌법</a> — Verifier 역할별 체크리스트</li></ul></div><h3 id="act-—-개선-루프" tabindex="-1"><a class="header-anchor" href="#act-—-개선-루프"><span>Act — 개선 루프</span></a></h3><p>Verifier가 통과를 선언하면 즉시 Act 루프가 시작된다.</p><ol><li>이번 사이클에서 발생한 실수나 학습 → <code>wisdom/</code> 업데이트</li><li>재발 방지가 에이전트 수준에서 가능하면 → 에이전트 정의 파일 수정</li><li>패턴이 팀 전체에 적용되면 → <code>CLAUDE.md</code> 또는 <code>CONSTITUTION.md</code> 업데이트</li></ol><p>Act 없는 PDCA는 같은 실수를 반복한다. &quot;이번엔 실수했지만 다음엔 안 그럴 것&quot;이라는 생각은 문서화하지 않으면 거짓이다.</p><div class="hint-container info"><p class="hint-container-title">관련 챕터</p><ul><li><a href="/study/ai-agent-workflow/01-core-principles">CH1. 대원칙</a> — Learn Proactively: 같은 실수를 두 번 반복하지 않는다.</li><li><a href="/study/ai-agent-workflow/05-agent-definition-files">CH5. 에이전트 정의 파일</a> — 에이전트 정의 파일 업데이트 방법</li></ul></div><h2 id="전체-시퀀스-다이어그램" tabindex="-1"><a class="header-anchor" href="#전체-시퀀스-다이어그램"><span>전체 시퀀스 다이어그램</span></a></h2><pre class="mermaid">sequenceDiagram
    participant U as 사용자
    participant O as Orchestrator
    participant R as Registry
    participant E as Executor
    participant V as Verifier
    participant D as 문서 시스템

    U-&gt;&gt;O: 지시
    O-&gt;&gt;O: Question Every Assumption&lt;br&gt;지시 구체화 + 완료 기준 확정
    O-&gt;&gt;D: plans/ 작성 (status: approved)

    O-&gt;&gt;R: 가용 에이전트 조회
    R--&gt;&gt;O: Executor ID 반환

    O-&gt;&gt;E: SendMessage (작업 위임)
    E-&gt;&gt;D: plans/ 읽기

    loop 구현
        E-&gt;&gt;E: 코드 작성 / 파일 수정
        alt 중요한 결정 발생
            E-&gt;&gt;D: decisions/ 작성 (ADR)
        end
        alt 실수 또는 학습
            E-&gt;&gt;D: wisdom/ 작성
        end
    end

    E-&gt;&gt;D: implementations/ 작성 (증거 포함)
    E-&gt;&gt;V: 검증 요청

    V-&gt;&gt;D: plans/ + implementations/ 읽기
    V-&gt;&gt;V: 완료 기준 충족 여부 판단

    alt 기준 미달
        V--&gt;&gt;E: 피드백 반환
    else 기준 충족
        V--&gt;&gt;O: 완료 선언
    end

    O-&gt;&gt;U: 결과 보고
    O-&gt;&gt;D: wisdom/ 업데이트 (Act 루프)
    O-&gt;&gt;D: 에이전트 정의 파일 개선
</pre><h2 id="이-스터디의-구성" tabindex="-1"><a class="header-anchor" href="#이-스터디의-구성"><span>이 스터디의 구성</span></a></h2><p>각 챕터는 위 플로우의 특정 구간을 깊이 다룬다.</p><pre class="mermaid">flowchart TD
    CH0[&quot;CH0. 전체 플로우 (지금 여기)&quot;]
    CH1[&quot;CH1. 대원칙&lt;br&gt;에이전트가 지켜야 할 행동 규칙&quot;]
    CH2[&quot;CH2. 에이전트 설계&lt;br&gt;Orchestrator / Executor / Verifier&quot;]
    CH3[&quot;CH3. 에이전트 간 소통&lt;br&gt;Registry 훅 방식&quot;]
    CH4[&quot;CH4. TypeScript 구현&lt;br&gt;레지스트리 훅 코드&quot;]
    CH5[&quot;CH5. 에이전트 정의 파일&lt;br&gt;항상 일하고 생각하도록&quot;]
    CH6[&quot;CH6. 문서화 체계&lt;br&gt;plans · decisions · wisdom&quot;]
    CH7[&quot;CH7. 에이전트 헌법&lt;br&gt;작업 전후 체크리스트&quot;]
    CH8[&quot;CH8. Scaffold&lt;br&gt;바로 복사해서 쓰는 템플릿&quot;]

    CH0 --&gt; CH1 --&gt; CH2 --&gt; CH3 --&gt; CH4 --&gt; CH5 --&gt; CH6 --&gt; CH7 --&gt; CH8
</pre><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>지시 → Plan(plans/) → Do(Executor) → Check(Verifier) → Act(wisdom/) → 다음 사이클 순서로 흐른다.</li><li>PDCA에서 Act가 가장 자주 생략된다. Act 없는 PDCA는 같은 실수를 반복한다.</li><li>각 역할은 문서로 소통한다. 구두 약속은 에이전트 시스템에서 증거가 아니다.</li></ul><p><a href="/study/ai-agent-workflow/01-core-principles">CH1. 대원칙</a>으로 이어진다.</p></div>`,37)]))}const c=e(l,[["render",r],["__file","00-overview.html.vue"]]),d=JSON.parse('{"path":"/study/ai-agent-workflow/00-overview.html","title":"CH0. 전체 플로우 — 지시에서 완료까지","lang":"en-US","frontmatter":{"title":"CH0. 전체 플로우 — 지시에서 완료까지","description":"지시 한 줄이 어떻게 완성된 결과물이 되는가. PDCA 사이클과 에이전트 역할의 전체 그림","date":"2026-04-16T00:00:00.000Z","tags":["AI","Agent","Workflow","PDCA","Overview"]},"headers":[{"level":1,"title":"CH0. 전체 플로우 — 지시에서 완료까지","slug":"ch0-전체-플로우-—-지시에서-완료까지","link":"#ch0-전체-플로우-—-지시에서-완료까지","children":[{"level":2,"title":"학습 목표","slug":"학습-목표","link":"#학습-목표","children":[]},{"level":2,"title":"전체 플로우 한눈에 보기","slug":"전체-플로우-한눈에-보기","link":"#전체-플로우-한눈에-보기","children":[]},{"level":2,"title":"PDCA 사이클 매핑","slug":"pdca-사이클-매핑","link":"#pdca-사이클-매핑","children":[]},{"level":2,"title":"단계별 상세 설명","slug":"단계별-상세-설명","link":"#단계별-상세-설명","children":[{"level":3,"title":"Plan — 지시 구체화","slug":"plan-—-지시-구체화","link":"#plan-—-지시-구체화","children":[]},{"level":3,"title":"Do — 구현과 증거 수집","slug":"do-—-구현과-증거-수집","link":"#do-—-구현과-증거-수집","children":[]},{"level":3,"title":"Check — 검증","slug":"check-—-검증","link":"#check-—-검증","children":[]},{"level":3,"title":"Act — 개선 루프","slug":"act-—-개선-루프","link":"#act-—-개선-루프","children":[]}]},{"level":2,"title":"전체 시퀀스 다이어그램","slug":"전체-시퀀스-다이어그램","link":"#전체-시퀀스-다이어그램","children":[]},{"level":2,"title":"이 스터디의 구성","slug":"이-스터디의-구성","link":"#이-스터디의-구성","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/00-overview.md"}');export{c as comp,d as data};
