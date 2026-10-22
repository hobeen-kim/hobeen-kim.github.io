<template>
  <div class="skills-section">
    <div class="header2">기술 스택</div>
    <div class="skills-container">
      <div class="skill-category">
        <div class="skill-category-title">디바이스 연동</div>
        <div class="skill-list"> AWS IoT Core(MQTT mTLS, Device Shadow, Jobs, Custom Authorizer), OTA, 디바이스 프로비저닝, WebRTC(Amazon KVS)</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">장비 통신</div>
        <div class="skill-list"> CAN/CAN FD, ISOBUS(ISO 11783 VT·TC)</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">시뮬레이션/SIL</div>
        <div class="skill-list"> QEMU 하드웨어 에뮬레이션, 센서·차량 동역학 시뮬레이션, 디지털 트윈</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">언어/프레임워크</div>
        <div class="skill-list"> Kotlin, Java, Rust, Python, Spring Boot, Spring Batch</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">DevOps/IaC</div>
        <div class="skill-list"> Terraform, ArgoCD, Helm, GitHub Actions, AWS SAM</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">클라우드/컨테이너</div>
        <div class="skill-list"> AWS(EKS, Lambda, SQS/SNS, Firehose, Aurora, DynamoDB, S3, KMS), Docker, Kubernetes</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">데이터/메시징</div>
        <div class="skill-list"> Kafka, Kafka Streams, Protobuf, PostgreSQL, Redis, MongoDB</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">관측성/보안</div>
        <div class="skill-list"> Grafana·Prometheus·Loki·Tempo, Datadog, Keycloak(OIDC), Prowler</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SkillsDevice"
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
