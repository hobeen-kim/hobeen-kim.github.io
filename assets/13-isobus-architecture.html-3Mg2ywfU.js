import{_ as e,c as r,e as n,o as l}from"./app-DW00K3Mq.js";const s={};function a(o,t){return l(),r("div",null,t[0]||(t[0]=[n(`<h1 id="isobus-네트워크-아키텍처" tabindex="-1"><a class="header-anchor" href="#isobus-네트워크-아키텍처"><span>ISOBUS 네트워크 아키텍처</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>ISOBUS 네트워크가 트랙터 버스와 Implement 버스로 구분되는 이유와, 두 버스를 TECU가 연결하는 구조를 설명할 수 있다.</li><li>IBBC(9핀 브레이크어웨이 커넥터)와 TBC(종단 바이어스 회로)의 역할을 구분할 수 있다.</li><li>ISOBUS 상의 주요 ECU 종류와 각 역할을 구분할 수 있다.</li><li>장비 시동 후 ISOBUS 통신이 확립되기까지의 메시지 흐름을 순서대로 설명할 수 있다.</li></ul></div><h2 id="_1-네트워크-토폴로지" tabindex="-1"><a class="header-anchor" href="#_1-네트워크-토폴로지"><span>1. 네트워크 토폴로지</span></a></h2><p>ISOBUS 네트워크는 물리적으로 두 개의 네트워크 세그먼트로 구성된다.</p><ul><li><strong>트랙터 버스</strong>(tractor network): 엔진, 변속기, 브레이크, 히치 컨트롤러 등 트랙터 구동계·섀시 ECU들이 연결되는 버스. 트랙터 제조사가 관리하며 내부 규격(J1939 등)을 쓸 수도 있다.</li><li><strong>Implement 버스</strong>(implement network): VT, TC, 작업기 ECU 등 작업기 관련 CF들이 연결되는 버스. 트랙터 위와 작업기 위에 걸쳐 존재하며 ISO 11783을 반드시 준수해야 한다.</li></ul><p>두 버스는 <strong>TECU(Tractor ECU)</strong>가 연결한다. TECU는 두 세그먼트 사이의 게이트웨이 역할을 하는 특수 NIU(Network Interconnection Unit)다. VT와 TC는 물리적으로 트랙터 캐빈에 장착되지만 <strong>버스 소속은 Implement 버스</strong>이며, 외부 작업기는 <strong>IBBC(Implement Bus Breakaway Connector)</strong>를 통해 Implement 버스에 이어진다.</p><pre class="mermaid">graph LR
    subgraph 트랙터_내부
        ENG[엔진·변속기·히치 등&lt;br&gt;트랙터 내부 ECU]
        ENG --- TracBus[Tractor Bus]
        TracBus --- TECU[TECU&lt;br&gt;게이트웨이 NIU]
        TECU --- ImplBus[Implement Bus&lt;br&gt;250kbps CAN]
        VT[VT&lt;br&gt;Virtual Terminal] --- ImplBus
        TC[TC&lt;br&gt;Task Controller] --- ImplBus
    end

    ImplBus --- IBBC[IBBC&lt;br&gt;9핀 커넥터]

    subgraph 작업기_외부
        IBBC --- ImplBus2[Implement Bus&lt;br&gt;연장]
        WSM[Working Set&lt;br&gt;Master]
        WSMem[Working Set&lt;br&gt;Member 1]
        WSMem2[Working Set&lt;br&gt;Member 2]
        ImplBus2 --- WSM
        ImplBus2 --- WSMem
        ImplBus2 --- WSMem2
    end
</pre><p>두 버스를 분리하는 이유는 <strong>트랙터 버스의 격리·보호</strong>다. TECU는 두 세그먼트 사이에서 전기적 격리와 메시지 격리(필터링)를 모두 제공해야 하며, 덕분에 외부 작업기의 전기적 문제나 과도한 트래픽이 트랙터 구동계 버스에 영향을 주지 않는다.</p><div class="hint-container tip"><p class="hint-container-title">NIU의 다섯 가지 유형 (Part 4)</p><p>세그먼트를 연결하는 NIU에는 기능 수준에 따라 리피터(단순 forwarding), 브리지(+ 필터링), 라우터(+ 주소 변환), 게이트웨이(+ 메시지 재조합)가 있고, 트랙터 버스와 Implement 버스를 잇는 <strong>Tractor ECU</strong>가 다섯 번째 특수 유형으로 정의된다. 작업기 내부에 하위 네트워크를 둘 때도 NIU로 Implement 버스와 격리한다.</p></div><h2 id="_2-ibbc-커넥터와-tbc-종단" tabindex="-1"><a class="header-anchor" href="#_2-ibbc-커넥터와-tbc-종단"><span>2. IBBC 커넥터와 TBC 종단</span></a></h2><p><strong>IBBC(Implement Bus Breakaway Connector)</strong>는 트랙터와 작업기의 Implement 버스를 물리적으로 연결하는 9핀 커넥터이다. ISO 11783-2에 정의되어 있으며, 작업기가 분리(breakaway)되어도 트랙터 측 버스가 안전하게 유지되도록 설계된다.</p><p><strong>TBC(Terminating Bias Circuit)</strong>는 커넥터가 아니라 <strong>종단 바이어스 회로</strong>다. 네트워크 세그먼트 양 끝단에 두어 CAN_H·CAN_L에 바이어스 전압과 공통 모드 임피던스 종단을 제공하는 능동 종단으로, 단순 120Ω 저항 종단(J1939-11)과 구별된다.</p><h3 id="_9핀-커넥터-신호-구성" tabindex="-1"><a class="header-anchor" href="#_9핀-커넥터-신호-구성"><span>9핀 커넥터 신호 구성</span></a></h3><p>IBBC의 9개 신호는 세 그룹으로 나뉜다.</p><table><thead><tr><th>그룹</th><th>신호</th><th>설명</th></tr></thead><tbody><tr><td>CAN</td><td>CAN_H, CAN_L</td><td>Implement 버스 신호선 1쌍 (트랙터 내부 버스는 커넥터를 지나지 않는다)</td></tr><tr><td>전원</td><td>PWR, GND, ECU_PWR, ECU_GND</td><td>액추에이터용 전원(PWR)과 ECU 전자회로용 전원(ECU_PWR), 각각의 접지</td></tr><tr><td>종단 제어</td><td>TBC_PWR, TBC_RTN, TBC_DIS</td><td>종단 바이어스 회로(TBC)의 전원·리턴·비활성화 신호</td></tr></tbody></table><h3 id="전원-공급-구조" tabindex="-1"><a class="header-anchor" href="#전원-공급-구조"><span>전원 공급 구조</span></a></h3><p>트랙터는 IBBC를 통해 작업기에 전원을 공급한다. 전원은 용도별로 두 계열로 나뉜다.</p><ul><li><strong>ECU_PWR</strong>: 작업기 ECU·센서 등 전자회로용 전원 (12V 기준 최소 15A)</li><li><strong>PWR</strong>: 밸브·모터 등 액추에이터용 전원 (12V 기준 최소 50A)</li></ul><p>두 전원의 분배 제어와 상태 메시지 송수신은 TECU(function instance 0)가 책임진다(ISO 11783-9). TBC_PWR은 ECU_PWR 또는 TECU 자체에서 급전되어, ECU 전원이 제어되는 상황에서도 버스 종단이 살아 있도록 한다. 작업기 자체 전원(배터리)이 없어도 트랙터에 연결하면 즉시 동작 가능하다.</p><h2 id="_3-ecu-종류" tabindex="-1"><a class="header-anchor" href="#_3-ecu-종류"><span>3. ECU 종류</span></a></h2><p>ISOBUS 네트워크 위에는 역할별로 명확히 구분된 ECU들이 존재한다.</p><pre class="mermaid">graph TB
    subgraph ISOBUS_ECU_역할
        VT[&quot;VT&lt;br&gt;Virtual Terminal&lt;br&gt;─────────&lt;br&gt;트랙터 캐빈의 디스플레이&lt;br&gt;작업기 UI를 화면에 표시&lt;br&gt;운전자 조작 입력 처리&quot;]
        TC[&quot;TC&lt;br&gt;Task Controller&lt;br&gt;─────────&lt;br&gt;작업 계획(Task) 관리&lt;br&gt;섹션 제어, 처방도 적용&lt;br&gt;작업 데이터 기록 (ISOXML)&quot;]
        TECU[&quot;TECU&lt;br&gt;Tractor ECU&lt;br&gt;─────────&lt;br&gt;트랙터 정보 브로드캐스트&lt;br&gt;속도, PTO RPM, 히치 위치&lt;br&gt;엔진 RPM, 연료량 등&quot;]
        GPS[&quot;GPS Receiver&lt;br&gt;─────────&lt;br&gt;위치 정보 (위도·경도)&lt;br&gt;NMEA 0183 / ISOBUS PGN&lt;br&gt;정밀 농업 기반 데이터&quot;]
        AUX[&quot;AUX Input Device&lt;br&gt;─────────&lt;br&gt;조이스틱, 버튼 패드&lt;br&gt;운전자 추가 조작 입력&lt;br&gt;AUX-N / AUX-O 기능&quot;]
        WSM[&quot;Working Set Master&lt;br&gt;─────────&lt;br&gt;작업기 대표 ECU&lt;br&gt;작업기 내 ECU 통합 관리&lt;br&gt;VT·TC와 협상&quot;]
        WSMem[&quot;Working Set Member&lt;br&gt;─────────&lt;br&gt;작업기 내 개별 ECU&lt;br&gt;섹션 밸브, 센서, 모터 등&lt;br&gt;Master 지시에 따라 동작&quot;]

        VT -. &quot;UI 요청/응답&quot; .-&gt; WSM
        TC -. &quot;작업 명령&quot; .-&gt; WSM
        TECU -. &quot;속도·PTO 정보&quot; .-&gt; WSM
        GPS -. &quot;위치 정보&quot; .-&gt; TC
        AUX -. &quot;조작 신호&quot; .-&gt; VT
        WSM -. &quot;내부 제어&quot; .-&gt; WSMem
    end
</pre><h3 id="각-ecu의-핵심-역할-요약" tabindex="-1"><a class="header-anchor" href="#각-ecu의-핵심-역할-요약"><span>각 ECU의 핵심 역할 요약</span></a></h3><table><thead><tr><th>ECU</th><th>버스 소속</th><th>핵심 역할</th></tr></thead><tbody><tr><td>VT (Virtual Terminal)</td><td>Implement 버스 (캐빈 장착)</td><td>작업기 화면 표시, 운전자 UI</td></tr><tr><td>TC (Task Controller)</td><td>Implement 버스 (캐빈 장착)</td><td>작업 계획·기록, 섹션 제어</td></tr><tr><td>TECU (Tractor ECU)</td><td>트랙터 버스 ↔ Implement 버스</td><td>두 버스 연결(게이트웨이), 트랙터 상태 정보 제공</td></tr><tr><td>GPS Receiver</td><td>Implement 버스</td><td>위치 정보 제공</td></tr><tr><td>AUX Input Device</td><td>Implement 버스</td><td>추가 조작 입력</td></tr><tr><td>Working Set Master</td><td>Implement 버스 (작업기)</td><td>작업기 대표, VT·TC와 통신</td></tr><tr><td>Working Set Member</td><td>Implement 버스 (작업기)</td><td>작업기 내부 개별 제어</td></tr></tbody></table><h3 id="tecu-클래스" tabindex="-1"><a class="header-anchor" href="#tecu-클래스"><span>TECU 클래스</span></a></h3><p>ISO 11783-9는 TECU가 Implement 버스에 제공해야 하는 최소 메시지 집합을 <strong>클래스</strong>로 구분한다.</p><table><thead><tr><th>클래스</th><th>의미</th></tr></thead><tbody><tr><td>Class 1</td><td>기본 측정값 제공 (속도, 히치 위치, PTO 회전수 등. 신규 설계에는 비권장)</td></tr><tr><td>Class 2</td><td>측정 기능 전체 제공 (Class 1 + 주행 거리·방향, 견인력, 조명, 밸브 유량)</td></tr><tr><td>Class 3</td><td>Implement 버스로부터의 제어 명령 수용 (히치·PTO·보조 밸브 명령)</td></tr></tbody></table><p>여기에 기능별 addendum이 붙는다: <strong>N</strong>(항법/GPS), <strong>F</strong>(전방 히치·PTO), <strong>G</strong>(조향 제어), <strong>P</strong>(속도·주행 전략 명령), <strong>M</strong>(발진 명령). 예를 들어 class 3GP는 조향과 속도 제어를 모두 수용하는 트랙터다. 작업기가 트랙터를 제어하는 자동화(가변 속도 작업, 자동 조향 등)는 Class 3 이상에서 가능하다.</p><h2 id="_4-네트워크-메시지-흐름" tabindex="-1"><a class="header-anchor" href="#_4-네트워크-메시지-흐름"><span>4. 네트워크 메시지 흐름</span></a></h2><p>트랙터에 작업기를 연결하고 시동을 켠 후, ISOBUS 통신이 확립되기까지 일련의 단계가 순서대로 진행된다.</p><pre class="mermaid">sequenceDiagram
    participant TECU as TECU
    participant WSM as Working Set Master
    participant VT as Virtual Terminal
    participant TC as Task Controller

    Note over TECU,TC: 전원 ON / 시동

    TECU-&gt;&gt;TECU: 주소 클레임 (Address Claim)
    WSM-&gt;&gt;WSM: 주소 클레임 (Address Claim)
    VT-&gt;&gt;VT: 주소 클레임 (Address Claim)
    TC-&gt;&gt;TC: 주소 클레임 (Address Claim)

    Note over TECU,TC: ~250ms: 모든 ECU 주소 확정

    WSM-&gt;&gt;WSM: Working Set Master 선언&lt;br&gt;(PGN 65037 브로드캐스트)
    WSM-&gt;&gt;WSM: Working Set Member 브로드캐스트&lt;br&gt;(PGN 65036, 멤버 수-1개)

    Note over TECU,TC: ~1s: Working Set 구성 완료

    WSM-&gt;&gt;VT: VT 연결 요청&lt;br&gt;(Working Set Maintenance)
    VT-&gt;&gt;WSM: VT Status 응답

    WSM-&gt;&gt;VT: Object Pool 전송 시작&lt;br&gt;(작업기 UI 데이터)
    VT-&gt;&gt;WSM: Object Pool 수신 완료
    VT-&gt;&gt;WSM: End of Object Pool 응답

    WSM-&gt;&gt;TC: Device Descriptor 전송&lt;br&gt;(작업 장치 구조 정보)
    TC-&gt;&gt;WSM: Device Descriptor 수신 완료

    Note over TECU,TC: 정상 동작: VT에 작업기 화면 표시, TC 작업 시작 가능

    TECU-&gt;&gt;WSM: 속도·PTO·히치 정보 주기 전송
    TC-&gt;&gt;WSM: 섹션 제어 명령 전송
    WSM-&gt;&gt;VT: 화면 업데이트 (작업기 상태)
</pre><p>각 단계의 의미:</p><ol><li><strong>주소 클레임</strong>: 모든 ECU가 네트워크에서 고유한 주소를 확보한다 (J1939 방식과 동일).</li><li><strong>Working Set 구성</strong>: 작업기를 대표하는 WSM이 Working Set Master 메시지(PGN 65037)로 멤버 수를, Working Set Member 메시지(PGN 65036)로 각 멤버의 NAME을 브로드캐스트한다. VT·TC 같은 서비스 제공자가 이를 수신해 Working Set을 인식한다.</li><li><strong>VT 연결</strong>: WSM이 VT에 연결을 요청하고 상태를 수신한다.</li><li><strong>Object Pool 전송</strong>: 작업기 UI 화면 데이터를 VT에 업로드한다.</li><li><strong>Device Descriptor 전송</strong>: 작업기의 기능 구조를 TC에 알린다.</li><li><strong>정상 동작</strong>: TECU 정보·TC 명령·VT 화면 업데이트가 주기적으로 이루어진다.</li></ol><blockquote><p><strong>핵심 정리</strong></p><ul><li>ISOBUS 네트워크는 트랙터 버스와 Implement 버스로 분리되며, 두 버스는 TECU(게이트웨이 NIU)가 연결한다. 외부 작업기는 IBBC 9핀 커넥터로 Implement 버스에 접속하고, 각 세그먼트 양 끝단은 TBC(종단 바이어스 회로)로 종단한다.</li><li>VT는 화면, TC는 작업 관리, TECU는 버스 연결과 트랙터 정보 제공, WSM은 작업기 대표 역할을 한다.</li><li>시동 후 주소 클레임 → Working Set 구성 → VT 연결 → Object Pool 전송 순으로 통신이 확립된다.</li><li>Object Pool은 작업기 UI를 정의하는 데이터로, WSM이 VT에 전송하여 화면을 구성한다.</li></ul></blockquote><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/14-isobus-network-mgmt">ISOBUS 네트워크 관리</a></li></ul>`,36)]))}const g=e(s,[["render",a],["__file","13-isobus-architecture.html.vue"]]),d=JSON.parse('{"path":"/study/isobus/13-isobus-architecture.html","title":"ISOBUS 네트워크 아키텍처","lang":"en-US","frontmatter":{"title":"ISOBUS 네트워크 아키텍처","description":"ISOBUS 네트워크의 물리적 토폴로지, IBBC 커넥터와 TBC 종단, ECU 종류, 메시지 흐름 순서를 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","ISO11783","IBBC","TBC","VT","TaskController","ECU"],"prev":"/study/isobus/12-isobus-overview","next":"/study/isobus/14-isobus-network-mgmt"},"headers":[{"level":1,"title":"ISOBUS 네트워크 아키텍처","slug":"isobus-네트워크-아키텍처","link":"#isobus-네트워크-아키텍처","children":[{"level":2,"title":"1. 네트워크 토폴로지","slug":"_1-네트워크-토폴로지","link":"#_1-네트워크-토폴로지","children":[]},{"level":2,"title":"2. IBBC 커넥터와 TBC 종단","slug":"_2-ibbc-커넥터와-tbc-종단","link":"#_2-ibbc-커넥터와-tbc-종단","children":[{"level":3,"title":"9핀 커넥터 신호 구성","slug":"_9핀-커넥터-신호-구성","link":"#_9핀-커넥터-신호-구성","children":[]},{"level":3,"title":"전원 공급 구조","slug":"전원-공급-구조","link":"#전원-공급-구조","children":[]}]},{"level":2,"title":"3. ECU 종류","slug":"_3-ecu-종류","link":"#_3-ecu-종류","children":[{"level":3,"title":"각 ECU의 핵심 역할 요약","slug":"각-ecu의-핵심-역할-요약","link":"#각-ecu의-핵심-역할-요약","children":[]},{"level":3,"title":"TECU 클래스","slug":"tecu-클래스","link":"#tecu-클래스","children":[]}]},{"level":2,"title":"4. 네트워크 메시지 흐름","slug":"_4-네트워크-메시지-흐름","link":"#_4-네트워크-메시지-흐름","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/13-isobus-architecture.md"}');export{g as comp,d as data};
