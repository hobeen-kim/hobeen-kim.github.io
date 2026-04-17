import{_ as t,c as n,e as a,o as s}from"./app-BprzU0vx.js";const r={};function i(l,e){return s(),n("div",null,e[0]||(e[0]=[a(`<h1 id="_4가지-역할과-용어" tabindex="-1"><a class="header-anchor" href="#_4가지-역할과-용어"><span>4가지 역할과 용어</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>OAuth의 4가지 역할(Resource Owner, Client, Authorization Server, Resource Server)과 각자의 책임을 설명할 수 있다.</li><li>인가 서버의 두 핵심 엔드포인트(<code>/authorize</code>, <code>/token</code>)의 용도를 구분한다.</li><li>Public Client와 Confidential Client의 차이, 왜 Native·SPA가 Public으로 분류되는지 안다.</li><li>Client ID와 Client Secret의 의미와 보관 위치의 원칙을 이해한다.</li></ul></div><hr><h2 id="_1-resource-owner-—-자원의-주인" tabindex="-1"><a class="header-anchor" href="#_1-resource-owner-—-자원의-주인"><span>1. Resource Owner — 자원의 주인</span></a></h2><p>Resource Owner는 <strong>자원의 주인</strong>이다. OAuth가 &quot;누구의 권한을 위임하는가&quot;라고 물으면, 바로 이 Resource Owner의 권한이다. 대부분의 경우 <strong>사용자(End User)</strong>가 곧 Resource Owner다.</p><h3 id="정의와-책임" tabindex="-1"><a class="header-anchor" href="#정의와-책임"><span>정의와 책임</span></a></h3><blockquote><p>Resource Owner — 보호된 자원에 대한 접근을 승인할 수 있는 엔티티. 사람인 경우 End User라고도 한다. (RFC 6749 §1.1)</p></blockquote><p>책임은 단순하다.</p><ul><li>AS에서 자신의 신원을 인증한다(로그인).</li><li>Consent 화면에서 클라이언트의 접근 요청을 승인하거나 거부한다.</li><li>언제든 발급된 토큰을 취소할 수 있다.</li></ul><h3 id="resource-owner가-사람이-아닌-경우" tabindex="-1"><a class="header-anchor" href="#resource-owner가-사람이-아닌-경우"><span>Resource Owner가 사람이 아닌 경우</span></a></h3><p>반드시 사람일 필요는 없다. <strong>M2M(Machine-to-Machine)</strong> 시나리오에서는 조직(organization) 또는 서비스 계정 자체가 Resource Owner가 된다. 이 경우 Client Credentials Grant(CH7)가 쓰이고, 사용자 개입 없이 클라이언트가 AS에서 직접 토큰을 받는다.</p><table><thead><tr><th>유형</th><th>Resource Owner</th><th>예시</th></tr></thead><tbody><tr><td>사용자 위임</td><td>개인 사용자</td><td>내 Gmail에 접근하는 Notion</td></tr><tr><td>M2M</td><td>조직·서비스 계정</td><td>배치 서버가 API 호출</td></tr><tr><td>제3자 사용자</td><td>다른 사람 사용자</td><td>고객이 사용하는 SaaS 기능</td></tr></tbody></table><h3 id="resource-owner-vs-end-user" tabindex="-1"><a class="header-anchor" href="#resource-owner-vs-end-user"><span>Resource Owner vs End User</span></a></h3><p>RFC는 두 용어를 미묘하게 구분한다. 대부분 문맥에서는 혼용해도 되지만, M2M 시나리오를 다룰 때는 <strong>Resource Owner = 조직</strong>, <strong>End User = 실사용자</strong>처럼 달라질 수 있다는 점을 의식해 둔다.</p><hr><h2 id="_2-client-—-접근하려는-앱" tabindex="-1"><a class="header-anchor" href="#_2-client-—-접근하려는-앱"><span>2. Client — 접근하려는 앱</span></a></h2><p>Client는 <strong>자원에 접근하려는 애플리케이션</strong>이다. 웹 백엔드, 모바일 앱, SPA, CLI 도구, 서버 데몬까지 모두 클라이언트에 해당한다. 사용자를 대신해서 자원 서버를 호출하는 주체다.</p><h3 id="정의와-책임-1" tabindex="-1"><a class="header-anchor" href="#정의와-책임-1"><span>정의와 책임</span></a></h3><blockquote><p>Client — Resource Owner의 승인을 받아 보호된 자원에 접근 요청을 하는 애플리케이션. (RFC 6749 §1.1)</p></blockquote><p>책임은 다음과 같다.</p><ul><li>AS에 자신을 등록하고 Client ID를 받는다.</li><li>사용자를 AS로 리다이렉트해 인증·동의를 받는다.</li><li>받아낸 토큰을 안전하게 보관한다.</li><li>자원 서버 호출 시 <code>Authorization: Bearer &lt;token&gt;</code> 헤더를 첨부한다.</li><li>토큰이 만료되면 Refresh Token으로 갱신하거나 사용자를 다시 인증시킨다.</li></ul><h3 id="클라이언트의-유형" tabindex="-1"><a class="header-anchor" href="#클라이언트의-유형"><span>클라이언트의 유형</span></a></h3><pre class="mermaid">flowchart TB
    CL[OAuth Client] --&gt; W[Web Server App]
    CL --&gt; N[Native App&lt;br&gt;iOS/Android/Desktop]
    CL --&gt; S[Single Page App&lt;br&gt;브라우저 JS]
    CL --&gt; M[Machine-to-Machine&lt;br&gt;서버 데몬·CLI]
    W -.-&gt; C1[Confidential]
    N -.-&gt; C2[Public]
    S -.-&gt; C2
    M -.-&gt; C1
    style C1 fill:#efe
    style C2 fill:#ffe
</pre><p>각 유형별로 권장되는 Grant Type이 다르다. 이는 CH6·CH7에서 다룬다.</p><hr><h2 id="_3-authorization-server-as-—-권한을-승인하고-토큰을-발급" tabindex="-1"><a class="header-anchor" href="#_3-authorization-server-as-—-권한을-승인하고-토큰을-발급"><span>3. Authorization Server (AS) — 권한을 승인하고 토큰을 발급</span></a></h2><p>AS는 OAuth 생태계의 심장이다. 사용자를 인증하고, Consent를 받고, 토큰을 발급한다. 실무에서는 Google·Kakao 같은 IdP의 AS를 쓰거나 Keycloak·Auth0·Okta 같은 솔루션을 자체 구축한다.</p><h3 id="정의와-책임-2" tabindex="-1"><a class="header-anchor" href="#정의와-책임-2"><span>정의와 책임</span></a></h3><blockquote><p>Authorization Server — 사용자 인증과 권한 승인 후 클라이언트에게 Access Token을 발급하는 서버. (RFC 6749 §1.1)</p></blockquote><p>책임은 넓다.</p><ul><li>사용자 인증 (비밀번호·MFA·생체 등)</li><li>클라이언트 등록 관리 (Client ID·Secret·redirect_uri)</li><li>Consent 화면 제공 및 승인 기록 보존</li><li>Authorization Code 발급 (Authorization Code Flow)</li><li>Access Token·Refresh Token 발급 및 서명</li><li>토큰 검증 엔드포인트 제공 (Introspection)</li><li>토큰 취소 엔드포인트 제공 (Revocation)</li><li>세션·로그아웃 관리</li></ul><h3 id="as의-두-핵심-엔드포인트" tabindex="-1"><a class="header-anchor" href="#as의-두-핵심-엔드포인트"><span>AS의 두 핵심 엔드포인트</span></a></h3><p>OAuth 2.0에서 AS는 최소 두 개의 HTTP 엔드포인트를 제공한다.</p><pre class="mermaid">flowchart LR
    U[사용자 브라우저] --&gt;|프론트채널| AU[/authorize 엔드포인트/]
    AU --&gt;|인증·동의 UI| U
    AU --&gt;|Authorization Code| U
    U --&gt;|redirect_uri| CL[클라이언트]
    CL --&gt;|백채널| TK[/token 엔드포인트/]
    TK --&gt;|Access Token| CL
    style AU fill:#eef
    style TK fill:#efe
</pre><table><thead><tr><th>엔드포인트</th><th>대상</th><th>용도</th></tr></thead><tbody><tr><td><code>/authorize</code></td><td>사용자 브라우저</td><td>로그인·동의 UI 표시, Authorization Code 발급</td></tr><tr><td><code>/token</code></td><td>클라이언트 백엔드</td><td>Code·Refresh Token 교환으로 Access Token 발급</td></tr></tbody></table><p>프론트채널과 백채널의 구분은 중요하다. <code>/authorize</code>는 <strong>사용자가 직접 보는 URL</strong>이고, <code>/token</code>은 <strong>클라이언트 서버가 직접 호출하는 API</strong>다. 보안 특성이 다르다.</p><h3 id="authorize-엔드포인트-요청-예시" tabindex="-1"><a class="header-anchor" href="#authorize-엔드포인트-요청-예시"><span>/authorize 엔드포인트 요청 예시</span></a></h3><div class="language-http line-numbers-mode" data-highlighter="prismjs" data-ext="http" data-title="http"><pre><code><span class="line">GET /authorize?</span>
<span class="line">    response_type=code</span>
<span class="line">    &amp;client_id=abc123</span>
<span class="line">    &amp;redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback</span>
<span class="line">    &amp;scope=openid%20profile%20email</span>
<span class="line">    &amp;state=xyzRandom</span>
<span class="line">    &amp;code_challenge=E9Melhoa...</span>
<span class="line">    &amp;code_challenge_method=S256 HTTP/1.1</span>
<span class="line"><span class="token header"><span class="token header-name keyword">Host</span><span class="token punctuation">:</span> <span class="token header-value">auth.example.com</span></span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>사용자의 브라우저가 이 URL로 접근하면 AS는 로그인 페이지와 Consent 화면을 보여준다. 승인이 끝나면 <code>redirect_uri</code>로 Authorization Code를 싣고 리다이렉트한다.</p><h3 id="token-엔드포인트-요청-예시" tabindex="-1"><a class="header-anchor" href="#token-엔드포인트-요청-예시"><span>/token 엔드포인트 요청 예시</span></a></h3><div class="language-http line-numbers-mode" data-highlighter="prismjs" data-ext="http" data-title="http"><pre><code><span class="line"><span class="token request-line"><span class="token method property">POST</span> <span class="token request-target url">/token</span> <span class="token http-version property">HTTP/1.1</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Host</span><span class="token punctuation">:</span> <span class="token header-value">auth.example.com</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Content-Type</span><span class="token punctuation">:</span> <span class="token header-value">application/x-www-form-urlencoded</span></span></span>
<span class="line"><span class="token header"><span class="token header-name keyword">Authorization</span><span class="token punctuation">:</span> <span class="token header-value">Basic YWJjMTIzOnNlY3JldA==</span></span></span>
<span class="line"></span>
<span class="line">grant_type=authorization_code</span>
<span class="line">&amp;code=SplxlOBeZQQYbYS6WxSbIA</span>
<span class="line">&amp;redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback</span>
<span class="line">&amp;code_verifier=dBjftJeZ...</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>응답은 다음과 같다.</p><div class="language-json line-numbers-mode" data-highlighter="prismjs" data-ext="json" data-title="json"><pre><code><span class="line"><span class="token punctuation">{</span></span>
<span class="line">  <span class="token property">&quot;access_token&quot;</span><span class="token operator">:</span> <span class="token string">&quot;2YotnFZFEjr1zCsicMWpAA&quot;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;token_type&quot;</span><span class="token operator">:</span> <span class="token string">&quot;Bearer&quot;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;expires_in&quot;</span><span class="token operator">:</span> <span class="token number">3600</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;refresh_token&quot;</span><span class="token operator">:</span> <span class="token string">&quot;tGzv3JOkF0XG5Qx2TlKWIA&quot;</span><span class="token punctuation">,</span></span>
<span class="line">  <span class="token property">&quot;scope&quot;</span><span class="token operator">:</span> <span class="token string">&quot;openid profile email&quot;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><h3 id="확장-엔드포인트" tabindex="-1"><a class="header-anchor" href="#확장-엔드포인트"><span>확장 엔드포인트</span></a></h3><p>RFC 6749가 정의한 두 엔드포인트 외에도 표준화된 확장 엔드포인트가 있다.</p><table><thead><tr><th>엔드포인트</th><th>RFC</th><th>용도</th></tr></thead><tbody><tr><td><code>/introspect</code></td><td>7662</td><td>opaque 토큰 유효성 실시간 조회</td></tr><tr><td><code>/revoke</code></td><td>7009</td><td>토큰 폐기</td></tr><tr><td><code>/userinfo</code></td><td>OIDC Core</td><td>사용자 Claim 조회</td></tr><tr><td><code>/.well-known/openid-configuration</code></td><td>OIDC Discovery</td><td>AS 메타데이터 공개</td></tr><tr><td><code>/jwks</code></td><td>RFC 7517</td><td>JWT 서명 검증용 공개키</td></tr><tr><td><code>/device_authorization</code></td><td>RFC 8628</td><td>Device Flow</td></tr></tbody></table><p>이 엔드포인트들은 CH8, CH11에서 각각 다룬다.</p><hr><h2 id="_4-resource-server-rs-—-보호-자원을-가진-api-서버" tabindex="-1"><a class="header-anchor" href="#_4-resource-server-rs-—-보호-자원을-가진-api-서버"><span>4. Resource Server (RS) — 보호 자원을 가진 API 서버</span></a></h2><p>Resource Server는 <strong>실제 자원을 가지고 있고, 토큰을 검증해서 자원을 내주는 서버</strong>다. API 게이트웨이 뒤의 마이크로서비스들, Google Drive API, Gmail API처럼 외부에 노출된 보호 자원 서버가 모두 이에 해당한다.</p><h3 id="정의와-책임-3" tabindex="-1"><a class="header-anchor" href="#정의와-책임-3"><span>정의와 책임</span></a></h3><blockquote><p>Resource Server — 보호된 자원을 호스트하는 서버. Access Token을 사용해 인증된 요청을 받는다. (RFC 6749 §1.1)</p></blockquote><p>책임은 생각보다 단순하다.</p><ul><li>요청의 <code>Authorization: Bearer &lt;token&gt;</code> 헤더를 확인한다.</li><li>토큰을 검증한다 (서명 검증 또는 Introspection).</li><li>토큰의 Scope가 요청된 동작에 충분한지 확인한다.</li><li>허용되면 자원을 반환, 거부되면 <code>401</code>/<code>403</code>을 반환한다.</li></ul><h3 id="rs는-사용자를-인증하지-않는다" tabindex="-1"><a class="header-anchor" href="#rs는-사용자를-인증하지-않는다"><span>RS는 사용자를 인증하지 않는다</span></a></h3><p>RS는 <strong>토큰만 본다</strong>. 사용자가 누군지 직접 인증하지 않고, AS가 서명해 준 토큰의 <code>sub</code> 필드를 믿는다. 이 신뢰 관계가 OAuth의 작동 전제다.</p><pre class="mermaid">sequenceDiagram
    participant C as 클라이언트
    participant RS as Resource Server
    participant AS as Authorization Server
    C-&gt;&gt;RS: GET /drive/files&lt;br&gt;Authorization: Bearer abc...
    alt JWT일 경우
        RS-&gt;&gt;RS: JWKS로 서명 검증
        RS-&gt;&gt;RS: scope에 drive.readonly 포함 확인
    else opaque일 경우
        RS-&gt;&gt;AS: POST /introspect (token=abc)
        AS--&gt;&gt;RS: {active:true, scope:&quot;drive.readonly&quot;, sub:42}
    end
    RS--&gt;&gt;C: 200 OK (files)
</pre><h3 id="rs와-as의-분리" tabindex="-1"><a class="header-anchor" href="#rs와-as의-분리"><span>RS와 AS의 분리</span></a></h3><p>RS와 AS가 <strong>같은 서비스</strong>일 수도, <strong>별개의 서비스</strong>일 수도 있다.</p><table><thead><tr><th>구성</th><th>예시</th></tr></thead><tbody><tr><td>AS = RS (통합형)</td><td>단일 API 서비스가 토큰 발급도 자원 제공도 한다</td></tr><tr><td>AS ≠ RS (분리형)</td><td>인증 플랫폼(Keycloak)과 비즈니스 API 서버가 분리</td></tr><tr><td>다중 RS</td><td>하나의 AS가 발급한 토큰이 여러 RS에서 수용됨</td></tr></tbody></table><p>대규모 조직은 보통 <strong>분리형</strong>을 택한다. 인증·인가 로직을 한곳(AS)에 집중시키고, 비즈니스 API(RS)는 토큰 검증만 하도록 책임을 나눈다.</p><h3 id="_4가지-역할-사이의-요청-방향" tabindex="-1"><a class="header-anchor" href="#_4가지-역할-사이의-요청-방향"><span>4가지 역할 사이의 요청 방향</span></a></h3><pre class="mermaid">flowchart TD
    RO[Resource Owner&lt;br&gt;사용자] -.인증·동의.-&gt; AS[Authorization Server]
    CL[Client] -.리다이렉트.-&gt; RO
    RO -.redirect 복귀.-&gt; CL
    CL --&gt;|code 교환| AS
    AS --&gt;|Access Token| CL
    CL --&gt;|Bearer Token| RS[Resource Server]
    RS -.토큰 검증.-&gt; AS
    RS --&gt;|Protected Resource| CL
    CL --&gt; RO
    style RO fill:#eef
    style CL fill:#ffe
    style AS fill:#efe
    style RS fill:#fef
</pre><p>이 그림은 Authorization Code Flow의 모든 요청 방향을 축약한다. 다음 챕터에서 각 단계를 시간 순으로 분해한다.</p><hr><h2 id="_5-엔드포인트-—-authorize와-token" tabindex="-1"><a class="header-anchor" href="#_5-엔드포인트-—-authorize와-token"><span>5. 엔드포인트 — /authorize와 /token</span></a></h2><p>이미 3절에서 엔드포인트를 소개했지만, <strong>왜 두 개로 나뉘는가</strong>가 핵심이라 한 번 더 정리한다.</p><h3 id="왜-엔드포인트가-둘로-나뉘는가" tabindex="-1"><a class="header-anchor" href="#왜-엔드포인트가-둘로-나뉘는가"><span>왜 엔드포인트가 둘로 나뉘는가</span></a></h3><p>핵심은 <strong>보안 특성이 다른 두 채널</strong>을 분리하는 것이다.</p><table><thead><tr><th>특성</th><th>/authorize (프론트채널)</th><th>/token (백채널)</th></tr></thead><tbody><tr><td>호출 주체</td><td>사용자 브라우저</td><td>클라이언트 서버</td></tr><tr><td>전송 방법</td><td>HTTP 리다이렉트</td><td>HTTPS POST</td></tr><tr><td>URL 노출</td><td>브라우저 히스토리·Referer에 남음</td><td>서버 간 통신이라 노출 없음</td></tr><tr><td>인증</td><td>사용자가 AS에서 로그인</td><td>Client Secret 또는 PKCE</td></tr><tr><td>민감 정보</td><td>Code (단기간 1회용)</td><td>Access Token·Refresh Token</td></tr></tbody></table><p>Access Token이 프론트채널로 흘러다니면 브라우저 히스토리·로그·Referer 헤더로 유출될 위험이 있다. 그래서 Authorization Code Flow는 <strong>프론트채널로는 Code만</strong>, <strong>실제 Token은 백채널로만</strong> 주고받도록 설계됐다.</p><h3 id="프론트채널-vs-백채널" tabindex="-1"><a class="header-anchor" href="#프론트채널-vs-백채널"><span>프론트채널 vs 백채널</span></a></h3><pre class="mermaid">sequenceDiagram
    participant U as 사용자 브라우저
    participant AS as Authorization Server
    participant C as 클라이언트 서버
    rect rgb(238, 238, 255)
    Note over U,AS: 프론트채널
    U-&gt;&gt;AS: GET /authorize
    AS--&gt;&gt;U: 로그인·동의 UI
    U-&gt;&gt;AS: 자격 증명 제출
    AS--&gt;&gt;U: 302 redirect_uri?code=xxx
    U-&gt;&gt;C: GET /callback?code=xxx
    end
    rect rgb(238, 255, 238)
    Note over C,AS: 백채널
    C-&gt;&gt;AS: POST /token (code, client_secret)
    AS--&gt;&gt;C: {access_token, refresh_token}
    end
</pre><ul><li><strong>프론트채널</strong>: 사용자가 직접 보는 URL과 리다이렉트 체인. 보안 경계가 약하다.</li><li><strong>백채널</strong>: 서버 간 HTTPS 직통 호출. 클라이언트 시크릿으로 인증할 수 있고 토큰이 URL에 노출되지 않는다.</li></ul><h3 id="authorization-code-flow의-이점" tabindex="-1"><a class="header-anchor" href="#authorization-code-flow의-이점"><span>Authorization Code Flow의 이점</span></a></h3><pre class="mermaid">flowchart LR
    subgraph 프론트[브라우저에 남음]
        CODE[code=xxx&lt;br&gt;1회용, 단기간]
    end
    subgraph 백채널[서버 간 통신]
        AT[Access Token&lt;br&gt;장기간]
        RT[Refresh Token&lt;br&gt;더 장기간]
    end
    CODE --&gt;|/token 교환| 백채널
    style CODE fill:#ffe
    style AT fill:#efe
    style RT fill:#efe
</pre><p>Authorization Code라는 <strong>중간 단계</strong>를 둔 덕분에, 민감한 토큰은 브라우저 이력에 남지 않는다. CH6에서 이 보안 이점을 더 자세히 다룬다.</p><hr><h2 id="_6-public-vs-confidential-client" tabindex="-1"><a class="header-anchor" href="#_6-public-vs-confidential-client"><span>6. Public vs Confidential Client</span></a></h2><p>OAuth가 클라이언트를 두 유형으로 나누는 이유는 <strong>&quot;Client Secret을 안전하게 보관할 수 있는가&quot;</strong>라는 단순한 질문 때문이다.</p><h3 id="정의" tabindex="-1"><a class="header-anchor" href="#정의"><span>정의</span></a></h3><blockquote><p>Confidential Client — Client Secret을 안전하게 보관할 수 있는 클라이언트. (RFC 6749 §2.1) Public Client — Client Secret을 안전하게 보관할 수 없는 클라이언트.</p></blockquote><h3 id="유형별-분류" tabindex="-1"><a class="header-anchor" href="#유형별-분류"><span>유형별 분류</span></a></h3><table><thead><tr><th>유형</th><th>분류</th><th>이유</th></tr></thead><tbody><tr><td>웹 서버 앱 (Spring, Django 등)</td><td>Confidential</td><td>서버 디스크에 Secret 저장 가능</td></tr><tr><td>Native 앱 (iOS, Android, 데스크톱)</td><td>Public</td><td>앱 바이너리를 디컴파일하면 Secret 노출</td></tr><tr><td>SPA (React, Vue 등)</td><td>Public</td><td>JS 소스가 브라우저에 그대로 노출</td></tr><tr><td>서버 데몬·CLI</td><td>Confidential</td><td>서버 측 설정 파일에 Secret 저장</td></tr><tr><td>IoT·Device</td><td>Public (또는 DCR)</td><td>기기마다 고유 Secret 관리 어려움</td></tr></tbody></table><h3 id="왜-native·spa는-public인가" tabindex="-1"><a class="header-anchor" href="#왜-native·spa는-public인가"><span>왜 Native·SPA는 Public인가</span></a></h3><p>모바일 앱을 생각해 보자. 앱 설치 파일(<code>.apk</code>, <code>.ipa</code>)에 Client Secret을 박아두면, 누구든 파일을 디컴파일해서 Secret을 추출할 수 있다. SPA도 마찬가지로, JS 번들에 Secret이 들어가면 브라우저 개발자 도구로 바로 보인다.</p><pre class="mermaid">flowchart LR
    subgraph 안전[Confidential - 서버 디스크]
        S1[Client Secret&lt;br&gt;환경변수·Vault]
    end
    subgraph 위험[Public - 배포물 안]
        S2[Client Secret&lt;br&gt;APK·JS 번들]
    end
    S2 -.디컴파일·DevTools.-&gt; X[노출]
    style S1 fill:#efe
    style S2 fill:#fee
</pre><p>이런 환경에서는 Secret 자체를 없애고, 대신 <strong>PKCE(Proof Key for Code Exchange)</strong>라는 대체 메커니즘을 쓴다. PKCE는 CH12에서 상세히 다룬다.</p><h3 id="confidential-vs-public-비교" tabindex="-1"><a class="header-anchor" href="#confidential-vs-public-비교"><span>Confidential vs Public 비교</span></a></h3><table><thead><tr><th>구분</th><th>Confidential</th><th>Public</th></tr></thead><tbody><tr><td>Client Secret</td><td>있음·안전 보관</td><td>없거나·있어도 신뢰 안 함</td></tr><tr><td>대표 Grant</td><td>Authorization Code + Secret</td><td>Authorization Code + PKCE</td></tr><tr><td>/token 호출 인증</td><td>Basic Auth (id:secret)</td><td>client_id만, PKCE 검증</td></tr><tr><td>적합 Flow</td><td>Authorization Code, Client Credentials</td><td>Authorization Code + PKCE, Device Flow</td></tr><tr><td>Refresh Token</td><td>발급 가능</td><td>Rotation과 함께 조건부 발급</td></tr></tbody></table><h3 id="client-id와-client-secret의-의미" tabindex="-1"><a class="header-anchor" href="#client-id와-client-secret의-의미"><span>Client ID와 Client Secret의 의미</span></a></h3><ul><li><strong>Client ID</strong> — 공개되어도 괜찮은 클라이언트 식별자. URL에 노출된다.</li><li><strong>Client Secret</strong> — 클라이언트를 <strong>증명</strong>하는 비밀. 유출되면 공격자가 그 클라이언트를 사칭할 수 있다.</li></ul><p>Confidential Client에서는 Secret이 사실상 클라이언트의 <strong>비밀번호</strong> 역할을 한다. Public Client에서는 Secret이 의미를 잃으므로, PKCE가 &quot;이 토큰 요청이 조금 전 Authorization 요청을 한 그 클라이언트가 맞다&quot;는 증명 수단이 된다.</p><h3 id="용어-총정리" tabindex="-1"><a class="header-anchor" href="#용어-총정리"><span>용어 총정리</span></a></h3><pre class="mermaid">mindmap
  root((OAuth 용어))
    역할
      Resource Owner
      Client
      Authorization Server
      Resource Server
    엔드포인트
      /authorize
      /token
      /introspect
      /revoke
      /userinfo
    토큰
      Access Token
      Refresh Token
      ID Token OIDC
      Authorization Code
    클라이언트 유형
      Confidential
      Public
    식별자
      Client ID
      Client Secret
      redirect_uri
      Scope
</pre><p>이 용어들이 자리잡히면 다음 챕터의 Authorization Code Flow가 훨씬 수월하게 읽힌다.</p><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>OAuth는 4가지 역할을 정의한다. Resource Owner(자원 주인·사용자), Client(접근하려는 앱), Authorization Server(인증·토큰 발급), Resource Server(자원 제공 API 서버).</li><li>AS는 두 핵심 엔드포인트를 제공한다. <code>/authorize</code>는 사용자 브라우저가 호출하는 프론트채널, <code>/token</code>은 클라이언트 서버가 호출하는 백채널이다. 보안 특성이 달라 Code와 Token의 전달 경로를 분리한다.</li><li>Client Secret을 안전하게 보관할 수 있는 웹 서버 앱은 Confidential Client, Native·SPA처럼 Secret이 노출되는 환경은 Public Client다. Public은 PKCE로 Secret을 대체한다.</li><li>Introspection·Revocation·UserInfo·JWKS·Discovery는 확장 엔드포인트로 각각 별도 RFC로 표준화되어 있으며 CH8·CH11에서 다룬다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>이전 : <a href="/study/oauth/04-what-oauth-solves">OAuth는 무엇을 해결했는가</a></li><li>다음 : <a href="/study/oauth/06-authorization-code-flow">Authorization Code Flow</a></li></ul>`,100)]))}const d=t(r,[["render",i],["__file","05-roles-and-terms.html.vue"]]),c=JSON.parse('{"path":"/study/oauth/05-roles-and-terms.html","title":"4가지 역할과 용어","lang":"en-US","frontmatter":{"title":"4가지 역할과 용어","description":"OAuth 2.0의 네 가지 역할(Resource Owner, Client, AS, RS)과 엔드포인트·토큰 용어를 정리한다.","date":"2026-04-17T00:00:00.000Z","tags":["OAuth","역할","용어","RFC6749"],"prev":"/study/oauth/04-what-oauth-solves","next":"/study/oauth/06-authorization-code-flow"},"headers":[{"level":1,"title":"4가지 역할과 용어","slug":"_4가지-역할과-용어","link":"#_4가지-역할과-용어","children":[{"level":2,"title":"1. Resource Owner — 자원의 주인","slug":"_1-resource-owner-—-자원의-주인","link":"#_1-resource-owner-—-자원의-주인","children":[{"level":3,"title":"정의와 책임","slug":"정의와-책임","link":"#정의와-책임","children":[]},{"level":3,"title":"Resource Owner가 사람이 아닌 경우","slug":"resource-owner가-사람이-아닌-경우","link":"#resource-owner가-사람이-아닌-경우","children":[]},{"level":3,"title":"Resource Owner vs End User","slug":"resource-owner-vs-end-user","link":"#resource-owner-vs-end-user","children":[]}]},{"level":2,"title":"2. Client — 접근하려는 앱","slug":"_2-client-—-접근하려는-앱","link":"#_2-client-—-접근하려는-앱","children":[{"level":3,"title":"정의와 책임","slug":"정의와-책임-1","link":"#정의와-책임-1","children":[]},{"level":3,"title":"클라이언트의 유형","slug":"클라이언트의-유형","link":"#클라이언트의-유형","children":[]}]},{"level":2,"title":"3. Authorization Server (AS) — 권한을 승인하고 토큰을 발급","slug":"_3-authorization-server-as-—-권한을-승인하고-토큰을-발급","link":"#_3-authorization-server-as-—-권한을-승인하고-토큰을-발급","children":[{"level":3,"title":"정의와 책임","slug":"정의와-책임-2","link":"#정의와-책임-2","children":[]},{"level":3,"title":"AS의 두 핵심 엔드포인트","slug":"as의-두-핵심-엔드포인트","link":"#as의-두-핵심-엔드포인트","children":[]},{"level":3,"title":"/authorize 엔드포인트 요청 예시","slug":"authorize-엔드포인트-요청-예시","link":"#authorize-엔드포인트-요청-예시","children":[]},{"level":3,"title":"/token 엔드포인트 요청 예시","slug":"token-엔드포인트-요청-예시","link":"#token-엔드포인트-요청-예시","children":[]},{"level":3,"title":"확장 엔드포인트","slug":"확장-엔드포인트","link":"#확장-엔드포인트","children":[]}]},{"level":2,"title":"4. Resource Server (RS) — 보호 자원을 가진 API 서버","slug":"_4-resource-server-rs-—-보호-자원을-가진-api-서버","link":"#_4-resource-server-rs-—-보호-자원을-가진-api-서버","children":[{"level":3,"title":"정의와 책임","slug":"정의와-책임-3","link":"#정의와-책임-3","children":[]},{"level":3,"title":"RS는 사용자를 인증하지 않는다","slug":"rs는-사용자를-인증하지-않는다","link":"#rs는-사용자를-인증하지-않는다","children":[]},{"level":3,"title":"RS와 AS의 분리","slug":"rs와-as의-분리","link":"#rs와-as의-분리","children":[]},{"level":3,"title":"4가지 역할 사이의 요청 방향","slug":"_4가지-역할-사이의-요청-방향","link":"#_4가지-역할-사이의-요청-방향","children":[]}]},{"level":2,"title":"5. 엔드포인트 — /authorize와 /token","slug":"_5-엔드포인트-—-authorize와-token","link":"#_5-엔드포인트-—-authorize와-token","children":[{"level":3,"title":"왜 엔드포인트가 둘로 나뉘는가","slug":"왜-엔드포인트가-둘로-나뉘는가","link":"#왜-엔드포인트가-둘로-나뉘는가","children":[]},{"level":3,"title":"프론트채널 vs 백채널","slug":"프론트채널-vs-백채널","link":"#프론트채널-vs-백채널","children":[]},{"level":3,"title":"Authorization Code Flow의 이점","slug":"authorization-code-flow의-이점","link":"#authorization-code-flow의-이점","children":[]}]},{"level":2,"title":"6. Public vs Confidential Client","slug":"_6-public-vs-confidential-client","link":"#_6-public-vs-confidential-client","children":[{"level":3,"title":"정의","slug":"정의","link":"#정의","children":[]},{"level":3,"title":"유형별 분류","slug":"유형별-분류","link":"#유형별-분류","children":[]},{"level":3,"title":"왜 Native·SPA는 Public인가","slug":"왜-native·spa는-public인가","link":"#왜-native·spa는-public인가","children":[]},{"level":3,"title":"Confidential vs Public 비교","slug":"confidential-vs-public-비교","link":"#confidential-vs-public-비교","children":[]},{"level":3,"title":"Client ID와 Client Secret의 의미","slug":"client-id와-client-secret의-의미","link":"#client-id와-client-secret의-의미","children":[]},{"level":3,"title":"용어 총정리","slug":"용어-총정리","link":"#용어-총정리","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/oauth/05-roles-and-terms.md"}');export{d as comp,c as data};
