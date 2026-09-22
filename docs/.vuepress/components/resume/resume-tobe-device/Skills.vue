<template>
  <div class="skills-section">
    <div class="header2">기술 스택</div>
    <div class="skills-container">
      <div class="skill-category">
        <div class="skill-category-title">디바이스/임베디드</div>
        <div class="skill-list"> CAN/CAN FD, ISOBUS(ISO 11783), J1939, QEMU, Embedded Linux<span class="todo-item">UDS/DoIP</span><span class="todo-item">ROS 2</span></div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">SIL/HIL 검증</div>
        <div class="skill-list"> 하드웨어 에뮬레이션, 신호 시뮬레이션, 테스트 자동화<span class="todo-item">HIL 벤치 구성</span></div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">디바이스 연동</div>
        <div class="skill-list"> AWS IoT(MQTT), Device Shadow, OTA, 원격 프로비저닝<span class="todo-item">gRPC</span></div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">장비 SW 플랫폼</div>
        <div class="skill-list"><span class="todo-item">Adaptive AUTOSAR</span><span class="todo-item">SOME/IP</span><span class="todo-item">기능안전 ISO 25119·26262</span></div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">언어</div>
        <div class="skill-list"> Rust, Kotlin, Java, C, Python<span class="todo-item">C++</span></div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">모니터링/관측성</div>
        <div class="skill-list"> 엣지 디바이스 상태 모니터링, 텔레메트리 수집·집계, 실시간 대시보드, Datadog</div>
      </div>
      <div class="skill-category">
        <div class="skill-category-title">클라우드</div>
        <div class="skill-list"> AWS(EKS, Lambda, SQS/SNS, S3, KMS), Docker, Kubernetes, Postgres, Redis</div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "SkillsDeviceTobe"
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
