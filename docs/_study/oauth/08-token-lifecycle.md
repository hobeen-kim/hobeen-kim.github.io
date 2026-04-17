---
title: "Access·Refresh Token의 수명 주기"
description: "Access/Refresh Token의 발급·검증·갱신 흐름과 Introspection(RFC 7662), Revocation(RFC 7009)을 다룬다."
date: 2026-04-17
tags: [OAuth, AccessToken, RefreshToken, Introspection, Revocation]
prev: /study/oauth/07-other-grant-types
next: /study/oauth/09-why-oidc
---

# Access·Refresh Token의 수명 주기

::: info 학습 목표
- Access Token과 Refresh Token의 수명·범위·저장 위치를 각각 설명할 수 있다.
- 불투명(opaque) 토큰과 자가 기술(JWT) 토큰의 검증 방식 차이를 안다.
- Introspection(RFC 7662)과 Revocation(RFC 7009) 엔드포인트의 용도를 구분한다.
- 로그아웃 시 어떤 토큰을 어떻게 무효화해야 하는지 체크리스트로 정리할 수 있다.
:::

---

## 1. Access Token — 짧은 수명, 자원 접근 증표

Access Token은 OAuth의 핵심 산출물이다. "이 토큰을 가진 누군가가 특정 Scope 안에서 특정 자원에 접근할 권리가 있다"는 증표다.

### 수명과 용도

| 속성 | 권장 값 | 이유 |
|----|-------|-----|
| 수명 | 5~60분 (짧을수록 안전) | 탈취 시 피해 창 최소화 |
| 범위 | Scope로 제한 | 최소 권한 원칙 |
| 사용처 | Resource Server API 호출 | Authorization Server는 검증용으로만 |
| 저장 | 메모리(권장) / HttpOnly 쿠키 / localStorage | 환경에 따라 |
| 전송 | `Authorization: Bearer <token>` | RFC 6750 |

### Bearer Token의 의미

RFC 6750이 정의한 Bearer 방식은 "이 토큰을 가진 자(bearer)가 권한을 가진다"는 단순한 모델이다. 누가 들고 왔든 토큰만 유효하면 RS는 받아들인다. 이는 <strong>토큰 자체가 돈처럼 작동</strong>한다는 뜻이다. 탈취되면 곧바로 쓸 수 있다.

```mermaid
flowchart LR
    T[Access Token<br>Bearer 방식] --> P1[소지자 누구든 사용 가능]
    T --> P2[별도 증명 절차 없음]
    T --> P3[탈취 시 즉시 오남용 가능]
    T --> MI[완화책]
    MI --> M1[짧은 수명]
    MI --> M2[HTTPS 필수]
    MI --> M3[DPoP·mTLS<br>Sender-Constrained]
    style T fill:#ffe
```

DPoP(Demonstrating Proof-of-Possession)와 mTLS(Mutual TLS)는 "토큰 소지자가 누구인지 추가 증명"하게 만드는 확장 규격이다. CH13에서 다룬다.

### 짧은 수명을 유지하는 이유

수명이 길면 탈취 시 공격 시간 창이 비례해 커진다. 반면 너무 짧으면 매번 갱신 요청이 빈번해져 성능 비용이 커진다. 실무적 절충점은 다음과 같다.

- <strong>민감 API</strong> (결제, 관리자): 5~15분
- <strong>일반 API</strong>: 30분~1시간
- <strong>읽기 전용 API</strong>: 1~2시간 (드물게 더 길게)

---

## 2. Refresh Token — 긴 수명, AS와만 통신

Refresh Token은 <strong>Access Token을 재발급받기 위한 장기 자격</strong>이다. Access Token 만료 시마다 사용자가 재로그인하지 않게 만드는 장치다.

### 수명과 용도

| 속성 | 권장 값 |
|----|-------|
| 수명 | 며칠~몇 개월 (최대치는 정책) |
| 사용처 | Authorization Server `/token` 엔드포인트만 |
| RS에 전송 | 절대 금지 |
| 저장 | HttpOnly 쿠키(웹) / Secure Storage(모바일) |
| 교체 | Rotation 권장 |

### Refresh Token 교환 플로우

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant AS as Authorization Server
    participant RS as Resource Server
    Note over C: Access Token 만료 (401 응답)
    C->>AS: POST /token<br>grant_type=refresh_token<br>refresh_token=xyz
    AS->>AS: Refresh Token 검증
    AS-->>C: 새 Access Token<br>(새 Refresh Token - Rotation)
    C->>RS: Authorization: Bearer <new access>
    RS-->>C: 200 OK
```

요청 예시.

```http
POST /token HTTP/1.1
Host: auth.example.com
Authorization: Basic <client credentials>
Content-Type: application/x-www-form-urlencoded

grant_type=refresh_token
&refresh_token=tGzv3JOkF0XG5Qx2TlKWIA
&scope=openid profile
```

응답.

```json
{
  "access_token": "newATeyJhbGc...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "newRTtGzv3JOk...",
  "scope": "openid profile"
}
```

### Refresh Token Rotation (RTR)

RTR은 <strong>Refresh Token을 한 번 쓰면 새 토큰으로 교체하는 정책</strong>이다. 이전 토큰은 즉시 무효화된다.

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant AS as AS
    C->>AS: /token (RT=RT1)
    AS->>AS: RT1 사용 기록, 폐기
    AS-->>C: AT2, RT2
    Note over AS: 이후 RT1로 재요청 시
    C->>AS: /token (RT=RT1) - 재사용 시도
    AS->>AS: 재사용 탐지!
    AS->>AS: 관련 전체 토큰 폐기
    AS-->>C: invalid_grant
```

공격자가 RT를 탈취해도 이미 정상 클라이언트가 한 번 썼다면 무효다. 반대로 공격자가 먼저 쓰면 정상 클라이언트가 쓸 때 재사용 탐지가 발동해 전체 세션이 폐기된다. 이 메커니즘은 탈취를 <strong>탐지 가능</strong>하게 만든다.

블로그의 [Refresh Token Rotation 포스트](/posts/spring/2023-04-18-rtr)에서 Spring 환경 실제 구현 예시를 확인할 수 있다.

### Refresh Token 저장 원칙

- <strong>서버 측 클라이언트(웹 백엔드)</strong>: DB·Redis 등 서버 저장소. 사용자별 해시 인덱스.
- <strong>브라우저 SPA</strong>: `localStorage` 금지. HttpOnly 쿠키 또는 BFF 서버가 대신 보관.
- <strong>모바일 앱</strong>: iOS Keychain, Android EncryptedSharedPreferences 또는 Keystore.
- <strong>데스크톱 앱</strong>: OS의 Credential Store (macOS Keychain, Windows Credential Manager).

---

## 3. Opaque Token vs Self-contained (JWT)

Access Token 포맷은 RFC 6749가 규정하지 않는다. 구현체가 자유롭게 선택한다. 크게 두 가지 방식이 있다.

### Opaque Token — 불투명 토큰

서버만 의미를 아는 불투명한 문자열이다.

```
Authorization: Bearer a1b2c3d4e5f6g7h8i9j0
```

RS는 이 토큰을 그대로는 해석할 수 없다. AS에게 "이 토큰 유효한가?"를 물어봐야 한다(Introspection).

<strong>장점</strong>
- AS가 언제든 즉시 무효화 가능 (DB 레코드 삭제)
- 토큰 내용이 노출되지 않음
- 짧음(저장·전송 비용 낮음)

<strong>단점</strong>
- 매 요청마다 Introspection 호출 필요 (세션 방식의 단점과 유사)
- AS 가용성이 RS 가용성에 영향

### Self-contained Token — JWT

JWT(JSON Web Token)는 토큰 자체에 정보를 담고 서명한다.

```
eyJhbGciOiJSUzI1NiJ9.eyJzdWIiOiI0MiIsInNjb3BlIjoib3BlbmlkIn0.signature
```

디코딩하면 페이로드가 나온다.

```json
{
  "iss": "https://auth.example.com",
  "sub": "42",
  "aud": "api.example.com",
  "exp": 1715000000,
  "iat": 1714996400,
  "scope": "openid profile drive.readonly"
}
```

RS는 AS가 공개한 키(JWKS)로 서명을 검증하면 끝이다. AS와 실시간 통신이 필요 없다.

<strong>장점</strong>
- Stateless 검증 (AS 호출 불필요)
- 수평 확장에 유리
- 페이로드에서 사용자·Scope를 바로 추출

<strong>단점</strong>
- 즉시 무효화가 어려움 (블랙리스트 필요)
- 토큰이 길어짐 (1~4KB)
- 페이로드가 노출(서명만 있지 암호화 아님)

### 둘의 비교

```mermaid
flowchart TB
    subgraph OP[Opaque Token]
        O1[짧은 랜덤 문자열]
        O2[AS가 DB 조회]
        O3[즉시 무효화 쉬움]
    end
    subgraph JW[JWT]
        J1[헤더.페이로드.서명]
        J2[RS가 서명 검증]
        J3[Stateless]
        J4[무효화 어려움]
    end
    OP -.적합.-> S1[내부 시스템·<br>즉시 무효화 중요]
    JW -.적합.-> S2[대규모 분산·<br>수평 확장 중요]
```

| 관점 | Opaque | JWT |
|----|-----|----|
| 검증 | Introspection 호출 | 서명 검증 |
| 무효화 | DB 레코드 삭제 즉시 | 블랙리스트·짧은 수명 필요 |
| 상태 | AS 저장소 필요 | Stateless |
| 성능 | AS에 부하 | RS CPU 부하 |
| 크기 | 작음(20~40자) | 큼(1~4KB) |
| 디버깅 | 내용 안 보임 | jwt.io 등으로 확인 가능 |

### 하이브리드 전략

실무에서는 두 방식을 조합하기도 한다.

- <strong>Access Token = JWT</strong> (짧은 수명, 빠른 검증)
- <strong>Refresh Token = Opaque</strong> (장기간, 즉시 무효화 가능)

JWT의 짧은 수명이 무효화 난점을 완화하고, Refresh Token의 opaque 속성이 즉시 취소 가능성을 보장한다.

---

## 4. Token Introspection (RFC 7662)

Introspection은 AS가 RS에게 "이 토큰 유효한가, 어떤 정보인가"를 실시간 응답하는 엔드포인트다.

### 요청과 응답

```http
POST /introspect HTTP/1.1
Host: auth.example.com
Authorization: Basic <RS credentials>
Content-Type: application/x-www-form-urlencoded

token=a1b2c3d4e5f6g7h8i9j0
&token_type_hint=access_token
```

유효한 토큰인 경우 응답.

```json
{
  "active": true,
  "scope": "openid profile drive.readonly",
  "client_id": "abc123",
  "username": "alice@example.com",
  "sub": "42",
  "aud": "api.example.com",
  "iss": "https://auth.example.com",
  "exp": 1715000000,
  "iat": 1714996400
}
```

무효한 경우.

```json
{
  "active": false
}
```

### 언제 쓰는가

- <strong>Opaque Access Token 검증</strong>이 주 용도
- JWT여도 <strong>즉시 무효화 확인</strong>이 필요할 때 보조 수단
- <strong>세밀한 감사</strong>(누가 누구에게 발급했는지)

### 성능 고려

Introspection은 AS 호출이므로 매 요청마다 부르면 부하가 크다. 완화책.

- RS 쪽 캐싱 (수 초~수십 초)
- Introspection 결과를 짧은 시간 메모리에 저장
- 고빈도 경로는 JWT로 전환

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant RS as Resource Server
    participant Cache as RS 캐시
    participant AS as Authorization Server
    C->>RS: Bearer opaque-token
    RS->>Cache: 토큰 캐시 조회
    alt 캐시 히트 (30초 이내)
        Cache-->>RS: active=true, sub=42
    else 캐시 미스
        RS->>AS: POST /introspect
        AS-->>RS: {active:true, ...}
        RS->>Cache: 결과 저장
    end
    RS-->>C: 200 OK
```

### 인증 요구

Introspection 엔드포인트는 <strong>RS(또는 허가된 클라이언트)만</strong> 호출할 수 있어야 한다. 아니면 공격자가 탈취한 토큰의 정보를 조회하는 데 악용될 수 있다. RS에게 별도 Client Credentials를 발급해 Basic Auth로 인증한다.

---

## 5. Token Revocation (RFC 7009)

Revocation은 <strong>토큰을 명시적으로 폐기</strong>하는 엔드포인트다. 로그아웃, 기기 분실, 권한 철회 시나리오에서 쓰인다.

### 요청

```http
POST /revoke HTTP/1.1
Host: auth.example.com
Authorization: Basic <client credentials>
Content-Type: application/x-www-form-urlencoded

token=tGzv3JOkF0XG5Qx2TlKWIA
&token_type_hint=refresh_token
```

응답은 단순하다.

```http
HTTP/1.1 200 OK
```

이미 무효한 토큰을 폐기 요청해도 <strong>200 OK</strong>로 응답한다. 이는 "존재 여부를 드러내지 않기" 위한 설계다.

### token_type_hint

`token_type_hint`는 힌트일 뿐이다. AS가 먼저 그 타입부터 조회하지만, 못 찾으면 다른 타입도 검색한다. 기본값은 서버별로 다르므로 명시하는 것이 좋다.

- `access_token`
- `refresh_token`

### Refresh Token 폐기의 연쇄 효과

많은 AS가 Refresh Token 폐기 시 <strong>관련된 Access Token까지 함께 폐기</strong>한다. 이 동작은 규격이 강제하지 않으므로 각 AS 정책을 확인해야 한다.

```mermaid
flowchart TD
    R[Refresh Token 폐기] --> Q{AS 정책}
    Q -->|연쇄 폐기| A1[관련 Access Token 모두 무효]
    Q -->|독립| A2[Refresh만 무효<br>Access Token은 만료까지 유효]
    style A1 fill:#efe
    style A2 fill:#ffe
```

### Revocation의 한계

- <strong>JWT Access Token</strong>은 RS가 서명만 보고 판단하므로, AS의 폐기가 RS에 즉시 반영되지 않는다. 블랙리스트 공유 또는 Introspection 호출이 필요하다.
- AS에 재요청이 가지 않는 한 만료까지 유효하다.

---

## 6. 로그아웃 체크리스트

"로그아웃 버튼을 누르면 뭘 해야 하나?"는 의외로 어려운 질문이다. 세션 기반은 단순하지만, OAuth 환경은 여러 토큰이 얽혀 있다.

### 체크리스트

```mermaid
mindmap
  root((로그아웃 시 해야 할 일))
    클라이언트 측
      메모리의 Access Token 제거
      localStorage 토큰 제거
      세션 쿠키 제거
    AS 측
      /revoke로 Refresh Token 폐기
      AS 세션 종료 OIDC RP-Initiated Logout
    RS 측
      Access Token 블랙리스트
      JWT는 jti 단위 블랙리스트
    감사
      로그아웃 이벤트 기록
      타 기기 통지
```

### 단계별 처리

1. <strong>클라이언트 로컬 정리</strong>
   - Access Token(메모리)·Refresh Token(저장소) 제거
   - 세션 쿠키 제거
   - UI 상태 초기화

2. <strong>AS에 폐기 요청</strong>
   - `/revoke`에 Refresh Token 폐기
   - 연쇄 폐기가 설정되어 있다면 Access Token도 자동 무효
   - OIDC를 쓰면 `end_session_endpoint` 호출

3. <strong>RS 측 처리 (JWT인 경우)</strong>
   - `jti`(JWT ID) 블랙리스트에 추가
   - 짧은 TTL 캐시(만료 시각까지만 보관)
   - 멀티 RS라면 블랙리스트 공유 메커니즘 필요

4. <strong>사용자에게 확인 피드백</strong>
   - 로그아웃 완료 페이지
   - 타 기기 알림("다른 기기에서 로그아웃됨")

### 싱글 로그아웃 (Single Logout)

OIDC는 여러 Relying Party 간 동시 로그아웃을 위한 규격을 제공한다.

- <strong>Front-Channel Logout</strong>: 브라우저 iframe으로 각 RP에 로그아웃 알림
- <strong>Back-Channel Logout</strong>: AS가 각 RP 서버에 직접 알림
- <strong>RP-Initiated Logout</strong>: RP가 AS에 로그아웃을 요청

CH9, CH11에서 OIDC 문맥 속에서 자세히 다룬다.

### 토큰 수명 시각화

```mermaid
timeline
    title Access Token 수명 경계 시나리오
    00:00 : 로그인 성공, AT1 발급 (expires_in 3600s)
    00:30 : API 호출 정상 (AT1 유효)
    01:00 : AT1 만료, RT로 AT2 발급 (Rotation 시 RT도 교체)
    01:30 : 다른 기기 로그인, RT 탈취 사고
    01:31 : 탈취자가 RT 사용, AT3 발급
    01:32 : 정상 클라이언트가 RT(이전) 사용 시도
    01:33 : AS가 재사용 탐지, 전체 세션 폐기
    01:34 : 사용자에게 재로그인 유도
```

### 구현 시 주의점

| 실수 | 영향 | 올바른 대처 |
|----|-----|----------|
| Access Token만 삭제, Refresh 남겨둠 | 장기간 피해 | `/revoke` 호출 필수 |
| JWT인데 블랙리스트 없음 | 만료까지 유효 | 짧은 TTL + 블랙리스트 |
| 로그아웃 후 리다이렉트 없음 | 캐시된 페이지 노출 | Cache-Control 헤더 + 302 |
| OIDC 세션 종료 안 함 | 재로그인 시 자동 재인증 | `end_session_endpoint` 호출 |

---

::: tip 핵심 정리
- Access Token은 짧은 수명(5~60분)의 자원 접근 증표로 RS에게만 제시하고, Refresh Token은 장기(며칠~몇 개월) 자격으로 AS `/token`에만 전송한다. Bearer 방식은 탈취 시 즉시 오남용되므로 HTTPS와 짧은 수명이 필수다.
- Opaque 토큰은 AS가 즉시 무효화 가능하지만 매 요청 Introspection 부하가 있고, JWT는 Stateless 검증으로 확장에 유리하지만 즉시 무효화가 어렵다. Access는 JWT, Refresh는 Opaque 조합이 자주 쓰인다.
- Introspection(RFC 7662)은 Opaque 토큰의 실시간 유효성 조회, Revocation(RFC 7009)은 명시적 폐기 용도다. Refresh Token Rotation은 탈취 탐지의 핵심 메커니즘이다.
- 로그아웃은 클라이언트 로컬 정리, AS `/revoke` 호출, RS 블랙리스트 등록, OIDC 싱글 로그아웃 호출까지 여러 레이어에서 처리해야 하며, JWT 환경에서는 짧은 TTL + 블랙리스트 조합이 현실적이다.
:::

## 다음 챕터

- 이전 : [나머지 Grant Type과 그 한계](/study/oauth/07-other-grant-types)
- 다음 : [OIDC는 왜 태어났나](/study/oauth/09-why-oidc)
