<template>
  <div class="log-list">
    <span class="log-list-title">짧은 글</span>
    <div class="log-list-description">생각과 감정, 다짐을 공유합니다.</div>
    <div class="log" v-for="log in processedLogs" :key="log.frontmatter.title">
      <h3 class="log-title">{{ log.frontmatter.title }}</h3>
      <div class="log-date">{{ formatDate(log.frontmatter.date) }}</div>
      <ImgBox v-if="hasImage(log.images)" :images="log.images" :path="`/images/${log.slug}/`"/>
      <div class="markdown-content" v-html="log.html"></div>
      <div class="log-tag">{{ log.frontmatter.tags.map(tag => `#${tag}`).join(' ') }}</div>
    </div>
  </div>
</template>

<script>
import MarkdownIt from 'markdown-it'
import ImgBox from "./ImgBox.vue";

export default {
  name: 'LogList',
  components: {ImgBox},
  data() {
    return {
      logs: __LOGS__ || [],
      md: new MarkdownIt()
    }
  },
  computed: {
    processedLogs() {
      return this.logs.map(log => ({
        ...log,
        html: this.md.render(log.content || '')
      }))
    }
  },
  methods: {
    formatDate(date) {
      if (!date) return ''
      return new Date(date).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    hasImage(images) {
      return images && images.length > 0
    }
  }
}
</script>

<style scoped>

.markdown-content {
  /* 마크다운 콘텐츠 스타일링 */
  h1, h2, h3 {
    margin: 1rem 0;
  }

  p {
    line-height: 1.6;
    margin: 1rem 0;
  }

  code {
    background-color: var(--vp-c-code-tab-bg);
    padding: 0.2em 0.4em;
    border-radius: 3px;
  }

  font-weight: 500;
  color: rgba(75,85,99,1);
}

[data-theme='dark'] .markdown-content {
  color: rgb(235 235 245 / 76%);
}

.log-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.log-list-title {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 1rem;
  margin-top: 1rem;
}

.log-list-description {
  font-size: 1rem;
  color: var(--vp-c-text-mute);
  margin-top: 1rem;
  margin-bottom: 3rem;
}

.log {
  padding-bottom: 1.5rem;
  border-bottom: 1.5px solid rgba(75,85,99, 0.3);
  margin-bottom: 1.5rem;
}

[data-theme='dark'] .log {
  border-bottom: 1.5px solid rgba(235,235,245, 0.3);
}

.log-title {
  font-weight: 700;
  margin-bottom: 0.5rem !important;
}

.log-date {
  color: var(--vp-c-text-subtle);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.log-tag {
  margin-top: 1rem;
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
}

</style>