<template>
  <div class="recent-container">
    <div class="post-container">
      <div class="post-header">
        최근 글
        <router-link class="post-router-link" :to="`/posts/`"> > 글 목록</router-link>
      </div>
      <div class="post-cards">
        <PostCard :post="recentPost1"/>
        <PostCard :post="recentPost2"/>
      </div>
    </div>
    <div class="book-container">
      <div class="book-header">
        최근 읽은 책
        <router-link class="book-router-link" :to="`/books/`"> > 책 목록</router-link>
      </div>
      <BookCard :book="recentBook"/>
    </div>
  </div>

  <div class="home-description-container">
    <MyDescription/>
  </div>
  <div class="resume-container">
    <Resume/>
  </div>
</template>

<script>
import PostCard from "../PostCard.vue";
import BookCard from "../BookCard.vue";
import Resume from "./Resume.vue";
import MyDescription from "./MyDescription.vue";

export default {
  name: 'Home',
  components: {MyDescription, Resume, BookCard, PostCard},
  data() {
    return {
      posts: __POSTS__ || [],
      books: __BOOKS__ || [],
    }
  },
  methods: {
  },
  computed: {
    recentPost1() {
      return this.posts[0]
    },
    recentPost2() {
      return this.posts[1]
    },
    recentBook() {
      return this.books[0]
    }
  },
  mounted() {
    document.body.classList.remove('page-has-title')
  }
}
</script>

<style scoped>

.home-description-container {
  border-top : 1px solid var(--vp-c-control-hover);
  padding-top: 1rem;
  padding-left: 2rem;
  margin-left: 2rem;
  font-size: 0.9rem;
  line-height: 1.5;
  position: relative;

  strong {
    font-weight: 700;
    text-decoration: underline;
  }
}

.recent-container {
  width: 1000px;
  display: flex;
  justify-content: space-between;
}

.post-container {
  width: 50%;
  height: 100%;
  padding: 1rem;
  flex-direction: column;
  justify-content: space-between;
}

.post-container > div:first-child {
  align-self: flex-start;
}

.post-container > div:last-child {
  align-self: flex-end;
}

.post-header {
  font-weight: 700;
  margin-bottom: 1rem;
}

.post-router-link{
  font-size: 0.9rem;
  margin-left: 0.4rem;
}


.book-container {
  width: 50%;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.book-container > div:first-child {
  align-self: flex-start;
}

.book-container > div:last-child {
  align-self: flex-end;
}

.book-header {
  font-weight: 700;
  margin-bottom: 1rem;
}

.book-router-link{
  font-size: 0.9rem;
  margin-left: 0.4rem;
}

.resume-container {
  margin-top: 1rem;
  margin-left: 2rem;
  padding-left: 2rem;
}

</style>