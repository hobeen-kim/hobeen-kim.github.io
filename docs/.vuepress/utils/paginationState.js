// Simple global pagination state (module singleton)
// Stores page per category without relying on URL
// Safe for client-only usage; SSR builds will import the module but state is only used in browser.

const state = {
  // { [category: string]: number }
  pagesByCategory: Object.create(null),
  pageSizeByCategory: Object.create(null),
}

export default {
  getPage(category) {
    if (!category) return 1
    return state.pagesByCategory[category] || 1
  },
  setPage(category, page) {
    if (!category) return
    state.pagesByCategory[category] = Math.max(1, Number(page) || 1)
  },
  getPageSize(category) {
    if (!category) return undefined
    return state.pageSizeByCategory[category]
  },
  setPageSize(category, size) {
    if (!category) return
    const n = Number(size)
    if (Number.isFinite(n) && n > 0) {
      state.pageSizeByCategory[category] = n
    }
  },
  reset(category) {
    if (!category) return
    delete state.pagesByCategory[category]
    delete state.pageSizeByCategory[category]
  }
}
