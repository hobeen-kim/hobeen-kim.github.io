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

</style>