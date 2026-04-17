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
    CH1[CH1. 개요와 역사] --> CH2[CH2. 로컬 기동]
    CH2 --> CH3[CH3. Admin Console]
    CH3 --> CH4[CH4. Realm · Organizations]
    CH4 --> CH5[CH5. Client · Service Account]
    CH4 --> CH6[CH6. 사용자와 자격 증명]
    CH5 --> CH7[CH7. Role · Group · Composite]
    CH6 --> CH7
    CH7 --> CH8[CH8. Scope · Protocol Mapper]
    CH8 --> CH9[CH9. Authorization Services · UMA]
    CH8 --> CH10[CH10. SAML · Token Exchange]
    CH5 --> CH11[CH11. Authentication Flow]
    CH11 --> CH12[CH12. Password Policy · Brute Force]
    CH11 --> CH13[CH13. MFA]
    CH6 --> CH14[CH14. User Federation]
    CH14 --> CH15[CH15. Identity Brokering]
    CH11 --> CH16[CH16. SPI 개요]
    CH16 --> CH17[CH17. 커스텀 Authenticator]
    CH16 --> CH18[CH18. 커스텀 User Storage]
    CH16 --> CH19[CH19. Theme]
    CH5 --> CH20[CH20. Infinispan HA]
    CH20 --> CH21[CH21. K8s · Operator]
    CH21 --> CH22[CH22. DB 성능]
    CH3 --> CH23[CH23. Admin REST API]
    CH23 --> CH24[CH24. Backup · Realm 이관]
    CH21 --> CH25[CH25. 모니터링 · 업그레이드]
    CH24 --> CH25
```

## 목차

### Keycloak 입문
1. [Keycloak 개요와 역사](/study/keycloak/01-overview) — IAM 개요, Wildfly→Quarkus 전환, 라이선스
2. [로컬에 Keycloak 기동](/study/keycloak/02-quickstart) — Docker Compose + PostgreSQL, start-dev vs start
3. [Admin Console 구조](/study/keycloak/03-admin-console) — 메뉴 지도와 주요 워크플로우

### 핵심 객체 모델
4. [Realm과 Organizations](/study/keycloak/04-realm-organizations) — 멀티테넌시 설계, v26+ Organizations
5. [Client와 Service Account](/study/keycloak/05-client-service-account) — Access Type, Client Authenticator, 시크릿 관리
6. [사용자와 자격 증명](/study/keycloak/06-user-credentials) — 해싱(Argon2/PBKDF2), OTP, WebAuthn 등록
7. [Role·Group과 Composite Role](/study/keycloak/07-role-group) — 권한 모델링 패턴

### 토큰·권한·프로토콜
8. [Client Scope와 Protocol Mapper](/study/keycloak/08-protocol-mapper) — 토큰 클레임 커스터마이징, Consent
9. [Authorization Services와 UMA 2.0](/study/keycloak/09-authz-uma) — Fine-grained 리소스 권한
10. [SAML 2.0과 Token Exchange](/study/keycloak/10-saml-token-exchange) — SAML 지원, RFC 8693 임퍼소네이션

### 인증 정책과 플로우
11. [인증 플로우 커스터마이징](/study/keycloak/11-auth-flow) — Browser/Direct Grant/Reset 플로우 편집
12. [Password Policy와 Brute Force](/study/keycloak/12-password-policy) — Required Actions, 계정 잠금
13. [MFA — TOTP / WebAuthn](/study/keycloak/13-mfa) — 2단계 인증과 Recovery Codes

### 페더레이션
14. [User Federation (LDAP/AD + SCIM)](/study/keycloak/14-user-federation) — 기업 내부 사용자 소스 연동
15. [Identity Brokering](/study/keycloak/15-identity-brokering) — Google/GitHub/Kakao 외부 IdP 연결

### 커스터마이징 (SPI)
16. [SPI로 Keycloak 확장](/study/keycloak/16-spi-overview) — providers/ 디렉토리, Quarkus 클래스로더
17. [커스텀 Authenticator](/study/keycloak/17-custom-authenticator) — 사내 사번 검증 같은 추가 단계
18. [커스텀 User Storage](/study/keycloak/18-custom-user-storage) — 레거시 DB를 사용자 소스로
19. [Theme 커스터마이징](/study/keycloak/19-theme) — 로그인 화면 브랜딩

### 운영과 확장
20. [Infinispan HA 클러스터링](/study/keycloak/20-ha-clustering) — 분산 캐시, Multi-site
21. [Kubernetes + Operator 배포](/study/keycloak/21-k8s-operator) — Keycloak Operator, Custom Resource
22. [데이터베이스와 성능](/study/keycloak/22-database-performance) — PostgreSQL 튜닝, 오프라인 세션
23. [Admin REST API와 자동화](/study/keycloak/23-admin-rest-api) — 운영 자동화, GitOps
24. [Backup/Restore와 Realm 이관](/study/keycloak/24-backup-restore) — Realm Import/Export, 재해 복구
25. [모니터링·감사와 업그레이드](/study/keycloak/25-monitoring-upgrade) — Event Listener, Metrics, 메이저 업그레이드

## 관련 자료

::: info 함께 보면 좋은 자료
- [OAuth 2.0 + OpenID Connect 스터디](/study/oauth/) — OAuth/OIDC 개념 선행
- [OAuth 스터디 CH17. Keycloak으로 AS 구축](/study/oauth/17-keycloak) — 소비자 관점 요약
- [Keycloak 개념 및 간단 사용 포스트](/posts/tech/2025-10-01-keycloak) — Docker Compose 실습 레퍼런스
:::
