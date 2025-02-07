<template>
  <div class="post-list">
    <span class="post-list-title">글</span><span v-if="category !== 'all'" class="category-title-sub">_ {{ toKorean(category) }}</span>
    <div class="post-list-description">{{ description }}</div>
    <div v-for="post in filteredPosts" :key="post.slug">
      <PostCard :post="post" :category="category" />
    </div>
  </div>
</template>

<script>
import {usePageData} from "@vuepress/client";
import ko from "../utils/locale"
import PostCard from "./PostCard.vue";

export default {
  name: "PostList",
  components: {PostCard},
  data() {
    return {
      posts: __POSTS__ || [], // 빌드 타임에 생성된 전역 변수 사용
      category: '',
      description: '',
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
  },
  computed: {
    filteredPosts() {

      if(this.category === 'all') {
        return this.posts
      }

      return this.posts.filter(post => post.category === this.category)
    }
  },
  mounted() {
    const page = usePageData()
    this.category = page.value.frontmatter.category
    this.description = page.value.frontmatter.description
    document.body.classList.remove('page-has-title')
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

</style>