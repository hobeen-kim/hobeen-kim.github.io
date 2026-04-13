import{_ as e,c as n,e as a,o as s}from"./app-3EOPCHRw.js";const r={};function d(l,t){return s(),n("div",null,t[0]||(t[0]=[a(`<h1 id="j1939-transport-protocol" tabindex="-1"><a class="header-anchor" href="#j1939-transport-protocol"><span>J1939 Transport Protocol</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN 프레임의 8바이트 제한과 Transport Protocol의 필요성을 설명할 수 있다.</li><li>BAM 방식과 CMDT 방식의 차이점과 적용 시나리오를 이해한다.</li><li>TP.CM과 TP.DT 메시지의 역할과 PGN 번호를 안다.</li><li>ETP가 필요한 상황과 TP와의 차이를 설명할 수 있다.</li><li>타임아웃 규칙을 이해하고 Abort 처리 흐름을 설명할 수 있다.</li></ul></div><hr><h2 id="_1-왜-transport-protocol이-필요한가" tabindex="-1"><a class="header-anchor" href="#_1-왜-transport-protocol이-필요한가"><span>1. 왜 Transport Protocol이 필요한가</span></a></h2><p>CAN 프레임의 데이터 필드는 <strong>최대 8바이트</strong>이다. 단순한 센서 값이나 제어 신호는 8바이트 안에 담을 수 있지만, 다음과 같은 데이터는 그렇지 않다.</p><table><thead><tr><th>데이터 유형</th><th>일반 크기</th></tr></thead><tbody><tr><td>DM1 (진단 코드 목록)</td><td>수십~수백 바이트</td></tr><tr><td>VT 오브젝트 풀 (화면 정의)</td><td>수십 KB ~ 수 MB</td></tr><tr><td>소프트웨어 업데이트 펌웨어</td><td>수 KB ~ 수 MB</td></tr><tr><td>제품 식별 정보(Product ID)</td><td>수십 바이트</td></tr></tbody></table><p>이런 데이터는 여러 CAN 프레임으로 <strong>분할(segmentation)<strong> 하여 순서대로 전송해야 한다. 수신 측은 조각들을 모아 </strong>재조립(reassembly)</strong> 한다. 이 역할을 담당하는 것이 <strong>J1939 Transport Protocol(TP)</strong>이다.</p><pre class="mermaid">graph TD
    A[&quot;큰 데이터 (예: 200 byte)&quot;] --&gt; B[&quot;TP 분할&quot;]
    B --&gt; F1[&quot;CAN Frame #1&lt;br&gt;Seq=1, 7 byte&quot;]
    B --&gt; F2[&quot;CAN Frame #2&lt;br&gt;Seq=2, 7 byte&quot;]
    B --&gt; F3[&quot;CAN Frame #3&lt;br&gt;Seq=3, 7 byte&quot;]
    B --&gt; FN[&quot;CAN Frame #N&lt;br&gt;Seq=N, 나머지&quot;]
    F1 --&gt; R[&quot;수신 측 재조립&quot;]
    F2 --&gt; R
    F3 --&gt; R
    FN --&gt; R
    R --&gt; D[&quot;원본 데이터 복원&quot;]
</pre><p>TP는 두 가지 모드를 제공한다.</p><ul><li><strong>BAM (Broadcast Announce Message)</strong>: 1:N 브로드캐스트 전송</li><li><strong>CMDT (Connection Mode Data Transfer)</strong>: 1:1 연결 기반 전송 (흐름 제어 포함)</li></ul><hr><h2 id="_2-bam-broadcast-announce-message" tabindex="-1"><a class="header-anchor" href="#_2-bam-broadcast-announce-message"><span>2. BAM (Broadcast Announce Message)</span></a></h2><p>BAM은 특정 수신자를 지정하지 않고 <strong>버스 전체에 브로드캐스트</strong>하는 방식이다. 흐름 제어가 없으므로 수신자는 확인 응답(ACK)을 보내지 않다. 구현이 단순하지만 재전송이 불가능한다.</p><h3 id="bam-흐름" tabindex="-1"><a class="header-anchor" href="#bam-흐름"><span>BAM 흐름</span></a></h3><pre class="mermaid">sequenceDiagram
    participant TX as 송신 ECU
    participant BUS as CAN Bus (Broadcast)

    TX-&gt;&gt;BUS: TP.CM_BAM (PGN 60416)&lt;br&gt;총 크기=200byte, 패킷수=29, PGN=정보PGN

    Note over TX,BUS: 50ms 이상 대기

    TX-&gt;&gt;BUS: TP.DT Packet #1 (Seq=1, 7byte)
    TX-&gt;&gt;BUS: TP.DT Packet #2 (Seq=2, 7byte)
    TX-&gt;&gt;BUS: TP.DT Packet #3 (Seq=3, 7byte)
    Note over TX,BUS: ...
    TX-&gt;&gt;BUS: TP.DT Packet #N (Seq=N, 나머지)

    Note over BUS: 모든 수신 장치가 개별적으로 재조립
</pre><h3 id="tp-cm-bam-메시지-구조-8바이트" tabindex="-1"><a class="header-anchor" href="#tp-cm-bam-메시지-구조-8바이트"><span>TP.CM_BAM 메시지 구조 (8바이트)</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Byte 1 : Control Byte = 0x20 (BAM 식별자)</span>
<span class="line">Byte 2~3: 총 데이터 크기 (Little-Endian, 최대 1785 byte)</span>
<span class="line">Byte 4 : 총 패킷 수 (1~255)</span>
<span class="line">Byte 5 : 0xFF (예약)</span>
<span class="line">Byte 6~8: 전송할 PGN (24bit, Little-Endian)</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="타이밍-규칙" tabindex="-1"><a class="header-anchor" href="#타이밍-규칙"><span>타이밍 규칙</span></a></h3><table><thead><tr><th>항목</th><th>값</th></tr></thead><tbody><tr><td>BAM 후 첫 TP.DT까지 대기</td><td>50ms ~ 200ms</td></tr><tr><td>TP.DT 패킷 간 간격</td><td>50ms ~ 200ms</td></tr><tr><td>수신 측 타임아웃</td><td>750ms (패킷 미수신 시 재조립 포기)</td></tr></tbody></table><hr><h2 id="_3-cmdt-connection-mode-data-transfer" tabindex="-1"><a class="header-anchor" href="#_3-cmdt-connection-mode-data-transfer"><span>3. CMDT (Connection Mode Data Transfer)</span></a></h2><p>CMDT는 <strong>특정 수신자와 1:1 연결을 맺고</strong> 흐름 제어를 포함한 데이터 전송을 수행한다. 수신자가 처리 가능한 패킷 수를 제어(CTS)할 수 있어 버퍼 오버플로를 방지한다.</p><h3 id="cmdt-흐름" tabindex="-1"><a class="header-anchor" href="#cmdt-흐름"><span>CMDT 흐름</span></a></h3><pre class="mermaid">sequenceDiagram
    participant TX as 송신 ECU (SA=0x23)
    participant RX as 수신 ECU (SA=0x82)

    TX-&gt;&gt;RX: RTS (Request To Send)&lt;br&gt;총 크기=200byte, 패킷수=29, PGN=정보PGN

    RX-&gt;&gt;TX: CTS (Clear To Send)&lt;br&gt;허용 패킷수=5, 시작 시퀀스=1

    TX-&gt;&gt;RX: TP.DT Packet #1 (Seq=1)
    TX-&gt;&gt;RX: TP.DT Packet #2 (Seq=2)
    TX-&gt;&gt;RX: TP.DT Packet #3 (Seq=3)
    TX-&gt;&gt;RX: TP.DT Packet #4 (Seq=4)
    TX-&gt;&gt;RX: TP.DT Packet #5 (Seq=5)

    RX-&gt;&gt;TX: CTS (Clear To Send)&lt;br&gt;허용 패킷수=5, 시작 시퀀스=6

    TX-&gt;&gt;RX: TP.DT Packet #6 (Seq=6)
    Note over TX,RX: ... 계속 ...
    TX-&gt;&gt;RX: TP.DT Packet #29 (Seq=29)

    RX-&gt;&gt;TX: EndOfMsgACK (전송 완료 확인)
</pre><h3 id="cmdt-제어-메시지-control-byte-값" tabindex="-1"><a class="header-anchor" href="#cmdt-제어-메시지-control-byte-값"><span>CMDT 제어 메시지 Control Byte 값</span></a></h3><table><thead><tr><th>메시지</th><th>Control Byte</th><th>설명</th></tr></thead><tbody><tr><td>RTS</td><td>0x10</td><td>전송 요청 (총 크기, 패킷 수, PGN 포함)</td></tr><tr><td>CTS</td><td>0x11</td><td>수신 준비 (허용 패킷 수, 시작 시퀀스 번호)</td></tr><tr><td>EndOfMsgACK</td><td>0x13</td><td>전체 전송 완료 확인</td></tr><tr><td>Abort</td><td>0xFF</td><td>연결 중단 (오류 코드 포함)</td></tr></tbody></table><h3 id="bam-vs-cmdt-비교" tabindex="-1"><a class="header-anchor" href="#bam-vs-cmdt-비교"><span>BAM vs CMDT 비교</span></a></h3><table><thead><tr><th>항목</th><th>BAM</th><th>CMDT</th></tr></thead><tbody><tr><td>수신 대상</td><td>브로드캐스트 (전체)</td><td>특정 장치 (1:1)</td></tr><tr><td>흐름 제어</td><td>없음</td><td>있음 (CTS)</td></tr><tr><td>완료 확인</td><td>없음</td><td>EndOfMsgACK</td></tr><tr><td>재전송</td><td>불가</td><td>가능 (Abort 후 재시도)</td></tr><tr><td>최대 크기</td><td>1785 byte</td><td>1785 byte</td></tr></tbody></table><hr><h2 id="_4-tp-cm과-tp-dt" tabindex="-1"><a class="header-anchor" href="#_4-tp-cm과-tp-dt"><span>4. TP.CM과 TP.DT</span></a></h2><p>Transport Protocol은 <strong>두 가지 PGN</strong>으로 동작한다.</p><h3 id="tp-cm-pgn-60416-0xec00-—-connection-management" tabindex="-1"><a class="header-anchor" href="#tp-cm-pgn-60416-0xec00-—-connection-management"><span>TP.CM (PGN 60416, 0xEC00) — Connection Management</span></a></h3><p>연결 관리를 담당한다. BAM 공지, RTS/CTS 흐름 제어, EndOfMsg, Abort 메시지가 모두 이 PGN을 사용하며, <strong>Control Byte(Byte 1)</strong>로 메시지 종류를 구분한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">TP.CM 메시지 (8 byte):</span>
<span class="line">┌────────────────────────────────────────────────────┐</span>
<span class="line">│ Byte 1: Control Byte (0x20=BAM, 0x10=RTS, 0x11=CTS,│</span>
<span class="line">│                        0x13=EndOfMsg, 0xFF=Abort)   │</span>
<span class="line">│ Byte 2~8: 메시지 종류에 따라 해석 방식 다름         │</span>
<span class="line">└────────────────────────────────────────────────────┘</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="tp-dt-pgn-60160-0xeb00-—-data-transfer" tabindex="-1"><a class="header-anchor" href="#tp-dt-pgn-60160-0xeb00-—-data-transfer"><span>TP.DT (PGN 60160, 0xEB00) — Data Transfer</span></a></h3><p>실제 데이터를 7바이트씩 분할하여 전송한다. <strong>Byte 1은 시퀀스 번호(1~255)</strong>, Byte 2~8이 페이로드이다. 마지막 패킷의 남는 바이트는 0xFF로 채운다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">TP.DT 메시지 (8 byte):</span>
<span class="line">┌──────────────────────────────────────────┐</span>
<span class="line">│ Byte 1: Sequence Number (1 ~ 255)        │</span>
<span class="line">│ Byte 2: 페이로드 바이트 1                │</span>
<span class="line">│ Byte 3: 페이로드 바이트 2                │</span>
<span class="line">│ ...                                      │</span>
<span class="line">│ Byte 8: 페이로드 바이트 7 (또는 0xFF)   │</span>
<span class="line">└──────────────────────────────────────────┘</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>예시 — 16바이트 데이터 전송:</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">원본 데이터: [A1 A2 A3 A4 A5 A6 A7 | B1 B2 B3 B4 B5 B6 B7 | C1 C2]</span>
<span class="line"></span>
<span class="line">TP.DT Packet #1: [01] A1 A2 A3 A4 A5 A6 A7</span>
<span class="line">TP.DT Packet #2: [02] B1 B2 B3 B4 B5 B6 B7</span>
<span class="line">TP.DT Packet #3: [03] C1 C2 FF FF FF FF FF  ← 남은 자리 0xFF 패딩</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h2 id="_5-etp-extended-transport-protocol" tabindex="-1"><a class="header-anchor" href="#_5-etp-extended-transport-protocol"><span>5. ETP (Extended Transport Protocol)</span></a></h2><p>TP는 최대 <strong>1785 바이트</strong>(255 패킷 × 7 바이트)까지 전송할 수 있다. ISOBUS VT 오브젝트 풀처럼 더 큰 데이터를 전송하려면 <strong>ETP(Extended Transport Protocol)</strong>를 사용한다.</p><h3 id="etp-vs-tp-비교" tabindex="-1"><a class="header-anchor" href="#etp-vs-tp-비교"><span>ETP vs TP 비교</span></a></h3><table><thead><tr><th>항목</th><th>TP</th><th>ETP</th></tr></thead><tbody><tr><td>TP.CM PGN</td><td>60416 (0xEC00)</td><td>51712 (0xC900)</td></tr><tr><td>TP.DT PGN</td><td>60160 (0xEB00)</td><td>51456 (0xC800)</td></tr><tr><td>최대 데이터 크기</td><td>1785 byte</td><td>약 117 MB (2^24 - 1 byte)</td></tr><tr><td>패킷당 데이터</td><td>7 byte</td><td>7 byte</td></tr><tr><td>연결 방식</td><td>BAM 또는 CMDT</td><td>CMDT 전용</td></tr></tbody></table><h3 id="etp-cmdt-흐름" tabindex="-1"><a class="header-anchor" href="#etp-cmdt-흐름"><span>ETP CMDT 흐름</span></a></h3><pre class="mermaid">sequenceDiagram
    participant TX as 송신 ECU
    participant RX as 수신 ECU

    TX-&gt;&gt;RX: ETP.CM_RTS (PGN 51712)&lt;br&gt;총 크기=50000byte, PGN=오브젝트풀PGN

    RX-&gt;&gt;TX: ETP.CM_CTS (PGN 51712)&lt;br&gt;허용 패킷수=255, 시작 패킷=1

    loop 255 패킷씩 전송
        TX-&gt;&gt;RX: ETP.DT Packet #1 (PGN 51456)
        TX-&gt;&gt;RX: ETP.DT Packet #2 (PGN 51456)
        Note over TX,RX: ... (255 패킷) ...
        TX-&gt;&gt;RX: ETP.DT Packet #255 (PGN 51456)
        RX-&gt;&gt;TX: ETP.CM_CTS&lt;br&gt;허용 패킷수=255, 시작 패킷=256
    end

    RX-&gt;&gt;TX: ETP.CM_EndOfMsgACK (PGN 51712)
</pre><p>ETP는 <strong>CMDT 전용</strong>이다. BAM 방식의 ETP는 존재하지 않다. 이는 대용량 데이터 전송 시 흐름 제어 없이는 수신 버퍼 오버플로가 발생할 수 있기 때문이다.</p><h3 id="isobus-vt-오브젝트-풀-전송" tabindex="-1"><a class="header-anchor" href="#isobus-vt-오브젝트-풀-전송"><span>ISOBUS VT 오브젝트 풀 전송</span></a></h3><p>VT(Virtual Terminal)에 화면을 표시하려면 오브젝트 풀을 전송해야 한다. 오브젝트 풀은 수십 KB를 초과하는 경우가 많으므로 ETP를 통해 전송된다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">작업기 ECU → VT:</span>
<span class="line">  ETP.CM_RTS (오브젝트 풀 PGN, 총 크기)</span>
<span class="line">  → ETP.CM_CTS</span>
<span class="line">  → ETP.DT × N</span>
<span class="line">  → ETP.CM_EndOfMsgACK</span>
<span class="line">  → Load Version / Activate Object Pool 명령</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h2 id="_6-시퀀스-다이어그램으로-보는-tp-etp-흐름" tabindex="-1"><a class="header-anchor" href="#_6-시퀀스-다이어그램으로-보는-tp-etp-흐름"><span>6. 시퀀스 다이어그램으로 보는 TP/ETP 흐름</span></a></h2><h3 id="bam-전체-흐름과-타임아웃" tabindex="-1"><a class="header-anchor" href="#bam-전체-흐름과-타임아웃"><span>BAM 전체 흐름과 타임아웃</span></a></h3><pre class="mermaid">sequenceDiagram
    participant TX as 송신 ECU
    participant RX as 수신 ECU

    TX-&gt;&gt;RX: TP.CM_BAM&lt;br&gt;(총 크기, 패킷수, PGN)
    Note over TX: 50ms ~ 200ms 대기

    TX-&gt;&gt;RX: TP.DT #1
    Note over TX: 50ms ~ 200ms 대기
    TX-&gt;&gt;RX: TP.DT #2
    Note over TX: 50ms ~ 200ms 대기
    TX-&gt;&gt;RX: TP.DT #N (완료)

    Note over RX: 750ms 이내 다음 패킷 미수신&lt;br&gt;→ 재조립 포기 (타임아웃)
</pre><h3 id="cmdt-전체-흐름과-abort-처리" tabindex="-1"><a class="header-anchor" href="#cmdt-전체-흐름과-abort-처리"><span>CMDT 전체 흐름과 Abort 처리</span></a></h3><pre class="mermaid">sequenceDiagram
    participant TX as 송신 ECU
    participant RX as 수신 ECU

    TX-&gt;&gt;RX: RTS (총 크기, 패킷수, PGN)

    alt 정상 흐름
        RX-&gt;&gt;TX: CTS (허용 패킷수=N, 시작 시퀀스=1)
        loop N 패킷씩
            TX-&gt;&gt;RX: TP.DT #1 ~ #N
            RX-&gt;&gt;TX: CTS (다음 배치)
        end
        RX-&gt;&gt;TX: EndOfMsgACK

    else 수신 측 오류 (버퍼 부족 등)
        RX-&gt;&gt;TX: Abort (오류 코드)
        Note over TX,RX: 연결 종료&lt;br&gt;송신 측은 재시도 여부 결정

    else 타임아웃 (RX가 CTS 미전송)
        Note over TX: 1250ms 이내 CTS 미수신&lt;br&gt;→ TX가 Abort 전송
        TX-&gt;&gt;RX: Abort (타임아웃)
    end
</pre><h3 id="타임아웃-규칙-요약" tabindex="-1"><a class="header-anchor" href="#타임아웃-규칙-요약"><span>타임아웃 규칙 요약</span></a></h3><table><thead><tr><th>상황</th><th>타임아웃 값</th><th>처리</th></tr></thead><tbody><tr><td>RTS 후 CTS 대기</td><td>1250ms</td><td>송신 측 Abort</td></tr><tr><td>CTS 후 첫 TP.DT 대기</td><td>1250ms</td><td>수신 측 Abort</td></tr><tr><td>TP.DT 패킷 간 간격</td><td>750ms</td><td>수신 측 Abort</td></tr><tr><td>EndOfMsg 대기</td><td>1250ms</td><td>송신 측 Abort</td></tr><tr><td>BAM TP.DT 패킷 간</td><td>750ms</td><td>수신 측 재조립 포기</td></tr></tbody></table><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN 프레임은 최대 8바이트이므로, 큰 데이터는 Transport Protocol로 분할 전송한다.</li><li><strong>BAM</strong>: 브로드캐스트, 흐름 제어 없음. TP.CM_BAM(PGN 60416) → TP.DT(PGN 60160).</li><li><strong>CMDT</strong>: 1:1 연결, CTS로 흐름 제어. RTS → CTS → TP.DT → EndOfMsgACK.</li><li>TP.DT는 패킷당 7바이트 페이로드, Byte 1이 시퀀스 번호(1~255), 남는 바이트는 0xFF 패딩.</li><li><strong>ETP</strong>: 1785 바이트 초과 시 사용. PGN 51712(ETP.CM), 51456(ETP.DT). CMDT 전용.</li><li>타임아웃 초과 시 Abort(Control Byte=0xFF)를 전송하여 연결을 종료한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/12-isobus-overview">ISOBUS 개요</a></li></ul>`,62)]))}const o=e(r,[["render",d],["__file","11-j1939-transport.html.vue"]]),c=JSON.parse('{"path":"/study/isobus/11-j1939-transport.html","title":"J1939 Transport Protocol","lang":"en-US","frontmatter":{"title":"J1939 Transport Protocol","description":"8바이트를 초과하는 데이터를 전송하기 위한 J1939 Transport Protocol(BAM, CMDT, ETP)을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","J1939","CAN","Transport Protocol","BAM","CMDT","ETP"],"prev":"/study/isobus/10-j1939-address","next":"/study/isobus/12-isobus-overview"},"headers":[{"level":1,"title":"J1939 Transport Protocol","slug":"j1939-transport-protocol","link":"#j1939-transport-protocol","children":[{"level":2,"title":"1. 왜 Transport Protocol이 필요한가","slug":"_1-왜-transport-protocol이-필요한가","link":"#_1-왜-transport-protocol이-필요한가","children":[]},{"level":2,"title":"2. BAM (Broadcast Announce Message)","slug":"_2-bam-broadcast-announce-message","link":"#_2-bam-broadcast-announce-message","children":[{"level":3,"title":"BAM 흐름","slug":"bam-흐름","link":"#bam-흐름","children":[]},{"level":3,"title":"TP.CM_BAM 메시지 구조 (8바이트)","slug":"tp-cm-bam-메시지-구조-8바이트","link":"#tp-cm-bam-메시지-구조-8바이트","children":[]},{"level":3,"title":"타이밍 규칙","slug":"타이밍-규칙","link":"#타이밍-규칙","children":[]}]},{"level":2,"title":"3. CMDT (Connection Mode Data Transfer)","slug":"_3-cmdt-connection-mode-data-transfer","link":"#_3-cmdt-connection-mode-data-transfer","children":[{"level":3,"title":"CMDT 흐름","slug":"cmdt-흐름","link":"#cmdt-흐름","children":[]},{"level":3,"title":"CMDT 제어 메시지 Control Byte 값","slug":"cmdt-제어-메시지-control-byte-값","link":"#cmdt-제어-메시지-control-byte-값","children":[]},{"level":3,"title":"BAM vs CMDT 비교","slug":"bam-vs-cmdt-비교","link":"#bam-vs-cmdt-비교","children":[]}]},{"level":2,"title":"4. TP.CM과 TP.DT","slug":"_4-tp-cm과-tp-dt","link":"#_4-tp-cm과-tp-dt","children":[{"level":3,"title":"TP.CM (PGN 60416, 0xEC00) — Connection Management","slug":"tp-cm-pgn-60416-0xec00-—-connection-management","link":"#tp-cm-pgn-60416-0xec00-—-connection-management","children":[]},{"level":3,"title":"TP.DT (PGN 60160, 0xEB00) — Data Transfer","slug":"tp-dt-pgn-60160-0xeb00-—-data-transfer","link":"#tp-dt-pgn-60160-0xeb00-—-data-transfer","children":[]}]},{"level":2,"title":"5. ETP (Extended Transport Protocol)","slug":"_5-etp-extended-transport-protocol","link":"#_5-etp-extended-transport-protocol","children":[{"level":3,"title":"ETP vs TP 비교","slug":"etp-vs-tp-비교","link":"#etp-vs-tp-비교","children":[]},{"level":3,"title":"ETP CMDT 흐름","slug":"etp-cmdt-흐름","link":"#etp-cmdt-흐름","children":[]},{"level":3,"title":"ISOBUS VT 오브젝트 풀 전송","slug":"isobus-vt-오브젝트-풀-전송","link":"#isobus-vt-오브젝트-풀-전송","children":[]}]},{"level":2,"title":"6. 시퀀스 다이어그램으로 보는 TP/ETP 흐름","slug":"_6-시퀀스-다이어그램으로-보는-tp-etp-흐름","link":"#_6-시퀀스-다이어그램으로-보는-tp-etp-흐름","children":[{"level":3,"title":"BAM 전체 흐름과 타임아웃","slug":"bam-전체-흐름과-타임아웃","link":"#bam-전체-흐름과-타임아웃","children":[]},{"level":3,"title":"CMDT 전체 흐름과 Abort 처리","slug":"cmdt-전체-흐름과-abort-처리","link":"#cmdt-전체-흐름과-abort-처리","children":[]},{"level":3,"title":"타임아웃 규칙 요약","slug":"타임아웃-규칙-요약","link":"#타임아웃-규칙-요약","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/11-j1939-transport.md"}');export{o as comp,c as data};
