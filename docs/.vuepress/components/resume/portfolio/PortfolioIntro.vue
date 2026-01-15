<template>
  <section class="intro-section">
    <div class="name">김호빈</div>
    <p class="position">백엔드 엔지니어</p>
    <div class="contact-info">
      <p>Email: sksjsksh32@gmail.com</p>
      <p>Github: <a href="https://github.com/hobeen-kim" target="_blank">https://github.com/hobeen-kim</a></p>
      <p>Blog: <a href="https://hobeen-kim.github.io" target="_blank">https://hobeen-kim.github.io</a></p>
    </div>
    <div class="intro-text">
      <p>
        안녕하세요, 백엔드 엔지니어 김호빈입니다. <br>
        안정적이고 확장 가능한 시스템을 설계하고 구축하는 것에 관심이 많습니다. <br>
        새로운 기술을 배우고 적용하여 비즈니스 문제를 해결하는 과정을 즐깁니다.
      </p>
    </div>
  </section>
</template>

<script>
export default {
  name: 'PortfolioIntro'
}
</script>

<style scoped>
.intro-section {
  margin-bottom: 3rem;
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 8px;
}

.name {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--vp-c-text-1);
}

.position {
  font-size: 1rem;
  color: var(--vp-c-text-2);
  margin-bottom: 1.5rem;
}

.contact-info p {
  margin: 0.25rem 0;
  color: var(--vp-c-text-2);
}

.contact-info a {
  color: var(--vp-c-brand);
  text-decoration: none;
}

.contact-info a:hover {
  text-decoration: underline;
}

.intro-text {
  margin-top: 1.5rem;
  line-height: 1.6;
  color: var(--vp-c-text-1);
}
</style>
