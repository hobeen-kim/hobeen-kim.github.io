import{_ as s,c as a,e as p,o as t}from"./app-CitQKXyz.js";const e={};function l(i,n){return t(),a("div",null,n[0]||(n[0]=[p(`<h1 id="ch8-scaffold-—-바로-복사해서-쓰는-템플릿" tabindex="-1"><a class="header-anchor" href="#ch8-scaffold-—-바로-복사해서-쓰는-템플릿"><span>CH8. Scaffold — 바로 복사해서 쓰는 템플릿</span></a></h1><h2 id="이-챕터의-목적" tabindex="-1"><a class="header-anchor" href="#이-챕터의-목적"><span>이 챕터의 목적</span></a></h2><p>앞 챕터를 읽었다면 이제 실제로 만들 차례다. 이 챕터의 파일들을 복사하면 바로 작동하는 에이전트 시스템이 완성된다. 개념을 이해하는 것과 실제로 실행하는 것 사이의 간격을 이 챕터가 채운다.</p><h2 id="_1-전체-디렉토리-구조" tabindex="-1"><a class="header-anchor" href="#_1-전체-디렉토리-구조"><span>1. 전체 디렉토리 구조</span></a></h2><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">my-agent-workspace/</span>
<span class="line">├── agents/                    ← 에이전트 정의 파일</span>
<span class="line">│   ├── orchestrator.md</span>
<span class="line">│   ├── dev.md</span>
<span class="line">│   ├── design.md</span>
<span class="line">│   ├── qa.md</span>
<span class="line">│   └── verifier.md</span>
<span class="line">├── hooks/                     ← TypeScript 훅</span>
<span class="line">│   ├── types.ts</span>
<span class="line">│   ├── registry.ts</span>
<span class="line">│   ├── team-registry-enforcer.ts</span>
<span class="line">│   └── team-registry-updater.ts</span>
<span class="line">├── CLAUDE.md                  ← 프로젝트 특화 클로드 파일</span>
<span class="line">├── CONSTITUTION.md            ← 에이전트 헌법</span>
<span class="line">├── .claude/</span>
<span class="line">│   └── settings.json         ← 훅 연결 설정</span>
<span class="line">└── package.json              ← TypeScript 실행 설정</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="각-파일의-역할-관계도" tabindex="-1"><a class="header-anchor" href="#각-파일의-역할-관계도"><span>각 파일의 역할 관계도</span></a></h3><pre class="mermaid">flowchart TD
    CM[CLAUDE.md&lt;br&gt;프로젝트 컨텍스트] --&gt; CO[CONSTITUTION.md&lt;br&gt;공통 원칙]
    CO --&gt; AG[agents/&lt;br&gt;역할별 정의 파일]

    CS[.claude/settings.json&lt;br&gt;훅 등록] --&gt; HK[hooks/&lt;br&gt;TypeScript 훅]
    HK --&gt; RE[registry.ts&lt;br&gt;에이전트 상태 관리]
    HK --&gt; EN[team-registry-enforcer.ts&lt;br&gt;중복 방지]
    HK --&gt; UP[team-registry-updater.ts&lt;br&gt;상태 업데이트]

    AG --&gt;|에이전트 생성| CS
</pre><h2 id="_2-설정-순서-step-by-step" tabindex="-1"><a class="header-anchor" href="#_2-설정-순서-step-by-step"><span>2. 설정 순서 (Step by Step)</span></a></h2><pre class="mermaid">flowchart LR
    S1[Step 1&lt;br&gt;파일 복사] --&gt; S2[Step 2&lt;br&gt;CLAUDE.md 수정]
    S2 --&gt; S3[Step 3&lt;br&gt;agents/ 팀 이름 수정]
    S3 --&gt; S4[Step 4&lt;br&gt;npm install]
    S4 --&gt; S5[Step 5&lt;br&gt;settings.json 훅 등록]
    S5 --&gt; S6[Step 6&lt;br&gt;동작 테스트]
</pre><p><strong>Step 1</strong>: 이 챕터의 템플릿 파일을 프로젝트 루트에 복사한다.</p><p><strong>Step 2</strong>: CLAUDE.md에 프로젝트 특화 내용을 추가한다. 기술 스택, 코딩 컨벤션, 금지 행동 목록이 들어간다.</p><p><strong>Step 3</strong>: agents/ 파일에서 팀 이름을 실제 팀 이름으로 수정한다. <code>executor-dev</code>를 <code>executor-backend</code>처럼 프로젝트에 맞게 바꾼다.</p><p><strong>Step 4</strong>: <code>npm install</code>로 ts-node, typescript 의존성을 설치한다.</p><p><strong>Step 5</strong>: .claude/settings.json에 훅을 등록한다. hooks/ 디렉토리의 TypeScript 파일 경로를 절대경로로 입력한다.</p><p><strong>Step 6</strong>: Claude Code에서 동일 에이전트를 두 번 생성하여 중복 방지 훅이 동작하는지 확인한다.</p><h2 id="_3-각-파일-완전한-템플릿" tabindex="-1"><a class="header-anchor" href="#_3-각-파일-완전한-템플릿"><span>3. 각 파일 완전한 템플릿</span></a></h2><details class="hint-container details"><summary>agents/orchestrator.md</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> orchestrator</span>
<span class="line"><span class="token key atrule">role</span><span class="token punctuation">:</span> Orchestrator</span>
<span class="line"><span class="token key atrule">dri</span><span class="token punctuation">:</span> <span class="token string">&quot;작업 우선순위, 에이전트 배분&quot;</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Orchestrator</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"></span>
<span class="line">전체 목표를 유지하고, 작업을 분해하여 적절한 에이전트에게 위임한다.</span>
<span class="line">직접 코드를 짜거나 결과물을 검증하지 않는다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">1.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">위임한다</span><span class="token punctuation">**</span></span>: 모든 실행 작업은 Executor에게 위임한다. 직접 실행은 금지다.</span>
<span class="line"><span class="token list punctuation">2.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">DRI를 배분한다</span><span class="token punctuation">**</span></span>: 모든 작업에 DRI 에이전트를 명확히 지정한다.</span>
<span class="line"><span class="token list punctuation">3.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">plan을 먼저 만든다</span><span class="token punctuation">**</span></span>: 실행 전에 plans/ 문서가 존재해야 한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 작업 시작 전 체크리스트</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 이 작업의 진짜 목표가 무엇인가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 적절한 에이전트가 registry에 등록되어 있는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] DRI를 명확히 배분했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] plan 문서를 작성했는가?</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 금지 행동</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> 코드 직접 작성</span>
<span class="line"><span class="token list punctuation">-</span> 파일 직접 수정</span>
<span class="line"><span class="token list punctuation">-</span> Verifier 없이 완료 선언</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>agents/dev.md</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> executor<span class="token punctuation">-</span>dev</span>
<span class="line"><span class="token key atrule">role</span><span class="token punctuation">:</span> Executor</span>
<span class="line"><span class="token key atrule">dri</span><span class="token punctuation">:</span> <span class="token string">&quot;코드 구현 방식, 기술 선택&quot;</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Executor (Dev)</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"></span>
<span class="line">구체적인 코드 구현을 담당한다. &quot;어떻게 구현하는가&quot;의 최종 결정권자다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">1.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">증거를 남긴다</span><span class="token punctuation">**</span></span>: 구현 완료 후 implementations/에 파일 경로, 커밋을 기록한다.</span>
<span class="line"><span class="token list punctuation">2.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">범위를 지킨다</span><span class="token punctuation">**</span></span>: plan에 명시된 범위만 구현한다. 추가 개선은 별도 TODO로 기록한다.</span>
<span class="line"><span class="token list punctuation">3.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">자기 검토를 거친다</span><span class="token punctuation">**</span></span>: Verifier에게 제출 전 스스로 한 번 더 검토한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 작업 완료 체크리스트</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] implementations/에 증거를 남겼는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] plan의 완료 기준을 모두 충족했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 스스로 검토를 완료했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] wisdom/을 확인했는가? (같은 실수 반복 방지)</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> DRI 범위</span></span>
<span class="line"></span>
<span class="line">결정 가능: 코드 구현 방식, 라이브러리 선택, 함수 구조</span>
<span class="line">결정 불가: 제품 방향, 기능 우선순위, 완료 선언</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>agents/verifier.md</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> verifier</span>
<span class="line"><span class="token key atrule">role</span><span class="token punctuation">:</span> Verifier</span>
<span class="line"><span class="token key atrule">dri</span><span class="token punctuation">:</span> <span class="token string">&quot;완료 기준 판단&quot;</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Verifier</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"></span>
<span class="line">결과물이 plan에 명시된 완료 기준을 충족하는지 검증한다.</span>
<span class="line">&quot;완료&quot;를 선언할 수 있는 유일한 권한을 보유한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">1.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">기준 기반으로 검증한다</span><span class="token punctuation">**</span></span>: 개인 기준이 아니라 plan 문서의 acceptance_criteria를 기준으로 판단한다.</span>
<span class="line"><span class="token list punctuation">2.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">증거를 확인한다</span><span class="token punctuation">**</span></span>: implementations/ 문서의 증거(파일 경로, 커밋)를 직접 확인한다.</span>
<span class="line"><span class="token list punctuation">3.</span> <span class="token bold"><span class="token punctuation">**</span><span class="token content">결과를 검증한다</span><span class="token punctuation">**</span></span>: 구현 방법이 아니라 결과가 기준을 충족하는지를 검증한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 검증 체크리스트</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] plan 문서의 acceptance_criteria를 확인했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] implementations/ 문서의 증거를 확인했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 기준 항목을 하나씩 대조했는가?</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 판정 결과</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> <span class="token code-snippet code keyword">\`approved\`</span>: 모든 기준 충족. 완료 선언.</span>
<span class="line"><span class="token list punctuation">-</span> <span class="token code-snippet code keyword">\`revision_required\`</span>: 미충족 항목 목록 + 구체적 피드백 반환.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>CONSTITUTION.md</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token title important"><span class="token punctuation">#</span> CONSTITUTION.md — 에이전트 헌법</span></span>
<span class="line"></span>
<span class="line">이 문서는 모든 에이전트에게 공통 적용된다.</span>
<span class="line">에이전트 정의 파일(agents/*.md)보다 상위 기준이다.</span>
<span class="line"></span>
<span class="line"><span class="token hr punctuation">---</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 공통 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> 작업 전</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 이 작업의 진짜 목표가 무엇인가? (Mission over Individual)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 내 DRI 범위 안의 작업인가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 이 접근법이 최선인가? (Question Every Assumption)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 요청 이상으로 하려 하지 않는가? (Focus on Impact)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 지금 바로 시작할 수 있는가? (Move with Urgency)</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> 작업 중</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 계획대로 진행되고 있는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 범위 확장이 생기지 않는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 막히면 논쟁 대신 실험</span>
<span class="line"><span class="token list punctuation">-</span> [ ] implementations/에 기록하고 있는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] wisdom/을 확인했는가?</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> 작업 후</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 결과물을 직접 검토했는가? (Aim Higher)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] Verifier에게 피드백을 요청했는가? (Ask for Feedback)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] implementations/에 증거가 있는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] wisdom/에 배운 것을 기록했는가? (Learn Proactively)</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 완료 선언은 Verifier가 했는가?</span>
<span class="line"></span>
<span class="line"><span class="token hr punctuation">---</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할별 추가 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> Orchestrator</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 적절한 에이전트에게 위임했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] DRI를 명확히 배분했는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 직접 실행하려 하지 않는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] plan 문서가 먼저 존재하는가?</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> Executor</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 구현 방식 결정은 내 DRI 범위인가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 제품 방향 결정을 내가 하려 하지 않는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 코드 외 파일을 건드리지 않는가?</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">###</span> Verifier</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> [ ] 완료 기준이 plan 문서에 명시된 것과 일치하는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 구현 방법이 아니라 결과를 검증하는가?</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 증거를 확인했는가?</span>
<span class="line"></span>
<span class="line"><span class="token hr punctuation">---</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 절대 규칙</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> Verifier의 <span class="token code-snippet code keyword">\`approved\`</span> 없이 완료는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> plans 없이 실행은 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 증거 없이 implementations는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 결정 당일 decisions를 작성한다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>hooks/registry.ts</summary><div class="language-typescript line-numbers-mode" data-highlighter="prismjs" data-ext="ts" data-title="ts"><pre><code><span class="line"><span class="token keyword">import</span> <span class="token operator">*</span> <span class="token keyword">as</span> fs <span class="token keyword">from</span> <span class="token string">&quot;fs&quot;</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token keyword">import</span> <span class="token operator">*</span> <span class="token keyword">as</span> path <span class="token keyword">from</span> <span class="token string">&quot;path&quot;</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token keyword">import</span> <span class="token operator">*</span> <span class="token keyword">as</span> os <span class="token keyword">from</span> <span class="token string">&quot;os&quot;</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">interface</span> <span class="token class-name">AgentRecord</span> <span class="token punctuation">{</span></span>
<span class="line">  name<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">  role<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">  pid<span class="token operator">:</span> <span class="token builtin">number</span><span class="token punctuation">;</span></span>
<span class="line">  startedAt<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">  lastSeenAt<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">  status<span class="token operator">:</span> <span class="token string">&quot;active&quot;</span> <span class="token operator">|</span> <span class="token string">&quot;stale&quot;</span> <span class="token operator">|</span> <span class="token string">&quot;terminated&quot;</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">const</span> <span class="token constant">REGISTRY_DIR</span> <span class="token operator">=</span> path<span class="token punctuation">.</span><span class="token function">join</span><span class="token punctuation">(</span>os<span class="token punctuation">.</span><span class="token function">homedir</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">&quot;.claude&quot;</span><span class="token punctuation">,</span> <span class="token string">&quot;registry&quot;</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token keyword">const</span> <span class="token constant">STALE_THRESHOLD_MS</span> <span class="token operator">=</span> <span class="token number">5</span> <span class="token operator">*</span> <span class="token number">60</span> <span class="token operator">*</span> <span class="token number">1000</span><span class="token punctuation">;</span> <span class="token comment">// 5 minutes</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">ensureRegistryDir</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token operator">:</span> <span class="token keyword">void</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">if</span> <span class="token punctuation">(</span><span class="token operator">!</span>fs<span class="token punctuation">.</span><span class="token function">existsSync</span><span class="token punctuation">(</span><span class="token constant">REGISTRY_DIR</span><span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    fs<span class="token punctuation">.</span><span class="token function">mkdirSync</span><span class="token punctuation">(</span><span class="token constant">REGISTRY_DIR</span><span class="token punctuation">,</span> <span class="token punctuation">{</span> recursive<span class="token operator">:</span> <span class="token boolean">true</span> <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">getRegistryPath</span><span class="token punctuation">(</span>agentName<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">)</span><span class="token operator">:</span> <span class="token builtin">string</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">return</span> path<span class="token punctuation">.</span><span class="token function">join</span><span class="token punctuation">(</span><span class="token constant">REGISTRY_DIR</span><span class="token punctuation">,</span> <span class="token template-string"><span class="token template-punctuation string">\`</span><span class="token interpolation"><span class="token interpolation-punctuation punctuation">\${</span>agentName<span class="token interpolation-punctuation punctuation">}</span></span><span class="token string">.json</span><span class="token template-punctuation string">\`</span></span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">readAgent</span><span class="token punctuation">(</span>agentName<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">)</span><span class="token operator">:</span> AgentRecord <span class="token operator">|</span> <span class="token keyword">null</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">const</span> filePath <span class="token operator">=</span> <span class="token function">getRegistryPath</span><span class="token punctuation">(</span>agentName<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">if</span> <span class="token punctuation">(</span><span class="token operator">!</span>fs<span class="token punctuation">.</span><span class="token function">existsSync</span><span class="token punctuation">(</span>filePath<span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token keyword">return</span> <span class="token keyword">null</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">try</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">return</span> <span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">parse</span><span class="token punctuation">(</span>fs<span class="token punctuation">.</span><span class="token function">readFileSync</span><span class="token punctuation">(</span>filePath<span class="token punctuation">,</span> <span class="token string">&quot;utf-8&quot;</span><span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token keyword">as</span> AgentRecord<span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span> <span class="token keyword">catch</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">return</span> <span class="token keyword">null</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">writeAgent</span><span class="token punctuation">(</span>record<span class="token operator">:</span> AgentRecord<span class="token punctuation">)</span><span class="token operator">:</span> <span class="token keyword">void</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token function">ensureRegistryDir</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  fs<span class="token punctuation">.</span><span class="token function">writeFileSync</span><span class="token punctuation">(</span></span>
<span class="line">    <span class="token function">getRegistryPath</span><span class="token punctuation">(</span>record<span class="token punctuation">.</span>name<span class="token punctuation">)</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span>record<span class="token punctuation">,</span> <span class="token keyword">null</span><span class="token punctuation">,</span> <span class="token number">2</span><span class="token punctuation">)</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token string">&quot;utf-8&quot;</span></span>
<span class="line">  <span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">isStale</span><span class="token punctuation">(</span>record<span class="token operator">:</span> AgentRecord<span class="token punctuation">)</span><span class="token operator">:</span> <span class="token builtin">boolean</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">const</span> lastSeen <span class="token operator">=</span> <span class="token keyword">new</span> <span class="token class-name">Date</span><span class="token punctuation">(</span>record<span class="token punctuation">.</span>lastSeenAt<span class="token punctuation">)</span><span class="token punctuation">.</span><span class="token function">getTime</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">return</span> Date<span class="token punctuation">.</span><span class="token function">now</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token operator">-</span> lastSeen <span class="token operator">&gt;</span> <span class="token constant">STALE_THRESHOLD_MS</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">export</span> <span class="token keyword">function</span> <span class="token function">listActiveAgents</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token operator">:</span> AgentRecord<span class="token punctuation">[</span><span class="token punctuation">]</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token function">ensureRegistryDir</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">return</span> fs</span>
<span class="line">    <span class="token punctuation">.</span><span class="token function">readdirSync</span><span class="token punctuation">(</span><span class="token constant">REGISTRY_DIR</span><span class="token punctuation">)</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token function">filter</span><span class="token punctuation">(</span><span class="token punctuation">(</span>f<span class="token punctuation">)</span> <span class="token operator">=&gt;</span> f<span class="token punctuation">.</span><span class="token function">endsWith</span><span class="token punctuation">(</span><span class="token string">&quot;.json&quot;</span><span class="token punctuation">)</span><span class="token punctuation">)</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token function">map</span><span class="token punctuation">(</span><span class="token punctuation">(</span>f<span class="token punctuation">)</span> <span class="token operator">=&gt;</span> <span class="token punctuation">{</span></span>
<span class="line">      <span class="token keyword">try</span> <span class="token punctuation">{</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">parse</span><span class="token punctuation">(</span></span>
<span class="line">          fs<span class="token punctuation">.</span><span class="token function">readFileSync</span><span class="token punctuation">(</span>path<span class="token punctuation">.</span><span class="token function">join</span><span class="token punctuation">(</span><span class="token constant">REGISTRY_DIR</span><span class="token punctuation">,</span> f<span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token string">&quot;utf-8&quot;</span><span class="token punctuation">)</span></span>
<span class="line">        <span class="token punctuation">)</span> <span class="token keyword">as</span> AgentRecord<span class="token punctuation">;</span></span>
<span class="line">      <span class="token punctuation">}</span> <span class="token keyword">catch</span> <span class="token punctuation">{</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token keyword">null</span><span class="token punctuation">;</span></span>
<span class="line">      <span class="token punctuation">}</span></span>
<span class="line">    <span class="token punctuation">}</span><span class="token punctuation">)</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token function">filter</span><span class="token punctuation">(</span><span class="token punctuation">(</span>r<span class="token punctuation">)</span><span class="token operator">:</span> r <span class="token keyword">is</span> AgentRecord <span class="token operator">=&gt;</span> r <span class="token operator">!==</span> <span class="token keyword">null</span> <span class="token operator">&amp;&amp;</span> <span class="token operator">!</span><span class="token function">isStale</span><span class="token punctuation">(</span>r<span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>hooks/team-registry-enforcer.ts</summary><div class="language-typescript line-numbers-mode" data-highlighter="prismjs" data-ext="ts" data-title="ts"><pre><code><span class="line"><span class="token keyword">import</span> <span class="token punctuation">{</span> readAgent<span class="token punctuation">,</span> isStale <span class="token punctuation">}</span> <span class="token keyword">from</span> <span class="token string">&quot;./registry&quot;</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">interface</span> <span class="token class-name">HookInput</span> <span class="token punctuation">{</span></span>
<span class="line">  tool_name<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">  tool_input<span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    prompt<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">[</span>key<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">]</span><span class="token operator">:</span> <span class="token builtin">unknown</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">interface</span> <span class="token class-name">HookOutput</span> <span class="token punctuation">{</span></span>
<span class="line">  decision<span class="token operator">:</span> <span class="token string">&quot;approve&quot;</span> <span class="token operator">|</span> <span class="token string">&quot;block&quot;</span><span class="token punctuation">;</span></span>
<span class="line">  reason<span class="token operator">?</span><span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">function</span> <span class="token function">extractAgentName</span><span class="token punctuation">(</span>prompt<span class="token operator">:</span> <span class="token builtin">string</span><span class="token punctuation">)</span><span class="token operator">:</span> <span class="token builtin">string</span> <span class="token operator">|</span> <span class="token keyword">null</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">const</span> match <span class="token operator">=</span> prompt<span class="token punctuation">.</span><span class="token function">match</span><span class="token punctuation">(</span><span class="token regex"><span class="token regex-delimiter">/</span><span class="token regex-source language-regex">name:\\s*([a-z0-9-]+)</span><span class="token regex-delimiter">/</span><span class="token regex-flags">i</span></span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">return</span> match <span class="token operator">?</span> match<span class="token punctuation">[</span><span class="token number">1</span><span class="token punctuation">]</span><span class="token punctuation">.</span><span class="token function">toLowerCase</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token operator">:</span> <span class="token keyword">null</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">async</span> <span class="token keyword">function</span> <span class="token function">main</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token operator">:</span> <span class="token builtin">Promise</span><span class="token operator">&lt;</span><span class="token keyword">void</span><span class="token operator">&gt;</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">const</span> input<span class="token operator">:</span> HookInput <span class="token operator">=</span> <span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">parse</span><span class="token punctuation">(</span></span>
<span class="line">    <span class="token keyword">await</span> <span class="token keyword">new</span> <span class="token class-name"><span class="token builtin">Promise</span></span><span class="token punctuation">(</span><span class="token punctuation">(</span>resolve<span class="token punctuation">)</span> <span class="token operator">=&gt;</span> <span class="token punctuation">{</span></span>
<span class="line">      <span class="token keyword">let</span> data <span class="token operator">=</span> <span class="token string">&quot;&quot;</span><span class="token punctuation">;</span></span>
<span class="line">      process<span class="token punctuation">.</span>stdin<span class="token punctuation">.</span><span class="token function">on</span><span class="token punctuation">(</span><span class="token string">&quot;data&quot;</span><span class="token punctuation">,</span> <span class="token punctuation">(</span>chunk<span class="token punctuation">)</span> <span class="token operator">=&gt;</span> <span class="token punctuation">(</span>data <span class="token operator">+=</span> chunk<span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">      process<span class="token punctuation">.</span>stdin<span class="token punctuation">.</span><span class="token function">on</span><span class="token punctuation">(</span><span class="token string">&quot;end&quot;</span><span class="token punctuation">,</span> <span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token operator">=&gt;</span> <span class="token function">resolve</span><span class="token punctuation">(</span>data<span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">}</span><span class="token punctuation">)</span></span>
<span class="line">  <span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">  <span class="token comment">// Only enforce on TeamCreate</span></span>
<span class="line">  <span class="token keyword">if</span> <span class="token punctuation">(</span>input<span class="token punctuation">.</span>tool_name <span class="token operator">!==</span> <span class="token string">&quot;TeamCreate&quot;</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    process<span class="token punctuation">.</span>stdout<span class="token punctuation">.</span><span class="token function">write</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span><span class="token punctuation">{</span> decision<span class="token operator">:</span> <span class="token string">&quot;approve&quot;</span> <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token keyword">return</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">  <span class="token keyword">const</span> prompt <span class="token operator">=</span> input<span class="token punctuation">.</span>tool_input<span class="token punctuation">.</span>prompt <span class="token operator">??</span> <span class="token string">&quot;&quot;</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token keyword">const</span> agentName <span class="token operator">=</span> <span class="token function">extractAgentName</span><span class="token punctuation">(</span>prompt<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">  <span class="token keyword">if</span> <span class="token punctuation">(</span><span class="token operator">!</span>agentName<span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    process<span class="token punctuation">.</span>stdout<span class="token punctuation">.</span><span class="token function">write</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span><span class="token punctuation">{</span> decision<span class="token operator">:</span> <span class="token string">&quot;approve&quot;</span> <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token keyword">return</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">  <span class="token keyword">const</span> existing <span class="token operator">=</span> <span class="token function">readAgent</span><span class="token punctuation">(</span>agentName<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">  <span class="token keyword">if</span> <span class="token punctuation">(</span>existing <span class="token operator">&amp;&amp;</span> <span class="token operator">!</span><span class="token function">isStale</span><span class="token punctuation">(</span>existing<span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">const</span> output<span class="token operator">:</span> HookOutput <span class="token operator">=</span> <span class="token punctuation">{</span></span>
<span class="line">      decision<span class="token operator">:</span> <span class="token string">&quot;block&quot;</span><span class="token punctuation">,</span></span>
<span class="line">      reason<span class="token operator">:</span> <span class="token template-string"><span class="token template-punctuation string">\`</span><span class="token string">Agent &#39;</span><span class="token interpolation"><span class="token interpolation-punctuation punctuation">\${</span>agentName<span class="token interpolation-punctuation punctuation">}</span></span><span class="token string">&#39; is already active (started: </span><span class="token interpolation"><span class="token interpolation-punctuation punctuation">\${</span>existing<span class="token punctuation">.</span>startedAt<span class="token interpolation-punctuation punctuation">}</span></span><span class="token string">). Use the existing agent or wait for it to become stale.</span><span class="token template-punctuation string">\`</span></span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">}</span><span class="token punctuation">;</span></span>
<span class="line">    process<span class="token punctuation">.</span>stdout<span class="token punctuation">.</span><span class="token function">write</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span>output<span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token keyword">return</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">  process<span class="token punctuation">.</span>stdout<span class="token punctuation">.</span><span class="token function">write</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span><span class="token punctuation">{</span> decision<span class="token operator">:</span> <span class="token string">&quot;approve&quot;</span> <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token function">main</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">.</span><span class="token function">catch</span><span class="token punctuation">(</span><span class="token punctuation">(</span>err<span class="token punctuation">)</span> <span class="token operator">=&gt;</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token builtin">console</span><span class="token punctuation">.</span><span class="token function">error</span><span class="token punctuation">(</span>err<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  process<span class="token punctuation">.</span><span class="token function">exit</span><span class="token punctuation">(</span><span class="token number">1</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>.claude/settings.json</summary><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span></span>
<span class="line">  <span class="token property">&quot;hooks&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;PreToolUse&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">      <span class="token punctuation">{</span></span>
<span class="line">        <span class="token property">&quot;matcher&quot;</span><span class="token operator">:</span> <span class="token string">&quot;TeamCreate&quot;</span><span class="token punctuation">,</span></span>
<span class="line">        <span class="token property">&quot;hooks&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">          <span class="token punctuation">{</span></span>
<span class="line">            <span class="token property">&quot;type&quot;</span><span class="token operator">:</span> <span class="token string">&quot;command&quot;</span><span class="token punctuation">,</span></span>
<span class="line">            <span class="token property">&quot;command&quot;</span><span class="token operator">:</span> <span class="token string">&quot;npx ts-node /absolute/path/to/hooks/team-registry-enforcer.ts&quot;</span></span>
<span class="line">          <span class="token punctuation">}</span></span>
<span class="line">        <span class="token punctuation">]</span></span>
<span class="line">      <span class="token punctuation">}</span></span>
<span class="line">    <span class="token punctuation">]</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;PostToolUse&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">      <span class="token punctuation">{</span></span>
<span class="line">        <span class="token property">&quot;matcher&quot;</span><span class="token operator">:</span> <span class="token string">&quot;TeamCreate&quot;</span><span class="token punctuation">,</span></span>
<span class="line">        <span class="token property">&quot;hooks&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">          <span class="token punctuation">{</span></span>
<span class="line">            <span class="token property">&quot;type&quot;</span><span class="token operator">:</span> <span class="token string">&quot;command&quot;</span><span class="token punctuation">,</span></span>
<span class="line">            <span class="token property">&quot;command&quot;</span><span class="token operator">:</span> <span class="token string">&quot;npx ts-node /absolute/path/to/hooks/team-registry-updater.ts&quot;</span></span>
<span class="line">          <span class="token punctuation">}</span></span>
<span class="line">        <span class="token punctuation">]</span></span>
<span class="line">      <span class="token punctuation">}</span></span>
<span class="line">    <span class="token punctuation">]</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="hint-container warning"><p class="hint-container-title">절대경로 필수</p><p><code>/absolute/path/to/hooks/</code> 부분을 실제 절대경로로 교체해야 한다. 상대경로를 사용하면 훅이 실행되지 않는다.</p></div></details><p>:::</p><details class="hint-container details"><summary>package.json</summary><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span></span>
<span class="line">  <span class="token property">&quot;name&quot;</span><span class="token operator">:</span> <span class="token string">&quot;agent-hooks&quot;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;version&quot;</span><span class="token operator">:</span> <span class="token string">&quot;1.0.0&quot;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;scripts&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;enforcer&quot;</span><span class="token operator">:</span> <span class="token string">&quot;ts-node hooks/team-registry-enforcer.ts&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;updater&quot;</span><span class="token operator">:</span> <span class="token string">&quot;ts-node hooks/team-registry-updater.ts&quot;</span></span>
<span class="line">  <span class="token punctuation">}</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;dependencies&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span><span class="token punctuation">}</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;devDependencies&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;ts-node&quot;</span><span class="token operator">:</span> <span class="token string">&quot;^10.9.2&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;typescript&quot;</span><span class="token operator">:</span> <span class="token string">&quot;^5.4.5&quot;</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token property">&quot;@types/node&quot;</span><span class="token operator">:</span> <span class="token string">&quot;^20.12.7&quot;</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><h2 id="_4-동작-확인" tabindex="-1"><a class="header-anchor" href="#_4-동작-확인"><span>4. 동작 확인</span></a></h2><div class="language-bash line-numbers-mode" data-highlighter="prismjs" data-ext="sh" data-title="sh"><pre><code><span class="line"><span class="token comment"># 레지스트리 초기화 확인</span></span>
<span class="line"><span class="token function">ls</span> ~/.claude/registry/</span>
<span class="line"></span>
<span class="line"><span class="token comment"># 등록된 에이전트 목록 확인</span></span>
<span class="line"><span class="token function">cat</span> ~/.claude/registry/orchestrator.json</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Claude Code에서 동일한 이름의 에이전트를 두 번 생성하려 할 때 훅이 차단 메시지를 반환하면 정상 동작이다.</p><h2 id="_5-자주-발생하는-문제" tabindex="-1"><a class="header-anchor" href="#_5-자주-발생하는-문제"><span>5. 자주 발생하는 문제</span></a></h2><table><thead><tr><th>문제</th><th>원인</th><th>해결</th></tr></thead><tbody><tr><td>훅이 실행 안 됨</td><td>settings.json 경로 오류</td><td>절대경로로 수정</td></tr><tr><td>stale 판정 너무 빠름</td><td>STALE_THRESHOLD_MS 값</td><td>값 늘리기 (기본 5분)</td></tr><tr><td>registry 파일 없음</td><td>디렉토리 미생성</td><td>registry.ts의 mkdirSync 확인</td></tr><tr><td>ts-node 명령 없음</td><td>npm install 미실행</td><td><code>npm install</code> 실행</td></tr></tbody></table><h2 id="마무리" tabindex="-1"><a class="header-anchor" href="#마무리"><span>마무리</span></a></h2><p>팀이 커지면 agents/ 에 파일만 추가하면 된다. Specialist 역할이 필요하면 agents/design.md 또는 agents/qa.md를 추가하고 registry에 등록한다. 원칙이 흔들리면 CONSTITUTION.md로 돌아온다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><p>원칙 → 역할 → 소통 → 구현 → 문서화 → 헌법 → 실행</p><p>이 순서가 최고의 에이전트 워크플로우를 만든다.</p></div>`,33)]))}const o=s(e,[["render",l],["__file","08-scaffold.html.vue"]]),u=JSON.parse('{"path":"/study/ai-agent-workflow/08-scaffold.html","title":"CH8. Scaffold — 바로 복사해서 쓰는 템플릿","lang":"en-US","frontmatter":{"title":"CH8. Scaffold — 바로 복사해서 쓰는 템플릿","description":"이 챕터의 파일들을 복사하면 에이전트 워크플로우가 즉시 작동한다","date":"2026-04-16T00:00:00.000Z","tags":["Scaffold","Template","시작하기"]},"headers":[{"level":1,"title":"CH8. Scaffold — 바로 복사해서 쓰는 템플릿","slug":"ch8-scaffold-—-바로-복사해서-쓰는-템플릿","link":"#ch8-scaffold-—-바로-복사해서-쓰는-템플릿","children":[{"level":2,"title":"이 챕터의 목적","slug":"이-챕터의-목적","link":"#이-챕터의-목적","children":[]},{"level":2,"title":"1. 전체 디렉토리 구조","slug":"_1-전체-디렉토리-구조","link":"#_1-전체-디렉토리-구조","children":[{"level":3,"title":"각 파일의 역할 관계도","slug":"각-파일의-역할-관계도","link":"#각-파일의-역할-관계도","children":[]}]},{"level":2,"title":"2. 설정 순서 (Step by Step)","slug":"_2-설정-순서-step-by-step","link":"#_2-설정-순서-step-by-step","children":[]},{"level":2,"title":"3. 각 파일 완전한 템플릿","slug":"_3-각-파일-완전한-템플릿","link":"#_3-각-파일-완전한-템플릿","children":[]},{"level":2,"title":"4. 동작 확인","slug":"_4-동작-확인","link":"#_4-동작-확인","children":[]},{"level":2,"title":"5. 자주 발생하는 문제","slug":"_5-자주-발생하는-문제","link":"#_5-자주-발생하는-문제","children":[]},{"level":2,"title":"마무리","slug":"마무리","link":"#마무리","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/08-scaffold.md"}');export{o as comp,u as data};
