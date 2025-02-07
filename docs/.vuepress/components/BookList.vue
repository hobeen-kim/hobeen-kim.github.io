<template>

  <div class="book-container">
    <span class="book-list-title">책</span>
    <div class="book-list-description">깊이 있는 사람이 되기 위해 책을 읽습니다.</div>
    <div class="book-list">
      <div v-for="book in books" :key="book.slug">
        <BookCard :book="book"/>
      </div>
    </div>
  </div>
</template>

<script>
import BookCard from "./BookCard.vue";
import {usePageData} from "@vuepress/client";

export default {
  name: "BookList",
  components: { BookCard },
  data() {
    return {
      books: __BOOKS__ || [], // 빌드 타임에 생성된 전역 변수 사용
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
  },
  mounted() {
    document.body.classList.remove('page-has-title')
  }
}
</script>

<style scoped>

.book-container {
  width: 1000px;
  position: relative;
  left: -20%;
  margin: 0 auto;
  padding: 20px;
}

.book-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr); /* 2개의 열 */
  gap: 2rem; /* 열 사이의 간격 */
}

.book-list-title {
  font-size: 1.875rem;
  font-weight: 700;
  position: relative;
  left: 12%;
  padding-left: 2rem;
  margin-bottom: 1rem;
  margin-top: 1rem;
}

.book-list-description {
  font-size: 1rem;
  color: var(--vp-c-text-mute);
  position: relative;
  left: 12.3%;
  padding-left: 2rem;
  margin-top: 1rem;
  margin-bottom: 3rem;
}
</style>