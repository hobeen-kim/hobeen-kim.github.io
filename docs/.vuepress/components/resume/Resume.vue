<template>
  <div class="resume-container">
    <div class="resume-header">
      <h1>몰입하는 개발자, 김호빈입니다. (작성중)</h1>
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
// 각 섹션 컴포넌트 가져오기
import BasicInfo from './resume/BasicInfo.vue'
import Summary from './resume/Summary.vue'
import Project from './resume/Project.vue'
import Experience from './resume/Experience.vue'
import Skills from './resume/Skills.vue'
import Education from './resume/Education.vue'

export default {
  name: "ResumeSection",
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

<style>
/* Resume 고유 스타일 */
.resume-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
</style>