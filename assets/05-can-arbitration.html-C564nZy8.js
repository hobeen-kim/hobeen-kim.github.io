import{_ as d,c as o,a as i,d as n,e as p,b as e,r as l,o as c,f as a}from"./app-BACRdUU3.js";const u={},g={class:"table-of-contents"};function v(h,t){const r=l("Header"),s=l("router-link");return c(),o("div",null,[i(r),n("nav",g,[n("ul",null,[n("li",null,[i(s,{to:"#can-중재와-우선순위"},{default:e(()=>t[0]||(t[0]=[a("CAN 중재와 우선순위")])),_:1}),n("ul",null,[n("li",null,[i(s,{to:"#_1-버스-중재-arbitration-란"},{default:e(()=>t[1]||(t[1]=[a("1. 버스 중재(Arbitration)란")])),_:1}),n("ul",null,[n("li",null,[i(s,{to:"#노드-id-가-아니라-메시지-id"},{default:e(()=>t[2]||(t[2]=[a('"노드 ID"가 아니라 "메시지 ID"')])),_:1})])])]),n("li",null,[i(s,{to:"#_2-비트-단위-중재-과정"},{default:e(()=>t[3]||(t[3]=[a("2. 비트 단위 중재 과정")])),_:1})]),n("li",null,[i(s,{to:"#_3-id-값과-우선순위-관계"},{default:e(()=>t[4]||(t[4]=[a("3. ID 값과 우선순위 관계")])),_:1}),n("ul",null,[n("li",null,[i(s,{to:"#priority가-같으면-어떻게-되는가"},{default:e(()=>t[5]||(t[5]=[a("Priority가 같으면 어떻게 되는가")])),_:1})])])]),n("li",null,[i(s,{to:"#_4-메시지-설계-시-고려사항"},{default:e(()=>t[6]||(t[6]=[a("4. 메시지 설계 시 고려사항")])),_:1})]),n("li",null,[i(s,{to:"#다음-챕터"},{default:e(()=>t[7]||(t[7]=[a("다음 챕터")])),_:1})])])])])]),t[8]||(t[8]=p(`<h1 id="can-중재와-우선순위" tabindex="-1"><a class="header-anchor" href="#can-중재와-우선순위"><span>CAN 중재와 우선순위</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN 버스의 중재(Arbitration) 개념과 필요성을 설명할 수 있다</li><li>CSMA/CD+AMP 메커니즘의 동작 방식을 이해한다</li><li>비트 단위 중재 과정을 단계별로 추적할 수 있다</li><li>ID 값과 우선순위의 관계를 설명할 수 있다</li><li>안전 관련 메시지 설계 시 ID 배정 원칙을 적용할 수 있다</li></ul></div><hr><h2 id="_1-버스-중재-arbitration-란" tabindex="-1"><a class="header-anchor" href="#_1-버스-중재-arbitration-란"><span>1. 버스 중재(Arbitration)란</span></a></h2><p><strong>문제 상황<strong>: 여러 노드가 하나의 버스를 공유하는 CAN에서, 두 노드가 </strong>동시에 메시지를 전송하기 시작하면</strong> 어떻게 될까?</p><p>이더넷의 경우 충돌(Collision)이 발생하면 두 노드 모두 전송을 멈추고 임의의 시간 뒤 재전송한다. 이 방식은 충돌 후 데이터가 손실된다.</p><p><strong>CAN의 해답</strong>: CAN은 <strong>CSMA/CD+AMP</strong> 방식을 사용해 충돌 없이 우선순위가 높은 메시지가 이기도록 한다.</p><table><thead><tr><th>용어</th><th>의미</th></tr></thead><tbody><tr><td><strong>CSMA</strong> (Carrier Sense Multiple Access)</td><td>전송 전 버스가 사용 중인지 확인한다</td></tr><tr><td><strong>CD</strong> (Collision Detection)</td><td>전송 중 충돌(다른 신호)을 감지한다</td></tr><tr><td><strong>AMP</strong> (Arbitration on Message Priority)</td><td>메시지 우선순위에 따라 중재한다</td></tr></tbody></table><p><strong>핵심 차이<strong>: 이더넷은 충돌 후 </strong>모두 재전송<strong>하지만, CAN은 중재 패배 노드만 재전송한다. 승리한 노드는 전송을 </strong>중단 없이 계속</strong>한다.</p><div class="hint-container info"><p class="hint-container-title">Info</p><p>중재는 ID 필드 전송 구간에서만 일어난다. 중재에서 이긴 노드의 메시지는 데이터 손실 없이 그대로 버스에 전달된다.</p></div><h3 id="노드-id-가-아니라-메시지-id" tabindex="-1"><a class="header-anchor" href="#노드-id-가-아니라-메시지-id"><span>&quot;노드 ID&quot;가 아니라 &quot;메시지 ID&quot;</span></a></h3><p>한 가지 주의할 점이 있다. CAN에서 ID는 <strong>노드(장치)를 식별하는 것이 아니라 메시지의 종류를 식별한다.</strong> 하나의 ECU가 여러 종류의 메시지를 보낼 수 있으며, 각각 다른 ID를 가진다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">엔진 ECU (하나의 노드)가 보내는 메시지들:</span>
<span class="line">  ID=0x100: 엔진 RPM 정보</span>
<span class="line">  ID=0x101: 엔진 온도 정보</span>
<span class="line">  ID=0x102: 엔진 토크 정보</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>따라서 중재에서 비교되는 것은 노드의 고유번호가 아니라, <strong>그 순간 전송하려는 메시지의 ID</strong>다. 같은 노드라도 어떤 메시지를 보내느냐에 따라 우선순위가 달라진다.</p><hr><h2 id="_2-비트-단위-중재-과정" tabindex="-1"><a class="header-anchor" href="#_2-비트-단위-중재-과정"><span>2. 비트 단위 중재 과정</span></a></h2><p>중재는 ID를 다 보낸 뒤에 비교하는 것이 아니다. 각 노드가 ID를 MSB(최상위 비트)부터 <strong>한 비트씩 버스에 보내면서, 동시에 버스를 읽어 실시간으로 비교</strong>한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">시간 →</span>
<span class="line">노드A: [SOF][비트10][비트9][비트8]...[비트0] → 승리 시 [DLC][Data]... 계속</span>
<span class="line">노드B: [SOF][비트10][비트9][비트8] ← 여기서 탈락하면 즉시 중단</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>ID 구간이 끝나면 중재도 끝나고, 승자만 나머지(DLC, Data, CRC 등)를 전송한다. 구체적인 예시를 보자. 노드A(ID=0x100)와 노드B(ID=0x200)가 동시에 전송을 시작하는 상황이다.</p><p><strong>ID 이진수 변환</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">노드A ID = 0x100 = 0001 0000 0000 (11bit)</span>
<span class="line">노드B ID = 0x200 = 0010 0000 0000 (11bit)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>비트별 중재 과정</strong></p><table><thead><tr><th>비트 위치</th><th>노드A</th><th>노드B</th><th>버스 상태</th><th>결과</th></tr></thead><tbody><tr><td>비트 10 (MSB)</td><td>0 (Dominant)</td><td>0 (Dominant)</td><td>Dominant</td><td>동점, 계속</td></tr><tr><td>비트 9</td><td>0 (Dominant)</td><td>0 (Dominant)</td><td>Dominant</td><td>동점, 계속</td></tr><tr><td>비트 8</td><td>0 (Dominant)</td><td>1 (Recessive)</td><td><strong>Dominant</strong></td><td><strong>노드B 탈락</strong></td></tr></tbody></table><p>비트 8에서 노드A는 0(Dominant)을, 노드B는 1(Recessive)을 전송한다. 버스는 Dominant 값인 0이 된다. 노드B는 자신이 1을 보냈는데 버스가 0이 된 것을 감지하고, <strong>즉시 전송을 중단</strong>한다. 노드A는 아무것도 모른 채 전송을 계속한다.</p><pre class="mermaid">sequenceDiagram
    participant A as 노드A (ID=0x100)
    participant Bus as CAN 버스
    participant B as 노드B (ID=0x200)

    Note over A,B: 두 노드가 동시에 SOF 전송 시작
    A-&gt;&gt;Bus: 비트10=0 (Dominant)
    B-&gt;&gt;Bus: 비트10=0 (Dominant)
    Note over Bus: 버스=0 (Dominant)
    Bus--&gt;&gt;A: 버스 읽기: 0 ✓ 일치
    Bus--&gt;&gt;B: 버스 읽기: 0 ✓ 일치

    A-&gt;&gt;Bus: 비트9=0 (Dominant)
    B-&gt;&gt;Bus: 비트9=0 (Dominant)
    Note over Bus: 버스=0 (Dominant)
    Bus--&gt;&gt;A: 버스 읽기: 0 ✓ 일치
    Bus--&gt;&gt;B: 버스 읽기: 0 ✓ 일치

    A-&gt;&gt;Bus: 비트8=0 (Dominant)
    B-&gt;&gt;Bus: 비트8=1 (Recessive)
    Note over Bus: 버스=0 (Dominant, A가 이김)
    Bus--&gt;&gt;A: 버스 읽기: 0 ✓ 일치 → 전송 계속
    Bus--&gt;&gt;B: 버스 읽기: 0 ✗ 불일치 → 즉시 중단

    Note over A: 중단 없이 나머지 프레임 전송
    Note over B: 전송 중단, 버스가 빌 때까지 대기
    A-&gt;&gt;Bus: 데이터 프레임 나머지 전송 완료
    Note over B: 버스 유휴 상태 감지 후 재전송 시도
</pre><hr><h2 id="_3-id-값과-우선순위-관계" tabindex="-1"><a class="header-anchor" href="#_3-id-값과-우선순위-관계"><span>3. ID 값과 우선순위 관계</span></a></h2><p><strong>원칙: ID 숫자가 작을수록 우선순위가 높다.</strong></p><p>이유는 간단하다. CAN 버스에서 <strong>0(Dominant)이 1(Recessive)을 이긴다</strong>. ID의 상위 비트부터 비교할 때, 먼저 0을 보내는 노드가 버스를 차지한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">ID = 0x001: 0000 0000 001  ← 앞쪽이 0으로 가득 참 → 버스 독점 유리</span>
<span class="line">ID = 0x7FF: 1111 1111 111  ← 앞쪽이 1로 가득 참 → 버스 독점 불리</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><pre class="mermaid">flowchart LR
    subgraph 높은 우선순위
        A[&quot;ID = 0x000&lt;br&gt;최고 우선순위&quot;]
        B[&quot;ID = 0x001&quot;]
        C[&quot;ID = 0x100&quot;]
    end
    subgraph 낮은 우선순위
        D[&quot;ID = 0x600&quot;]
        E[&quot;ID = 0x700&quot;]
        F[&quot;ID = 0x7FF&lt;br&gt;최저 우선순위&quot;]
    end
    A --&gt; B --&gt; C --&gt; D --&gt; E --&gt; F
    style A fill:#ff6b6b,color:#fff
    style F fill:#74c0fc,color:#000
</pre><p><strong>29bit Extended ID에서의 우선순위</strong></p><p>ISOBUS는 29bit Extended ID를 사용하며, ID의 상위 3비트가 Priority 필드다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">29bit ID 구조:</span>
<span class="line">[P P P][R][DP][PF 8bit][PS 8bit][SA 8bit]</span>
<span class="line">  ↑</span>
<span class="line">Priority (0~7, 낮을수록 높은 우선순위)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>Priority 0이 가장 높고, Priority 7이 가장 낮다. 이를 통해 메시지 종류별 우선순위를 명시적으로 설정할 수 있다.</p><h3 id="priority가-같으면-어떻게-되는가" tabindex="-1"><a class="header-anchor" href="#priority가-같으면-어떻게-되는가"><span>Priority가 같으면 어떻게 되는가</span></a></h3><p>Priority 필드는 29비트 ID의 최상위 3비트일 뿐이다. Priority가 같으면 중재가 끝나는 것이 아니라, <strong>나머지 비트(EDP → DP → PF → PS → SA)로 계속 비교</strong>한다. 결국 29비트 ID 전체가 하나의 우선순위 값이다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">메시지A: Priority=3, PF=0xF0, PS=0x04, SA=0x00</span>
<span class="line">  → ID = 0x0CF00400</span>
<span class="line"></span>
<span class="line">메시지B: Priority=3, PF=0xFE, PS=0xEE, SA=0x00</span>
<span class="line">  → ID = 0x0CFEEE00</span>
<span class="line"></span>
<span class="line">비교:</span>
<span class="line">  Priority: 011 vs 011 → 동점, 계속</span>
<span class="line">  EDP:      0   vs 0   → 동점, 계속</span>
<span class="line">  DP:       0   vs 0   → 동점, 계속</span>
<span class="line">  PF:       11110000 vs 11111110</span>
<span class="line">                    ↑ 비트 19에서 A=0, B=1 → 메시지A 승리</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><table><thead><tr><th>상황</th><th>중재 방식</th></tr></thead><tbody><tr><td>Priority가 다름</td><td>Priority가 작은 쪽이 즉시 승리</td></tr><tr><td>Priority가 같음</td><td>PF → PS → SA 순서로 계속 비교</td></tr><tr><td>29비트 전체가 같음</td><td>발생할 수 없음 (같은 PGN+SA 조합은 네트워크에 하나뿐)</td></tr></tbody></table><p>이 원칙을 이해하면, 실제 시스템에서 메시지 ID를 어떻게 배정해야 하는지가 자연스럽게 도출된다.</p><hr><h2 id="_4-메시지-설계-시-고려사항" tabindex="-1"><a class="header-anchor" href="#_4-메시지-설계-시-고려사항"><span>4. 메시지 설계 시 고려사항</span></a></h2><p>중재 메커니즘을 이해하면 <strong>ID 배정 전략</strong>이 명확해진다.</p><p><strong>안전 관련 메시지에는 낮은 ID를 배정</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Priority 0 (ID 앞자리 000): 브레이크, 조향, 비상 정지</span>
<span class="line">Priority 1 (ID 앞자리 001): 엔진 제어, 변속기</span>
<span class="line">Priority 2 (ID 앞자리 010): 차량 속도, 자세 제어</span>
<span class="line">Priority 3 (ID 앞자리 011): 일반 제어 데이터</span>
<span class="line">Priority 6 (ID 앞자리 110): 진단, 설정</span>
<span class="line">Priority 7 (ID 앞자리 111): 정보성 메시지, 로그</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>주기적 메시지 vs 이벤트 메시지</strong></p><table><thead><tr><th>구분</th><th>특징</th><th>ID 전략</th></tr></thead><tbody><tr><td><strong>주기적 메시지</strong></td><td>일정 주기(예: 10ms, 100ms)로 반복 전송</td><td>중간 우선순위 배정. 너무 낮은 ID는 다른 중요 메시지를 방해할 수 있음</td></tr><tr><td><strong>이벤트 메시지</strong></td><td>특정 조건 발생 시에만 전송</td><td>안전 관련이면 낮은 ID, 정보성이면 높은 ID</td></tr></tbody></table><p><strong>버스 부하 고려</strong></p><p>중재에서 계속 패배하는 메시지는 버스가 바쁠수록 더 오래 기다려야 한다. 높은 우선순위 메시지가 너무 자주 전송되면, 낮은 우선순위 메시지는 <strong>기아 상태(Starvation)</strong>에 빠질 수 있다.</p><div class="hint-container tip"><p class="hint-container-title">실무 설계 원칙</p><ul><li>안전 관련 메시지: Priority 0~2</li><li>실시간성이 중요한 제어 데이터: Priority 3~4</li><li>진단, 설정, 정보: Priority 5~7</li><li>동일 Priority 내에서는 기능별로 ID 범위를 구분해 관리한다</li></ul></div><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN의 <strong>CSMA/CD+AMP</strong> 방식은 비트 단위로 중재해, 우선순위 높은 메시지가 데이터 손실 없이 전송된다.</li><li>Dominant(0)이 Recessive(1)을 이기므로, <strong>ID 값이 작을수록 우선순위가 높다</strong>.</li><li>중재 패패 노드는 즉시 전송을 중단하고 버스가 빌 때까지 대기 후 재시도한다.</li><li>ISOBUS의 29bit ID에서 상위 3비트(Priority)로 메시지 우선순위를 명시한다.</li><li>안전 관련 메시지(브레이크, 조향)에는 낮은 ID를, 정보성 메시지에는 높은 ID를 배정한다.</li></ul></div><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/06-can-error">CAN 에러 처리</a></li></ul>`,54))])}const m=d(u,[["render",v],["__file","05-can-arbitration.html.vue"]]),D=JSON.parse('{"path":"/study/isobus/05-can-arbitration.html","title":"CAN 중재와 우선순위","lang":"en-US","frontmatter":{"title":"CAN 중재와 우선순위","description":"두 노드가 동시에 전송할 때 CAN 버스가 충돌 없이 중재하는 메커니즘을 이해한다","date":"2026-04-13T00:00:00.000Z","tags":["isobus","can","arbitration"]},"headers":[{"level":1,"title":"CAN 중재와 우선순위","slug":"can-중재와-우선순위","link":"#can-중재와-우선순위","children":[{"level":2,"title":"1. 버스 중재(Arbitration)란","slug":"_1-버스-중재-arbitration-란","link":"#_1-버스-중재-arbitration-란","children":[{"level":3,"title":"\\"노드 ID\\"가 아니라 \\"메시지 ID\\"","slug":"노드-id-가-아니라-메시지-id","link":"#노드-id-가-아니라-메시지-id","children":[]}]},{"level":2,"title":"2. 비트 단위 중재 과정","slug":"_2-비트-단위-중재-과정","link":"#_2-비트-단위-중재-과정","children":[]},{"level":2,"title":"3. ID 값과 우선순위 관계","slug":"_3-id-값과-우선순위-관계","link":"#_3-id-값과-우선순위-관계","children":[{"level":3,"title":"Priority가 같으면 어떻게 되는가","slug":"priority가-같으면-어떻게-되는가","link":"#priority가-같으면-어떻게-되는가","children":[]}]},{"level":2,"title":"4. 메시지 설계 시 고려사항","slug":"_4-메시지-설계-시-고려사항","link":"#_4-메시지-설계-시-고려사항","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/05-can-arbitration.md"}');export{m as comp,D as data};
