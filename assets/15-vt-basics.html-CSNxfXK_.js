import{_ as n,c as e,d as r,o as s}from"./app-C_ZVVrcH.js";const a={};function i(l,t){return s(),e("div",null,t[0]||(t[0]=[r(`<h1 id="virtual-terminal-vt-기초" tabindex="-1"><a class="header-anchor" href="#virtual-terminal-vt-기초"><span>Virtual Terminal (VT) 기초</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>Virtual Terminal(VT)이 무엇이며 어떤 문제를 해결하는지 설명할 수 있다.</li><li>VT의 동작 원리와 오브젝트 풀의 역할을 이해한다.</li><li>VT 버전별 주요 기능 차이를 비교할 수 있다.</li><li>AUX(보조 입력) 장치의 개념과 Preferred Assignment를 설명할 수 있다.</li></ul></div><hr><h2 id="_1-vt란-무엇인가" tabindex="-1"><a class="header-anchor" href="#_1-vt란-무엇인가"><span>1. VT란 무엇인가</span></a></h2><p><strong>Virtual Terminal(VT)</strong>은 ISO 11783-6에 정의된 표준 사용자 인터페이스 시스템이다. 트랙터 운전석에 장착된 디스플레이에 <strong>작업기의 UI를 표시하고 사용자 입력을 받는</strong> 인터페이스 역할을 한다.</p><p>VT 시스템은 두 주체로 구성된다.</p><table><thead><tr><th>역할</th><th>장치</th><th>담당</th></tr></thead><tbody><tr><td><strong>VT Server</strong></td><td>트랙터 캐빈 디스플레이</td><td>화면 렌더링, 입력 처리</td></tr><tr><td><strong>VT Client</strong></td><td>작업기 ECU</td><td>화면 내용(오브젝트 풀) 정의, 데이터 갱신</td></tr></tbody></table><p>즉, <strong>디스플레이 하드웨어는 트랙터가 제공</strong>하고, <strong>화면에 무엇을 보여줄지는 작업기 ECU가 결정</strong>한다. 트랙터와 작업기의 역할이 명확히 분리되어 있는 것이 핵심이다.</p><pre class="mermaid">graph LR
    subgraph 트랙터
        VTS[VT Server&lt;br&gt;CANBUS 주소 0x26]
        DISP[디스플레이 하드웨어]
        VTS --&gt; DISP
    end
    subgraph 작업기
        ECU[작업기 ECU&lt;br&gt;VT Client]
    end
    ECU -- &quot;오브젝트 풀 전송&lt;br&gt;사용자 입력 수신&quot; --&gt; VTS
    VTS -- &quot;사용자 입력 이벤트&quot; --&gt; ECU
</pre><hr><h2 id="_2-왜-vt가-혁신적인가" tabindex="-1"><a class="header-anchor" href="#_2-왜-vt가-혁신적인가"><span>2. 왜 VT가 혁신적인가</span></a></h2><h3 id="vt-이전-전용-디스플레이-시대" tabindex="-1"><a class="header-anchor" href="#vt-이전-전용-디스플레이-시대"><span>VT 이전: 전용 디스플레이 시대</span></a></h3><p>VT 표준이 없던 시절, 각 작업기 제조사는 <strong>전용 디스플레이 패널</strong>을 함께 납품했다.</p><ul><li>비료 살포기 → 비료 살포기 전용 컨트롤 박스</li><li>파종기 → 파종기 전용 모니터</li><li>스프레이어 → 스프레이어 전용 디스플레이</li></ul><p>운전석에 작업기가 늘어날수록 디스플레이도 늘어났다. 배선은 복잡해지고, 운전자는 여러 개의 서로 다른 UI를 익혀야 했다.</p><h3 id="vt-이후-통합-디스플레이" tabindex="-1"><a class="header-anchor" href="#vt-이후-통합-디스플레이"><span>VT 이후: 통합 디스플레이</span></a></h3><p>VT는 이 문제를 <strong>스마트폰 앱 스토어 모델</strong>로 해결했다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">스마트폰(VT Server) = 하드웨어 플랫폼</span>
<span class="line">앱(오브젝트 풀)     = 작업기 ECU가 제공하는 UI 정의</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><p>하나의 VT 디스플레이에 어떤 제조사의 작업기를 연결해도, 작업기가 자신의 UI 정의를 VT로 전송하면 VT가 화면을 렌더링한다. 운전자는 <strong>하나의 디스플레이로 모든 작업기를 조작</strong>할 수 있다.</p><pre class="mermaid">graph TD
    VT[VT 디스플레이&lt;br&gt;하나의 통합 인터페이스]
    A[비료 살포기 ECU]
    B[파종기 ECU]
    C[스프레이어 ECU]
    D[베일러 ECU]

    A -- &quot;오브젝트 풀 A&quot; --&gt; VT
    B -- &quot;오브젝트 풀 B&quot; --&gt; VT
    C -- &quot;오브젝트 풀 C&quot; --&gt; VT
    D -- &quot;오브젝트 풀 D&quot; --&gt; VT
</pre><hr><h2 id="_3-vt-동작-원리" tabindex="-1"><a class="header-anchor" href="#_3-vt-동작-원리"><span>3. VT 동작 원리</span></a></h2><p>VT와 작업기 ECU 사이의 동작은 크게 세 단계로 나뉜다.</p><ol><li><strong>오브젝트 풀 전송</strong>: 작업기 ECU가 화면 정의 데이터를 VT로 업로드</li><li><strong>렌더링</strong>: VT가 오브젝트 풀을 해석해 화면에 표시</li><li><strong>상호작용</strong>: 사용자 입력 → VT → ECU, ECU 데이터 갱신 → VT 화면 업데이트</li></ol><pre class="mermaid">sequenceDiagram
    participant ECU as 작업기 ECU (VT Client)
    participant VT as VT Server (디스플레이)
    participant User as 운전자

    ECU-&gt;&gt;VT: VT Status 요청 (Working Set Maintenance)
    VT--&gt;&gt;ECU: VT Status 응답 (버전, 메모리 등)

    ECU-&gt;&gt;VT: Object Pool Transfer (화면 정의 데이터 전송)
    VT--&gt;&gt;ECU: End of Object Pool Response (전송 완료 확인)

    VT-&gt;&gt;VT: 오브젝트 풀 파싱 및 화면 렌더링

    User-&gt;&gt;VT: 버튼 클릭 / 소프트키 입력
    VT-&gt;&gt;ECU: Button Activation Message (입력 이벤트 전달)

    ECU-&gt;&gt;ECU: 입력 처리 (예: 살포량 변경)
    ECU-&gt;&gt;VT: Change Numeric Value (화면 데이터 갱신)
    VT-&gt;&gt;User: 새로운 값 화면 표시
</pre><hr><h2 id="_4-vt-버전" tabindex="-1"><a class="header-anchor" href="#_4-vt-버전"><span>4. VT 버전</span></a></h2><p>ISO 11783-6은 지속적으로 개정되어 왔으며, VT Server와 Client가 지원하는 <strong>버전(Version)</strong>에 따라 사용 가능한 기능이 달라진다.</p><table><thead><tr><th>버전</th><th>주요 특징</th></tr></thead><tbody><tr><td><strong>Version 2</strong></td><td>기본 오브젝트 타입, 기본 그래픽(픽셀 단위)</td></tr><tr><td><strong>Version 3</strong></td><td>색상 팔레트 확장(256색), 소프트키 마스크 개선</td></tr><tr><td><strong>Version 4</strong></td><td>향상된 그래픽 품질, 윈도우 마스크(복수 화면 관리)</td></tr><tr><td><strong>Version 5</strong></td><td>스크롤 컨테이너, 드래그 앤 드롭 이벤트 지원</td></tr><tr><td><strong>Version 6</strong></td><td>최신 버전, 추가 입력 이벤트, 다국어 개선</td></tr></tbody></table><p>VT Server와 Client가 서로 다른 버전을 지원할 경우, <strong>낮은 버전으로 협상</strong>하여 동작한다. 협상 과정은 VT Status 메시지 교환 시 이루어진다.</p><pre class="mermaid">graph LR
    subgraph 버전 협상 예시
        C[ECU: Version 5 지원]
        V[VT: Version 4 지원]
        R[실제 동작: Version 4]
        C -- min 버전 협상 --&gt; V
        V --&gt; R
    end
</pre><hr><h2 id="_5-aux-보조-입력" tabindex="-1"><a class="header-anchor" href="#_5-aux-보조-입력"><span>5. AUX (보조 입력)</span></a></h2><p><strong>AUX(Auxiliary Input)</strong>는 조이스틱, 추가 버튼 패드, 풋 페달 등 VT 디스플레이 외부의 보조 입력 장치를 ISOBUS에 통합하는 메커니즘이다. ISO 11783-6 Annex에 정의되어 있다.</p><p>현재 표준에서 사용되는 버전은 <strong>AUX-N</strong>(New AUX)으로, 기존 AUX-O(Old AUX)를 대체했다.</p><h3 id="aux-구성-요소" tabindex="-1"><a class="header-anchor" href="#aux-구성-요소"><span>AUX 구성 요소</span></a></h3><table><thead><tr><th>구성 요소</th><th>설명</th></tr></thead><tbody><tr><td><strong>AUX Input Unit</strong></td><td>물리적 입력 장치 (조이스틱, 버튼 등)</td></tr><tr><td><strong>AUX Function</strong></td><td>작업기 ECU가 정의하는 논리적 기능 (예: &quot;살포 시작&quot;)</td></tr><tr><td><strong>Assignment</strong></td><td>입력 유닛의 특정 입력과 ECU 기능을 연결하는 매핑</td></tr></tbody></table><h3 id="preferred-assignment" tabindex="-1"><a class="header-anchor" href="#preferred-assignment"><span>Preferred Assignment</span></a></h3><p>AUX의 핵심 개념 중 하나는 <strong>Preferred Assignment</strong>이다. 사용자가 한 번 입력 장치와 기능의 매핑을 설정하면, 그 설정이 VT에 저장된다. 다음에 같은 작업기를 연결하면 <strong>이전 매핑이 자동으로 복원</strong>된다.</p><pre class="mermaid">sequenceDiagram
    participant AUX as AUX Input Unit (조이스틱)
    participant VT as VT Server
    participant ECU as 작업기 ECU

    ECU-&gt;&gt;VT: AUX Function 정의 (오브젝트 풀 포함)
    AUX-&gt;&gt;VT: AUX Input Unit 능력 광고 (Available Input 목록)

    VT-&gt;&gt;VT: Preferred Assignment 복원 (이전 저장 설정)
    VT-&gt;&gt;ECU: Preferred Assignment 적용 알림
    VT-&gt;&gt;AUX: Assignment 적용 알림

    Note over AUX, ECU: 매핑 완료 — 조이스틱 조작 시 ECU 기능 실행

    AUX-&gt;&gt;VT: AUX Input Status (입력값 전달)
    VT-&gt;&gt;ECU: AUX Input Maintenance (기능에 매핑된 입력값 전달)
</pre><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>VT는 ISO 11783-6에 정의된 표준 디스플레이 인터페이스로, 트랙터 디스플레이(VT Server)와 작업기 ECU(VT Client)로 구성된다.</li><li>작업기 ECU는 오브젝트 풀을 VT로 전송하고, VT는 이를 렌더링한다.</li><li>VT는 버전(2~6)에 따라 지원 기능이 다르며, 낮은 버전으로 자동 협상한다.</li><li>AUX-N은 조이스틱 등 보조 입력 장치를 ISOBUS에 통합하며, Preferred Assignment로 매핑 설정을 저장한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/16-vt-object-pool">VT 오브젝트 풀</a></li></ul>`,44)]))}const o=n(a,[["render",i],["__file","15-vt-basics.html.vue"]]),g=JSON.parse('{"path":"/study/isobus/15-vt-basics.html","title":"Virtual Terminal (VT) 기초","lang":"en-US","frontmatter":{"title":"Virtual Terminal (VT) 기초","description":"ISOBUS Virtual Terminal의 개념, 동작 원리, 버전별 기능, 그리고 AUX 보조 입력까지 VT의 기초를 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","VT","Virtual Terminal","ISO-11783-6","AUX"],"prev":"/study/isobus/14-isobus-network-mgmt","next":"/study/isobus/16-vt-object-pool"},"headers":[{"level":1,"title":"Virtual Terminal (VT) 기초","slug":"virtual-terminal-vt-기초","link":"#virtual-terminal-vt-기초","children":[{"level":2,"title":"1. VT란 무엇인가","slug":"_1-vt란-무엇인가","link":"#_1-vt란-무엇인가","children":[]},{"level":2,"title":"2. 왜 VT가 혁신적인가","slug":"_2-왜-vt가-혁신적인가","link":"#_2-왜-vt가-혁신적인가","children":[{"level":3,"title":"VT 이전: 전용 디스플레이 시대","slug":"vt-이전-전용-디스플레이-시대","link":"#vt-이전-전용-디스플레이-시대","children":[]},{"level":3,"title":"VT 이후: 통합 디스플레이","slug":"vt-이후-통합-디스플레이","link":"#vt-이후-통합-디스플레이","children":[]}]},{"level":2,"title":"3. VT 동작 원리","slug":"_3-vt-동작-원리","link":"#_3-vt-동작-원리","children":[]},{"level":2,"title":"4. VT 버전","slug":"_4-vt-버전","link":"#_4-vt-버전","children":[]},{"level":2,"title":"5. AUX (보조 입력)","slug":"_5-aux-보조-입력","link":"#_5-aux-보조-입력","children":[{"level":3,"title":"AUX 구성 요소","slug":"aux-구성-요소","link":"#aux-구성-요소","children":[]},{"level":3,"title":"Preferred Assignment","slug":"preferred-assignment","link":"#preferred-assignment","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/15-vt-basics.md"}');export{o as comp,g as data};
