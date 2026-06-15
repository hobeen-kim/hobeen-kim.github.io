<template>
  <div class="summary-section">
    <div class="header2">자기 소개</div>
    <div class="summary">
      <p> AWS 기반 인프라/DevOps 엔지니어로 농기계 자율주행·ISOBUS OS 플랫폼 스타트업에서 EKS 클러스터 운영, Terraform IaC,
        ArgoCD GitOps, 관측성 스택 구축을 담당했습니다. AWS Solutions Architect Professional, DevOps Engineer Professional 자격을 보유하고 있습니다.</p>
      <p> Terraform 으로 인프라를 모듈화하고 dev/prod 환경을 코드로 분리 관리하며, ArgoCD 기반 GitOps 로 무중단 배포 파이프라인을 운영합니다.
        Grafana·Prometheus·Loki·Tempo·Pyroscope 로 메트릭·로그·트레이스·프로파일을 통합한 관측성 체계를 구축했습니다.</p>
      <p> IAM Identity Center 전환, Aurora 접근 로깅·RBAC, KMS 기반 위치정보 암호화, 네트워크/IAM/Secrets/EKS/TLS 보안 점검 등
        보안을 인프라 설계의 기본 축으로 다룹니다. 부하 테스트와 리소스 최적화로 AWS 비용을 월 56% 절감한 경험이 있습니다.</p>
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
