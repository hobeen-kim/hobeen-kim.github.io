<template>
  <div class="skills-section">
    <div class="header2">기술 문서</div>
    <div class="skills-container">
      <div class="skill-category">
        <div class="skill-category-title">장비 통신</div>
        <div class="skill-list"> ISOBUS(ISO 11783) 42편 / AgIsoStack++ 22편 / CAN 통신 심화 25편 / WebRTC·AWS KVS 28편</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">로보틱스/임베디드</div>
        <div class="skill-list"> ArduPilot UAV 임베디드 37편 / Android Internals 26편 / 스마트농업 15편</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">인프라/관측성</div>
        <div class="skill-list"> 쿠버네티스·도커 52편 / 관측성(Grafana 스택) 46편</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">공개 링크</div>
        <div class="skill-list"><a href="https://hobeen-kim.github.io/" target="_blank">https://hobeen-kim.github.io/</a></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "WritingsDevice"
}
</script>

<style scoped>
.skills-container {
  padding: 1rem 1rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
}

.skill-description {
  font-size: 0.8rem;
  margin-bottom: 0.7rem;
  color: var(--vp-c-text-2, #8e8e8e);
  font-style: italic;
}

.skill-category {
  display: flex;
}

.skill-category-title {
  margin-top: 0.3rem;
  margin-bottom: 0.3rem;
  font-size: 1rem;
  font-weight: 700;
  min-width: 130px;
}

.skill-list {
  font-size: 0.9rem;
  margin-top: 0.3rem;
  margin-left: 1rem;
  margin-bottom: 0.3rem;
}
</style>
