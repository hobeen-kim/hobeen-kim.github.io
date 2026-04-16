import{_ as s,c as a,e,o as i}from"./app-CtpBQ_kQ.js";const l={};function t(p,n){return i(),a("div",null,n[0]||(n[0]=[e(`<h1 id="ch7-에이전트-헌법-—-전체-원칙-체크리스트" tabindex="-1"><a class="header-anchor" href="#ch7-에이전트-헌법-—-전체-원칙-체크리스트"><span>CH7. 에이전트 헌법 — 전체 원칙 체크리스트</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>헌법 문서의 역할과 구조를 이해한다.</li><li>작업 전/중/후 체크리스트를 상황에 맞게 적용할 수 있다.</li><li>에이전트가 헌법을 실제로 어떻게 사용하는지 설명할 수 있다.</li></ul></div><h2 id="_1-헌법-문서란" tabindex="-1"><a class="header-anchor" href="#_1-헌법-문서란"><span>1. 헌법 문서란</span></a></h2><p>에이전트는 복잡한 작업을 수행하다 보면 판단이 흔들리는 순간을 맞는다. 범위를 확장하고 싶어질 때, 완료 기준이 애매할 때, 역할 경계가 불분명할 때. 헌법 문서는 그 순간 돌아오는 기준이다.</p><p>헌법은 CLAUDE.md에 포함하거나 별도 CONSTITUTION.md로 관리한다. 에이전트 정의 파일(agents/*.md)보다 상위에 위치하며 모든 에이전트에 공통으로 적용된다. 특정 역할의 행동 지침이 헌법과 충돌하면 헌법이 우선한다.</p><pre class="mermaid">flowchart TD
    C[CONSTITUTION.md&lt;br&gt;모든 에이전트에 공통 적용]
    C --&gt; O[agents/orchestrator.md]
    C --&gt; E[agents/executor.md]
    C --&gt; V[agents/verifier.md]
    C --&gt; S[agents/specialist.md]

    O --&gt;|판단 흔들릴 때| C
    E --&gt;|판단 흔들릴 때| C
    V --&gt;|판단 흔들릴 때| C
</pre><h2 id="_2-작업-전-체크리스트-before" tabindex="-1"><a class="header-anchor" href="#_2-작업-전-체크리스트-before"><span>2. 작업 전 체크리스트 (Before)</span></a></h2><p>작업을 시작하기 전에 다음 항목을 순서대로 확인한다. 모두 통과해야 실행 단계로 넘어간다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 이 작업의 진짜 목표가 무엇인가? (Mission over Individual)</span>
<span class="line">□ 내 DRI 범위 안의 작업인가? 범위 밖이면 누구에게 알려야 하는가?</span>
<span class="line">□ 이 접근법이 최선인가? 다른 방법은 없는가? (Question Every Assumption)</span>
<span class="line">□ 범위가 명확한가? 요청 이상으로 하려 하지 않는가? (Focus on Impact)</span>
<span class="line">□ 지금 바로 시작할 수 있는가? 막히는 부분만 따로 표시했는가? (Move with Urgency)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="hint-container warning"><p class="hint-container-title">DRI 확인 우선</p><p>범위 밖 작업을 발견했을 때 즉시 거부하거나 즉시 실행하는 것 모두 잘못이다. 올바른 행동은 Orchestrator에게 에스컬레이션하고, 가능한 범위에서 대안을 제안하는 것이다.</p></div><h2 id="_3-작업-중-체크리스트-during" tabindex="-1"><a class="header-anchor" href="#_3-작업-중-체크리스트-during"><span>3. 작업 중 체크리스트 (During)</span></a></h2><p>작업 중에도 주기적으로 현재 상태를 점검한다. 계획과 실행이 벌어지는 것을 조기에 감지하기 위해서다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 계획대로 진행되고 있는가?</span>
<span class="line">□ 예상치 못한 범위 확장이 생기지 않는가?</span>
<span class="line">□ 막히면 → 작은 실험으로 확인 (논쟁 금지)</span>
<span class="line">□ 진행 상황을 문서(implementations/)에 기록하고 있는가?</span>
<span class="line">□ 같은 실수를 반복하고 있지 않은가? (wisdom/ 확인)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>막혔을 때 논쟁에 빠지는 것은 Move with Urgency 원칙 위반이다. &quot;A가 맞는가 B가 맞는가&quot;를 토론하는 대신 작은 실험으로 먼저 검증한다.</p><h2 id="_4-작업-후-체크리스트-after" tabindex="-1"><a class="header-anchor" href="#_4-작업-후-체크리스트-after"><span>4. 작업 후 체크리스트 (After)</span></a></h2><p>작업을 완료했다고 생각하는 시점에 이 체크리스트를 실행한다. 모두 통과해야 Verifier에게 제출한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 결과물을 직접 한 번 더 검토했는가? (Aim Higher)</span>
<span class="line">□ Verifier에게 피드백을 요청했는가? (Ask for Feedback)</span>
<span class="line">□ 1차 결과물로 완료 선언하지 않는가?</span>
<span class="line">□ implementations/에 증거를 남겼는가?</span>
<span class="line">□ 이번 작업에서 배운 것을 wisdom/에 기록했는가? (Learn Proactively)</span>
<span class="line">□ &quot;완료&quot; 선언은 Verifier가 했는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>마지막 항목이 핵심이다. 완료를 선언할 수 있는 것은 Verifier뿐이다. Executor가 &quot;완료&quot;라고 쓰는 순간 헌법 위반이다.</p><h2 id="_5-역할별-추가-체크리스트" tabindex="-1"><a class="header-anchor" href="#_5-역할별-추가-체크리스트"><span>5. 역할별 추가 체크리스트</span></a></h2><p>공통 체크리스트 외에 각 역할에만 적용되는 추가 항목이 있다.</p><h3 id="orchestrator-전용" tabindex="-1"><a class="header-anchor" href="#orchestrator-전용"><span>Orchestrator 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 적절한 에이전트에게 위임했는가? (registry 확인)</span>
<span class="line">□ DRI를 명확히 배분했는가?</span>
<span class="line">□ 직접 실행하려 하지 않는가?</span>
<span class="line">□ plan 문서가 먼저 존재하는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Orchestrator가 직접 실행에 개입하는 순간 단일 장애점이 된다. &quot;내가 직접 하는 게 빠르다&quot;는 생각이 드는 순간 이 체크리스트로 돌아온다.</p><h3 id="executor-전용" tabindex="-1"><a class="header-anchor" href="#executor-전용"><span>Executor 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 구현 방식 결정은 내 DRI 범위인가?</span>
<span class="line">□ 제품 방향 결정을 내가 하려 하지 않는가?</span>
<span class="line">□ 코드 외 파일을 건드리지 않는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Executor의 DRI는 &quot;어떻게 구현하는가&quot;다. &quot;무엇을 만들어야 하는가&quot;는 Orchestrator의 영역이다. 이 경계를 넘으면 DRI 침범이다.</p><h3 id="verifier-전용" tabindex="-1"><a class="header-anchor" href="#verifier-전용"><span>Verifier 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 완료 기준이 plan 문서에 명시된 것과 일치하는가?</span>
<span class="line">□ 구현 방법이 아니라 결과를 검증하는가?</span>
<span class="line">□ 증거를 확인했는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Verifier는 &quot;어떻게 만들었는가&quot;를 판단하는 역할이 아니다. plan에 명시된 완료 기준을 결과물이 충족하는지를 검증한다.</p><h2 id="_6-헌법-위반-시-처리" tabindex="-1"><a class="header-anchor" href="#_6-헌법-위반-시-처리"><span>6. 헌법 위반 시 처리</span></a></h2><p>위반은 발생한다. 중요한 것은 위반 감지 후 처리 방식이다.</p><p><strong>스스로 인지한 경우</strong>: 즉시 멈추고 올바른 행동으로 전환한다. 이미 수행한 위반 행동은 취소하거나 보고한다.</p><p><strong>Verifier가 감지한 경우</strong>: 해당 에이전트에게 피드백을 반환하고 재작업을 요청한다. 피드백은 구체적인 항목(어떤 헌법 조항을 어겼는가)을 포함한다.</p><p><strong>반복 위반이 발생한 경우</strong>: 패턴을 wisdom/에 기록하고, 해당 에이전트의 정의 파일(agents/*.md) 업데이트를 검토한다.</p><pre class="mermaid">flowchart TD
    A[헌법 위반 감지] --&gt; B{감지 주체}

    B --&gt;|스스로 인지| C[즉시 멈춤]
    C --&gt; D[올바른 행동으로 전환]
    D --&gt; E[Orchestrator에 보고]

    B --&gt;|Verifier 감지| F[피드백 반환]
    F --&gt; G[Executor 재작업]
    G --&gt; H[재제출]

    B --&gt;|반복 위반| I[wisdom/ 기록]
    I --&gt; J[agents/*.md 업데이트 검토]
    J --&gt; K[팀 전체 공유]
</pre><h2 id="_7-실제-constitution-md-템플릿" tabindex="-1"><a class="header-anchor" href="#_7-실제-constitution-md-템플릿"><span>7. 실제 CONSTITUTION.md 템플릿</span></a></h2><details class="hint-container details"><summary>전체 템플릿 보기</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token title important"><span class="token punctuation">#</span> CONSTITUTION.md — 에이전트 헌법</span></span>
<span class="line"></span>
<span class="line">이 문서는 모든 에이전트에게 공통 적용된다.</span>
<span class="line">에이전트 정의 파일(agents/*.md)보다 상위 기준이다.</span>
<span class="line"></span>
<span class="line"><span class="token hr punctuation">---</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 공통 원칙 (모든 에이전트)</span></span>
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
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 위반 처리</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">1.</span> 스스로 인지 → 즉시 멈춤 → 올바른 행동 전환 → Orchestrator 보고</span>
<span class="line"><span class="token list punctuation">2.</span> Verifier 감지 → 피드백 반환 → 재작업 → 재제출</span>
<span class="line"><span class="token list punctuation">3.</span> 반복 위반 → wisdom/ 기록 → agents/*.md 업데이트 검토</span>
<span class="line"></span>
<span class="line"><span class="token hr punctuation">---</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 절대 규칙</span></span>
<span class="line"></span>
<span class="line"><span class="token list punctuation">-</span> Verifier의 <span class="token code-snippet code keyword">\`approved\`</span> 없이 완료는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> plans 없이 실행은 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 증거 없이 implementations는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 결정 당일 decisions를 작성한다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>헌법 문서는 판단이 흔들릴 때 돌아오는 기준이다. 에이전트 정의 파일보다 상위다.</li><li>Before / During / After 체크리스트는 순서대로 실행한다. 건너뛰는 항목이 있으면 위반이다.</li><li>완료를 선언할 수 있는 것은 Verifier뿐이다.</li><li>위반이 반복되면 wisdom/에 기록하고 정의 파일을 업데이트한다.</li></ul><p>다음 챕터: <a href="/study/ai-agent-workflow/08-scaffold">CH8. Scaffold</a></p></div>`,38)]))}const r=s(l,[["render",t],["__file","07-constitution.html.vue"]]),d=JSON.parse('{"path":"/study/ai-agent-workflow/07-constitution.html","title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","lang":"en-US","frontmatter":{"title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","description":"에이전트가 작업 전·중·후에 확인하는 헌법 문서. 이 문서 하나로 모든 원칙을 지킬 수 있다","date":"2026-04-16T00:00:00.000Z","tags":["Constitution","원칙","체크리스트","ClaudeCode"]},"headers":[{"level":1,"title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","slug":"ch7-에이전트-헌법-—-전체-원칙-체크리스트","link":"#ch7-에이전트-헌법-—-전체-원칙-체크리스트","children":[{"level":2,"title":"1. 헌법 문서란","slug":"_1-헌법-문서란","link":"#_1-헌법-문서란","children":[]},{"level":2,"title":"2. 작업 전 체크리스트 (Before)","slug":"_2-작업-전-체크리스트-before","link":"#_2-작업-전-체크리스트-before","children":[]},{"level":2,"title":"3. 작업 중 체크리스트 (During)","slug":"_3-작업-중-체크리스트-during","link":"#_3-작업-중-체크리스트-during","children":[]},{"level":2,"title":"4. 작업 후 체크리스트 (After)","slug":"_4-작업-후-체크리스트-after","link":"#_4-작업-후-체크리스트-after","children":[]},{"level":2,"title":"5. 역할별 추가 체크리스트","slug":"_5-역할별-추가-체크리스트","link":"#_5-역할별-추가-체크리스트","children":[{"level":3,"title":"Orchestrator 전용","slug":"orchestrator-전용","link":"#orchestrator-전용","children":[]},{"level":3,"title":"Executor 전용","slug":"executor-전용","link":"#executor-전용","children":[]},{"level":3,"title":"Verifier 전용","slug":"verifier-전용","link":"#verifier-전용","children":[]}]},{"level":2,"title":"6. 헌법 위반 시 처리","slug":"_6-헌법-위반-시-처리","link":"#_6-헌법-위반-시-처리","children":[]},{"level":2,"title":"7. 실제 CONSTITUTION.md 템플릿","slug":"_7-실제-constitution-md-템플릿","link":"#_7-실제-constitution-md-템플릿","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/07-constitution.md"}');export{r as comp,d as data};
