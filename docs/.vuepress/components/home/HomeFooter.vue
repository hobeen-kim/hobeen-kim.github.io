<template>
  <div class="home-footer">
    <div class="copy-right">
    © 2025 Andy.
    </div>
    <div class="contact">
      📧 sksjsksh32@gmail.com ·
      <a href="https://github.com/hobeen-kim"><img src="/images/github-mark.png" alt="github" class="home-description-icon"></a>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomeFooter"
}
</script>

<style scoped>
.home-footer {
  margin-top: 3rem;
  margin-bottom: 3rem;
  margin-left: 2rem;
  padding-top: 1rem;
  padding-left: 2rem;
  border-top: 1.5px solid var(--vp-c-text);
  display: flex;
  justify-content: space-between;
}

.copy-right {
  font-size: 0.9rem;
  font-weight: 700;
}

.contact {
  margin-left: 2rem;
  font-size: 0.9rem;
  font-weight: 700;
}

.home-description-icon {
  width: 1.2rem;
  height: 1.2rem;
  content: url('/images/github-mark.png');
}

[data-theme='dark'] .home-description-icon {
  content: url('/images/github-mark-white.png');
}
</style>