import{_ as o,c as u,a,b as s,d as r,f as l,r as p,o as d,e as t}from"./app-BitF5Zgk.js";const v={},k={class:"table-of-contents"};function m(b,n){const i=p("Header"),e=p("router-link"),c=p("Footer");return d(),u("div",null,[a(i),s("nav",k,[s("ul",null,[s("li",null,[a(e,{to:"#_1-테스트-커버리지-툴을-도입한-이유"},{default:l(()=>n[0]||(n[0]=[t("1. 테스트 커버리지 툴을 도입한 이유")])),_:1}),s("ul",null,[s("li",null,[a(e,{to:"#목표"},{default:l(()=>n[1]||(n[1]=[t("목표")])),_:1})])])]),s("li",null,[a(e,{to:"#_2-테스트-커버리지-툴"},{default:l(()=>n[2]||(n[2]=[t("2. 테스트 커버리지 툴")])),_:1}),s("ul",null,[s("li",null,[a(e,{to:"#kover"},{default:l(()=>n[3]||(n[3]=[t("Kover")])),_:1})]),s("li",null,[a(e,{to:"#diff-cover"},{default:l(()=>n[4]||(n[4]=[t("diff-cover")])),_:1})])])]),s("li",null,[a(e,{to:"#_3-도입-방법"},{default:l(()=>n[5]||(n[5]=[t("3. 도입 방법")])),_:1}),s("ul",null,[s("li",null,[a(e,{to:"#gradle에-kover-추가"},{default:l(()=>n[6]||(n[6]=[t("Gradle에 Kover 추가")])),_:1})]),s("li",null,[a(e,{to:"#github-actions와-통합"},{default:l(()=>n[7]||(n[7]=[t("GitHub Actions와 통합")])),_:1})]),s("li",null,[a(e,{to:"#결과물"},{default:l(()=>n[8]||(n[8]=[t("결과물")])),_:1})])])])])]),n[9]||(n[9]=r(`<h1 id="_1-테스트-커버리지-툴을-도입한-이유" tabindex="-1"><a class="header-anchor" href="#_1-테스트-커버리지-툴을-도입한-이유"><span>1. 테스트 커버리지 툴을 도입한 이유</span></a></h1><p>테스트 코드를 모두 작성한 이후, 테스트 문화를 정착하기 위해 (비록 거의 혼자 코드를 짜고 있지만) 테스트 결과와 커버리지를 PR 메시지로 생성하도록 구현했다. 처음에는 테스트 커버리지 목표를 설정하려고 했으나 현재 상황에서 숫자 자체는 무의미하다고 생각하여 목표는 따로 없이 측정만 하도록 했다.</p><h2 id="목표" tabindex="-1"><a class="header-anchor" href="#목표"><span>목표</span></a></h2><ul><li>CI 와 커버리지 확인을 통합</li><li>신규/변경 라인 커버리지(diff coverage)를 수치로 보여준다.</li><li>전체 커버리지도 함께 보되, 머지 기준은 변경분에 둔다. (현재는 목표 설정 x)</li></ul><h1 id="_2-테스트-커버리지-툴" tabindex="-1"><a class="header-anchor" href="#_2-테스트-커버리지-툴"><span>2. 테스트 커버리지 툴</span></a></h1><h3 id="kover" tabindex="-1"><a class="header-anchor" href="#kover"><span>Kover</span></a></h3><p><strong>뭐 하는 툴인가</strong></p><ul><li>Kotlin/JVM 프로젝트의 커버리지를 뽑는 <strong>Gradle 플러그인</strong>이다.</li><li>내부적으로 IntelliJ 커버리지 엔진을 쓰고, <strong>JaCoCo XML 포맷</strong>을 뱉는다. 그래서 다른 도구(예: diff-cover)와 바로 물린다.</li><li>Kotlin의 인라인 함수, <code>data class</code> 생성 코드, 디폴트 인자 등에서 <strong>라인 매칭이 JaCoCo보다 자연스러운 경우가 많다.</strong></li></ul><p><strong>왜 Kover를 썼나 (장점)</strong></p><ul><li><strong>Kotlin 친화적</strong>이다. 코틀린 특유의 생성 코드 때문에 커버리지 라인이 어색하게 잡히는 문제를 줄였다.</li><li><strong>설정이 간단</strong>하다. 플러그인만 추가하면 <code>koverXmlReport</code>, <code>koverHtmlReport</code> 같은 태스크가 바로 생긴다.</li><li>**필터(Exclude)**가 유연하다. 패키지/클래스/파일/어노테이션 기준으로 제외할 수 있어 잡음(예: <code>config</code>, DTO, 생성코드)을 정리하기 좋다.</li></ul><p><strong>설치/사용</strong><code>build.gradle.kts</code></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">plugins {</span>
<span class="line">    kotlin(&quot;jvm&quot;) version &quot;1.9.24&quot;</span>
<span class="line">    id(&quot;org.jetbrains.kotlinx.kover&quot;) version &quot;0.8.3&quot;</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">tasks.test { useJUnitPlatform() }</span>
<span class="line"></span>
<span class="line">/**</span>
<span class="line"> * 리포트 생성 (기본 경로 예)</span>
<span class="line"> *  - XML:  build/reports/kover/report.xml</span>
<span class="line"> *  - HTML: build/reports/kover/html/index.html</span>
<span class="line"> */</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>자주 쓰는 태스크</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line"># 테스트 + XML</span>
<span class="line">./gradlew test koverXmlReport</span>
<span class="line"></span>
<span class="line"># HTML 리포트까지</span>
<span class="line">./gradlew test koverHtmlReport</span>
<span class="line"></span>
<span class="line"># (루트에서) 멀티모듈 집계 XML/HTML</span>
<span class="line">./gradlew :koverXmlReport :koverHtmlReport</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><strong>필터링(노이즈 줄이기)</strong></p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">kover {</span>
<span class="line">    filters {</span>
<span class="line">        classes {</span>
<span class="line">            excludes += listOf(</span>
<span class="line">                &quot;com.example.config.*&quot;,</span>
<span class="line">                &quot;com.example.generated.*&quot;,</span>
<span class="line">                &quot;*.ApplicationKt&quot;</span>
<span class="line">            )</span>
<span class="line">        }</span>
<span class="line">        // 필요하면 패키지/파일/어노테이션 단위도 가능</span>
<span class="line">    }</span>
<span class="line">}</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><blockquote><p>팁: “커버리지 0% 찍히는 파일”은 대개 <strong>생성 코드</strong>거나 <strong>테스트에서 로드되지 않은 경로</strong>다. 필터에서 과감히 제외하거나, 테스트로 실제 사용 경로를 태우면 된다.</p></blockquote><h3 id="diff-cover" tabindex="-1"><a class="header-anchor" href="#diff-cover"><span>diff-cover</span></a></h3><ul><li><p>**JaCoCo XML 리포트 + <code>git diff</code>**를 비교해서 <strong>“이번 변경 라인들의 커버리지”</strong>(diff coverage)를 계산한다.</p><ul><li>출력 형식은 <strong>텍스트/ANSI/Markdown/HTML/JSON/XML</strong>을 지원한다. PR 코멘트/체크/아티팩트 등 용도에 맞춰 뽑을 수 있다.</li></ul><p><strong>왜 diff-cover를 썼나 (장점)</strong></p><ul><li><strong>변경분 중심의 품질 관리</strong>가 된다. 전체 커버리지 수치가 높아도 <strong>새로 바꾼 코드가 비어 있으면</strong> 바로 잡아낸다.</li><li><strong>머지 기준으로 쓰기 좋다.</strong> <code>--fail-under 80</code>처럼 임계치를 걸어 <strong>체크 실패 → 머지 차단</strong> 흐름을 만들 수 있다.</li></ul></li><li><p><strong>도입이 빠르다.</strong> Kover가 내는 XML만 있으면 바로 적용된다. 빌드 파이프라인에 거의 영향 없다.</p><ul><li><strong>출력 포맷이 풍부</strong>해서 PR 코멘트/HTML 리포트/머신 파싱(JSON)까지 한 번에 해결한다.</li></ul></li></ul><p><strong>Kover + diff-cover 시너지</strong></p><ul><li>Kover는 <strong>정확한 Kotlin 라인 매핑 + JaCoCo XML</strong>을 제공하고, diff-cover는 그 XML로 <strong>변경분 커버리지</strong>를 계산한다.</li><li>둘을 엮으면 **“전체 커버리지(헬스 체크)” + “변경분 커버리지(머지 기준)”**를 동시에 만족하는 파이프라인을 아주 간단히 만든다.</li><li>특히 코틀린 프로젝트에서 **불필요한 라인(생성 코드)**을 Kover 필터로 빼고, 나머지를 diff-cover로 집요하게 본다. 리뷰 스트레스가 줄고, 실패도 **“정말 필요한 실패”**만 난다.</li></ul><h1 id="_3-도입-방법" tabindex="-1"><a class="header-anchor" href="#_3-도입-방법"><span>3. 도입 방법</span></a></h1><h3 id="gradle에-kover-추가" tabindex="-1"><a class="header-anchor" href="#gradle에-kover-추가"><span>Gradle에 Kover 추가</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">plugins {</span>
<span class="line">    ...</span>
<span class="line">    </span>
<span class="line">    id(&quot;org.jetbrains.kotlinx.kover&quot;) version &quot;0.9.1&quot; // Kover 플러그인</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line">tasks.test {</span>
<span class="line">    useJUnitPlatform()</span>
<span class="line">}</span>
<span class="line"></span>
<span class="line"></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>해당 plugin 을 추가하면 <code>./gradlew koverXmlReport</code> 명령어를 사용할 수 있다. <code>build/reports/kover/</code> 위치에 report.xml 을 생성해준다. 해당 리포트는 전체 테스트에 대한 커버리지이다.</p><h2 id="github-actions와-통합" tabindex="-1"><a class="header-anchor" href="#github-actions와-통합"><span>GitHub Actions와 통합</span></a></h2><p>목표는 <strong>PR에 스티키 코멘트 1개</strong>로 <code>전체 커버리지 + 변경분 커버리지</code>를 남기는 것이다.</p><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line">.github/workflows/diff<span class="token punctuation">-</span>coverage.yml</span>
<span class="line"><span class="token key atrule">name</span><span class="token punctuation">:</span> Diff Coverage (Kover + diff<span class="token punctuation">-</span>cover)</span>
<span class="line"></span>
<span class="line"><span class="token key atrule">on</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">pull_request</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">branches</span><span class="token punctuation">:</span> <span class="token punctuation">[</span> main <span class="token punctuation">]</span></span>
<span class="line"></span>
<span class="line"><span class="token key atrule">permissions</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">contents</span><span class="token punctuation">:</span> read</span>
<span class="line">  <span class="token key atrule">pull-requests</span><span class="token punctuation">:</span> write</span>
<span class="line"></span>
<span class="line"><span class="token key atrule">jobs</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token key atrule">diff-coverage</span><span class="token punctuation">:</span></span>
<span class="line">    <span class="token key atrule">runs-on</span><span class="token punctuation">:</span> ubuntu<span class="token punctuation">-</span>latest</span>
<span class="line">    <span class="token key atrule">env</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token key atrule">THRESHOLD</span><span class="token punctuation">:</span> <span class="token string">&quot;80&quot;</span></span>
<span class="line">      <span class="token key atrule">COVER_XML</span><span class="token punctuation">:</span> build/reports/kover/report.xml</span>
<span class="line"></span>
<span class="line">    <span class="token key atrule">steps</span><span class="token punctuation">:</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Checkout</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> actions/checkout@v4</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">fetch-depth</span><span class="token punctuation">:</span> <span class="token number">0</span></span>
<span class="line"></span>
<span class="line">      <span class="token comment"># JDK + Gradle 캐시</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Set up JDK</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> actions/setup<span class="token punctuation">-</span>java@v4</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">distribution</span><span class="token punctuation">:</span> temurin</span>
<span class="line">          <span class="token key atrule">java-version</span><span class="token punctuation">:</span> <span class="token string">&quot;21&quot;</span></span>
<span class="line">          <span class="token key atrule">cache</span><span class="token punctuation">:</span> gradle</span>
<span class="line"></span>
<span class="line">      <span class="token comment"># 프로젝트 .gradle 캐시(증분 빌드 가속)</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Cache project .gradle</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> actions/cache@v3</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">path</span><span class="token punctuation">:</span> .gradle</span>
<span class="line">          <span class="token key atrule">key</span><span class="token punctuation">:</span> gradle<span class="token punctuation">-</span>project<span class="token punctuation">-</span>$<span class="token punctuation">{</span><span class="token punctuation">{</span> runner.os <span class="token punctuation">}</span><span class="token punctuation">}</span><span class="token punctuation">-</span>$<span class="token punctuation">{</span><span class="token punctuation">{</span> hashFiles(&#39;<span class="token important">**/*.gradle*&#39;</span><span class="token punctuation">,</span> &#39;<span class="token important">**/gradle-wrapper.properties&#39;)</span> <span class="token punctuation">}</span><span class="token punctuation">}</span></span>
<span class="line">          <span class="token key atrule">restore-keys</span><span class="token punctuation">:</span> gradle<span class="token punctuation">-</span>project<span class="token punctuation">-</span>$<span class="token punctuation">{</span><span class="token punctuation">{</span> runner.os <span class="token punctuation">}</span><span class="token punctuation">}</span><span class="token punctuation">-</span></span>
<span class="line"></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Build &amp; Test (Kover XML)</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> ./gradlew <span class="token punctuation">-</span><span class="token punctuation">-</span>no<span class="token punctuation">-</span>daemon test koverXmlReport</span>
<span class="line"></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Verify coverage XML exists</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token scalar string"></span>
<span class="line">          test -f &quot;\${{ env.COVER_XML }}&quot; || {</span>
<span class="line">            echo &quot;Coverage XML not found at \${{ env.COVER_XML }}&quot;; exit 1;</span>
<span class="line">          }</span></span>
<span class="line"></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Set up Python</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> actions/setup<span class="token punctuation">-</span>python@v5</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">python-version</span><span class="token punctuation">:</span> <span class="token string">&quot;3.x&quot;</span></span>
<span class="line"></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Install diff<span class="token punctuation">-</span>cover</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> pip install diff<span class="token punctuation">-</span>cover</span>
<span class="line"></span>
<span class="line">      <span class="token comment"># 로그에 요약 + 임계치 체크(미달 시 실패)</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Diff coverage (fail<span class="token punctuation">-</span>under + log)</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token scalar string"></span>
<span class="line">          diff-cover &quot;\${{ env.COVER_XML }}&quot; \\</span>
<span class="line">            --compare-branch origin/\${{ github.base_ref || &#39;main&#39; }} \\</span>
<span class="line">            --src-roots src/main/kotlin src/test/kotlin \\</span>
<span class="line">            --fail-under &quot;\${{ env.THRESHOLD }}&quot; \\</span>
<span class="line">            --format ansi:-</span></span>
<span class="line"></span>
<span class="line">      <span class="token comment"># HTML/Markdown 리포트 생성</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Diff coverage (reports)</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token scalar string"></span>
<span class="line">          diff-cover &quot;\${{ env.COVER_XML }}&quot; \\</span>
<span class="line">            --compare-branch origin/\${{ github.base_ref || &#39;main&#39; }} \\</span>
<span class="line">            --src-roots src/main/kotlin src/test/kotlin \\</span>
<span class="line">            --format html:diff-cover.html,markdown:diff-cover.md</span></span>
<span class="line"></span>
<span class="line">      <span class="token comment"># 전체/변경 파일 커버리지 수치를 추출(코멘트는 만들지 않음)</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> JaCoCo coverage summary (no comment)</span>
<span class="line">        <span class="token key atrule">id</span><span class="token punctuation">:</span> jacoco</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> madrapps/jacoco<span class="token punctuation">-</span>report@v1.7.2</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">paths</span><span class="token punctuation">:</span> $<span class="token punctuation">{</span><span class="token punctuation">{</span> github.workspace <span class="token punctuation">}</span><span class="token punctuation">}</span>/$<span class="token punctuation">{</span><span class="token punctuation">{</span> env.COVER_XML <span class="token punctuation">}</span><span class="token punctuation">}</span></span>
<span class="line">          <span class="token key atrule">token</span><span class="token punctuation">:</span> $<span class="token punctuation">{</span><span class="token punctuation">{</span> secrets.GITHUB_TOKEN <span class="token punctuation">}</span><span class="token punctuation">}</span></span>
<span class="line">          <span class="token key atrule">min-coverage-overall</span><span class="token punctuation">:</span> <span class="token number">0</span></span>
<span class="line">          <span class="token key atrule">min-coverage-changed-files</span><span class="token punctuation">:</span> <span class="token number">0</span></span>
<span class="line">          <span class="token key atrule">comment-type</span><span class="token punctuation">:</span> <span class="token string">&quot;none&quot;</span></span>
<span class="line"></span>
<span class="line">      <span class="token comment"># diff-cover.md -&gt; 테이블 변환 + summary 덧붙여 최종 코멘트 생성</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Merge coverage reports (build pr<span class="token punctuation">-</span>comment.md)</span>
<span class="line">        <span class="token key atrule">run</span><span class="token punctuation">:</span> <span class="token punctuation">|</span><span class="token scalar string"></span>
<span class="line">          echo &quot;# 📊 Coverage Report&quot; &gt; pr-comment.md</span>
<span class="line">          echo &quot;&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;- Overall coverage: **\${{ steps.jacoco.outputs[&#39;coverage-overall&#39;] }}**&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;- Changed files coverage: **\${{ steps.jacoco.outputs[&#39;coverage-changed-files&#39;] }}**&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;### 🔍 Diff Coverage&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;|Files|Diff Coverage (%)|Missing lines|&quot; &gt;&gt; pr-comment.md</span>
<span class="line">          echo &quot;|-----|-----------------|--------------|&quot; &gt;&gt; pr-comment.md</span></span>
<span class="line"></span>
<span class="line">          <span class="token comment"># 3번째 줄부터 읽고, 빈 줄은 무시, &#39;## Summary&#39; 만나면 종료</span></span>
<span class="line">          tail <span class="token punctuation">-</span>n +3 diff<span class="token punctuation">-</span>cover.md <span class="token punctuation">|</span> while read <span class="token punctuation">-</span>r line; do</span>
<span class="line">            <span class="token punctuation">[</span><span class="token punctuation">[</span> <span class="token punctuation">-</span>z &quot;$line&quot; <span class="token punctuation">]</span><span class="token punctuation">]</span> <span class="token important">&amp;&amp;</span> continue</span>
<span class="line">            <span class="token punctuation">[</span><span class="token punctuation">[</span> &quot;$line&quot; == &quot;<span class="token comment">## Summary&quot;* ]] &amp;&amp; break</span></span>
<span class="line"></span>
<span class="line">            file=$(echo &quot;$line&quot;    <span class="token punctuation">|</span> sed <span class="token punctuation">-</span>E &#39;s/^<span class="token punctuation">-</span> (<span class="token punctuation">[</span>^(<span class="token punctuation">]</span>+) .<span class="token important">*/\\1/&#39;)</span></span>
<span class="line">            percent=$(echo &quot;$line&quot; <span class="token punctuation">|</span> sed <span class="token punctuation">-</span>E &#39;s/.<span class="token important">*\\((</span><span class="token punctuation">[</span>0<span class="token punctuation">-</span><span class="token number">9.</span><span class="token punctuation">]</span>+%)\\).<span class="token important">*/\\1/&#39;)</span></span>
<span class="line">            missing=$(echo &quot;$line&quot; <span class="token punctuation">|</span> grep <span class="token punctuation">-</span>o &#39;Missing lines.<span class="token important">*&#39;</span> <span class="token punctuation">|</span> sed <span class="token punctuation">-</span>E &#39;s/Missing lines //&#39;)</span>
<span class="line">            <span class="token punctuation">[</span><span class="token punctuation">[</span> <span class="token punctuation">-</span>z &quot;$missing&quot; <span class="token punctuation">]</span><span class="token punctuation">]</span> <span class="token important">&amp;&amp;</span> missing=&quot; &quot;</span>
<span class="line"></span>
<span class="line">            <span class="token comment"># 경로 앞 6개 컴포넌트 제거 (src/main/kotlin/... 기준)</span></span>
<span class="line">            short_file=$(echo &quot;$file&quot; <span class="token punctuation">|</span> cut <span class="token punctuation">-</span>d&#39;/&#39; <span class="token punctuation">-</span>f7<span class="token punctuation">-</span>)</span>
<span class="line"></span>
<span class="line">            echo &quot;<span class="token punctuation">|</span>$short_file<span class="token punctuation">|</span>$percent<span class="token punctuation">|</span>$missing<span class="token punctuation">|</span>&quot; <span class="token punctuation">&gt;</span><span class="token punctuation">&gt;</span> pr<span class="token punctuation">-</span>comment.md</span>
<span class="line">          done</span>
<span class="line"></span>
<span class="line">          echo &quot;&quot; <span class="token punctuation">&gt;</span><span class="token punctuation">&gt;</span> pr<span class="token punctuation">-</span>comment.md</span>
<span class="line">          <span class="token comment"># 원본의 Summary 블록 추가</span></span>
<span class="line">          awk &#39;/^<span class="token comment">## Summary/{flag=1} flag&#39; diff-cover.md &gt;&gt; pr-comment.md</span></span>
<span class="line"></span>
<span class="line">      <span class="token comment"># 스티키 코멘트로 PR에 1개만 유지</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Post PR comment (sticky)</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> marocchino/sticky<span class="token punctuation">-</span>pull<span class="token punctuation">-</span>request<span class="token punctuation">-</span>comment@v2</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">path</span><span class="token punctuation">:</span> pr<span class="token punctuation">-</span>comment.md</span>
<span class="line"></span>
<span class="line">      <span class="token comment"># HTML 리포트는 아티팩트로 업로드(다운로드해서 열어보기)</span></span>
<span class="line">      <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> Upload HTML report</span>
<span class="line">        <span class="token key atrule">uses</span><span class="token punctuation">:</span> actions/upload<span class="token punctuation">-</span>artifact@v4</span>
<span class="line">        <span class="token key atrule">with</span><span class="token punctuation">:</span></span>
<span class="line">          <span class="token key atrule">name</span><span class="token punctuation">:</span> diff<span class="token punctuation">-</span>cover<span class="token punctuation">-</span>report</span>
<span class="line">          <span class="token key atrule">path</span><span class="token punctuation">:</span> diff<span class="token punctuation">-</span>cover.html</span>
<span class="line">          <span class="token key atrule">if-no-files-found</span><span class="token punctuation">:</span> error</span>
<span class="line">          <span class="token key atrule">retention-days</span><span class="token punctuation">:</span> <span class="token number">14</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h2 id="결과물" tabindex="-1"><a class="header-anchor" href="#결과물"><span>결과물</span></a></h2><ol><li>Test Results : 테스트 보고서다. 실패한다면 git actions 의 summary 에 실패 로그가 추가된다.</li><li>Test Coverage Report : 커밋된 내용의 테스트 커버리지 보고서</li></ol><p>![screencapture-github-hobeen-kim-kovertest-pull-6-2025-08-25-15_19_17 (1)](/images/2025-08-20-test2/screencapture-github-hobeen-kim-kovertest-pull-6-2025-08-25-15_19_17 (1).png) )</p>`,31)),a(c)])}const f=o(v,[["render",m],["__file","2025-08-20-test2.html.vue"]]),h=JSON.parse('{"path":"/posts/spring/2025-08-20-test2.html","title":"테스트가 업무다 - 2 (CICD: kover, diff-cover)","lang":"en-US","frontmatter":{"title":"테스트가 업무다 - 2 (CICD: kover, diff-cover)","date":"2025-08-19T00:00:00.000Z","tags":["kover","diff-cover"],"description":"회사에서 테스트 코드를 작성하면서 얻은 인사이트입니다."},"headers":[{"level":1,"title":"1. 테스트 커버리지 툴을 도입한 이유","slug":"_1-테스트-커버리지-툴을-도입한-이유","link":"#_1-테스트-커버리지-툴을-도입한-이유","children":[{"level":2,"title":"목표","slug":"목표","link":"#목표","children":[]}]},{"level":1,"title":"2. 테스트 커버리지 툴","slug":"_2-테스트-커버리지-툴","link":"#_2-테스트-커버리지-툴","children":[{"level":3,"title":"Kover","slug":"kover","link":"#kover","children":[]},{"level":3,"title":"diff-cover","slug":"diff-cover","link":"#diff-cover","children":[]}]},{"level":1,"title":"3. 도입 방법","slug":"_3-도입-방법","link":"#_3-도입-방법","children":[{"level":3,"title":"Gradle에 Kover 추가","slug":"gradle에-kover-추가","link":"#gradle에-kover-추가","children":[]},{"level":2,"title":"GitHub Actions와 통합","slug":"github-actions와-통합","link":"#github-actions와-통합","children":[]},{"level":2,"title":"결과물","slug":"결과물","link":"#결과물","children":[]}]}],"git":{},"filePathRelative":"_posts/spring/2025-08-20-test2.md"}');export{f as comp,h as data};
