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
import CoverLetter from './CoverLetter.vue'

export default {
  name: 'Resume',
  components: { Portfolio, CoverLetter },
  data() {
    return {
      tabs: [
        { key: 'cover', label: '자기소개서', component: 'CoverLetter' },
        { key: 'portfolio', label: 'Portfolio', component: 'Portfolio' },
      ],
      currentTab: 'cover',
    }
  },
  computed: {
    currentTabComponent() {
      const found = this.tabs.find(t => t.key === this.currentTab)
      return found ? found.component : 'CoverLetter'
    }
  },
  methods: {
    selectTab(key) {
      this.currentTab = key
    }
  }
}
</script>

<style scoped>
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
</style>