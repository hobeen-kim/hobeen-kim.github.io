<template>
  <div class="study-container">
    <div class="study-header">
      공부하기
      <router-link class="study-router-link" :to="'/_study/'"> > 전체 보기</router-link>
    </div>
    <div class="study-cards">
      <router-link
        v-for="study in recentStudies"
        :key="study.path"
        :to="study.path"
        class="study-item"
      >
        <img
          v-if="study.frontmatter && study.frontmatter.thumbnail"
          class="study-image"
          :src="study.frontmatter.thumbnail"
          alt="study thumbnail"
        />
        <div class="study-content">
          <div class="study-title">
            {{ study.frontmatter && study.frontmatter.title }}
          </div>
          <p v-if="study.excerpt" class="study-excerpt">{{ study.excerpt }}</p>
          <div class="study-meta">
            <span v-if="study.frontmatter && study.frontmatter.tags" class="study-tags">
              {{ study.frontmatter.tags.join(', ') }}
            </span>
          </div>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RecentStudies',
  data() {
    return {
      studies: __STUDIES__ || [],
    }
  },
  computed: {
    recentStudies() {
      return this.studies.slice(0, 2)
    },
  },
}
</script>

<style scoped>
.study-container {
  width: 100%;
  padding: 1rem;
}

.study-header {
  font-weight: 700;
  margin-bottom: 1rem;
}

.study-router-link {
  font-size: 0.9rem;
  margin-left: 0.4rem;
}

.study-cards {
  display: flex;
  flex-direction: column;
  gap: 0;
}

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
  width: 150px;
  height: 150px;
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
  width: calc(100% - 150px - 2rem);
}

.study-title {
  font-size: 1.25rem;
  color: var(--vp-c-text);
  margin-bottom: 0.5rem;
  font-weight: 600;
}

.study-excerpt {
  margin: 0.5rem 0 0;
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
}

.study-meta {
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
  margin: 0.5rem 0;
}

.study-tags {
  color: #3eaf7c;
}
</style>
