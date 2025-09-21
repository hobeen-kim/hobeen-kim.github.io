<template>
  <div class="experience-section">
    <div class="header2">경력 사항</div>
    <div class="experience-item">
      <div class="experience-header">
        <div class="company-name">아그모</div>
        <span class="company-description">농기계 자율주행 시스템 및 ISOBUS 기반 마켓플레이스 서비스</span>
        <div class="position-period">
          <span class="position">백엔드 엔지니어</span><span class="period"> / 2025.02 ~ 현재</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">마켓플레이스 개발</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"> • ISOBUS 기반 장비에 대한 앱을 제공하는 마켓플레이스 서비스</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">마켓플레이스 개발</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"> • ISOBUS 기반 장비에 대한 앱을 제공하는 마켓플레이스 서비스</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
          </div>
        </div>
      </div>
    </div>
    <div class="experience-item">
      <div class="experience-header">
        <div class="company-name">테크랩스</div>
        <span class="company-description">고객 활동 이력을 바탕으로 한 초개인화 추천 서비스</span>
        <div class="position-period">
          <span class="position">AI 사업부 백엔드 엔지니어</span><span class="period"> / 2023.11 ~ 2025.02</span>
        </div>
      </div>
      <div class="responsibilities">
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">마켓플레이스 개발</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"> • ISOBUS 기반 장비에 대한 앱을 제공하는 마켓플레이스 서비스</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
          </div>
        </div>
        <div class="responsibility-item">
          <div class="responsibility-header">
            <div class="responsibility-title">마켓플레이스 개발</div>
            <div class="period">2025.04 ~ 현재</div>
          </div>
          <div class="responsibility-description">
            <div class="responsibility-detail-main"> • ISOBUS 기반 장비에 대한 앱을 제공하는 마켓플레이스 서비스</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
            <div class="responsibility-detail"> • 실시간 데이터 처리 시스템 개발</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Experience"
}
</script>

<style scoped>

.experience-section {
  margin-bottom: 1rem;
}
.experience-item {
  padding: 1rem;
  background-color: var(--vp-c-bg-soft);
  border-radius: 4px;
}

.experience-header {
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.company-name {
  font-size: 1.25rem;
  margin-bottom: 0.25rem;
  font-weight: 600;
  margin-right: 0.5rem;
  color: var(--vp-c-text-1);
}

.company-description {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  border-bottom: 1px solid var(--vp-c-border);
}

.position-period {
  margin-top: 0.25rem;
}

.period {
  margin-top: 0.25rem;
  font-weight: 300;
  font-size: 0.8rem;
  color: var(--vp-c-text-2, #6c757d);
}

.position {
  font-size: 0.8rem;
  color: var(--vp-c-text-2);
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  font-weight: 700;
}

.responsibilities {
  margin-top: 1.5rem;
  margin-bottom: 0.5rem;
}

.responsibility-item {
  margin-bottom: 1rem;
  display: flex;
}

.responsibility-header {
  font-weight: 700;
  margin-right: 0.5rem;
  min-width: 130px;
  color: var(--vp-c-text-1);
}

.responsibility-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--vp-c-text-1);
}

.responsibility-description {
}

.responsibility-detail-main {
  font-size: 0.9rem;
  border-bottom: 1px solid var(--vp-c-border);
  color: var(--vp-c-text-2);
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.responsibility-detail {
  font-size: 0.9rem;
  color: var(--vp-c-text-2);
  margin-bottom: 0.5rem;
}


</style>
