<template>
  <div class="summary-section">
    <div class="header2">자기 소개</div>
    <div class="summary">
      <p>몰입을 즐기는 개발자, 김호빈입니다. 2년차 백엔드 개발자로 대규모 로그 관리 및 추천 API 서버 개발과 운영 경험이 있습니다. 테스트 코드 작성과 부하테스트를 통해 서비스 안정성을 높이고 리소스 효율화로 비용을 56% 절감한 경험이 있습니다.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: "Summary"
}
</script>

<style scoped>
.summary {
  background-color: var(--vp-c-bg-soft);
  padding: 1rem;
  border-radius: 4px;
  border-left: 4px solid var(--vp-c-brand);
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}

</style>
