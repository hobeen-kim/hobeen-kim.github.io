<template>
  <div class="project-section">
    <div class="header2">프로젝트 경험</div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">아그모</div>
        <div class="position-period">
          <span class="position">백엔드 엔지니어</span><span class="period"> / 2025.02 ~ 현재</span>
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
            <div class="responsibility-title">Terraform IaC &amp; 보안</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 인프라를 Terraform 으로 코드화하고 보안을 설계 기본 축으로 관리</span></div>
            <div class="responsibility-detail"> • Terraform 모듈화 + global/security 모듈(SSM 세션 로깅) 구성, dev/prod 환경 분리 관리</div>
            <div class="responsibility-detail"> • 자율주행 모니터링 인프라(ECS/MSK/task-definition) Terraform 모듈로 코드화 및 의존성 관리</div>
            <div class="responsibility-detail"> • IAM Identity Center 로 Role 기반 접근 점진 전환, Aurora 접근 로깅 + DB 유저 분리(RBAC) 적용</div>
            <div class="responsibility-detail"> • KMS 기반 위치정보 암호화 인프라 구축, 네트워크/IAM/Secrets/EKS/TLS 보안 점검 수행</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">Terraform</span>
                <span class="tag">IAM Identity Center</span>
                <span class="tag">KMS</span>
                <span class="tag">Aurora</span>
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
            <div class="responsibility-title">인증·인가 체계 (Keycloak RBAC)</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • Keycloak 기반 RBAC 인증·인가 체계를 전사 표준으로 설계·구축</span></div>
            <div class="responsibility-detail"> • Realm·Client/Realm Role·Group 권한 상속 모델 설계로 서비스 전반 RBAC 표준화</div>
            <div class="responsibility-detail"> • 다수 서비스에 OIDC/OAuth2 SSO 연동 및 토큰 기반 인가(Client·Service 계정) 적용</div>
            <div class="responsibility-detail"> • Keycloak 인증 서버 인프라 dev → prod 구축 (Aurora 백엔드·환경 분리 운영)</div>
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
            <div class="responsibility-detail"> • Grafana·Prometheus·Loki·Tempo·Pyroscope 로 메트릭/로그/트레이스/프로파일 통합 관측성 구축</div>
            <div class="responsibility-detail"> • AI 에이전트 기반 알림 분석·온콜 보조 — Grafana Alertmanager·에러 알림을 Slack 으로 수집하고, AI 에이전트가 Grafana 로그·메트릭을 분석해 원인 진단·조치 제안 후 관련자에게 메일 자동 발송</div>
            <div class="responsibility-detail"> • 자율주행 서비스(log-server·stream·batch·monitor) GitHub Actions CI/CD 및 aws-serverless Lambda SAM 배포 파이프라인 구축</div>
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
            <div class="responsibility-title">비용 최적화 &amp; 모니터링</div>
            <div class="period">주요 업무</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 하루 8000만 건 로그, API 호출 4000만 회 규모 서비스의 인프라 비용·안정성 관리</span></div>
            <div class="responsibility-detail"> • 자사 6개 모든 서비스 기능/부하 테스트 진행 및 리소스 재조정으로 AWS 비용 월 56% 절감</div>
            <div class="responsibility-detail"> • Datadog PoC 및 도입·고도화로 실시간 모니터링·알림 체계 구축</div>
            <div class="responsibility-detail"> • EKS·Lambda·SNS 기반 서버리스 이벤트 아키텍처 운영 및 DB read replica·파티셔닝으로 조회 성능 개선</div>
            <div class="responsibility-skills">
              <div class="tech-stack">
                <span class="tag">AWS EKS</span>
                <span class="tag">Datadog</span>
                <span class="tag">Kinesis</span>
                <span class="tag">Lambda</span>
                <span class="tag">Postgres(Aurora)</span>
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
