<template>
  <div class="summary-section">
    <div class="header2">자기 소개</div>
    <div class="summary">
      <p> Java, Kotlin, Spring 기반 3년차 백엔드 개발자로 일 로그 8000만 건의 추천 서비스 스타트업과 농기계 자율주행 스타트업에서
        백엔드 시스템 개발과 데이터 파이프라인 구축 업무를 진행했습니다. 디바이스 OTA 관리, OIDC 인증, 이벤트 기반 동기화 등
        도메인 복잡도가 높은 시스템을 멀티모듈 아키텍처로 설계·구현했습니다.</p>
      <p> 테스트 코드 작성을 즐기며 실제 환경에 맞는 테스트를 통해 가능한 모든 경우를 대비하고자 노력합니다. Testcontainers 기반
        통합 테스트와 idempotency·retry·rollback 정책으로 멱등하고 회귀에 강한 코드를 추구합니다. </p>
      <p>모르는 영역에 발을 들이는 것을 좋아합니다. 신기술에 관심이 많아 Keycloak, Kafka Streams, LLM 등 여러 기술을 배우고 실제로 업무에
        적용한 경험이 있습니다. 이러한 배움으로 문제를 해결할 때 항상 더 나은 방법과 기술을 찾고자 노력합니다.</p>
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

  p {
    margin-top: 0.2rem;
    margin-bottom: 0.2rem;
  }
}

</style>
