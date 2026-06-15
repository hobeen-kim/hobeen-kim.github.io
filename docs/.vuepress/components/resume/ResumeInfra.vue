<template>
  <div class="resume-variant">
    <div class="resume-header">
      <h1>김호빈</h1>
      <div class="resume-header-sub">인프라 엔지니어</div>
    </div>

    <!-- 각 섹션을 컴포넌트로 분리 -->
    <BasicInfo />
    <Summary />
    <Skills />
    <Experience />
    <Project />
    <Education />
  </div>
</template>

<script>
// 인프라 이력서 섹션 컴포넌트 (resume-infra/)
import BasicInfo from './resume-infra/BasicInfo.vue'
import Summary from './resume-infra/Summary.vue'
import Project from './resume-infra/Project.vue'
import Experience from './resume-infra/Experience.vue'
import Skills from './resume-infra/Skills.vue'
import Education from './resume-infra/Education.vue'

export default {
  name: "ResumeInfra",
  components: {
    BasicInfo,
    Summary,
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
