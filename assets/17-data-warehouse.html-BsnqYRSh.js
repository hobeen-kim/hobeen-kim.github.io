import{_ as s,c as a,e,o as t}from"./app-BprzU0vx.js";const l={};function i(p,n){return t(),a("div",null,n[0]||(n[0]=[e(`<h1 id="데이터-웨어하우스" tabindex="-1"><a class="header-anchor" href="#데이터-웨어하우스"><span>데이터 웨어하우스</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>OLTP와 OLAP의 목적과 특성 차이를 설명할 수 있다.</li><li>Star 스키마와 Snowflake 스키마의 구조와 팩트/디멘션 테이블의 역할을 이해한다.</li><li>ETL 파이프라인의 각 단계와 CDC 개념을 설명할 수 있다.</li><li>Roll-up, Drill-down, Slice, Dice, Pivot 연산의 의미와 차이를 설명할 수 있다.</li></ul></div><hr><h2 id="_1-oltp-vs-olap" tabindex="-1"><a class="header-anchor" href="#_1-oltp-vs-olap"><span>1. OLTP vs OLAP</span></a></h2><h3 id="비교" tabindex="-1"><a class="header-anchor" href="#비교"><span>비교</span></a></h3><table><thead><tr><th>구분</th><th>OLTP (Online Transaction Processing)</th><th>OLAP (Online Analytical Processing)</th></tr></thead><tbody><tr><td>목적</td><td>일상적인 트랜잭션 처리</td><td>대규모 데이터 분석</td></tr><tr><td>데이터</td><td>현재 운영 데이터 (최신 상태)</td><td>이력 데이터 (수년치 축적)</td></tr><tr><td>쿼리 유형</td><td>단순 INSERT/UPDATE/SELECT (소량 행)</td><td>복잡한 집계, 조인, 집합 연산 (수백만 행)</td></tr><tr><td>정규화</td><td>높음 (중복 최소화)</td><td>낮음 (읽기 최적화, 역정규화)</td></tr><tr><td>응답 시간</td><td>수 ms</td><td>수 초 ~ 수 분</td></tr><tr><td>동시 사용자</td><td>수천 ~ 수만 명</td><td>수십 ~ 수백 명</td></tr><tr><td>예시</td><td>주문 처리, 결제, 재고 관리</td><td>매출 분석, 고객 행동 분석, 경영 리포트</td></tr></tbody></table><h3 id="왜-같은-db로-둘-다-하면-안-되는가" tabindex="-1"><a class="header-anchor" href="#왜-같은-db로-둘-다-하면-안-되는가"><span>왜 같은 DB로 둘 다 하면 안 되는가</span></a></h3><p>OLAP 쿼리는 수백만 건 이상의 데이터를 스캔하며 CPU와 I/O를 대량 소비한다. 같은 DB에서 OLTP와 OLAP을 함께 실행하면 다음 문제가 발생한다.</p><ul><li>OLAP 쿼리가 테이블 락 또는 공유 락을 오래 유지해 OLTP 트랜잭션이 대기 상태에 빠짐</li><li>OLAP의 풀스캔이 버퍼 풀의 OLTP용 캐시 데이터를 밀어내 캐시 히트율 급락</li><li>실시간 서비스 응답 시간이 증가해 사용자 경험 저하</li></ul><p>이 때문에 운영 DB(OLTP)와 분석 DB(OLAP/DW)를 분리하는 것이 일반적이다.</p><hr><h2 id="_2-데이터-웨어하우스-구조" tabindex="-1"><a class="header-anchor" href="#_2-데이터-웨어하우스-구조"><span>2. 데이터 웨어하우스 구조</span></a></h2><h3 id="팩트-테이블과-디멘션-테이블" tabindex="-1"><a class="header-anchor" href="#팩트-테이블과-디멘션-테이블"><span>팩트 테이블과 디멘션 테이블</span></a></h3><p><strong>팩트 테이블(Fact Table)</strong>은 분석 대상인 측정값(Measure)과 디멘션 테이블을 참조하는 FK의 집합이다. 행 수가 매우 많고 자주 집계된다.</p><p><strong>디멘션 테이블(Dimension Table)</strong>은 팩트를 설명하는 속성(Attribute)과 계층(Hierarchy) 정보를 담는다. 팩트 테이블보다 행 수가 적고 잘 변하지 않는다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">팩트 테이블 예시 (sales_fact):</span>
<span class="line">- sale_id (PK)</span>
<span class="line">- date_id (FK → date_dim)</span>
<span class="line">- product_id (FK → product_dim)</span>
<span class="line">- customer_id (FK → customer_dim)</span>
<span class="line">- quantity (측정값)</span>
<span class="line">- amount (측정값)</span>
<span class="line"></span>
<span class="line">디멘션 테이블 예시 (date_dim):</span>
<span class="line">- date_id (PK)</span>
<span class="line">- date, year, quarter, month, day_of_week</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="star-스키마" tabindex="-1"><a class="header-anchor" href="#star-스키마"><span>Star 스키마</span></a></h3><p>팩트 테이블이 중심에 있고 디멘션 테이블이 방사형으로 연결된 구조이다. 쿼리가 단순하고 직관적이며 조인 횟수가 적어 분석 성능이 좋다.</p><pre class="mermaid">erDiagram
    SALES_FACT {
        int sale_id PK
        int date_id FK
        int product_id FK
        int customer_id FK
        int quantity
        decimal amount
    }
    DATE_DIM {
        int date_id PK
        date full_date
        int year
        int quarter
        int month
        string day_of_week
    }
    PRODUCT_DIM {
        int product_id PK
        string product_name
        string category
        string brand
        decimal unit_price
    }
    CUSTOMER_DIM {
        int customer_id PK
        string customer_name
        string region
        string grade
    }
    SALES_FACT }o--|| DATE_DIM : &quot;date_id&quot;
    SALES_FACT }o--|| PRODUCT_DIM : &quot;product_id&quot;
    SALES_FACT }o--|| CUSTOMER_DIM : &quot;customer_id&quot;
</pre><h3 id="snowflake-스키마" tabindex="-1"><a class="header-anchor" href="#snowflake-스키마"><span>Snowflake 스키마</span></a></h3><p>Star 스키마에서 디멘션 테이블을 추가로 정규화한 구조이다. 예를 들어 <code>product_dim</code>의 <code>category</code>를 별도 <code>category_dim</code>으로 분리한다. 데이터 중복은 줄어들지만 조인이 많아져 쿼리가 복잡해진다.</p><table><thead><tr><th>비교</th><th>Star 스키마</th><th>Snowflake 스키마</th></tr></thead><tbody><tr><td>정규화 수준</td><td>낮음 (디멘션 비정규화)</td><td>높음 (디멘션 정규화)</td></tr><tr><td>쿼리 복잡도</td><td>낮음</td><td>높음 (다단계 조인)</td></tr><tr><td>저장 공간</td><td>많이 사용</td><td>절약</td></tr><tr><td>쿼리 성능</td><td>빠름</td><td>상대적으로 느림</td></tr></tbody></table><p>실무에서는 대부분 Star 스키마를 선호한다.</p><hr><h2 id="_3-etl-extract-transform-load" tabindex="-1"><a class="header-anchor" href="#_3-etl-extract-transform-load"><span>3. ETL (Extract-Transform-Load)</span></a></h2><h3 id="etl-개념" tabindex="-1"><a class="header-anchor" href="#etl-개념"><span>ETL 개념</span></a></h3><p><strong>ETL</strong>은 운영 시스템(OLTP DB, 로그, 외부 API 등)에서 데이터를 추출하고, 분석에 적합한 형태로 변환하며, 데이터 웨어하우스에 적재하는 과정이다.</p><p><strong>Extract (추출)</strong> — 소스 시스템에서 데이터를 읽는다. 전체 추출(Full Extract) 또는 변경분만 추출(Incremental Extract)을 사용한다.</p><p><strong>Transform (변환)</strong> — 데이터를 정제, 통합, 집계한다. 중복 제거, 결측값 처리, 코드 변환(예: &#39;M&#39; → &#39;남성&#39;), 여러 소스 통합, 집계 계산 등이 포함된다.</p><p><strong>Load (적재)</strong> — 변환된 데이터를 DW에 저장한다. 전체 교체(Full Load) 또는 증분 추가(Incremental Load) 방식이 있다.</p><h3 id="etl-파이프라인" tabindex="-1"><a class="header-anchor" href="#etl-파이프라인"><span>ETL 파이프라인</span></a></h3><pre class="mermaid">flowchart LR
    subgraph Sources[&quot;소스 시스템&quot;]
        S1[주문 DB]
        S2[고객 DB]
        S3[상품 DB]
    end
    subgraph ETL[&quot;ETL 프로세스&quot;]
        E[Extract&lt;br&gt;데이터 추출]
        T[Transform&lt;br&gt;정제 · 통합 · 집계]
        L[Load&lt;br&gt;DW 적재]
        E --&gt; T --&gt; L
    end
    subgraph DW[&quot;데이터 웨어하우스&quot;]
        F[팩트 테이블]
        D[디멘션 테이블]
    end
    S1 --&gt; E
    S2 --&gt; E
    S3 --&gt; E
    L --&gt; F
    L --&gt; D
</pre><h3 id="cdc-change-data-capture" tabindex="-1"><a class="header-anchor" href="#cdc-change-data-capture"><span>CDC (Change Data Capture)</span></a></h3><p><strong>CDC</strong>는 소스 DB의 변경 사항(INSERT, UPDATE, DELETE)만 실시간 또는 주기적으로 감지해 ETL에 활용하는 기법이다. 전체 테이블을 매번 읽지 않으므로 소스 시스템 부하가 낮고 지연 시간이 짧다.</p><p>MySQL에서는 바이너리 로그(binlog)를 활용한 CDC가 일반적이다. Debezium 같은 오픈소스 툴이 binlog를 읽어 Kafka로 변경 이벤트를 스트리밍한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">[MySQL binlog] → [Debezium] → [Kafka] → [ETL 소비자] → [DW]</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div></div></div><hr><h2 id="_4-olap-연산" tabindex="-1"><a class="header-anchor" href="#_4-olap-연산"><span>4. OLAP 연산</span></a></h2><p>OLAP에서는 다차원 데이터 큐브를 다양한 각도로 분석하는 연산을 사용한다. 온라인 쇼핑몰의 매출 데이터(상품, 지역, 시간 차원)를 예로 든다.</p><h3 id="roll-up-합산-상위-집계" tabindex="-1"><a class="header-anchor" href="#roll-up-합산-상위-집계"><span>Roll-up (합산/상위 집계)</span></a></h3><p>데이터를 상위 계층으로 집계한다. 세부 수준에서 요약 수준으로 올라간다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">일별 매출 → 월별 매출 → 분기별 매출 → 연별 매출</span>
<span class="line">도시별 매출 → 지역별 매출 → 전국 매출</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-sql line-numbers-mode" data-highlighter="prismjs" data-ext="sql" data-title="sql"><pre><code><span class="line"><span class="token comment">-- 일별 → 월별 Roll-up</span></span>
<span class="line"><span class="token keyword">SELECT</span> <span class="token keyword">YEAR</span><span class="token punctuation">(</span>sale_date<span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token keyword">MONTH</span><span class="token punctuation">(</span>sale_date<span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token function">SUM</span><span class="token punctuation">(</span>amount<span class="token punctuation">)</span></span>
<span class="line"><span class="token keyword">FROM</span> sales_fact</span>
<span class="line"><span class="token keyword">GROUP</span> <span class="token keyword">BY</span> <span class="token keyword">YEAR</span><span class="token punctuation">(</span>sale_date<span class="token punctuation">)</span><span class="token punctuation">,</span> <span class="token keyword">MONTH</span><span class="token punctuation">(</span>sale_date<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="drill-down-하위-상세" tabindex="-1"><a class="header-anchor" href="#drill-down-하위-상세"><span>Drill-down (하위 상세)</span></a></h3><p>Roll-up의 반대. 상위 집계에서 세부 데이터로 내려간다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">연별 매출 → 분기별 → 월별 → 일별</span>
<span class="line">전국 매출 → 지역별 → 도시별 → 구별</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="slice-한-차원-고정" tabindex="-1"><a class="header-anchor" href="#slice-한-차원-고정"><span>Slice (한 차원 고정)</span></a></h3><p>여러 차원 중 하나의 차원을 특정 값으로 고정해 2차원 단면을 추출한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">전체 매출 데이터(상품 x 지역 x 시간) 중</span>
<span class="line">시간 차원 = &quot;2024년 1분기&quot;로 고정</span>
<span class="line">→ 2024년 1분기의 상품 x 지역 매출표</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-sql line-numbers-mode" data-highlighter="prismjs" data-ext="sql" data-title="sql"><pre><code><span class="line"><span class="token keyword">SELECT</span> product_id<span class="token punctuation">,</span> region<span class="token punctuation">,</span> <span class="token function">SUM</span><span class="token punctuation">(</span>amount<span class="token punctuation">)</span></span>
<span class="line"><span class="token keyword">FROM</span> sales_fact</span>
<span class="line"><span class="token keyword">WHERE</span> <span class="token keyword">year</span> <span class="token operator">=</span> <span class="token number">2024</span> <span class="token operator">AND</span> quarter <span class="token operator">=</span> <span class="token number">1</span></span>
<span class="line"><span class="token keyword">GROUP</span> <span class="token keyword">BY</span> product_id<span class="token punctuation">,</span> region<span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="dice-여러-차원-조건" tabindex="-1"><a class="header-anchor" href="#dice-여러-차원-조건"><span>Dice (여러 차원 조건)</span></a></h3><p>Slice가 하나의 차원을 고정하는 반면, Dice는 여러 차원에 조건을 적용해 더 작은 하위 큐브를 추출한다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">상품 = &quot;전자제품&quot;</span>
<span class="line">지역 = &quot;서울, 부산&quot;</span>
<span class="line">시간 = &quot;2024년 1~3분기&quot;</span>
<span class="line">→ 위 세 조건을 모두 만족하는 데이터</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-sql line-numbers-mode" data-highlighter="prismjs" data-ext="sql" data-title="sql"><pre><code><span class="line"><span class="token keyword">SELECT</span> product_id<span class="token punctuation">,</span> region<span class="token punctuation">,</span> quarter<span class="token punctuation">,</span> <span class="token function">SUM</span><span class="token punctuation">(</span>amount<span class="token punctuation">)</span></span>
<span class="line"><span class="token keyword">FROM</span> sales_fact</span>
<span class="line"><span class="token keyword">WHERE</span> category <span class="token operator">=</span> <span class="token string">&#39;전자제품&#39;</span></span>
<span class="line">  <span class="token operator">AND</span> region <span class="token operator">IN</span> <span class="token punctuation">(</span><span class="token string">&#39;서울&#39;</span><span class="token punctuation">,</span> <span class="token string">&#39;부산&#39;</span><span class="token punctuation">)</span></span>
<span class="line">  <span class="token operator">AND</span> <span class="token keyword">year</span> <span class="token operator">=</span> <span class="token number">2024</span> <span class="token operator">AND</span> quarter <span class="token operator">IN</span> <span class="token punctuation">(</span><span class="token number">1</span><span class="token punctuation">,</span> <span class="token number">2</span><span class="token punctuation">,</span> <span class="token number">3</span><span class="token punctuation">)</span></span>
<span class="line"><span class="token keyword">GROUP</span> <span class="token keyword">BY</span> product_id<span class="token punctuation">,</span> region<span class="token punctuation">,</span> quarter<span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="pivot-축-회전" tabindex="-1"><a class="header-anchor" href="#pivot-축-회전"><span>Pivot (축 회전)</span></a></h3><p>행과 열의 축을 바꿔 데이터를 재배치한다. 행으로 나열된 데이터를 열로 펼치거나 그 반대를 수행해 가독성 높은 크로스탭 형태로 만든다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">Pivot 전:</span>
<span class="line">region  | quarter | amount</span>
<span class="line">서울    | Q1      | 100</span>
<span class="line">서울    | Q2      | 150</span>
<span class="line">부산    | Q1      | 80</span>
<span class="line">부산    | Q2      | 90</span>
<span class="line"></span>
<span class="line">Pivot 후:</span>
<span class="line">region  | Q1  | Q2</span>
<span class="line">서울    | 100 | 150</span>
<span class="line">부산    | 80  | 90</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><div class="language-sql line-numbers-mode" data-highlighter="prismjs" data-ext="sql" data-title="sql"><pre><code><span class="line"><span class="token comment">-- MySQL에서 CASE WHEN으로 Pivot 구현</span></span>
<span class="line"><span class="token keyword">SELECT</span> region<span class="token punctuation">,</span></span>
<span class="line">    <span class="token function">SUM</span><span class="token punctuation">(</span><span class="token keyword">CASE</span> <span class="token keyword">WHEN</span> quarter <span class="token operator">=</span> <span class="token number">1</span> <span class="token keyword">THEN</span> amount <span class="token keyword">ELSE</span> <span class="token number">0</span> <span class="token keyword">END</span><span class="token punctuation">)</span> <span class="token keyword">AS</span> Q1<span class="token punctuation">,</span></span>
<span class="line">    <span class="token function">SUM</span><span class="token punctuation">(</span><span class="token keyword">CASE</span> <span class="token keyword">WHEN</span> quarter <span class="token operator">=</span> <span class="token number">2</span> <span class="token keyword">THEN</span> amount <span class="token keyword">ELSE</span> <span class="token number">0</span> <span class="token keyword">END</span><span class="token punctuation">)</span> <span class="token keyword">AS</span> Q2<span class="token punctuation">,</span></span>
<span class="line">    <span class="token function">SUM</span><span class="token punctuation">(</span><span class="token keyword">CASE</span> <span class="token keyword">WHEN</span> quarter <span class="token operator">=</span> <span class="token number">3</span> <span class="token keyword">THEN</span> amount <span class="token keyword">ELSE</span> <span class="token number">0</span> <span class="token keyword">END</span><span class="token punctuation">)</span> <span class="token keyword">AS</span> Q3<span class="token punctuation">,</span></span>
<span class="line">    <span class="token function">SUM</span><span class="token punctuation">(</span><span class="token keyword">CASE</span> <span class="token keyword">WHEN</span> quarter <span class="token operator">=</span> <span class="token number">4</span> <span class="token keyword">THEN</span> amount <span class="token keyword">ELSE</span> <span class="token number">0</span> <span class="token keyword">END</span><span class="token punctuation">)</span> <span class="token keyword">AS</span> Q4</span>
<span class="line"><span class="token keyword">FROM</span> sales_fact</span>
<span class="line"><span class="token keyword">WHERE</span> <span class="token keyword">year</span> <span class="token operator">=</span> <span class="token number">2024</span></span>
<span class="line"><span class="token keyword">GROUP</span> <span class="token keyword">BY</span> region<span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="olap-연산-요약" tabindex="-1"><a class="header-anchor" href="#olap-연산-요약"><span>OLAP 연산 요약</span></a></h3><pre class="mermaid">flowchart TD
    Cube[&quot;3D 데이터 큐브&lt;br&gt;(상품 x 지역 x 시간)&quot;]
    Cube --&gt;|&quot;Roll-up&lt;br&gt;세부 → 요약&quot;| RU[&quot;월별 → 분기별 → 연별&quot;]
    Cube --&gt;|&quot;Drill-down&lt;br&gt;요약 → 세부&quot;| DD[&quot;연별 → 월별 → 일별&quot;]
    Cube --&gt;|&quot;Slice&lt;br&gt;차원 1개 고정&quot;| SL[&quot;시간 = 2024 Q1&lt;br&gt;→ 2차원 단면&quot;]
    Cube --&gt;|&quot;Dice&lt;br&gt;여러 차원 조건&quot;| DC[&quot;상품+지역+시간&lt;br&gt;→ 하위 큐브&quot;]
    Cube --&gt;|&quot;Pivot&lt;br&gt;행/열 재배치&quot;| PV[&quot;행 지역 → 열 지역&lt;br&gt;크로스탭&quot;]
</pre><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>OLTP는 빠른 트랜잭션 처리, OLAP는 대용량 분석이 목적이다. 같은 DB에서 병행하면 OLTP 성능이 저하된다.</li><li>Star 스키마는 팩트 테이블(측정값 + FK)과 디멘션 테이블(속성, 계층)로 구성되며, 단순한 구조로 조회 성능이 좋다.</li><li>ETL은 Extract(추출) → Transform(변환) → Load(적재) 순서로 진행하며, CDC는 변경분만 실시간으로 감지한다.</li><li>OLAP 연산: Roll-up(상위 집계), Drill-down(하위 상세), Slice(1차원 고정), Dice(다차원 조건), Pivot(축 회전).</li></ul></div>`,62)]))}const d=s(l,[["render",i],["__file","17-data-warehouse.html.vue"]]),o=JSON.parse('{"path":"/study/database/17-data-warehouse.html","title":"데이터 웨어하우스","lang":"en-US","frontmatter":{"title":"데이터 웨어하우스","description":"OLTP와 OLAP의 차이, 스타 스키마 구조, ETL 파이프라인, OLAP 연산을 학습한다.","date":"2026-04-14T00:00:00.000Z","tags":["데이터베이스","DW","OLAP","OLTP","ETL","정보처리기사"],"prev":"/study/database/16-distributed-db","next":null},"headers":[{"level":1,"title":"데이터 웨어하우스","slug":"데이터-웨어하우스","link":"#데이터-웨어하우스","children":[{"level":2,"title":"1. OLTP vs OLAP","slug":"_1-oltp-vs-olap","link":"#_1-oltp-vs-olap","children":[{"level":3,"title":"비교","slug":"비교","link":"#비교","children":[]},{"level":3,"title":"왜 같은 DB로 둘 다 하면 안 되는가","slug":"왜-같은-db로-둘-다-하면-안-되는가","link":"#왜-같은-db로-둘-다-하면-안-되는가","children":[]}]},{"level":2,"title":"2. 데이터 웨어하우스 구조","slug":"_2-데이터-웨어하우스-구조","link":"#_2-데이터-웨어하우스-구조","children":[{"level":3,"title":"팩트 테이블과 디멘션 테이블","slug":"팩트-테이블과-디멘션-테이블","link":"#팩트-테이블과-디멘션-테이블","children":[]},{"level":3,"title":"Star 스키마","slug":"star-스키마","link":"#star-스키마","children":[]},{"level":3,"title":"Snowflake 스키마","slug":"snowflake-스키마","link":"#snowflake-스키마","children":[]}]},{"level":2,"title":"3. ETL (Extract-Transform-Load)","slug":"_3-etl-extract-transform-load","link":"#_3-etl-extract-transform-load","children":[{"level":3,"title":"ETL 개념","slug":"etl-개념","link":"#etl-개념","children":[]},{"level":3,"title":"ETL 파이프라인","slug":"etl-파이프라인","link":"#etl-파이프라인","children":[]},{"level":3,"title":"CDC (Change Data Capture)","slug":"cdc-change-data-capture","link":"#cdc-change-data-capture","children":[]}]},{"level":2,"title":"4. OLAP 연산","slug":"_4-olap-연산","link":"#_4-olap-연산","children":[{"level":3,"title":"Roll-up (합산/상위 집계)","slug":"roll-up-합산-상위-집계","link":"#roll-up-합산-상위-집계","children":[]},{"level":3,"title":"Drill-down (하위 상세)","slug":"drill-down-하위-상세","link":"#drill-down-하위-상세","children":[]},{"level":3,"title":"Slice (한 차원 고정)","slug":"slice-한-차원-고정","link":"#slice-한-차원-고정","children":[]},{"level":3,"title":"Dice (여러 차원 조건)","slug":"dice-여러-차원-조건","link":"#dice-여러-차원-조건","children":[]},{"level":3,"title":"Pivot (축 회전)","slug":"pivot-축-회전","link":"#pivot-축-회전","children":[]},{"level":3,"title":"OLAP 연산 요약","slug":"olap-연산-요약","link":"#olap-연산-요약","children":[]}]}]}],"git":{},"filePathRelative":"_study/database/17-data-warehouse.md"}');export{d as comp,o as data};
