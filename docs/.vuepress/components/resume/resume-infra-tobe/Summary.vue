<template>
  <div class="summary-section">
    <div class="header2">자기 소개</div>
    <div class="summary">
      <p>농기계 자율주행·ISOBUS 기반 OS 플랫폼 스타트업에서 AWS·EKS 환경을 운영하는 인프라/DevOps 엔지니어입니다.
        Terraform IaC와 ArgoCD GitOps로 컨테이너 플랫폼을 구성·배포하며, AWS Solutions Architect·DevOps Engineer Professional 자격을 보유하고 있습니다.</p>
      <p>클라우드 보안과 비용 최적화를 중심으로 일합니다. Prowler 기반 ISMS-P 점검을 자동화해 취약점을 조치하고 위치정보사업자 인증에 대응했으며,
        Karpenter·Spot 확대와 네트워크 경로 최적화로 운영 비용을 꾸준히 낮춰 왔습니다.</p>
      <p>반복되는 운영 작업을 코드와 파이프라인으로 옮기는 일을 우선합니다. GitHub OIDC 기반 Terraform CI와 LGTM 관측성 스택·SLO 기반 모니터링을 구축해,
        변경은 안전하게 자동화하고 장애는 빠르게 감지하도록 인프라를 운영합니다.</p>
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
