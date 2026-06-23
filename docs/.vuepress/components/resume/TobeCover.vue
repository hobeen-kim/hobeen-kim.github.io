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
        <div class="scale-selector">
          <select v-model="contentScale" style="max-width: 100px">
            <option value="1">100%</option>
            <option value="0.9">90%</option>
            <option value="0.8">80%</option>
            <option value="0.7">70%</option>
          </select>
        </div>
        <button class="download-btn" @click="downloadPDF">
          <img src="/images/pdf.png" alt="download" class="download-icon"/>
        </button>
      </div>
    </div>
    <div class="tab-panel" ref="contentToDownload" :style="{ transform: `scale(${contentScale})`, transformOrigin: 'top' }">
      <component :is="currentTabComponent" />
    </div>
  </div>
</template>

<script>
import ResumeInfraTobe from './ResumeInfraTobe.vue'
import PortfolioTobe from './PortfolioTobe.vue'
// html2pdf는 SSR 환경에서 'self'를 참조하여 빌드 오류가 발생할 수 있으므로
// 클라이언트 사이드에서만 동적 로딩합니다.

export default {
  name: 'TobeCover',
  components: { ResumeInfraTobe, PortfolioTobe },
  data() {
    return {
      tabs: [
        { key: 'infra', label: '인프라 경력서', component: 'ResumeInfraTobe' },
        { key: 'portfolio', label: '포트폴리오', component: 'PortfolioTobe' },
      ],
      currentTab: 'infra',
      contentScale: 1
    }
  },
  computed: {
    currentTabComponent() {
      const found = this.tabs.find(t => t.key === this.currentTab)
      return found ? found.component : 'ResumeInfraTobe'
    }
  },
  methods: {
    selectTab(key) {
      this.currentTab = key
    },
    async downloadPDF() {
      // SSR 환경 방지: 브라우저에서만 동작
      if (typeof window === 'undefined') {
        console.warn('PDF 다운로드는 브라우저에서만 가능합니다.');
        return;
      }

      const element = this.$refs.contentToDownload;
      const filenameMap = {
        infra: '김호빈_인프라_경력서.pdf',
        portfolio: '김호빈_포트폴리오.pdf',
      };
      const filename = filenameMap[this.currentTab] || '김호빈_이력서.pdf';

      const opt = {
        margin: 10,
        filename: filename,
        image: {
          type: 'jpeg',
          quality: 0.98
        },
        html2canvas: {
          scale: 3,
          useCORS: true,
          onclone: (doc) => {
            doc.documentElement.classList.remove('dark')
          }
        },
        jsPDF: {
          unit: 'mm',
          format: 'a4',
          orientation: 'portrait'
        }
      };

      try {
        // 클라이언트에서만 동적 임포트
        const { default: html2pdf } = await import('html2pdf.js');
        await this.$nextTick();
        await html2pdf().set(opt).from(element).save();
        console.log('PDF 생성 완료');
      } catch (err) {
        console.error('PDF 생성 중 오류 발생:', err);
        alert('PDF 생성 중 오류가 발생했습니다.');
      }
    }
  }
}
</script>

<style>
.resume-tabs {
  position: relative;
}

.tabs {
  z-index: 1;
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
  pointer-events: none;
  user-select: none;
}

.scale-selector {
  display: inline-block;
  margin-right: 10px;
  vertical-align: middle;
}

.scale-selector select {
  padding: 0.35rem 0.5rem;
  border: 1px solid var(--vp-c-accent-bg);
  border-radius: 4px;
  background-color: var(--vp-c-bg);
  color: var(--vp-c-text);
  font-size: 0.8rem;
}

.download-button {
  margin-top: 0.5rem;
  display: flex;
  align-items: center;
}

.tab-panel {
  margin-top: 0.5rem;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.tag {
  background-color: #eef1f5;
  padding: 0.1rem 0.25rem;
  border-radius: 15px;
  font-size: 0.85rem;
  color: #476582;
}

[data-theme='dark'] .tag {
  background-color: rgb(87, 87, 87);
  color: #82a9cf;
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
