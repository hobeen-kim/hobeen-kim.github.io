import{_ as r,c as p,a,d as s,e as o,b as e,r as i,o as c,f as l}from"./app-DuMXKYjZ.js";const u={},h={class:"table-of-contents"};function b(C,n){const d=i("Header"),t=i("router-link");return c(),p("div",null,[a(d),s("nav",h,[s("ul",null,[s("li",null,[a(t,{to:"#_1-can-fd가-나온-이유"},{default:e(()=>n[0]||(n[0]=[l("1. CAN FD가 나온 이유")])),_:1}),s("ul",null,[s("li",null,[a(t,{to:"#기존-can의-한계"},{default:e(()=>n[1]||(n[1]=[l("기존 CAN의 한계")])),_:1})])])]),s("li",null,[a(t,{to:"#_2-can-fd의-구조"},{default:e(()=>n[2]||(n[2]=[l("2. CAN FD의 구조")])),_:1}),s("ul",null,[s("li",null,[a(t,{to:"#새로-추가된-제어-비트"},{default:e(()=>n[3]||(n[3]=[l("새로 추가된 제어 비트")])),_:1})]),s("li",null,[a(t,{to:"#can-fd-프레임-구조"},{default:e(()=>n[4]||(n[4]=[l("CAN FD 프레임 구조")])),_:1})]),s("li",null,[a(t,{to:"#프레임-흐름-다이어그램"},{default:e(()=>n[5]||(n[5]=[l("프레임 흐름 다이어그램")])),_:1})]),s("li",null,[a(t,{to:"#최대-64바이트-페이로드"},{default:e(()=>n[6]||(n[6]=[l("최대 64바이트 페이로드")])),_:1})])])]),s("li",null,[a(t,{to:"#_3-듀얼-비트레이트"},{default:e(()=>n[7]||(n[7]=[l("3. 듀얼 비트레이트")])),_:1}),s("ul",null,[s("li",null,[a(t,{to:"#두-개의-phase"},{default:e(()=>n[8]||(n[8]=[l("두 개의 Phase")])),_:1})]),s("li",null,[a(t,{to:"#brs-비트가-전환-신호"},{default:e(()=>n[9]||(n[9]=[l("BRS 비트가 전환 신호")])),_:1})]),s("li",null,[a(t,{to:"#실제-처리량-비교-예시"},{default:e(()=>n[10]||(n[10]=[l("실제 처리량 비교 예시")])),_:1})])])]),s("li",null,[a(t,{to:"#_4-can-2-0과의-호환성"},{default:e(()=>n[11]||(n[11]=[l("4. CAN 2.0과의 호환성")])),_:1}),s("ul",null,[s("li",null,[a(t,{to:"#같은-버스에서-공존할-수-있는가"},{default:e(()=>n[12]||(n[12]=[l("같은 버스에서 공존할 수 있는가?")])),_:1})]),s("li",null,[a(t,{to:"#isobus와-can-fd"},{default:e(()=>n[13]||(n[13]=[l("ISOBUS와 CAN FD")])),_:1})]),s("li",null,[a(t,{to:"#다음-챕터"},{default:e(()=>n[14]||(n[14]=[l("다음 챕터")])),_:1})])])])])]),n[15]||(n[15]=o(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN FD가 등장한 배경과 Classic CAN의 한계를 설명할 수 있다.</li><li>FDF, BRS, ESI 비트의 역할을 이해하고 CAN FD 프레임 구조를 설명할 수 있다.</li><li>듀얼 비트레이트 동작 원리와 BRS 비트의 역할을 이해한다.</li><li>FD tolerant / FD active 노드의 차이를 구분하고, ISOBUS와의 관계를 설명할 수 있다.</li></ul></div><hr><h1 id="_1-can-fd가-나온-이유" tabindex="-1"><a class="header-anchor" href="#_1-can-fd가-나온-이유"><span>1. CAN FD가 나온 이유</span></a></h1><h2 id="기존-can의-한계" tabindex="-1"><a class="header-anchor" href="#기존-can의-한계"><span>기존 CAN의 한계</span></a></h2><p>1986년 Bosch가 발표한 Classic CAN은 자동차 네트워크의 표준으로 자리 잡았다. 그러나 자동차 전자화가 가속화되면서 두 가지 근본적인 한계에 부딪혔다.</p><table><thead><tr><th>항목</th><th>Classic CAN (2.0B)</th><th>요구 사항</th></tr></thead><tbody><tr><td>최대 페이로드</td><td>8 바이트</td><td>수십~수백 바이트</td></tr><tr><td>최대 비트레이트</td><td>1 Mbps</td><td>수 Mbps 이상</td></tr></tbody></table><p><strong>한계 1 — 8바이트 페이로드 상한</strong></p><p>ECU 소프트웨어 업데이트(OTA), 레이더/카메라 데이터, 고정밀 센서 융합 등 현대 자동차 기능은 한 프레임에 훨씬 많은 데이터를 담아야 한다. 8바이트로는 여러 프레임으로 쪼개서 보내야 하고, 이는 오버헤드와 응답 지연을 유발한다.</p><p><strong>한계 2 — 1 Mbps 비트레이트 상한</strong></p><p>버스 길이와 전파 지연 특성상 Classic CAN은 이론적으로 1 Mbps가 최대다. ADAS, 자율주행처럼 실시간성이 요구되는 애플리케이션에서는 이 속도로는 대역폭이 부족하다.</p><p>Bosch는 이 두 한계를 모두 해결하기 위해 <strong>2012년 CAN FD(CAN with Flexible Data-rate)</strong> 규격을 발표했다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Classic CAN 한계 요약</span>
<span class="line">─────────────────────────────────────</span>
<span class="line">  페이로드:   최대 8 bytes</span>
<span class="line">  비트레이트: 최대 1 Mbps</span>
<span class="line">  → 현대 차량 전자화 요구를 충족 불가</span>
<span class="line">─────────────────────────────────────</span>
<span class="line">CAN FD 개선</span>
<span class="line">  페이로드:   최대 64 bytes  (8배)</span>
<span class="line">  비트레이트: Data phase 최대 8 Mbps (8배)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h1 id="_2-can-fd의-구조" tabindex="-1"><a class="header-anchor" href="#_2-can-fd의-구조"><span>2. CAN FD의 구조</span></a></h1><h2 id="새로-추가된-제어-비트" tabindex="-1"><a class="header-anchor" href="#새로-추가된-제어-비트"><span>새로 추가된 제어 비트</span></a></h2><p>CAN FD는 Classic CAN 프레임에 세 개의 비트를 추가해 하위 호환성을 유지하면서 새 기능을 제공한다.</p><table><thead><tr><th>비트</th><th>이름</th><th>역할</th></tr></thead><tbody><tr><td><strong>FDF</strong></td><td>FD Format</td><td>이 프레임이 CAN FD임을 표시 (FDF=1이면 CAN FD)</td></tr><tr><td><strong>BRS</strong></td><td>Bit Rate Switch</td><td>Data phase에서 비트레이트를 전환할지 결정</td></tr><tr><td><strong>ESI</strong></td><td>Error State Indicator</td><td>송신 노드의 에러 상태를 표시 (Error Active=0, Error Passive=1)</td></tr></tbody></table><h2 id="can-fd-프레임-구조" tabindex="-1"><a class="header-anchor" href="#can-fd-프레임-구조"><span>CAN FD 프레임 구조</span></a></h2><pre class="mermaid">packet-beta
  0-10: &quot;SOF + Arbitration ID (11/29 bit)&quot;
  11-14: &quot;Control (IDE, FDF, res, BRS, ESI, DLC)&quot;
  15-78: &quot;Data (0~64 bytes)&quot;
  79-93: &quot;CRC (17 or 21 bit)&quot;
  94-95: &quot;CRC Del + ACK&quot;
  96-97: &quot;ACK Del + EOF&quot;
</pre><blockquote><p>참고: CAN FD의 CRC는 페이로드 길이에 따라 17비트(0~16바이트) 또는 21비트(20~64바이트)로 확장된다.</p></blockquote><h2 id="프레임-흐름-다이어그램" tabindex="-1"><a class="header-anchor" href="#프레임-흐름-다이어그램"><span>프레임 흐름 다이어그램</span></a></h2><pre class="mermaid">sequenceDiagram
    participant TX as 송신 노드
    participant BUS as CAN 버스
    participant RX as 수신 노드

    TX-&gt;&gt;BUS: SOF + Arbitration ID (표준 속도)
    Note over BUS: Arbitration phase&lt;br&gt;(모든 노드 동일 속도)
    TX-&gt;&gt;BUS: FDF=1, BRS=1 (CAN FD, 비트레이트 전환)
    BUS--&gt;&gt;TX: BRS 이후 고속 전환
    TX-&gt;&gt;BUS: ESI + DLC + Data (64바이트, 고속)
    Note over BUS: Data phase&lt;br&gt;(고속 전송)
    TX-&gt;&gt;BUS: CRC (17/21비트)
    TX-&gt;&gt;BUS: ACK + EOF (표준 속도 복귀)
    BUS--&gt;&gt;RX: 수신 완료
</pre><h2 id="최대-64바이트-페이로드" tabindex="-1"><a class="header-anchor" href="#최대-64바이트-페이로드"><span>최대 64바이트 페이로드</span></a></h2><p>DLC(Data Length Code) 값과 실제 데이터 길이의 매핑이 CAN FD에서 확장되었다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">DLC  0~ 8 → 0~8 bytes  (Classic CAN과 동일)</span>
<span class="line">DLC  9    → 12 bytes</span>
<span class="line">DLC 10    → 16 bytes</span>
<span class="line">DLC 11    → 20 bytes</span>
<span class="line">DLC 12    → 24 bytes</span>
<span class="line">DLC 13    → 32 bytes</span>
<span class="line">DLC 14    → 48 bytes</span>
<span class="line">DLC 15    → 64 bytes</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h1 id="_3-듀얼-비트레이트" tabindex="-1"><a class="header-anchor" href="#_3-듀얼-비트레이트"><span>3. 듀얼 비트레이트</span></a></h1><h2 id="두-개의-phase" tabindex="-1"><a class="header-anchor" href="#두-개의-phase"><span>두 개의 Phase</span></a></h2><p>CAN FD 프레임은 <strong>두 개의 비트레이트 구간</strong>으로 나뉜다.</p><pre class="mermaid">gantt
    title CAN FD 듀얼 비트레이트 타임라인
    dateFormat X
    axisFormat %s

    section Arbitration Phase (표준 속도)
    SOF + ID + Control (FDF/BRS 포함)  :a1, 0, 4

    section Data Phase (고속)
    ESI + DLC + Data + CRC             :a2, 4, 10

    section 복귀
    CRC Del + ACK + EOF                :a3, 10, 12
</pre><table><thead><tr><th>구간</th><th>포함 필드</th><th>속도</th></tr></thead><tbody><tr><td><strong>Arbitration phase</strong></td><td>SOF, ID, Control (FDF까지)</td><td>Nominal Bit Rate (통상 500 kbps)</td></tr><tr><td><strong>Data phase</strong></td><td>BRS 이후 ~ CRC</td><td>Data Bit Rate (2 ~ 8 Mbps)</td></tr></tbody></table><h2 id="brs-비트가-전환-신호" tabindex="-1"><a class="header-anchor" href="#brs-비트가-전환-신호"><span>BRS 비트가 전환 신호</span></a></h2><p><code>BRS=1</code>이면 BRS 비트 직후부터 Data phase 비트레이트로 전환된다. <code>BRS=0</code>이면 Data phase도 동일한 Nominal Bit Rate로 전송된다(속도 이점 없음).</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Arbitration phase  BRS  │  Data phase            │  EOF</span>
<span class="line">───────────────────[1]──┼──[고속 전송 구간]────────┼──[표준 복귀]</span>
<span class="line">500 kbps           ↑    │  2~8 Mbps               │  500 kbps</span>
<span class="line">                   전환 시점</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="실제-처리량-비교-예시" tabindex="-1"><a class="header-anchor" href="#실제-처리량-비교-예시"><span>실제 처리량 비교 예시</span></a></h2><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Classic CAN (8바이트, 1 Mbps):</span>
<span class="line">  유효 데이터 처리량 ≈ 8 byte / ~130 bit(프레임 오버헤드) ≈ 492 kbps</span>
<span class="line"></span>
<span class="line">CAN FD (64바이트, 4 Mbps Data phase):</span>
<span class="line">  Arbitration phase: ~80 bit @ 500 kbps = 160 µs</span>
<span class="line">  Data phase:        ~600 bit @ 4 Mbps  = 150 µs</span>
<span class="line">  총 전송 시간 ≈ 310 µs → 약 2 Mbps 유효 처리량</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h1 id="_4-can-2-0과의-호환성" tabindex="-1"><a class="header-anchor" href="#_4-can-2-0과의-호환성"><span>4. CAN 2.0과의 호환성</span></a></h1><h2 id="같은-버스에서-공존할-수-있는가" tabindex="-1"><a class="header-anchor" href="#같은-버스에서-공존할-수-있는가"><span>같은 버스에서 공존할 수 있는가?</span></a></h2><p>CAN FD 노드와 Classic CAN 노드는 <strong>버스를 물리적으로 공유</strong>할 수 있지만, 동작 방식에 따라 두 종류로 나뉜다.</p><pre class="mermaid">graph TD
    BUS[&quot;CAN 버스 (물리 계층 공유)&quot;]
    FD_ACTIVE[&quot;CAN FD Active 노드&lt;br&gt;CAN FD 프레임 송수신 가능&quot;]
    FD_TOLERANT[&quot;CAN FD Tolerant 노드&lt;br&gt;CAN FD 프레임을 무시(에러 없이 수신)&quot;]
    CLASSIC[&quot;Classic CAN 노드&lt;br&gt;CAN FD 프레임을 에러로 인식&quot;]

    BUS --- FD_ACTIVE
    BUS --- FD_TOLERANT
    BUS --- CLASSIC
</pre><table><thead><tr><th>노드 종류</th><th>CAN FD 프레임 수신</th><th>에러 발생</th></tr></thead><tbody><tr><td><strong>FD Active</strong></td><td>정상 처리</td><td>없음</td></tr><tr><td><strong>FD Tolerant</strong></td><td>무시(수신 후 폐기)</td><td>없음</td></tr><tr><td><strong>Classic CAN</strong></td><td>인식 불가</td><td>에러 프레임 발생</td></tr></tbody></table><blockquote><p>Classic CAN 노드가 같은 버스에 존재하면 CAN FD 프레임 전송 시 에러 프레임을 생성한다. 따라서 <strong>혼합 네트워크</strong>에서는 CAN FD를 사용하지 않거나, 게이트웨이로 분리해야 한다.</p></blockquote><h2 id="isobus와-can-fd" tabindex="-1"><a class="header-anchor" href="#isobus와-can-fd"><span>ISOBUS와 CAN FD</span></a></h2><p>현재 <strong>ISOBUS(ISO 11783)는 CAN 2.0B(29비트 확장 ID) 기반</strong>이다. 250 kbps의 비트레이트를 사용하며, CAN FD를 공식 채택하지 않았다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">현재 ISOBUS 스택</span>
<span class="line">  물리 계층: CAN 2.0B, 250 kbps</span>
<span class="line">  데이터 링크: ISO 11783-2 (버스 전기 특성 등)</span>
<span class="line">  상위 계층: ISO 11783-3~14</span>
<span class="line"></span>
<span class="line">CAN FD 채택 동향</span>
<span class="line">  - 농기계 데이터량 증가(정밀농업, 자율주행)로 수요 증가</span>
<span class="line">  - ISO TC23/SC19 WG1에서 CAN FD 확장 검토 중</span>
<span class="line">  - 일부 제조사는 자체 게이트웨이로 내부 CAN FD 망 구성</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN FD는 2012년 Bosch가 발표, <strong>64바이트 페이로드</strong>와 <strong>최대 8 Mbps Data phase</strong>가 핵심 개선점이다.</li><li><strong>FDF</strong> 비트로 CAN FD 프레임임을 표시하고, <strong>BRS</strong> 비트로 Data phase 고속 전환, <strong>ESI</strong> 비트로 에러 상태를 나타낸다.</li><li>Arbitration phase는 기존 속도(Nominal), Data phase만 고속(Data Bit Rate)으로 동작한다.</li><li>Classic CAN 노드가 혼재하면 CAN FD 프레임을 에러로 처리하므로 혼합 네트워크는 격리가 필요하다.</li><li>ISOBUS는 현재 CAN 2.0B 기반이며 CAN FD 채택은 진행 중이다.</li></ul></div><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/08-j1939-intro">SAE J1939 입문</a></li></ul>`,50))])}const D=r(u,[["render",b],["__file","07-can-fd.html.vue"]]),g=JSON.parse('{"path":"/study/isobus/07-can-fd.html","title":"CAN FD","lang":"en-US","frontmatter":{"title":"CAN FD","description":"CAN FD의 등장 배경, 프레임 구조, 듀얼 비트레이트 동작 원리, 그리고 Classic CAN과의 호환성을 학습한다.","date":"2026-04-13T00:00:00.000Z","tags":["isobus","can","can-fd","automotive"]},"headers":[{"level":1,"title":"1. CAN FD가 나온 이유","slug":"_1-can-fd가-나온-이유","link":"#_1-can-fd가-나온-이유","children":[{"level":2,"title":"기존 CAN의 한계","slug":"기존-can의-한계","link":"#기존-can의-한계","children":[]}]},{"level":1,"title":"2. CAN FD의 구조","slug":"_2-can-fd의-구조","link":"#_2-can-fd의-구조","children":[{"level":2,"title":"새로 추가된 제어 비트","slug":"새로-추가된-제어-비트","link":"#새로-추가된-제어-비트","children":[]},{"level":2,"title":"CAN FD 프레임 구조","slug":"can-fd-프레임-구조","link":"#can-fd-프레임-구조","children":[]},{"level":2,"title":"프레임 흐름 다이어그램","slug":"프레임-흐름-다이어그램","link":"#프레임-흐름-다이어그램","children":[]},{"level":2,"title":"최대 64바이트 페이로드","slug":"최대-64바이트-페이로드","link":"#최대-64바이트-페이로드","children":[]}]},{"level":1,"title":"3. 듀얼 비트레이트","slug":"_3-듀얼-비트레이트","link":"#_3-듀얼-비트레이트","children":[{"level":2,"title":"두 개의 Phase","slug":"두-개의-phase","link":"#두-개의-phase","children":[]},{"level":2,"title":"BRS 비트가 전환 신호","slug":"brs-비트가-전환-신호","link":"#brs-비트가-전환-신호","children":[]},{"level":2,"title":"실제 처리량 비교 예시","slug":"실제-처리량-비교-예시","link":"#실제-처리량-비교-예시","children":[]}]},{"level":1,"title":"4. CAN 2.0과의 호환성","slug":"_4-can-2-0과의-호환성","link":"#_4-can-2-0과의-호환성","children":[{"level":2,"title":"같은 버스에서 공존할 수 있는가?","slug":"같은-버스에서-공존할-수-있는가","link":"#같은-버스에서-공존할-수-있는가","children":[]},{"level":2,"title":"ISOBUS와 CAN FD","slug":"isobus와-can-fd","link":"#isobus와-can-fd","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/07-can-fd.md"}');export{D as comp,g as data};
