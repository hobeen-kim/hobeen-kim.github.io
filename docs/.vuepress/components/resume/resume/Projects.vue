<template>
  <div class="projects-section">
    <h2>프로젝트 경험</h2>
    <div class="project-item">
      <div class="project-header">
        <h3>Interest-Detection 프로젝트</h3>
        <span class="period">2024.05 ~ 2024.12</span>
      </div>
      <div class="project-details">
        <div class="team-size">팀 규모: 5명 (백엔드 2, 프론트엔드 2, 데이터 분석가 1)</div>
        <div class="tech-stack">
          <h4>사용 기술:</h4>
          <div class="tech-tags">
            <span class="tech-tag">Java</span>
            <span class="tech-tag">Spring Boot</span>
            <span class="tech-tag">Kafka</span>
            <span class="tech-tag">PostgreSQL</span>
            <span class="tech-tag">AWS</span>
          </div>
        </div>
        <div class="contribution">
          <h4>기여도와 역할:</h4>
          <ul>
            <li>기획부터 서비스 단계까지 전 과정 참여</li>
            <li>사용자 행동 데이터 수집 및 분석 시스템 설계</li>
            <li>실시간 추천 API 개발 및 최적화</li>
          </ul>
        </div>
        <div class="results">
          <h4>성과:</h4>
          <ul>
            <li>API 응답 시간 30% 개선</li>
            <li>월간 10만 사용자 서비스 안정적 운영</li>
            <li>사용자 관심사 탐지 정확도 85% 달성</li>
          </ul>
        </div>
      </div>
    </div>
    
    <div class="project-item">
      <div class="project-header">
        <h3>로그 관리 시스템 구축</h3>
        <span class="period">2023.12 ~ 2024.03</span>
      </div>
      <div class="project-details">
        <div class="team-size">팀 규모: 3명 (백엔드 개발자)</div>
        <div class="tech-stack">
          <h4>사용 기술:</h4>
          <div class="tech-tags">
            <span class="tech-tag">Kotlin</span>
            <span class="tech-tag">Spring Boot</span>
            <span class="tech-tag">MongoDB</span>
            <span class="tech-tag">Kubernetes</span>
            <span class="tech-tag">Datadog</span>
          </div>
        </div>
        <div class="contribution">
          <h4>기여도와 역할:</h4>
          <ul>
            <li>대규모 로그 수집 및 저장 시스템 설계</li>
            <li>Kubernetes 기반 마이크로서비스 아키텍처 구축</li>
            <li>Datadog을 활용한 모니터링 시스템 구현</li>
          </ul>
        </div>
        <div class="results">
          <h4>성과:</h4>
          <ul>
            <li>로그 처리 속도 45% 향상</li>
            <li>CI/CD 구축으로 배포 시간 40% 단축</li>
            <li>실시간 모니터링으로 장애 대응 시간 60% 단축</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Projects"
}
</script>

<style scoped>
.project-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.period {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
}

.team-size {
  margin-bottom: 0.5rem;
  font-size: 0.95rem;
}
</style>
