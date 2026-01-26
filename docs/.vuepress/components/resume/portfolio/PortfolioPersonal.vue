<template>
  <section class="personal-projects-section">
    <div class="header2">Personal Projects</div>

    <!-- DevTag -->
    <div class="personal-project-item">
      <div class="project-header">
        <h3>DevTag</h3>
        <span class="period">2025.12 ~ 진행중</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 국내 기술 블로그의 글을 수집하여 태그별로 분류해 제공하고, 주간 리포트를 발행하는 서비스</p>
        <p><strong>수행 인원:</strong> 1명 (개인 프로젝트)</p>
        <p><strong>역할:</strong> 풀스택 개발 (기획, 디자인, 개발, 배포, 운영)</p>
      </div>

      <div class="project-details">
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">Next.js</span>
          <span class="tech-tag">Spring Boot</span>
          <span class="tech-tag">Jsoup</span>
          <span class="tech-tag">GitHub Actions</span>
        </div>

        <h4>트러블 슈팅</h4>
        <div class="troubleshooting">
          <div class="ts-item">
            <p class="ts-problem"><strong>Problem:</strong> 다양한 블로그 플랫폼(Tistory, Velog, Medium 등)마다 DOM 구조가 달라 크롤링 규칙 관리가 어려움</p>
            <p class="ts-solution"><strong>Solution:</strong> 전략 패턴(Strategy Pattern)을 적용하여 플랫폼별 파서를 모듈화하고, 공통 인터페이스를 통해 확장성을 확보. 동적 렌더링 페이지는 Headless Browser를 도입하여 수집 성공률 개선</p>
          </div>
        </div>

        <div class="link-container">
          <strong>Link:</strong> <a href="#" target="_blank">DevTag 바로가기</a>
        </div>
      </div>
    </div>

    <!-- 한달살러 -->
    <div class="personal-project-item">
      <div class="project-header">
        <h3>한달살러</h3>
        <span class="period">2024.01 ~ 2024.12</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 국내 지자체 여행 지원금 및 한달 살기 프로그램 정보 제공 플랫폼 (App/Web)</p>
        <p><strong>수행 인원:</strong> 3명 (백엔드 1, 프론트엔드 1, 기획/마케팅 1)</p>
        <p><strong>역할:</strong> 백엔드 개발 (API 설계, 데이터 크롤링, 관리자 페이지)</p>
      </div>

      <div class="project-details">
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">NestJS</span>
          <span class="tech-tag">PostgreSQL</span>
          <span class="tech-tag">AWS</span>
          <span class="tech-tag">Docker</span>
        </div>

        <h4>트러블 슈팅</h4>
        <div class="troubleshooting">
          <div class="ts-item">
            <p class="ts-problem"><strong>Problem:</strong> 지자체 공고 데이터가 비정형 텍스트로 제공되어 검색 및 필터링이 불가능한 문제</p>
            <p class="ts-solution"><strong>Solution:</strong> OpenAI API를 활용하여 공고 텍스트에서 핵심 정보(지원 금액, 기간, 지역 등)를 추출하여 정형 데이터로 변환하는 전처리 파이프라인 구축</p>
          </div>
        </div>

        <div class="link-container">
          <strong>Link:</strong> <a href="#" target="_blank">한달살러 바로가기</a>
        </div>
      </div>
    </div>

    <!-- 개인 기술 블로그 -->
    <div class="personal-project-item">
      <div class="project-header">
        <h3>개인 기술 블로그 운영</h3>
        <span class="period">2023.03 ~ 현재</span>
      </div>

      <div class="project-overview">
        <p><strong>개요:</strong> 학습한 내용과 트러블 슈팅 경험을 기록하고 공유하기 위한 기술 블로그</p>
        <p><strong>수행 인원:</strong> 1명</p>
        <p><strong>역할:</strong> 블로그 구축 및 운영, 콘텐츠 작성</p>
      </div>

      <div class="project-details">
        <h4>사용 기술</h4>
        <div class="tech-tags">
          <span class="tech-tag">VuePress</span>
          <span class="tech-tag">Vue.js</span>
          <span class="tech-tag">GitHub Actions</span>
        </div>

        <h4>트러블 슈팅</h4>
        <div class="troubleshooting">
          <div class="ts-item">
            <p class="ts-problem"><strong>Problem:</strong> 이미지 리소스 증가로 인한 초기 로딩 속도 저하</p>
            <p class="ts-solution"><strong>Solution:</strong> 이미지 포맷을 WebP로 변환하고 Lazy Loading을 적용하여 LCP(Largest Contentful Paint) 시간 단축 및 사용자 경험 개선</p>
          </div>
        </div>

        <div class="link-container">
          <strong>Link:</strong> <a href="https://hobeen-kim.github.io" target="_blank">https://hobeen-kim.github.io</a>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
export default {
  name: 'PortfolioPersonal'
}
</script>

<style scoped>
.personal-projects-section {
  margin-bottom: 3rem;
}

.personal-project-item {
  margin-bottom: 3rem;
  padding: 1.5rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-border);
}

.project-header {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  border-bottom: 1px solid var(--vp-c-border);
  padding-bottom: 0.5rem;
}

.personal-project-item h3 {
  font-size: 1.5rem;
  margin: 0;
  color: var(--vp-c-brand);
  font-weight: 700;
}

.period {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.project-overview {
  background-color: var(--vp-c-bg-alt);
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
}

.project-overview p {
  margin: 0.3rem 0;
  color: var(--vp-c-text-1);
}

h4 {
  font-size: 1.1rem;
  margin-top: 1.5rem;
  margin-bottom: 0.75rem;
  color: var(--vp-c-brand);
  font-weight: 600;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tech-tag {
  display: inline-block;
  padding: 0.25rem 0.6rem;
  background-color: var(--vp-c-brand-dimm);
  color: var(--vp-c-brand);
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.troubleshooting {
  background-color: var(--vp-c-bg-alt);
  border-left: 4px solid var(--vp-c-warning);
  padding: 1rem;
  border-radius: 4px;
  margin-top: 1rem;
}

.ts-item {
  margin-bottom: 0.5rem;
}

.ts-problem {
  color: var(--vp-c-text-1);
  margin-bottom: 0.3rem;
}

.ts-solution {
  color: var(--vp-c-text-1);
}

.link-container {
  margin-top: 1.5rem;
  font-size: 0.95rem;
  color: var(--vp-c-text-1);
}

.link-container a {
  color: var(--vp-c-brand);
  text-decoration: none;
}

.link-container a:hover {
  text-decoration: underline;
}
</style>
