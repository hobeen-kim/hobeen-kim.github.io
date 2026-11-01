<template>
  <dl class="gl-list">
    <div
      v-for="item in items"
      :key="item.id"
      class="gl-entry"
      :class="{ 'is-target': targetId === item.id }"
    >
      <dt class="gl-entry-term">
        <span :id="`term-${item.id}`" class="gl-entry-anchor"></span>{{ item.term }}
        <span v-if="item.full || item.ko" class="gl-entry-names">{{ [item.full, item.ko].filter(Boolean).join(' · ') }}</span>
      </dt>
      <dd class="gl-entry-short">{{ item.short }}</dd>
      <dd v-if="item.detail" class="gl-entry-detail">{{ item.detail }}</dd>
      <dd v-if="item.see" class="gl-entry-see">
        <RouterLink :to="item.see">{{ seeLabel(item.see) }}</RouterLink>
      </dd>
    </div>
  </dl>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vuepress/client'
import { glossaries, seeLabel } from '../data/glossary/index.js'

const props = defineProps({
  g: { type: String, default: 'isobus' },
  cat: { type: String, default: '' },
})

const route = useRoute()
const targetId = ref(null)

const items = computed(() =>
  (glossaries[props.g] ?? [])
    .filter((item) => !props.cat || item.cat === props.cat)
    .sort((a, b) => a.term.localeCompare(b.term, 'en', { sensitivity: 'base' })),
)

onMounted(() => {
  // The default theme rewrites the hash to the active heading while scrolling, so keep the last term hash.
  watch(
    () => route.hash,
    (hash) => {
      if (hash.startsWith('#term-')) targetId.value = hash.slice('#term-'.length)
    },
    { immediate: true },
  )
})
</script>
