<template>
  <div class="portfolio-container">
    <div class="portfolio-header">
      <h1>개발자 포트폴리오 (작성중)</h1>
      
      <!-- 1. 소개 -->
      <div class="intro-section">
        <h2>소개</h2>
        <div class="intro-content">
          <div class="profile-image">
            <div class="image-placeholder">
              <i class="fas fa-user-circle"></i>
            </div>
          </div>
          <div class="profile-text">
            <p>안녕하세요, 몰입을 즐기는 백엔드 개발자 김호빈입니다. 대규모 트래픽 서비스 운영 경험과 데이터 파이프라인 구축 경험을 가지고 있습니다.</p>
            <p>저는 <strong>테스트 코드 작성</strong>과 <strong>성능 최적화</strong>에 관심이 많으며, 항상 더 나은 방법을 찾기 위해 노력합니다. 새로운 기술을 배우고 적용하는 것을 좋아하며, 특히 Kubernetes, 부하 테스트, 모니터링 도구 등을 실무에 적용한 경험이 있습니다.</p>
            <p>개발자로서 저의 철학은 <strong>"사용자 경험을 위한 기술적 완성도 추구"</strong>입니다. 비즈니스 가치를 높이기 위해 팀원들과 적극적으로 소통하며, 애자일 프로세스에 익숙합니다.</p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 2. 주요 프로젝트 -->
    <div class="section">
      <h2>주요 프로젝트</h2>
      
      <!-- 프로젝트 1 -->
      <div class="project-card">
        <div class="project-header">
          <div class="project-title">
            <h3>Interest-Detection 프로젝트</h3>
            <div class="project-links">
              <a href="https://github.com/username/interest-detection" target="_blank" class="project-link">
                <i class="fab fa-github"></i> GitHub
              </a>
              <a href="https://example.com/demo" target="_blank" class="project-link">
                <i class="fas fa-external-link-alt"></i> 서비스 링크
              </a>
            </div>
          </div>
          <div class="project-meta">
            <span><i class="far fa-calendar-alt"></i> 2024.05 ~ 2024.12</span>
            <span><i class="fas fa-users"></i> 팀 규모: 5명</span>
          </div>
        </div>
        
        <div class="project-body">
          <div class="tech-stack">
            <h4>기술 스택</h4>
            <div class="tech-tags">
              <span class="tech-tag">Java</span>
              <span class="tech-tag">Spring Boot</span>
              <span class="tech-tag">Kafka</span>
              <span class="tech-tag">PostgreSQL</span>
              <span class="tech-tag">AWS</span>
              <span class="tech-tag">Docker</span>
            </div>
          </div>
          
          <div class="project-content">
            <div class="problem-section">
              <h4>문제 정의</h4>
              <p>사용자의 웹 활동 데이터를 기반으로 관심사를 자동으로 탐지하고, 이를 활용한 맞춤형 추천 서비스 제공이 필요했습니다. 기존 시스템은 수동 태깅에 의존하여 정확도가 낮고 확장성에 제한이 있었습니다.</p>
            </div>
            
            <div class="solution-section">
              <h4>해결 과정</h4>
              <ul>
                <li>사용자 행동 데이터 수집을 위한 로깅 시스템 설계 및 구현</li>
                <li>Kafka를 활용한 실시간 데이터 파이프라인 구축</li>
                <li>Spring Boot 기반 RESTful API 서버 개발</li>
                <li>관심사 탐지 알고리즘 구현 및 최적화</li>
                <li>부하 테스트를 통한 시스템 안정성 확보</li>
              </ul>
            </div>
            
            <div class="result-section">
              <h4>결과</h4>
              <ul>
                <li>API 응답 시간 30% 개선 (평균 200ms → 140ms)</li>
                <li>월간 10만 사용자 서비스 안정적 운영</li>
                <li>사용자 관심사 탐지 정확도 85% 달성</li>
                <li>추천 클릭률(CTR) 22% 향상</li>
              </ul>
            </div>
          </div>
          
          <div class="project-images">
            <div class="image-container">
              <div class="image-placeholder">
                <i class="fas fa-image"></i>
                <span>아키텍처 다이어그램</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 프로젝트 2 -->
      <div class="project-card">
        <div class="project-header">
          <div class="project-title">
            <h3>로그 관리 시스템 구축</h3>
            <div class="project-links">
              <a href="https://github.com/username/log-management" target="_blank" class="project-link">
                <i class="fab fa-github"></i> GitHub
              </a>
            </div>
          </div>
          <div class="project-meta">
            <span><i class="far fa-calendar-alt"></i> 2023.12 ~ 2024.03</span>
            <span><i class="fas fa-users"></i> 팀 규모: 3명</span>
          </div>
        </div>
        
        <div class="project-body">
          <div class="tech-stack">
            <h4>기술 스택</h4>
            <div class="tech-tags">
              <span class="tech-tag">Kotlin</span>
              <span class="tech-tag">Spring Boot</span>
              <span class="tech-tag">MongoDB</span>
              <span class="tech-tag">Kubernetes</span>
              <span class="tech-tag">Datadog</span>
            </div>
          </div>
          
          <div class="project-content">
            <div class="problem-section">
              <h4>문제 정의</h4>
              <p>대규모 로그 데이터 처리 및 분석이 필요했으나, 기존 시스템은 확장성 문제와 높은 운영 비용 문제가 있었습니다. 또한 로그 검색 및 분석에 많은 시간이 소요되어 신속한 문제 해결이 어려웠습니다.</p>
            </div>
            
            <div class="solution-section">
              <h4>해결 과정</h4>
              <ul>
                <li>Kubernetes 기반 마이크로서비스 아키텍처 설계</li>
                <li>MongoDB를 활용한 로그 저장 및 검색 시스템 구현</li>
                <li>Datadog을 활용한 모니터링 및 알림 시스템 구축</li>
                <li>로그 데이터 압축 및 샤딩 전략 적용</li>
                <li>CI/CD 파이프라인 구축으로 배포 자동화</li>
              </ul>
            </div>
            
            <div class="result-section">
              <h4>결과</h4>
              <ul>
                <li>로그 처리 속도 45% 향상</li>
                <li>메인서버 리소스 효율화로 비용 56% 절감</li>
                <li>CI/CD 구축으로 배포 시간 40% 단축</li>
                <li>실시간 모니터링으로 장애 대응 시간 60% 단축</li>
              </ul>
            </div>
          </div>
          
          <div class="project-images">
            <div class="image-container">
              <div class="image-placeholder">
                <i class="fas fa-image"></i>
                <span>시스템 구성도</span>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 프로젝트 3 -->
      <div class="project-card">
        <div class="project-header">
          <div class="project-title">
            <h3>자율주행 데이터 파이프라인</h3>
            <div class="project-links">
              <a href="https://github.com/username/autonomous-data" target="_blank" class="project-link">
                <i class="fab fa-github"></i> GitHub
              </a>
            </div>
          </div>
          <div class="project-meta">
            <span><i class="far fa-calendar-alt"></i> 2025.02 ~ 현재</span>
            <span><i class="fas fa-users"></i> 팀 규모: 4명</span>
          </div>
        </div>
        
        <div class="project-body">
          <div class="tech-stack">
            <h4>기술 스택</h4>
            <div class="tech-tags">
              <span class="tech-tag">Java</span>
              <span class="tech-tag">Spring Boot</span>
              <span class="tech-tag">Apache Spark</span>
              <span class="tech-tag">AWS</span>
              <span class="tech-tag">Kubernetes</span>
            </div>
          </div>
          
          <div class="project-content">
            <div class="problem-section">
              <h4>문제 정의</h4>
              <p>자율주행 차량에서 생성되는 대용량 센서 데이터를 실시간으로 처리하고 분석해야 하는 과제가 있었습니다. 데이터의 양이 방대하고 지연 시간에 민감한 처리가 필요했습니다.</p>
            </div>
            
            <div class="solution-section">
              <h4>해결 과정</h4>
              <ul>
                <li>실시간 데이터 수집 및 전처리 파이프라인 설계</li>
                <li>Apache Spark를 활용한 분산 처리 시스템 구축</li>
                <li>AWS 클라우드 인프라 최적화</li>
                <li>Kubernetes 기반 컨테이너 오케스트레이션 구현</li>
                <li>데이터 품질 모니터링 시스템 개발</li>
              </ul>
            </div>
            
            <div class="result-section">
              <h4>결과</h4>
              <ul>
                <li>데이터 처리 속도 25% 향상</li>
                <li>시스템 안정성 개선으로 다운타임 40% 감소</li>
                <li>데이터 처리 비용 30% 절감</li>
                <li>실시간 분석 지연 시간 50ms 이내로 유지</li>
              </ul>
            </div>
          </div>
          
          <div class="project-images">
            <div class="image-container">
              <div class="image-placeholder">
                <i class="fas fa-image"></i>
                <span>데이터 파이프라인 구조</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 3. 코드/레포지토리 링크 -->
    <div class="section">
      <h2>코드/레포지토리 링크</h2>
      <div class="repo-list">
        <div class="repo-card">
          <div class="repo-header">
            <h3>Interest-Detection</h3>
            <a href="https://github.com/username/interest-detection" target="_blank" class="repo-link">
              <i class="fab fa-github"></i>
            </a>
          </div>
          <p class="repo-description">사용자 행동 데이터 기반 관심사 탐지 및 추천 시스템</p>
          <div class="tech-tags">
            <span class="tech-tag">Java</span>
            <span class="tech-tag">Spring Boot</span>
            <span class="tech-tag">Kafka</span>
          </div>
        </div>
        
        <div class="repo-card">
          <div class="repo-header">
            <h3>Log-Management-System</h3>
            <a href="https://github.com/username/log-management" target="_blank" class="repo-link">
              <i class="fab fa-github"></i>
            </a>
          </div>
          <p class="repo-description">Kubernetes 기반 대규모 로그 관리 시스템</p>
          <div class="tech-tags">
            <span class="tech-tag">Kotlin</span>
            <span class="tech-tag">MongoDB</span>
            <span class="tech-tag">Kubernetes</span>
          </div>
        </div>
        
        <div class="repo-card">
          <div class="repo-header">
            <h3>Autonomous-Data-Pipeline</h3>
            <a href="https://github.com/username/autonomous-data" target="_blank" class="repo-link">
              <i class="fab fa-github"></i>
            </a>
          </div>
          <p class="repo-description">자율주행 차량 데이터 실시간 처리 파이프라인</p>
          <div class="tech-tags">
            <span class="tech-tag">Java</span>
            <span class="tech-tag">Apache Spark</span>
            <span class="tech-tag">AWS</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 4. 추가 활동 -->
    <div class="section">
      <h2>추가 활동</h2>
      
      <div class="activities-container">
        <div class="activity-category">
          <h3>기술 블로그</h3>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-header">
                <a href="https://hobeen-kim.github.io/posts/kubernetes-in-production" target="_blank" class="activity-title">
                  프로덕션 환경에서의 Kubernetes 운영 경험
                </a>
                <span class="activity-date">2024.07</span>
              </div>
              <p class="activity-description">실제 프로덕션 환경에서 Kubernetes를 도입하고 운영한 경험을 공유합니다.</p>
            </div>
            
            <div class="activity-item">
              <div class="activity-header">
                <a href="https://hobeen-kim.github.io/posts/performance-testing" target="_blank" class="activity-title">
                  k6를 활용한 효과적인 부하 테스트 전략
                </a>
                <span class="activity-date">2024.05</span>
              </div>
              <p class="activity-description">k6 테스트 도구를 활용하여 API 서버의 성능을 측정하고 개선한 방법을 설명합니다.</p>
            </div>
          </div>
        </div>
        
        <div class="activity-category">
          <h3>오픈소스 기여</h3>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-header">
                <a href="https://github.com/some-org/some-project/pull/123" target="_blank" class="activity-title">
                  Spring Data JPA 성능 개선 PR
                </a>
                <span class="activity-date">2024.03</span>
              </div>
              <p class="activity-description">대용량 데이터 처리 시 발생하는 메모리 누수 문제를 해결하는 패치를 제공했습니다.</p>
            </div>
          </div>
        </div>
        
        <div class="activity-category">
          <h3>세미나 발표</h3>
          <div class="activity-list">
            <div class="activity-item">
              <div class="activity-header">
                <span class="activity-title">대규모 로그 시스템 구축 경험 공유</span>
                <span class="activity-date">2024.04</span>
              </div>
              <p class="activity-description">사내 기술 세미나에서 로그 관리 시스템 구축 경험과 노하우를 공유했습니다.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PortfolioSection'
}
</script>

<style scoped>
.portfolio-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Noto Sans KR', sans-serif;
  color: var(--vp-c-text-1);
  background-color: var(--vp-c-bg);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.portfolio-header {
  margin-bottom: 2rem;
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--vp-c-brand);
  margin-bottom: 1.5rem;
  text-align: center;
}

h2 {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--vp-c-brand);
  margin: 1.5rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--vp-c-divider-light);
}

h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0.5rem 0;
}

h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
  margin: 0.5rem 0;
}

.intro-content {
  display: flex;
  gap: 2rem;
  align-items: center;
  margin-top: 1rem;
}

.profile-image {
  flex-shrink: 0;
}

.image-placeholder {
  width: 150px;
  height: 150px;
  background-color: var(--vp-c-bg-soft);
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--vp-c-text-2);
  font-size: 3rem;
}

.profile-text {
  flex-grow: 1;
}

.profile-text p {
  margin-bottom: 1rem;
  line-height: 1.6;
}

.section {
  margin-bottom: 3rem;
}

.project-card {
  margin-bottom: 2.5rem;
  padding: 1.5rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.project-header {
  margin-bottom: 1.5rem;
}

.project-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.project-links {
  display: flex;
  gap: 1rem;
}

.project-link {
  color: var(--vp-c-brand);
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.project-meta {
  display: flex;
  gap: 1.5rem;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.project-meta span {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.project-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.tech-stack {
  margin-bottom: 1rem;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tech-tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--vp-c-brand-dimm);
  color: var(--vp-c-brand);
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.project-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

.problem-section, .solution-section, .result-section {
  background-color: var(--vp-c-bg);
  padding: 1rem;
  border-radius: 4px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

ul {
  margin: 0.5rem 0 0.5rem 1.5rem;
  padding: 0;
}

li {
  margin-bottom: 0.5rem;
}

.project-images {
  margin-top: 1.5rem;
}

.image-container {
  display: flex;
  justify-content: center;
}

.image-container .image-placeholder {
  width: 100%;
  height: 200px;
  border-radius: 4px;
  background-color: var(--vp-c-bg);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--vp-c-text-2);
  font-size: 2rem;
  border: 1px dashed var(--vp-c-divider);
}

.image-container .image-placeholder span {
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

.repo-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.repo-card {
  padding: 1.25rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
}

.repo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.repo-link {
  color: var(--vp-c-brand);
  font-size: 1.25rem;
}

.repo-description {
  margin-bottom: 1rem;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  line-height: 1.5;
}

.activities-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 2rem;
}

.activity-category {
  margin-bottom: 1.5rem;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 6px;
}

.activity-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.activity-title {
  font-weight: 600;
  color: var(--vp-c-brand);
  text-decoration: none;
}

.activity-date {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}

.activity-description {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

@media (max-width: 768px) {
  .intro-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .project-title, .project-meta, .activity-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .project-links {
    margin-top: 0.5rem;
  }
  
  .project-meta {
    margin-top: 0.5rem;
  }
  
  .activity-date {
    margin-top: 0.25rem;
  }
  
  .repo-list {
    grid-template-columns: 1fr;
  }
}
</style>
