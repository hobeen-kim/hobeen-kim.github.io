import{_ as r,c as e,d as n,o as l}from"./app-BSj_EDeZ.js";const a={};function o(s,t){return l(),e("div",null,t[0]||(t[0]=[n(`<h1 id="isobus-네트워크-아키텍처" tabindex="-1"><a class="header-anchor" href="#isobus-네트워크-아키텍처"><span>ISOBUS 네트워크 아키텍처</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>ISOBUS 네트워크가 In-Cab 버스와 Implement 버스로 구분되는 이유를 설명할 수 있다.</li><li>TBC(Tractor Bus Connector)의 역할과 핀 구성을 이해한다.</li><li>ISOBUS 상의 주요 ECU 종류와 각 역할을 구분할 수 있다.</li><li>장비 시동 후 ISOBUS 통신이 확립되기까지의 메시지 흐름을 순서대로 설명할 수 있다.</li></ul></div><hr><h2 id="_1-네트워크-토폴로지" tabindex="-1"><a class="header-anchor" href="#_1-네트워크-토폴로지"><span>1. 네트워크 토폴로지</span></a></h2><p>ISOBUS 네트워크는 물리적으로 두 개의 CAN 버스로 구성된다.</p><ul><li><strong>In-Cab 버스</strong>: 트랙터 내부 ECU들이 연결되는 버스</li><li><strong>Implement 버스</strong>: 트랙터 외부에 연결되는 작업기 ECU들이 연결되는 버스</li></ul><p>두 버스는 <strong>TBC(Tractor Bus Connector)</strong>를 통해 연결된다.</p><pre class="mermaid">graph LR
    subgraph 트랙터_내부
        TECU[TECU&lt;br&gt;Tractor ECU]
        VT[VT&lt;br&gt;Virtual Terminal]
        TC[TC&lt;br&gt;Task Controller]
        GW[Gateway&lt;br&gt;브리지]
        TECU --- InCab[In-Cab Bus&lt;br&gt;250kbps CAN]
        VT --- InCab
        TC --- InCab
        GW --- InCab
    end

    GW --- TBC[TBC&lt;br&gt;9핀 커넥터]

    subgraph 작업기_외부
        TBC --- ImplBus[Implement Bus&lt;br&gt;250kbps CAN]
        WSM[Working Set&lt;br&gt;Master]
        WSMem[Working Set&lt;br&gt;Member 1]
        WSMem2[Working Set&lt;br&gt;Member 2]
        ImplBus --- WSM
        ImplBus --- WSMem
        ImplBus --- WSMem2
    end
</pre><p>두 버스를 분리하는 이유는 <strong>전기적 안전성</strong>과 <strong>버스 부하 분산</strong>이다. 작업기를 탈착할 때 발생하는 전기적 충격이 트랙터 내부 버스에 영향을 주지 않도록 격리한다.</p><hr><h2 id="_2-tbc-tractor-bus-connector" tabindex="-1"><a class="header-anchor" href="#_2-tbc-tractor-bus-connector"><span>2. TBC (Tractor Bus Connector)</span></a></h2><p>TBC는 트랙터와 작업기를 물리적으로 연결하는 9핀 커넥터이다. ISO 11783-2에 정의되어 있다.</p><h3 id="_9핀-커넥터-핀-배치" tabindex="-1"><a class="header-anchor" href="#_9핀-커넥터-핀-배치"><span>9핀 커넥터 핀 배치</span></a></h3><table><thead><tr><th>핀 번호</th><th>신호명</th><th>설명</th></tr></thead><tbody><tr><td>핀 A</td><td>Shield</td><td>차폐선</td></tr><tr><td>핀 B</td><td>In-Cab CAN_H</td><td>트랙터 내부 버스 High</td></tr><tr><td>핀 C</td><td>In-Cab CAN_L</td><td>트랙터 내부 버스 Low</td></tr><tr><td>핀 D</td><td>ECU_PWR_A</td><td>작업기 ECU 전원 (12V/24V)</td></tr><tr><td>핀 E</td><td>GND</td><td>접지</td></tr><tr><td>핀 F</td><td>Implement CAN_H</td><td>작업기 버스 High</td></tr><tr><td>핀 G</td><td>Implement CAN_L</td><td>작업기 버스 Low</td></tr><tr><td>핀 H</td><td>In-Cab PWR</td><td>트랙터 캐빈 전원</td></tr><tr><td>핀 J</td><td>ECU_PWR_B</td><td>작업기 ECU 전원 보조</td></tr></tbody></table><h3 id="전원-공급-구조" tabindex="-1"><a class="header-anchor" href="#전원-공급-구조"><span>전원 공급 구조</span></a></h3><p>트랙터는 TBC를 통해 작업기 ECU에 전원을 공급한다. ECU_PWR 핀을 통해 작업기의 ECU와 센서가 동작에 필요한 전력을 받다. 작업기 자체 전원(배터리)이 없어도 트랙터에 연결하면 즉시 동작 가능한다.</p><hr><h2 id="_3-ecu-종류" tabindex="-1"><a class="header-anchor" href="#_3-ecu-종류"><span>3. ECU 종류</span></a></h2><p>ISOBUS 네트워크 위에는 역할별로 명확히 구분된 ECU들이 존재한다.</p><pre class="mermaid">graph TB
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
</pre><h3 id="각-ecu의-핵심-역할-요약" tabindex="-1"><a class="header-anchor" href="#각-ecu의-핵심-역할-요약"><span>각 ECU의 핵심 역할 요약</span></a></h3><table><thead><tr><th>ECU</th><th>위치</th><th>핵심 역할</th></tr></thead><tbody><tr><td>VT (Virtual Terminal)</td><td>트랙터 내부</td><td>작업기 화면 표시, 운전자 UI</td></tr><tr><td>TC (Task Controller)</td><td>트랙터 내부</td><td>작업 계획·기록, 섹션 제어</td></tr><tr><td>TECU (Tractor ECU)</td><td>트랙터 내부</td><td>트랙터 상태 정보 제공</td></tr><tr><td>GPS Receiver</td><td>트랙터 내부</td><td>위치 정보 제공</td></tr><tr><td>AUX Input Device</td><td>트랙터 내부</td><td>추가 조작 입력</td></tr><tr><td>Working Set Master</td><td>작업기</td><td>작업기 대표, VT·TC와 통신</td></tr><tr><td>Working Set Member</td><td>작업기</td><td>작업기 내부 개별 제어</td></tr></tbody></table><hr><h2 id="_4-네트워크-메시지-흐름" tabindex="-1"><a class="header-anchor" href="#_4-네트워크-메시지-흐름"><span>4. 네트워크 메시지 흐름</span></a></h2><p>트랙터에 작업기를 연결하고 시동을 켠 후, ISOBUS 통신이 확립되기까지 일련의 단계가 순서대로 진행된다.</p><pre class="mermaid">sequenceDiagram
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

    WSM-&gt;&gt;WSM: Working Set Master 선언&lt;br&gt;(PGN 65070 브로드캐스트)
    WSM-&gt;&gt;TC: Working Set Member 목록 알림

    Note over TECU,TC: ~1s: Working Set 구성 완료

    WSM-&gt;&gt;VT: VT 연결 요청&lt;br&gt;(Working Set Master Maintenance)
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
</pre><p>각 단계의 의미:</p><ol><li><strong>주소 클레임</strong>: 모든 ECU가 네트워크에서 고유한 주소를 확보한다 (J1939 방식과 동일).</li><li><strong>Working Set 구성</strong>: 작업기를 대표하는 WSM이 자신과 멤버 ECU를 선언한다.</li><li><strong>VT 연결</strong>: WSM이 VT에 연결을 요청하고 상태를 수신한다.</li><li><strong>Object Pool 전송</strong>: 작업기 UI 화면 데이터를 VT에 업로드한다.</li><li><strong>Device Descriptor 전송</strong>: 작업기의 기능 구조를 TC에 알린다.</li><li><strong>정상 동작</strong>: TECU 정보·TC 명령·VT 화면 업데이트가 주기적으로 이루어진다.</li></ol><hr><blockquote><p><strong>핵심 정리</strong></p><ul><li>ISOBUS 네트워크는 In-Cab 버스와 Implement 버스로 분리되며, TBC 9핀 커넥터로 연결된다.</li><li>VT는 화면, TC는 작업 관리, TECU는 트랙터 정보 제공, WSM은 작업기 대표 역할을 한다.</li><li>시동 후 주소 클레임 → Working Set 구성 → VT 연결 → Object Pool 전송 순으로 통신이 확립된다.</li><li>Object Pool은 작업기 UI를 정의하는 데이터로, WSM이 VT에 전송하여 화면을 구성한다.</li></ul></blockquote><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/14-isobus-network-mgmt">ISOBUS 네트워크 관리</a></li></ul>`,33)]))}const i=r(a,[["render",o],["__file","13-isobus-architecture.html.vue"]]),g=JSON.parse('{"path":"/study/isobus/13-isobus-architecture.html","title":"ISOBUS 네트워크 아키텍처","lang":"en-US","frontmatter":{"title":"ISOBUS 네트워크 아키텍처","description":"ISOBUS 네트워크의 물리적 토폴로지, TBC 커넥터, ECU 종류, 메시지 흐름 순서를 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","ISO11783","TBC","VT","TaskController","ECU"],"prev":"/study/isobus/12-isobus-overview","next":"/study/isobus/14-isobus-network-mgmt"},"headers":[{"level":1,"title":"ISOBUS 네트워크 아키텍처","slug":"isobus-네트워크-아키텍처","link":"#isobus-네트워크-아키텍처","children":[{"level":2,"title":"1. 네트워크 토폴로지","slug":"_1-네트워크-토폴로지","link":"#_1-네트워크-토폴로지","children":[]},{"level":2,"title":"2. TBC (Tractor Bus Connector)","slug":"_2-tbc-tractor-bus-connector","link":"#_2-tbc-tractor-bus-connector","children":[{"level":3,"title":"9핀 커넥터 핀 배치","slug":"_9핀-커넥터-핀-배치","link":"#_9핀-커넥터-핀-배치","children":[]},{"level":3,"title":"전원 공급 구조","slug":"전원-공급-구조","link":"#전원-공급-구조","children":[]}]},{"level":2,"title":"3. ECU 종류","slug":"_3-ecu-종류","link":"#_3-ecu-종류","children":[{"level":3,"title":"각 ECU의 핵심 역할 요약","slug":"각-ecu의-핵심-역할-요약","link":"#각-ecu의-핵심-역할-요약","children":[]}]},{"level":2,"title":"4. 네트워크 메시지 흐름","slug":"_4-네트워크-메시지-흐름","link":"#_4-네트워크-메시지-흐름","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/13-isobus-architecture.md"}');export{i as comp,g as data};
