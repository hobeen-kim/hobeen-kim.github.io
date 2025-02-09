<template>
  <router-link :to="book.path" class="book-item">
    <img class="book-image" :src="book.frontmatter.thumbnail" alt="이미지가 없습니다." />
    <div class="book-content">
      <div class="book-header">
        <div class="book-title">
          <a :href="book.path">{{ book.frontmatter.title }}</a>
        </div>
        <div class="book-info">{{ book.frontmatter.author }}, <span class="book-name">『{{ book.frontmatter.bookName }}』</span></div>
        <p v-if="book.excerpt" class="excerpt">{{ book.excerpt }}</p>
      </div>
      <div class="book-meta">
        <span class="date">{{ formatDate(book.frontmatter.date) }}</span>
        <span v-if="book.frontmatter.tags" class="tags">
          {{ book.frontmatter.tags.join(', ') }}
        </span>
      </div>
    </div>
  </router-link>
</template>

<script>
export default {
  name: "BookCard",
  props: {
    book: Object,
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

.book-item {
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

.book-image {
  width: 220px;
  height: 330px;
  margin-right: 1rem;
  object-fit: cover;
  border-radius: 5px;
  user-select: none;
  -webkit-user-drag: none;
  cursor: pointer;
}

.book-content {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  width: calc(100% - 150px - 2rem);
  text-decoration: none;
}

.book-header {
  flex-grow: 1;
}

.book-title {
  margin-bottom: 1rem;
}

.book-title a {
  font-size: 1.25rem;
  color: var(--vp-c-text);
  text-decoration: none;
  position: relative;
  top: 0.15rem;
}

.book-title a:hover {
  color: var(--vp-c-accent-hover);
}

.book-info {
  font-size: 1rem;
  color: var(--vp-c-text-mute);
  padding: 0.2rem;
  margin-bottom: 1rem;
  border-radius: 5px;
}

.book-name {
  border-bottom: 1px solid var(--vp-c-accent-hover);
  font-weight: bold;

  [data-theme='dark'] & {
    border-bottom: 1px solid rgba(52, 148, 105, 0.8);
  }
}

.book-meta {
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