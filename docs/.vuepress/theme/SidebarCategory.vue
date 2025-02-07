<template>
  <div class="custom-sidebar">
    <div class="hovering">
      <p class="vp-sidebar-item vp-sidebar-heading hovering">글</p>
    </div>
    <ul>
      <li><a class="vp-sidebar-item" :href="`/posts/`">모두</a></li>
      <li v-for="category in categories" :key="category">
        <a class="vp-sidebar-item" :href="`/posts/${category.name}/`">{{ toKorean(category.name) }}</a>
      </li>
    </ul>
    <div class="hovering" style="margin-top: 5px">
      <a class="vp-sidebar-item vp-sidebar-heading " href="/books/">책</a>
    </div>
    <div class="hovering" style="margin-top: 10px">
      <a class="vp-sidebar-item vp-sidebar-heading" href="/logs/">짧은 글</a>
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
  padding-top: 15px;
  border-top: 1px solid var(--vp-c-border);
}

ul {
  list-style: none;
  padding-left: 0;
  margin: 0;

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