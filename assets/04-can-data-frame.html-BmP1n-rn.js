import{_ as r,c as o,a as e,b as n,d as u,f as d,r as i,o as p,e as a}from"./app-_YXo6X2Y.js";const c={},b={class:"table-of-contents"};function g(v,t){const l=i("Header"),s=i("router-link");return p(),o("div",null,[e(l),n("nav",b,[n("ul",null,[n("li",null,[e(s,{to:"#can-데이터-프레임"},{default:d(()=>t[0]||(t[0]=[a("CAN 데이터 프레임")])),_:1}),n("ul",null,[n("li",null,[e(s,{to:"#학습-목표"},{default:d(()=>t[1]||(t[1]=[a("학습 목표")])),_:1})]),n("li",null,[e(s,{to:"#_1-프레임의-종류"},{default:d(()=>t[2]||(t[2]=[a("1. 프레임의 종류")])),_:1})]),n("li",null,[e(s,{to:"#_2-데이터-프레임-필드-해부"},{default:d(()=>t[3]||(t[3]=[a("2. 데이터 프레임 필드 해부")])),_:1})]),n("li",null,[e(s,{to:"#_3-standard-11bit-vs-extended-29bit"},{default:d(()=>t[4]||(t[4]=[a("3. Standard(11bit) vs Extended(29bit)")])),_:1})]),n("li",null,[e(s,{to:"#_4-비트-스터핑-bit-stuffing"},{default:d(()=>t[5]||(t[5]=[a("4. 비트 스터핑(Bit Stuffing)")])),_:1})]),n("li",null,[e(s,{to:"#_5-dlc와-데이터-길이"},{default:d(()=>t[6]||(t[6]=[a("5. DLC와 데이터 길이")])),_:1})]),n("li",null,[e(s,{to:"#_6-프레임-읽기-실습"},{default:d(()=>t[7]||(t[7]=[a("6. 프레임 읽기 실습")])),_:1})]),n("li",null,[e(s,{to:"#다음-챕터"},{default:d(()=>t[8]||(t[8]=[a("다음 챕터")])),_:1})])])])])]),t[9]||(t[9]=u(`<h1 id="can-데이터-프레임" tabindex="-1"><a class="header-anchor" href="#can-데이터-프레임"><span>CAN 데이터 프레임</span></a></h1><h2 id="학습-목표" tabindex="-1"><a class="header-anchor" href="#학습-목표"><span>학습 목표</span></a></h2><ul><li>CAN 버스에서 사용하는 4가지 프레임 종류를 구분할 수 있다</li><li>데이터 프레임의 각 필드(SOF, ID, DLC, Data, CRC 등)의 역할을 설명할 수 있다</li><li>Standard(11bit)와 Extended(29bit) ID의 차이를 이해한다</li><li>비트 스터핑의 목적과 동작 방식을 설명할 수 있다</li><li>실제 CAN 로그를 보고 ID, DLC, Data를 직접 파싱할 수 있다</li></ul><hr><h2 id="_1-프레임의-종류" tabindex="-1"><a class="header-anchor" href="#_1-프레임의-종류"><span>1. 프레임의 종류</span></a></h2><p>CAN 버스 위를 오가는 메시지는 목적에 따라 4가지 종류로 나뉜다.</p><table><thead><tr><th>프레임 종류</th><th>역할</th></tr></thead><tbody><tr><td><strong>데이터 프레임 (Data Frame)</strong></td><td>실제 데이터를 전송하는 가장 일반적인 프레임</td></tr><tr><td><strong>리모트 프레임 (Remote Frame)</strong></td><td>다른 노드에게 특정 데이터를 보내달라고 요청하는 프레임</td></tr><tr><td><strong>에러 프레임 (Error Frame)</strong></td><td>오류를 감지한 노드가 버스 전체에 오류를 알리는 프레임</td></tr><tr><td><strong>오버로드 프레임 (Overload Frame)</strong></td><td>노드가 처리 준비가 안 됐을 때 다음 전송을 잠시 지연시키는 프레임</td></tr></tbody></table><p><strong>비유로 이해하기</strong></p><p>CAN 버스를 무전기 채널이라고 생각해보자.</p><ul><li><strong>데이터 프레임</strong>: &quot;본부, 현재 위치 좌표는 37.5°N, 127.0°E입니다.&quot; — 실제 정보 전달</li><li><strong>리모트 프레임</strong>: &quot;본부, 현재 온도 데이터 좀 보내줘요.&quot; — 데이터 요청</li><li><strong>에러 프레임</strong>: &quot;잠깐! 방금 전송에 오류가 있었습니다!&quot; — 오류 신호</li><li><strong>오버로드 프레임</strong>: &quot;저 지금 처리 중이에요, 잠깐만요.&quot; — 전송 지연 요청</li></ul><hr><h2 id="_2-데이터-프레임-필드-해부" tabindex="-1"><a class="header-anchor" href="#_2-데이터-프레임-필드-해부"><span>2. 데이터 프레임 필드 해부</span></a></h2><p>데이터 프레임은 여러 필드로 구성되며, 각각 정해진 역할이 있다.</p><pre class="mermaid">packet-beta
title CAN Standard Data Frame (2.0A)
0: &quot;SOF&quot;
1-11: &quot;Identifier (11bit)&quot;
12: &quot;RTR&quot;
13: &quot;IDE&quot;
14: &quot;r0&quot;
15-18: &quot;DLC (4bit)&quot;
19-82: &quot;Data (0~64bit)&quot;
83-97: &quot;CRC (15bit)&quot;
98: &quot;CRC Del&quot;
99: &quot;ACK Slot&quot;
100: &quot;ACK Del&quot;
101-107: &quot;EOF (7bit)&quot;
</pre><p>각 필드를 순서대로 살펴보자.</p><table><thead><tr><th>필드</th><th>크기</th><th>역할</th></tr></thead><tbody><tr><td><strong>SOF</strong> (Start of Frame)</td><td>1 bit</td><td>프레임 시작을 알리는 Dominant(0) 비트</td></tr><tr><td><strong>Identifier</strong></td><td>11 bit</td><td>메시지 식별자 겸 우선순위. 값이 낮을수록 높은 우선순위</td></tr><tr><td><strong>RTR</strong> (Remote Transmission Request)</td><td>1 bit</td><td>0=데이터 프레임, 1=리모트 프레임 구분</td></tr><tr><td><strong>IDE</strong> (Identifier Extension)</td><td>1 bit</td><td>0=Standard(11bit), 1=Extended(29bit) 구분</td></tr><tr><td><strong>r0</strong> (Reserved)</td><td>1 bit</td><td>예약된 비트, 항상 Dominant(0)</td></tr><tr><td><strong>DLC</strong> (Data Length Code)</td><td>4 bit</td><td>데이터 필드의 바이트 수 (0~8)</td></tr><tr><td><strong>Data</strong></td><td>0~64 bit</td><td>실제 전송 데이터 (0~8바이트)</td></tr><tr><td><strong>CRC</strong> (Cyclic Redundancy Check)</td><td>15 bit</td><td>전송 오류 검출을 위한 체크섬</td></tr><tr><td><strong>ACK</strong></td><td>2 bit</td><td>수신 노드의 정상 수신 확인 (ACK Slot + ACK Delimiter)</td></tr><tr><td><strong>EOF</strong> (End of Frame)</td><td>7 bit</td><td>프레임 종료를 알리는 7개의 Recessive(1) 비트</td></tr></tbody></table><blockquote><p>[!TIP] <strong>Dominant vs Recessive</strong>: CAN 버스에서 0을 Dominant, 1을 Recessive라 부른다. 여러 노드가 동시에 신호를 내보낼 때 Dominant(0)가 항상 이긴다. 전선을 당기는(0) 쪽이 안 당기는(1) 쪽을 이기는 것과 같다.</p></blockquote><hr><h2 id="_3-standard-11bit-vs-extended-29bit" tabindex="-1"><a class="header-anchor" href="#_3-standard-11bit-vs-extended-29bit"><span>3. Standard(11bit) vs Extended(29bit)</span></a></h2><p>CAN 2.0A는 11bit Identifier를, CAN 2.0B는 29bit Identifier를 사용한다. ISOBUS(ISO 11783)는 29bit Extended ID를 기반으로 한다.</p><pre class="mermaid">packet-beta
title CAN Extended Data Frame (2.0B) — 29bit ID
0: &quot;SOF&quot;
1-11: &quot;Base ID (11bit)&quot;
12: &quot;SRR&quot;
13: &quot;IDE=1&quot;
14-31: &quot;Extended ID (18bit)&quot;
32: &quot;RTR&quot;
33: &quot;r1&quot;
34: &quot;r0&quot;
35-38: &quot;DLC (4bit)&quot;
39-102: &quot;Data (0~64bit)&quot;
103-117: &quot;CRC (15bit)&quot;
118: &quot;CRC Del&quot;
119: &quot;ACK&quot;
120: &quot;ACK Del&quot;
121-127: &quot;EOF (7bit)&quot;
</pre><p><strong>Standard와 Extended의 차이</strong></p><table><thead><tr><th>항목</th><th>Standard (2.0A)</th><th>Extended (2.0B)</th></tr></thead><tbody><tr><td>Identifier 크기</td><td>11 bit</td><td>29 bit (11 + 18)</td></tr><tr><td>메시지 가짓수</td><td>2¹¹ = 2,048개</td><td>2²⁹ = 536,870,912개</td></tr><tr><td>IDE 비트</td><td>0</td><td>1</td></tr><tr><td>추가 필드</td><td>없음</td><td>SRR (Substitute Remote Request)</td></tr><tr><td>주요 용도</td><td>일반 CAN</td><td>ISOBUS, CANopen 등</td></tr></tbody></table><p>Extended 프레임에서 추가된 필드:</p><ul><li><strong>SRR</strong> (Substitute Remote Request): Standard 프레임의 RTR 위치에 들어가는 Recessive 비트. Extended 프레임에서 항상 1</li><li><strong>18bit Extension</strong>: Base ID(11bit) 뒤에 붙는 추가 18bit로 총 29bit ID를 구성</li></ul><hr><h2 id="_4-비트-스터핑-bit-stuffing" tabindex="-1"><a class="header-anchor" href="#_4-비트-스터핑-bit-stuffing"><span>4. 비트 스터핑(Bit Stuffing)</span></a></h2><p><strong>왜 필요한가?</strong></p><p>CAN은 클럭 신호 없이 데이터 신호만으로 통신한다. 수신 노드는 신호의 변화(0→1 또는 1→0)를 감지해 동기화를 유지한다. 그런데 같은 값이 너무 오래 연속되면 동기화 기준점을 잃어버릴 수 있다.</p><p><strong>동작 방식</strong></p><p>같은 값의 비트가 <strong>5개 연속</strong> 나타나면, 다음에 반드시 <strong>반대 값의 비트를 1개 삽입</strong>한다. 이 삽입된 비트를 <strong>Stuff Bit</strong>이라 한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">원본 비트열: 1 1 1 1 1 0 0 0 0 0 1</span>
<span class="line">                              ↑</span>
<span class="line">                   5개 연속 1 뒤에 0 삽입됨</span>
<span class="line"></span>
<span class="line">스터핑 후:  1 1 1 1 1 [0] 0 0 0 0 0 [1] 1</span>
<span class="line">                       ↑             ↑</span>
<span class="line">                   Stuff Bit      Stuff Bit</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>수신측 처리</strong>: 수신 노드는 5개 연속 비트 뒤에 오는 비트를 자동으로 제거(Destuffing)하여 원래 데이터를 복원한다.</p><blockquote><p>[!TIP] 비트 스터핑은 SOF부터 CRC 필드까지 적용된다. EOF와 ACK 필드에는 적용되지 않는다.</p></blockquote><hr><h2 id="_5-dlc와-데이터-길이" tabindex="-1"><a class="header-anchor" href="#_5-dlc와-데이터-길이"><span>5. DLC와 데이터 길이</span></a></h2><p>DLC(Data Length Code)는 4비트 필드로, 데이터 필드에 실제로 몇 바이트의 데이터가 있는지 알려준다.</p><table><thead><tr><th>DLC 값 (10진수)</th><th>데이터 바이트 수</th></tr></thead><tbody><tr><td>0</td><td>0 바이트</td></tr><tr><td>1</td><td>1 바이트</td></tr><tr><td>2</td><td>2 바이트</td></tr><tr><td>3</td><td>3 바이트</td></tr><tr><td>4</td><td>4 바이트</td></tr><tr><td>5</td><td>5 바이트</td></tr><tr><td>6</td><td>6 바이트</td></tr><tr><td>7</td><td>7 바이트</td></tr><tr><td>8</td><td>8 바이트</td></tr><tr><td>9~15</td><td>8 바이트 (표준 CAN에서는 8을 초과하지 않음)</td></tr></tbody></table><blockquote><p>[!INFO] CAN FD(Flexible Data Rate)에서는 DLC 9~15가 12, 16, 20, 24, 32, 48, 64 바이트에 매핑되어 최대 64바이트 전송이 가능하다. 그러나 일반 CAN과 ISOBUS에서는 최대 8바이트다.</p></blockquote><hr><h2 id="_6-프레임-읽기-실습" tabindex="-1"><a class="header-anchor" href="#_6-프레임-읽기-실습"><span>6. 프레임 읽기 실습</span></a></h2><p>실제 CAN 로그에서 자주 보이는 형식을 파싱해보자.</p><p><strong>로그 예시</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">0CF004FE#FF3C320000FFFF00</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><p>이 형식은 <code>[CAN ID]#[Data]</code> 구조다.</p><p><strong>파싱 과정</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">원본: 0CF004FE#FF3C320000FFFF00</span>
<span class="line">       ↓</span>
<span class="line">CAN ID: 0CF004FE (16진수 8자리 = 29bit Extended ID)</span>
<span class="line">Data  : FF 3C 32 00 00 FF FF 00</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>CAN ID 분해 (ISOBUS PGN 구조)</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">0C F0 04 FE  →  이진수로 변환</span>
<span class="line">= 0000 1100  1111 0000  0000 0100  1111 1110</span>
<span class="line"></span>
<span class="line">29bit ID (Extended):</span>
<span class="line">  Priority  : 000 (3bit)       → 우선순위 0</span>
<span class="line">  Reserved  : 0 (1bit)</span>
<span class="line">  Data Page : 0 (1bit)</span>
<span class="line">  PGN       : F004 (16진수)    → PGN = 61444 (EEC1, 엔진 속도)</span>
<span class="line">  Source Addr: FE (16진수)     → 소스 주소 254</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>Data 필드 해석</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Data (8바이트): FF 3C 32 00 00 FF FF 00</span>
<span class="line"></span>
<span class="line">DLC = 8 (데이터 8바이트)</span>
<span class="line"></span>
<span class="line">PGN F004 (EEC1) 기준 해석:</span>
<span class="line">  Byte 0 (FF): Engine Torque Mode — 0xFF = 데이터 없음</span>
<span class="line">  Byte 1 (3C): Driver&#39;s Demand Torque — 0x3C = 60 (offset -125 → -65%)</span>
<span class="line">  Byte 2 (32): Actual Engine Torque  — 0x32 = 50 (offset -125 → -75%)</span>
<span class="line">  Byte 3-4 (0000): Engine Speed      — 0x0000 = 0 RPM</span>
<span class="line">  Byte 5 (FF): Source Address — 0xFF = 데이터 없음</span>
<span class="line">  Byte 6 (FF): Engine Demand Torque — 0xFF = 데이터 없음</span>
<span class="line">  Byte 7 (00): Reserved</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><pre class="mermaid">flowchart LR
    A[&quot;CAN 로그\\n0CF004FE#FF3C320000FFFF00&quot;]
    A --&gt; B[&quot;CAN ID\\n0x0CF004FE&quot;]
    A --&gt; C[&quot;Data\\nFF 3C 32 00 00 FF FF 00&quot;]

    B --&gt; D[&quot;Priority: 3\\n(상위 3bit)&quot;]
    B --&gt; E[&quot;PGN: 0xF004\\n= EEC1 엔진 속도&quot;]
    B --&gt; F[&quot;Source: 0xFE\\n= 주소 254&quot;]

    C --&gt; G[&quot;Byte 0-1: 토크 정보&quot;]
    C --&gt; H[&quot;Byte 2-3: 엔진 RPM&quot;]
    C --&gt; I[&quot;Byte 4-7: 기타&quot;]
</pre><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN 프레임에는 데이터/리모트/에러/오버로드 4가지 종류가 있으며, 가장 많이 쓰이는 것은 <strong>데이터 프레임</strong>이다.</li><li>데이터 프레임은 SOF → ID → 제어 필드 → Data → CRC → ACK → EOF 순서로 구성된다.</li><li><strong>Standard(11bit)</strong> ID는 2,048개, <strong>Extended(29bit)</strong> ID는 5억 개 이상의 메시지를 구별할 수 있다. ISOBUS는 Extended를 사용한다.</li><li><strong>비트 스터핑</strong>은 5개 연속 동일 비트 뒤에 반대 비트를 삽입해 수신 노드의 동기화를 돕는다.</li><li><strong>DLC</strong> 0~8은 데이터 길이(바이트)와 1:1 대응한다.</li><li>CAN 로그 <code>ID#DATA</code> 형식에서 ID를 분해하면 PGN과 소스 주소를 알 수 있다.</li></ul></div><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li><strong>이전</strong>: <a href="/study/isobus/03-can-physical">03. CAN 물리 계층</a></li><li><strong>다음</strong>: <a href="/study/isobus/05-can-arbitration">05. CAN 중재와 우선순위</a></li></ul>`,56))])}const m=r(c,[["render",g],["__file","04-can-data-frame.html.vue"]]),C=JSON.parse('{"path":"/study/isobus/04-can-data-frame.html","title":"CAN 데이터 프레임","lang":"en-US","frontmatter":{"title":"CAN 데이터 프레임","description":"CAN 통신에서 데이터를 담는 그릇, 프레임의 구조와 각 필드의 역할을 이해한다","date":"2026-04-13T00:00:00.000Z","tags":["isobus","can","data-frame"]},"headers":[{"level":1,"title":"CAN 데이터 프레임","slug":"can-데이터-프레임","link":"#can-데이터-프레임","children":[{"level":2,"title":"학습 목표","slug":"학습-목표","link":"#학습-목표","children":[]},{"level":2,"title":"1. 프레임의 종류","slug":"_1-프레임의-종류","link":"#_1-프레임의-종류","children":[]},{"level":2,"title":"2. 데이터 프레임 필드 해부","slug":"_2-데이터-프레임-필드-해부","link":"#_2-데이터-프레임-필드-해부","children":[]},{"level":2,"title":"3. Standard(11bit) vs Extended(29bit)","slug":"_3-standard-11bit-vs-extended-29bit","link":"#_3-standard-11bit-vs-extended-29bit","children":[]},{"level":2,"title":"4. 비트 스터핑(Bit Stuffing)","slug":"_4-비트-스터핑-bit-stuffing","link":"#_4-비트-스터핑-bit-stuffing","children":[]},{"level":2,"title":"5. DLC와 데이터 길이","slug":"_5-dlc와-데이터-길이","link":"#_5-dlc와-데이터-길이","children":[]},{"level":2,"title":"6. 프레임 읽기 실습","slug":"_6-프레임-읽기-실습","link":"#_6-프레임-읽기-실습","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/04-can-data-frame.md"}');export{m as comp,C as data};
