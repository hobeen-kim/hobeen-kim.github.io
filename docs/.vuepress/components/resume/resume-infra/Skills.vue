<template>
  <div class="skills-section">
    <div class="header2">기술 스택</div>
    <div class="skills-container">
      <div class="skill-description">*실무에서 사용한 기술입니다.</div>
      <div class="skill-category">
        <div class="skill-category-title">IaC / GitOps</div>
        <div class="skill-list"> Terraform, ArgoCD, Helm</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">컨테이너 / 오케스트레이션</div>
        <div class="skill-list"> Kubernetes(EKS), Docker</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">클라우드 (AWS)</div>
        <div class="skill-list"> EKS, IoT Core, SQS/SNS, Lambda, S3/CloudFront/Route53, Aurora, ECR, SSM, KMS</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">관측성</div>
        <div class="skill-list"> Grafana, Prometheus, Loki, Tempo, Pyroscope, Datadog</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">인증/보안</div>
        <div class="skill-list"> Keycloak, IAM Identity Center, KMS</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">CI/CD</div>
        <div class="skill-list"> GitHub Actions, AWS SAM</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Skills"
}
</script>

<style scoped>
.skills-container {
  padding: 1rem 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}

.skill-description {
  font-size: 0.8rem;
  margin-bottom: 0.7rem;
  color: var(--vp-c-text-2, #8e8e8e);
  font-style: italic;
}

.skill-category {
  display: flex;
}

.skill-category-title {
  margin-top: 0.3rem;
  margin-bottom: 0.3rem;
  font-size: 1rem;
  font-weight: 700;
  min-width: 130px;
}

.skill-list {
  font-size: 0.9rem;
  margin-top: 0.3rem;
  margin-left: 1rem;
  margin-bottom: 0.3rem;
}
</style>
