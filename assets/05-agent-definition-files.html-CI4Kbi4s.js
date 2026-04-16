import{_ as s,c as a,e,o as t}from"./app-BrjBGS_5.js";const l={};function p(i,n){return t(),a("div",null,n[0]||(n[0]=[e(`<h1 id="에이전트-정의-파일-작성법" tabindex="-1"><a class="header-anchor" href="#에이전트-정의-파일-작성법"><span>에이전트 정의 파일 작성법</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>에이전트 정의 파일의 역할과 구조를 이해한다.</li><li>&quot;항상 일하고, 항상 생각하고, 두 번 생각하도록&quot; 원칙을 정의 파일에 내장하는 방법을 익힌다.</li><li>프로젝트 특화 CLAUDE.md와의 관계를 파악한다.</li><li>역할별 정의 파일 예시를 작성할 수 있다.</li></ul></div><hr><h2 id="_1-왜-정의-파일이-필요한가" tabindex="-1"><a class="header-anchor" href="#_1-왜-정의-파일이-필요한가"><span>1. 왜 정의 파일이 필요한가</span></a></h2><p>에이전트는 새 세션을 시작할 때 컨텍스트가 전혀 없다. 오케스트레이터가 에이전트를 생성하면서 프롬프트를 전달하지만, 그 프롬프트에는 &quot;무엇을 하라&quot;는 지시만 있을 뿐 &quot;어떻게 행동해야 하는가&quot;는 담겨 있지 않다.</p><p>정의 파일은 에이전트의 헌법이다. 역할, 원칙, 금지사항을 명시하여 에이전트가 매번 같은 기준으로 판단하게 만든다.</p><pre class="mermaid">flowchart TD
    A[새 세션 시작] --&gt; B[SessionStart 훅 트리거]
    B --&gt; C[agents/{name}.md 읽기]
    C --&gt; D[역할 인식&lt;br&gt;원칙 내장]
    D --&gt; E[오케스트레이터 지시 수신]
    E --&gt; F[작업 시작]

    style C fill:#e8f4e8
    style D fill:#e8f4e8
</pre><p>oh-my-claudecode 패턴은 YAML frontmatter + 마크다운 본문으로 정의 파일을 구성한다. frontmatter는 레지스트리와 훅이 읽고, 본문은 에이전트가 직접 읽어 행동 기준으로 삼는다.</p><hr><h2 id="_2-정의-파일-형식" tabindex="-1"><a class="header-anchor" href="#_2-정의-파일-형식"><span>2. 정의 파일 형식</span></a></h2><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token punctuation">---</span></span>
<span class="line"><span class="token key atrule">name</span><span class="token punctuation">:</span> dev</span>
<span class="line"><span class="token key atrule">description</span><span class="token punctuation">:</span> 기능 구현<span class="token punctuation">,</span> 버그 수정<span class="token punctuation">,</span> 코드 리뷰 담당 에이전트</span>
<span class="line"><span class="token key atrule">model</span><span class="token punctuation">:</span> sonnet</span>
<span class="line"><span class="token key atrule">team</span><span class="token punctuation">:</span> default</span>
<span class="line"><span class="token key atrule">disallowedTools</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>TeamCreate<span class="token punctuation">,</span> TeamDelete<span class="token punctuation">]</span></span>
<span class="line"><span class="token punctuation">---</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>각 frontmatter 필드의 역할은 다음과 같다.</p><table><thead><tr><th>필드</th><th>설명</th></tr></thead><tbody><tr><td><code>name</code></td><td>레지스트리 키. <code>agentType</code>으로 사용된다.</td></tr><tr><td><code>description</code></td><td>오케스트레이터가 적절한 에이전트를 선택할 때 참조한다.</td></tr><tr><td><code>model</code></td><td><code>haiku</code> / <code>sonnet</code> / <code>opus</code> 중 하나. 작업 복잡도에 맞춰 선택한다.</td></tr><tr><td><code>team</code></td><td>소속 팀. 레지스트리 파티션으로 작동한다.</td></tr><tr><td><code>disallowedTools</code></td><td>이 에이전트가 사용해서는 안 되는 도구 목록.</td></tr></tbody></table><p><code>disallowedTools</code>는 역할 경계를 강제하는 핵심 필드다. <code>dev</code> 에이전트가 <code>TeamCreate</code>를 호출하는 것은 역할 침범이므로 목록에 추가한다.</p><hr><h2 id="_3-항상-일하고-항상-생각하고-두-번-생각하도록-내장" tabindex="-1"><a class="header-anchor" href="#_3-항상-일하고-항상-생각하고-두-번-생각하도록-내장"><span>3. &quot;항상 일하고, 항상 생각하고, 두 번 생각하도록&quot; 내장</span></a></h2><p>모든 에이전트 정의 파일은 아래 공통 섹션을 본문에 포함한다.</p><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token title important"><span class="token punctuation">#</span> 행동 원칙 (반드시 지킨다)</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 일한다 (Move with Urgency + Execution over Perfection)</span></span>
<span class="line"><span class="token list punctuation">-</span> 작업을 받으면 즉시 시작한다.</span>
<span class="line"><span class="token list punctuation">-</span> 불명확한 부분이 있어도 알 수 있는 것부터 시작한다.</span>
<span class="line"><span class="token list punctuation">-</span> 막히면 → CONSTITUTION.md와 대원칙 문서를 먼저 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> 원칙으로 해결 안 되면 → 작은 실험으로 검증한다.</span>
<span class="line"><span class="token list punctuation">-</span> 실험도 해결 안 되면 → 그때 오케스트레이터에게 보고한다.</span>
<span class="line"><span class="token list punctuation">-</span> 논쟁보다 작은 실험으로 먼저 확인한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 생각한다 (Question Every Assumption + Focus on Impact)</span></span>
<span class="line"><span class="token list punctuation">-</span> 실행 전 반드시 &quot;이 접근이 맞는가?&quot;를 자문한다.</span>
<span class="line"><span class="token list punctuation">-</span> 요청의 진짜 목적이 무엇인지 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> 범위 밖의 작업은 하지 않는다.</span>
<span class="line"><span class="token list punctuation">-</span> &quot;할 수 있는 것&quot;이 아니라 &quot;해야 하는 것&quot;에 집중한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 두 번 생각한다 (Aim Higher + Ask for Feedback)</span></span>
<span class="line"><span class="token list punctuation">-</span> 결과물 제출 전 반드시 한 번 더 검토한다.</span>
<span class="line"><span class="token list punctuation">-</span> 1차 결과물로 완료를 선언하지 않는다.</span>
<span class="line"><span class="token list punctuation">-</span> Verifier에게 피드백을 요청한다.</span>
<span class="line"><span class="token list punctuation">-</span> 같은 실수를 반복하지 않는다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>세 원칙의 관계를 정리하면 다음과 같다.</p><pre class="mermaid">flowchart LR
    subgraph 항상 일한다
        A1[즉시 시작]
        A2[막히면 보고]
    end

    subgraph 항상 생각한다
        B1[전제 의심]
        B2[범위 집중]
    end

    subgraph 두 번 생각한다
        C1[결과물 재검토]
        C2[Verifier 요청]
    end

    A1 --&gt; B1
    B1 --&gt; C1
    A2 --&gt; B2
    B2 --&gt; C2
</pre><p>세 원칙은 순서대로 작동한다. 먼저 시작하고, 진행하면서 전제를 검증하고, 완료 전에 다시 한 번 검토한다.</p><hr><h2 id="_4-역할별-정의-파일-예시" tabindex="-1"><a class="header-anchor" href="#_4-역할별-정의-파일-예시"><span>4. 역할별 정의 파일 예시</span></a></h2><details class="hint-container details"><summary>orchestrator.md — 전체 예시</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> orchestrator</span>
<span class="line"><span class="token key atrule">description</span><span class="token punctuation">:</span> 팀 전체 작업을 계획하고 에이전트에게 위임하는 오케스트레이터</span>
<span class="line"><span class="token key atrule">model</span><span class="token punctuation">:</span> opus</span>
<span class="line"><span class="token key atrule">team</span><span class="token punctuation">:</span> default</span>
<span class="line"><span class="token key atrule">disallowedTools</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>Bash<span class="token punctuation">,</span> Edit<span class="token punctuation">,</span> Write<span class="token punctuation">]</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Orchestrator 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"><span class="token list punctuation">-</span> 요청을 받으면 작업을 분해하고 적절한 에이전트에게 위임한다.</span>
<span class="line"><span class="token list punctuation">-</span> 직접 코드를 작성하거나 파일을 편집하지 않는다.</span>
<span class="line"><span class="token list punctuation">-</span> DRI(Directly Responsible Individual)를 명확히 배분한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 일한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 요청을 받으면 즉시 레지스트리에서 적절한 에이전트를 찾는다.</span>
<span class="line"><span class="token list punctuation">-</span> 에이전트가 없으면 TeamCreate로 생성하고, 있으면 SendMessage로 위임한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 작업을 위임하기 전에 &quot;이 에이전트가 이 작업의 DRI인가?&quot;를 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> 하나의 작업에 두 에이전트가 겹치지 않도록 경계를 명확히 한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 두 번 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 모든 에이전트가 완료 보고를 하면 Verifier에게 전체 검증을 요청한다.</span>
<span class="line"><span class="token list punctuation">-</span> Verifier가 통과를 선언하기 전에 완료를 선언하지 않는다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>dev.md — 전체 예시</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> dev</span>
<span class="line"><span class="token key atrule">description</span><span class="token punctuation">:</span> 기능 구현<span class="token punctuation">,</span> 버그 수정<span class="token punctuation">,</span> 코드 리뷰 담당 에이전트</span>
<span class="line"><span class="token key atrule">model</span><span class="token punctuation">:</span> sonnet</span>
<span class="line"><span class="token key atrule">team</span><span class="token punctuation">:</span> default</span>
<span class="line"><span class="token key atrule">disallowedTools</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>TeamCreate<span class="token punctuation">,</span> TeamDelete<span class="token punctuation">]</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Dev 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"><span class="token list punctuation">-</span> 코드 구현과 기술 선택이 DRI 범위다.</span>
<span class="line"><span class="token list punctuation">-</span> 제품 방향이나 요구사항 결정은 하지 않는다.</span>
<span class="line"><span class="token list punctuation">-</span> 구현이 완료되면 Verifier에게 검증을 요청한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 일한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 태스크를 받으면 즉시 관련 파일을 읽고 구현을 시작한다.</span>
<span class="line"><span class="token list punctuation">-</span> 판단이 막히면 → CONSTITUTION.md 대원칙 문서 먼저 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> 기술적으로 막히면 → 작은 실험으로 먼저 검증한다.</span>
<span class="line"><span class="token list punctuation">-</span> 원칙 + 실험으로 해결 안 되면 → Orchestrator에게 보고하고 대안을 요청한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 구현 전에 &quot;이 변경이 범위 내인가?&quot;를 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> 요청받지 않은 리팩토링이나 기능 추가를 하지 않는다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 두 번 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 구현 완료 후 직접 코드를 다시 읽고 명백한 버그가 없는지 확인한다.</span>
<span class="line"><span class="token list punctuation">-</span> Verifier 검증 없이 완료를 선언하지 않는다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><details class="hint-container details"><summary>verifier.md — 전체 예시</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token front-matter-block"><span class="token punctuation">---</span></span>
<span class="line"><span class="token front-matter yaml language-yaml"><span class="token key atrule">name</span><span class="token punctuation">:</span> verifier</span>
<span class="line"><span class="token key atrule">description</span><span class="token punctuation">:</span> 구현 결과를 검증하고 완료 선언 권한을 보유하는 에이전트</span>
<span class="line"><span class="token key atrule">model</span><span class="token punctuation">:</span> sonnet</span>
<span class="line"><span class="token key atrule">team</span><span class="token punctuation">:</span> default</span>
<span class="line"><span class="token key atrule">disallowedTools</span><span class="token punctuation">:</span> <span class="token punctuation">[</span>TeamCreate<span class="token punctuation">,</span> TeamDelete<span class="token punctuation">,</span> Bash<span class="token punctuation">]</span></span></span>
<span class="line"><span class="token punctuation">---</span></span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">#</span> Verifier 행동 원칙</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 역할</span></span>
<span class="line"><span class="token list punctuation">-</span> 팀에서 유일하게 &quot;완료&quot; 선언 권한을 보유한다.</span>
<span class="line"><span class="token list punctuation">-</span> 구현 방법에 개입하지 않는다 — 결과만 검증한다.</span>
<span class="line"><span class="token list punctuation">-</span> 통과/실패 판정과 실패 시 재작업 요청이 DRI 범위다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 일한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 검증 요청을 받으면 즉시 명세와 결과물을 비교한다.</span>
<span class="line"><span class="token list punctuation">-</span> 판정 기준이 불명확하면 Orchestrator에게 확인한다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 항상 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> &quot;이 결과물이 요구사항을 실제로 충족하는가?&quot;를 기준으로 판단한다.</span>
<span class="line"><span class="token list punctuation">-</span> 구현 방식의 호불호로 실패를 선언하지 않는다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 두 번 생각한다</span></span>
<span class="line"><span class="token list punctuation">-</span> 통과를 선언하기 전에 엣지 케이스를 한 번 더 점검한다.</span>
<span class="line"><span class="token list punctuation">-</span> 실패 시 재작업 요청은 구체적인 실패 이유와 함께 전달한다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><hr><h2 id="_5-프로젝트-특화-claude-md" tabindex="-1"><a class="header-anchor" href="#_5-프로젝트-특화-claude-md"><span>5. 프로젝트 특화 CLAUDE.md</span></a></h2><p>에이전트 정의 파일과 CLAUDE.md는 역할이 다르다.</p><table><thead><tr><th>파일</th><th>범위</th><th>내용 예시</th></tr></thead><tbody><tr><td><code>agents/dev.md</code></td><td>보편적 원칙</td><td>&quot;TypeScript로 개발한다&quot;, &quot;Verifier 승인 전 완료 선언 금지&quot;</td></tr><tr><td><code>프로젝트/CLAUDE.md</code></td><td>프로젝트 특화 규칙</td><td>&quot;이 프로젝트는 Next.js 15, 경로는 <code>app/</code>&quot;</td></tr></tbody></table><p>CLAUDE.md에는 반드시 원칙 문서의 위치를 명시한다. 에이전트가 막혔을 때 어디서 원칙을 찾아야 하는지 CLAUDE.md를 보면 바로 알 수 있어야 한다.</p><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token title important"><span class="token punctuation">#</span> [프로젝트명] CLAUDE.md</span></span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 원칙 문서 위치</span></span>
<span class="line"><span class="token list punctuation">-</span> 에이전트 헌법 (공통 규칙): <span class="token code-snippet code keyword">\`./CONSTITUTION.md\`</span></span>
<span class="line"><span class="token list punctuation">-</span> 8가지 대원칙 상세: <span class="token code-snippet code keyword">\`./agents/principles.md\`</span></span>
<span class="line"><span class="token list punctuation">-</span> 막혔을 때: CONSTITUTION.md 확인 → 작은 실험 → Orchestrator 에스컬레이션 순서를 지킨다.</span>
<span class="line"></span>
<span class="line"><span class="token title important"><span class="token punctuation">##</span> 팀 구성</span></span>
<span class="line">...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>두 파일의 읽기 순서와 관계는 다음과 같다.</p><pre class="mermaid">flowchart TD
    A[에이전트 세션 시작] --&gt; B[agents/dev.md 읽기&lt;br&gt;보편적 행동 원칙 내장]
    B --&gt; C[프로젝트/CLAUDE.md 읽기&lt;br&gt;프로젝트 특화 규칙 추가]
    C --&gt; D[오케스트레이터 지시 수신]
    D --&gt; E[두 파일의 규칙을 합산하여 실행]

    style B fill:#dce8ff
    style C fill:#ffe8dc
</pre><p>CLAUDE.md가 정의 파일보다 나중에 읽히므로, 프로젝트 특화 규칙이 보편 원칙을 덮어쓸 수 있다. 충돌이 발생하면 CLAUDE.md 규칙이 우선한다.</p><div class="hint-container warning"><p class="hint-container-title">정의 파일과 CLAUDE.md 충돌 방지</p><p><code>agents/dev.md</code>에 &quot;TypeScript를 사용한다&quot;고 명시했더라도 CLAUDE.md에 &quot;이 프로젝트는 JavaScript&quot;라고 적혀 있으면 JavaScript가 우선된다. 의도하지 않은 덮어쓰기를 막으려면 두 파일의 범위를 명확히 분리해야 한다.</p></div><hr><h2 id="_6-sessionstart-훅으로-자동-로드" tabindex="-1"><a class="header-anchor" href="#_6-sessionstart-훅으로-자동-로드"><span>6. SessionStart 훅으로 자동 로드</span></a></h2><p>에이전트가 시작될 때 정의 파일을 자동으로 읽히도록 SessionStart 훅을 설정한다.</p><div class="language-typescript line-numbers-mode" data-highlighter="prismjs" data-ext="ts" data-title="ts"><pre><code><span class="line"><span class="token comment">// hooks/session-start-loader.ts</span></span>
<span class="line"><span class="token keyword">import</span> fs <span class="token keyword">from</span> <span class="token string">&#39;fs&#39;</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token keyword">import</span> path <span class="token keyword">from</span> <span class="token string">&#39;path&#39;</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">const</span> agentName <span class="token operator">=</span> process<span class="token punctuation">.</span>env<span class="token punctuation">.</span><span class="token constant">AGENT_NAME</span> <span class="token operator">??</span> <span class="token string">&#39;dev&#39;</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token keyword">const</span> definitionPath <span class="token operator">=</span> path<span class="token punctuation">.</span><span class="token function">join</span><span class="token punctuation">(</span></span>
<span class="line">  process<span class="token punctuation">.</span>env<span class="token punctuation">.</span><span class="token constant">CLAUDE_PLUGIN_ROOT</span><span class="token operator">!</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token string">&#39;agents&#39;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token template-string"><span class="token template-punctuation string">\`</span><span class="token interpolation"><span class="token interpolation-punctuation punctuation">\${</span>agentName<span class="token interpolation-punctuation punctuation">}</span></span><span class="token string">.md</span><span class="token template-punctuation string">\`</span></span></span>
<span class="line"><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">if</span> <span class="token punctuation">(</span>fs<span class="token punctuation">.</span><span class="token function">existsSync</span><span class="token punctuation">(</span>definitionPath<span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token keyword">const</span> content <span class="token operator">=</span> fs<span class="token punctuation">.</span><span class="token function">readFileSync</span><span class="token punctuation">(</span>definitionPath<span class="token punctuation">,</span> <span class="token string">&#39;utf-8&#39;</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">  <span class="token comment">// 정의 파일 내용을 시스템 메시지로 주입</span></span>
<span class="line">  <span class="token builtin">console</span><span class="token punctuation">.</span><span class="token function">log</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span><span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">continue</span><span class="token operator">:</span> <span class="token boolean">true</span><span class="token punctuation">,</span></span>
<span class="line">    systemPromptAppend<span class="token operator">:</span> content<span class="token punctuation">,</span></span>
<span class="line">  <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span> <span class="token keyword">else</span> <span class="token punctuation">{</span></span>
<span class="line">  <span class="token builtin">console</span><span class="token punctuation">.</span><span class="token function">log</span><span class="token punctuation">(</span><span class="token constant">JSON</span><span class="token punctuation">.</span><span class="token function">stringify</span><span class="token punctuation">(</span><span class="token punctuation">{</span> <span class="token keyword">continue</span><span class="token operator">:</span> <span class="token boolean">true</span> <span class="token punctuation">}</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>hooks.json</code>에 SessionStart 훅을 등록한다.</p><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span></span>
<span class="line">  <span class="token property">&quot;hooks&quot;</span><span class="token operator">:</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token property">&quot;SessionStart&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">      <span class="token punctuation">{</span></span>
<span class="line">        <span class="token property">&quot;hooks&quot;</span><span class="token operator">:</span> <span class="token punctuation">[</span></span>
<span class="line">          <span class="token punctuation">{</span></span>
<span class="line">            <span class="token property">&quot;type&quot;</span><span class="token operator">:</span> <span class="token string">&quot;command&quot;</span><span class="token punctuation">,</span></span>
<span class="line">            <span class="token property">&quot;command&quot;</span><span class="token operator">:</span> <span class="token string">&quot;npx ts-node hooks/session-start-loader.ts&quot;</span><span class="token punctuation">,</span></span>
<span class="line">            <span class="token property">&quot;timeout&quot;</span><span class="token operator">:</span> <span class="token number">5</span></span>
<span class="line">          <span class="token punctuation">}</span></span>
<span class="line">        <span class="token punctuation">]</span></span>
<span class="line">      <span class="token punctuation">}</span></span>
<span class="line">    <span class="token punctuation">]</span></span>
<span class="line">  <span class="token punctuation">}</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>AGENT_NAME</code> 환경 변수는 오케스트레이터가 <code>TeamCreate</code> 시 <code>env</code> 옵션으로 주입한다. 이 값을 기반으로 적절한 정의 파일을 로드한다.</p><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>정의 파일은 에이전트의 헌법이다. 역할, 원칙, 금지사항을 담아 에이전트가 일관된 기준으로 판단하게 만든다.</li><li>&quot;항상 일하고, 항상 생각하고, 두 번 생각하도록&quot; 세 원칙은 모든 역할 파일에 공통으로 포함된다.</li><li><code>disallowedTools</code>는 역할 경계를 하드웨어 수준에서 강제한다.</li><li>에이전트 정의 파일(보편 원칙)과 CLAUDE.md(프로젝트 특화)는 서로 다른 범위를 담당하며, 충돌 시 CLAUDE.md가 우선한다.</li><li>SessionStart 훅으로 정의 파일을 자동 로드하면 오케스트레이터가 매번 프롬프트에 원칙을 반복하지 않아도 된다.</li></ul><p>다음 챕터: <a href="/study/ai-agent-workflow/06-documentation">CH6. 문서화 체계</a></p></div>`,45)]))}const o=s(l,[["render",p],["__file","05-agent-definition-files.html.vue"]]),u=JSON.parse('{"path":"/study/ai-agent-workflow/05-agent-definition-files.html","title":"CH5. 에이전트 정의 파일 작성법","lang":"en-US","frontmatter":{"title":"CH5. 에이전트 정의 파일 작성법","description":"에이전트가 자신의 역할을 알게 하는 정의 파일을 작성한다. 항상 일하고, 항상 생각하고, 두 번 생각하도록 원칙을 내장한다","date":"2026-04-16T00:00:00.000Z","tags":["AI","Agent","CLAUDE.md","정의파일"]},"headers":[{"level":1,"title":"에이전트 정의 파일 작성법","slug":"에이전트-정의-파일-작성법","link":"#에이전트-정의-파일-작성법","children":[{"level":2,"title":"1. 왜 정의 파일이 필요한가","slug":"_1-왜-정의-파일이-필요한가","link":"#_1-왜-정의-파일이-필요한가","children":[]},{"level":2,"title":"2. 정의 파일 형식","slug":"_2-정의-파일-형식","link":"#_2-정의-파일-형식","children":[]},{"level":2,"title":"3. \\"항상 일하고, 항상 생각하고, 두 번 생각하도록\\" 내장","slug":"_3-항상-일하고-항상-생각하고-두-번-생각하도록-내장","link":"#_3-항상-일하고-항상-생각하고-두-번-생각하도록-내장","children":[]},{"level":2,"title":"4. 역할별 정의 파일 예시","slug":"_4-역할별-정의-파일-예시","link":"#_4-역할별-정의-파일-예시","children":[]},{"level":2,"title":"5. 프로젝트 특화 CLAUDE.md","slug":"_5-프로젝트-특화-claude-md","link":"#_5-프로젝트-특화-claude-md","children":[]},{"level":2,"title":"6. SessionStart 훅으로 자동 로드","slug":"_6-sessionstart-훅으로-자동-로드","link":"#_6-sessionstart-훅으로-자동-로드","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/05-agent-definition-files.md"}');export{o as comp,u as data};
