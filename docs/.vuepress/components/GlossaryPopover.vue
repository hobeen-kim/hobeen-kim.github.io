<template>
  <ClientOnly>
    <Teleport to="body">
      <div
        v-if="active"
        ref="popover"
        class="gl-popover"
        role="dialog"
        :aria-label="active.entry.term"
        tabindex="-1"
        :style="popoverStyle"
      >
        <div class="gl-popover-head">
          <strong class="gl-popover-term">{{ active.entry.term }}</strong>
          <button type="button" class="gl-popover-close" aria-label="닫기" @click="close(true)">×</button>
        </div>
        <p v-if="names" class="gl-popover-names">{{ names }}</p>
        <p class="gl-popover-short">{{ active.entry.short }}</p>
        <div class="gl-popover-links">
          <RouterLink :to="`${active.scope.page}#term-${active.entry.id}`" @click="close()">용어 사전에서 보기</RouterLink>
          <RouterLink v-if="active.entry.see" :to="active.entry.see" @click="close()">{{ seeLabel(active.entry.see) }}</RouterLink>
        </div>
      </div>
    </Teleport>
  </ClientOnly>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import { useRoute } from 'vuepress/client'
import { glossaries, glossaryScopes, seeLabel } from '../data/glossary/index.js'

const GAP = 6
const EDGE = 8

const route = useRoute()
const popover = ref(null)
const active = shallowRef(null)
const position = ref(null)
let viewportWidth = 0

const names = computed(() => {
  const entry = active.value?.entry
  return entry ? [entry.full, entry.ko].filter(Boolean).join(' · ') : ''
})

const popoverStyle = computed(() =>
  position.value
    ? { top: `${position.value.top}px`, left: `${position.value.left}px` }
    : { top: '0px', left: '0px', visibility: 'hidden' },
)

const place = () => {
  const box = popover.value
  if (!active.value || !box) return
  const rect = active.value.el.getBoundingClientRect()
  const { clientWidth, clientHeight } = document.documentElement
  let top = rect.bottom + GAP
  if (top + box.offsetHeight > clientHeight && rect.top - GAP - box.offsetHeight >= 0) {
    top = rect.top - GAP - box.offsetHeight
  }
  const left = Math.max(EDGE, Math.min(rect.left, clientWidth - EDGE - box.offsetWidth))
  position.value = { top: top + window.scrollY, left: left + window.scrollX }
}

const close = (restoreFocus = false) => {
  const current = active.value
  if (!current) return
  current.el.setAttribute('aria-expanded', 'false')
  active.value = null
  if (restoreFocus) current.el.focus()
}

const open = async (el) => {
  const entry = glossaries[el.dataset.g]?.find((item) => item.id === el.dataset.t)
  const scope = glossaryScopes.find((item) => item.id === el.dataset.g)
  if (!entry || !scope) return
  close()
  position.value = null
  active.value = { el, entry, scope }
  el.setAttribute('aria-expanded', 'true')
  await nextTick()
  place()
  // focus() is ignored until the visibility: hidden used for measuring is rendered away.
  await nextTick()
  popover.value?.focus({ preventScroll: true })
}

const toggle = (el) => (active.value?.el === el ? close() : open(el))

const onClick = (event) => {
  const term = event.target.closest?.('.gl-term')
  if (term) toggle(term)
  else if (active.value && !popover.value?.contains(event.target)) close()
}

const onKeydown = (event) => {
  if (event.key === 'Escape' && active.value) {
    close(true)
  } else if ((event.key === 'Enter' || event.key === ' ') && event.target.classList?.contains('gl-term')) {
    event.preventDefault()
    toggle(event.target)
  }
}

const closeOnWidthChange = () => {
  if (window.innerWidth === viewportWidth) return
  viewportWidth = window.innerWidth
  close()
}

watch(() => route.path, () => close())

onMounted(() => {
  viewportWidth = window.innerWidth
  document.addEventListener('click', onClick)
  document.addEventListener('keydown', onKeydown)
  window.addEventListener('resize', closeOnWidthChange)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onClick)
  document.removeEventListener('keydown', onKeydown)
  window.removeEventListener('resize', closeOnWidthChange)
})
</script>
