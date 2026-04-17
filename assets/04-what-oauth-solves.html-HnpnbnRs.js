import{_ as n,c as t,e as s,o as a}from"./app-BprzU0vx.js";const l={};function i(o,e){return a(),t("div",null,e[0]||(e[0]=[s(`<h1 id="oauth는-무엇을-해결했는가" tabindex="-1"><a class="header-anchor" href="#oauth는-무엇을-해결했는가"><span>OAuth는 무엇을 해결했는가</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>권한 위임(delegation)의 개념과 기존 공유 모델과의 차이를 설명할 수 있다.</li><li>OAuth가 해결한 4가지 핵심 문제를 구체적인 시나리오로 열거할 수 있다.</li><li>Scope의 존재 이유와 세분화된 권한 부여가 왜 중요한지 이해한다.</li><li>사용자 동의(Consent) 화면의 역할과 OAuth의 한계(인증 아님)를 안다.</li></ul></div><hr><h2 id="_1-대신-접근한다-는-아이디어" tabindex="-1"><a class="header-anchor" href="#_1-대신-접근한다-는-아이디어"><span>1. &quot;대신 접근한다&quot;는 아이디어</span></a></h2><p>OAuth의 핵심 아이디어는 놀랍도록 단순하다. <strong>&quot;비밀번호 대신, 제한된 권한만 담긴 증표(token)를 건넨다&quot;</strong>는 것이다. 이 문장 하나로 CH1에서 본 4대 문제가 거의 다 풀린다.</p><h3 id="전통적-방식과의-대비" tabindex="-1"><a class="header-anchor" href="#전통적-방식과의-대비"><span>전통적 방식과의 대비</span></a></h3><pre class="mermaid">flowchart LR
    subgraph 과거[기존 - 비밀번호 공유]
        U1[사용자] --&gt;|Gmail ID+PW| APP1[제3자 앱]
        APP1 --&gt;|ID+PW로 로그인| G1[Gmail]
        G1 -.모든 권한 전권.-&gt; APP1
    end
    subgraph 현재[OAuth - 권한 위임]
        U2[사용자] --&gt;|AS에서 동의| AS[Authorization Server]
        AS --&gt;|Scope 제한 토큰| APP2[제3자 앱]
        APP2 --&gt;|Bearer Token| G2[Gmail API]
        G2 -.contacts.readonly 만.-&gt; APP2
    end
    style APP1 fill:#fee
    style APP2 fill:#efe
</pre><p>핵심 전환은 두 가지다.</p><ul><li>사용자가 <strong>제3자 앱이 아니라 인가 서버(AS)</strong>에 직접 인증한다. 제3자 앱은 사용자의 비밀번호를 볼 수 없다.</li><li>제3자 앱이 받는 토큰은 <strong>허용된 범위만</strong> 담고 있다. 토큰으로는 &quot;주소록 읽기&quot;는 가능하지만 &quot;메일 발송&quot;은 불가능할 수 있다.</li></ul><h3 id="위임-delegation-이라는-관계" tabindex="-1"><a class="header-anchor" href="#위임-delegation-이라는-관계"><span>위임(Delegation)이라는 관계</span></a></h3><p>일상 언어로 &quot;위임&quot;은 &quot;A가 자신의 권한 일부를 B에게 맡긴다&quot;는 뜻이다. OAuth의 위임도 같다.</p><table><thead><tr><th>요소</th><th>일상 위임</th><th>OAuth 위임</th></tr></thead><tbody><tr><td>위임자</td><td>본인</td><td>Resource Owner (사용자)</td></tr><tr><td>수임자</td><td>대리인</td><td>Client (제3자 앱)</td></tr><tr><td>권한 범위</td><td>위임장 명시</td><td>Scope</td></tr><tr><td>증거</td><td>위임장</td><td>Access Token</td></tr><tr><td>승인자</td><td>본인 서명</td><td>Consent 화면 승인</td></tr><tr><td>취소</td><td>위임장 파기</td><td>Revocation 엔드포인트</td></tr></tbody></table><p>OAuth는 위임 관계를 <strong>프로토콜 수준에서 명시적으로 표현</strong>한다. 이 명시성이 다음 단계에서 네 가지 문제를 푸는 토대가 된다.</p><hr><h2 id="_2-해결한-4가지" tabindex="-1"><a class="header-anchor" href="#_2-해결한-4가지"><span>2. 해결한 4가지</span></a></h2><p>CH1에서 나열한 비밀번호 공유의 4대 문제(유출·전권·취소 불가·감사 불가)를 OAuth가 각각 어떻게 풀었는지 본다.</p><h3 id="문제-1-—-비밀번호-유출-방지" tabindex="-1"><a class="header-anchor" href="#문제-1-—-비밀번호-유출-방지"><span>문제 1 — 비밀번호 유출 방지</span></a></h3><p>OAuth에서 클라이언트는 사용자 비밀번호를 <strong>본 적도 없고 저장하지도 않는다</strong>. 사용자는 오직 AS(인가 서버) 도메인에서만 비밀번호를 입력한다. 클라이언트는 결과물인 토큰만 받는다.</p><pre class="mermaid">sequenceDiagram
    participant U as 사용자
    participant C as 클라이언트
    participant AS as 인가 서버
    C-&gt;&gt;U: AS로 리다이렉트 (로그인·동의)
    U-&gt;&gt;AS: AS 도메인에서만 비밀번호 입력
    AS-&gt;&gt;AS: 비밀번호 검증
    AS--&gt;&gt;C: Access Token 반환
    Note over C: 비밀번호를 본 적 없음
</pre><p>클라이언트가 털려도 <strong>토큰만 노출</strong>된다. 토큰은 스코프가 제한되어 있고, 만료되며, 폐기 가능하다. 비밀번호 유출에 비해 피해 반경이 훨씬 작다.</p><h3 id="문제-2-—-최소-권한-scope" tabindex="-1"><a class="header-anchor" href="#문제-2-—-최소-권한-scope"><span>문제 2 — 최소 권한(Scope)</span></a></h3><p>Scope는 &quot;이 토큰으로 무엇을 할 수 있는가&quot;를 문자열로 표현한 것이다. AS가 토큰을 발급할 때 어떤 Scope를 포함시킬지 결정한다.</p><div class="language-http line-numbers-mode" data-highlighter="prismjs" data-ext="http" data-title="http"><pre><code><span class="line">POST /authorize?</span>
<span class="line">    response_type=code</span>
<span class="line">    &amp;client_id=abc123</span>
<span class="line">    &amp;scope=contacts.readonly%20calendar.events.readonly</span>
<span class="line">    &amp;redirect_uri=https://app.example.com/cb</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>이 요청은 &quot;주소록 읽기&quot;와 &quot;캘린더 이벤트 읽기&quot; 두 권한만 요구한다. 사용자가 동의 화면에서 승인하면, 발급되는 토큰은 오직 이 두 범위 안에서만 동작한다. 메일 발송, 파일 업로드 같은 다른 API 호출은 <code>403 Forbidden</code>으로 거부된다.</p><p>Scope의 실무적 이점은 다음과 같다.</p><ul><li><strong>최소 권한 원칙(Principle of Least Privilege)</strong>: 앱이 필요 이상 권한을 갖지 않는다.</li><li><strong>사용자 신뢰</strong>: 동의 화면에 &quot;주소록 읽기만 허용&quot;이라고 명시되면 사용자가 안심한다.</li><li><strong>피해 억제</strong>: 토큰이 탈취돼도 허용 범위 이상은 할 수 없다.</li></ul><h3 id="문제-3-—-사용자가-취소-가능" tabindex="-1"><a class="header-anchor" href="#문제-3-—-사용자가-취소-가능"><span>문제 3 — 사용자가 취소 가능</span></a></h3><p>OAuth는 토큰 단위의 취소(Revocation)를 <strong>프로토콜로 정의</strong>한다. RFC 7009가 표준화한 <code>/revoke</code> 엔드포인트다.</p><div class="language-http line-numbers-mode" data-highlighter="prismjs" data-ext="http" data-title="http"><pre><code><span class="line"><span class="token request-line"><span class="token method property">POST</span> <span class="token request-target url">/oauth/revoke</span> <span class="token http-version property">HTTP/1.1</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Host</span><span class="token punctuation">:</span> <span class="token header-value">auth.example.com</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Authorization</span><span class="token punctuation">:</span> <span class="token header-value">Basic &lt;client credentials&gt;</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Content-Type</span><span class="token punctuation">:</span> <span class="token header-value">application/x-www-form-urlencoded</span></span></span>
<span class="line"></span>
<span class="line">token=eyJhbGc...&amp;token_type_hint=refresh_token</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>또한 사용자는 AS의 계정 관리 페이지에서 &quot;연결된 앱&quot; 목록을 보고 원하는 앱의 권한을 한 번에 취소할 수 있다.</p><pre class="mermaid">flowchart LR
    U[사용자] --&gt;|연결된 앱 관리| AS[AS 계정 페이지]
    AS --&gt; L[연결된 앱 목록]
    L --&gt; A1[앱 A - 연결 끊기]
    L --&gt; A2[앱 B - 유지]
    L --&gt; A3[앱 C - 유지]
    A1 --&gt;|토큰 즉시 폐기| INV[해당 앱 토큰만 무효]
    style INV fill:#fee
</pre><p>중요한 것은 <strong>비밀번호를 바꾸지 않아도 된다</strong>는 점이다. 앱 A만 연결을 끊으면 앱 B, C는 정상 동작을 유지한다. 이 입도(granularity)는 비밀번호 공유 시대에는 불가능했다.</p><h3 id="문제-4-—-감사-audit-가능" tabindex="-1"><a class="header-anchor" href="#문제-4-—-감사-audit-가능"><span>문제 4 — 감사(Audit) 가능</span></a></h3><p>OAuth에서 모든 API 호출은 <strong>어떤 토큰으로</strong> 들어왔는지 식별된다. 토큰에는 다음 정보가 결합되어 있다.</p><ul><li>사용자(Resource Owner)</li><li>클라이언트(Client ID)</li><li>Scope</li><li>발급 시각·만료 시각</li><li>세션/디바이스 정보 (확장)</li></ul><p>자원 서버의 로그를 분석하면 &quot;사용자 42가 2026-04-17 10:23:45에 <strong>앱 Notion</strong>에게 <code>drive.readonly</code> 권한을 위임했고, 그 토큰으로 <code>/drive/files/xxx</code>를 조회했다&quot;처럼 책임 소재가 명확하게 추적된다.</p><p>비정상 패턴 탐지도 가능하다. 같은 토큰이 갑자기 해외에서 사용된다거나, 평소와 다른 Scope를 호출한다거나 하는 이상 행동을 토큰 단위로 감지할 수 있다.</p><hr><h2 id="_3-사용자-동의-consent-화면의-역할" tabindex="-1"><a class="header-anchor" href="#_3-사용자-동의-consent-화면의-역할"><span>3. 사용자 동의(Consent) 화면의 역할</span></a></h2><p>&quot;앱이 당신의 구글 캘린더에 접근해도 될까요?&quot; 우리가 익숙한 이 화면이 Consent(동의) 화면이다. OAuth의 설계에서 Consent는 <strong>법적·윤리적 장치</strong>의 역할도 겸한다.</p><h3 id="consent-화면의-네-가지-기능" tabindex="-1"><a class="header-anchor" href="#consent-화면의-네-가지-기능"><span>Consent 화면의 네 가지 기능</span></a></h3><pre class="mermaid">flowchart TD
    CN[Consent 화면] --&gt; F1[정보 공개&lt;br&gt;어떤 앱이 요청하는지]
    CN --&gt; F2[범위 공개&lt;br&gt;어떤 Scope를 요구하는지]
    CN --&gt; F3[선택권 부여&lt;br&gt;Scope별 허용·거부 가능]
    CN --&gt; F4[법적 증빙&lt;br&gt;사용자 승인 기록 보존]
</pre><ol><li><strong>정보 공개</strong>: 어떤 클라이언트가 요청하는지 이름·로고·도메인을 표시한다. 피싱 앱을 식별할 단서가 된다.</li><li><strong>범위 공개</strong>: 요청된 Scope를 사람이 읽을 수 있는 형태로 나열한다. (&quot;이 앱은 주소록을 읽을 수 있어요&quot;)</li><li><strong>선택권 부여</strong>: Google·Facebook 등 주요 IdP는 Scope별로 개별 허용/거부가 가능하다.</li><li><strong>법적 증빙</strong>: 사용자 승인이 기록된다. GDPR·개인정보보호법상 &quot;정보주체의 동의&quot;의 근거가 된다.</li></ol><h3 id="consent-화면-예시" tabindex="-1"><a class="header-anchor" href="#consent-화면-예시"><span>Consent 화면 예시</span></a></h3><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">[Google 계정 로고]</span>
<span class="line">홍길동님, Notion에서 Google 계정에 접근하려고 합니다.</span>
<span class="line"></span>
<span class="line">Notion이 다음 작업을 수행할 수 있도록 허용하시겠습니까?</span>
<span class="line"></span>
<span class="line">  [v] 내 기본 계정 정보 보기</span>
<span class="line">  [v] 내 Google Drive 파일 조회 (읽기 전용)</span>
<span class="line">  [ ] Google Drive 파일 수정</span>
<span class="line"></span>
<span class="line">  [거부]          [허용]</span>
<span class="line"></span>
<span class="line">이 권한은 언제든지 https://myaccount.google.com 에서 취소할 수 있습니다.</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="consent-fatigue-문제" tabindex="-1"><a class="header-anchor" href="#consent-fatigue-문제"><span>Consent Fatigue 문제</span></a></h3><p>실무에서 Consent 화면이 너무 자주 뜨면 사용자가 <strong>무조건 &quot;허용&quot;을 누르는 습관</strong>이 생긴다. 이를 Consent Fatigue라고 한다. 주요 IdP는 이 문제를 다음처럼 완화한다.</p><ul><li>같은 앱·같은 Scope는 한 번 승인 후 일정 기간 재표시 안 함</li><li>Scope를 최소 단위로 세분화 유도</li><li>새로운 Scope 추가 시에만 재확인 요구</li><li>&quot;필수&quot; vs &quot;선택&quot; Scope 구분</li></ul><hr><h2 id="_4-scope가-없었다면" tabindex="-1"><a class="header-anchor" href="#_4-scope가-없었다면"><span>4. Scope가 없었다면</span></a></h2><p>Scope는 OAuth의 핵심 발명품 중 하나다. 없다면 어떤 일이 벌어지는지 구체적인 Google Drive 예시로 본다.</p><h3 id="google-drive-scope-예시" tabindex="-1"><a class="header-anchor" href="#google-drive-scope-예시"><span>Google Drive Scope 예시</span></a></h3><p>Google Drive API는 다음과 같이 세분화된 Scope를 제공한다.</p><table><thead><tr><th>Scope</th><th>의미</th></tr></thead><tbody><tr><td><code>drive.file</code></td><td>앱이 생성/연 파일만</td></tr><tr><td><code>drive.readonly</code></td><td>모든 파일 읽기 전용</td></tr><tr><td><code>drive.metadata.readonly</code></td><td>파일 메타데이터만 읽기</td></tr><tr><td><code>drive.appdata</code></td><td>앱 전용 숨김 폴더만</td></tr><tr><td><code>drive</code></td><td>모든 파일 읽기·쓰기·삭제 (전체 권한)</td></tr></tbody></table><h3 id="scope-계층" tabindex="-1"><a class="header-anchor" href="#scope-계층"><span>Scope 계층</span></a></h3><pre class="mermaid">mindmap
  root((drive.*))
    drive
      drive.file
        사용자가 연 파일만
      drive.appdata
        앱 숨김 폴더만
    읽기
      drive.readonly
        전체 읽기
      drive.metadata.readonly
        메타만
    쓰기
      drive.file
      drive
    삭제
      drive
</pre><h3 id="시나리오-비교" tabindex="-1"><a class="header-anchor" href="#시나리오-비교"><span>시나리오 비교</span></a></h3><p>&quot;파일 업로드 기능만 있는 단순 백업 앱&quot;을 만든다고 하자.</p><table><thead><tr><th>선택</th><th>효과</th></tr></thead><tbody><tr><td><code>drive.file</code></td><td>앱이 직접 생성한 파일만 접근. 사용자 기존 파일은 건드리지 못함. 안전.</td></tr><tr><td><code>drive</code></td><td>사용자 모든 파일에 대한 전권. 백업 앱이 해킹되면 모든 파일 유출·삭제 가능.</td></tr></tbody></table><p>최소 권한 원칙대로 <code>drive.file</code>을 선택하는 것이 옳다. Scope가 없다면 이런 선택 자체가 불가능하다.</p><h3 id="scope-설계-가이드" tabindex="-1"><a class="header-anchor" href="#scope-설계-가이드"><span>Scope 설계 가이드</span></a></h3><p>AS(인가 서버)를 직접 운영하는 경우 Scope 설계는 중요한 결정이다.</p><ul><li><strong>동사·명사 조합</strong>: <code>read:profile</code>, <code>write:posts</code>처럼 동작과 자원을 명시한다.</li><li><strong>자원 계층 반영</strong>: <code>org:admin</code>, <code>team:write</code>처럼 조직 구조를 반영한다.</li><li><strong>최소 단위 분리</strong>: 읽기와 쓰기를 합치지 않는다.</li><li><strong>사람이 읽을 설명</strong>: 동의 화면에 표시할 한국어·영어 설명을 함께 정의한다.</li></ul><div class="language-yaml line-numbers-mode" data-highlighter="prismjs" data-ext="yml" data-title="yml"><pre><code><span class="line"><span class="token comment"># AS scope 정의 예시</span></span>
<span class="line"><span class="token key atrule">scopes</span><span class="token punctuation">:</span></span>
<span class="line">  <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> contacts.readonly</span>
<span class="line">    <span class="token key atrule">description_ko</span><span class="token punctuation">:</span> 주소록 읽기</span>
<span class="line">    <span class="token key atrule">description_en</span><span class="token punctuation">:</span> Read your contacts</span>
<span class="line">  <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> contacts.write</span>
<span class="line">    <span class="token key atrule">description_ko</span><span class="token punctuation">:</span> 주소록 추가·수정</span>
<span class="line">    <span class="token key atrule">description_en</span><span class="token punctuation">:</span> Create and modify contacts</span>
<span class="line">  <span class="token punctuation">-</span> <span class="token key atrule">name</span><span class="token punctuation">:</span> calendar.events.readonly</span>
<span class="line">    <span class="token key atrule">description_ko</span><span class="token punctuation">:</span> 캘린더 일정 조회</span>
<span class="line">    <span class="token key atrule">description_en</span><span class="token punctuation">:</span> View your calendar events</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><hr><h2 id="_5-oauth의-한계" tabindex="-1"><a class="header-anchor" href="#_5-oauth의-한계"><span>5. OAuth의 한계</span></a></h2><p>OAuth가 모든 걸 해결한 것은 아니다. CH3에서 이미 짚었듯, OAuth는 <strong>인증을 책임지지 않는다</strong>. 이 한계는 OIDC로 보완된다.</p><h3 id="oauth-혼자-할-수-없는-것" tabindex="-1"><a class="header-anchor" href="#oauth-혼자-할-수-없는-것"><span>OAuth 혼자 할 수 없는 것</span></a></h3><ol><li><strong>사용자 로그인(인증)</strong> — Access Token으로 사용자 신원을 확정하는 것은 위험하다.</li><li><strong>사용자 정보 표준화</strong> — &quot;이름&quot;, &quot;이메일&quot;을 담는 표준 필드가 없다. 각 IdP가 임의 정의한다.</li><li><strong>세션 관리</strong> — 싱글 로그아웃(Single Logout), 세션 타임아웃 표준이 없다.</li><li><strong>토큰 포맷 규정</strong> — Access Token이 opaque인지 JWT인지, 어떤 필드를 담는지 명시되지 않는다.</li></ol><h3 id="oidc는-이-공백을-채운다" tabindex="-1"><a class="header-anchor" href="#oidc는-이-공백을-채운다"><span>OIDC는 이 공백을 채운다</span></a></h3><pre class="mermaid">flowchart TB
    OA[OAuth 2.0&lt;br&gt;인가 프레임워크] --&gt; OL[한계]
    OL --&gt; L1[사용자 신원 확정 불가]
    OL --&gt; L2[사용자 정보 표준 없음]
    OL --&gt; L3[싱글 로그아웃 없음]
    OIDC[OpenID Connect] --&gt; A1[ID Token JWT]
    OIDC --&gt; A2[표준 Claim]
    OIDC --&gt; A3[UserInfo 엔드포인트]
    OIDC --&gt; A4[Discovery &amp; JWKS]
    A1 --&gt; L1
    A2 --&gt; L2
    A3 --&gt; L2
    A4 --&gt; L3
    style OA fill:#eef
    style OIDC fill:#efe
</pre><p>OIDC는 OAuth 2.0 위에 <strong>얇은 인증 레이어</strong>를 얹는다. 핵심은 <code>openid</code> scope를 요청하면 함께 받게 되는 <strong>ID Token</strong>이다. 이 JWT는 서명된 상태로 &quot;누가(sub), 언제(iat), 어디(iss) 발급했고, 누구(aud)를 위한 것인지&quot; 표준 필드로 명시한다.</p><h3 id="이-챕터의-위치" tabindex="-1"><a class="header-anchor" href="#이-챕터의-위치"><span>이 챕터의 위치</span></a></h3><pre class="mermaid">flowchart LR
    CH1[CH1&lt;br&gt;왜 필요한가] --&gt; CH2[CH2&lt;br&gt;토큰 채택 이유]
    CH2 --&gt; CH3[CH3&lt;br&gt;인증 vs 인가]
    CH3 --&gt; CH4[CH4&lt;br&gt;현재 위치]
    CH4 --&gt; CH5[CH5&lt;br&gt;4가지 역할]
    CH5 --&gt; CH6[CH6&lt;br&gt;Authorization Code Flow]
    CH4 --&gt; CH9[CH9&lt;br&gt;OIDC 왜]
    style CH4 fill:#efe
</pre><p>다음 챕터에서는 OAuth가 정의하는 <strong>4가지 역할</strong>(Resource Owner, Client, AS, RS)과 실제 <strong>엔드포인트·토큰 용어</strong>를 본격적으로 정리한다. 이 용어들이 잡히면 Authorization Code Flow 같은 실제 플로우를 보는 시야가 열린다.</p><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>OAuth의 본질은 &quot;비밀번호 대신 제한된 권한 토큰을 건넨다&quot;는 권한 위임(delegation) 모델이다. AS에서만 비밀번호를 입력하고 클라이언트는 토큰만 받는다.</li><li>OAuth는 비밀번호 유출 방지, 최소 권한(Scope) 부여, 사용자 취소 가능(/revoke), 토큰 단위 감사 가능이라는 4대 문제를 구조적으로 해결했다.</li><li>Consent 화면은 정보 공개·범위 공개·선택권·법적 증빙을 제공하며, Scope는 최소 권한 원칙을 실현하는 핵심 도구다. Google Drive의 <code>drive.file</code> vs <code>drive</code> 예시가 대표적이다.</li><li>OAuth는 인증을 책임지지 않는다. 사용자 신원 확정과 세션 관리가 필요하면 OpenID Connect가 필요하며, 이는 CH9에서 본격적으로 다룬다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>이전 : <a href="/study/oauth/03-authn-vs-authz">인증과 인가는 어떻게 다른가</a></li><li>다음 : <a href="/study/oauth/05-roles-and-terms">4가지 역할과 용어</a></li></ul>`,79)]))}const d=n(l,[["render",i],["__file","04-what-oauth-solves.html.vue"]]),c=JSON.parse('{"path":"/study/oauth/04-what-oauth-solves.html","title":"OAuth는 무엇을 해결했는가","lang":"en-US","frontmatter":{"title":"OAuth는 무엇을 해결했는가","description":"OAuth의 권한 위임 모델과 그것이 기존 방식 대비 얻어낸 이득을 정리한다.","date":"2026-04-17T00:00:00.000Z","tags":["OAuth","권한위임","Delegation"],"prev":"/study/oauth/03-authn-vs-authz","next":"/study/oauth/05-roles-and-terms"},"headers":[{"level":1,"title":"OAuth는 무엇을 해결했는가","slug":"oauth는-무엇을-해결했는가","link":"#oauth는-무엇을-해결했는가","children":[{"level":2,"title":"1. \\"대신 접근한다\\"는 아이디어","slug":"_1-대신-접근한다-는-아이디어","link":"#_1-대신-접근한다-는-아이디어","children":[{"level":3,"title":"전통적 방식과의 대비","slug":"전통적-방식과의-대비","link":"#전통적-방식과의-대비","children":[]},{"level":3,"title":"위임(Delegation)이라는 관계","slug":"위임-delegation-이라는-관계","link":"#위임-delegation-이라는-관계","children":[]}]},{"level":2,"title":"2. 해결한 4가지","slug":"_2-해결한-4가지","link":"#_2-해결한-4가지","children":[{"level":3,"title":"문제 1 — 비밀번호 유출 방지","slug":"문제-1-—-비밀번호-유출-방지","link":"#문제-1-—-비밀번호-유출-방지","children":[]},{"level":3,"title":"문제 2 — 최소 권한(Scope)","slug":"문제-2-—-최소-권한-scope","link":"#문제-2-—-최소-권한-scope","children":[]},{"level":3,"title":"문제 3 — 사용자가 취소 가능","slug":"문제-3-—-사용자가-취소-가능","link":"#문제-3-—-사용자가-취소-가능","children":[]},{"level":3,"title":"문제 4 — 감사(Audit) 가능","slug":"문제-4-—-감사-audit-가능","link":"#문제-4-—-감사-audit-가능","children":[]}]},{"level":2,"title":"3. 사용자 동의(Consent) 화면의 역할","slug":"_3-사용자-동의-consent-화면의-역할","link":"#_3-사용자-동의-consent-화면의-역할","children":[{"level":3,"title":"Consent 화면의 네 가지 기능","slug":"consent-화면의-네-가지-기능","link":"#consent-화면의-네-가지-기능","children":[]},{"level":3,"title":"Consent 화면 예시","slug":"consent-화면-예시","link":"#consent-화면-예시","children":[]},{"level":3,"title":"Consent Fatigue 문제","slug":"consent-fatigue-문제","link":"#consent-fatigue-문제","children":[]}]},{"level":2,"title":"4. Scope가 없었다면","slug":"_4-scope가-없었다면","link":"#_4-scope가-없었다면","children":[{"level":3,"title":"Google Drive Scope 예시","slug":"google-drive-scope-예시","link":"#google-drive-scope-예시","children":[]},{"level":3,"title":"Scope 계층","slug":"scope-계층","link":"#scope-계층","children":[]},{"level":3,"title":"시나리오 비교","slug":"시나리오-비교","link":"#시나리오-비교","children":[]},{"level":3,"title":"Scope 설계 가이드","slug":"scope-설계-가이드","link":"#scope-설계-가이드","children":[]}]},{"level":2,"title":"5. OAuth의 한계","slug":"_5-oauth의-한계","link":"#_5-oauth의-한계","children":[{"level":3,"title":"OAuth 혼자 할 수 없는 것","slug":"oauth-혼자-할-수-없는-것","link":"#oauth-혼자-할-수-없는-것","children":[]},{"level":3,"title":"OIDC는 이 공백을 채운다","slug":"oidc는-이-공백을-채운다","link":"#oidc는-이-공백을-채운다","children":[]},{"level":3,"title":"이 챕터의 위치","slug":"이-챕터의-위치","link":"#이-챕터의-위치","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/oauth/04-what-oauth-solves.md"}');export{d as comp,c as data};
