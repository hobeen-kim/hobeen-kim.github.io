// Polyfill localStorage for SSR (fixes @vue/devtools-kit issue)
if (typeof globalThis.localStorage === 'undefined' || typeof globalThis.localStorage.getItem !== 'function') {
  globalThis.localStorage = {
    _data: {},
    getItem(key) { return this._data[key] ?? null },
    setItem(key, value) { this._data[key] = String(value) },
    removeItem(key) { delete this._data[key] },
    clear() { this._data = {} },
    get length() { return Object.keys(this._data).length },
    key(i) { return Object.keys(this._data)[i] ?? null },
  }
}
