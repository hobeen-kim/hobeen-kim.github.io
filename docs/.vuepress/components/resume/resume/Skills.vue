<template>
  <div class="skills-section">
    <div class="header2">기술 스택</div>
    <div class="skills-container">
      <div class="skill-category">
        <div class="skill-category-title">언어/프레임워크</div>
        <div class="skill-list"> Java, Kotlin, Spring Boot, Spring Batch</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">메시징/스트리밍</div>
        <div class="skill-list"> Kafka, Kafka Streams, AWS SQS/SNS, AWS IoT(MQTT)</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">인증/보안</div>
        <div class="skill-list"> Keycloak(OIDC), Spring Security</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">데이터베이스</div>
        <div class="skill-list"> Postgres, Redis, MongoDB</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">테스트</div>
        <div class="skill-list"> JUnit, Testcontainers, Kover</div>
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
