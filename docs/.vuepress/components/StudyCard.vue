<template>
  <router-link :to="study.path" class="study-item">
    <img class="study-image" :src="study.frontmatter.thumbnail" alt="이미지가 없습니다." />
    <div class="study-content">
      <div class="study-header">
        <div class="study-title">
          <a :href="study.path">{{ study.frontmatter.title }}</a>
        </div>
        <p v-if="study.frontmatter.description" class="excerpt">{{ study.frontmatter.description }}</p>
      </div>
      <div class="study-meta">
        <span class="date">{{ formatDate(study.frontmatter.date) }}</span>
        <span v-if="study.frontmatter.tags" class="tags">{{ study.frontmatter.tags.join(', ') }}</span>
      </div>
    </div>
  </router-link>
</template>

<script>
export default {
  name: "StudyCard",
  props: {
    study: Object,
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
  },
}
</script>

<style scoped>

.study-item {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--vp-c-gutter, #e2e2e3);
  border-radius: 5px;
  position: relative;
  display: flex;
  cursor: pointer;
  text-decoration: none !important;
  overflow: hidden;

  &::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 0;
    height: 1px;
    background-color: var(--vp-c-accent-hover);
    transition: width 0.3s ease;
    z-index: 1;
  }

  &:hover {
    box-shadow: 2px 2px 5px var(--vp-c-shadow);

    &::after {
      width: 100%;
    }
  }
}

.study-image {
  width: 220px;
  height: 160px;
  margin-right: 1rem;
  object-fit: cover;
  border-radius: 5px;
  user-select: none;
  -webkit-user-drag: none;
  cursor: pointer;
}

.study-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: calc(100% - 220px - 1rem);
  text-decoration: none;
}

.study-header {
  flex-grow: 1;
}

.study-title {
  margin-bottom: 1rem;
}

.study-title a {
  font-size: 1.25rem;
  color: var(--vp-c-text);
  text-decoration: none;
  position: relative;
  top: 0.15rem;
}

.study-title a:hover {
  color: var(--vp-c-accent-hover);
}

.study-meta {
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
  margin: 0.5rem 0;
  display: flex;
  gap: 1rem;
}

.tags {
  color: #3eaf7c;
}

.excerpt {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
}
</style>
