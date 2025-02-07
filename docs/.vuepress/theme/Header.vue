<template>
  <header class="page-header">
    <h1 class="title">{{ title }}</h1>
    <div v-if="frontmatter.date" class="meta">
      <time>{{ formatDate(frontmatter.date) }}</time>
    </div>
  </header>
</template>

<script setup>
import { usePageData, usePageFrontmatter } from '@vuepress/client'
import {computed, createApp, onBeforeUnmount, onMounted} from 'vue'
import SidebarCategory from "./SidebarCategory.vue";

const page = usePageData()
const frontmatter = usePageFrontmatter()

// frontmatter의 title이 있으면 그것을 사용하고, 없으면 페이지의 title 사용
const title = computed(() => frontmatter.value.title || page.value.title)

const formatDate = (date) => {
  if (!date) return ''
  return new Date(date).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

onMounted(() => {

  const customSidebar = document.querySelector('.custom-sidebar')

  if (customSidebar) {
    return
  }

  const sidebarEl = document.querySelector('.vp-sidebar')
  if (sidebarEl) {
    const sidebarContainer = document.createElement('div')
    sidebarContainer.classList.add('custom-sidebar')
    sidebarEl.appendChild(sidebarContainer)

    const sidebarApp = createApp(SidebarCategory)
    sidebarApp.mount(sidebarContainer)
  }
})
</script>

<style scoped>
.page-header {
  margin-bottom: 2rem;
  text-align: center;
  padding: 2rem 1rem;
}

.title {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--vp-c-text);
}

.meta {
  font-size: 0.9rem;
  color: var(--vp-c-text-mute);
}
</style>