<template>
  <div class="portfolio-container">
    <PortfolioIntro />
    <PortfolioProjects />
    <PortfolioPersonal />
  </div>
</template>

<script>
import PortfolioIntro from './portfolio/PortfolioIntro.vue'
import PortfolioProjects from './portfolio/PortfolioProjects.vue'
import PortfolioPersonal from './portfolio/PortfolioPersonal.vue'

export default {
  name: 'Portfolio',
  components: {
    PortfolioIntro,
    PortfolioProjects,
    PortfolioPersonal
  }
}
</script>

<style scoped>
.portfolio-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 1rem;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: var(--vp-c-text-1);
}

/* 공통 헤더 스타일 (Resume와 통일) */
:deep(.header2) {
  margin-top: 0;
  padding-top: 0.5rem;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--vp-c-brand);
  padding-bottom: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}
</style>
