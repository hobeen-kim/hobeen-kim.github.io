<template>
  <div class="education-section">
      <div class="header2">자격증 / 교육</div>
    <div class="eduCert-container">
      <div class="certifications-container">
        <div class="header3">자격증</div>
        <div class="certification-list">
          <div class="certification-item">
            <div class="certification-name">AWS DevOps Engineer - Professional</div>
            <div class="certification-date">2024.03.27</div>
          </div>
          <div class="certification-item">
            <div class="certification-name">AWS Solutions Architect - Professional</div>
            <div class="certification-date">2024.02.14</div>
          </div>
        </div>
      </div>
      <div class="education-container">
        <div class="header3">교육</div>
        <div class="education-list">
          <div class="education-item">
            <div class="education-header">
              <div class="education-title">코드스테이츠</div>
              <div class="period">2023.03 ~ 2023.10</div>
            </div>
            <div class="education-description">
              <div class="education-detail"> • 백엔드 개발자 양성 교육 과정 (45기)</div>
              <div class="education-detail"> • Java, Spring 학습</div>
              <div class="education-detail"> • 페어 프로그래밍, 팀 프로젝트를 통한 협업</div>
            </div>
          </div>
          <div class="education-item">
            <div class="education-header">
              <div class="education-title">육군사관학교</div>
              <div class="period">2014.03 ~ 2018.03</div>
            </div>
            <div class="education-description">
              <div class="education-detail"> • 국제관계학과</div>
              <div class="education-detail"> • 5년 군복무 ( ~ 23.04)</div>
            </div>
          </div>
        </div>
      </div>
    </div>

  </div>
</template>

<script>
export default {
  name: "Education"
}
</script>

<style scoped>

.education-section {
}

.eduCert-container {
  padding: 1rem;
}

.certifications-container {
  margin-bottom: 1.5rem;
}

.certification-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.certification-name {
  font-size: 1rem;
  color: var(--vp-c-text-1);
}

.certification-date {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.education-list {
  margin-top: 1rem;
  margin-bottom: 0.5rem;
}

.education-item {
  margin-bottom: 1rem;
  display: flex;
}

.education-header {
  font-weight: 700;
  margin-right: 0.5rem;
  min-width: 140px;
  color: var(--vp-c-text-1);
}

.education-title {
  font-size: 1rem;
  font-weight: 700;
  max-width: 130px;
  color: var(--vp-c-text-1);
}

.education-description {
}

.education-detail {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;
  line-height: 1.3;
  padding-left: 1rem;
  text-indent: -1rem;
}

.period {
  margin-top: 0.25rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}
</style>
