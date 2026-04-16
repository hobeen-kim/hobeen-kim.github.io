import{_ as s,c as a,e,o as i}from"./app-DFC1WEy-.js";const l={};function t(r,n){return i(),a("div",null,n[0]||(n[0]=[e(`<h1 id="ch7-에이전트-헌법-—-전체-원칙-체크리스트" tabindex="-1"><a class="header-anchor" href="#ch7-에이전트-헌법-—-전체-원칙-체크리스트"><span>CH7. 에이전트 헌법 — 전체 원칙 체크리스트</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>헌법 문서의 역할과 구조를 이해한다.</li><li>작업 전/중/후 체크리스트를 상황에 맞게 적용할 수 있다.</li><li>에이전트가 헌법을 실제로 어떻게 사용하는지 설명할 수 있다.</li></ul></div><h2 id="_1-헌법-문서란" tabindex="-1"><a class="header-anchor" href="#_1-헌법-문서란"><span>1. 헌법 문서란</span></a></h2><p>에이전트는 복잡한 작업을 수행하다 보면 판단이 흔들리는 순간을 맞는다. 범위를 확장하고 싶어질 때, 완료 기준이 애매할 때, 역할 경계가 불분명할 때. 헌법 문서는 그 순간 돌아오는 기준이다.</p><p>헌법은 CLAUDE.md에 포함하거나 별도 CONSTITUTION.md로 관리한다. 에이전트 정의 파일(agents/*.md)보다 상위에 위치하며 모든 에이전트에 공통으로 적용된다. 특정 역할의 행동 지침이 헌법과 충돌하면 헌법이 우선한다.</p><pre class="mermaid">flowchart TD
    C[CONSTITUTION.md&lt;br&gt;모든 에이전트에 공통 적용]
    C --&gt; O[agents/orchestrator.md]
    C --&gt; E[agents/executor.md]
    C --&gt; V[agents/verifier.md]
    C --&gt; S[agents/specialist.md]

    O --&gt;|판단 흔들릴 때| C
    E --&gt;|판단 흔들릴 때| C
    V --&gt;|판단 흔들릴 때| C
</pre><h2 id="_2-자율-실행-루프" tabindex="-1"><a class="header-anchor" href="#_2-자율-실행-루프"><span>2. 자율 실행 루프</span></a></h2><p>에이전트 시스템은 사용자 개입 없이 작동해야 한다. 사용자는 목표를 정의하고 실행을 시작시킨 뒤, 에이전트가 스스로 PDCA 루프를 돌리면서 완료까지 이른다. 이를 위해서는 두 가지가 필요하다. <strong>명확한 목표 문서(goal.md)</strong> 와 <strong>스스로 완료를 판단하는 기준</strong> 이다.</p><h3 id="자율-실행의-전제-조건" tabindex="-1"><a class="header-anchor" href="#자율-실행의-전제-조건"><span>자율 실행의 전제 조건</span></a></h3><p>에이전트가 사람 없이 일하려면 다음 세 가지가 반드시 있어야 한다.</p><table><thead><tr><th>전제 조건</th><th>없을 때 결과</th></tr></thead><tbody><tr><td>goal.md — 목표 + 완료 기준</td><td>에이전트가 각자 다른 목표로 작업하거나 완료를 선언할 수 없음</td></tr><tr><td>에스컬레이션 프로토콜</td><td>막혔을 때 무한 루프 또는 임의 결정</td></tr><tr><td>Verifier의 합격 판정</td><td>Executor가 스스로 완료를 선언해 검증이 생략됨</td></tr></tbody></table><h3 id="자율-실행-루프-구조" tabindex="-1"><a class="header-anchor" href="#자율-실행-루프-구조"><span>자율 실행 루프 구조</span></a></h3><pre class="mermaid">flowchart TD
    START[사용자: 목표 + 시작 지시] --&gt; GOAL[Orchestrator: goal.md 생성]
    GOAL --&gt; PLAN[plans/ 작성]
    PLAN --&gt; EXEC_START[Executor: goal.md + plans/ 읽기]

    EXEC_START --&gt; WORK[구현]
    WORK --&gt; ALIGN{goal과 정렬?}
    ALIGN -- 아니오 --&gt; ESCALATE[에스컬레이션 프로토콜]
    ESCALATE --&gt; ALIGN
    ALIGN -- 예 --&gt; IMPL[implementations/ + 증거 작성]

    IMPL --&gt; VERIFY[Verifier: success_criteria 검증]
    VERIFY -- 미달 --&gt; FEEDBACK[재작업 요청]
    FEEDBACK --&gt; EXEC_START
    VERIFY -- 통과 --&gt; DONE[goal.md status: done]

    DONE --&gt; ACT[Act 루프&lt;br&gt;wisdom/ + skill + 정의 파일 강화]
    ACT --&gt; REPORT[Orchestrator: 사용자에게 결과 보고]
</pre><h3 id="goal-md가-자율성을-가능하게-하는-이유" tabindex="-1"><a class="header-anchor" href="#goal-md가-자율성을-가능하게-하는-이유"><span>goal.md가 자율성을 가능하게 하는 이유</span></a></h3><pre class="mermaid">sequenceDiagram
    participant O as Orchestrator
    participant E as Executor
    participant V as Verifier
    participant G as goal.md

    O-&gt;&gt;G: objective + success_criteria + non_goals 기록
    O-&gt;&gt;E: 작업 시작 (goal.md 경로 전달)

    loop 구현 반복
        E-&gt;&gt;G: 작업 전 읽기 (non_goals 벗어났는가?)
        E-&gt;&gt;E: 구현
        E-&gt;&gt;G: 막혔을 때 읽기 (constraints 확인)
    end

    E-&gt;&gt;V: 검증 요청
    V-&gt;&gt;G: success_criteria 읽기
    V-&gt;&gt;V: 기준 충족 여부 판정

    alt 통과
        V-&gt;&gt;G: status: done
        V-&gt;&gt;O: 완료 선언
    else 미달
        V-&gt;&gt;E: 재작업 요청
    end
</pre><p>사용자가 개입하지 않아도 루프가 돌아간다. goal.md의 <code>status: done</code>이 루프 종료 신호이고, <code>success_criteria</code>가 합격 기준이며, <code>non_goals</code>가 범위 이탈 방지 장치다.</p><h3 id="자율-실행-중-자기-점검-주기" tabindex="-1"><a class="header-anchor" href="#자율-실행-중-자기-점검-주기"><span>자율 실행 중 자기 점검 주기</span></a></h3><p>에이전트가 자율 작업하는 동안 스스로 점검해야 하는 시점이 있다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 구현 시작 전: goal.md의 objective와 내 작업이 정렬되는가?</span>
<span class="line">□ 주요 파일 변경 전: non_goals에 포함된 영역인가?</span>
<span class="line">□ 막혔을 때: constraints에 의해 막힌 것인가, 아니면 기술적 문제인가?</span>
<span class="line">□ 구현 완료 후: success_criteria를 각각 충족하는가?</span>
<span class="line">□ Verifier 요청 전: implementations/에 증거가 있는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이 점검을 생략하면 Verifier 단계에서 반려되어 재작업이 발생한다. 자율 실행에서 재작업은 사람의 개입 없이 처리되어야 하므로, 점검을 철저히 할수록 전체 루프가 빠르게 완료된다.</p><h2 id="_3-작업-전-체크리스트-before" tabindex="-1"><a class="header-anchor" href="#_3-작업-전-체크리스트-before"><span>3. 작업 전 체크리스트 (Before)</span></a></h2><p>작업을 시작하기 전에 다음 항목을 순서대로 확인한다. 모두 통과해야 실행 단계로 넘어간다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 이 작업의 진짜 목표가 무엇인가? (Mission over Individual)</span>
<span class="line">□ 내 DRI 범위 안의 작업인가? 범위 밖이면 누구에게 알려야 하는가?</span>
<span class="line">□ 이 접근법이 최선인가? 다른 방법은 없는가? (Question Every Assumption)</span>
<span class="line">□ 범위가 명확한가? 요청 이상으로 하려 하지 않는가? (Focus on Impact)</span>
<span class="line">□ 지금 바로 시작할 수 있는가? 막히는 부분만 따로 표시했는가? (Move with Urgency)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="hint-container warning"><p class="hint-container-title">DRI 확인 우선</p><p>범위 밖 작업을 발견했을 때 즉시 거부하거나 즉시 실행하는 것 모두 잘못이다. 올바른 행동은 Orchestrator에게 에스컬레이션하고, 가능한 범위에서 대안을 제안하는 것이다.</p></div><h2 id="_4-작업-중-체크리스트-during" tabindex="-1"><a class="header-anchor" href="#_4-작업-중-체크리스트-during"><span>4. 작업 중 체크리스트 (During)</span></a></h2><p>작업 중에도 주기적으로 현재 상태를 점검한다. 계획과 실행이 벌어지는 것을 조기에 감지하기 위해서다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 계획대로 진행되고 있는가?</span>
<span class="line">□ 예상치 못한 범위 확장이 생기지 않는가?</span>
<span class="line">□ 막히면 → 작은 실험으로 확인 (논쟁 금지)</span>
<span class="line">□ 진행 상황을 문서(implementations/)에 기록하고 있는가?</span>
<span class="line">□ 같은 실수를 반복하고 있지 않은가? (wisdom/ 확인)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>막혔을 때 논쟁에 빠지는 것은 Move with Urgency 원칙 위반이다. &quot;A가 맞는가 B가 맞는가&quot;를 토론하는 대신 작은 실험으로 먼저 검증한다.</p><h2 id="_5-막혔을-때-에스컬레이션-프로토콜" tabindex="-1"><a class="header-anchor" href="#_5-막혔을-때-에스컬레이션-프로토콜"><span>5. 막혔을 때 에스컬레이션 프로토콜</span></a></h2><p>막히는 상황은 두 가지로 나뉜다. <strong>기술적 막힘</strong> — 어떻게 구현할지 모른다. <strong>판단 막힘</strong> — 어떻게 결정해야 할지 모른다. 두 경우의 처리 방법이 다르다.</p><pre class="mermaid">flowchart TD
    A[막힘 발생] --&gt; B{막힘 유형}

    B --&gt;|판단 막힘&lt;br&gt;원칙 적용 불명확| C[CONSTITUTION.md&lt;br&gt;대원칙 문서 확인]
    C --&gt; D{원칙으로 해결?}
    D --&gt;|해결| E[원칙 기준으로 결정&lt;br&gt;decisions/ 에 기록]
    E --&gt; F[작업 재개]
    D --&gt;|여전히 불명확| G[Orchestrator에 에스컬레이션]

    B --&gt;|기술적 막힘&lt;br&gt;구현 방법 모름| H[작은 실험 먼저]
    H --&gt; I{실험으로 해결?}
    I --&gt;|해결| F
    I --&gt;|해결 안 됨| G

    G --&gt; J[Orchestrator:&lt;br&gt;원칙 기준으로 설명]
    J --&gt; K[에이전트 결정 후 작업 재개]
    K --&gt; L[결정 내용 decisions/ 기록]
</pre><h3 id="판단-막힘-원칙-문서를-먼저-연다" tabindex="-1"><a class="header-anchor" href="#판단-막힘-원칙-문서를-먼저-연다"><span>판단 막힘: 원칙 문서를 먼저 연다</span></a></h3><p>에이전트가 &quot;이 상황에서 어떻게 해야 하는가&quot;를 모를 때, 가장 먼저 할 일은 Orchestrator에게 묻는 것이 아니다. <strong>CONSTITUTION.md와 대원칙 문서를 먼저 확인하는 것이다.</strong></p><p>원칙 문서 접근 경로:</p><ul><li><code>CONSTITUTION.md</code> — 모든 에이전트 공통 규칙, 역할 경계</li><li><code>.claude/agents/principles.md</code> — 8가지 대원칙 상세</li><li><code>CLAUDE.md</code> — 프로젝트 특화 규칙</li></ul><p>대부분의 판단 막힘은 원칙 문서에서 해결된다. 예를 들어 &quot;범위를 확장해도 되는가?&quot;는 Focus on Impact 원칙에서 답이 나온다. &quot;지금 바로 실험해야 하는가, 더 분석해야 하는가?&quot;는 Move with Urgency와 Execution over Perfection에서 답이 나온다.</p><h3 id="기술적-막힘-작은-실험-먼저" tabindex="-1"><a class="header-anchor" href="#기술적-막힘-작은-실험-먼저"><span>기술적 막힘: 작은 실험 먼저</span></a></h3><p>&quot;어떻게 구현할지 모른다&quot;는 기술적 막힘은 논쟁이 아니라 실험으로 해결한다. 5분 안에 검증 가능한 가장 작은 실험을 먼저 실행한다. 실험이 실패하면 그때 Orchestrator에게 기술적 맥락과 함께 보고한다.</p><h3 id="orchestrator에-에스컬레이션" tabindex="-1"><a class="header-anchor" href="#orchestrator에-에스컬레이션"><span>Orchestrator에 에스컬레이션</span></a></h3><p>원칙 문서 확인과 작은 실험으로 해결되지 않으면 Orchestrator에게 에스컬레이션한다.</p><p>에스컬레이션 보고 형식:</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">1. 현재 상황: [어디서 막혔는가]</span>
<span class="line">2. 시도한 것: [원칙 문서 확인 결과, 실험 결과]</span>
<span class="line">3. 남은 모호함: [여전히 결정 못 한 것]</span>
<span class="line">4. 제안: [에이전트가 생각하는 옵션 A / B]</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Orchestrator는 에이전트의 보고를 받으면 <strong>원칙 문서를 기준으로</strong> 설명한다. &quot;내 생각에는&quot;이 아니라 &quot;CONSTITUTION.md 3항 / Learn Proactively 원칙에 따르면&quot;으로 답한다.</p><div class="hint-container warning"><p class="hint-container-title">에스컬레이션 남용 금지</p><p>원칙 문서 확인을 생략하고 바로 Orchestrator에게 묻는 것은 Mission over Individual 위반이다. 에이전트 스스로 해결할 수 있는 것을 Orchestrator에게 넘기면 전체 흐름이 느려진다. 원칙 문서 확인이 선행되지 않은 질문은 Orchestrator가 거부할 수 있다.</p></div><h2 id="_6-작업-후-체크리스트-after" tabindex="-1"><a class="header-anchor" href="#_6-작업-후-체크리스트-after"><span>6. 작업 후 체크리스트 (After)</span></a></h2><p>작업을 완료했다고 생각하는 시점에 이 체크리스트를 실행한다. 모두 통과해야 Verifier에게 제출한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 결과물을 직접 한 번 더 검토했는가? (Aim Higher)</span>
<span class="line">□ Verifier에게 피드백을 요청했는가? (Ask for Feedback)</span>
<span class="line">□ 1차 결과물로 완료 선언하지 않는가?</span>
<span class="line">□ implementations/에 증거를 남겼는가?</span>
<span class="line">□ 이번 작업에서 배운 것을 wisdom/에 기록했는가? (Learn Proactively)</span>
<span class="line">□ &quot;완료&quot; 선언은 Verifier가 했는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>마지막 항목이 핵심이다. 완료를 선언할 수 있는 것은 Verifier뿐이다. Executor가 &quot;완료&quot;라고 쓰는 순간 헌법 위반이다.</p><h2 id="_7-역할별-추가-체크리스트" tabindex="-1"><a class="header-anchor" href="#_7-역할별-추가-체크리스트"><span>7. 역할별 추가 체크리스트</span></a></h2><p>공통 체크리스트 외에 각 역할에만 적용되는 추가 항목이 있다.</p><h3 id="orchestrator-전용" tabindex="-1"><a class="header-anchor" href="#orchestrator-전용"><span>Orchestrator 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 적절한 에이전트에게 위임했는가? (registry 확인)</span>
<span class="line">□ DRI를 명확히 배분했는가?</span>
<span class="line">□ 직접 실행하려 하지 않는가?</span>
<span class="line">□ plan 문서가 먼저 존재하는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Orchestrator가 직접 실행에 개입하는 순간 단일 장애점이 된다. &quot;내가 직접 하는 게 빠르다&quot;는 생각이 드는 순간 이 체크리스트로 돌아온다.</p><h3 id="executor-전용" tabindex="-1"><a class="header-anchor" href="#executor-전용"><span>Executor 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 구현 방식 결정은 내 DRI 범위인가?</span>
<span class="line">□ 제품 방향 결정을 내가 하려 하지 않는가?</span>
<span class="line">□ 코드 외 파일을 건드리지 않는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Executor의 DRI는 &quot;어떻게 구현하는가&quot;다. &quot;무엇을 만들어야 하는가&quot;는 Orchestrator의 영역이다. 이 경계를 넘으면 DRI 침범이다.</p><h3 id="verifier-전용" tabindex="-1"><a class="header-anchor" href="#verifier-전용"><span>Verifier 전용</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">□ 완료 기준이 plan 문서에 명시된 것과 일치하는가?</span>
<span class="line">□ 구현 방법이 아니라 결과를 검증하는가?</span>
<span class="line">□ 증거를 확인했는가?</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Verifier는 &quot;어떻게 만들었는가&quot;를 판단하는 역할이 아니다. plan에 명시된 완료 기준을 결과물이 충족하는지를 검증한다.</p><h2 id="_8-헌법-위반-시-처리" tabindex="-1"><a class="header-anchor" href="#_8-헌법-위반-시-처리"><span>8. 헌법 위반 시 처리</span></a></h2><p>위반은 발생한다. 중요한 것은 위반 감지 후 처리 방식이다.</p><p><strong>스스로 인지한 경우</strong>: 즉시 멈추고 올바른 행동으로 전환한다. 이미 수행한 위반 행동은 취소하거나 보고한다.</p><p><strong>Verifier가 감지한 경우</strong>: 해당 에이전트에게 피드백을 반환하고 재작업을 요청한다. 피드백은 구체적인 항목(어떤 헌법 조항을 어겼는가)을 포함한다.</p><p><strong>반복 위반이 발생한 경우</strong>: 패턴을 wisdom/에 기록하고, 해당 에이전트의 정의 파일(agents/*.md) 업데이트를 검토한다.</p><pre class="mermaid">flowchart TD
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
</pre><h2 id="_9-실제-constitution-md-템플릿" tabindex="-1"><a class="header-anchor" href="#_9-실제-constitution-md-템플릿"><span>9. 실제 CONSTITUTION.md 템플릿</span></a></h2><details class="hint-container details"><summary>전체 템플릿 보기</summary><div class="language-markdown line-numbers-mode" data-highlighter="prismjs" data-ext="md" data-title="md"><pre><code><span class="line"><span class="token title important"><span class="token punctuation">#</span> CONSTITUTION.md — 에이전트 헌법</span></span>
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
<span class="line"><span class="token list punctuation">-</span> [ ] 판단 막힘 → CONSTITUTION.md 먼저 확인</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 막히면 논쟁 대신 실험</span>
<span class="line"><span class="token list punctuation">-</span> [ ] 실험 + 원칙으로 해결 안 되면 Orchestrator에 에스컬레이션</span>
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
<span class="line"><span class="token list punctuation">-</span> goal.md 없이 작업 시작은 없다.</span>
<span class="line"><span class="token list punctuation">-</span> Verifier의 <span class="token code-snippet code keyword">\`approved\`</span> 없이 완료는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> plans 없이 실행은 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 증거 없이 implementations는 없다.</span>
<span class="line"><span class="token list punctuation">-</span> 결정 당일 decisions를 작성한다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>자율 실행의 전제: goal.md(목표+완료기준) + 에스컬레이션 프로토콜 + Verifier 합격 판정. 이 세 가지가 없으면 사람이 개입해야 한다.</li><li>헌법 문서는 판단이 흔들릴 때 돌아오는 기준이다. 에이전트 정의 파일보다 상위다.</li><li>Before / During / After 체크리스트는 순서대로 실행한다. 건너뛰는 항목이 있으면 위반이다.</li><li>막혔을 때 순서: 원칙 문서 확인 → 작은 실험 → Orchestrator 에스컬레이션. 이 순서를 지키지 않으면 Mission over Individual 위반이다.</li><li>완료를 선언할 수 있는 것은 Verifier뿐이다.</li><li>위반이 반복되면 wisdom/에 기록하고 정의 파일을 업데이트한다.</li></ul><p>다음 챕터: <a href="/study/ai-agent-workflow/08-scaffold">CH8. Scaffold</a></p></div>`,68)]))}const c=s(l,[["render",t],["__file","07-constitution.html.vue"]]),d=JSON.parse('{"path":"/study/ai-agent-workflow/07-constitution.html","title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","lang":"en-US","frontmatter":{"title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","description":"에이전트가 작업 전·중·후에 확인하는 헌법 문서. 이 문서 하나로 모든 원칙을 지킬 수 있다","date":"2026-04-16T00:00:00.000Z","tags":["Constitution","원칙","체크리스트","ClaudeCode"]},"headers":[{"level":1,"title":"CH7. 에이전트 헌법 — 전체 원칙 체크리스트","slug":"ch7-에이전트-헌법-—-전체-원칙-체크리스트","link":"#ch7-에이전트-헌법-—-전체-원칙-체크리스트","children":[{"level":2,"title":"1. 헌법 문서란","slug":"_1-헌법-문서란","link":"#_1-헌법-문서란","children":[]},{"level":2,"title":"2. 자율 실행 루프","slug":"_2-자율-실행-루프","link":"#_2-자율-실행-루프","children":[{"level":3,"title":"자율 실행의 전제 조건","slug":"자율-실행의-전제-조건","link":"#자율-실행의-전제-조건","children":[]},{"level":3,"title":"자율 실행 루프 구조","slug":"자율-실행-루프-구조","link":"#자율-실행-루프-구조","children":[]},{"level":3,"title":"goal.md가 자율성을 가능하게 하는 이유","slug":"goal-md가-자율성을-가능하게-하는-이유","link":"#goal-md가-자율성을-가능하게-하는-이유","children":[]},{"level":3,"title":"자율 실행 중 자기 점검 주기","slug":"자율-실행-중-자기-점검-주기","link":"#자율-실행-중-자기-점검-주기","children":[]}]},{"level":2,"title":"3. 작업 전 체크리스트 (Before)","slug":"_3-작업-전-체크리스트-before","link":"#_3-작업-전-체크리스트-before","children":[]},{"level":2,"title":"4. 작업 중 체크리스트 (During)","slug":"_4-작업-중-체크리스트-during","link":"#_4-작업-중-체크리스트-during","children":[]},{"level":2,"title":"5. 막혔을 때 에스컬레이션 프로토콜","slug":"_5-막혔을-때-에스컬레이션-프로토콜","link":"#_5-막혔을-때-에스컬레이션-프로토콜","children":[{"level":3,"title":"판단 막힘: 원칙 문서를 먼저 연다","slug":"판단-막힘-원칙-문서를-먼저-연다","link":"#판단-막힘-원칙-문서를-먼저-연다","children":[]},{"level":3,"title":"기술적 막힘: 작은 실험 먼저","slug":"기술적-막힘-작은-실험-먼저","link":"#기술적-막힘-작은-실험-먼저","children":[]},{"level":3,"title":"Orchestrator에 에스컬레이션","slug":"orchestrator에-에스컬레이션","link":"#orchestrator에-에스컬레이션","children":[]}]},{"level":2,"title":"6. 작업 후 체크리스트 (After)","slug":"_6-작업-후-체크리스트-after","link":"#_6-작업-후-체크리스트-after","children":[]},{"level":2,"title":"7. 역할별 추가 체크리스트","slug":"_7-역할별-추가-체크리스트","link":"#_7-역할별-추가-체크리스트","children":[{"level":3,"title":"Orchestrator 전용","slug":"orchestrator-전용","link":"#orchestrator-전용","children":[]},{"level":3,"title":"Executor 전용","slug":"executor-전용","link":"#executor-전용","children":[]},{"level":3,"title":"Verifier 전용","slug":"verifier-전용","link":"#verifier-전용","children":[]}]},{"level":2,"title":"8. 헌법 위반 시 처리","slug":"_8-헌법-위반-시-처리","link":"#_8-헌법-위반-시-처리","children":[]},{"level":2,"title":"9. 실제 CONSTITUTION.md 템플릿","slug":"_9-실제-constitution-md-템플릿","link":"#_9-실제-constitution-md-템플릿","children":[]}]}],"git":{},"filePathRelative":"_study/ai-agent-workflow/07-constitution.md"}');export{c as comp,d as data};
