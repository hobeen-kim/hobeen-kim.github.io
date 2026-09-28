<template>
  <div class="resume-variant">
    <div class="resume-header">
      <h1>김호빈</h1>
      <div class="resume-header-sub">백엔드 엔지니어 · 디바이스 플랫폼</div>
    </div>

    <!-- 각 섹션을 컴포넌트로 분리 -->
    <BasicInfo />
    <Skills />
    <Experience />
    <Project />
    <Education />
  </div>
</template>

<script>
// 디바이스 플랫폼 이력서 섹션 컴포넌트 (resume-device/)
import BasicInfo from './resume-device/BasicInfo.vue'
import Project from './resume-device/Project.vue'
import Experience from './resume-device/Experience.vue'
import Skills from './resume-device/Skills.vue'
import Education from './resume-device/Education.vue'

export default {
  name: "ResumeDevice",
  components: {
    BasicInfo,
    Project,
    Experience,
    Skills,
    Education
  }
}
</script>

<style scoped>
.resume-variant {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.resume-header-sub {
  margin-top: -10px;
  margin-left: 2px;
  margin-bottom: 10px;
  color: var(--vp-c-text);
}
</style>
