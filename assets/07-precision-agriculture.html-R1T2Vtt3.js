import{_ as l,c as i,e as r,o as n}from"./app-CXdp2zNn.js";const a={};function e(s,t){return n(),i("div",null,t[0]||(t[0]=[r(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>정밀농업의 &quot;적시, 적소, 적량&quot; 원칙과 경제적 효과를 설명할 수 있다.</li><li>데이터 수집 → 분석 → 실행 → 평가의 사이클 전 과정을 이해한다.</li><li>처방맵의 구조와 TC가 이를 실시간으로 활용하는 방식을 설명할 수 있다.</li><li>수확량 매핑이 다음 시즌 처방맵과 어떻게 연결되는지 이해한다.</li></ul></div><h2 id="정밀농업이란" tabindex="-1"><a class="header-anchor" href="#정밀농업이란"><span>정밀농업이란</span></a></h2><p>정밀농업(Precision Agriculture)은 <strong>적시(Right Time), 적소(Right Place), 적량(Right Amount)</strong>의 세 원칙에 따라 농업 자원을 투입하는 방식이다. 필지 전체에 동일한 양을 살포하는 균일 살포 방식과 달리, 구역별로 실제 필요한 양만 정확히 투입한다.</p><p>균일 살포 방식의 문제점은 다음과 같다.</p><ul><li>토양 비옥도가 낮은 구역에는 비료가 부족해 수확량이 저조하다.</li><li>토양 비옥도가 높은 구역에는 비료가 과잉 투입되어 비용이 낭비되고 환경을 오염시킨다.</li><li>전체 필지를 최대 투입량 기준으로 관리하면 필연적으로 일부 구역에서 과잉이 발생한다.</li></ul><p>가변 살포로 전환 시 얻을 수 있는 경제적 효과는 다음과 같다.</p><table><thead><tr><th>항목</th><th>효과</th></tr></thead><tbody><tr><td>비료 절감</td><td>15~30%</td></tr><tr><td>농약 절감</td><td>10~20%</td></tr><tr><td>수확량 향상</td><td>5~10%</td></tr><tr><td>환경 부담(질소 유출)</td><td>20~40% 감소</td></tr></tbody></table><pre class="mermaid">flowchart LR
    A[균일 살포&lt;br&gt;필지 전체 동일량] --&gt; B{구역별 토양 상태}
    B --&gt;|비옥도 낮음| C[투입 부족&lt;br&gt;수확량 저조]
    B --&gt;|비옥도 높음| D[투입 과잉&lt;br&gt;비용 낭비·환경오염]
    E[가변 살포&lt;br&gt;구역별 처방량] --&gt; F[투입 최적화&lt;br&gt;비료 15~30% 절감&lt;br&gt;수확량 5~10% 향상]
</pre><h2 id="데이터-수집-→-분석-→-실행-사이클" tabindex="-1"><a class="header-anchor" href="#데이터-수집-→-분석-→-실행-사이클"><span>데이터 수집 → 분석 → 실행 사이클</span></a></h2><p>정밀농업은 단발성 기술이 아니라 매 시즌 반복되는 데이터 사이클이다.</p><pre class="mermaid">sequenceDiagram
    participant SOIL as 토양 샘플링·&lt;br&gt;위성 영상
    participant GIS as GIS 분석 시스템
    participant MAP as 처방맵
    participant TC as TC(작업 컨트롤러)
    participant HARV as 수확기&lt;br&gt;유량 센서+GPS

    SOIL-&gt;&gt;GIS: 토양 성분, NDVI 영상 전달
    GIS-&gt;&gt;GIS: 구역 분류(Zones)&lt;br&gt;영양 결핍 분석
    GIS-&gt;&gt;MAP: 처방맵 생성(ISOXML)
    MAP-&gt;&gt;TC: 처방맵 업로드
    TC-&gt;&gt;TC: GPS 위치와 처방맵 대조&lt;br&gt;실시간 살포량 명령 생성
    TC--&gt;&gt;HARV: 가변 살포 실행
    HARV-&gt;&gt;GIS: 수확량 맵 데이터 전달
    GIS-&gt;&gt;MAP: 다음 시즌 처방맵 업데이트
</pre><p>각 단계의 구체적인 내용은 다음과 같다.</p><p><strong>1단계 - 데이터 수집</strong></p><ul><li>토양 샘플링: 격자(Grid) 또는 구역(Zone) 단위로 토양을 채취해 pH, 질소·인산·칼륨 농도를 분석한다.</li><li>위성·드론 영상: NDVI(정규화 식생 지수)로 작물의 생육 균일성과 스트레스 구역을 파악한다.</li><li>수확량 기록: 이전 시즌 수확량 맵이 토양 데이터와 함께 기본 입력 데이터가 된다.</li></ul><p><strong>2단계 - GIS 분석·구역 분류</strong></p><ul><li>수집된 데이터를 GIS(지리 정보 시스템) 도구로 레이어별 분석한다.</li><li>k-means 클러스터링 등으로 필지를 비옥도·수분·pH 기준 관리 구역(Management Zone)으로 분류한다.</li></ul><p><strong>3단계 - 처방맵 생성 및 실행</strong></p><ul><li>구역별 최적 투입량을 담은 처방맵을 ISOXML 형식으로 생성한다.</li><li>TC가 GPS 위치와 처방맵을 실시간 대조하여 작업기에 살포량 명령을 전달한다.</li></ul><p><strong>4단계 - 수확량 매핑으로 결과 평가</strong></p><ul><li>수확기에 장착된 유량 센서와 GPS로 구역별 수확량을 기록한다.</li><li>수확량 맵이 다음 시즌 처방맵 생성의 핵심 입력 데이터가 된다.</li></ul><h2 id="처방맵-prescription-map" tabindex="-1"><a class="header-anchor" href="#처방맵-prescription-map"><span>처방맵(Prescription Map)</span></a></h2><p>처방맵은 필지를 격자(Grid) 또는 관리 구역으로 나누고, 각 구역에 적용할 살포량(비료·농약·씨앗)을 지정한 데이터 파일이다.</p><p>처방맵의 핵심 특성은 다음과 같다.</p><ul><li><strong>형식</strong>: ISOXML(ISO 11783-10 기반). TC가 직접 읽을 수 있는 농업 표준 형식이다.</li><li><strong>좌표 정보</strong>: 각 격자 셀에 지오레퍼런스(경위도 또는 UTM 좌표)가 포함된다.</li><li><strong>작업 변수</strong>: 셀마다 비료 투입량, 씨앗 파종 간격, 농약 살포율 등이 지정된다.</li></ul><p>TC(작업 컨트롤러)가 처방맵을 실행하는 방식은 다음과 같다.</p><ol><li>트랙터의 RTK GPS가 현재 위치를 TC에 제공한다.</li><li>TC는 처방맵에서 현재 위치에 해당하는 셀의 살포량을 조회한다.</li><li>해당 살포량 값을 작업기 ECU에 명령으로 전송한다.</li><li>작업기 ECU가 모터·밸브를 제어해 지정된 양을 정확히 살포한다.</li></ol><pre class="mermaid">flowchart TD
    A[처방맵&lt;br&gt;ISOXML 형식&lt;br&gt;격자별 살포량 지정] --&gt; B[TC 업로드]
    B --&gt; C{RTK GPS&lt;br&gt;현재 위치}
    C --&gt;|위치 → 격자 조회| D[해당 격자의&lt;br&gt;살포량 값 추출]
    D --&gt; E[작업기 ECU에&lt;br&gt;명령 전송]
    E --&gt; F[모터·밸브 제어&lt;br&gt;실시간 살포량 조절]
</pre><h2 id="수확량-매핑-yield-mapping" tabindex="-1"><a class="header-anchor" href="#수확량-매핑-yield-mapping"><span>수확량 매핑(Yield Mapping)</span></a></h2><p>수확량 매핑은 수확기 작업 중 유량 센서와 GPS를 결합해 필지의 위치별 수확량을 실시간으로 기록하는 기술이다.</p><p>수확량 매핑의 구성 요소는 다음과 같다.</p><ul><li><strong>질량 유량 센서</strong>: 콤바인의 곡물 엘리베이터에 장착되어 단위 시간당 수확량을 측정한다.</li><li><strong>수분 센서</strong>: 곡물 수분 함량을 측정해 표준 수분(14%)으로 보정한 수확량을 계산한다.</li><li><strong>RTK GPS</strong>: 수확 지점의 정확한 위치를 기록한다.</li><li><strong>데이터 로거</strong>: 유량·수분·위치·시각 데이터를 초 단위로 통합 저장한다.</li></ul><p>수확량 매핑의 결과물이 중요한 이유는 다음과 같다.</p><ul><li>균일해 보이는 필지에도 수확량 편차가 20~40%에 달하는 구역이 숨겨져 있다.</li><li>수확량 맵과 토양 분석 데이터를 중첩하면 수확량이 낮은 원인을 파악할 수 있다.</li><li>이 분석 결과가 다음 시즌의 처방맵 생성에 직접 반영되는 피드백 루프가 형성된다.</li></ul><pre class="mermaid">flowchart LR
    A[수확량 매핑&lt;br&gt;유량 센서 + GPS] --&gt; B[수확량 맵&lt;br&gt;위치별 수확량 기록]
    B --&gt; C[GIS 분석&lt;br&gt;토양 데이터와 중첩]
    C --&gt; D[원인 파악&lt;br&gt;저수확 구역 식별]
    D --&gt; E[처방맵 업데이트&lt;br&gt;다음 시즌 가변살포 계획]
    E --&gt; F[가변 살포 실행&lt;br&gt;TC + 작업기 ECU]
    F --&gt; A
</pre><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>정밀농업의 핵심은 &quot;적시·적소·적량&quot; 원칙으로, 가변 살포를 통해 비료 15~30%를 절감하고 수확량을 5~10% 향상시킬 수 있다.</li><li>데이터 수집 → GIS 분석·구역 분류 → 처방맵 생성 → TC 기반 가변 살포 → 수확량 매핑의 5단계 사이클이 매 시즌 반복된다.</li><li>처방맵은 ISOXML 형식으로 저장되며, TC가 RTK GPS 위치와 대조해 실시간으로 살포량을 조절한다.</li><li>수확량 매핑 데이터는 다음 시즌 처방맵의 핵심 입력값이 되어 시스템이 시즌마다 개선되는 피드백 루프를 형성한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/smart-agriculture/08-smart-irrigation">스마트 관개</a></li></ul>`,37)]))}const p=l(a,[["render",e],["__file","07-precision-agriculture.html.vue"]]),o=JSON.parse('{"path":"/study/smart-agriculture/07-precision-agriculture.html","title":"정밀농업","lang":"en-US","frontmatter":{"title":"정밀농업","description":"가변살포, 처방맵, 수확량 매핑 등 정밀농업의 핵심 개념과 실제 적용 과정을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["스마트농업","정밀농업","가변살포","처방맵","수확량매핑"]},"headers":[{"level":2,"title":"정밀농업이란","slug":"정밀농업이란","link":"#정밀농업이란","children":[]},{"level":2,"title":"데이터 수집 → 분석 → 실행 사이클","slug":"데이터-수집-→-분석-→-실행-사이클","link":"#데이터-수집-→-분석-→-실행-사이클","children":[]},{"level":2,"title":"처방맵(Prescription Map)","slug":"처방맵-prescription-map","link":"#처방맵-prescription-map","children":[]},{"level":2,"title":"수확량 매핑(Yield Mapping)","slug":"수확량-매핑-yield-mapping","link":"#수확량-매핑-yield-mapping","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}],"git":{},"filePathRelative":"_study/smart-agriculture/07-precision-agriculture.md"}');export{p as comp,o as data};
