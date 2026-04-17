---
title: "4가지 역할과 용어"
description: "OAuth 2.0의 네 가지 역할(Resource Owner, Client, AS, RS)과 엔드포인트·토큰 용어를 정리한다."
date: 2026-04-17
tags: [OAuth, 역할, 용어, RFC6749]
prev: /study/oauth/04-what-oauth-solves
next: /study/oauth/06-authorization-code-flow
---

# 4가지 역할과 용어

::: info 학습 목표
- OAuth의 4가지 역할(Resource Owner, Client, Authorization Server, Resource Server)과 각자의 책임을 설명할 수 있다.
- 인가 서버의 두 핵심 엔드포인트(`/authorize`, `/token`)의 용도를 구분한다.
- Public Client와 Confidential Client의 차이, 왜 Native·SPA가 Public으로 분류되는지 안다.
- Client ID와 Client Secret의 의미와 보관 위치의 원칙을 이해한다.
:::

---

## 1. Resource Owner — 자원의 주인

Resource Owner는 <strong>자원의 주인</strong>이다. OAuth가 "누구의 권한을 위임하는가"라고 물으면, 바로 이 Resource Owner의 권한이다. 대부분의 경우 <strong>사용자(End User)</strong>가 곧 Resource Owner다.

### 정의와 책임

> Resource Owner — 보호된 자원에 대한 접근을 승인할 수 있는 엔티티. 사람인 경우 End User라고도 한다. (RFC 6749 §1.1)

책임은 단순하다.

- AS에서 자신의 신원을 인증한다(로그인).
- Consent 화면에서 클라이언트의 접근 요청을 승인하거나 거부한다.
- 언제든 발급된 토큰을 취소할 수 있다.

### Resource Owner가 사람이 아닌 경우

반드시 사람일 필요는 없다. <strong>M2M(Machine-to-Machine)</strong> 시나리오에서는 조직(organization) 또는 서비스 계정 자체가 Resource Owner가 된다. 이 경우 Client Credentials Grant(CH7)가 쓰이고, 사용자 개입 없이 클라이언트가 AS에서 직접 토큰을 받는다.

| 유형 | Resource Owner | 예시 |
|----|----------------|------|
| 사용자 위임 | 개인 사용자 | 내 Gmail에 접근하는 Notion |
| M2M | 조직·서비스 계정 | 배치 서버가 API 호출 |
| 제3자 사용자 | 다른 사람 사용자 | 고객이 사용하는 SaaS 기능 |

### Resource Owner vs End User

RFC는 두 용어를 미묘하게 구분한다. 대부분 문맥에서는 혼용해도 되지만, M2M 시나리오를 다룰 때는 <strong>Resource Owner = 조직</strong>, <strong>End User = 실사용자</strong>처럼 달라질 수 있다는 점을 의식해 둔다.

---

## 2. Client — 접근하려는 앱

Client는 <strong>자원에 접근하려는 애플리케이션</strong>이다. 웹 백엔드, 모바일 앱, SPA, CLI 도구, 서버 데몬까지 모두 클라이언트에 해당한다. 사용자를 대신해서 자원 서버를 호출하는 주체다.

### 정의와 책임

> Client — Resource Owner의 승인을 받아 보호된 자원에 접근 요청을 하는 애플리케이션. (RFC 6749 §1.1)

책임은 다음과 같다.

- AS에 자신을 등록하고 Client ID를 받는다.
- 사용자를 AS로 리다이렉트해 인증·동의를 받는다.
- 받아낸 토큰을 안전하게 보관한다.
- 자원 서버 호출 시 `Authorization: Bearer <token>` 헤더를 첨부한다.
- 토큰이 만료되면 Refresh Token으로 갱신하거나 사용자를 다시 인증시킨다.

### 클라이언트의 유형

```mermaid
flowchart TB
    CL[OAuth Client] --> W[Web Server App]
    CL --> N[Native App<br>iOS/Android/Desktop]
    CL --> S[Single Page App<br>브라우저 JS]
    CL --> M[Machine-to-Machine<br>서버 데몬·CLI]
    W -.-> C1[Confidential]
    N -.-> C2[Public]
    S -.-> C2
    M -.-> C1
    style C1 fill:#efe
    style C2 fill:#ffe
```

각 유형별로 권장되는 Grant Type이 다르다. 이는 CH6·CH7에서 다룬다.

---

## 3. Authorization Server (AS) — 권한을 승인하고 토큰을 발급

AS는 OAuth 생태계의 심장이다. 사용자를 인증하고, Consent를 받고, 토큰을 발급한다. 실무에서는 Google·Kakao 같은 IdP의 AS를 쓰거나 Keycloak·Auth0·Okta 같은 솔루션을 자체 구축한다.

### 정의와 책임

> Authorization Server — 사용자 인증과 권한 승인 후 클라이언트에게 Access Token을 발급하는 서버. (RFC 6749 §1.1)

책임은 넓다.

- 사용자 인증 (비밀번호·MFA·생체 등)
- 클라이언트 등록 관리 (Client ID·Secret·redirect_uri)
- Consent 화면 제공 및 승인 기록 보존
- Authorization Code 발급 (Authorization Code Flow)
- Access Token·Refresh Token 발급 및 서명
- 토큰 검증 엔드포인트 제공 (Introspection)
- 토큰 취소 엔드포인트 제공 (Revocation)
- 세션·로그아웃 관리

### AS의 두 핵심 엔드포인트

OAuth 2.0에서 AS는 최소 두 개의 HTTP 엔드포인트를 제공한다.

```mermaid
flowchart LR
    U[사용자 브라우저] -->|프론트채널| AU[/authorize 엔드포인트/]
    AU -->|인증·동의 UI| U
    AU -->|Authorization Code| U
    U -->|redirect_uri| CL[클라이언트]
    CL -->|백채널| TK[/token 엔드포인트/]
    TK -->|Access Token| CL
    style AU fill:#eef
    style TK fill:#efe
```

| 엔드포인트 | 대상 | 용도 |
|---------|-----|-----|
| `/authorize` | 사용자 브라우저 | 로그인·동의 UI 표시, Authorization Code 발급 |
| `/token` | 클라이언트 백엔드 | Code·Refresh Token 교환으로 Access Token 발급 |

프론트채널과 백채널의 구분은 중요하다. `/authorize`는 <strong>사용자가 직접 보는 URL</strong>이고, `/token`은 <strong>클라이언트 서버가 직접 호출하는 API</strong>다. 보안 특성이 다르다.

### /authorize 엔드포인트 요청 예시

```http
GET /authorize?
    response_type=code
    &client_id=abc123
    &redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback
    &scope=openid%20profile%20email
    &state=xyzRandom
    &code_challenge=E9Melhoa...
    &code_challenge_method=S256 HTTP/1.1
Host: auth.example.com
```

사용자의 브라우저가 이 URL로 접근하면 AS는 로그인 페이지와 Consent 화면을 보여준다. 승인이 끝나면 `redirect_uri`로 Authorization Code를 싣고 리다이렉트한다.

### /token 엔드포인트 요청 예시

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic YWJjMTIzOnNlY3JldA==

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback
&code_verifier=dBjftJeZ...
```

응답은 다음과 같다.

```json
{
  "access_token": "2YotnFZFEjr1zCsicMWpAA",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
  "scope": "openid profile email"
}
```

### 확장 엔드포인트

RFC 6749가 정의한 두 엔드포인트 외에도 표준화된 확장 엔드포인트가 있다.

| 엔드포인트 | RFC | 용도 |
|---------|-----|-----|
| `/introspect` | 7662 | opaque 토큰 유효성 실시간 조회 |
| `/revoke` | 7009 | 토큰 폐기 |
| `/userinfo` | OIDC Core | 사용자 Claim 조회 |
| `/.well-known/openid-configuration` | OIDC Discovery | AS 메타데이터 공개 |
| `/jwks` | RFC 7517 | JWT 서명 검증용 공개키 |
| `/device_authorization` | RFC 8628 | Device Flow |

이 엔드포인트들은 CH8, CH11에서 각각 다룬다.

---

## 4. Resource Server (RS) — 보호 자원을 가진 API 서버

Resource Server는 <strong>실제 자원을 가지고 있고, 토큰을 검증해서 자원을 내주는 서버</strong>다. API 게이트웨이 뒤의 마이크로서비스들, Google Drive API, Gmail API처럼 외부에 노출된 보호 자원 서버가 모두 이에 해당한다.

### 정의와 책임

> Resource Server — 보호된 자원을 호스트하는 서버. Access Token을 사용해 인증된 요청을 받는다. (RFC 6749 §1.1)

책임은 생각보다 단순하다.

- 요청의 `Authorization: Bearer <token>` 헤더를 확인한다.
- 토큰을 검증한다 (서명 검증 또는 Introspection).
- 토큰의 Scope가 요청된 동작에 충분한지 확인한다.
- 허용되면 자원을 반환, 거부되면 `401`/`403`을 반환한다.

### RS는 사용자를 인증하지 않는다

RS는 <strong>토큰만 본다</strong>. 사용자가 누군지 직접 인증하지 않고, AS가 서명해 준 토큰의 `sub` 필드를 믿는다. 이 신뢰 관계가 OAuth의 작동 전제다.

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant RS as Resource Server
    participant AS as Authorization Server
    C->>RS: GET /drive/files<br>Authorization: Bearer abc...
    alt JWT일 경우
        RS->>RS: JWKS로 서명 검증
        RS->>RS: scope에 drive.readonly 포함 확인
    else opaque일 경우
        RS->>AS: POST /introspect (token=abc)
        AS-->>RS: {active:true, scope:"drive.readonly", sub:42}
    end
    RS-->>C: 200 OK (files)
```

### RS와 AS의 분리

RS와 AS가 <strong>같은 서비스</strong>일 수도, <strong>별개의 서비스</strong>일 수도 있다.

| 구성 | 예시 |
|----|-----|
| AS = RS (통합형) | 단일 API 서비스가 토큰 발급도 자원 제공도 한다 |
| AS ≠ RS (분리형) | 인증 플랫폼(Keycloak)과 비즈니스 API 서버가 분리 |
| 다중 RS | 하나의 AS가 발급한 토큰이 여러 RS에서 수용됨 |

대규모 조직은 보통 <strong>분리형</strong>을 택한다. 인증·인가 로직을 한곳(AS)에 집중시키고, 비즈니스 API(RS)는 토큰 검증만 하도록 책임을 나눈다.

### 4가지 역할 사이의 요청 방향

```mermaid
flowchart TD
    RO[Resource Owner<br>사용자] -.인증·동의.-> AS[Authorization Server]
    CL[Client] -.리다이렉트.-> RO
    RO -.redirect 복귀.-> CL
    CL -->|code 교환| AS
    AS -->|Access Token| CL
    CL -->|Bearer Token| RS[Resource Server]
    RS -.토큰 검증.-> AS
    RS -->|Protected Resource| CL
    CL --> RO
    style RO fill:#eef
    style CL fill:#ffe
    style AS fill:#efe
    style RS fill:#fef
```

이 그림은 Authorization Code Flow의 모든 요청 방향을 축약한다. 다음 챕터에서 각 단계를 시간 순으로 분해한다.

---

## 5. 엔드포인트 — /authorize와 /token

이미 3절에서 엔드포인트를 소개했지만, <strong>왜 두 개로 나뉘는가</strong>가 핵심이라 한 번 더 정리한다.

### 왜 엔드포인트가 둘로 나뉘는가

핵심은 <strong>보안 특성이 다른 두 채널</strong>을 분리하는 것이다.

| 특성 | /authorize (프론트채널) | /token (백채널) |
|----|----------------------|---------------|
| 호출 주체 | 사용자 브라우저 | 클라이언트 서버 |
| 전송 방법 | HTTP 리다이렉트 | HTTPS POST |
| URL 노출 | 브라우저 히스토리·Referer에 남음 | 서버 간 통신이라 노출 없음 |
| 인증 | 사용자가 AS에서 로그인 | Client Secret 또는 PKCE |
| 민감 정보 | Code (단기간 1회용) | Access Token·Refresh Token |

Access Token이 프론트채널로 흘러다니면 브라우저 히스토리·로그·Referer 헤더로 유출될 위험이 있다. 그래서 Authorization Code Flow는 <strong>프론트채널로는 Code만</strong>, <strong>실제 Token은 백채널로만</strong> 주고받도록 설계됐다.

### 프론트채널 vs 백채널

```mermaid
sequenceDiagram
    participant U as 사용자 브라우저
    participant AS as Authorization Server
    participant C as 클라이언트 서버
    rect rgb(238, 238, 255)
    Note over U,AS: 프론트채널
    U->>AS: GET /authorize
    AS-->>U: 로그인·동의 UI
    U->>AS: 자격 증명 제출
    AS-->>U: 302 redirect_uri?code=xxx
    U->>C: GET /callback?code=xxx
    end
    rect rgb(238, 255, 238)
    Note over C,AS: 백채널
    C->>AS: POST /token (code, client_secret)
    AS-->>C: {access_token, refresh_token}
    end
```

- <strong>프론트채널</strong>: 사용자가 직접 보는 URL과 리다이렉트 체인. 보안 경계가 약하다.
- <strong>백채널</strong>: 서버 간 HTTPS 직통 호출. 클라이언트 시크릿으로 인증할 수 있고 토큰이 URL에 노출되지 않는다.

### Authorization Code Flow의 이점

```mermaid
flowchart LR
    subgraph 프론트[브라우저에 남음]
        CODE[code=xxx<br>1회용, 단기간]
    end
    subgraph 백채널[서버 간 통신]
        AT[Access Token<br>장기간]
        RT[Refresh Token<br>더 장기간]
    end
    CODE -->|/token 교환| 백채널
    style CODE fill:#ffe
    style AT fill:#efe
    style RT fill:#efe
```

Authorization Code라는 <strong>중간 단계</strong>를 둔 덕분에, 민감한 토큰은 브라우저 이력에 남지 않는다. CH6에서 이 보안 이점을 더 자세히 다룬다.

---

## 6. Public vs Confidential Client

OAuth가 클라이언트를 두 유형으로 나누는 이유는 <strong>"Client Secret을 안전하게 보관할 수 있는가"</strong>라는 단순한 질문 때문이다.

### 정의

> Confidential Client — Client Secret을 안전하게 보관할 수 있는 클라이언트. (RFC 6749 §2.1)
> Public Client — Client Secret을 안전하게 보관할 수 없는 클라이언트.

### 유형별 분류

| 유형 | 분류 | 이유 |
|----|-----|-----|
| 웹 서버 앱 (Spring, Django 등) | Confidential | 서버 디스크에 Secret 저장 가능 |
| Native 앱 (iOS, Android, 데스크톱) | Public | 앱 바이너리를 디컴파일하면 Secret 노출 |
| SPA (React, Vue 등) | Public | JS 소스가 브라우저에 그대로 노출 |
| 서버 데몬·CLI | Confidential | 서버 측 설정 파일에 Secret 저장 |
| IoT·Device | Public (또는 DCR) | 기기마다 고유 Secret 관리 어려움 |

### 왜 Native·SPA는 Public인가

모바일 앱을 생각해 보자. 앱 설치 파일(`.apk`, `.ipa`)에 Client Secret을 박아두면, 누구든 파일을 디컴파일해서 Secret을 추출할 수 있다. SPA도 마찬가지로, JS 번들에 Secret이 들어가면 브라우저 개발자 도구로 바로 보인다.

```mermaid
flowchart LR
    subgraph 안전[Confidential - 서버 디스크]
        S1[Client Secret<br>환경변수·Vault]
    end
    subgraph 위험[Public - 배포물 안]
        S2[Client Secret<br>APK·JS 번들]
    end
    S2 -.디컴파일·DevTools.-> X[노출]
    style S1 fill:#efe
    style S2 fill:#fee
```

이런 환경에서는 Secret 자체를 없애고, 대신 <strong>PKCE(Proof Key for Code Exchange)</strong>라는 대체 메커니즘을 쓴다. PKCE는 CH12에서 상세히 다룬다.

### Confidential vs Public 비교

| 구분 | Confidential | Public |
|----|-----|-----|
| Client Secret | 있음·안전 보관 | 없거나·있어도 신뢰 안 함 |
| 대표 Grant | Authorization Code + Secret | Authorization Code + PKCE |
| /token 호출 인증 | Basic Auth (id:secret) | client_id만, PKCE 검증 |
| 적합 Flow | Authorization Code, Client Credentials | Authorization Code + PKCE, Device Flow |
| Refresh Token | 발급 가능 | Rotation과 함께 조건부 발급 |

### Client ID와 Client Secret의 의미

- <strong>Client ID</strong> — 공개되어도 괜찮은 클라이언트 식별자. URL에 노출된다.
- <strong>Client Secret</strong> — 클라이언트를 <strong>증명</strong>하는 비밀. 유출되면 공격자가 그 클라이언트를 사칭할 수 있다.

Confidential Client에서는 Secret이 사실상 클라이언트의 <strong>비밀번호</strong> 역할을 한다. Public Client에서는 Secret이 의미를 잃으므로, PKCE가 "이 토큰 요청이 조금 전 Authorization 요청을 한 그 클라이언트가 맞다"는 증명 수단이 된다.

### 용어 총정리

```mermaid
mindmap
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
```

이 용어들이 자리잡히면 다음 챕터의 Authorization Code Flow가 훨씬 수월하게 읽힌다.

---

::: tip 핵심 정리
- OAuth는 4가지 역할을 정의한다. Resource Owner(자원 주인·사용자), Client(접근하려는 앱), Authorization Server(인증·토큰 발급), Resource Server(자원 제공 API 서버).
- AS는 두 핵심 엔드포인트를 제공한다. `/authorize`는 사용자 브라우저가 호출하는 프론트채널, `/token`은 클라이언트 서버가 호출하는 백채널이다. 보안 특성이 달라 Code와 Token의 전달 경로를 분리한다.
- Client Secret을 안전하게 보관할 수 있는 웹 서버 앱은 Confidential Client, Native·SPA처럼 Secret이 노출되는 환경은 Public Client다. Public은 PKCE로 Secret을 대체한다.
- Introspection·Revocation·UserInfo·JWKS·Discovery는 확장 엔드포인트로 각각 별도 RFC로 표준화되어 있으며 CH8·CH11에서 다룬다.
:::

## 다음 챕터

- 이전 : [OAuth는 무엇을 해결했는가](/study/oauth/04-what-oauth-solves)
- 다음 : [Authorization Code Flow](/study/oauth/06-authorization-code-flow)
