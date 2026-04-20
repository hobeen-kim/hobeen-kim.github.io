---
title: "Keycloak 실전"
description: "Keycloak을 처음 도입하는 개발자부터 IAM 아키텍트까지, 설치·운영·SPI 커스터마이징·K8s 배포·업그레이드를 한 권으로 다룬다."
date: 2026-04-17
tags: [Keycloak, IAM, OAuth, OIDC, SAML, SSO, Quarkus, Kubernetes]
---

# Keycloak 실전

OAuth 스터디에서 Keycloak을 "Authorization Server로 쓰는 방법"을 다뤘다면, 이 스터디는 Keycloak 그 자체를 깊이 운영·확장하는 관점으로 접근한다. Realm/Client 같은 기본 개념부터 Authorization Services·SPI 커스터마이징·Kubernetes Operator 배포·버전 업그레이드까지, 제공자(Provider)와 운영자(Operator)의 시선에서 체계적으로 학습한다.

::: info 선행 지식
OAuth 2.0과 OpenID Connect의 기본 개념은 [OAuth 스터디](/study/oauth/)에서 전제된다. 특히 [CH17. Keycloak으로 AS 구축](/study/oauth/17-keycloak)은 "소비자 관점"의 요약이고, 이 스터디는 그 내용을 훨씬 깊게 풀어낸다.
:::

## 학습 로드맵

```mermaid
flowchart TD
    CH1[CH1. 개요] --> CH2[CH2. 핵심 개념과 용어]
    CH2 --> CH3[CH3. Realm · Organizations]
    CH3 --> CH4[CH4. Client · Service Account]
    CH3 --> CH5[CH5. 사용자와 자격 증명]
    CH4 --> CH6[CH6. Role · Group · Composite]
    CH5 --> CH6
    CH6 --> CH7[CH7. Scope · Protocol Mapper]
    CH7 --> CH8[CH8. Authorization Services · UMA]
    CH7 --> CH9[CH9. SAML · Token Exchange]
    CH4 --> CH10[CH10. Authentication Flow]
    CH10 --> CH11[CH11. Password Policy · Brute Force]
    CH10 --> CH12[CH12. MFA]
    CH5 --> CH13[CH13. User Federation]
    CH13 --> CH14[CH14. Identity Brokering]
    CH10 --> CH15[CH15. SPI 개요]
    CH15 --> CH16[CH16. 커스텀 Authenticator]
    CH15 --> CH17[CH17. 커스텀 User Storage]
    CH15 --> CH18[CH18. Theme]
    CH4 --> CH19[CH19. Infinispan HA]
    CH19 --> CH20[CH20. K8s · Operator]
    CH20 --> CH21[CH21. DB 성능]
    CH3 --> CH22[CH22. Admin REST API]
    CH20 --> CH22
    CH22 --> CH23[CH23. Backup · Realm 이관]
    CH20 --> CH24[CH24. 모니터링 · 업그레이드]
    CH23 --> CH24
```

## 목차

### Keycloak
1. [Keycloak 개요](/study/keycloak/01-overview) — IAM 개요, 라이선스, OAuth 스터디와의 관계
2. [핵심 개념과 용어](/study/keycloak/02-core-concepts) — Realm·User·Client 외 주요 객체·용어 사전

### 핵심 객체 모델
3. [Realm과 Organizations](/study/keycloak/03-realm-organizations) — 멀티테넌시 설계, v26+ Organizations
4. [Client와 Service Account](/study/keycloak/04-client-service-account) — Access Type, Client Authenticator, 시크릿 관리
5. [사용자와 자격 증명](/study/keycloak/05-user-credentials) — 해싱(Argon2/PBKDF2), OTP, WebAuthn 등록
6. [Role·Group과 Composite Role](/study/keycloak/06-role-group) — 권한 모델링 패턴

### 토큰·권한·프로토콜
7. [Client Scope와 Protocol Mapper](/study/keycloak/07-protocol-mapper) — 토큰 클레임 커스터마이징, Consent
8. [Authorization Services와 UMA 2.0](/study/keycloak/08-authz-uma) — Fine-grained 리소스 권한
9. [SAML 2.0과 Token Exchange](/study/keycloak/09-saml-token-exchange) — SAML 지원, RFC 8693 임퍼소네이션

### 인증 정책과 플로우
10. [인증 플로우 커스터마이징](/study/keycloak/10-auth-flow) — Browser/Direct Grant/Reset 플로우 편집
11. [Password Policy와 Brute Force](/study/keycloak/11-password-policy) — Required Actions, 계정 잠금
12. [MFA — TOTP / WebAuthn](/study/keycloak/12-mfa) — 2단계 인증과 Recovery Codes

### 페더레이션
13. [User Federation (LDAP/AD + SCIM)](/study/keycloak/13-user-federation) — 기업 내부 사용자 소스 연동
14. [Identity Brokering](/study/keycloak/14-identity-brokering) — Google/GitHub/Kakao 외부 IdP 연결

### 커스터마이징 (SPI)
15. [SPI로 Keycloak 확장](/study/keycloak/15-spi-overview) — providers/ 디렉토리, Quarkus 클래스로더
16. [커스텀 Authenticator](/study/keycloak/16-custom-authenticator) — 사내 사번 검증 같은 추가 단계
17. [커스텀 User Storage](/study/keycloak/17-custom-user-storage) — 레거시 DB를 사용자 소스로
18. [Theme 커스터마이징](/study/keycloak/18-theme) — 로그인 화면 브랜딩

### 운영과 확장
19. [Infinispan HA 클러스터링](/study/keycloak/19-ha-clustering) — 분산 캐시, Multi-site
20. [Kubernetes + Operator 배포](/study/keycloak/20-k8s-operator) — Keycloak Operator, Custom Resource
21. [데이터베이스와 성능](/study/keycloak/21-database-performance) — PostgreSQL 튜닝, 오프라인 세션
22. [Admin REST API와 자동화](/study/keycloak/22-admin-rest-api) — 운영 자동화, GitOps
23. [Backup/Restore와 Realm 이관](/study/keycloak/23-backup-restore) — Realm Import/Export, 재해 복구
24. [모니터링·감사와 업그레이드](/study/keycloak/24-monitoring-upgrade) — Event Listener, Metrics, 메이저 업그레이드

## 관련 자료

::: info 함께 보면 좋은 자료
- [OAuth 2.0 + OpenID Connect 스터디](/study/oauth/) — OAuth/OIDC 개념 선행
- [OAuth 스터디 CH17. Keycloak으로 AS 구축](/study/oauth/17-keycloak) — 소비자 관점 요약
- [Keycloak 개념 및 간단 사용 포스트](/posts/tech/2025-10-01-keycloak) — Docker Compose 실습 레퍼런스
:::
