---
title: "Keycloak 개요와 역사"
description: "Keycloak이 해결하는 IAM 문제, 역사, 라이선스, Wildfly→Quarkus 대전환을 정리한다."
date: 2026-04-17
tags: [Keycloak, IAM, 역사, Quarkus]
prev: /study/keycloak/
next: /study/keycloak/02-quickstart
---

# Keycloak 개요와 역사

::: info 학습 목표
- IAM(Identity and Access Management) 문제를 Keycloak이 어떻게 푸는지 설명할 수 있다.
- Wildfly→Quarkus 런타임 전환이 운영에 미친 영향을 이해한다.
- Keycloak 라이선스와 상용 제품(Red Hat Build of Keycloak, Red Hat SSO)의 관계를 파악한다.
- OAuth 스터디 CH17과 이 스터디의 포지셔닝 차이를 구분한다.
:::

---

## 1. IAM 문제와 Keycloak의 자리

IAM(Identity and Access Management)은 "누가(Identity) 무엇을(Access) 할 수 있는가"를 일관되게 관리하는 영역이다. 작은 서비스라면 사용자 테이블 하나와 비밀번호 해시만으로도 충분해 보이지만, 서비스가 성장하면 다음과 같은 요구가 한꺼번에 쏟아진다.

| 요구 | 자체 구현 시 부담 |
|------|------------------|
| 소셜 로그인(Google/Kakao/Apple) | IdP별 OAuth/OIDC 플로우 각각 구현, 토큰 저장, 실패 대응 |
| SSO(Single Sign-On) | 서비스 간 세션 공유, 쿠키 도메인/서명 정책 |
| 비밀번호 정책·MFA·Passkey | 해싱 알고리즘 관리, TOTP/WebAuthn 등록 UX |
| 감사 로그·이벤트 | 로그인 실패·관리자 행위 추적, 외부 SIEM 연동 |
| 관리자 UI | 사용자 생성/비활성화/초기화, 역할 부여 |
| 프로토콜 다양성 | OIDC, OAuth 2.0, SAML 2.0, Token Exchange(RFC 8693) |

자체 구현은 "지금 필요한 한 가지"로 시작하지만, 6개월 뒤에는 전담 팀이 필요한 수준이 된다. <strong>Keycloak</strong>은 이 영역을 "외부에 둔다"는 전략의 오픈소스 구현체다. 애플리케이션은 OIDC/SAML 같은 표준 프로토콜만 구현하고, 사용자 저장·로그인 UX·MFA·소셜 로그인은 Keycloak에 위임한다.

```mermaid
flowchart LR
    subgraph Before[자체 구현]
        A1[앱 A] --- U1[사용자 DB A]
        A2[앱 B] --- U2[사용자 DB B]
        A3[앱 C] --- U3[사용자 DB C]
    end
    subgraph After[Keycloak 도입]
        B1[앱 A] --> KC[(Keycloak)]
        B2[앱 B] --> KC
        B3[앱 C] --> KC
        KC --- UDB[(통합 사용자 저장소)]
        KC --- Social[소셜 IdP]
        KC --- LDAP[LDAP/AD]
    end
```

Keycloak의 위치는 명확하다. "인증(Authentication)과 인가(Authorization)의 중앙 허브"다. 앱은 사용자 정보를 직접 저장하지 않고, Keycloak이 발급한 토큰(Access Token/ID Token)을 검증해서 사용자를 식별한다.

### 경쟁군 비교

IAM 영역에는 Keycloak 외에도 여러 대안이 있다. 큰 범주로 나누면 다음과 같다.

| 제품 | 형태 | 특징 |
|------|------|------|
| Keycloak | 오픈소스 셀프호스팅 | Apache 2.0, CNCF, Realm·SPI 중심 |
| Auth0 (Okta) | SaaS | 개발 편의성 최고, 벤더 종속·비용 이슈 |
| Okta Workforce | SaaS | 대기업·B2B SSO 표준, 디렉토리 연동 강력 |
| Azure Entra ID | SaaS (MS 생태계) | M365/Azure와 긴밀 통합 |
| AWS Cognito | SaaS (AWS 생태계) | AWS 서비스 연동, Keycloak 대비 기능 제한 |
| Ory Kratos/Hydra | 오픈소스 컴포넌트 | 작은 단위 조합, 러닝커브 높음 |
| Authelia | 오픈소스 Forward-Auth | 경량, 기능 범위 좁음 |

Keycloak은 "셀프호스팅·풀스택·표준 프로토콜"이라는 조합에서 가장 균형 잡힌 선택지로 자주 꼽힌다. 데이터 소버린티 요구가 있거나, 커스터마이징 깊이가 필요하거나, 벤더 락인을 피하려는 조직에 특히 잘 맞는다.

### OAuth 스터디와의 연결

[OAuth 스터디 CH5. 역할과 용어](/study/oauth/05-roles-and-terms)에서 정리한 역할 구분을 복습하면 Keycloak의 자리를 더 분명히 볼 수 있다.

- Resource Owner → 최종 사용자
- Client → 앱(웹/모바일/백엔드)
- Authorization Server → <strong>Keycloak</strong>
- Resource Server → 우리 API 서버

[CH6. Authorization Code Flow](/study/oauth/06-authorization-code-flow)의 표준 플로우에서 "AS" 자리에 그대로 Keycloak을 끼워 넣으면 된다.

---

## 2. Keycloak의 역사

Keycloak은 2014년 Red Hat이 JBoss 생태계의 SSO 요구를 해결하기 위해 시작한 오픈소스 프로젝트다. 초기 이름은 그대로 "Keycloak"이었고, 곧바로 Red Hat의 상용 지원 버전인 <strong>Red Hat SSO</strong>(RH-SSO)로도 포장되어 엔터프라이즈에 공급됐다.

### 주요 연혁

```mermaid
timeline
    title Keycloak 주요 버전 연혁
    2014 : 1.0 출시, JBoss/Wildfly 기반
    2018 : 4.x, OIDC 1.0 완전 지원 / Account Console
    2020 : 12.x, Quarkus distribution 실험 배포
    2022 : 17.0, Quarkus 정식 전환 (Wildfly deprecated)
    2023 : CNCF Incubating 프로젝트 승격
    2024 : 25.x, Organizations, Client Policy v2
    2025 : 26.x, Argon2 기본, WebAuthn 강화
```

- 2014년 1.0 릴리스. Wildfly(구 JBoss AS) 위에서 동작하는 Java 웹 애플리케이션으로 출발했다.
- 2018년 전후 OIDC 1.0 스펙을 충실히 구현하면서 "오픈소스 OIDC Provider"로 자리잡았다. Account Console(사용자가 자기 프로필/세션을 관리하는 UI)도 이 무렵 도입됐다.
- 2020년 12.x에서 Quarkus 기반 배포판을 실험적으로 제공. 이때까지의 기본은 여전히 Wildfly였다.
- 2022년 17.0에서 <strong>Quarkus</strong>를 정식 런타임으로 채택. 이전 Wildfly 배포는 deprecated로 지정됐고, 이후 18.x에서 완전히 제거됐다.
- 2023년 <strong>CNCF Incubating</strong> 프로젝트로 승격. Kubernetes 생태계의 일원으로 공식 편입됐다.
- 2024~2025년 Organizations(B2B 조직), Client Policy v2, Argon2 기본 해시, WebAuthn/Passkey UX 강화 등 기능 확장이 이어졌다.

### 버전 네이밍 규칙

Keycloak의 버전 번호는 한 번 크게 점프한 적이 있다. 초기에 1.x~4.x로 올라갔고, 한동안 날짜 기반 버전(`4.8.3`)과 연도 기반(`10.x`, `11.x`)이 섞여 혼란을 줬다. Quarkus 전환 시점에 <strong>17.0</strong>으로 재출발한 이후로는 한 자리 메이저(17, 18, …, 26)를 일정 주기로 올리는 방식이 정착됐다.

| 버전대 | 시기 | 비고 |
|--------|------|------|
| 1.x ~ 3.x | 2014~2017 | Wildfly 기반, 초기 OIDC/SAML 구현 |
| 4.x ~ 16.x | 2018~2021 | OIDC/OAuth 기능 안정화, Quarkus 실험 |
| 17.x ~ 현재 | 2022~ | Quarkus 정식, 기능 고도화·K8s 네이티브 |

메이저 업그레이드는 거의 매 릴리스마다 "주의할 Breaking Change"가 공지된다. 상세한 업그레이드 전략은 CH25에서 다룬다.

### CNCF 편입의 의미

CNCF Incubating 프로젝트가 됐다는 것은 단순한 이름값 이상이다.

- 거버넌스가 Red Hat 단독에서 CNCF TOC 감독 아래로 이동했다.
- Kubernetes Operator, Helm Chart, Observability(Prometheus/OpenTelemetry) 같은 주변 생태계가 공식 로드맵에 포함됐다.
- 대기업 고객이 "벤더 락인 아닌 중립 프로젝트"로 도입 승인을 받기 쉬워졌다.

---

## 3. Wildfly → Quarkus 대전환

Keycloak의 기술적 전환점은 단연 <strong>Quarkus</strong> 런타임 채택이다. 이 변화는 단순한 런타임 교체가 아니라 "JVM 애플리케이션을 컨테이너에 어떻게 띄울 것인가"에 대한 철학 전환이다.

### Wildfly와 Quarkus 비교

| 항목 | Wildfly (구) | Quarkus (신, v17+) |
|------|--------------|-------------------|
| 설계 철학 | 범용 Java EE 앱 서버 | 컨테이너·쿠버네티스 네이티브 |
| 빌드 단계 | 없음 (런타임 초기화) | `kc.sh build` 로 사전 최적화 |
| 부팅 시간 | 10~30초 | 2~5초 |
| 런타임 메모리 | 500MB+ | 200MB 수준 |
| Native Image | 미지원 | GraalVM 네이티브 빌드 가능 |
| 설정 | standalone.xml (복잡) | `keycloak.conf` + CLI 옵션 |
| 확장(Provider) 로딩 | 모듈 시스템 | `providers/` 디렉토리에 JAR 드롭 |

Quarkus의 핵심은 "빌드 타임에 최대한 작업을 끝내고, 런타임에는 그 결과만 쓴다"는 접근이다. Keycloak에서 이는 `kc.sh build` 단계로 드러난다. Provider 스캔·DB 벤더 결정·HTTP 기능 활성화 같은 결정을 빌드 타임에 고정해 버리고, 런타임 부팅은 고정된 결과를 읽기만 한다.

```mermaid
xychart-beta
    title "Wildfly vs Quarkus — Boot Time (seconds)"
    x-axis ["Wildfly 16", "Wildfly 18 (deprecated)", "Quarkus 17", "Quarkus 22", "Quarkus 26"]
    y-axis "seconds" 0 --> 35
    bar [28, 22, 5, 4, 3]
```

### 운영 영향

- <strong>부팅 시간 단축</strong>: 쿠버네티스 Rolling Update 시 Pod 교체 속도가 빨라진다. 스케일 아웃 반응성이 개선된다.
- <strong>메모리 절감</strong>: HPA(Horizontal Pod Autoscaler) 스케일 아웃 비용이 줄어든다. 같은 트래픽을 더 적은 Pod로 처리 가능하다.
- <strong>설정 구조화</strong>: standalone.xml의 XML 지옥에서 탈출. `--db=postgres`처럼 CLI 플래그로 끝난다.
- <strong>러닝 커브</strong>: 기존 Wildfly 운영 지식은 대부분 무효화됐다. `kcadm.sh` 자동화 스크립트도 문법이 바뀌었다.
- <strong>확장(Provider) 모델</strong>: 과거 JBoss 모듈 시스템 대신 `providers/` 디렉토리에 JAR을 드롭하고 `kc.sh build`로 스캔하는 단순 모델로 바뀌었다.

### 전환 체크리스트

기존 Wildfly 기반 Keycloak을 운영하다가 Quarkus로 올라간 조직은 다음을 다시 점검해야 한다.

| 항목 | 전환 시 확인 |
|------|-------------|
| 배포 파이프라인 | `kc.sh build` 이후 `kc.sh start --optimized` 2단계 적용 |
| 확장 Provider | 모듈(JBoss CLI) → JAR 드롭 방식으로 재패키징 |
| 구성 파일 | standalone.xml → `keycloak.conf` + CLI 플래그 |
| 자동화 스크립트 | `jboss-cli.sh` 문법 → `kc.sh`·`kcadm.sh` 문법 |
| Docker 이미지 | WildFly 베이스 → `quay.io/keycloak/keycloak` |
| 헬스체크 | `/auth/` 프리픽스 제거(기본 root 경로) |

기본 컨텍스트 경로가 `/auth`에서 `/`로 바뀐 것은 특히 주의해야 한다. 기존 앱이 `auth.example.com/auth/realms/...` 기준으로 구성돼 있다면 `KC_HTTP_RELATIVE_PATH=/auth`로 호환 모드를 유지할 수 있다.

CH21에서 Kubernetes Operator와 함께 다시 다룬다.

---

## 4. 라이선스와 상용 지원

Keycloak은 <strong>Apache License 2.0</strong>으로 배포된다. 상용 이용·수정·재배포에 제한이 없다. 그래서 많은 기업이 사내 IAM으로 Keycloak을 그대로 쓴다.

### 상용 트랙

상용 지원이 필요한 조직을 위해 Red Hat은 두 가지 제품 라인을 유지한다.

| 이름 | 관계 | 특징 |
|------|------|------|
| Keycloak (커뮤니티) | 업스트림 오픈소스 | Apache 2.0, 빠른 릴리스 주기, Red Hat 지원 없음 |
| Red Hat Build of Keycloak (RHBK) | Keycloak 위에 Red Hat 빌드·지원 추가 | OpenShift 중심, CVE/보안 패치 장기 지원 |
| Red Hat Single Sign-On (RH-SSO) | 구 제품명, RHBK로 대체됨 | 2023년까지 유지되던 상용 브랜드 |

- 커뮤니티 Keycloak은 `quay.io/keycloak/keycloak` 이미지로 공개돼 있다.
- RHBK는 Red Hat 서브스크립션이 있는 조직에게 제공된다. 기술 지원·보안 패치 SLA·인증된 Operator 같은 "엔터프라이즈 계약이 필요한 것"들이 포함된다.
- 공식 Red Hat 문서는 RHBK 기준으로 작성된다. 커뮤니티 기능 중 일부는 RHBK에선 "Technology Preview"로 구분된다.

### 실무 선택 가이드

- 스타트업·내부 도구: 커뮤니티 Keycloak. 충분하다.
- 금융·공공·규제 산업: RHBK 또는 RH-SSO 서브스크립션. 보안 패치 SLA와 지원 계약이 필수다.
- 글로벌 서비스, 자체 운영 역량 있음: 커뮤니티 + 내부 SRE 팀. 대부분의 테크 기업이 여기 속한다.

### 라이선스 오해 방지

Apache 2.0이라는 이유로 종종 "Red Hat 허락 없이 Keycloak 이름을 붙인 SaaS를 팔 수 있나"라는 질문이 나온다. 두 가지로 답할 수 있다.

- 코드와 바이너리의 재배포·수정·상용 이용은 자유다.
- "Keycloak"이라는 상표(Trademark)는 별도 보호 대상이다. 상업 제품명으로 사용하려면 CNCF의 상표 가이드라인을 따라야 한다.

이 구분은 Linux(커널 코드 자유 vs "Linux" 상표)와 동일한 구조다. 내부 운영·고객용 SSO로 쓰는 데는 상표 이슈가 없다.

---

## 5. OAuth 스터디 CH17과의 관계

[OAuth 스터디 CH17. Keycloak으로 AS 구축](/study/oauth/17-keycloak)은 "OAuth 2.0 소비자 입장에서 Keycloak을 AS로 어떻게 쓸지"에 초점을 맞췄다. Realm 하나 만들고 Client 등록하고 토큰을 받는 수준의 Quick Tour다.

이 스터디(Keycloak 실전)는 그 반대편의 관점을 다룬다.

| 구분 | OAuth CH17 | Keycloak 스터디 |
|------|-----------|----------------|
| 관점 | 사용자(소비자) | 제공자·운영자 |
| 범위 | Realm·Client·토큰 요청 | 전체 관리, SPI, K8s, 업그레이드 |
| 깊이 | "쓸 수 있을 정도" | "운영하고 확장할 수 있을 정도" |
| 길이 | 1챕터 | 25챕터 |

OAuth 스터디를 읽었다면 "왜 Keycloak이 필요한가"는 이미 알고 있다. 이제는 Keycloak 안쪽으로 들어가, Authentication Flow를 뜯고, 커스텀 Authenticator를 만들고, Kubernetes에 Operator로 배포하고, 메이저 버전 업그레이드를 안전하게 수행하는 방법을 다룬다.

```mermaid
flowchart LR
    OAuth[OAuth 스터디<br>CH17. Keycloak] -->|"Keycloak으로<br>AS 구축 Quick Tour"| KC1[Keycloak 스터디<br>CH1~3. 입문]
    KC1 --> KC2[CH4~10. 객체 모델·토큰·권한]
    KC2 --> KC3[CH11~15. 인증 정책·페더레이션]
    KC3 --> KC4[CH16~19. SPI 확장]
    KC4 --> KC5[CH20~25. 운영]
```

### 이 스터디를 읽는 순서 제안

- 이미 Keycloak을 운영 중이라면 CH1~5를 훑고 CH6부터 정독.
- 신규 도입이라면 순서대로 읽되, CH2(Quickstart)에서 실제 Compose를 띄우고 CH3(Admin Console)을 눈으로 함께 따라가는 것을 추천.
- SPI 커스터마이징만 관심이라면 CH5·CH11·CH16 이후를 중점 학습.
- Kubernetes 배포만 관심이라면 CH20~21을 먼저 읽고 필요할 때 앞장으로 돌아오기.

### 이 챕터 이후 당장 할 일

1. 로컬에 Docker가 설치돼 있는지 확인.
2. [CH2. 로컬에 Keycloak 기동](/study/keycloak/02-quickstart)의 Compose 파일을 그대로 띄워 보기.
3. Admin Console에 로그인해 master realm의 Realm Selector 위치를 눈에 익히기.

### 이 스터디의 범위 한눈에

25개 챕터 전체가 다룰 주제를 범주별로 정리하면 다음과 같다. 챕터 사이의 연결은 서두 목차의 Mermaid 로드맵에 그려 뒀다.

| 범주 | 챕터 | 무엇을 배우는가 |
|------|------|----------------|
| 입문 | CH1~3 | 개요·기동·Admin Console |
| 객체 모델 | CH4~7 | Realm·Client·User·Role |
| 토큰·권한·프로토콜 | CH8~10 | Scope·Mapper·UMA·SAML·Token Exchange |
| 인증 정책 | CH11~13 | Flow·Policy·MFA |
| 페더레이션 | CH14~15 | LDAP·Social IdP |
| SPI 확장 | CH16~19 | Authenticator·User Storage·Theme |
| 운영 | CH20~25 | HA·K8s·DB·REST API·Backup·Upgrade |

"도구를 설치하는 법"에서 시작해 "도구를 만드는 법"까지 내려간 뒤, "도구를 운영하는 법"으로 확장하는 구성이다.

### 실습 환경 권장사항

전체 스터디를 실습하려면 다음 환경이 권장된다.

- 로컬 OS: macOS / Linux / Windows + WSL2 (모두 가능)
- Docker Desktop 또는 OrbStack: Compose 기능 사용
- 메모리 8GB 이상: Keycloak + PostgreSQL + 보조 컨테이너 동시 기동
- JDK 17+ (SPI 커스터마이징 실습 시)
- kubectl + minikube/kind (CH21~22 K8s 실습 시)

준비가 부족해도 CH1~15는 Docker Compose만으로 충분히 따라올 수 있다. K8s·SPI 실습은 해당 챕터 도달 시점에 추가 설치를 검토하면 된다.

### 자주 받는 초기 질문

스터디에 들어가기 전 자주 나오는 의문을 미리 정리한다. 본문 각 장에서 더 깊게 다루지만, 감을 잡는 데 도움이 될 것이다.

- "Keycloak이 없어도 OAuth 2.0은 쓸 수 있지 않은가" → 맞다. 자체 구현도 가능하다. 다만 OIDC/SAML·MFA·소셜·감사·관리 UI를 모두 직접 만들 계획이 없다면, Keycloak은 합리적인 디폴트다.
- "토큰 발급 속도가 충분한가" → Quarkus 전환 후 단일 Pod에서 수백 TPS 이상 가볍게 처리한다. Infinispan 캐시(CH20)와 DB 튜닝(CH22)을 병행하면 대규모 트래픽도 문제없다.
- "업그레이드가 쉬운가" → 쉬운 편은 아니다. 메이저 버전마다 Breaking Change가 누적된다. 그래서 이 스터디의 마지막 챕터(CH25)가 업그레이드와 모니터링에 통째로 할당돼 있다.
- "무료로 전부 쓸 수 있는가" → 코드·기능 전체가 Apache 2.0이다. 상용 제품에 통합해도 라이선스 비용이 없다. "상용 지원(SLA·CVE 대응 계약)"이 필요할 때만 RHBK 서브스크립션을 고려한다.

### 이 스터디를 쓴 시점의 기준

- 커뮤니티 Keycloak <strong>26.x</strong>를 기준으로 한다.
- Docker 이미지 태그는 `quay.io/keycloak/keycloak:26.1`을 사용한다.
- Admin Console 스크린 설명은 v26 레이아웃 기준이다. v24 이하는 메뉴 구조가 일부 다르다.
- Quarkus 배포판만 다룬다. Wildfly 배포판은 이미 제거된 지 오래된 과거 스택이다.

버전이 올라가면서 옵션 이름이 바뀌는 경우가 있다. 본문에서 설명한 환경 변수와 CLI 플래그가 동작하지 않는다면, 먼저 Keycloak 공식 Release Notes의 Breaking Changes 섹션을 확인하는 것이 좋다.

---

::: tip 핵심 정리
- Keycloak은 인증·인가를 중앙 허브로 위임하는 오픈소스 IAM 솔루션이다. 자체 구현의 장기 부담을 표준 프로토콜(OIDC/SAML)로 대체한다.
- 2014년 Red Hat이 시작한 프로젝트이며 2023년 CNCF Incubating으로 편입되어 Kubernetes 생태계의 일원이 됐다.
- 17.x(2022)부터 Wildfly를 버리고 Quarkus로 전환했다. 빌드 타임 최적화·부팅 단축·메모리 절감이 핵심 이득이다.
- 라이선스는 Apache 2.0. 상용 지원은 Red Hat Build of Keycloak(과거 Red Hat SSO)으로 제공된다.
- 이 스터디는 OAuth CH17의 소비자 관점을 넘어 제공자·운영자 관점을 25챕터에 걸쳐 다룬다.
:::

## 다음 챕터

- 이전 : [Keycloak 실전 개요](/study/keycloak/)
- 다음 : [로컬에 Keycloak 기동](/study/keycloak/02-quickstart)
