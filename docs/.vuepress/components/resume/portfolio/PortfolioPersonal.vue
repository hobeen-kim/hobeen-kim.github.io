<template>
  <section class="personal-projects-section">
    <div class="header2">Personal Projects</div>

    <div class="personal-project-item">
      <h3>개인 기술 블로그 운영</h3>
      <p class="pp-desc">
        학습한 내용과 트러블 슈팅 경험을 기록하고 공유하기 위해 VuePress를 활용하여 블로그를 직접 구축하고 운영하고 있습니다.
      </p>
      <p><strong>사용 기술:</strong> VuePress, Vue.js, GitHub Actions</p>
      <p><strong>Link:</strong> <a href="https://hobeen-kim.github.io" target="_blank">https://hobeen-kim.github.io</a></p>
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
  margin-bottom: 2rem;
  padding: 1.5rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 8px;
  border: 1px solid var(--vp-c-border);
}

.personal-project-item h3 {
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
  color: var(--vp-c-brand);
  font-weight: 700;
}

.pp-desc {
  margin-bottom: 0.8rem;
  color: var(--vp-c-text-1);
  line-height: 1.5;
}

.personal-project-item p {
  margin: 0.3rem 0;
  color: var(--vp-c-text-2);
}

.personal-project-item a {
  color: var(--vp-c-brand);
  text-decoration: none;
}

.personal-project-item a:hover {
  text-decoration: underline;
}
</style>
