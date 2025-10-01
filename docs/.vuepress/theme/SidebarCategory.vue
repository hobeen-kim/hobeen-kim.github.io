<template>
  <div class="custom-sidebar">
    <div class="hovering">
      <p class="custom-sidebar-item custom-sidebar-heading">글</p>
      <ul>
        <li><a class="custom-sidebar-item vp-sidebar-children" :href="`/posts/`">모두</a></li>
        <li v-for="category in categories" :key="category">
          <a class="custom-sidebar-item custom-sidebar-children" :href="`/posts/${category.name}/`">{{ toKorean(category.name) }}</a>
        </li>
      </ul>
    </div>
    <div class="custom-sidebar-heading hovering" style="margin-top: 5px">
      <a class="custom-sidebar-item" href="/books/">책</a>
    </div>
    <div class="custom-sidebar-heading  hovering" style="margin-top: 10px">
      <a class="custom-sidebar-item" href="/logs/">짧은 글</a>
    </div>
    <div class="custom-sidebar-heading  hovering" style="margin-top: 10px">
      <a class="custom-sidebar-item" href="/resume/">이력서</a>
    </div>
  </div>
</template>

<script>
import ko from "../utils/locale"

export default {
  name: "SidebarCategory",
  data() {
    return {
      categories: __CATEGORIES__ || [], // 빌드 타임에 생성된 전역 변수 사용
    }
  },
  methods: {
    toKorean(category) {
      return ko[category]
    }
  }
}
</script>


<style scoped>

.custom-sidebar {
  margin-left: 15px;
  margin-right: 15px;
  margin-bottom: 70px;
  padding-top: 15px;
  border-top: 1px solid var(--vp-c-border);
}

.custom-sidebar-item {
  padding: 0.3rem 1.5rem 0.3rem 1.25rem;
  color: var(--vp-c-text);
}

.custom-sidebar-heading {
  box-sizing: border-box;
  width: 100%;
  font-weight: 700;
  font-size: 1.1em;
  transition: color 0.15s ease;
  padding-top: 0.2rem;
  padding-bottom: 0.2rem;
}

ul {
  list-style: none;

  :hover {
    cursor: pointer;
    color: var(--vp-c-accent-hover);
  }
}

.hovering {
  :hover {
    cursor: pointer;
    color: var(--vp-c-accent-hover);
  }
}
</style>