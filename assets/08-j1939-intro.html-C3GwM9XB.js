import{_ as d,c as o,a as s,d as t,e as u,b as e,r as i,o as p,f as a}from"./app-C-zf-UQP.js";const c={},b={class:"table-of-contents"};function v(g,n){const r=i("Header"),l=i("router-link");return p(),o("div",null,[s(r),t("nav",b,[t("ul",null,[t("li",null,[s(l,{to:"#_1-왜-can만으로는-부족한가"},{default:e(()=>n[0]||(n[0]=[a("1. 왜 CAN만으로는 부족한가")])),_:1}),t("ul",null,[t("li",null,[s(l,{to:"#can은-데이터-전달만-담당한다"},{default:e(()=>n[1]||(n[1]=[a("CAN은 데이터 전달만 담당한다")])),_:1})]),t("li",null,[s(l,{to:"#택배-트럭과-물류-시스템-비유"},{default:e(()=>n[2]||(n[2]=[a("택배 트럭과 물류 시스템 비유")])),_:1})])])]),t("li",null,[s(l,{to:"#_2-상위-프로토콜-지도"},{default:e(()=>n[3]||(n[3]=[a("2. 상위 프로토콜 지도")])),_:1}),t("ul",null,[t("li",null,[s(l,{to:"#osi-7계층에서의-위치"},{default:e(()=>n[4]||(n[4]=[a("OSI 7계층에서의 위치")])),_:1})]),t("li",null,[s(l,{to:"#프로토콜별-적용-도메인"},{default:e(()=>n[5]||(n[5]=[a("프로토콜별 적용 도메인")])),_:1})])])]),t("li",null,[s(l,{to:"#_3-j1939이란"},{default:e(()=>n[6]||(n[6]=[a("3. J1939이란")])),_:1})]),t("li",null,[s(l,{to:"#_4-j1939과-can의-관계"},{default:e(()=>n[7]||(n[7]=[a("4. J1939과 CAN의 관계")])),_:1}),t("ul",null,[t("li",null,[s(l,{to:"#_29비트-can-id의-구조화"},{default:e(()=>n[8]||(n[8]=[a("29비트 CAN ID의 구조화")])),_:1})]),t("li",null,[s(l,{to:"#_29비트-id-예시-해석"},{default:e(()=>n[9]||(n[9]=[a("29비트 ID 예시 해석")])),_:1})])])]),t("li",null,[s(l,{to:"#_5-j1939-네트워크-구성"},{default:e(()=>n[10]||(n[10]=[a("5. J1939 네트워크 구성")])),_:1}),t("ul",null,[t("li",null,[s(l,{to:"#소스-어드레스-sa-할당"},{default:e(()=>n[11]||(n[11]=[a("소스 어드레스(SA) 할당")])),_:1})]),t("li",null,[s(l,{to:"#네트워크-토폴로지-예시"},{default:e(()=>n[12]||(n[12]=[a("네트워크 토폴로지 예시")])),_:1})]),t("li",null,[s(l,{to:"#j1939-통신-흐름-예시"},{default:e(()=>n[13]||(n[13]=[a("J1939 통신 흐름 예시")])),_:1})]),t("li",null,[s(l,{to:"#다음-챕터"},{default:e(()=>n[14]||(n[14]=[a("다음 챕터")])),_:1})])])])])]),n[15]||(n[15]=u(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN만으로 부족한 이유를 상위 프로토콜의 필요성과 연결해서 설명할 수 있다.</li><li>CANopen, DeviceNet, J1939, ISOBUS의 위치와 차이를 구분할 수 있다.</li><li>J1939의 29비트 CAN ID 구조(Priority, EDP, DP, PF, PS, SA)를 해석할 수 있다.</li><li>J1939 네트워크에서 소스 어드레스(SA)의 역할을 이해한다.</li></ul></div><hr><h1 id="_1-왜-can만으로는-부족한가" tabindex="-1"><a class="header-anchor" href="#_1-왜-can만으로는-부족한가"><span>1. 왜 CAN만으로는 부족한가</span></a></h1><h2 id="can은-데이터-전달만-담당한다" tabindex="-1"><a class="header-anchor" href="#can은-데이터-전달만-담당한다"><span>CAN은 데이터 전달만 담당한다</span></a></h2><p>CAN 프로토콜은 물리 계층과 데이터 링크 계층만 정의한다. 메시지를 버스에 올리고 내리는 것, 에러를 감지하는 것 — 여기까지가 CAN이 하는 일이다.</p><p>다음 기능들은 CAN 규격 어디에도 없다.</p><table><thead><tr><th>필요 기능</th><th>CAN 2.0 지원 여부</th></tr></thead><tbody><tr><td>노드별 고유 주소 관리</td><td>없음 (29비트 ID를 자유롭게 사용)</td></tr><tr><td>메시지 의미 해석 (온도, 압력 등)</td><td>없음</td></tr><tr><td>8바이트 초과 데이터 전송 프로토콜</td><td>없음</td></tr><tr><td>네트워크 진단 / 장치 검색</td><td>없음</td></tr><tr><td>타임아웃, 재전송 정책</td><td>없음</td></tr></tbody></table><h2 id="택배-트럭과-물류-시스템-비유" tabindex="-1"><a class="header-anchor" href="#택배-트럭과-물류-시스템-비유"><span>택배 트럭과 물류 시스템 비유</span></a></h2><blockquote><p>&quot;CAN은 택배 트럭이고, J1939은 물류 시스템이다.&quot;</p></blockquote><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">CAN (택배 트럭)</span>
<span class="line">  - 소포를 버스에서 목적지까지 운반</span>
<span class="line">  - 어떤 소포인지, 배송 순서, 반품 정책은 모름</span>
<span class="line"></span>
<span class="line">J1939 (물류 시스템)</span>
<span class="line">  - 소포에 송장(PGN/SPN) 붙이기</span>
<span class="line">  - 발송지(SA)/수신지(DA) 주소 관리</span>
<span class="line">  - 큰 짐을 여러 소포로 나누는 규칙(Transport Protocol)</span>
<span class="line">  - 배송 실패 처리, 재전송 정책</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>CAN 위에 상위 프로토콜을 올려야 비로소 실용적인 차량 네트워크가 완성된다.</p><hr><h1 id="_2-상위-프로토콜-지도" tabindex="-1"><a class="header-anchor" href="#_2-상위-프로토콜-지도"><span>2. 상위 프로토콜 지도</span></a></h1><h2 id="osi-7계층에서의-위치" tabindex="-1"><a class="header-anchor" href="#osi-7계층에서의-위치"><span>OSI 7계층에서의 위치</span></a></h2><p>CAN 기반 상위 프로토콜은 모두 OSI 모델의 3계층 이상을 담당한다.</p><pre class="mermaid">block-beta
  columns 3

  block:osi[&quot;OSI 7계층&quot;]:1
    L7[&quot;7. Application&quot;]
    L6[&quot;6. Presentation&quot;]
    L5[&quot;5. Session&quot;]
    L4[&quot;4. Transport&quot;]
    L3[&quot;3. Network&quot;]
    L2[&quot;2. Data Link&quot;]
    L1[&quot;1. Physical&quot;]
  end

  block:proto[&quot;프로토콜 스택&quot;]:2
    block:upper[&quot;상위 프로토콜 (3~7계층)&quot;]
      columns 2
      CANopen[&quot;CANopen&lt;br&gt;산업 자동화&quot;]
      DeviceNet[&quot;DeviceNet&lt;br&gt;공장 자동화&quot;]
      J1939[&quot;SAE J1939&lt;br&gt;대형 차량·농기계&quot;]
      ISOBUS[&quot;ISOBUS&lt;br&gt;(ISO 11783)&lt;br&gt;농기계 전용&quot;]
    end
    block:lower[&quot;하위 계층 (1~2계층)&quot;]
      columns 1
      CAN[&quot;CAN 2.0B&lt;br&gt;(데이터 링크 + 물리)&quot;]
    end
  end
</pre><h2 id="프로토콜별-적용-도메인" tabindex="-1"><a class="header-anchor" href="#프로토콜별-적용-도메인"><span>프로토콜별 적용 도메인</span></a></h2><pre class="mermaid">graph LR
    CAN[&quot;CAN 물리·링크 계층&quot;]
    CANopen[&quot;CANopen&lt;br&gt;산업 자동화&lt;br&gt;(PLC, 모터 제어)&quot;]
    DeviceNet[&quot;DeviceNet&lt;br&gt;공장 자동화&lt;br&gt;(센서, 액추에이터 네트워크)&quot;]
    J1939[&quot;SAE J1939&lt;br&gt;대형 차량·농기계&lt;br&gt;(트럭, 버스, 굴착기)&quot;]
    ISOBUS[&quot;ISOBUS (ISO 11783)&lt;br&gt;농기계 전용&lt;br&gt;(트랙터-작업기 통신)&quot;]

    CAN --&gt; CANopen
    CAN --&gt; DeviceNet
    CAN --&gt; J1939
    J1939 --&gt; ISOBUS
</pre><blockquote><p>ISOBUS는 J1939을 기반으로 농기계 도메인에 특화한 확장 프로토콜이다. J1939을 이해하면 ISOBUS의 절반은 이해한 것이다.</p></blockquote><hr><h1 id="_3-j1939이란" tabindex="-1"><a class="header-anchor" href="#_3-j1939이란"><span>3. J1939이란</span></a></h1><p>SAE(Society of Automotive Engineers)가 정의한 <strong>대형 차량 및 작업 기계용 통신 상위 프로토콜</strong>이다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">표준명: SAE J1939</span>
<span class="line">관리 기관: SAE International</span>
<span class="line">기반 CAN: CAN 2.0B (29비트 확장 ID)</span>
<span class="line">비트레이트: 250 kbps (표준) / 500 kbps (옵션)</span>
<span class="line">주요 적용: 트럭, 버스, 굴착기, 트랙터, 농기계</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>J1939이 정의하는 것들:</p><ul><li><strong>PGN (Parameter Group Number)</strong>: 메시지 종류 식별자</li><li><strong>SPN (Suspect Parameter Number)</strong>: 데이터 필드 내 개별 파라미터 식별자</li><li><strong>소스/목적지 주소 관리</strong></li><li><strong>Transport Protocol</strong>: 8바이트 초과 데이터를 여러 프레임으로 분할 전송</li><li><strong>네트워크 관리</strong>: 주소 요청, 주소 충돌 감지</li></ul><hr><h1 id="_4-j1939과-can의-관계" tabindex="-1"><a class="header-anchor" href="#_4-j1939과-can의-관계"><span>4. J1939과 CAN의 관계</span></a></h1><h2 id="_29비트-can-id의-구조화" tabindex="-1"><a class="header-anchor" href="#_29비트-can-id의-구조화"><span>29비트 CAN ID의 구조화</span></a></h2><p>Classic CAN 2.0B는 29비트 확장 ID를 제공하지만, 이 ID를 어떻게 쓸지는 규정하지 않는다. J1939은 이 29비트를 다음과 같이 <strong>명확한 필드로 구조화</strong>한다.</p><pre class="mermaid">packet-beta
  0-2: &quot;Priority (3 bit)&quot;
  3-3: &quot;EDP (1 bit)&quot;
  4-4: &quot;DP (1 bit)&quot;
  5-12: &quot;PF: PDU Format (8 bit)&quot;
  13-20: &quot;PS: PDU Specific (8 bit)&quot;
  21-28: &quot;SA: Source Address (8 bit)&quot;
</pre><table><thead><tr><th>필드</th><th>비트 수</th><th>설명</th></tr></thead><tbody><tr><td><strong>Priority</strong></td><td>3</td><td>메시지 우선순위. 0이 최고, 7이 최저</td></tr><tr><td><strong>EDP</strong></td><td>1</td><td>Extended Data Page. J1939에서는 보통 0</td></tr><tr><td><strong>DP</strong></td><td>1</td><td>Data Page. PGN 공간을 두 배로 확장</td></tr><tr><td><strong>PF</strong></td><td>8</td><td>PDU Format. 메시지 유형 결정 (PDU1 vs PDU2 구분)</td></tr><tr><td><strong>PS</strong></td><td>8</td><td>PDU Specific. PF &lt; 240이면 목적지 주소, PF &gt;= 240이면 그룹 확장</td></tr><tr><td><strong>SA</strong></td><td>8</td><td>Source Address. 메시지를 보내는 노드의 주소 (0x00~0xFD)</td></tr></tbody></table><h2 id="_29비트-id-예시-해석" tabindex="-1"><a class="header-anchor" href="#_29비트-id-예시-해석"><span>29비트 ID 예시 해석</span></a></h2><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">CAN 29비트 ID: 0x18FEE000</span>
<span class="line"></span>
<span class="line">바이너리: 000 1 1000 1111 1110 1110 0000 0000</span>
<span class="line"></span>
<span class="line">분해:</span>
<span class="line">  Priority : 000   = 0 (최고 우선순위)</span>
<span class="line">  EDP      : 1     = 0 (EDP 비트, 실제로 CAN 확장 ID의 비트 28)</span>
<span class="line">  DP       : 1     = 0</span>
<span class="line">  PF       : 1111 1110 = 0xFE = 254 → PDU2 (브로드캐스트)</span>
<span class="line">  PS       : 1110 0000 = 0xE0 = 224 → Group Extension</span>
<span class="line">  SA       : 0000 0000 = 0x00 → 엔진 ECU</span>
<span class="line"></span>
<span class="line">※ 실제 CAN ID 0x18FEE000 분해 (hex → 29bit):</span>
<span class="line">  18FEE000 hex = 0001 1000 1111 1110 1110 0000 0000 0000 (32bit)</span>
<span class="line">  하위 29비트만 사용:  000 1 1000 1111 1110 1110 0000 0000 0000 (29bit)</span>
<span class="line">  Priority=6, EDP=0, DP=0, PF=0xFE=254, PS=0xE0=224, SA=0x00</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>29비트 ID의 구조를 이해했으니, 이제 이 ID 체계 위에서 실제 J1939 네트워크가 어떻게 구성되는지 살펴보자.</p><hr><h1 id="_5-j1939-네트워크-구성" tabindex="-1"><a class="header-anchor" href="#_5-j1939-네트워크-구성"><span>5. J1939 네트워크 구성</span></a></h1><h2 id="소스-어드레스-sa-할당" tabindex="-1"><a class="header-anchor" href="#소스-어드레스-sa-할당"><span>소스 어드레스(SA) 할당</span></a></h2><p>J1939은 노드마다 <strong>고유한 소스 어드레스(SA)</strong>를 부여한다. SAE J1939-81(네트워크 관리) 규격이 주소 요청/충돌 감지 절차를 정의한다.</p><p>예약된 주소 예시:</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">SA 0x00 (0)   : Engine #1</span>
<span class="line">SA 0x03 (3)   : Transmission #1</span>
<span class="line">SA 0x17 (23)  : Instrument Cluster #1</span>
<span class="line">SA 0x28 (40)  : Cab Controller</span>
<span class="line">SA 0xF9 (249) : Diagnostic Tool (오프보드)</span>
<span class="line">SA 0xFE (254) : Null Address (아직 주소 없음)</span>
<span class="line">SA 0xFF (255) : Global (브로드캐스트 목적지)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="네트워크-토폴로지-예시" tabindex="-1"><a class="header-anchor" href="#네트워크-토폴로지-예시"><span>네트워크 토폴로지 예시</span></a></h2><pre class="mermaid">graph LR
    TERM1[&quot;종단 저항&lt;br&gt;120Ω&quot;]
    ECU_ENG[&quot;엔진 ECU&lt;br&gt;SA=0x00&quot;]
    ECU_TRANS[&quot;변속기 ECU&lt;br&gt;SA=0x03&quot;]
    ECU_DASH[&quot;계기판&lt;br&gt;SA=0x17&quot;]
    ECU_CAB[&quot;캡 컨트롤러&lt;br&gt;SA=0x28&quot;]
    DIAG[&quot;진단 도구&lt;br&gt;SA=0xF9&quot;]
    TERM2[&quot;종단 저항&lt;br&gt;120Ω&quot;]

    TERM1 --- ECU_ENG
    ECU_ENG --- ECU_TRANS
    ECU_TRANS --- ECU_DASH
    ECU_DASH --- ECU_CAB
    ECU_CAB --- DIAG
    DIAG --- TERM2
</pre><blockquote><p>J1939 버스는 단일 버스 토폴로지(daisy-chain 또는 stub 방식)로 구성하며, 양 끝에 120Ω 종단 저항을 달아야 한다. ISOBUS도 동일한 물리 구성을 따른다.</p></blockquote><h2 id="j1939-통신-흐름-예시" tabindex="-1"><a class="header-anchor" href="#j1939-통신-흐름-예시"><span>J1939 통신 흐름 예시</span></a></h2><pre class="mermaid">sequenceDiagram
    participant ENG as 엔진 ECU (SA=0x00)
    participant BUS as J1939 버스
    participant DASH as 계기판 (SA=0x17)
    participant DIAG as 진단 도구 (SA=0xF9)

    ENG-&gt;&gt;BUS: PGN 65262 (Engine Temp, SA=0x00, 브로드캐스트)
    BUS--&gt;&gt;DASH: 수신 → 수온 게이지 표시
    BUS--&gt;&gt;DIAG: 수신 → 로그 기록

    DIAG-&gt;&gt;BUS: PGN 59904 (Request PGN, DA=0x00, SA=0xF9)
    BUS--&gt;&gt;ENG: 요청 수신 → PGN 65262 응답

    ENG-&gt;&gt;BUS: PGN 65262 응답 (SA=0x00)
    BUS--&gt;&gt;DIAG: 수신
</pre><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN은 물리·링크 계층만 담당하므로 주소 관리, 메시지 의미, 대용량 전송은 상위 프로토콜이 필요하다.</li><li>CANopen(산업), DeviceNet(공장), J1939(대형 차량·농기계), ISOBUS(농기계 전용) 모두 CAN 위에 올라가는 상위 프로토콜이다.</li><li>J1939은 CAN 2.0B의 <strong>29비트 ID</strong>를 Priority + EDP + DP + PF + PS + SA 필드로 구조화한다.</li><li><strong>SA(Source Address)</strong>로 버스 내 노드를 구분하며, 0x00~0xFD가 일반 노드에 할당된다.</li><li>ISOBUS는 J1939을 농기계 도메인에 맞게 확장한 프로토콜이다.</li></ul></div><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/09-j1939-message">J1939 메시지 구조</a></li></ul>`,49))])}const A=d(c,[["render",v],["__file","08-j1939-intro.html.vue"]]),S=JSON.parse('{"path":"/study/isobus/08-j1939-intro.html","title":"SAE J1939 입문","lang":"en-US","frontmatter":{"title":"SAE J1939 입문","description":"CAN만으로는 부족한 이유, 상위 프로토콜의 역할, SAE J1939의 구조와 29비트 ID 구성을 학습한다.","date":"2026-04-13T00:00:00.000Z","tags":["isobus","j1939","can","sae","protocol"]},"headers":[{"level":1,"title":"1. 왜 CAN만으로는 부족한가","slug":"_1-왜-can만으로는-부족한가","link":"#_1-왜-can만으로는-부족한가","children":[{"level":2,"title":"CAN은 데이터 전달만 담당한다","slug":"can은-데이터-전달만-담당한다","link":"#can은-데이터-전달만-담당한다","children":[]},{"level":2,"title":"택배 트럭과 물류 시스템 비유","slug":"택배-트럭과-물류-시스템-비유","link":"#택배-트럭과-물류-시스템-비유","children":[]}]},{"level":1,"title":"2. 상위 프로토콜 지도","slug":"_2-상위-프로토콜-지도","link":"#_2-상위-프로토콜-지도","children":[{"level":2,"title":"OSI 7계층에서의 위치","slug":"osi-7계층에서의-위치","link":"#osi-7계층에서의-위치","children":[]},{"level":2,"title":"프로토콜별 적용 도메인","slug":"프로토콜별-적용-도메인","link":"#프로토콜별-적용-도메인","children":[]}]},{"level":1,"title":"3. J1939이란","slug":"_3-j1939이란","link":"#_3-j1939이란","children":[]},{"level":1,"title":"4. J1939과 CAN의 관계","slug":"_4-j1939과-can의-관계","link":"#_4-j1939과-can의-관계","children":[{"level":2,"title":"29비트 CAN ID의 구조화","slug":"_29비트-can-id의-구조화","link":"#_29비트-can-id의-구조화","children":[]},{"level":2,"title":"29비트 ID 예시 해석","slug":"_29비트-id-예시-해석","link":"#_29비트-id-예시-해석","children":[]}]},{"level":1,"title":"5. J1939 네트워크 구성","slug":"_5-j1939-네트워크-구성","link":"#_5-j1939-네트워크-구성","children":[{"level":2,"title":"소스 어드레스(SA) 할당","slug":"소스-어드레스-sa-할당","link":"#소스-어드레스-sa-할당","children":[]},{"level":2,"title":"네트워크 토폴로지 예시","slug":"네트워크-토폴로지-예시","link":"#네트워크-토폴로지-예시","children":[]},{"level":2,"title":"J1939 통신 흐름 예시","slug":"j1939-통신-흐름-예시","link":"#j1939-통신-흐름-예시","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/08-j1939-intro.md"}');export{A as comp,S as data};
