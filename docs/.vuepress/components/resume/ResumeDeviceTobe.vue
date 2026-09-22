<template>
  <div class="resume-variant">
    <div class="resume-header">
      <h1>김호빈</h1>
      <div class="resume-header-sub">디바이스 플랫폼 엔지니어</div>
      <div class="tobe-note">
        2028년 5월 목표 이력서 —
        <span class="todo-item">점선 표시</span> 항목은 아직 채우지 않은 칸이다.
      </div>
    </div>

    <BasicInfo />
    <Skills />
    <Experience />
    <Project />
    <Writings />
    <Education />
  </div>
</template>

<script>
// 2028.05 목표(To-Be) 디바이스 플랫폼 이력서 (resume-tobe-device/)
import BasicInfo from './resume-tobe-device/BasicInfo.vue'
import Skills from './resume-tobe-device/Skills.vue'
import Experience from './resume-tobe-device/Experience.vue'
import Project from './resume-tobe-device/Project.vue'
import Writings from './resume-tobe-device/Writings.vue'
import Education from './resume-tobe-device/Education.vue'

export default {
  name: "ResumeDeviceTobe",
  components: { BasicInfo, Skills, Experience, Project, Writings, Education }
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
  margin-bottom: 6px;
  color: var(--vp-c-text);
}

.tobe-note {
  margin-left: 2px;
  margin-bottom: 10px;
  font-size: 0.8rem;
  color: var(--vp-c-text-mute, #8e8e8e);
}
</style>
