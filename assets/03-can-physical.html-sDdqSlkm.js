import{_ as s,c as a,d as e,o as t}from"./app-BSj_EDeZ.js";const i={};function l(p,n){return t(),a("div",null,n[0]||(n[0]=[e(`<h1 id="can-물리-계층" tabindex="-1"><a class="header-anchor" href="#can-물리-계층"><span>CAN 물리 계층</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN_H와 CAN_L 차동 신호의 원리와 노이즈 내성을 설명할 수 있다.</li><li>Dominant(0)과 Recessive(1) 상태의 전압을 암기하고 Wired-AND 동작을 이해한다.</li><li>CAN 버스의 선형 토폴로지와 종단 저항의 역할을 설명할 수 있다.</li><li>통신 속도에 따른 최대 버스 길이를 이해한다.</li><li>DB9 커넥터 핀 배치를 확인할 수 있다.</li></ul></div><hr><h2 id="_1-can-h와-can-l-—-차동-신호" tabindex="-1"><a class="header-anchor" href="#_1-can-h와-can-l-—-차동-신호"><span>1. CAN_H와 CAN_L — 차동 신호</span></a></h2><p>CAN은 <strong>두 개의 선(CAN_H, CAN_L)</strong>으로 신호를 전달한다. 이 방식을 <strong>차동 신호(Differential Signal)</strong>라고 한다.</p><h3 id="왜-두-선이-필요한가" tabindex="-1"><a class="header-anchor" href="#왜-두-선이-필요한가"><span>왜 두 선이 필요한가</span></a></h3><p>한 선만 쓰면(단선 신호) 외부 노이즈가 신호에 직접 더해진다. 그런데 두 선을 쓰면 노이즈가 두 선에 <strong>같은 크기로<strong> 더해진다. 수신 측은 두 선의 </strong>전압 차이</strong>만 보기 때문에, 두 선에 동일하게 더해진 노이즈는 자동으로 상쇄된다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">노이즈 발생 시:</span>
<span class="line">  CAN_H: 3.5V + 0.3V(노이즈) = 3.8V</span>
<span class="line">  CAN_L: 1.5V + 0.3V(노이즈) = 1.8V</span>
<span class="line">  전압 차: 3.8 - 1.8 = 2.0V  ← 노이즈가 상쇄되어 원래 신호 유지</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>모터, 점화 플러그 등 노이즈가 많은 농기계 환경에서 CAN이 선택된 핵심 이유이다.</p><h3 id="전압-레벨" tabindex="-1"><a class="header-anchor" href="#전압-레벨"><span>전압 레벨</span></a></h3><table><thead><tr><th>상태</th><th>CAN_H</th><th>CAN_L</th><th>전압 차(CAN_H - CAN_L)</th></tr></thead><tbody><tr><td>Dominant (비트 0)</td><td>2.75 ~ 3.5 V</td><td>1.5 ~ 2.25 V</td><td>≥ 1.5 V (통상 2 V)</td></tr><tr><td>Recessive (비트 1)</td><td>2.5 V</td><td>2.5 V</td><td>~0 V</td></tr><tr><td>유휴(버스 비어 있음)</td><td>2.5 V</td><td>2.5 V</td><td>~0 V</td></tr></tbody></table><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">전압(V)</span>
<span class="line"> 3.5 ─ ─ ─ ┌────┐    ┌────┐   CAN_H</span>
<span class="line"> 2.5 ───────┘    └────┘    └────</span>
<span class="line">            │                    </span>
<span class="line"> 2.5 ───────┐    ┌────┐    ┌────  CAN_L</span>
<span class="line"> 1.5 ─ ─ ─ └────┘    └────┘   </span>
<span class="line"></span>
<span class="line">          [Dominant][Rec][Dominant][Rec]</span>
<span class="line">          [  bit 0 ][ 1 ][  bit 0 ][ 1 ]</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h2 id="_2-dominant-vs-recessive-—-wired-and-동작" tabindex="-1"><a class="header-anchor" href="#_2-dominant-vs-recessive-—-wired-and-동작"><span>2. Dominant vs Recessive — Wired-AND 동작</span></a></h2><h3 id="상태-정의" tabindex="-1"><a class="header-anchor" href="#상태-정의"><span>상태 정의</span></a></h3><ul><li><strong>Dominant (우세, 비트 0)</strong>: CAN_H=3.5V, CAN_L=1.5V, 전압 차 2V</li><li><strong>Recessive (열세, 비트 1)</strong>: CAN_H=CAN_L=2.5V, 전압 차 0V</li></ul><h3 id="wired-and란" tabindex="-1"><a class="header-anchor" href="#wired-and란"><span>Wired-AND란</span></a></h3><p>버스에 연결된 노드 중 <strong>단 하나라도 Dominant(0)</strong>를 보내면, 버스 전체가 Dominant가 된다. 모든 노드가 Recessive(1)를 보낼 때만 버스가 Recessive 상태가 된다.</p><p>논리식으로: <code>버스 상태 = 노드A AND 노드B AND 노드C AND ...</code><br> (0이 &quot;강한&quot; 값이므로, 하나라도 0이면 결과는 0)</p><p>이것이 중재(Arbitration) 메커니즘의 기반이다.</p><pre class="mermaid">flowchart TD
    A[&quot;노드A가 비트 전송&quot;] --&gt; C{버스 읽기}
    B[&quot;노드B가 비트 전송&quot;] --&gt; C
    C --&gt;|내가 보낸 값 = 버스 값| D[계속 전송]
    C --&gt;|내가 Recessive 보냈는데&lt;br&gt;버스는 Dominant| E[중재 패배&lt;br&gt;전송 중단 후 재시도]
</pre><h3 id="물리적으로-이해하기" tabindex="-1"><a class="header-anchor" href="#물리적으로-이해하기"><span>물리적으로 이해하기</span></a></h3><p>Dominant와 Recessive의 차이는 <strong>전류를 흘리느냐 안 흘리느냐</strong>의 차이이다.</p><table><thead><tr><th>동작</th><th>트랜시버가 하는 일</th><th>버스 상태</th></tr></thead><tbody><tr><td>Dominant(0) 보내기</td><td>전류를 흘려서 CAN_H를 3.5V, CAN_L을 1.5V로 강제 변경</td><td>Dominant</td></tr><tr><td>Recessive(1) 보내기</td><td>아무것도 안 함. 종단 저항이 자연히 2.5V로 유지</td><td>Recessive</td></tr></tbody></table><p>아무도 전류를 흘리지 않으면 버스는 자연히 Recessive(2.5V) 상태이다. 그래서 <strong>하나라도</strong> 전류를 흘리면(Dominant), 나머지가 아무것도 안 해도 버스는 Dominant가 된다. 별도의 AND 게이트 칩 없이 <strong>전선(Wire) 자체의 물리적 특성으로</strong> AND 동작이 구현되기 때문에 &quot;Wired-AND&quot;라 부른다.</p><h3 id="줄다리기-비유" tabindex="-1"><a class="header-anchor" href="#줄다리기-비유"><span>줄다리기 비유</span></a></h3><p>두 팀이 줄다리기를 한다고 생각해봅시다. 각 라운드마다 &quot;당기기(0)&quot; 또는 &quot;쉬기(1)&quot;를 선택한다.</p><ul><li>한쪽이라도 당기면 줄은 그쪽으로 감 (Dominant 승리)</li><li>둘 다 쉬어야 줄이 가운데에 유지 (Recessive)</li></ul><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">라운드 1: 팀A=당김(0), 팀B=당김(0) → 같음 → 아직 승부 안 남</span>
<span class="line">라운드 2: 팀A=당김(0), 팀B=당김(0) → 같음 → 계속</span>
<span class="line">라운드 3: 팀A=당김(0), 팀B=쉼(1)  → 팀A가 줄을 당김!</span>
<span class="line">  팀B: &quot;나는 쉬었는데 줄이 움직였네&quot; → 내가 졌다 → 포기</span>
<span class="line">  팀A: 아무 일 없었다는 듯 계속 진행</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>팀B가 포기한 뒤, 팀A 혼자서 나머지 데이터를 전부 보낸다. 팀A의 메시지는 처음부터 끝까지 손상 없이 전달된다.</p><h3 id="왜-id가-작을수록-우선순위가-높은가" tabindex="-1"><a class="header-anchor" href="#왜-id가-작을수록-우선순위가-높은가"><span>왜 ID가 작을수록 우선순위가 높은가</span></a></h3><p>ID는 MSB(최상위 비트)부터 한 비트씩 버스에 전송된다. 두 노드가 동시에 전송을 시작하면 ID를 비트 단위로 비교해 나간다.</p><p><strong>예시: ID=0x001 vs ID=0x100 (11비트)</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">비트 위치:  10  9  8  7  6  5  4  3  2  1  0</span>
<span class="line"></span>
<span class="line">ID=0x100:   0  0  1  0  0  0  0  0  0  0  0</span>
<span class="line">ID=0x001:   0  0  0  0  0  0  0  0  0  0  1</span>
<span class="line">                   ↑</span>
<span class="line">              비트 8에서 갈림</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><pre class="mermaid">sequenceDiagram
    participant A as ID=0x100
    participant Bus as CAN 버스
    participant B as ID=0x001

    Note over A,B: 비트 10: 둘 다 0 → 버스=0 → 동점
    Note over A,B: 비트 9: 둘 다 0 → 버스=0 → 동점

    A-&gt;&gt;Bus: 비트 8 = 1 (Recessive, 전류 안 흘림)
    B-&gt;&gt;Bus: 비트 8 = 0 (Dominant, 전류 흘림)
    Note over Bus: 버스 = 0 (Dominant)

    Bus--&gt;&gt;A: 버스 읽기: 0 → 내가 1을 보냈는데 0이네 → 패배!
    Bus--&gt;&gt;B: 버스 읽기: 0 → 내가 0을 보냈고 0이니 정상 → 계속 전송

    Note over A: 즉시 전송 중단, 버스 빌 때까지 대기
    Note over B: 나머지 프레임 전송 완료
</pre><p>ID가 작으면 상위 비트에 0(Dominant)이 더 많다. 0은 1을 항상 이기므로, 상대가 1을 보내는 순간 내가 덮어쓰고 승리한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">ID=0x001: 00000000001  ← 앞에 0이 10개 → 거의 무적</span>
<span class="line">ID=0x100: 00100000000  ← 비트 8에서 이미 1이 나옴 → 일찍 탈락</span>
<span class="line">ID=0x7FF: 11111111111  ← 전부 1 → 누구에게나 짐</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이것이 <strong>브레이크, 조향 같은 안전 메시지에 낮은 ID를 배정</strong>하는 이유이다. 버스가 아무리 바빠도 이 메시지가 항상 가장 먼저 전달된다.</p><p>이러한 파형이 정상적으로 나타나려면, 버스 자체가 올바른 물리적 구조로 연결되어 있어야 한다. CAN 버스의 배선 방식을 살펴봅시다.</p><hr><h2 id="_3-파형으로-보는-can-신호" tabindex="-1"><a class="header-anchor" href="#_3-파형으로-보는-can-신호"><span>3. 파형으로 보는 CAN 신호</span></a></h2><p>오실로스코프로 CAN 버스를 측정하면 CAN_H와 CAN_L이 서로 반전된 형태로 움직이는 것을 볼 수 있다.</p><p><strong>이상적인 파형:</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">CAN_H ──┐  ┌──┐  ┌──┐  ┌──</span>
<span class="line">         └──┘  └──┘  └──┘  </span>
<span class="line">CAN_L ──┐  ┌──┐  ┌──┐  ┌──  ← 반전 (CAN_H와 대칭)</span>
<span class="line">         └──┘  └──┘  └──┘  </span>
<span class="line">Diff  ──┐  ┌──┐  ┌──┐  ┌──  ← 차동 전압 (CAN_H - CAN_L)</span>
<span class="line">     0V ┘  └  ┘  └  ┘  └  </span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>실제 파형에서 보이는 현상:</strong></p><table><thead><tr><th>현상</th><th>원인</th><th>대처</th></tr></thead><tbody><tr><td>신호 끝이 뭉툭함</td><td>버스 커패시턴스(배선 길이)</td><td>배선 단축, 비트레이트 낮추기</td></tr><tr><td>링잉(파형 진동)</td><td>종단 저항 미설치 또는 불일치</td><td>양 끝 120Ω 확인</td></tr><tr><td>전압 레벨 비대칭</td><td>접지(GND) 연결 불량</td><td>GND 배선 점검</td></tr><tr><td>신호 없음</td><td>CAN_H/CAN_L 단선 또는 합선</td><td>배선 점검, 저항값 측정</td></tr></tbody></table><p>오실로스코프 없이 멀티미터로도 기본 점검이 가능한다. 버스가 유휴 상태일 때 CAN_H와 CAN_L 모두 약 2.5V이어야 한다.</p><p>이러한 파형이 정상적으로 나타나려면, 버스 자체가 올바른 물리적 구조로 연결되어 있어야 한다. CAN 버스의 배선 방식을 살펴봅시다.</p><hr><h2 id="_4-버스-토폴로지" tabindex="-1"><a class="header-anchor" href="#_4-버스-토폴로지"><span>4. 버스 토폴로지</span></a></h2><p>CAN은 <strong>선형 버스(Linear Bus)</strong> 구조를 사용한다. 하나의 주선(Backbone)에 각 노드가 짧은 분기선(Stub)으로 연결된다.</p><pre class="mermaid">graph LR
    RT1[&quot;종단저항&lt;br&gt;120Ω&quot;] --- MAIN

    subgraph MAIN[&quot;주선 (Backbone)&quot;]
        direction LR
        P1[ ] --- P2[ ] --- P3[ ] --- P4[ ] --- P5[ ]
    end

    MAIN --- RT2[&quot;종단저항&lt;br&gt;120Ω&quot;]

    P1 -- &quot;스텁&lt;br&gt;≤0.3m&quot; --&gt; N1[&quot;ECU A&lt;br&gt;엔진&quot;]
    P2 -- &quot;스텁&lt;br&gt;≤0.3m&quot; --&gt; N2[&quot;ECU B&lt;br&gt;변속기&quot;]
    P3 -- &quot;스텁&lt;br&gt;≤0.3m&quot; --&gt; N3[&quot;ECU C&lt;br&gt;계기판&quot;]
    P4 -- &quot;스텁&lt;br&gt;≤0.3m&quot; --&gt; N4[&quot;ECU D&lt;br&gt;ABS&quot;]
    P5 -- &quot;스텁&lt;br&gt;≤0.3m&quot; --&gt; N5[&quot;ECU E&lt;br&gt;작업기&quot;]

    style RT1 fill:#f9a,stroke:#c55
    style RT2 fill:#f9a,stroke:#c55
</pre><p><strong>스텁(Stub) 길이 제한:</strong></p><ul><li>스텁이 길면 신호 반사가 발생한다.</li><li>1 Mbps에서는 스텁 0.3m 이하 권장 (속도가 낮을수록 허용 스텁 길이가 늘어남).</li><li>ISOBUS(250 kbps)에서는 최대 스텁 길이 1m.</li></ul><p><strong>최대 노드 수:</strong></p><ul><li>CAN 사양 상 이론적 최대 노드 수는 제한이 없으나, 실제로는 버스 전기적 특성으로 약 110개 노드가 한계이다.</li><li>ISOBUS 구현에서는 실용적으로 30개 이하를 권장한다.</li></ul><hr><h2 id="_5-종단-저항-120ω" tabindex="-1"><a class="header-anchor" href="#_5-종단-저항-120ω"><span>5. 종단 저항 (120Ω)</span></a></h2><h3 id="왜-필요한가" tabindex="-1"><a class="header-anchor" href="#왜-필요한가"><span>왜 필요한가</span></a></h3><p>전선은 일종의 전송 선로이다. 신호가 선로 끝에 도달하면 &quot;반사&quot;가 일어난다. 반사된 신호가 되돌아오면 원래 신호를 왜곡시킨다.</p><p><strong>종단 저항(Termination Resistor)</strong>은 버스 양 끝에 달아 신호를 흡수해 반사를 막다. 저항값이 선로 특성 임피던스(120Ω)와 같아야 한다.</p><pre class="mermaid">graph LR
    RT1[&quot;120Ω&quot;] ---|CAN_H| STUB1[&quot;노드들&quot;]
    RT1 ---       |CAN_L| STUB1
    STUB1 ---     |CAN_H| RT2[&quot;120Ω&quot;]
    STUB1 ---     |CAN_L| RT2

    Note1[&quot;양 끝 120Ω 병렬&lt;br&gt;= 합성 저항 60Ω&quot;]

    style RT1 fill:#f9a,stroke:#c55
    style RT2 fill:#f9a,stroke:#c55
</pre><p>두 종단 저항이 병렬 연결되므로 버스 전체 임피던스는 <strong>60Ω</strong>이다. 이 값이 맞지 않으면 파형이 불안정해진다.</p><p><strong>멀티미터로 종단 저항 확인하는 방법:</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">1. 버스의 전원을 끈다.</span>
<span class="line">2. CAN_H와 CAN_L 사이의 저항을 측정한다.</span>
<span class="line">3. 정상: 약 60Ω</span>
<span class="line">   종단저항 1개 없음: 약 120Ω</span>
<span class="line">   종단저항 모두 없음: 무한대(∞)</span>
<span class="line">   단선: 무한대(∞)</span>
<span class="line">   CAN_H/CAN_L 단락: 0Ω</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><details class="hint-container details"><summary>Python 예제: 종단 저항 측정값 해석</summary><div class="language-python line-numbers-mode" data-highlighter="prismjs" data-ext="py" data-title="py"><pre><code><span class="line"><span class="token comment"># 종단 저항 측정값 해석 예시 (진단 스크립트)</span></span>
<span class="line"><span class="token keyword">def</span> <span class="token function">interpret_termination_resistance</span><span class="token punctuation">(</span>ohm<span class="token punctuation">)</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token keyword">if</span> ohm <span class="token operator">&lt;</span> <span class="token number">10</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token string">&quot;ERROR: CAN_H/CAN_L 단락 (Short circuit)&quot;</span></span>
<span class="line">    <span class="token keyword">elif</span> <span class="token number">50</span> <span class="token operator">&lt;=</span> ohm <span class="token operator">&lt;=</span> <span class="token number">70</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token string">&quot;OK: 정상 (양쪽 120Ω 종단저항 장착됨)&quot;</span></span>
<span class="line">    <span class="token keyword">elif</span> <span class="token number">110</span> <span class="token operator">&lt;=</span> ohm <span class="token operator">&lt;=</span> <span class="token number">130</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token string">&quot;WARNING: 종단저항 1개만 장착됨&quot;</span></span>
<span class="line">    <span class="token keyword">elif</span> ohm <span class="token operator">&gt;</span> <span class="token number">1000</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token string">&quot;ERROR: 종단저항 없음 또는 단선&quot;</span></span>
<span class="line">    <span class="token keyword">else</span><span class="token punctuation">:</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token string-interpolation"><span class="token string">f&quot;WARNING: 비정상 저항값 </span><span class="token interpolation"><span class="token punctuation">{</span>ohm<span class="token punctuation">}</span></span><span class="token string">Ω — 배선 점검 필요&quot;</span></span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">print</span><span class="token punctuation">(</span>interpret_termination_resistance<span class="token punctuation">(</span><span class="token number">60</span><span class="token punctuation">)</span><span class="token punctuation">)</span>   <span class="token comment"># OK</span></span>
<span class="line"><span class="token keyword">print</span><span class="token punctuation">(</span>interpret_termination_resistance<span class="token punctuation">(</span><span class="token number">120</span><span class="token punctuation">)</span><span class="token punctuation">)</span>  <span class="token comment"># WARNING</span></span>
<span class="line"><span class="token keyword">print</span><span class="token punctuation">(</span>interpret_termination_resistance<span class="token punctuation">(</span><span class="token number">9999</span><span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token comment"># ERROR</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div></details><p>종단 저항이 올바르게 설치된 버스에서, 실제로 얼마나 빠르게, 얼마나 먼 거리까지 통신할 수 있을까요? 속도와 거리 사이에는 중요한 트레이드오프가 있다.</p><hr><h2 id="_6-통신-속도와-버스-길이" tabindex="-1"><a class="header-anchor" href="#_6-통신-속도와-버스-길이"><span>6. 통신 속도와 버스 길이</span></a></h2><p>CAN에서 <strong>속도와 거리는 반비례</strong> 관계이다. 속도가 빠를수록 비트 하나의 시간이 짧아지는데, 버스가 길면 신호가 양 끝을 왕복하는 시간(전파 지연)이 비트 시간을 초과해 버린다.</p><table><thead><tr><th>비트레이트</th><th>최대 버스 길이</th><th>주요 용도</th></tr></thead><tbody><tr><td>1 Mbps</td><td>약 25 m</td><td>고속 제어 (소형 ECU 네트워크)</td></tr><tr><td>500 kbps</td><td>약 100 m</td><td>자동차 파워트레인 네트워크</td></tr><tr><td><strong>250 kbps</strong></td><td>약 250 m</td><td><strong>ISOBUS 표준 속도</strong></td></tr><tr><td>125 kbps</td><td>약 500 m</td><td>저속 기능 버스 (차체 계통)</td></tr><tr><td>50 kbps</td><td>약 1000 m</td><td>장거리 산업 네트워크</td></tr></tbody></table><p>ISOBUS는 250 kbps를 표준으로 사용한다. 트랙터 + 작업기의 연결 거리를 고려해도 충분한 속도와 거리를 제공한다.</p><pre class="mermaid">xychart-beta
    title &quot;비트레이트와 최대 버스 길이&quot;
    x-axis [&quot;1 Mbps&quot;, &quot;500 kbps&quot;, &quot;250 kbps&quot;, &quot;125 kbps&quot;, &quot;50 kbps&quot;]
    y-axis &quot;최대 버스 길이 (m)&quot; 0 --&gt; 1100
    bar [25, 100, 250, 500, 1000]
</pre><div class="language-c line-numbers-mode" data-highlighter="prismjs" data-ext="c" data-title="c"><pre><code><span class="line"><span class="token comment">/* CAN 비트 타이밍 설정 예시 (250 kbps, 16 MHz 클럭) */</span></span>
<span class="line"><span class="token comment">/* Bit time = 1 / 250,000 = 4 µs */</span></span>
<span class="line"><span class="token comment">/* TQ(Time Quantum) 단위로 비트 시간을 분할 */</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">typedef</span> <span class="token keyword">struct</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token class-name">uint8_t</span> brp<span class="token punctuation">;</span>   <span class="token comment">/* Baud Rate Prescaler */</span></span>
<span class="line">    <span class="token class-name">uint8_t</span> tseg1<span class="token punctuation">;</span> <span class="token comment">/* Time Segment 1 */</span></span>
<span class="line">    <span class="token class-name">uint8_t</span> tseg2<span class="token punctuation">;</span> <span class="token comment">/* Time Segment 2 */</span></span>
<span class="line">    <span class="token class-name">uint8_t</span> sjw<span class="token punctuation">;</span>   <span class="token comment">/* Synchronization Jump Width */</span></span>
<span class="line"><span class="token punctuation">}</span> CAN_BitTiming<span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token comment">/* 250 kbps @ 16 MHz: BRP=4, TSEG1=11, TSEG2=4, SJW=1 */</span></span>
<span class="line"><span class="token comment">/* Bit time = (1 + TSEG1 + TSEG2) * TQ = 16 TQ          */</span></span>
<span class="line"><span class="token comment">/* TQ = BRP / f_clk = 4 / 16MHz = 0.25 µs               */</span></span>
<span class="line"><span class="token comment">/* Bit time = 16 * 0.25 µs = 4 µs → 250 kbps            */</span></span>
<span class="line">CAN_BitTiming timing_250k <span class="token operator">=</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token punctuation">.</span>brp   <span class="token operator">=</span> <span class="token number">4</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">.</span>tseg1 <span class="token operator">=</span> <span class="token number">11</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">.</span>tseg2 <span class="token operator">=</span> <span class="token number">4</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">.</span>sjw   <span class="token operator">=</span> <span class="token number">1</span></span>
<span class="line"><span class="token punctuation">}</span><span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>속도와 거리가 정해지면, 마지막으로 물리적인 연결 방법을 알아야 한다. CAN 장비를 실제로 연결할 때 사용하는 커넥터와 핀 배치를 살펴봅시다.</p><hr><h2 id="_7-커넥터와-핀아웃" tabindex="-1"><a class="header-anchor" href="#_7-커넥터와-핀아웃"><span>7. 커넥터와 핀아웃</span></a></h2><h3 id="db9-커넥터-iso-11898-권장" tabindex="-1"><a class="header-anchor" href="#db9-커넥터-iso-11898-권장"><span>DB9 커넥터 (ISO 11898 권장)</span></a></h3><p>CAN 디버깅 장비나 PC 인터페이스에서 가장 많이 쓰이는 9핀 D-Sub 커넥터이다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">DB9 Female (장비 측)</span>
<span class="line"> ┌─────────────────────┐</span>
<span class="line"> │  ○   ○   ○   ○   ○  │  ← 핀 1~5</span>
<span class="line"> │    ○   ○   ○   ○    │  ← 핀 6~9</span>
<span class="line"> └─────────────────────┘</span>
<span class="line"></span>
<span class="line">핀 번호 → 신호:</span>
<span class="line">  Pin 1: 없음 (NC)</span>
<span class="line">  Pin 2: CAN_L  ← 통신</span>
<span class="line">  Pin 3: GND    ← 접지</span>
<span class="line">  Pin 4: 없음 (NC)</span>
<span class="line">  Pin 5: CAN_SHLD (선택적, 차폐 연결)</span>
<span class="line">  Pin 6: GND    ← 접지 (선택적)</span>
<span class="line">  Pin 7: CAN_H  ← 통신</span>
<span class="line">  Pin 8: 없음 (NC)</span>
<span class="line">  Pin 9: CAN_V+ (선택적, 전원 공급)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>핵심 핀 요약:</strong></p><table><thead><tr><th>핀 번호</th><th>신호명</th><th>설명</th></tr></thead><tbody><tr><td>2</td><td>CAN_L</td><td>통신 선 (저전압 측)</td></tr><tr><td>3</td><td>GND</td><td>공통 접지</td></tr><tr><td>7</td><td>CAN_H</td><td>통신 선 (고전압 측)</td></tr></tbody></table><h3 id="isobus-농기계-진단-커넥터" tabindex="-1"><a class="header-anchor" href="#isobus-농기계-진단-커넥터"><span>ISOBUS / 농기계 진단 커넥터</span></a></h3><p>트랙터와 작업기 연결에는 <strong>AMP Deutsch DT 시리즈</strong> 방수 커넥터가 많이 사용된다. 진단 목적으로는 <strong>9핀 Deutsch 커넥터</strong>가 표준이다.</p><pre class="mermaid">graph TB
    subgraph 농기계_커넥터_핀_배치
        direction TB
        P1[&quot;1: Battery(+12V)&quot;]
        P2[&quot;2: Ignition(+12V)&quot;]
        P3[&quot;3: GND&quot;]
        P4[&quot;4: ECU_GND&quot;]
        P5[&quot;5: CAN_H (ISOBUS)&quot;]
        P6[&quot;6: CAN_L (ISOBUS)&quot;]
        P7[&quot;7: LIN Bus&quot;]
        P8[&quot;8: Reserved&quot;]
        P9[&quot;9: CAN_H (진단 전용)&quot;]
    end
</pre><p>실제 농기계 커넥터 배치는 제조사마다 다를 수 있으므로, 항상 해당 기종의 전기 회로도를 참고해야 한다.</p><p><strong>현장에서 CAN 신호 확인 방법:</strong></p><div class="language-c line-numbers-mode" data-highlighter="prismjs" data-ext="c" data-title="c"><pre><code><span class="line"><span class="token comment">/* CAN 메시지 수신 및 출력 예시 (의사코드 / 임베디드 C) */</span></span>
<span class="line"><span class="token macro property"><span class="token directive-hash">#</span><span class="token directive keyword">include</span> <span class="token string">&lt;stdio.h&gt;</span></span></span>
<span class="line"><span class="token macro property"><span class="token directive-hash">#</span><span class="token directive keyword">include</span> <span class="token string">&lt;stdint.h&gt;</span></span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">typedef</span> <span class="token keyword">struct</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token class-name">uint32_t</span> id<span class="token punctuation">;</span></span>
<span class="line">    <span class="token class-name">uint8_t</span>  dlc<span class="token punctuation">;</span>       <span class="token comment">/* Data Length Code: 0~8 */</span></span>
<span class="line">    <span class="token class-name">uint8_t</span>  data<span class="token punctuation">[</span><span class="token number">8</span><span class="token punctuation">]</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span> CAN_Message<span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line"><span class="token keyword">void</span> <span class="token function">on_can_receive</span><span class="token punctuation">(</span>CAN_Message <span class="token operator">*</span>msg<span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token function">printf</span><span class="token punctuation">(</span><span class="token string">&quot;ID: 0x%08X  DLC: %d  Data:&quot;</span><span class="token punctuation">,</span> msg<span class="token operator">-&gt;</span>id<span class="token punctuation">,</span> msg<span class="token operator">-&gt;</span>dlc<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token keyword">for</span> <span class="token punctuation">(</span><span class="token keyword">int</span> i <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span> i <span class="token operator">&lt;</span> msg<span class="token operator">-&gt;</span>dlc<span class="token punctuation">;</span> i<span class="token operator">++</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">        <span class="token function">printf</span><span class="token punctuation">(</span><span class="token string">&quot; %02X&quot;</span><span class="token punctuation">,</span> msg<span class="token operator">-&gt;</span>data<span class="token punctuation">[</span>i<span class="token punctuation">]</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">}</span></span>
<span class="line">    <span class="token function">printf</span><span class="token punctuation">(</span><span class="token string">&quot;\\n&quot;</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line"><span class="token comment">/* 출력 예시:</span>
<span class="line">   ID: 0x0CF004B4  DLC: 8  Data: F0 00 FF 00 00 00 00 FF</span>
<span class="line">   → ISOBUS J1939 EEC1 (엔진 전자 제어 #1) 메시지</span>
<span class="line">*/</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN은 CAN_H/CAN_L 두 선의 <strong>전압 차이</strong>로 신호를 전달해 노이즈에 강한다.</li><li>Dominant(0): CAN_H=3.5V, CAN_L=1.5V / Recessive(1): 양쪽 2.5V.</li><li>종단 저항 120Ω을 버스 양 끝에 반드시 설치해야 한다. 합성 저항 60Ω.</li><li>멀티미터로 CAN_H-CAN_L 간 저항을 측정해 60Ω이면 정상이다.</li><li>ISOBUS 표준 속도는 250 kbps이며, 최대 버스 길이는 약 250m이다.</li><li>DB9 커넥터 기준 CAN_H=핀7, CAN_L=핀2, GND=핀3이다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/04-can-data-frame">CAN 데이터 프레임</a></li></ul>`,92)]))}const d=s(i,[["render",l],["__file","03-can-physical.html.vue"]]),r=JSON.parse('{"path":"/study/isobus/03-can-physical.html","title":"CAN 물리 계층","lang":"en-US","frontmatter":{"title":"CAN 물리 계층","description":"CAN_H/CAN_L 차동 신호, 종단 저항, 통신 속도와 버스 길이, 커넥터 핀아웃을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","CAN","물리계층","차동신호","종단저항"],"prev":"/study/isobus/02-can-intro","next":"/study/isobus/04-can-data-frame"},"headers":[{"level":1,"title":"CAN 물리 계층","slug":"can-물리-계층","link":"#can-물리-계층","children":[{"level":2,"title":"1. CAN_H와 CAN_L — 차동 신호","slug":"_1-can-h와-can-l-—-차동-신호","link":"#_1-can-h와-can-l-—-차동-신호","children":[{"level":3,"title":"왜 두 선이 필요한가","slug":"왜-두-선이-필요한가","link":"#왜-두-선이-필요한가","children":[]},{"level":3,"title":"전압 레벨","slug":"전압-레벨","link":"#전압-레벨","children":[]}]},{"level":2,"title":"2. Dominant vs Recessive — Wired-AND 동작","slug":"_2-dominant-vs-recessive-—-wired-and-동작","link":"#_2-dominant-vs-recessive-—-wired-and-동작","children":[{"level":3,"title":"상태 정의","slug":"상태-정의","link":"#상태-정의","children":[]},{"level":3,"title":"Wired-AND란","slug":"wired-and란","link":"#wired-and란","children":[]},{"level":3,"title":"물리적으로 이해하기","slug":"물리적으로-이해하기","link":"#물리적으로-이해하기","children":[]},{"level":3,"title":"줄다리기 비유","slug":"줄다리기-비유","link":"#줄다리기-비유","children":[]},{"level":3,"title":"왜 ID가 작을수록 우선순위가 높은가","slug":"왜-id가-작을수록-우선순위가-높은가","link":"#왜-id가-작을수록-우선순위가-높은가","children":[]}]},{"level":2,"title":"3. 파형으로 보는 CAN 신호","slug":"_3-파형으로-보는-can-신호","link":"#_3-파형으로-보는-can-신호","children":[]},{"level":2,"title":"4. 버스 토폴로지","slug":"_4-버스-토폴로지","link":"#_4-버스-토폴로지","children":[]},{"level":2,"title":"5. 종단 저항 (120Ω)","slug":"_5-종단-저항-120ω","link":"#_5-종단-저항-120ω","children":[{"level":3,"title":"왜 필요한가","slug":"왜-필요한가","link":"#왜-필요한가","children":[]}]},{"level":2,"title":"6. 통신 속도와 버스 길이","slug":"_6-통신-속도와-버스-길이","link":"#_6-통신-속도와-버스-길이","children":[]},{"level":2,"title":"7. 커넥터와 핀아웃","slug":"_7-커넥터와-핀아웃","link":"#_7-커넥터와-핀아웃","children":[{"level":3,"title":"DB9 커넥터 (ISO 11898 권장)","slug":"db9-커넥터-iso-11898-권장","link":"#db9-커넥터-iso-11898-권장","children":[]},{"level":3,"title":"ISOBUS / 농기계 진단 커넥터","slug":"isobus-농기계-진단-커넥터","link":"#isobus-농기계-진단-커넥터","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/03-can-physical.md"}');export{d as comp,r as data};
