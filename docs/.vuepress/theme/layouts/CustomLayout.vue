<template>
  <DefaultLayout>
    <template #sidebar-bottom>
      <SidebarCategory />
    </template>
    <template #page-top>
      <div class="title">
        <h1>{{ $page.title }}</h1>
      </div>
    </template>
    <template #page-bottom>
      <Footer />
    </template>
  </DefaultLayout>
</template>

<script>
import DefaultLayout from '@vuepress/theme-default/lib/client/layouts/Layout.vue'
import SidebarCategory from "../SidebarCategory.vue";
import Footer from "../Footer.vue";

export default {
  name: 'Layout',
  components: {
    SidebarCategory,
    DefaultLayout,
    Footer,
  }
}
</script>

<style>
.title {
  text-align: center;
  margin-top: 50px;
  font-weight: 700;
}
</style>