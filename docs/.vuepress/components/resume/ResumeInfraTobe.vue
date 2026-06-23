<template>
  <div class="resume-variant">
    <div class="resume-header">
      <h1>김호빈</h1>
      <div class="resume-header-sub">인프라 / DevOps 엔지니어</div>
    </div>

    <BasicInfo />
    <Summary />
    <Skills />
    <Experience />
    <Project />
    <Education />
  </div>
</template>

<script>
import BasicInfo from './resume-infra-tobe/BasicInfo.vue'
import Summary from './resume-infra-tobe/Summary.vue'
import Project from './resume-infra-tobe/Project.vue'
import Experience from './resume-infra-tobe/Experience.vue'
import Skills from './resume-infra-tobe/Skills.vue'
import Education from './resume-infra-tobe/Education.vue'

export default {
  name: "ResumeInfraTobe",
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
