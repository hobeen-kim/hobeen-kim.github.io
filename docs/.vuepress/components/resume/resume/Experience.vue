<template>
  <div class="experience-section">
    <div class="header2">경력 사항</div>
    <div class="experience-list">
      <div class="experience-item">
        <div class="experience-header">
          <div class="experience-name">아그모</div>
          <div class="position">TD팀 백엔드 엔지니어</div>
          <div class="period">25.02 ~ 현재 / 1년</div>
        </div>
        <div>
          <span class="company-description"> 농기계 자율주행 시스템 및 ISOBUS 기반 OS 플랫폼 스타트업</span>
          <div class="experience-descriptions">
            <div class="experience-description"> • <span>SEAMOS</span> : 농기계/건설기계 OS 의 플랫폼 서비스. 앱 업로드 및 다운로드, 결제 API 개발</div>
            <div class="experience-description"> • <span>AGMO Monitoring</span> : 농기계 자율주행에서 생성되는 로그를 수집하고 분석하는 파이프라인 구축 및 모니터링 API 개발 </div>
            <div class="experience-skills"> • <span>사용 기술</span> : Java, Kotlin, Spring Boot, Kafka, PostgreSQL, MongoDB, Redis, AWS, Kubernetes, Grafana, Prometheus, Loki, ArgoCD, Terraform </div>
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
            <div class="experience-description"> • <span>Interest detection</span> : 사용자가 선택한 상품을 통해 GPT 로 관심사 키워드를 추출하고 상품을 추천하는 LLM 서비스 개발 </div>
            <div class="experience-description"> • 하루 8000만 건의 쇼핑몰 사용자 로그를 수집하고 분석하는 ETL 파이프라인 관리 </div>
            <div class="experience-skills"> • <span>사용 기술</span> : Java, Kotlin, Spring Boot, AWS, AWS Kinesis, PostgreSQL, Kubernetes, Datadog </div>
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
  margin-bottom: 0.3rem;
  line-height: 1.5;
  padding-left: 1rem;
  text-indent: -1rem;

}

.experience-skills span {
  font-weight: 600;
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