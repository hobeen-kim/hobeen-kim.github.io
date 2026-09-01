import{_ as d,c as e,f as s,o as n}from"./app-g4YXskd6.js";const r="/images/study-isobus/10-can-id-bitfields-light.png",a="/images/study-isobus/10-can-id-bitfields-dark.png",l="/images/study-isobus/10-commanded-address-light.png",i="/images/study-isobus/10-commanded-address-dark.png",o={};function A(c,t){return n(),e("div",null,t[0]||(t[0]=[s('<h1 id="j1939-주소-체계" tabindex="-1"><a class="header-anchor" href="#j1939-주소-체계"><span>J1939 주소 체계</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>소스 주소(SA)의 범위와 예약 주소의 의미를 설명할 수 있다.</li><li>64비트 NAME의 각 필드 구성과 역할을 이해한다.</li><li>주소 클레임 절차의 단계별 흐름과 충돌 해결 방식을 설명할 수 있다.</li><li>Commanded Address(PGN 65240)의 동작 원리를 이해한다.</li></ul></div><h2 id="_1-소스-주소-sa" tabindex="-1"><a class="header-anchor" href="#_1-소스-주소-sa"><span>1. 소스 주소 (SA)</span></a></h2><p>J1939 네트워크에서 모든 ECU는 <strong>소스 주소(Source Address, SA)</strong>를 가진다. SA는 8비트 값으로, 29비트 CAN ID의 <strong>하위 8비트(비트 7~0)</strong>에 위치한다.</p><p><img src="'+r+'" alt="29비트 CAN Identifier 비트 필드 배치"><img src="'+a+`" alt="29비트 CAN Identifier 비트 필드 배치"></p><h3 id="sa-값-범위" tabindex="-1"><a class="header-anchor" href="#sa-값-범위"><span>SA 값 범위</span></a></h3><table><thead><tr><th>범위</th><th>의미</th></tr></thead><tbody><tr><td>0 ~ 127, 248 ~ 253</td><td>Preferred address 영역 — 이 범위를 클레임하는 장치는 해당 주소에 정의된 기능을 실제로 수행해야 한다</td></tr><tr><td>128 ~ 247</td><td>Self-configurable address 범위 — preferred address가 없거나 클레임에 실패한 장치가 사용</td></tr><tr><td>254 (0xFE)</td><td>Null Address — <strong>소스 주소로만</strong> 사용. 주소 클레임 전, 또는 클레임 실패 시</td></tr><tr><td>255 (0xFF)</td><td>Global Address — <strong>목적지 주소로만</strong> 사용 (브로드캐스트)</td></tr></tbody></table><h3 id="예약된-주소-일부" tabindex="-1"><a class="header-anchor" href="#예약된-주소-일부"><span>예약된 주소 (일부)</span></a></h3><table><thead><tr><th>SA</th><th>장치</th></tr></thead><tbody><tr><td>0 (0x00)</td><td>Engine #1</td></tr><tr><td>3 (0x03)</td><td>Transmission #1</td></tr><tr><td>23 (0x17)</td><td>Instrument Cluster #1</td></tr><tr><td>33 (0x21)</td><td>Cab Controller — Primary</td></tr><tr><td>38 (0x26)</td><td>Virtual Terminal (ISOBUS)</td></tr><tr><td>247 (0xF7)</td><td>Task Controller (ISOBUS)</td></tr></tbody></table><p>예약(preferred) 주소는 <strong>우선권</strong>을 가지지 않는다. 주소 클레임 경쟁에서 NAME 값이 작은 쪽이 이기며, 예약 주소라도 더 작은 NAME을 가진 장치가 있으면 양보해야 한다. 기능 판단도 SA가 아니라 반드시 NAME으로 해야 한다. 참고로 <strong>ISOBUS(ISO 11783) 적합 장치는 self-configurable address 능력이 필수</strong>이며, non-configurable 장치는 J1939·구판 호환을 위해 허용될 뿐이다.</p><pre class="mermaid">graph LR
    subgraph 29bit_CAN_ID
        P[&quot;Priority&lt;br&gt;(3bit)&quot;]
        R[&quot;Reserved&lt;br&gt;(1bit)&quot;]
        DP[&quot;Data Page&lt;br&gt;(1bit)&quot;]
        PF[&quot;PDU Format&lt;br&gt;(8bit)&quot;]
        PS[&quot;PDU Specific&lt;br&gt;(8bit)&quot;]
        SA[&quot;Source Address&lt;br&gt;(8bit)&quot;]
    end
    P --&gt; R --&gt; DP --&gt; PF --&gt; PS --&gt; SA
    style SA fill:#ffd700,stroke:#b8860b,color:#000
</pre><h2 id="_2-name-64비트" tabindex="-1"><a class="header-anchor" href="#_2-name-64비트"><span>2. NAME (64비트)</span></a></h2><p><strong>NAME</strong>은 J1939 네트워크에서 ECU를 전 세계적으로 고유하게 식별하는 64비트 구조체이다. 주소 클레임 시 충돌이 발생하면 NAME 값을 비교해 우선순위를 결정한다. NAME 값이 <strong>수치적으로 더 작은</strong> 장치가 주소를 획득한다.</p><h3 id="name-필드-구성" tabindex="-1"><a class="header-anchor" href="#name-필드-구성"><span>NAME 필드 구성</span></a></h3><pre class="mermaid">packet-beta
  0-0: &quot;AAC&quot;
  1-3: &quot;IG&quot;
  4-7: &quot;VSI&quot;
  8-14: &quot;VS&quot;
  15-15: &quot;Rsvd&quot;
  16-23: &quot;Function&quot;
  24-28: &quot;FI&quot;
  29-31: &quot;EI&quot;
  32-42: &quot;Manufacturer Code&quot;
  43-63: &quot;Identity Number&quot;
</pre><table><thead><tr><th>필드</th><th>비트 수</th><th>위치 (MSB 기준)</th><th>설명</th></tr></thead><tbody><tr><td>Arbitrary Address Capable (AAC)</td><td>1</td><td>bit 63</td><td>1이면 자동 주소 재할당 가능</td></tr><tr><td>Industry Group (IG)</td><td>3</td><td>bit 62~60</td><td>0=Global, 2=Agricultural</td></tr><tr><td>Vehicle System Instance (VSI)</td><td>4</td><td>bit 59~56</td><td>동일 시스템 여러 개 구분</td></tr><tr><td>Vehicle System (VS)</td><td>7</td><td>bit 55~49</td><td>시스템 유형 (예: 트랙터)</td></tr><tr><td>Reserved</td><td>1</td><td>bit 48</td><td>항상 0</td></tr><tr><td>Function (F)</td><td>8</td><td>bit 47~40</td><td>장치 기능 (예: 엔진 제어)</td></tr><tr><td>Function Instance (FI)</td><td>5</td><td>bit 39~35</td><td>동일 기능 여러 개 구분</td></tr><tr><td>ECU Instance (EI)</td><td>3</td><td>bit 34~32</td><td>동일 장치 내 ECU 구분</td></tr><tr><td>Manufacturer Code</td><td>11</td><td>bit 31~21</td><td>제조사 코드 (SAE J1939 등록)</td></tr><tr><td>Identity Number</td><td>21</td><td>bit 20~0</td><td>제조사 내 일련번호</td></tr></tbody></table><p><strong>NAME 예시 (16진수):</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">NAME = 0x2000000000000000</span>
<span class="line">       └─────────────────┘</span>
<span class="line">         Arbitrary Address Capable = 0,</span>
<span class="line">         Industry Group = 2 (Agricultural equipment),</span>
<span class="line">         Function = 0 (Engine),</span>
<span class="line">         Manufacturer Code = 0,</span>
<span class="line">         Identity Number = 0</span>
<span class="line"></span>
<span class="line">최상위 바이트 = 0b0010_0000 = 0x20</span>
<span class="line">  → AAC(1bit)=0, IG(3bit)=010(2), VSI(4bit)=0000</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="_3-주소-클레임-절차" tabindex="-1"><a class="header-anchor" href="#_3-주소-클레임-절차"><span>3. 주소 클레임 절차</span></a></h2><p>J1939 장치는 네트워크에 연결되면 <strong>Address Claimed 메시지(PGN 60928, 0xEE00)</strong>를 브로드캐스트하여 주소를 선점한다. 같은 주소를 사용하려는 장치가 있으면 NAME 비교를 통해 충돌을 해결한다.</p><p>클레임에 앞서 <strong>주소 조회 시퀀스</strong>를 거치는 것이 표준 절차다. Request for Address Claimed(PGN 59904)를 Global 또는 자신의 초기 주소로 보내고, <strong>최소 250 ms + RTxD</strong>를 대기하면서 수신된 Address Claimed들로 사용 중인 주소를 파악한 뒤, 비어 있는 주소를 클레임한다. 여기서 <strong>RTxD(Random Transmit Delay)</strong>는 0~255 범위의 난수에 0.6 ms를 곱한 지연 시간으로, 여러 장치가 동시에 송신해 버스 오류를 일으키는 것을 막는다.</p><pre class="mermaid">sequenceDiagram
    participant ECU_A as ECU A (NAME=0x100)
    participant BUS as CAN Bus
    participant ECU_B as ECU B (NAME=0x200)

    Note over ECU_A,ECU_B: 전원 ON

    ECU_A-&gt;&gt;BUS: Address Claimed (SA=23, NAME=0x100)
    ECU_B-&gt;&gt;BUS: Address Claimed (SA=23, NAME=0x200)

    Note over BUS: SA 충돌 감지

    ECU_A-&gt;&gt;BUS: Address Claimed 재송신 (SA=23, NAME=0x100)
    Note over ECU_A: 상대 NAME(0x200) &gt; 내 NAME(0x100)&lt;br&gt;→ 승자도 재클레임으로 주소를 지킨다
    ECU_B-&gt;&gt;ECU_B: 상대 NAME(0x100) &lt; 내 NAME(0x200)&lt;br&gt;→ 내가 패배

    alt AAC=1 (자동 재할당 가능)
        ECU_B-&gt;&gt;BUS: Address Claimed (SA=128, NAME=0x200)
        Note over ECU_B: 새 주소 SA=128로 클레임 성공 (128~247 범위)
    else AAC=0 (자동 재할당 불가)
        ECU_B-&gt;&gt;BUS: Cannot Claim Address (SA=0xFE)
        Note over ECU_B: Null Address로 동작 (제한적 기능)
    end
</pre><h3 id="절차-단계-요약" tabindex="-1"><a class="header-anchor" href="#절차-단계-요약"><span>절차 단계 요약</span></a></h3><ol><li><strong>전원 ON</strong> — ECU가 사용할 SA를 선택 (선호 주소 또는 저장된 초기 주소)</li><li><strong>주소 조회</strong> — Request for Address Claimed(PGN 59904)를 보내고 250 ms + RTxD 대기하며 사용 중인 주소를 파악</li><li><strong>Address Claimed 전송</strong> — 선택한 SA와 자신의 NAME을 PGN 60928으로 브로드캐스트</li><li><strong>충돌 감지</strong> — 같은 SA로 다른 NAME이 수신되면 충돌</li><li><strong>NAME 비교</strong> — 더 작은 NAME 값을 가진 장치가 해당 SA를 획득. <strong>승자도 자신의 NAME으로 Address Claimed를 재송신</strong>해 주소를 지켜야 한다</li><li><strong>패자 처리</strong><ul><li>AAC=1: 128~247 범위에서 다른 SA를 선택하여 재클레임</li><li>AAC=0: Cannot Claim (SA=0xFE) 전송 후 수신 전용 동작 (RTxD 삽입 후 송신)</li></ul></li></ol><h3 id="타이밍-규칙" tabindex="-1"><a class="header-anchor" href="#타이밍-규칙"><span>타이밍 규칙</span></a></h3><table><thead><tr><th>항목</th><th>값</th></tr></thead><tbody><tr><td>주소 조회(Request) 후 대기</td><td>최소 250 ms + RTxD</td></tr><tr><td>클레임 성공 판정</td><td>Address Claimed 송신 후 250 ms 동안 경합 클레임이 없어야 성공</td></tr><tr><td>일반 통신 시작</td><td>클레임 성공 후 250 ms 경과 전에는 일반 메시지 송신 금지 (Request 응답은 예외)</td></tr><tr><td>RTxD</td><td>난수(0~255) × 0.6 ms</td></tr></tbody></table><h2 id="_4-commanded-address" tabindex="-1"><a class="header-anchor" href="#_4-commanded-address"><span>4. Commanded Address</span></a></h2><p><strong>Commanded Address</strong>는 외부 장치가 특정 ECU에게 주소를 강제로 지정하는 메커니즘이다. <strong>PGN 65240 (0xFED8)</strong>을 사용하며, 지원 여부는 <strong>선택 사항</strong>이다.</p><h3 id="메시지-구조" tabindex="-1"><a class="header-anchor" href="#메시지-구조"><span>메시지 구조</span></a></h3><p><img src="`+l+'" alt="Commanded Address 9바이트 구조 — Byte 1~8은 대상 NAME, Byte 9는 새 SA. 8바이트를 넘어 BAM으로 전송한다"><img src="'+i+`" alt="Commanded Address 9바이트 구조 — Byte 1~8은 대상 NAME, Byte 9는 새 SA. 8바이트를 넘어 BAM으로 전송한다"></p><p>데이터가 9바이트라 단일 CAN 프레임(8바이트)에 담을 수 없으므로 <strong>BAM(Broadcast Announce Message) 전송 프로토콜로 Global(255)에 송신</strong>한다. 따라서 Commanded Address를 지원하는 장치는 BAM 수신도 지원해야 한다.</p><h3 id="동작-방식" tabindex="-1"><a class="header-anchor" href="#동작-방식"><span>동작 방식</span></a></h3><pre class="mermaid">sequenceDiagram
    participant MASTER as 관리 장치 (예: 진단기)
    participant BUS as CAN Bus
    participant ECU as 대상 ECU (NAME=0xABCD)

    MASTER-&gt;&gt;BUS: Commanded Address (BAM 전송)&lt;br&gt;(NAME=0xABCD, New SA=0x10)
    BUS-&gt;&gt;ECU: Commanded Address 수신

    ECU-&gt;&gt;ECU: 내 NAME(0xABCD) 일치 확인
    ECU-&gt;&gt;BUS: Address Claimed (SA=0x10, NAME=0xABCD)
    Note over ECU: SA=0x10으로 변경 완료
</pre><h3 id="사용-사례" tabindex="-1"><a class="header-anchor" href="#사용-사례"><span>사용 사례</span></a></h3><table><thead><tr><th>상황</th><th>설명</th></tr></thead><tbody><tr><td>공장 설정</td><td>제조 라인에서 장치에 고정 SA 부여</td></tr><tr><td>네트워크 재구성</td><td>시스템 통합 시 주소 충돌 사전 방지</td></tr><tr><td>진단/유지보수</td><td>특정 SA로 장치를 강제 이동</td></tr></tbody></table><p>Commanded Address를 수락한 ECU는 명령받은 주소를 새 SA로 하는 <strong>Address Claimed 메시지를 발행</strong>해야 하며, 이때 일반 주소 클레임 요구사항이 그대로 적용된다. 수신했지만 주소를 변경할 수 없는 ECU는 <strong>현재 SA를 클레임하는 Address Claimed로 응답</strong>한다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>SA는 8비트이며 0~127·248~253은 preferred, 128~247은 self-configurable 범위, 254=Null(소스 전용), 255=Global(목적지 전용)이다.</li><li>SA는 29비트 CAN ID의 하위 8비트에 위치한다.</li><li>NAME은 64비트 구조체로 장치를 전 세계적으로 고유 식별하며, <strong>값이 작을수록 우선순위가 높다.</strong></li><li>클레임 전에 주소 조회 후 250 ms + RTxD를 대기하고, 충돌 시 NAME 비교로 승자를 결정한다. 승자도 Address Claimed를 재송신해야 한다.</li><li>AAC=1인 장치는 충돌 패배 후 128~247 범위의 다른 주소로 자동 재클레임할 수 있다. ISOBUS 적합 장치는 이 능력이 필수다.</li><li>Commanded Address(PGN 65240)는 외부에서 ECU의 주소를 강제 지정하는 방법이며, 9바이트 데이터라 BAM으로 전송된다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/11-j1939-transport">J1939 Transport Protocol</a></li></ul>`,39)]))}const h=d(o,[["render",A],["__file","10-j1939-address.html.vue"]]),u=JSON.parse('{"path":"/study/isobus/10-j1939-address.html","title":"J1939 주소 체계","lang":"en-US","frontmatter":{"title":"J1939 주소 체계","description":"J1939의 소스 주소(SA), 64비트 NAME, 주소 클레임 절차, Commanded Address를 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","J1939","CAN","주소","NAME"],"prev":"/study/isobus/09-j1939-message","next":"/study/isobus/11-j1939-transport"},"headers":[{"level":1,"title":"J1939 주소 체계","slug":"j1939-주소-체계","link":"#j1939-주소-체계","children":[{"level":2,"title":"1. 소스 주소 (SA)","slug":"_1-소스-주소-sa","link":"#_1-소스-주소-sa","children":[{"level":3,"title":"SA 값 범위","slug":"sa-값-범위","link":"#sa-값-범위","children":[]},{"level":3,"title":"예약된 주소 (일부)","slug":"예약된-주소-일부","link":"#예약된-주소-일부","children":[]}]},{"level":2,"title":"2. NAME (64비트)","slug":"_2-name-64비트","link":"#_2-name-64비트","children":[{"level":3,"title":"NAME 필드 구성","slug":"name-필드-구성","link":"#name-필드-구성","children":[]}]},{"level":2,"title":"3. 주소 클레임 절차","slug":"_3-주소-클레임-절차","link":"#_3-주소-클레임-절차","children":[{"level":3,"title":"절차 단계 요약","slug":"절차-단계-요약","link":"#절차-단계-요약","children":[]},{"level":3,"title":"타이밍 규칙","slug":"타이밍-규칙","link":"#타이밍-규칙","children":[]}]},{"level":2,"title":"4. Commanded Address","slug":"_4-commanded-address","link":"#_4-commanded-address","children":[{"level":3,"title":"메시지 구조","slug":"메시지-구조","link":"#메시지-구조","children":[]},{"level":3,"title":"동작 방식","slug":"동작-방식","link":"#동작-방식","children":[]},{"level":3,"title":"사용 사례","slug":"사용-사례","link":"#사용-사례","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/10-j1939-address.md"}');export{h as comp,u as data};
