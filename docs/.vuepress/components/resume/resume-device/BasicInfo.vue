<template>
  <div class="basic-info-section">
    <div class="contact-section">
      <div class="section-title">연락처</div>
      <div class="contact-item">
        <div class="contact-label">이메일</div>
        <div class="contact-value">sksjsksh32@gmail.com</div>
      </div>
      <div class="contact-item">
        <div class="contact-label">전화번호</div>
        <div class="contact-value">010-7174-4174</div>
      </div>
    </div>
    
    <div class="channel-section">
      <div class="section-title">채널</div>
      <div class="contact-item">
        <div class="contact-label">블로그</div>
        <div class="contact-value">
          <a href="https://github.com/hobeen-kim" target="_blank">https://github.com/hobeen-kim</a>
        </div>
      </div>
      <div class="contact-item">
        <div class="contact-label">깃허브</div>
        <div class="contact-value">
          <a href="https://hobeen-kim.github.io/" target="_blank">https://hobeen-kim.github.io/</a>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "BasicInfo"
}
</script>

<style scoped>
.basic-info-section {
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}

.contact-section, .channel-section {
  margin-bottom: 1.5rem;
}

.section-title {
  color: var(--vp-c-brand);
  font-size: 1rem;
  font-weight: 900;
  margin-bottom: 1rem;
  padding-bottom: 0;
  border-bottom: none;
}

.contact-item {
  display: flex;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
  font-weight: 700;
}

.contact-label {
  font-size: 0.9rem;
  font-weight: 600;
  min-width: 80px;
  margin-right: 0.5rem;
}

.contact-value {
  font-size: 0.9rem;
  color: var(--vp-c-text-1);
}

.contact-value a {
  color: var(--vp-c-text-1);
  text-decoration: none;
}

.contact-value a:hover {
  text-decoration: underline;
}
</style>
