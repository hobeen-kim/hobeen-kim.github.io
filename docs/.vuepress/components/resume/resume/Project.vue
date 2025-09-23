<template>
  <div class="project-section">
    <div class="header2">프로젝트 경험</div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">아그모</div>
        <span class="company-description">농기계 자율주행 시스템 및 ISOBUS 기반 마켓플레이스 서비스</span>
        <div class="position-period">
          <span class="position">백엔드 엔지니어</span><span class="period"> / 2025.02 ~ 현재</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">마켓플레이스 개발</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • ISOBUS 기반 장비에 대한 앱을 제공하는 마켓플레이스 서비스</span></div>
            <div class="responsibility-detail"> • 마켓 플레이스 기본 백엔드 API 기능 개발 (앱 설치, 다운로드, 검색, 디바이스/회원 관리) </div>
            <div class="responsibility-detail"> • Grafana, Prometheus, Loki, Pyroscope 를 활용한 모니터링 시스템 구축</div>
            <div class="responsibility-detail"> • AWS IoT 를 활용하여 디바이스와 MQTT 통신 시스템 개발</div>
            <div class="responsibility-skills"><span><strong>사용기술</strong>: Kotlin/Spring, EKS, ArgoCD, AWS IoT, Postgres, Grafana, Prometheus</span></div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">자율주행 모니터링 앱</div>
            <div class="period">2025.02 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 자율주행에서 생성되는 로그를 수집하고 분석하는 파이프라인 및 모니터링 앱 개발</span></div>
            <div class="responsibility-detail"> • 실시간 로그 ETL 파이프라인 개발</div>
            <div class="responsibility-detail"> • Kafka Streams 기반 실시간 로그 집계 및 통계 분석</div>
            <div class="responsibility-detail"> • 하나의 배치 서버를 모듈 기반으로 구축</div>
            <div class="responsibility-skills"><span><strong>사용기술</strong>: Java/Spring, AWS ECS, Kafka, MongoDB</span></div>
          </div>
        </div>
      </div>
    </div>
    <div class="project-item">
      <div class="project-header">
        <div class="company-name">테크랩스</div>
        <span class="company-description">고객 활동 이력을 바탕으로 한 초개인화 추천 서비스</span>
        <div class="position-period">
          <span class="position">AI 사업부 백엔드 엔지니어</span><span class="period"> / 2023.11 ~ 2025.02</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">Interest detection</div>
            <div class="period">2024.04 ~ 2025.02</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 사용자가 선택한 상품을 통해 GPT 로 관심사 키워드를 추출하고 상품을 추천하는 서비스</span></div>
            <div class="responsibility-detail"> • 상품/리뷰 데이터로 추천문구를 추출하는 LLM 기반 ETL 파이프라인 개발</div>
            <div class="responsibility-detail"> • 추천문구와 추천결과를 조합하는 Spring 서버와 langchain 을 활용하는 fast api 서버 개발</div>
            <div class="responsibility-detail"> • 수 초 이상 걸리는 gpt 요청으로 인한 지연을 비동기로 구조를 변경하여 200ms ~ 300ms 로 개선</div>
            <div class="responsibility-detail"> • EKS 와 Lambda, SNS 를 활용한 서버리스 이벤트 기반 아키텍처로 일 100만 건의 상품과 1만 건의 리뷰에서 키워드 및 추천문구 출력 처리</div>
            <div class="responsibility-skills"><span><strong>사용기술</strong>: Kotlin/Spring, Python, AWS EKS, MongoDB, ChatGPT</span></div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">추천 시스템 관리</div>
            <div class="period">주요 업무</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"><span> • 하루 8000만 건 로그, API 호출 4000만 회의 Spring 기반 추천 API 및 배치 시스템 관리</span></div>
            <div class="responsibility-detail"> • 데이터독 PoC 및 도입 및 고도화로 실시간 모니터링 시스템 구축</div>
            <div class="responsibility-detail"> • 자사 6개 모든 서비스에 대한 기능/부하 테스트 진행 및 비용감소 프로젝트로 AWS 비용 월 56% 감축</div>
            <div class="responsibility-skills"><span><strong>사용기술</strong>: Java/Spring, Kotlin, Postgres(AWS Aurora), Kinesis, Datadog, S3</span></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Experience"
}
</script>

<style scoped>

.project-section {
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}
.project-item {
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.project-header {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.company-name {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: var(--vp-c-text-1);
}

.company-description {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  border-bottom: 1px solid var(--vp-c-border);
}

.position-period {
  margin-top: 0.25rem;
}

.period {
  margin-top: 0.25rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}

.position {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.responsibilities {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.responsibility-item {
  margin-bottom: 1rem;
  display: flex;
}

.responsibility-header {
  font-weight: 700;
  margin-right: 0.5rem;
  min-width: 130px;
  color: var(--vp-c-text-1);
}

.responsibility-title {
  font-size: 1rem;
  font-weight: 700;
  max-width: 130px;
  color: var(--vp-c-text-1);
}

.responsibility-description {
}

.responsibility-detail-main {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  font-weight: 600;
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-detail-main span {
  border-bottom: 1px solid var(--vp-c-border);
}

.responsibility-detail {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.responsibility-skills {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;

}

.responsibility-skills span {
  background-color: #dadada;
  padding: 0.1rem 0.25rem;
  border-radius: 4px;
}


</style>
