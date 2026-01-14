<template>
  <div class="portfolio-container">
    <!-- 1. 기본적인 소개 -->
    <section class="intro-section">
      <h1 class="name">이름 (Name)</h1>
      <p class="position">Frontend Developer / Backend Developer</p>
      <div class="contact-info">
        <p>Email: email@example.com</p>
        <p>Github: <a href="https://github.com/your-id" target="_blank">https://github.com/your-id</a></p>
        <p>Blog: <a href="https://your-blog.com" target="_blank">https://your-blog.com</a></p>
      </div>
      <div class="intro-text">
        <p>
          여기에 간단한 자기소개를 작성해주세요. 어떤 개발자인지, 어떤 가치를 중요하게 생각하는지 등을 기술합니다.
        </p>
      </div>
    </section>

    <hr class="divider" />

    <!-- 2. 프로젝트 -->
    <section class="projects-section">
      <h2>Projects</h2>

      <!-- 프로젝트 항목 예시 -->
      <div class="project-item">
        <div class="project-header">
          <h3>프로젝트 명 (Project Name)</h3>
          <span class="period">202X.XX - 202X.XX</span>
        </div>
        
        <div class="project-overview">
          <p><strong>개요:</strong> 프로젝트에 대한 한 줄 요약 및 설명</p>
          <p><strong>수행 인원:</strong> 4명 (FE 2, BE 2)</p>
          <p><strong>역할:</strong> Frontend 개발, UI/UX 설계</p>
        </div>

        <div class="project-details">
          <h4>수행 업무</h4>
          <ul>
            <li>주요 기능 개발 내용 1</li>
            <li>주요 기능 개발 내용 2</li>
            <li>주요 기능 개발 내용 3</li>
          </ul>

          <h4>성과</h4>
          <ul>
            <li>정량적 성과 (예: 로딩 속도 50% 개선)</li>
            <li>정성적 성과 (예: 사용자 편의성 증대)</li>
          </ul>

          <h4>사용 기술</h4>
          <div class="tech-stack">
            <span class="tag">Vue.js</span>
            <span class="tag">TypeScript</span>
            <span class="tag">Spring Boot</span>
          </div>

          <h4>트러블 슈팅</h4>
          <div class="troubleshooting">
            <div class="ts-item">
              <p class="ts-problem"><strong>Problem:</strong> 발생했던 문제 상황 기술</p>
              <p class="ts-solution"><strong>Solution:</strong> 해결 방법 및 결과 기술</p>
            </div>
          </div>
        </div>
      </div>
      <!-- // 프로젝트 항목 끝 -->

      <!-- 추가 프로젝트가 있다면 위 구조를 복사해서 사용하세요 -->

    </section>

    <hr class="divider" />

    <!-- 3. 개인 프로젝트 -->
    <section class="personal-projects-section">
      <h2>Personal Projects</h2>

      <div class="personal-project-item">
        <h3>개인 프로젝트 명</h3>
        <p class="pp-desc">개인 프로젝트에 대한 간단한 설명입니다. 학습 목적이나 토이 프로젝트 등을 기술합니다.</p>
        <p><strong>사용 기술:</strong> React, Node.js</p>
        <p><strong>Github:</strong> <a href="#" target="_blank">Link</a></p>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'Portfolio',
  data() {
    return {
      // 필요한 경우 데이터를 이곳에서 관리할 수 있습니다.
    }
  }
}
</script>

<style scoped>
.portfolio-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #2c3e50;
}

.intro-section {
  margin-bottom: 3rem;
}

.name {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.position {
  font-size: 1.2rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.contact-info p {
  margin: 0.25rem 0;
}

.intro-text {
  margin-top: 1.5rem;
  line-height: 1.6;
}

.divider {
  border: 0;
  border-top: 1px solid #eaecef;
  margin: 3rem 0;
}

h2 {
  font-size: 2rem;
  border-bottom: 2px solid #3eaf7c;
  padding-bottom: 0.5rem;
  margin-bottom: 2rem;
}

.project-item {
  margin-bottom: 4rem;
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.project-header h3 {
  font-size: 1.75rem;
  margin: 0;
}

.period {
  color: #666;
  font-size: 0.9rem;
}

.project-overview {
  background-color: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.project-overview p {
  margin: 0.5rem 0;
}

h4 {
  font-size: 1.2rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: #3eaf7c;
}

ul {
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}

li {
  margin-bottom: 0.5rem;
}

.troubleshooting {
  background-color: #fffbf0;
  border: 1px solid #ffe58f;
  padding: 1rem;
  border-radius: 8px;
}

.ts-item {
  margin-bottom: 0.5rem;
}

.ts-item:last-child {
  margin-bottom: 0;
}

.personal-project-item {
  margin-bottom: 2rem;
}

.personal-project-item h3 {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.pp-desc {
  margin-bottom: 0.5rem;
}
</style>