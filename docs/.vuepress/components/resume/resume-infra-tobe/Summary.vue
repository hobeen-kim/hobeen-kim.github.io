<template>
  <div class="summary-section">
    <div class="header2">자기 소개</div>
    <div class="summary">
      <p>백엔드 개발로 시작해 2025년부터 인프라로 전향했습니다. 농기계 자율주행·ISOBUS 기반 OS 플랫폼 스타트업에서
        AWS·EKS 환경을 운영하며, Terraform IaC와 ArgoCD GitOps로 컨테이너 플랫폼을 구성·배포합니다.
        AWS Solutions Architect Professional, DevOps Engineer Professional 자격을 보유하고 있습니다.</p>
      <p>Terraform 으로 인프라를 모듈화하고 GitHub Actions OIDC 기반 CI 로 plan/apply 를 자동화해 변경 리드타임을 줄였습니다.
        ArgoCD App-of-Apps 와 Argo Rollouts 로 무중단·카나리 배포를 운영하고, 레거시 ECS 워크로드를 EKS 로 무중단 마이그레이션했습니다.
        Grafana·Prometheus·Loki·Tempo·Pyroscope 로 메트릭·로그·트레이스·프로파일을 통합하고, SLO 를 정의해 오탐 알림을 정리했습니다.</p>
      <p>보안을 인프라 설계의 기본 축으로 다룹니다. Prowler 기반 ISMS-P 점검을 자동화해 Critical·High 취약점을 조치하고,
        평문 시크릿을 External Secrets Operator 로 이관했으며, 위치정보사업자 인증 2건의 보안 요건을 설계·이행했습니다.
        Karpenter·Graviton·Spot 확대와 네트워크 경로 최적화로 AWS 비용을 절감하고, Infracost·Cost Anomaly Detection 으로 지속 모니터링합니다.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "Summary"
}
</script>

<style scoped>
.summary {
  background-color: var(--vp-c-bg-soft);
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid var(--vp-c-brand);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);

  p {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
  }
}

</style>
