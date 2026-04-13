import{_ as e,c as d,d as r,o as D}from"./app-BSj_EDeZ.js";const l={};function n(o,t){return D(),d("div",null,t[0]||(t[0]=[r(`<h1 id="tc-디바이스-디스크립션-ddop" tabindex="-1"><a class="header-anchor" href="#tc-디바이스-디스크립션-ddop"><span>TC 디바이스 디스크립션 (DDOP)</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>DDOP가 무엇이고 왜 필요한지 설명할 수 있다.</li><li>DDOP를 구성하는 5가지 오브젝트 타입의 역할을 구분할 수 있다.</li><li>DDOP 전송 과정을 시퀀스 다이어그램으로 그릴 수 있다.</li><li>3구획 살포기의 DDOP를 직접 설계하고 오브젝트 표를 작성할 수 있다.</li></ul></div><hr><h2 id="_1-ddop란" tabindex="-1"><a class="header-anchor" href="#_1-ddop란"><span>1. DDOP란</span></a></h2><p><strong>DDOP(Device Description Object Pool)</strong>는 작업기가 자기 자신의 구조와 능력을 TC에게 알려주는 데이터 집합이다.</p><blockquote><p>DDOP는 &quot;작업기의 자기소개서&quot;이다.</p></blockquote><p>TC-Server는 버스에 연결된 작업기에 대해 아무런 사전 정보가 없다. 작업기가 어떤 구획(Section)을 가졌는지, 어떤 DDI를 지원하는지, 작업폭이 얼마인지를 TC는 알 수 없다. DDOP는 이 정보를 구조화된 형식으로 TC에 전달하여, TC가 작업기를 이해하고 제어할 수 있게 한다.</p><p><strong>DDOP가 없다면:</strong></p><ul><li>TC는 작업기에 어떤 명령을 보낼 수 있는지 모른다.</li><li>처방 맵의 살포량을 어느 DDI로 전달해야 하는지 알 수 없다.</li><li>Section Control을 위해 몇 개의 구획이 있는지 파악하지 못한다.</li></ul><p><strong>DDOP가 있다면:</strong></p><ul><li>TC는 작업기의 구조를 파악하고 적절한 명령을 선택한다.</li><li>지원되지 않는 DDI로의 명령 시도를 사전에 방지한다.</li></ul><hr><h2 id="_2-ddop-오브젝트-구조" tabindex="-1"><a class="header-anchor" href="#_2-ddop-오브젝트-구조"><span>2. DDOP 오브젝트 구조</span></a></h2><p>DDOP는 5가지 타입의 오브젝트로 구성된다.</p><table><thead><tr><th>오브젝트 타입</th><th>역할</th><th>주요 속성</th></tr></thead><tbody><tr><td><strong>Device</strong></td><td>장치 전체 정보 (최상위)</td><td>제조사, 제품명, 시리얼번호, Structure Label</td></tr><tr><td><strong>DeviceElement</strong></td><td>장치의 논리적 구성 요소</td><td>Element Type, Element Number, 부모 Element</td></tr><tr><td><strong>DeviceProcessData</strong></td><td>지원하는 프로세스 데이터 항목</td><td>DDI, Property Flag (Setpoint/Measurement), Trigger Methods</td></tr><tr><td><strong>DeviceProperty</strong></td><td>고정 속성값</td><td>DDI, 값 (작업폭, 구획 폭 등)</td></tr><tr><td><strong>DeviceValuePresentation</strong></td><td>데이터 표현 방식</td><td>오프셋, 스케일, 단위 기호</td></tr></tbody></table><pre class="mermaid">graph TD
    DVC[&quot;Device&lt;br&gt;살포기 전체&lt;br&gt;제조사/모델/S/N&quot;]

    DE_ROOT[&quot;DeviceElement&lt;br&gt;Type=Device&lt;br&gt;(전체 기능 루트)&quot;]
    DE_SEC1[&quot;DeviceElement&lt;br&gt;Type=Section&lt;br&gt;Section 1 (3m)&quot;]
    DE_SEC2[&quot;DeviceElement&lt;br&gt;Type=Section&lt;br&gt;Section 2 (3m)&quot;]
    DE_SEC3[&quot;DeviceElement&lt;br&gt;Type=Section&lt;br&gt;Section 3 (3m)&quot;]

    DPD_SP[&quot;DeviceProcessData&lt;br&gt;DDI=1&lt;br&gt;Setpoint Volume/Area&quot;]
    DPD_MS[&quot;DeviceProcessData&lt;br&gt;DDI=2&lt;br&gt;Actual Volume/Area&quot;]

    DPROP[&quot;DeviceProperty&lt;br&gt;DDI=작업폭&lt;br&gt;Value=9m&quot;]

    DVP[&quot;DeviceValuePresentation&lt;br&gt;Unit=L/ha&lt;br&gt;Scale=0.01&quot;]

    DVC --&gt; DE_ROOT
    DE_ROOT --&gt; DE_SEC1
    DE_ROOT --&gt; DE_SEC2
    DE_ROOT --&gt; DE_SEC3
    DE_SEC1 --&gt; DPD_SP
    DE_SEC1 --&gt; DPD_MS
    DE_ROOT --&gt; DPROP
    DPD_SP --&gt; DVP
    DPD_MS --&gt; DVP
</pre><h3 id="오브젝트-타입-상세" tabindex="-1"><a class="header-anchor" href="#오브젝트-타입-상세"><span>오브젝트 타입 상세</span></a></h3><p><strong>Device</strong></p><ul><li>DDOP 전체의 루트 오브젝트이다.</li><li><code>Structure Label</code>: DDOP 버전을 나타내는 식별자이다. TC는 이 라벨을 보고 DDOP를 새로 받을지 캐시된 것을 쓸지 결정한다.</li><li><code>Localization Label</code>: 언어·단위 설정</li></ul><p><strong>DeviceElement</strong></p><ul><li>작업기의 논리적 부품이다. Element Type으로 역할을 정의한다.</li><li><code>Device</code>: 장치 전체를 대표하는 Element</li><li><code>Function</code>: 살포 펌프, 파종 유닛 등 기능 단위</li><li><code>Section</code>: 독립 제어 가능한 구획</li><li><code>Bin</code>: 씨앗·비료 저장 용기</li><li><code>Connector</code>: 히치 연결점</li></ul><p><strong>DeviceProcessData</strong></p><ul><li>DeviceElement에 연결되며, 해당 Element에서 지원하는 DDI 항목을 정의한다.</li><li><code>Property Flag</code>: Setpoint 지원 여부, Measurement 지원 여부, Default 값 설정 가능 여부</li><li><code>Trigger Methods</code>: 값 보고 트리거 (시간 기반, 변화량 기반, 요청 기반)</li></ul><p><strong>DeviceProperty</strong></p><ul><li>변하지 않는 고정 속성이다. 작업폭, 구획 폭 등이 여기에 해당한다.</li><li>DeviceProcessData와 달리 TC가 값을 변경하지 않다.</li></ul><p><strong>DeviceValuePresentation</strong></p><ul><li>숫자값을 사람이 읽기 쉬운 형식으로 변환하는 규칙이다.</li><li>공식: <code>표시값 = (원시값 + Offset) × Scale</code></li><li>예: 원시값 20000, Offset=0, Scale=0.01 → 표시값 200.00 L/ha</li></ul><hr><h2 id="_3-ddop-전송-과정" tabindex="-1"><a class="header-anchor" href="#_3-ddop-전송-과정"><span>3. DDOP 전송 과정</span></a></h2><p>작업기가 ISOBUS 네트워크에 연결되면 다음 순서로 DDOP를 전송한다.</p><pre class="mermaid">sequenceDiagram
    participant CLIENT as TC-Client&lt;br&gt;(작업기 ECU)
    participant TC as TC-Server

    Note over CLIENT,TC: 네트워크 연결 및 주소 클레임 완료

    CLIENT -&gt;&gt; TC: Working Set Master 메시지&lt;br&gt;(버스 참여 알림)

    TC -&gt;&gt; CLIENT: Request Structure Label&lt;br&gt;(DDOP 버전 확인)

    CLIENT --&gt;&gt; TC: Structure Label 응답&lt;br&gt;(예: &quot;SPRAY-V2.1-20240101&quot;)

    alt DDOP가 캐시에 없거나 버전이 다름
        TC -&gt;&gt; CLIENT: Request Object Pool Transfer&lt;br&gt;(DDOP 요청)
        CLIENT --&gt;&gt; TC: Object Pool Transfer 시작&lt;br&gt;(Transport Protocol 사용)
        CLIENT --&gt;&gt; TC: DDOP 데이터 전송 (멀티패킷)
        CLIENT --&gt;&gt; TC: Object Pool Transfer 종료
        TC --&gt;&gt; CLIENT: Object Pool Transfer Response&lt;br&gt;(성공/실패)
    else DDOP가 캐시에 있음
        Note over TC: 캐시된 DDOP 사용
    end

    TC -&gt;&gt; CLIENT: Object Pool Activate&lt;br&gt;(DDOP 활성화 요청)
    CLIENT --&gt;&gt; TC: Object Pool Activate Response&lt;br&gt;(활성화 완료)

    Note over TC,CLIENT: Task 수행 준비 완료
</pre><h3 id="전송-프로토콜" tabindex="-1"><a class="header-anchor" href="#전송-프로토콜"><span>전송 프로토콜</span></a></h3><p>DDOP 데이터는 일반적으로 수백 바이트~수 킬로바이트에 달하므로, 단일 CAN 프레임으로 전송할 수 없다. ISO 11783의 <strong>TP(Transport Protocol)</strong> 또는 <strong>ETP(Extended Transport Protocol)</strong>를 사용하여 멀티패킷으로 분할 전송한다.</p><hr><h2 id="_4-ddop-설계-예제" tabindex="-1"><a class="header-anchor" href="#_4-ddop-설계-예제"><span>4. DDOP 설계 예제</span></a></h2><h3 id="대상-3구획-붐-스프레이어" tabindex="-1"><a class="header-anchor" href="#대상-3구획-붐-스프레이어"><span>대상: 3구획 붐 스프레이어</span></a></h3><ul><li>총 작업폭: 9m (3구획 × 3m)</li><li>지원 기능: Section Control(구획별 ON/OFF), Rate Control(살포량 가변)</li><li>지원 DDI: DDI 1(Setpoint Volume/Area), DDI 2(Actual Volume/Area), DDI 141(Section Control State)</li></ul><h3 id="ddop-계층-구조" tabindex="-1"><a class="header-anchor" href="#ddop-계층-구조"><span>DDOP 계층 구조</span></a></h3><pre class="mermaid">graph TD
    DVC[&quot;Device&lt;br&gt;오브젝트 ID: 1&lt;br&gt;3구획 붐 스프레이어&quot;]

    DE0[&quot;DeviceElement&lt;br&gt;ID: 2, Type: Device&lt;br&gt;Element Number: 0&lt;br&gt;전체 기능 루트&quot;]

    DE1[&quot;DeviceElement&lt;br&gt;ID: 3, Type: Section&lt;br&gt;Element Number: 1&lt;br&gt;Section 1 (좌, 3m)&quot;]

    DE2[&quot;DeviceElement&lt;br&gt;ID: 4, Type: Section&lt;br&gt;Element Number: 2&lt;br&gt;Section 2 (중, 3m)&quot;]

    DE3[&quot;DeviceElement&lt;br&gt;ID: 5, Type: Section&lt;br&gt;Element Number: 3&lt;br&gt;Section 3 (우, 3m)&quot;]

    PROP[&quot;DeviceProperty&lt;br&gt;ID: 6&lt;br&gt;작업폭 = 9m&quot;]

    DPD_SP1[&quot;DeviceProcessData&lt;br&gt;ID: 7&lt;br&gt;DDI=1 Setpoint&lt;br&gt;(Section 1)&quot;]
    DPD_MS1[&quot;DeviceProcessData&lt;br&gt;ID: 8&lt;br&gt;DDI=2 Measurement&lt;br&gt;(Section 1)&quot;]
    DPD_SC1[&quot;DeviceProcessData&lt;br&gt;ID: 9&lt;br&gt;DDI=141 SectionCtrl&lt;br&gt;(Section 1)&quot;]

    DPD_SP2[&quot;DeviceProcessData&lt;br&gt;ID: 10&lt;br&gt;DDI=1 Setpoint&lt;br&gt;(Section 2)&quot;]
    DPD_MS2[&quot;DeviceProcessData&lt;br&gt;ID: 11&lt;br&gt;DDI=2 Measurement&lt;br&gt;(Section 2)&quot;]
    DPD_SC2[&quot;DeviceProcessData&lt;br&gt;ID: 12&lt;br&gt;DDI=141 SectionCtrl&lt;br&gt;(Section 2)&quot;]

    DPD_SP3[&quot;DeviceProcessData&lt;br&gt;ID: 13&lt;br&gt;DDI=1 Setpoint&lt;br&gt;(Section 3)&quot;]
    DPD_MS3[&quot;DeviceProcessData&lt;br&gt;ID: 14&lt;br&gt;DDI=2 Measurement&lt;br&gt;(Section 3)&quot;]
    DPD_SC3[&quot;DeviceProcessData&lt;br&gt;ID: 15&lt;br&gt;DDI=141 SectionCtrl&lt;br&gt;(Section 3)&quot;]

    DVP[&quot;DeviceValuePresentation&lt;br&gt;ID: 16&lt;br&gt;Unit=L/ha, Scale=0.01&quot;]

    DVC --&gt; DE0
    DE0 --&gt; DE1
    DE0 --&gt; DE2
    DE0 --&gt; DE3
    DE0 --&gt; PROP

    DE1 --&gt; DPD_SP1
    DE1 --&gt; DPD_MS1
    DE1 --&gt; DPD_SC1

    DE2 --&gt; DPD_SP2
    DE2 --&gt; DPD_MS2
    DE2 --&gt; DPD_SC2

    DE3 --&gt; DPD_SP3
    DE3 --&gt; DPD_MS3
    DE3 --&gt; DPD_SC3

    DPD_SP1 --&gt; DVP
    DPD_MS1 --&gt; DVP
    DPD_SP2 --&gt; DVP
    DPD_MS2 --&gt; DVP
    DPD_SP3 --&gt; DVP
    DPD_MS3 --&gt; DVP
</pre><h3 id="ddop-오브젝트-정의-표" tabindex="-1"><a class="header-anchor" href="#ddop-오브젝트-정의-표"><span>DDOP 오브젝트 정의 표</span></a></h3><table><thead><tr><th>오브젝트 ID</th><th>타입</th><th>주요 속성</th><th>값</th></tr></thead><tbody><tr><td>1</td><td>Device</td><td>제품명</td><td>BoomSprayer-3S</td></tr><tr><td></td><td></td><td>제조사</td><td>ExampleCo</td></tr><tr><td></td><td></td><td>Structure Label</td><td>SPRY3-V1.0</td></tr><tr><td>2</td><td>DeviceElement</td><td>Type</td><td>Device</td></tr><tr><td></td><td></td><td>Element Number</td><td>0</td></tr><tr><td></td><td></td><td>부모</td><td>Device(1)</td></tr><tr><td>3</td><td>DeviceElement</td><td>Type</td><td>Section</td></tr><tr><td></td><td></td><td>Element Number</td><td>1</td></tr><tr><td></td><td></td><td>부모</td><td>DE(2)</td></tr><tr><td>4</td><td>DeviceElement</td><td>Type</td><td>Section</td></tr><tr><td></td><td></td><td>Element Number</td><td>2</td></tr><tr><td></td><td></td><td>부모</td><td>DE(2)</td></tr><tr><td>5</td><td>DeviceElement</td><td>Type</td><td>Section</td></tr><tr><td></td><td></td><td>Element Number</td><td>3</td></tr><tr><td></td><td></td><td>부모</td><td>DE(2)</td></tr><tr><td>6</td><td>DeviceProperty</td><td>DDI</td><td>작업폭 DDI</td></tr><tr><td></td><td></td><td>Value</td><td>9000 (단위: mm)</td></tr><tr><td></td><td></td><td>연결 Element</td><td>DE(2)</td></tr><tr><td>7</td><td>DeviceProcessData</td><td>DDI</td><td>1 (Setpoint Vol/Area)</td></tr><tr><td></td><td></td><td>Property Flag</td><td>Setpoint 지원</td></tr><tr><td></td><td></td><td>연결 Element</td><td>DE(3) — Section 1</td></tr><tr><td>8</td><td>DeviceProcessData</td><td>DDI</td><td>2 (Actual Vol/Area)</td></tr><tr><td></td><td></td><td>Property Flag</td><td>Measurement 지원</td></tr><tr><td></td><td></td><td>Trigger</td><td>변화량(10 L/ha 이상 변화 시)</td></tr><tr><td></td><td></td><td>연결 Element</td><td>DE(3) — Section 1</td></tr><tr><td>9</td><td>DeviceProcessData</td><td>DDI</td><td>141 (Section Ctrl)</td></tr><tr><td></td><td></td><td>Property Flag</td><td>Setpoint 지원</td></tr><tr><td></td><td></td><td>연결 Element</td><td>DE(3) — Section 1</td></tr><tr><td>10–12</td><td>DeviceProcessData</td><td>(Section 2 동일 구조)</td><td>DE(4) 연결</td></tr><tr><td>13–15</td><td>DeviceProcessData</td><td>(Section 3 동일 구조)</td><td>DE(5) 연결</td></tr><tr><td>16</td><td>DeviceValuePresentation</td><td>Offset</td><td>0</td></tr><tr><td></td><td></td><td>Scale</td><td>0.01</td></tr><tr><td></td><td></td><td>Unit Symbol</td><td>L/ha</td></tr></tbody></table><p>이 DDOP를 수신한 TC-Server는 다음을 파악한다.</p><ul><li>이 작업기는 3개의 Section을 가진 살포기이다.</li><li>각 Section에 DDI 1(Setpoint), DDI 2(Measurement), DDI 141(Section Control)을 지원한다.</li><li>전체 작업폭은 9m이다.</li><li>값의 단위는 L/ha이며 스케일 인자는 0.01이다.</li></ul><hr><blockquote><p><strong>핵심 정리</strong></p><ul><li>DDOP(Device Description Object Pool)는 작업기가 TC에게 자신의 구조와 능력을 알리는 데이터로, &quot;작업기의 자기소개서&quot;이다.</li><li>DDOP는 Device, DeviceElement, DeviceProcessData, DeviceProperty, DeviceValuePresentation 5가지 오브젝트로 구성된다.</li><li>TC-Client는 연결 시 Structure Label을 먼저 전달하고, TC가 요청하면 DDOP 전체를 멀티패킷으로 전송한다.</li><li>TC는 DDOP를 파싱하여 지원 DDI, Section 구성, 작업폭 등을 파악한 뒤 Task를 활성화한다.</li><li>3구획 살포기 DDOP에는 Section별로 DDI 1(Setpoint), DDI 2(Measurement), DDI 141(Section Control) 항목이 정의된다.</li></ul></blockquote><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/21-isobus-misc">ISOBUS 기타 기능</a></li></ul>`,48)]))}const c=e(l,[["render",n],["__file","20-tc-ddop.html.vue"]]),a=JSON.parse('{"path":"/study/isobus/20-tc-ddop.html","title":"TC 디바이스 디스크립션 (DDOP)","lang":"en-US","frontmatter":{"title":"TC 디바이스 디스크립션 (DDOP)","description":"작업기가 자신의 구조와 능력을 TC에 알리는 Device Description Object Pool(DDOP)의 구조, 오브젝트 타입, 전송 과정을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","ISO11783","TaskController","TC","DDOP","DeviceDescription","ObjectPool"],"prev":"/study/isobus/19-tc-process-data","next":"/study/isobus/21-tc-task"},"headers":[{"level":1,"title":"TC 디바이스 디스크립션 (DDOP)","slug":"tc-디바이스-디스크립션-ddop","link":"#tc-디바이스-디스크립션-ddop","children":[{"level":2,"title":"1. DDOP란","slug":"_1-ddop란","link":"#_1-ddop란","children":[]},{"level":2,"title":"2. DDOP 오브젝트 구조","slug":"_2-ddop-오브젝트-구조","link":"#_2-ddop-오브젝트-구조","children":[{"level":3,"title":"오브젝트 타입 상세","slug":"오브젝트-타입-상세","link":"#오브젝트-타입-상세","children":[]}]},{"level":2,"title":"3. DDOP 전송 과정","slug":"_3-ddop-전송-과정","link":"#_3-ddop-전송-과정","children":[{"level":3,"title":"전송 프로토콜","slug":"전송-프로토콜","link":"#전송-프로토콜","children":[]}]},{"level":2,"title":"4. DDOP 설계 예제","slug":"_4-ddop-설계-예제","link":"#_4-ddop-설계-예제","children":[{"level":3,"title":"대상: 3구획 붐 스프레이어","slug":"대상-3구획-붐-스프레이어","link":"#대상-3구획-붐-스프레이어","children":[]},{"level":3,"title":"DDOP 계층 구조","slug":"ddop-계층-구조","link":"#ddop-계층-구조","children":[]},{"level":3,"title":"DDOP 오브젝트 정의 표","slug":"ddop-오브젝트-정의-표","link":"#ddop-오브젝트-정의-표","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/20-tc-ddop.md"}');export{c as comp,a as data};
