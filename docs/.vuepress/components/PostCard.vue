<template>
  <router-link class="post-item" :to="post.path">
    <img class="post-image" :src="post.frontmatter.thumbnail" alt="post.frontmatter.thumbnail" />
    <div class="post-content">
      <div class="post-header">
        <div class="post-title">
          <a :href="post.path">{{ post.frontmatter.title }}</a>
          <span v-if="category === 'all'" class="post-title-cat">_{{ toKorean(post.category) }}</span>
        </div>
        <p v-if="post.excerpt" class="excerpt">{{ post.excerpt }}</p>
      </div>
      <div class="post-meta">
        <span class="date">{{ formatDate(post.frontmatter.date) }}</span>
        <span v-if="post.frontmatter.tags" class="tags">
          {{ post.frontmatter.tags.join(', ') }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script>
import ko from "../utils/locale";

export default {
  name: "PostCard",
  props: {
    post: Object,
    category: String,
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
    toKorean(category) {
      return ko[category]
    },
  },
}
</script>

<style scoped>
.post-item {
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

.post-image {
  width: 150px;
  height: 150px;
  margin-right: 1rem;
  object-fit: cover;
  border-radius: 5px;
  user-select: none;
  -webkit-user-drag: none;
  cursor: pointer;
}

.post-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: calc(100% - 150px - 2rem);
  text-decoration: none;
}

.post-header {
  flex-grow: 1;
}

.post-title {
  margin-bottom: 1rem;
}

.post-title a {
  font-size: 1.25rem;
  color: var(--vp-c-text);
  text-decoration: none;
  position: relative;
  top: 0.15rem;
}

.post-title a:hover {
  color: var(--vp-c-accent-hover);
}

.post-title-cat {
  font-size: 0.9rem;
  background-color: var(--vp-c-accent-soft);
  color: var(--vp-c-text-mute);
  padding: 0.2rem;
  margin-left: 0.5rem;
  border-radius: 5px;
}

.post-meta {
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
  margin: 0.5rem 0;
  display: flex;
  gap: 1rem;
}

.tags {
  color: #3eaf7c;
  width: 13rem;
}

.date {
  width: 9rem;
}

.excerpt {
  margin: 0.5rem 0 0;
  color: var(--vp-c-text-mute);
}
</style>