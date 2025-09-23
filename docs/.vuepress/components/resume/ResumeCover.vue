<template>
  <div class="resume-tabs">
    <div class="tabs">
      <div class="tab-buttons">
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
      <div class="download-button">
        <button class="download-btn" @click="downloadPDF">
          <img src="/images/pdf.png" alt="download" class="download-icon"/>
        </button>
      </div>
    </div>
    <div class="tab-panel" ref="contentToDownload">
      <component :is="currentTabComponent" />
    </div>


  </div>
  
</template>

<script>
import Portfolio from './Portfolio.vue'
import Resume from './Resume.vue'
import html2pdf from 'html2pdf.js'

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
    },
    downloadPDF() {
      const element = this.$refs.contentToDownload;
      const filename = this.currentTab === 'resume' ? '이력서.pdf' : '포트폴리오.pdf';
      
      const opt = {
        margin: 10,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      };
      
      // PDF 생성 시작 알림
      this.$nextTick(() => {
        // PDF 생성 및 다운로드
        html2pdf().set(opt).from(element).save().then(() => {
          console.log('PDF 생성 완료');
        }).catch(err => {
          console.error('PDF 생성 중 오류 발생:', err);
          alert('PDF 생성 중 오류가 발생했습니다.');
        });
      });
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
  justify-content: space-between;
  align-items: center;
  background-color: var(--vp-c-bg);
  border-bottom: 1px solid var(--vp-c-border);
  padding-bottom: 0.5rem;
  margin-bottom: 1rem;
}

.tab-buttons {
  display: flex;
  gap: 0.5rem;
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

.download-button {
  margin-top: 0.5rem;
}

.download-btn {
  border: 1px solid var(--vp-c-brand);
  background: var(--vp-c-brand);
  padding: 0.35rem 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
}

.download-btn:hover {
  background-color: var(--vp-c-brand-dark);
}

.download-icon {
  margin-top: 0.3rem;
  width: 1.5rem;
  height: 1.7rem;
}

.tab-panel {
  margin-top: 0.5rem;
}

.header2 {
  margin-top: 0;
  padding-top: 0.5rem;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--vp-c-brand);
  padding-bottom: 0;
  margin-bottom: 0;
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

.vp-page [vp-content] {
  max-width: 860px !important;
}

@media (max-width: 768px) {

  .activity-date {
    margin-top: 0.25rem;
  }
  
}
</style>