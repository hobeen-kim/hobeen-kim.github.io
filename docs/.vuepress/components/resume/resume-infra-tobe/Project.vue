<template>
  <div class="project-section">
    <div class="header2">프로젝트 경험</div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">아그모</div>
        <div class="position-period">
          <span class="position">TD팀 인프라/DevOps 엔지니어</span><span class="period"> / 2025.02 ~ 현재</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">EKS 클러스터 운영 &amp; GitOps</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • EKS 기반 컨테이너 플랫폼 구성 및 ArgoCD GitOps 배포 운영</span></div>
            <div class="responsibility-detail"> • EKS 파드 리소스 할당·HPA 오토스케일링 정책 수립, 무중단 rolling update 적용</div>
            <div class="responsibility-detail"> • ArgoCD 기반 GitOps 배포 체계 구축 및 dev → prod 환경 배포 파이프라인 운영</div>
            <div class="responsibility-detail"> • EKS 컨트롤 플레인 로그 장기 보관 파이프라인 구성</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">EKS</span>
                <span class="tag">ArgoCD</span>
                <span class="tag">Helm</span>
                <span class="tag">Terraform</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">Terraform IaC</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 인프라를 Terraform 으로 코드화하고 dev/prod 환경을 분리 관리</span></div>
            <div class="responsibility-detail"> • Terraform 모듈화 + global/security 모듈(SSM 세션 로깅) 구성</div>
            <div class="responsibility-detail"> • 자율주행 모니터링 인프라(ECS/MSK/task-definition) Terraform 모듈로 코드화 및 의존성 관리</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Terraform</span>
                <span class="tag">SSM</span>
                <span class="tag">KMS</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">클라우드 보안 진단 &amp; 취약점 조치</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • Prowler + ISMS-P 기준 클라우드 보안 취약점을 정기 진단하고 Critical/High 항목 조치</span></div>
            <div class="responsibility-detail"> • Airflow + Prowler 로 ISMS-P 보안 점검 매주 자동 시행, AI 에이전트로 결과 분석·조치 우선순위 도출</div>
            <div class="responsibility-detail"> • 시크릿 외부화 — Lambda/ECS env 평문 시크릿 → Secrets Manager + External Secrets Operator 이관, gitleaks CI 게이트</div>
            <div class="responsibility-detail"> • IAM 최소권한 재설계, 서비스 역할 혼동 대리(confused deputy) 방지 조건 적용, 루트 MFA 강제</div>
            <div class="responsibility-detail"> • S3 퍼블릭 접근 차단, IMDSv2 강제, 보안그룹 정비 등 인프라 보호 조치, 네트워크/EKS/TLS 보안 점검</div>
            <div class="responsibility-detail"> • Prowler 정기 스캔 CI/스케줄 자동화 + suppression 근거 문서화</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Prowler</span>
                <span class="tag">ISMS-P</span>
                <span class="tag">External Secrets Operator</span>
                <span class="tag">IAM</span>
                <span class="tag">gitleaks</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">보안 침해 사후분석 &amp; 재발방지</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 프로덕션 EKS 크립토재킹(XMRig) 침해를 사후분석하고 근본 결함을 코드로 차단</span></div>
            <div class="responsibility-detail"> • 침투 경로 분석 — 취약 버전(Next.js CVE) 프레임워크 RCE → root 컨테이너 셸 spawn → 마이너 다운로드·실행, 앱 코드 전수 감사·노드 포렌식으로 진입점 특정 및 활성 위협 제거 확인</div>
            <div class="responsibility-detail"> • 탐지-알림 단절 해소 — GuardDuty(고위험) → EventBridge → SNS → Lambda → Slack/Google Chat 자동 알림 파이프라인 구축</div>
            <div class="responsibility-detail"> • 컨테이너 non-root 전환(runAsNonRoot·privilege escalation 차단·read-only rootfs), egress NetworkPolicy로 마이너 풀 차단</div>
            <div class="responsibility-detail"> • ECR enhanced scanning·의존성 정기 업데이트(SCA 게이트), ALB/WAF 액세스 로깅 활성화로 사후 추적성 확보</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">GuardDuty</span>
                <span class="tag">EventBridge</span>
                <span class="tag">securityContext</span>
                <span class="tag">NetworkPolicy</span>
                <span class="tag">ECR Scanning</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">위치정보사업자 인증 (보안 컴플라이언스)</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 위치정보사업자 인증 평가를 주도해 인증 2건 획득, 관련 인프라 보안 요건 설계·이행</span></div>
            <div class="responsibility-detail"> • KMS 기반 위치정보 저장·전송 구간 암호화 인프라 구축</div>
            <div class="responsibility-detail"> • IAM·RBAC 최소권한·DB 유저 분리 및 위치정보 접근 로그 법정 기간 보관·감사 추적 구성</div>
            <div class="responsibility-detail"> • 망 분리·보안그룹·TLS·Secrets 관리 등 인프라 보안 점검·개선</div>
            <div class="responsibility-detail"> • 기술적·관리적 보호조치 명세·증빙 자료 준비 및 인증 평가 대응</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">KMS</span>
                <span class="tag">IAM/RBAC</span>
                <span class="tag">위치정보보호</span>
                <span class="tag">보안감사</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">AWS IoT &amp; 이벤트 인프라</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 디바이스 통신과 서비스 간 이벤트 메시징 인프라 설계·구축</span></div>
            <div class="responsibility-detail"> • AWS IoT Core 토픽/정책/인증서 설계, 디바이스 Shadow 상태 SQS/IoT Rule 적재 구성</div>
            <div class="responsibility-detail"> • feature_status_notification SNS → SQS fanout 파이프라인 구축</div>
            <div class="responsibility-detail"> • MQTT 중복 접속(DUPLICATE_CLIENTID) 대응</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">AWS IoT</span>
                <span class="tag">SQS</span>
                <span class="tag">SNS</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">OTA 업데이트 파이프라인</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • IoT 디바이스의 BSP·데비안 패키지·보안 패치를 무선(OTA)으로 배포하는 파이프라인 설계·구축</span></div>
            <div class="responsibility-detail"> • AWS IoT Core Jobs 기반으로 Job document를 통해 디바이스 SDM 에이전트에 업데이트 지시·결과 회수</div>
            <div class="responsibility-detail"> • 아티팩트 3종(defined/ftp/execute) 지원, 캠페인·BSP/Core 버전 범위 타겟팅으로 보안 패치 누락 방지</div>
            <div class="responsibility-detail"> • S3 presigned URL로 펌웨어 전송(만료 5분→60분), Job Report SQS 수신·Redis 진행 추적·재시도 처리</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">AWS IoT Core Jobs</span>
                <span class="tag">S3</span>
                <span class="tag">SQS</span>
                <span class="tag">Redis</span>
                <span class="tag">Debian/BSP</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">인증·인가 체계 (Keycloak RBAC)</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • Keycloak 기반 RBAC 로 여러 서비스가 함께 쓰는 공통 인증·인가 기반 설계·구축</span></div>
            <div class="responsibility-detail"> • Realm·Client/Realm Role·Group 권한 상속 모델 설계로 서비스 전반 RBAC 표준화</div>
            <div class="responsibility-detail"> • 다수 서비스에 OIDC/OAuth2 SSO 연동 및 토큰 기반 인가(Client·Service 계정) 적용</div>
            <div class="responsibility-detail"> • Keycloak 인증 서버 인프라 dev → prod 구축 (Aurora 백엔드·환경 분리 운영), 단일 인스턴스 → HA 클러스터링·백업 자동화로 SPOF 제거</div>
            <div class="responsibility-detail"> • Keycloak user events SNS → SQS fanout 파이프라인으로 계정 변경 이벤트 외부 시스템 동기화</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Keycloak</span>
                <span class="tag">OIDC</span>
                <span class="tag">RBAC</span>
                <span class="tag">SNS/SQS</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">관측성 &amp; CI/CD 자동화</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 관측성 스택 통합 및 AI 툴 기반 모니터링·배포 자동화</span></div>
            <div class="responsibility-detail"> • Grafana·Prometheus·Loki·Tempo·Pyroscope 로 메트릭/로그/트레이스/프로파일 통합 관측성 구축, RED(Rate·Errors·Duration) 기반 골든 시그널 대시보드 표준화</div>
            <div class="responsibility-detail"> • AI 에이전트 기반 알림 분석·온콜 보조 — Grafana Alertmanager·에러 알림을 Slack 으로 수집하고, AI 에이전트가 Grafana 로그·메트릭을 분석해 원인 진단·조치 제안 후 관련자에게 메일 자동 발송</div>
            <div class="responsibility-detail"> • 자율주행 서비스(log-server·stream·batch·monitor) GitHub Actions CI/CD 및 aws-serverless Lambda SAM 배포 파이프라인 구축</div>
            <div class="responsibility-detail"> • GitHub Actions·ArgoCD 이벤트로 DORA 4지표(리드타임·배포빈도·변경실패율·MTTR) 계측·대시보드화하여 배포 성과 가시화·개선 추적</div>
            <div class="responsibility-detail"> • Claude Code 기반 사내 AI 개발 워크플로우 구축 — 공용 에이전트·스킬·MCP 서버로 이슈 생성·문서화·배포 자동화</div>
            <div class="responsibility-detail"> • ADS 문서 사이트 S3/CloudFront/Route53 정적 호스팅, ECR lifecycle policy 환경별 분리</div>
            <div class="responsibility-skills">
                <div class="tech-stack">
                  <span class="tag">Grafana</span>
                  <span class="tag">GitHub Actions</span>
                  <span class="tag">AWS SAM</span>
                  <span class="tag">CloudFront</span>
                </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">NISHIBE 택시 인프라</div>
            <div class="period">2026.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 일본 택시 운행관리 서비스의 클라우드 인프라를 신규 설계·구축</span></div>
            <div class="responsibility-detail"> • EKS + Aurora + Redis + ArgoCD 풀스택 dev 환경 구성 및 서비스 배포</div>
            <div class="responsibility-detail"> • global 네트워크 레이어 + 환경 골격 Terraform 모듈화, GitHub OIDC 기반 CI 인증 구성</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">EKS</span>
                <span class="tag">Aurora</span>
                <span class="tag">Terraform</span>
                <span class="tag">ArgoCD</span>
                <span class="tag">GitHub OIDC</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">멀티리전 페일오버</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 단일 리전 운영의 리전 장애 위험을 비용 최소화 방식(Pilot Light)으로 대응</span></div>
            <div class="responsibility-detail"> • Aurora Global DB 로 서울(Primary) → 도쿄(Replica) 비동기 복제, 페일오버 시 Replica 승격</div>
            <div class="responsibility-detail"> • 도쿄에 최소 노드(Spot) EKS 상시 유지, 페일오버 시 Karpenter 즉시 확장</div>
            <div class="responsibility-detail"> • Route53 Health Check 로 서울 엔드포인트 실패 시 도쿄로 DNS 자동 전환 (RTO &lt;15분, Standby 유휴 비용 Active 대비 ~7%)</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Aurora Global DB</span>
                <span class="tag">Route53</span>
                <span class="tag">EKS</span>
                <span class="tag">Karpenter</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">온프렘 GPU AI 인프라</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • SeamOS 개발 보조 AI 의 사내 코드 외부 전송 문제를 온프렘 GPU 서버로 해소</span></div>
            <div class="responsibility-detail"> • 물리 GPU 서버(RTX 4090, VRAM 24GB)에 vLLM 을 Docker 로 배포, OpenAI 호환 API 노출</div>
            <div class="responsibility-detail"> • AWQ INT4 양자화로 VRAM 사용량 ~50% 절감(70B 단일 GPU 서빙), continuous batching·Flash Attention 2 로 throughput 최적화</div>
            <div class="responsibility-detail"> • Tailscale VPN·Nginx + Keycloak API 인증으로 사내망·VPN 경유만 허용, Grafana 로 GPU 모니터링</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">vLLM</span>
                <span class="tag">NVIDIA GPU</span>
                <span class="tag">Tailscale VPN</span>
                <span class="tag">Nginx</span>
                <span class="tag">Keycloak</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">테크랩스</div>
        <div class="position-period">
          <span class="position">AI 사업부 백엔드 엔지니어</span><span class="period"> / 2023.11 ~ 2025.02</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">추천 시스템 서버 관리</div>
            <div class="period">2023.11 ~ 2025.02</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 하루 8000만 건 로그·API 호출 4000만 회 규모 추천 API/배치 시스템의 인프라 비용·안정성 관리</span></div>
            <div class="responsibility-detail"> • 자사 6개 모든 서비스 기능/부하 테스트 진행 및 리소스 재조정으로 AWS 비용 월 56% 절감</div>
            <div class="responsibility-detail"> • AWS CloudFront 세분화 캐시 정책으로 추천 서버 리소스 40% 이상 효율화</div>
            <div class="responsibility-detail"> • Datadog PoC·도입·고도화로 실시간 모니터링·알림 체계 구축</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Java/Spring</span>
                <span class="tag">Kotlin</span>
                <span class="tag">Datadog</span>
                <span class="tag">CloudFront</span>
                <span class="tag">Kinesis</span>
                <span class="tag">Postgres(Aurora)</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">Interest detection — 이벤트 기반 아키텍처</div>
            <div class="period">2024.04 ~ 2024.11</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 상품/리뷰 데이터로 관심사 키워드·추천문구를 추출하는 서비스의 서버리스 아키텍처 설계</span></div>
            <div class="responsibility-detail"> • EKS·Lambda·SNS 기반 서버리스 이벤트 아키텍처로 일 100만 건 상품·1만 건 리뷰의 키워드/추천문구 처리</div>
            <div class="responsibility-detail"> • 상품/리뷰 데이터로 추천문구를 추출하는 LLM 기반 ETL 파이프라인 구성 (Spring + langchain FastAPI)</div>
            <div class="responsibility-detail"> • 수 초 이상 걸리던 GPT 요청 지연을 비동기 구조로 변경해 200~300ms 로 개선</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">AWS EKS</span>
                <span class="tag">Lambda</span>
                <span class="tag">SNS</span>
                <span class="tag">MongoDB</span>
                <span class="tag">ChatGPT</span>
              </div>
            </div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">vaunce 차세대 시스템 — Serverless ETL</div>
            <div class="period">2024.05 ~ 2024.09</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • vaunce 사 데이터 시각화 SI 프로젝트의 로그 수집·분석 파이프라인 구축</span></div>
            <div class="responsibility-detail"> • 바운스앱 raw 로그에 대한 Serverless ETL 파이프라인 구축 (Kinesis)</div>
            <div class="responsibility-detail"> • 데이터 분석 결과를 보여주는 통계 대시보드 백엔드 API 개발</div>
            <div class="responsibility-detail"> • 역정규화·파티셔닝으로 DB 조회 시간을 수 초 → 200ms 이하로 단축</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Kotlin/Spring</span>
                <span class="tag">Kinesis</span>
                <span class="tag">Postgres(Aurora)</span>
                <span class="tag">S3</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Experience"
}
</script>

<style scoped>

.project-section {
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}
.project-item {
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.project-header {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.company-name {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: var(--vp-c-text-1);
}

.position-period {
  margin-top: 0.25rem;
}

.period {
  margin-top: 0.25rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}

.position {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.responsibilities {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.responsibility-item {
  margin-bottom: 1rem;
  display: flex;
}

.responsibility-header {
  font-weight: 700;
  margin-right: 0.5rem;
  min-width: 140px;
  color: var(--vp-c-text-1);
}

.responsibility-title {
  font-size: 1rem;
  font-weight: 700;
  max-width: 130px;
  color: var(--vp-c-text-1);
}

.responsibility-description {
}

.responsibility-detail-main {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-detail-main span {
  border-bottom: 1px solid var(--vp-c-border);
}

.responsibility-detail {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-skills {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;

}

.responsibility-skills span {
}


</style>
