---
title: "Authorization Code Flow"
description: "표준 OAuth 플로우인 Authorization Code 흐름을 단계별로 해부하고 Device Authorization Grant도 소개한다."
date: 2026-04-17
tags: [OAuth, AuthorizationCode, DeviceFlow]
prev: /study/oauth/05-roles-and-terms
next: /study/oauth/07-other-grant-types
---

# Authorization Code Flow

::: info 학습 목표
- Authorization Code Flow의 6단계를 순서와 함께 설명할 수 있다.
- `response_type`, `state`, `redirect_uri`, `scope` 등 핵심 파라미터의 존재 이유를 안다.
- 프론트채널과 백채널을 구분하고 왜 두 채널을 분리하는지 이해한다.
- Device Authorization Grant(RFC 8628)가 언제 쓰이는지 두 기기 시나리오로 설명할 수 있다.
:::

---

## 1. 왜 코드(code)를 한 번 거치는가

Authorization Code Flow의 이름은 오해를 부른다. "Code"가 Access Token을 뜻하는 것처럼 들리지만, 실제로 Code는 <strong>Token을 받기 위한 1회용 교환 티켓</strong>이다. 이 한 단계가 추가된 이유는 보안 때문이다.

### Token을 바로 받으면 생기는 문제

만약 AS가 `/authorize` 응답으로 Access Token을 바로 돌려준다고 하자(이게 바로 곧 나올 Implicit Flow다).

```
302 Found
Location: https://app.example.com/callback#access_token=abc123&...
```

이 응답의 문제는 다음과 같다.

- 토큰이 <strong>브라우저 URL</strong>에 찍힌다. 히스토리, Referer 헤더, 브라우저 로그로 흐를 수 있다.
- 프록시·CDN·네트워크 감시 장비가 URL을 기록한다.
- 사용자가 URL을 실수로 공유하면 토큰 그대로 유출된다.
- 프래그먼트(`#`)로 회피해도 JS가 `window.location`을 읽을 수 있다.

### Code 교환이 주는 이점

Authorization Code Flow는 이 문제를 <strong>두 단계로 분리</strong>해 해결한다.

```mermaid
flowchart LR
    AS[Authorization<br>Server] -->|프론트채널| Q[code=xxx<br>1회용·단기간]
    Q --> U[브라우저 URL에 남음]
    U -->|Code 제시| CL[클라이언트 서버]
    CL -->|백채널 /token| AS
    AS -->|Access Token<br>Refresh Token| CL
    style Q fill:#ffe
    style U fill:#fee
    style CL fill:#efe
```

브라우저에는 단기간·1회용 Code만 남는다. 실제 토큰은 <strong>클라이언트 서버와 AS 사이의 HTTPS 백채널</strong>로만 전달된다. Code가 URL에서 유출돼도 이미 교환되어 무효화됐거나, 공격자가 Client Secret을 가지지 못하면 토큰으로 바꿀 수 없다.

### Code의 제약

Code를 안전하게 만들기 위한 몇 가지 제약이 있다.

| 제약 | 이유 |
|----|-----|
| 단기간 만료 (10분 이하 권장) | 유출돼도 짧은 시간만 유효 |
| 1회만 사용 가능 | 두 번째 교환 시도는 AS가 전체 토큰을 무효화 |
| redirect_uri 정확 일치 | 공격자가 임의 URI로 Code 탈취 방지 |
| client_id 결합 | 발급받은 클라이언트만 교환 가능 |

이 제약 조합이 "Code는 새어도 비교적 안전하다"는 특성을 만든다.

---

## 2. 6단계 시퀀스

Authorization Code Flow는 총 6단계로 구성된다. 사용자 브라우저, 클라이언트 서버, AS, RS 네 주체가 등장한다.

### 전체 시퀀스

```mermaid
sequenceDiagram
    participant U as 사용자 브라우저
    participant C as 클라이언트 서버
    participant AS as Authorization Server
    participant RS as Resource Server
    Note over U,C: 1. 사용자가 로그인 버튼 클릭
    U->>C: GET /login
    C-->>U: 302 redirect to AS /authorize
    Note over U,AS: 2. 프론트채널 - 인증·동의
    U->>AS: GET /authorize?response_type=code&...
    AS-->>U: 로그인 폼
    U->>AS: 자격 증명 제출
    AS-->>U: Consent 화면
    U->>AS: 승인
    Note over AS,U: 3. Code 발급
    AS-->>U: 302 redirect_uri?code=xxx&state=yyy
    U->>C: GET /callback?code=xxx&state=yyy
    Note over C,AS: 4. 백채널 - Code를 Token으로 교환
    C->>C: state 검증
    C->>AS: POST /token (code, client_secret)
    AS-->>C: {access_token, refresh_token, expires_in}
    Note over C,RS: 5. 자원 요청
    C->>RS: GET /api/me<br>Authorization: Bearer abc...
    RS->>RS: 토큰 검증
    RS-->>C: 200 OK (user data)
    Note over C,U: 6. 응답
    C-->>U: 로그인 완료 페이지
```

### 각 단계 설명

1. <strong>사용자가 로그인 시작</strong> — "Google로 로그인" 버튼 등을 클릭. 클라이언트 서버가 사용자를 AS `/authorize`로 리다이렉트한다.
2. <strong>사용자가 AS에서 인증·동의</strong> — AS 도메인에서 사용자가 직접 로그인하고 Consent 화면을 승인한다. 이 구간은 클라이언트 서버가 관여하지 않는다.
3. <strong>Code 발급과 리다이렉트</strong> — AS가 사전 등록된 `redirect_uri`로 브라우저를 302 리다이렉트하면서 쿼리에 `code`를 싣는다.
4. <strong>Code를 Token으로 교환(백채널)</strong> — 클라이언트 서버가 AS `/token`에 POST하여 Code와 Client Secret을 제시하고 Access Token을 받는다.
5. <strong>자원 요청</strong> — 받은 Access Token을 `Authorization: Bearer` 헤더에 실어 RS를 호출한다.
6. <strong>사용자에게 응답</strong> — 클라이언트는 자원 데이터를 바탕으로 UI를 구성해 사용자에게 보여준다.

### 실제 HTTP 예제

1단계 — 클라이언트가 사용자를 리다이렉트.

```http
HTTP/1.1 302 Found
Location: https://auth.example.com/authorize?
    response_type=code
    &client_id=abc123
    &redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback
    &scope=openid%20profile%20email
    &state=n-0S6_WzA2Mj
```

3단계 — AS가 사용자를 redirect_uri로 복귀.

```http
HTTP/1.1 302 Found
Location: https://app.example.com/callback?
    code=SplxlOBeZQQYbYS6WxSbIA
    &state=n-0S6_WzA2Mj
```

4단계 — 클라이언트 서버의 Token 교환 요청.

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded
Authorization: Basic YWJjMTIzOnNlY3JldA==

grant_type=authorization_code
&code=SplxlOBeZQQYbYS6WxSbIA
&redirect_uri=https%3A%2F%2Fapp.example.com%2Fcallback
```

Token 응답.

```json
{
  "access_token": "2YotnFZFEjr1zCsicMWpAA",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
  "scope": "openid profile email"
}
```

5단계 — RS 호출.

```http
GET /api/me HTTP/1.1
Host: api.example.com
Authorization: Bearer 2YotnFZFEjr1zCsicMWpAA
```

---

## 3. 핵심 파라미터

Authorization Code Flow 요청에 등장하는 파라미터 하나하나가 보안 장치다. 각 파라미터가 왜 필요한지 이해하는 것이 이 플로우를 제대로 이해하는 것이다.

### response_type=code

AS에게 "Authorization Code를 달라"고 요청하는 플래그. 가능한 값은 다음과 같다.

| 값 | 플로우 |
|---|-----|
| `code` | Authorization Code Flow (권장) |
| `token` | Implicit Flow (deprecated) |
| `id_token` | OIDC Implicit |
| `code id_token` | OIDC Hybrid Flow |

OAuth 2.1에서는 `code`만 실질적으로 허용된다.

### client_id

AS에 등록된 클라이언트 식별자. 공개되어도 무방하다. URL에 노출된다.

### redirect_uri

Code를 받을 클라이언트의 URL. <strong>AS에 사전 등록된 URI와 정확히 일치</strong>해야 한다. 이 검증은 "공격자가 임의로 redirect_uri를 바꿔서 Code를 자기 도메인으로 빼돌리는" 공격을 막는다.

```mermaid
flowchart TD
    A[AS 등록 URI<br>https://app.example.com/callback] --> C[/authorize 요청<br>redirect_uri 파라미터]
    C -->|일치| OK[허용·Code 발급]
    C -->|불일치| FAIL[400 error - invalid_redirect_uri]
    style OK fill:#efe
    style FAIL fill:#fee
```

유효성 검증 규칙.

- <strong>정확 일치(exact match)</strong>가 권장된다. 부분 일치·와일드카드는 공격 벡터가 된다.
- 여러 URI를 등록할 수 있지만 요청 시에는 그중 하나와 정확히 같아야 한다.
- `localhost`는 개발용으로 특별 허용되는 경우가 많다.

### scope

요청할 권한의 범위. 공백으로 구분된 문자열. AS는 사용자에게 Consent 화면으로 표시하고 승인받은 Scope만 토큰에 포함시킨다.

```
scope=openid profile email drive.readonly
```

### state — CSRF 방어 필수

`state`는 클라이언트가 생성한 <strong>랜덤 값</strong>이다. AS는 이 값을 그대로 redirect_uri에 돌려준다. 클라이언트는 받은 `state`가 자신이 보낸 값인지 확인한다.

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant S as 세션
    participant AS as AS
    C->>S: state = randomUUID()
    C->>AS: /authorize?state=abc-123
    AS-->>C: /callback?state=abc-123 &code=xxx
    C->>S: state 일치 확인
    alt 일치
        C->>AS: /token 교환
    else 불일치
        C-->>C: 공격 의심 → 400
    end
```

이 검증이 없으면 <strong>CSRF 공격</strong>이 가능하다. 공격자가 자신의 Code를 피해자 브라우저로 리다이렉트시켜서, 피해자가 공격자 계정으로 로그인하게 만드는 시나리오다.

`state`는 다음 용도를 겸할 수도 있다.

- CSRF 방어 (필수)
- 원래 요청 경로 복원 (예: 사용자가 보려던 페이지 URL)
- 멀티스텝 폼 상태 전달

### code_challenge / code_challenge_method — PKCE

PKCE(Proof Key for Code Exchange)는 Public Client가 Client Secret 없이도 "이 토큰 요청이 그 Authorization 요청과 같은 클라이언트에서 왔다"를 증명하는 메커니즘이다.

```
code_challenge=E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM
code_challenge_method=S256
```

PKCE는 CH12에서 자세히 다룬다. 여기서는 Public Client에 필수이며, OAuth 2.1에서는 Confidential Client도 포함해 <strong>모든 클라이언트에 필수화</strong>된다는 점만 기억한다.

### nonce — OIDC

OIDC에서 `id_token` 응답을 받을 때 리플레이 공격을 방지한다. CH10에서 다룬다.

---

## 4. Front-channel vs Back-channel

플로우 중간에 프론트채널과 백채널이 번갈아 나온다. 각각의 보안 특성이 다른 점을 이해해야 한다.

### 프론트채널

```mermaid
flowchart LR
    U[사용자 브라우저] -->|GET /authorize| AS[AS]
    AS -->|302 redirect| U
    U -->|/callback?code=xxx| CL[클라이언트]
```

- HTTP 리다이렉트 체인으로 구성된다.
- 사용자가 직접 볼 수 있고, URL 바에 모두 찍힌다.
- 브라우저 히스토리·Referer 헤더·프록시 로그에 남을 수 있다.
- <strong>통과시키면 안 되는 정보</strong>: Access Token, Refresh Token, Client Secret.
- <strong>통과시켜도 되는 정보</strong>: Authorization Code(1회용·단기간), state, scope.

### 백채널

```mermaid
flowchart LR
    CL[클라이언트 서버] -->|POST /token<br>HTTPS| AS[AS]
    AS -->|200 OK<br>tokens JSON| CL
```

- 서버 간 HTTPS 직통 호출.
- URL에 민감 정보가 노출되지 않는다(요청 바디에 들어감).
- Client Secret으로 클라이언트 인증이 가능하다.
- 브라우저 이력에 남지 않는다.
- <strong>여기로 Access Token·Refresh Token을 주고받는다.</strong>

### 채널 분리의 보안 이점

| 시나리오 | 프론트채널 노출 | 실제 피해 |
|-------|-------------|--------|
| 브라우저 히스토리에 Code가 남음 | 유출됨 | 1회 사용됐으면 무효·Client Secret 없으면 교환 불가 |
| Access Token이 URL에 있었다면 | 유출됨 | 공격자가 그대로 API 호출 가능 |
| Refresh Token이 URL에 있었다면 | 유출됨 | 장기간 API 호출 가능 |

Authorization Code Flow의 설계 의도가 이 표에 요약된다. <strong>유출돼도 피해가 작은 것만 프론트채널로 보내고, 피해가 큰 것은 백채널로만 보낸다.</strong>

### Public Client는 Client Secret이 없는데?

Native·SPA는 Client Secret이 없기 때문에 "이 토큰 요청이 정말 그 클라이언트에서 왔다"를 증명할 수단이 없다. 이 공백을 <strong>PKCE</strong>가 메운다. `/authorize` 요청에 `code_challenge`를 포함하고, `/token` 요청에 `code_verifier`를 포함한다. AS는 challenge와 verifier의 해시 관계를 검증한다. 이 메커니즘 덕분에 Public Client도 Authorization Code Flow를 안전하게 쓸 수 있다.

---

## 5. Device Authorization Grant (RFC 8628)

TV·셋톱박스·CLI·IoT 기기에는 <strong>키보드가 없거나 브라우저를 띄우기 어렵다</strong>. 이런 환경에서 사용자를 AS로 리다이렉트하는 전통적 플로우는 작동하지 않는다. Device Authorization Grant는 이 문제를 "두 기기를 쓰자"로 해결한다.

### 두 기기 시나리오

```mermaid
sequenceDiagram
    participant D as 디바이스<br>(TV·CLI)
    participant AS as Authorization Server
    participant P as 사용자 휴대폰
    D->>AS: POST /device_authorization<br>(client_id, scope)
    AS-->>D: device_code, user_code<br>verification_uri
    D->>D: 화면에 user_code 표시
    Note over P: 사용자는 폰으로 URL 방문
    P->>AS: GET verification_uri
    AS-->>P: 로그인·동의 화면
    P->>AS: user_code 입력, 승인
    loop 폴링 (5초 간격)
        D->>AS: POST /token<br>grant_type=device_code
        alt 아직 승인 전
            AS-->>D: authorization_pending
        else 승인 완료
            AS-->>D: access_token + refresh_token
        end
    end
```

### 핵심 아이디어

디바이스는 AS에게 "코드 두 개를 달라"고 요청한다.

- `device_code` — 디바이스만 아는 긴 값. 토큰 교환에 사용.
- `user_code` — 사람이 타이핑할 수 있는 짧은 값 (예: `WDJB-MJHT`).

디바이스는 화면에 `user_code`와 `verification_uri`를 표시한다. 사용자는 본인 휴대폰으로 그 URL에 방문해 `user_code`를 입력하고 동의한다. 그 사이 디바이스는 `/token`을 주기적으로 폴링하다가 승인이 완료되면 토큰을 받는다.

### 실제 응답 예시

`/device_authorization` 응답.

```json
{
  "device_code": "GmRhmhcxhwAzkoEqiMEg_DnyEysNkuNhszIySk9eS",
  "user_code": "WDJB-MJHT",
  "verification_uri": "https://example.com/device",
  "verification_uri_complete": "https://example.com/device?user_code=WDJB-MJHT",
  "expires_in": 1800,
  "interval": 5
}
```

디바이스는 `interval`만큼 기다린 뒤 `/token`을 폴링한다.

```http
POST /token HTTP/1.1
Host: auth.example.com
Content-Type: application/x-www-form-urlencoded

grant_type=urn:ietf:params:oauth:grant-type:device_code
&device_code=GmRhmhcxhwAzkoEqiMEg_DnyEysNkuNhszIySk9eS
&client_id=abc123
```

### 활용 예

- Apple TV·Android TV에서 Netflix·YouTube 로그인
- AWS CLI, GitHub CLI의 `gh auth login`
- IoT 기기 초기 설정 (스마트 스피커 등)
- 개발자 도구 (kubectl, gcloud)

### Authorization Code Flow와의 비교

| 관점 | Authorization Code | Device Authorization |
|----|----------------|-------------------|
| 브라우저 필요 | 디바이스 자체 | 다른 기기 |
| redirect_uri | 사용 | 미사용 |
| 사용자 동선 | 한 기기에서 완결 | 두 기기 협조 |
| 적합 환경 | 웹·모바일 | TV·CLI·IoT |
| 토큰 수령 | redirect 콜백 | 폴링 |

---

## 6. 블로그 포스트와의 차이

이 스터디의 [OIDC 블로그 포스트](/posts/tech/2025-08-29-oidc)에도 Authorization Code Flow의 실제 플로우 이미지가 있다. 블로그 포스트와 이 챕터의 차이는 초점에 있다.

### 블로그 포스트 — "무엇이 일어나는가"

블로그 포스트는 플로우의 <strong>전체 그림</strong>을 빠르게 보여준다. 실제 화면 캡처와 시퀀스 이미지를 통해 "브라우저가 이런 순서로 움직인다"는 감을 얻게 한다.

### 이 챕터 — "왜 그렇게 설계됐는가"

이 챕터는 각 단계의 <strong>존재 이유</strong>에 집중했다.

- <strong>Code 교환이 왜 필요한가</strong> — Token이 URL에 찍히면 안 되기 때문
- <strong>state가 왜 필수인가</strong> — CSRF를 막기 위해
- <strong>redirect_uri 정확 일치가 왜 중요한가</strong> — Code 탈취를 막기 위해
- <strong>프론트채널/백채널이 왜 나뉘는가</strong> — 유출 피해 분리를 위해
- <strong>Device Flow가 왜 존재하는가</strong> — 브라우저 없는 환경의 요구 때문

### 어느 걸 먼저 봐도 괜찮다

- 처음이라면 <strong>블로그 포스트</strong> → 이 챕터 순서가 좋다. 큰 그림을 먼저 잡고 세부 이유를 이해한다.
- 이미 플로우를 아는 상태라면 이 챕터만으로 충분하다. PKCE(CH12), 토큰 관리(CH13), BFF(CH14) 같은 심화 주제로 이어진다.

---

::: tip 핵심 정리
- Authorization Code Flow는 프론트채널로 단기간·1회용 Code만 흘리고 실제 토큰은 백채널로만 주고받아, URL 노출로 인한 토큰 유출을 구조적으로 막는다.
- 6단계는 (1) 리다이렉트 시작, (2) AS에서 인증·동의, (3) Code 발급, (4) 백채널 Token 교환, (5) RS 자원 요청, (6) 클라이언트 UI 응답이다. 각 파라미터는 보안 장치다.
- `state`는 CSRF 방어에 필수이며, `redirect_uri`의 정확 일치 검증은 Code 탈취를 막는다. Public Client는 Client Secret 대신 PKCE로 클라이언트 증명을 대체한다.
- Device Authorization Grant(RFC 8628)는 TV·CLI·IoT처럼 브라우저가 없는 기기에서 다른 기기(휴대폰)와 협조해 토큰을 발급받는 전용 플로우다.
:::

## 다음 챕터

- 이전 : [4가지 역할과 용어](/study/oauth/05-roles-and-terms)
- 다음 : [나머지 Grant Type과 그 한계](/study/oauth/07-other-grant-types)
