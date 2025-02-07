<template>
  <div class="home-description">
    <div>
      <span class="contact-text">저는...</span>
      <ul style="margin-top: 0.2rem">
        <li><strong>테스트</strong>를 좋아합니다.</li>
        <li><strong>책 읽기</strong>를 좋아합니다.</li>
        <li><strong>문제</strong>를 풀면서 희열을 느낍니다.</li>
        <li><strong>목표를 설정하고 추진</strong>하는 데 강합니다.</li>
      </ul>
    </div>
    <div class="contact-container">
      <span class="contact-text">연락처</span>
      <div class="resume-body">
        <div>
          <ul style="list-style-type: none; margin-top: 0.2rem">
            <li>📧</li>
            <li>📞</li>
            <li><img src="/images/github-mark.png" alt="github" class="home-description-icon"></li>
          </ul>
        </div>
        <div>
          <ul style="list-style-type: none; margin-top: 0.2rem">
            <li>sksjsksh32@gmail.com</li>
            <li>010-7174-4174</li>
            <li><a href="https://github.com/hobeen-kim">https://github.com/hobeen-kim</a></li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "MyDescription"
}
</script>

<style scoped>
strong {
  font-weight: 700;
  text-decoration: underline;
}

.home-description {
  display: flex;
}

.contact-container {
  margin-left: 16rem;
}

.resume-body {
  display: flex;
}

.contact-text {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--vp-c-accent);
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