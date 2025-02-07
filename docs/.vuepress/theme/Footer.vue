<template>
  <nav class="vp-page-nav" aria-label="page navigation">
    <a v-if="prev !== ''" class="route-link auto-link prev" :href="prev.path" aria-label="Get Started" style="text-decoration: none">
      <div class="hint" >
        <span class="arrow left"></span>
        이전
      </div>
      <div class="link">
        <span>{{ prev.frontmatter.title }}</span>
      </div>
    </a>
    <a v-if="next !== ''" class="route-link auto-link next" :href="next.path" aria-label="Get Started" style="text-decoration: none">
      <div class="hint">
        다음
        <span class="arrow right"></span>
      </div>
      <div class="link">
        <span>{{ next.frontmatter.title }}</span>
      </div>
    </a>
  </nav>
</template>

<script>
export default {
  name: 'Footer',
  data() {
    return {
      posts: __POSTS__ || [],
      books: __BOOKS__ || [],
      prev: '',
      next: '',
    }
  },
  mounted() {
    document.body.classList.add('page-has-title')

    if (this.$route.path.split('/')[1] === 'posts') {
      this.setPost()
    } else if (this.$route.path.split('/')[1] === 'books') {
      this.setBooks()
    }
  },
  methods: {
    setPost() {
      const currentLoc = this.posts.findIndex(post => post.path === this.$route.path)

      if (this.posts.length === 0) {
        return
      }

      if (currentLoc + 1 >= this.posts.length) {
        this.next = this.posts[currentLoc - 1]
        return
      }

      if (currentLoc - 1 < 0) {
        this.prev = this.posts[currentLoc + 1]
        return
      }

      this.next = this.posts[currentLoc - 1]
      this.prev = this.posts[currentLoc + 1]
    },
    setBooks() {
      const currentLoc = this.books.findIndex(book => book.path === this.$route.path)

      if (this.books.length === 0) {
        return
      }

      if (currentLoc + 1 >= this.books.length) {
        this.next = this.books[currentLoc - 1]
        return
      }

      if (currentLoc - 1 < 0) {
        this.prev = this.books[currentLoc + 1]
        return
      }

      this.next = this.books[currentLoc - 1]
      this.prev = this.books[currentLoc + 1]
    }
  },
}

</script>

<style scoped>

.vp-page-nav {
  padding: 1rem 0;
  text-decoration: none;
}
</style>