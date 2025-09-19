<template>
  <div class="post-list">
    <span class="post-list-title">글</span><span v-if="category !== 'all'" class="category-title-sub">_ {{ toKorean(category) }}</span>
    <div class="post-list-description">{{ description }}</div>
    <div v-for="post in paginatedPosts" :key="post.slug">
      <PostCard :post="post" :category="category" />
    </div>

    <div v-if="totalPages > 1" class="pagination">
      <button class="page-btn" :disabled="currentPage === 1" @click="prevPage">이전</button>

      <button
        v-for="page in totalPages"
        :key="page"
        class="page-number"
        :class="{ active: page === currentPage }"
        @click="goToPage(page)"
      >
        {{ page }}
      </button>

      <button class="page-btn" :disabled="currentPage === totalPages" @click="nextPage">다음</button>
    </div>
  </div>
</template>

<script>
import {usePageData} from "@vuepress/client";
import ko from "../utils/locale"
import PostCard from "./PostCard.vue";
import paginationState from "../utils/paginationState";

export default {
  name: "PostList",
  components: {PostCard},
  data() {
    return {
      posts: __POSTS__ || [], // 빌드 타임에 생성된 전역 변수 사용
      category: '',
      description: '',
      currentPage: 1,
      pageSize: 10,
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
    toKorean(category) {
      return ko[category]
    },
    goToPage(page) {
      if (page < 1 || page > this.totalPages) return
      this.currentPage = page
      this.scrollToTop()
    },
    prevPage() {
      if (this.currentPage > 1) {
        this.currentPage -= 1
        this.scrollToTop()
      }
    },
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage += 1
        this.scrollToTop()
      }
    },
    scrollToTop() {
      if (typeof window !== 'undefined') {
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    }
  },
  computed: {
    filteredPosts() {

      if(this.category === 'all') {
        return this.posts
      }

      return this.posts.filter(post => post.category === this.category)
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.filteredPosts.length / this.pageSize))
    },
    paginatedPosts() {
      const start = (this.currentPage - 1) * this.pageSize
      const end = start + this.pageSize
      return this.filteredPosts.slice(start, end)
    }
  },
  mounted() {
    const page = usePageData()
    this.category = page.value.frontmatter.category
    this.description = page.value.frontmatter.description
    document.body.classList.remove('page-has-title')
    // 전역 상태에서 카테고리별 페이지 초기화
    const saved = paginationState.getPage(this.category)
    this.currentPage = Math.min(Math.max(1, saved), this.totalPages)
  },
  watch: {
    // 필터링된 목록이나 카테고리가 바뀌면 페이지를 1로 리셋
    category() {
      // 카테고리 변경 시 저장된 페이지 복원 (없으면 1)
      const saved = paginationState.getPage(this.category)
      this.currentPage = Math.min(Math.max(1, saved), this.totalPages)
    },
    currentPage(newVal) {
      // 페이지 변경 시 전역 상태에 저장
      paginationState.setPage(this.category, newVal)
    },
    filteredPosts() {
      // 현재 페이지가 전체 페이지 수를 넘지 않도록 보정
      if (this.currentPage > this.totalPages) {
        this.currentPage = this.totalPages
        paginationState.setPage(this.category, this.currentPage)
      }
    }
  }
}
</script>

<style scoped>
.post-list {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.post-list-title {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 1rem;
  margin-top: 1rem;
}

.category-title-sub {
  margin-left: 0.3rem;
}

.post-list-description {
  font-size: 1rem;
  color: var(--vp-c-text-mute);
  margin-top: 1rem;
  margin-bottom: 3rem;
}

.pagination {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  justify-content: center;
  margin-top: 2rem;
}

.page-btn,
.page-number {
  border: 1px solid var(--vp-c-border);
  background: var(--vp-c-bg);
  color: var(--vp-c-border);
  border-radius: 6px;
  padding: 0.4rem 0.7rem;
  font-size: 0.9rem;
  cursor: pointer;
}

.page-number.active {
  background: var(--vp-c-bg);
  color: var(--vp-c-text);
  border-color: var(--vp-c-text);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>