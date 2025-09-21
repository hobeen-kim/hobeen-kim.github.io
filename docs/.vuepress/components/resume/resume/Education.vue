<template>
  <div class="education-section">
    <h2>학력 / 자격증</h2>
    <div class="education-container">
      <div class="education-item">
        <h3>한국대학교</h3>
        <div class="education-details">
          <div>컴퓨터공학과 학사</div>
          <div class="period">2017.03 ~ 2021.02</div>
        </div>
      </div>
    </div>
    
    <div class="certifications-container">
      <h3>자격증</h3>
      <div class="certification-list">
        <div class="certification-item">
          <div class="certification-name">AWS Certified Solutions Architect - Associate</div>
          <div class="certification-date">2023.05</div>
        </div>
        <div class="certification-item">
          <div class="certification-name">Certified Kubernetes Administrator (CKA)</div>
          <div class="certification-date">2024.01</div>
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
.education-item {
  margin-bottom: 1rem;
}

.education-details {
  display: flex;
  justify-content: space-between;
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}

.certifications-container {
  margin-top: 1.5rem;
}

.certification-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.certification-date {
  color: var(--vp-c-text-2);
  font-size: 0.9rem;
}
</style>
