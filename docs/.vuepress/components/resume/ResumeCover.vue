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
    <div class="tab-panel" ref="contentToDownload"  :style="{ transform: `scale(${contentScale})`, transformOrigin: 'top' }">
      <component :is="currentTabComponent" />
    </div>


  </div>
  
</template>

<script>
import Portfolio from './Portfolio.vue'
import ResumeBackend from './ResumeBackend.vue'
import ResumeInfra from './ResumeInfra.vue'
// html2pdf는 SSR 환경에서 'self'를 참조하여 빌드 오류가 발생할 수 있으므로
// 클라이언트 사이드에서만 동적 로딩합니다.

export default {
  name: 'ResumeCover',
  components: { Portfolio, ResumeBackend, ResumeInfra },
  data() {
    return {
      tabs: [
        { key: 'backend', label: '백엔드 이력서', component: 'ResumeBackend' },
        { key: 'infra', label: '인프라 이력서', component: 'ResumeInfra' },
        { key: 'portfolio', label: '포트폴리오 (작성중)', component: 'Portfolio' },
      ],
      currentTab: 'backend',
      contentScale: 1
    }
  },
  computed: {
    currentTabComponent() {
      const found = this.tabs.find(t => t.key === this.currentTab)
      return found ? found.component : 'ResumeBackend'
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

      const filenameMap = {
        backend: '김호빈_백엔드_이력서.pdf',
        infra: '김호빈_인프라_이력서.pdf',
        portfolio: '김호빈_포트폴리오.pdf',
      };
      const filename = filenameMap[this.currentTab] || '김호빈_이력서.pdf';

      const scale = Number(this.contentScale) || 1;
      const MARGIN_MM = 10;                          // PDF 상하좌우 여백
      const INNER_W_MM = 210 - MARGIN_MM * 2;        // A4 내부 폭 190mm
      const INNER_H_MM = 297 - MARGIN_MM * 2;        // A4 내부 높이 277mm
      const H2C_SCALE = 3;                           // html2canvas 렌더 배율
      // 페이지 경계에서 쪼개지면 안 되는 블록
      const AVOID = [
        '.responsibility-item',
        '.experience-item',
        '.skill-category',
        '.certification-item',
        '.contact-item',
        '.project-header',
        '.responsibility-header'
      ].join(', ');

      // html2pdf 는 내용을 A4 내부 폭(mm)짜리 컨테이너에 복제해 캡처한다.
      // 화면 밖에 같은 폭의 호스트를 미리 만들어 두면, 여기서 잰 좌표가
      // 실제 캡처 결과와 1:1 로 일치하므로 페이지 나눔을 정확히 계산할 수 있다.
      const holder = document.createElement('div');
      holder.style.cssText = 'position:fixed;left:-10000px;top:0;z-index:-1;';
      const host = document.createElement('div');
      host.style.cssText = `width:${INNER_W_MM}mm;background:#ffffff;`;
      const inner = document.createElement('div');
      inner.style.cssText = `transform-origin:top left;transform:scale(${scale});`;

      const clone = this.$refs.contentToDownload.cloneNode(true);
      clone.style.transform = 'none';   // 축소는 inner 가 담당한다
      clone.style.transformOrigin = '';
      inner.appendChild(clone);
      host.appendChild(inner);
      holder.appendChild(host);
      document.body.appendChild(holder);

      try {
        const hostWidth = host.getBoundingClientRect().width;
        inner.style.width = hostWidth + 'px';
        await new Promise(r => requestAnimationFrame(r));

        // html2pdf 가 캔버스를 자르는 식과 동일하게 한 페이지 높이를 구한다
        const ratio = INNER_H_MM / INNER_W_MM;
        const pageHeight = Math.floor(hostWidth * H2C_SCALE * ratio) / H2C_SCALE;
        const GUARD = 3;   // 캔버스 픽셀 반올림 오차 여유

        // 경계에 걸친 항목 앞에 패딩을 넣어 다음 장으로 밀어낸다.
        // 패딩은 scale 이 걸린 서브트리 안에 들어가므로 실제 이동량이
        // scale 배로 줄어든다. 그만큼 미리 나눠서 높이를 잡는다.
        const targets = Array.prototype.slice.call(host.querySelectorAll(AVOID));
        for (const el of targets) {
          const base = host.getBoundingClientRect().top;
          const rect = el.getBoundingClientRect();
          const top = rect.top - base;
          const bottom = rect.bottom - base + GUARD;
          if (bottom - top > pageHeight) continue;   // 한 장을 넘는 항목은 어쩔 수 없다
          if (Math.floor(top / pageHeight) === Math.floor(bottom / pageHeight)) continue;

          const pad = document.createElement('div');
          pad.style.cssText =
            `display:block;height:${(pageHeight - (top % pageHeight)) / scale}px;`;
          el.parentNode.insertBefore(pad, el);
        }

        // 축소된 실제 높이를 호스트에 고정해야 빈 여백 페이지가 생기지 않는다.
        // 컨테이너 자체의 여백까지 포함하면 내용 없는 페이지가 한 장 더 붙으므로,
        // 실제로 뭔가 그려지는 마지막 요소의 아래쪽까지만 높이로 잡는다.
        const hostTop = host.getBoundingClientRect().top;
        let contentBottom = 0;
        for (const el of host.querySelectorAll('*')) {
          if (el.children.length > 0) continue;                 // 잎 노드만 본다
          if (el.tagName !== 'IMG' && !el.textContent.trim()) continue;
          const r = el.getBoundingClientRect();
          if (r.height === 0 || r.width === 0) continue;
          if (r.bottom > contentBottom) contentBottom = r.bottom;
        }
        const TAIL = 12;   // 마지막 줄이 잘리지 않도록 약간의 여유
        host.style.height =
          Math.ceil(Math.max(contentBottom - hostTop + TAIL, 1)) + 'px';

        const opt = {
          margin: MARGIN_MM,
          filename: filename,
          image: {
            type: 'jpeg',
            quality: 0.98
          },
          html2canvas: {
            scale: H2C_SCALE,
            useCORS: true,
            backgroundColor: '#ffffff',
            onclone: (doc) => {
              doc.documentElement.classList.remove('dark')
            }
          },
          // 페이지 나눔은 위에서 직접 계산해 넣었으므로 플러그인은 끈다
          pagebreak: { mode: [] },
          jsPDF: {
            unit: 'mm',
            format: 'a4',
            orientation: 'portrait'
          }
        };

        const { default: html2pdf } = await import('html2pdf.js');
        await html2pdf().set(opt).from(host).save();
        console.log('PDF 생성 완료');
      } catch (err) {
        console.error('PDF 생성 중 오류 발생:', err);
        alert('PDF 생성 중 오류가 발생했습니다.');
      } finally {
        document.body.removeChild(holder);
      }
    }
  }
}
</script>

<style>
/* PDF 출력 시 항목이 페이지 경계에서 잘리지 않도록 */
.responsibility-item,
.experience-item,
.skill-category,
.certification-item,
.contact-item,
.project-header,
.responsibility-header {
  break-inside: avoid;
  page-break-inside: avoid;
}

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
  pointer-events: none; /* 이미지에 마우스 이벤트 비활성화 */
  user-select: none; /* 사용자 선택 비활성화 */
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