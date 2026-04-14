import{_ as d,c as r,e as l,o as a}from"./app-DuMXKYjZ.js";const e={};function n(i,t){return a(),r("div",null,t[0]||(t[0]=[l(`<h1 id="스마트농업-기술-지도" tabindex="-1"><a class="header-anchor" href="#스마트농업-기술-지도"><span>스마트농업 기술 지도</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>스마트농업 기술 스택을 4개 계층(하드웨어·통신·플랫폼·지능)으로 설명할 수 있다.</li><li>노지농업과 시설농업의 기술적 차이를 비교할 수 있다.</li><li>센서에서 농기계 자동제어까지 이어지는 데이터 파이프라인을 도식으로 그릴 수 있다.</li><li>주요국의 스마트농업 현황을 서술할 수 있다.</li></ul></div><hr><h2 id="_1-기술-스택-조감도" tabindex="-1"><a class="header-anchor" href="#_1-기술-스택-조감도"><span>1. 기술 스택 조감도</span></a></h2><p>스마트농업을 구성하는 기술은 4개 계층으로 정리할 수 있다. 아래 계층일수록 물리 세계와 맞닿아 있고, 위로 올라갈수록 추상화 수준이 높아진다.</p><pre class="mermaid">mindmap
  root((스마트농업&lt;br&gt;기술 스택))
    하드웨어 계층
      센서
        토양 센서
        기상 센서
        작물 센서
      액추에이터
        관개 밸브
        가변살포 노즐
      농기계
        트랙터
        드론
        로봇
    통신 계층
      단거리
        Wi-Fi
        Bluetooth
        Zigbee
      장거리
        LoRa / LoRaWAN
        NB-IoT
        셀룰러 LTE/5G
      기계 내부
        CAN Bus
        ISOBUS
    플랫폼 계층
      FMIS
      클라우드
      엣지 게이트웨이
    지능 계층
      AI / 머신러닝
      처방맵 생성
      작황 예측 모델
</pre><p>각 계층의 역할을 정리하면 다음과 같다.</p><table><thead><tr><th>계층</th><th>구성 요소</th><th>역할</th></tr></thead><tbody><tr><td>하드웨어 계층</td><td>센서, 액추에이터, 농기계</td><td>물리 세계의 데이터 수집과 실행</td></tr><tr><td>통신 계층</td><td>CAN, ISOBUS, LoRa, 셀룰러</td><td>데이터 전달 경로 제공</td></tr><tr><td>플랫폼 계층</td><td>FMIS, 클라우드, 엣지</td><td>데이터 저장·관리·통합</td></tr><tr><td>지능 계층</td><td>AI, 처방맵, 예측 모델</td><td>데이터 분석과 의사결정</td></tr></tbody></table><hr><h2 id="_2-노지농업-vs-시설농업" tabindex="-1"><a class="header-anchor" href="#_2-노지농업-vs-시설농업"><span>2. 노지농업 vs 시설농업</span></a></h2><p>스마트농업은 적용 환경에 따라 노지농업과 시설농업으로 구분된다. 두 분야는 제어 대상, 사용 기술, 규모 면에서 상당한 차이가 있다.</p><table><thead><tr><th>항목</th><th>노지농업</th><th>시설농업(스마트팜)</th></tr></thead><tbody><tr><td>재배 환경</td><td>노천, 자연 기상 조건</td><td>온실·비닐하우스, 폐쇄 환경</td></tr><tr><td>주요 기계·장치</td><td>트랙터, 이앙기, 콤바인</td><td>PLC, 환경제어기, 양액기</td></tr><tr><td>통신 표준</td><td>ISOBUS, CAN Bus</td><td>독자 프로토콜, Modbus, RS-485</td></tr><tr><td>제어 대상</td><td>비료·농약 살포량(가변살포)</td><td>온도, 습도, CO2, 광량, 양액 농도</td></tr><tr><td>규모</td><td>수십~수백 ha</td><td>수백~수천 m2</td></tr><tr><td>데이터 수집 주기</td><td>비교적 느림(분~시간 단위)</td><td>빠름(초~분 단위)</td></tr><tr><td>주요 불확실성</td><td>기상 변동, 지형 차이</td><td>에너지 비용, 병해충 내부 발생</td></tr></tbody></table><p>노지농업에서는 <strong>광활한 면적을 효율적으로 관리</strong>하는 것이 핵심 과제이고, 시설농업에서는 <strong>폐쇄 환경의 변수를 정밀하게 제어</strong>하는 것이 핵심이다.</p><hr><h2 id="_3-기술-간-연결-관계" tabindex="-1"><a class="header-anchor" href="#_3-기술-간-연결-관계"><span>3. 기술 간 연결 관계</span></a></h2><p>스마트농업의 핵심 파이프라인은 센서 데이터가 생성되는 시점부터 농기계가 실제로 작업을 수행하는 시점까지 이어진다. 이 스터디의 14개 챕터는 이 파이프라인을 따라 구성된다.</p><pre class="mermaid">flowchart LR
    A[센서 데이터 수집&lt;br&gt;CH3 IoT·센서&lt;br&gt;CH4 드론·위성] --&gt; B[통신&lt;br&gt;CH3 LoRa/NB-IoT&lt;br&gt;CH5 GNSS]
    B --&gt; C[클라우드 / FMIS&lt;br&gt;CH8 데이터 플랫폼]
    C --&gt; D[AI 분석&lt;br&gt;CH9 머신러닝&lt;br&gt;CH10 작황 예측]
    D --&gt; E[처방맵 생성&lt;br&gt;CH4 NDVI&lt;br&gt;CH11 가변살포]
    E --&gt; F[농기계 자동제어&lt;br&gt;CH5 자동조향&lt;br&gt;CH6 ISOBUS&lt;br&gt;CH7 농기계 제어]
    F --&gt; G[작업 이력 기록&lt;br&gt;CH8 FMIS]
    G --&gt; C
</pre><p>각 챕터가 파이프라인의 어느 위치에 해당하는지 파악하면 전체 구조를 이해하는 데 도움이 된다.</p><hr><h2 id="_4-글로벌-트렌드" tabindex="-1"><a class="header-anchor" href="#_4-글로벌-트렌드"><span>4. 글로벌 트렌드</span></a></h2><p>주요국은 각자의 농업 환경과 정책 목표에 따라 스마트농업을 추진하는 방향이 다르다.</p><table><thead><tr><th>국가/지역</th><th>주요 전략</th><th>특징적 기술</th><th>배경</th></tr></thead><tbody><tr><td>미국</td><td>대규모 정밀농업</td><td>자율주행 농기계, 가변살포</td><td>평균 농장 규모 180ha 이상, 효율 극대화</td></tr><tr><td>EU</td><td>환경 규제 기반 스마트농업</td><td>질소 관리, 탄소 발자국 추적</td><td>Farm to Fork 전략, 2030년 농약 50% 감축 목표</td></tr><tr><td>한국</td><td>스마트팜 혁신밸리</td><td>시설 원예 스마트팜, 수직농장</td><td>고령화·소농 구조, 국가 주도 클러스터 조성</td></tr><tr><td>일본</td><td>초고령화 대응 농업 로봇</td><td>수확 로봇, 이앙 자율주행</td><td>농업인 평균 연령 68세, 노동력 대체 긴급</td></tr><tr><td>중국</td><td>대규모 디지털 농업</td><td>드론 방제, 위성 모니터링</td><td>식량 안보 전략, 광대한 농지 관리</td></tr></tbody></table><p>한국의 스마트팜 혁신밸리는 스마트팜 창업 보육, 기술 실증, 청년 농업인 육성을 한 곳에서 수행하는 집약적 모델이다. 2022년 기준 전남 고흥, 경북 상주, 전북 김제, 경남 밀양 4개 거점이 조성됐다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>스마트농업 기술은 하드웨어 → 통신 → 플랫폼 → 지능의 4개 계층으로 구성된다.</li><li>노지농업은 광대한 면적의 가변 관리가 핵심이고, 시설농업은 폐쇄 환경의 정밀 제어가 핵심이다.</li><li>데이터 파이프라인은 센서 수집 → 통신 → 클라우드 → AI 분석 → 처방맵 → 농기계 제어의 순서로 흐른다.</li><li>주요국은 각자의 농업 구조(규모, 고령화, 환경 규제)에 맞춰 다른 방향으로 스마트농업을 추진한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/smart-agriculture/03-iot-sensors">농업 IoT와 센서</a></li></ul>`,26)]))}const h=d(e,[["render",n],["__file","02-technology-map.html.vue"]]),o=JSON.parse('{"path":"/study/smart-agriculture/02-technology-map.html","title":"스마트농업 기술 지도","lang":"en-US","frontmatter":{"title":"스마트농업 기술 지도","description":"스마트농업을 구성하는 기술 영역의 전체 조감도를 이해하고, 노지농업과 시설농업의 차이를 구분한다.","date":"2026-04-13T00:00:00.000Z","tags":["스마트농업","기술지도","노지","시설원예"],"prev":"/study/smart-agriculture/01-what-is-smart-agriculture","next":"/study/smart-agriculture/03-iot-sensors"},"headers":[{"level":1,"title":"스마트농업 기술 지도","slug":"스마트농업-기술-지도","link":"#스마트농업-기술-지도","children":[{"level":2,"title":"1. 기술 스택 조감도","slug":"_1-기술-스택-조감도","link":"#_1-기술-스택-조감도","children":[]},{"level":2,"title":"2. 노지농업 vs 시설농업","slug":"_2-노지농업-vs-시설농업","link":"#_2-노지농업-vs-시설농업","children":[]},{"level":2,"title":"3. 기술 간 연결 관계","slug":"_3-기술-간-연결-관계","link":"#_3-기술-간-연결-관계","children":[]},{"level":2,"title":"4. 글로벌 트렌드","slug":"_4-글로벌-트렌드","link":"#_4-글로벌-트렌드","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/smart-agriculture/02-technology-map.md"}');export{h as comp,o as data};
