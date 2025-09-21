<template>
  <div class="resume-tabs">
    <div class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: currentTab === tab.key }"
        @click="selectTab(tab.key)"
      >
        {{ tab.label }}
      </button>
    </div>

    <div class="tab-panel">
      <component :is="currentTabComponent" />
    </div>
  </div>
  
</template>

<script>
import Portfolio from './Portfolio.vue'
import Resume from './Resume.vue'

export default {
  name: 'ResumeCover',
  components: { Portfolio, Resume },
  data() {
    return {
      tabs: [
        { key: 'resume', label: '이력서', component: 'Resume' },
        { key: 'portfolio', label: '포트폴리오', component: 'Portfolio' },
      ],
      currentTab: 'resume',
    }
  },
  computed: {
    currentTabComponent() {
      const found = this.tabs.find(t => t.key === this.currentTab)
      return found ? found.component : 'Resume'
    }
  },
  methods: {
    selectTab(key) {
      this.currentTab = key
    }
  }
}
</script>

<style>
.resume-tabs {
  position: relative;
}

.tabs {
  position: sticky;
  top: 3.5rem;
  display: flex;
  gap: 0.5rem;
  align-items: center;
  background-color: var(--vp-c-bg);
  border-bottom: 1px solid var(--vp-c-border);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.tab-btn {
  margin-top: 0.5rem;
  border: 1px solid var(--vp-c-accent-bg);
  background: var(--vp-c-bg);
  color: var(--vp-c-accent-bg);
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
}

.tab-btn.active {
  border-color: var(--vp-c-accent);
  font-weight: 900;
  color: var(--vp-c-accent);
}

.tab-panel {
  margin-top: 0.5rem;
}

/* 공통 스타일 */
.resume-container, .portfolio-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
  font-family: 'Noto Sans KR', sans-serif;
  color: var(--vp-c-text-1);
  background-color: var(--vp-c-bg);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.resume-header, .portfolio-header {
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--vp-c-divider);
}

h1 {
  font-size: 2rem;
  font-weight: 700;
  color: var(--vp-c-brand);
  margin-bottom: 1.5rem;
  text-align: center;
}

.header2 {
  margin-top: 0;
  padding-top: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--vp-c-brand);
  padding-bottom: 0;
  margin-bottom: 0;
}

h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--vp-c-text-1);
  margin: 0.5rem 0;
}

h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--vp-c-text-2);
  margin: 0.5rem 0;
}

.section {
  margin-bottom: 2rem;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.tech-tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: var(--vp-c-brand-dimm);
  color: var(--vp-c-brand);
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

ul {
  margin: 0.5rem 0 0.5rem 1.5rem;
  padding: 0;
}

li {
  margin-bottom: 0.5rem;
}

@media (max-width: 768px) {

  .activity-date {
    margin-top: 0.25rem;
  }
  
}
</style>