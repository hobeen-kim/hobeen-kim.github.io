<template>
  <div class="experience-section">
    <div class="header2">경력 사항</div>
    <div class="experience-list">
      <div class="experience-item">
        <div class="experience-header">
          <div class="experience-name">아그모</div>
          <div class="position">TD팀 인프라/DevOps 엔지니어</div>
          <div class="period">25.02 ~ 현재 / 1년</div>
        </div>
        <div>
          <span class="company-description"> 농기계 자율주행 시스템 및 ISOBUS 기반 OS 플랫폼 스타트업</span>
          <div class="experience-descriptions">
            <div class="experience-description"> • dev/prod EKS 클러스터 구성·운영 및 GitOps 배포 파이프라인 구축 (Terraform, ArgoCD, Argo Rollouts, GitHub OIDC CI), 레거시 ECS → EKS 무중단 마이그레이션 </div>
            <div class="experience-description"> • 클라우드 보안 점검 자동화 및 취약점 조치 (Prowler 기반 ISMS-P, 시크릿 External Secrets Operator 이관, IAM 최소권한 설계), 위치정보사업자 인증 대응 </div>
            <div class="experience-description"> • 프로덕션 EKS 크립토재킹 침해 사후분석 및 재발방지 (GuardDuty→Slack 자동 알림, 컨테이너 non-root, egress NetworkPolicy, ECR 스캐닝) </div>
            <div class="experience-description"> • 컴퓨팅 비용 최적화 및 관측성 스택 구축 (Karpenter·Graviton·Spot, Grafana·Prometheus·Loki·Tempo·Pyroscope), SLO 정의 및 AI 온콜 보조 운영 </div>
            <div class="experience-description"> • IoT 메시징 인프라 및 OTA 업데이트 파이프라인 구축 (AWS IoT Core·SNS/SQS, IoT Jobs 기반 BSP·데비안 패키지·보안 패치 배포) </div>
            <div class="experience-description"> • Keycloak 공통 인증 인프라(HA) 및 멀티리전 Active-Standby 페일오버 구성, 온프렘 GPU 추론 서버 구축 </div>
            <div class="experience-description"> • 일본 택시 운행관리 서비스(NISHIBE) 클라우드 인프라 신규 설계·구축 (EKS+Aurora+Redis+ArgoCD, Terraform CI) </div>
            <div class="experience-skills">
              <div class="tech-stack">
                <span class="tag">AWS</span>
                <span class="tag">EKS</span>
                <span class="tag">Terraform</span>
                <span class="tag">ArgoCD</span>
                <span class="tag">Karpenter</span>
                <span class="tag">Grafana</span>
                <span class="tag">Prometheus</span>
                <span class="tag">Prowler</span>
                <span class="tag">Keycloak</span>
                <span class="tag">vLLM</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="experience-item">
        <div class="experience-header">
          <div class="experience-name">테크랩스</div>
          <div class="position">AI 사업부 백엔드 엔지니어</div>
          <div class="period">23.11 ~ 25.02 / 1년 4개월</div>
        </div>
        <div>
          <span class="company-description"> 고객 활동 이력을 바탕으로 한 초개인화 추천 서비스 스타트업</span>
          <div class="experience-descriptions">
            <div class="experience-description"> • 인프라 비용 최적화 (6개 서비스 부하/기능 테스트 및 리소스 재조정, CloudFront 캐시 정책 적용) </div>
            <div class="experience-description"> • 대규모 로그 서비스 실시간 모니터링 체계 구축 (Datadog 도입·고도화) </div>
            <div class="experience-skills">
              <div class="tech-stack">
                <span class="tag">AWS</span>
                <span class="tag">EKS</span>
                <span class="tag">AWS Kinesis</span>
                <span class="tag">Datadog</span>
                <span class="tag">Postgres</span>
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
  name: "Experience.vue"
}
</script>

<style scoped>

.experience-section {
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}

.experience-list {
  padding: 1rem;
}

.experience-item {
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
  display: flex;
  margin-bottom: 1.2rem;
  margin-top: 0.5rem;
}

.experience-header {
  font-size: 1.1rem;
  font-weight: 700;
  min-width: 150px;
  color: var(--vp-c-text-1);
}

.period {
  margin-top: 0.2rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}

.position {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 0.2rem;
  margin-bottom: 0.2rem;
  font-weight: 500;
}

.experience-description {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.3rem;
  line-height: 1.5;
  padding-left: 1rem;
  text-indent: -1rem;
}

.experience-description span {
  font-weight: 600;
}

.experience-skills {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}

.experience-descriptions {
  margin-top: 0.5rem;
}

.company-description {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 600;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-border);
}

</style>