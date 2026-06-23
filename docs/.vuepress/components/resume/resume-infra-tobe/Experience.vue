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
            <div class="experience-description"> • <span>보안 자동화</span> : Prowler 기반 ISMS-P 클라우드 보안 점검 자동화·취약점 조치, 시크릿 ESO 이관, 위치정보사업자 인증 대응 </div>
            <div class="experience-description"> • <span>EKS·GitOps</span> : Terraform IaC 운영, GitHub OIDC 기반 Terraform CI 구축, ArgoCD·Argo Rollouts 배포, ECS→EKS 마이그레이션 </div>
            <div class="experience-description"> • <span>비용·관측성</span> : Karpenter·Graviton·Spot 기반 비용 최적화, LGTM 관측성 스택 구축·SLO 정의·AI 온콜 보조 </div>
            <div class="experience-description"> • <span>그 외</span> : Keycloak 공통 인증(HA) 운영, 멀티리전 페일오버 구성, 온프렘 GPU AI 인프라 구축, NISHIBE 택시 인프라 신규 구축 </div>
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
            <div class="experience-description"> • <span>비용 최적화</span> : 6개 서비스 부하/기능 테스트 및 리소스 재조정, CloudFront 캐시 정책 적용 </div>
            <div class="experience-description"> • <span>모니터링 구축</span> : Datadog 도입·고도화로 대규모 로그 서비스 실시간 모니터링 체계 구축 </div>
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