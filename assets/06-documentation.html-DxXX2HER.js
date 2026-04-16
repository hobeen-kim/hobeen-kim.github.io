import{_ as s,c as a,e as t,o as e}from"./app-CtpBQ_kQ.js";const i={};function l(p,n){return e(),a("div",null,n[0]||(n[0]=[t(`<h1 id="ch6-문서화-체계-—-어떤-폴더에-무엇을-남기는가" tabindex="-1"><a class="header-anchor" href="#ch6-문서화-체계-—-어떤-폴더에-무엇을-남기는가"><span>CH6. 문서화 체계 — 어떤 폴더에 무엇을 남기는가</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>왜 문서화가 자율성의 전제 조건인지 설명할 수 있다.</li><li>4종 문서(plans/implementations/decisions/wisdom)의 역할과 차이를 구분한다.</li><li>상황에 맞는 문서 유형을 선택하고, 올바른 시점에 작성할 수 있다.</li></ul></div><h2 id="_1-최고의-자율성은-최고의-정보-공유에서-나온다" tabindex="-1"><a class="header-anchor" href="#_1-최고의-자율성은-최고의-정보-공유에서-나온다"><span>1. &quot;최고의 자율성은 최고의 정보 공유에서 나온다&quot;</span></a></h2><p>에이전트 시스템을 설계할 때 가장 쉽게 간과하는 것이 문서화다. 각 에이전트가 독립적으로 작업하는 구조에서, 정보가 한 에이전트의 컨텍스트에 갇히면 전체 흐름이 막힌다. 오케스트레이터가 완료 여부를 판단하려 해도, Executor가 무엇을 했는지 알 수 없다면 검증이 불가능하다.</p><p>문서화는 에이전트 간 비동기 소통 채널이다. 에이전트가 종료되거나 컨텍스트가 초기화되어도 문서는 남는다. stale 에이전트 문제를 완전히 해결하지는 못하지만, 문서가 있으면 다음 에이전트가 이전 맥락을 이어받을 수 있다.</p><h3 id="문서화-없을-때-vs-있을-때" tabindex="-1"><a class="header-anchor" href="#문서화-없을-때-vs-있을-때"><span>문서화 없을 때 vs 있을 때</span></a></h3><pre class="mermaid">flowchart TD
    subgraph Without[&quot;문서화 없음&quot;]
        O1[Orchestrator] --&gt;|작업 지시| E1[Executor]
        E1 --&gt;|완료 주장| V1[Verifier]
        V1 --&gt;|무엇을?| Q1[알 수 없음]
        Q1 --&gt;|재확인 요청| E1
    end

    subgraph With[&quot;문서화 있음&quot;]
        O2[Orchestrator] --&gt;|작업 지시 + plan 작성| E2[Executor]
        E2 --&gt;|implementation 작성| V2[Verifier]
        V2 --&gt;|문서 기반 검증| R2[완료 선언]
    end
</pre><p>정보가 문서로 공유되지 않으면 Verifier는 &quot;무엇을 검증해야 하는가&quot;를 알 수 없다. 에이전트 간 신뢰는 구두 약속이 아니라 문서에 의해 형성된다.</p><h2 id="_2-4종-문서-체계" tabindex="-1"><a class="header-anchor" href="#_2-4종-문서-체계"><span>2. 4종 문서 체계</span></a></h2><p>문서는 4개의 폴더로 분리된다. 각 폴더는 작업 라이프사이클의 다른 시점을 담당한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">~/.obsidian-vault/ (또는 프로젝트 내)</span>
<span class="line">├── plans/           ← 실행 전 합의 문서</span>
<span class="line">├── implementations/ ← 실행 결과 + 증거</span>
<span class="line">├── decisions/       ← 왜 그 결정을 했는가 (ADR)</span>
<span class="line">└── wisdom/          ← 반복 실수 방지 + 패턴 누적</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><pre class="mermaid">flowchart LR
    A[작업 시작 전] --&gt;|plans/| B[합의된 계획]
    B --&gt;|실행| C[Executor 작업]
    C --&gt;|implementations/| D[결과 + 증거]
    D --&gt;|Verifier 검증| E[완료]

    C --&gt;|중요한 결정 발생| F[decisions/&lt;br&gt;ADR 작성]
    C --&gt;|실수 또는 학습| G[wisdom/&lt;br&gt;패턴 기록]
</pre><h3 id="plans" tabindex="-1"><a class="header-anchor" href="#plans"><span>plans/</span></a></h3><p>작업을 시작하기 전에 Orchestrator와 Planner가 작성한다. 목표, 접근법, DRI 배분, 완료 기준을 담는다. 실행 전 합의 문서이므로 팀 전체가 읽고 동의해야 한다.</p><table><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>작성 시점</td><td>실행 전</td></tr><tr><td>작성자</td><td>Orchestrator + Planner</td></tr><tr><td>핵심 내용</td><td>목표, 접근법, DRI, 완료 기준</td></tr><tr><td>frontmatter status</td><td>draft → approved</td></tr></tbody></table><p>plans 문서가 없으면 Executor는 &quot;무엇을 만들어야 하는가&quot;의 기준 없이 작업을 시작한다. 이후에 &quot;이게 맞지 않는다&quot;는 재작업이 발생한다.</p><h3 id="implementations" tabindex="-1"><a class="header-anchor" href="#implementations"><span>implementations/</span></a></h3><p>Executor가 작업을 완료한 뒤 작성한다. &quot;무엇을 했는가&quot;가 아니라 &quot;증거&quot;를 남긴다. 파일 경로, 커밋 해시, 변경된 함수 목록이 증거의 예시다. &quot;기능을 구현했다&quot;는 서술은 증거가 아니다.</p><table><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>작성 시점</td><td>실행 완료 후</td></tr><tr><td>작성자</td><td>Executor</td></tr><tr><td>핵심 내용</td><td>변경 내용, 파일 경로, 커밋, 남은 항목</td></tr><tr><td>규칙</td><td>결과가 아니라 증거로 보고한다</td></tr></tbody></table><h3 id="decisions" tabindex="-1"><a class="header-anchor" href="#decisions"><span>decisions/</span></a></h3><p>중요한 결정이 내려진 시점에 작성한다. ADR(Architecture Decision Record) 형식을 따른다. &quot;왜 그 결정을 했는가&quot;가 핵심이다. 결정 자체보다 이유를 기록하는 것이 목적이다.</p><p>나중에 재구성하면 실제 이유와 달라진다. 결정 당일에 작성해야 한다.</p><table><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>작성 시점</td><td>중요한 결정 발생 시</td></tr><tr><td>형식</td><td>ADR: 배경 / 결정 / 이유 / 대안들 / 결과</td></tr><tr><td>핵심</td><td>&quot;왜 그 결정을 했는가&quot;</td></tr></tbody></table><h3 id="wisdom" tabindex="-1"><a class="header-anchor" href="#wisdom"><span>wisdom/</span></a></h3><p>실수 또는 중요한 학습이 발생한 시점에 작성한다. &quot;무엇이 문제였는가&quot;와 &quot;다음에 어떻게 할 것인가&quot;를 기록한다. CH1의 Learn Proactively 원칙의 구체적 구현이다.</p><p>wisdom은 팀 전체가 읽을 수 있어야 한다. 특정 에이전트의 실수가 다른 에이전트의 실수 방지로 이어져야 의미가 있다.</p><table><thead><tr><th>항목</th><th>내용</th></tr></thead><tbody><tr><td>작성 시점</td><td>실수 또는 중요한 학습 발생 시</td></tr><tr><td>핵심 내용</td><td>문제, 원인, 다음 행동</td></tr><tr><td>접근 권한</td><td>팀 전체</td></tr></tbody></table><h2 id="_3-각-문서의-frontmatter-형식" tabindex="-1"><a class="header-anchor" href="#_3-각-문서의-frontmatter-형식"><span>3. 각 문서의 frontmatter 형식</span></a></h2><h3 id="plans-frontmatter" tabindex="-1"><a class="header-anchor" href="#plans-frontmatter"><span>plans/ frontmatter</span></a></h3><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">title</span><span class="token punctuation">:</span> <span class="token string">&quot;작업명&quot;</span></span>
<span class="line"><span class="token key atrule">status</span><span class="token punctuation">:</span> draft          <span class="token comment"># draft | approved | in-progress | done</span></span>
<span class="line"><span class="token key atrule">date</span><span class="token punctuation">:</span> <span class="token datetime number">2026-04-16</span></span>
<span class="line"><span class="token key atrule">owner</span><span class="token punctuation">:</span> orchestrator</span>
<span class="line"><span class="token key atrule">dri</span><span class="token punctuation">:</span> executor<span class="token punctuation">-</span>dev</span>
<span class="line"><span class="token key atrule">goal</span><span class="token punctuation">:</span> <span class="token string">&quot;무엇을 달성하는가&quot;</span></span>
<span class="line"><span class="token key atrule">acceptance_criteria</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token punctuation">-</span> <span class="token string">&quot;기준 1&quot;</span></span>
<span class="line">  <span class="token punctuation">-</span> <span class="token string">&quot;기준 2&quot;</span></span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="implementations-frontmatter" tabindex="-1"><a class="header-anchor" href="#implementations-frontmatter"><span>implementations/ frontmatter</span></a></h3><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">title</span><span class="token punctuation">:</span> <span class="token string">&quot;구현 결과: 작업명&quot;</span></span>
<span class="line"><span class="token key atrule">date</span><span class="token punctuation">:</span> <span class="token datetime number">2026-04-16</span></span>
<span class="line"><span class="token key atrule">executor</span><span class="token punctuation">:</span> executor<span class="token punctuation">-</span>dev</span>
<span class="line"><span class="token key atrule">plan_ref</span><span class="token punctuation">:</span> <span class="token string">&quot;plans/작업명.md&quot;</span></span>
<span class="line"><span class="token key atrule">status</span><span class="token punctuation">:</span> pending_review  <span class="token comment"># pending_review | approved</span></span>
<span class="line"><span class="token key atrule">evidence</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token punctuation">-</span> <span class="token key atrule">path</span><span class="token punctuation">:</span> <span class="token string">&quot;src/foo.ts&quot;</span></span>
<span class="line">    <span class="token key atrule">commit</span><span class="token punctuation">:</span> <span class="token string">&quot;abc1234&quot;</span></span>
<span class="line">  <span class="token punctuation">-</span> <span class="token key atrule">path</span><span class="token punctuation">:</span> <span class="token string">&quot;src/bar.ts&quot;</span></span>
<span class="line">    <span class="token key atrule">commit</span><span class="token punctuation">:</span> <span class="token string">&quot;abc1234&quot;</span></span>
<span class="line"><span class="token key atrule">remaining</span><span class="token punctuation">:</span> <span class="token punctuation">[</span><span class="token punctuation">]</span></span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="decisions-frontmatter" tabindex="-1"><a class="header-anchor" href="#decisions-frontmatter"><span>decisions/ frontmatter</span></a></h3><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">title</span><span class="token punctuation">:</span> <span class="token string">&quot;ADR-001: 결정 제목&quot;</span></span>
<span class="line"><span class="token key atrule">date</span><span class="token punctuation">:</span> <span class="token datetime number">2026-04-16</span></span>
<span class="line"><span class="token key atrule">status</span><span class="token punctuation">:</span> accepted       <span class="token comment"># proposed | accepted | deprecated | superseded</span></span>
<span class="line"><span class="token key atrule">deciders</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>orchestrator<span class="token punctuation">,</span> executor<span class="token punctuation">-</span>dev<span class="token punctuation">]</span></span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="wisdom-frontmatter" tabindex="-1"><a class="header-anchor" href="#wisdom-frontmatter"><span>wisdom/ frontmatter</span></a></h3><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">title</span><span class="token punctuation">:</span> <span class="token string">&quot;패턴 제목&quot;</span></span>
<span class="line"><span class="token key atrule">date</span><span class="token punctuation">:</span> <span class="token datetime number">2026-04-16</span></span>
<span class="line"><span class="token key atrule">source</span><span class="token punctuation">:</span> <span class="token string">&quot;어떤 작업에서 발생했는가&quot;</span></span>
<span class="line"><span class="token key atrule">severity</span><span class="token punctuation">:</span> warning      <span class="token comment"># info | warning | critical</span></span>
<span class="line"><span class="token key atrule">tags</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>typescript<span class="token punctuation">,</span> api<span class="token punctuation">,</span> null<span class="token punctuation">-</span>handling<span class="token punctuation">]</span></span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="_4-문서-작성-규칙" tabindex="-1"><a class="header-anchor" href="#_4-문서-작성-규칙"><span>4. 문서 작성 규칙</span></a></h2><p>4종 문서 각각에 지켜야 할 규칙이 있다. 이 규칙을 어기면 문서가 존재해도 신뢰할 수 없게 된다.</p><p><strong>plans</strong>는 실행 전 반드시 존재해야 한다. Orchestrator의 책임이다. plans 없이 Executor가 작업을 시작하면 완료 기준이 없으므로 Verifier가 검증을 할 수 없다.</p><p><strong>implementations</strong>는 증거 없이 작성이 금지된다. &quot;구현 완료&quot; 한 줄로 끝내는 것은 무효다. Verifier가 확인할 수 있는 파일 경로, 커밋, 변경 목록이 반드시 포함되어야 한다.</p><p><strong>decisions</strong>는 결정 당일에 작성한다. 나중에 재구성하면 기억이 편집되어 실제 이유와 달라진다. 결정이 내려진 그 시점에 15분 안에 초안을 남긴다.</p><p><strong>wisdom</strong>은 팀 전체가 읽을 수 있어야 한다. 특정 에이전트 전용으로 작성하면 패턴이 공유되지 않는다. 작성 후 팀에 알린다.</p><h2 id="_5-작업-라이프사이클과-문서-작성-타이밍" tabindex="-1"><a class="header-anchor" href="#_5-작업-라이프사이클과-문서-작성-타이밍"><span>5. 작업 라이프사이클과 문서 작성 타이밍</span></a></h2><pre class="mermaid">sequenceDiagram
    participant O as Orchestrator
    participant E as Executor
    participant V as Verifier
    participant D as 문서 시스템

    O-&gt;&gt;D: plans/ 작성 (status: approved)
    O-&gt;&gt;E: 작업 위임
    E-&gt;&gt;D: plans/ 읽기 (목표 + 완료 기준 확인)
    E-&gt;&gt;E: 구현 실행

    alt 중요한 결정 발생
        E-&gt;&gt;D: decisions/ 작성 (ADR)
    end

    alt 실수 또는 학습
        E-&gt;&gt;D: wisdom/ 작성
    end

    E-&gt;&gt;D: implementations/ 작성 (증거 포함)
    E-&gt;&gt;V: 검증 요청

    V-&gt;&gt;D: implementations/ 읽기
    V-&gt;&gt;D: plans/ 읽기 (완료 기준 확인)
    V-&gt;&gt;V: 기준 충족 여부 검증

    alt 기준 미달
        V--&gt;&gt;E: 피드백 반환
        E-&gt;&gt;D: implementations/ 업데이트
    else 기준 충족
        V-&gt;&gt;D: implementations/ status: approved
        V--&gt;&gt;O: 완료 선언
    end
</pre><h2 id="_6-obsidian을-허브로" tabindex="-1"><a class="header-anchor" href="#_6-obsidian을-허브로"><span>6. Obsidian을 허브로</span></a></h2><p>모든 문서를 Obsidian vault에 보관한다. Obsidian은 마크다운 기반이므로 에이전트가 직접 읽고 쓸 수 있다. 에이전트는 작업 시작 전 vault에서 관련 plans와 wisdom을 조회하여 컨텍스트를 파악한다.</p><p>archivist 에이전트가 vault 관리를 담당한다. stale 문서를 정리하고, 중복 wisdom을 통합하고, decisions의 상태를 최신으로 유지한다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>문서화는 에이전트 간 비동기 소통 채널이다. 에이전트가 사라져도 문서는 남는다.</li><li>4종 문서는 작업 라이프사이클의 각기 다른 시점을 담당한다. plans → implementations → decisions → wisdom 순서로 쌓인다.</li><li>plans 없이 시작 금지, implementations는 증거 필수, decisions는 당일 작성, wisdom은 팀 공유.</li><li>Obsidian vault가 문서의 중앙 허브다. 에이전트는 작업 전 vault를 먼저 읽는다.</li></ul><p>다음 챕터: <a href="/study/ai-agent-workflow/07-constitution">CH7. 에이전트 헌법</a></p></div>`,48)]))}const r=s(i,[["render",l],["__file","06-documentation.html.vue"]]),c=JSON.parse('{"path":"/study/ai-agent-workflow/06-documentation.html","title":"CH6. 문서화 체계 — 어떤 폴더에 무엇을 남기는가","lang":"en-US","frontmatter":{"title":"CH6. 문서화 체계 — 어떤 폴더에 무엇을 남기는가","description":"에이전트 간 정보 공유의 구체적 구현. 4종 문서의 역할과 작성 규칙을 정의한다","date":"2026-04-16T00:00:00.000Z","tags":["Documentation","Obsidian","문서화","정보공유"]},"headers":[{"level":1,"title":"CH6. 문서화 체계 — 어떤 폴더에 무엇을 남기는가","slug":"ch6-문서화-체계-—-어떤-폴더에-무엇을-남기는가","link":"#ch6-문서화-체계-—-어떤-폴더에-무엇을-남기는가","children":[{"level":2,"title":"1. \\"최고의 자율성은 최고의 정보 공유에서 나온다\\"","slug":"_1-최고의-자율성은-최고의-정보-공유에서-나온다","link":"#_1-최고의-자율성은-최고의-정보-공유에서-나온다","children":[{"level":3,"title":"문서화 없을 때 vs 있을 때","slug":"문서화-없을-때-vs-있을-때","link":"#문서화-없을-때-vs-있을-때","children":[]}]},{"level":2,"title":"2. 4종 문서 체계","slug":"_2-4종-문서-체계","link":"#_2-4종-문서-체계","children":[{"level":3,"title":"plans/","slug":"plans","link":"#plans","children":[]},{"level":3,"title":"implementations/","slug":"implementations","link":"#implementations","children":[]},{"level":3,"title":"decisions/","slug":"decisions","link":"#decisions","children":[]},{"level":3,"title":"wisdom/","slug":"wisdom","link":"#wisdom","children":[]}]},{"level":2,"title":"3. 각 문서의 frontmatter 형식","slug":"_3-각-문서의-frontmatter-형식","link":"#_3-각-문서의-frontmatter-형식","children":[{"level":3,"title":"plans/ frontmatter","slug":"plans-frontmatter","link":"#plans-frontmatter","children":[]},{"level":3,"title":"implementations/ frontmatter","slug":"implementations-frontmatter","link":"#implementations-frontmatter","children":[]},{"level":3,"title":"decisions/ frontmatter","slug":"decisions-frontmatter","link":"#decisions-frontmatter","children":[]},{"level":3,"title":"wisdom/ frontmatter","slug":"wisdom-frontmatter","link":"#wisdom-frontmatter","children":[]}]},{"level":2,"title":"4. 문서 작성 규칙","slug":"_4-문서-작성-규칙","link":"#_4-문서-작성-규칙","children":[]},{"level":2,"title":"5. 작업 라이프사이클과 문서 작성 타이밍","slug":"_5-작업-라이프사이클과-문서-작성-타이밍","link":"#_5-작업-라이프사이클과-문서-작성-타이밍","children":[]},{"level":2,"title":"6. Obsidian을 허브로","slug":"_6-obsidian을-허브로","link":"#_6-obsidian을-허브로","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/06-documentation.md"}');export{r as comp,c as data};
