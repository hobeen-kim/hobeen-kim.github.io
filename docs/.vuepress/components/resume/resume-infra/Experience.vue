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
            <div class="experience-description"> • <span>EKS 클러스터 운영</span> : Terraform IaC + ArgoCD GitOps 기반 dev/prod 클러스터 구성·배포 및 무중단 운영 </div>
            <div class="experience-description"> • <span>관측성 / 보안</span> : Grafana·Prometheus·Loki·Tempo·Pyroscope 관측성 구축, IAM·KMS·보안 점검 수행 </div>
            <div class="experience-description"> • <span>AWS IoT / 이벤트 인프라</span> : IoT Core·SNS/SQS 메시징 인프라 및 Keycloak 인증 인프라 구축 </div>
            <div class="experience-description"> • <span>NISHIBE</span> : 일본 택시 운행관리 서비스 클라우드 인프라 신규 설계·구축 (EKS+Aurora+Redis+ArgoCD, Terraform CI) </div>
            <div class="experience-skills">
              <div class="tech-stack">
                <span class="tag">AWS</span>
                <span class="tag">EKS</span>
                <span class="tag">Terraform</span>
                <span class="tag">ArgoCD</span>
                <span class="tag">Grafana</span>
                <span class="tag">Prometheus</span>
                <span class="tag">Loki</span>
                <span class="tag">AWS IoT</span>
                <span class="tag">Keycloak</span>
                <span class="tag">KMS</span>
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
            <div class="experience-description"> • <span>비용 최적화</span> : 자사 6개 서비스 부하/기능 테스트 후 리소스 재조정으로 AWS 비용 월 56% 절감 </div>
            <div class="experience-description"> • <span>모니터링 구축</span> : Datadog PoC 및 도입·고도화로 일 8000만 건 로그 서비스의 실시간 모니터링 체계 구축 </div>
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