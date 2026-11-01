const REGEXP_SPECIAL = /[.*+?^${}()|[\]\\]/g
const ALNUM = /[A-Za-z0-9]/
const WORD_CHAR = /[A-Za-z0-9_]/
const HANGUL = /\p{Script=Hangul}/u
const RAW_TAG = /^<(\/?)(a|code|span)(?=[\s/>])/i

// 통신 기초 용어(16진수 등)와 once: 'page'인 흔한 낱말(작업기 등)은
// 절마다가 아니라 페이지에서 한 번만 표시한다
const PAGE_ONCE_CATEGORIES = new Set(['basic'])

const buildMatcher = (entries) => {
  const idByText = new Map()
  const pageOnce = new Set()
  for (const entry of entries) {
    if (PAGE_ONCE_CATEGORIES.has(entry.cat) || entry.once === 'page') pageOnce.add(entry.id)
    for (const text of entry.match ?? []) {
      if (text && !idByText.has(text)) idByText.set(text, entry.id)
    }
  }
  if (idByText.size === 0) return null
  const source = [...idByText.keys()]
    .sort((a, b) => b.length - a.length)
    .map((text) => text.replace(REGEXP_SPECIAL, '\\$&'))
    .join('|')
  return { re: new RegExp(source, 'g'), idByText, pageOnce }
}

const isStandalone = (text, start, end) => {
  const first = text[start]
  const last = text[end - 1]
  const before = text[start - 1] ?? ''
  const after = text[end] ?? ''
  if (ALNUM.test(first) && WORD_CHAR.test(before)) return false
  if (ALNUM.test(last) && WORD_CHAR.test(after)) return false
  return !(HANGUL.test(first) && HANGUL.test(before))
}

const trackRawHtml = (content, raw) => {
  const tag = RAW_TAG.exec(content)
  if (!tag) return
  const closing = tag[1] === '/'
  const name = tag[2].toLowerCase()
  if (name === 'span') {
    if (closing) raw.spans.pop()
    else raw.spans.push(/\bgl-term\b/.test(content))
  } else {
    raw[name] = Math.max(0, raw[name] + (closing ? -1 : 1))
  }
}

const splitText = (token, ctx) => {
  const { re, idByText } = ctx.matcher
  const text = token.content
  const parts = []
  const push = (type, content) => {
    const part = new ctx.Token(type, '', 0)
    part.content = content
    part.level = token.level
    parts.push(part)
  }
  let cursor = 0
  re.lastIndex = 0
  for (let found = re.exec(text); found; found = re.exec(text)) {
    const start = found.index
    const end = start + found[0].length
    if (!isStandalone(text, start, end)) {
      re.lastIndex = start + 1
      continue
    }
    const termId = idByText.get(found[0])
    const shown = ctx.matcher.pageOnce.has(termId) ? ctx.shownOnPage : ctx.shown
    if (shown.has(termId)) continue
    shown.add(termId)
    if (start > cursor) push('text', text.slice(cursor, start))
    push(
      'html_inline',
      `<span class="gl-term" data-g="${ctx.glossaryId}" data-t="${termId}" tabindex="0" role="button" aria-haspopup="dialog" aria-expanded="false">${ctx.escapeHtml(found[0])}</span>`,
    )
    cursor = end
  }
  if (parts.length === 0) return [token]
  if (cursor < text.length) push('text', text.slice(cursor))
  return parts
}

const markInline = (children, ctx) => {
  const out = []
  const raw = { a: 0, code: 0, spans: [] }
  let linkDepth = 0
  for (const child of children) {
    if (child.type === 'link_open') linkDepth++
    else if (child.type === 'link_close') linkDepth--
    else if (child.type === 'html_inline') trackRawHtml(child.content, raw)
    else if (child.type === 'text' && !linkDepth && !raw.a && !raw.code && !raw.spans.includes(true)) {
      out.push(...splitText(child, ctx))
      continue
    }
    out.push(child)
  }
  return out
}

export const glossaryPlugin = (md, { glossaries, scopes }) => {
  const matchers = new Map()
  const matcherFor = (glossaryId) => {
    if (!matchers.has(glossaryId)) matchers.set(glossaryId, buildMatcher(glossaries[glossaryId] ?? []))
    return matchers.get(glossaryId)
  }

  md.core.ruler.push('glossary', (state) => {
    const filePathRelative = state.env?.filePathRelative
    if (!filePathRelative || state.env.frontmatter?.glossary === false) return
    const scope = scopes.find(({ prefix }) => filePathRelative.startsWith(prefix))
    const matcher = scope && matcherFor(scope.id)
    if (!matcher) return

    const ctx = {
      matcher,
      glossaryId: scope.id,
      shown: new Set(),
      shownOnPage: new Set(),
      Token: state.Token,
      escapeHtml: md.utils.escapeHtml,
    }
    let excluded = false
    for (const token of state.tokens) {
      if (token.type === 'heading_open') {
        excluded = true
        if (token.tag === 'h1' || token.tag === 'h2') ctx.shown.clear()
      } else if (token.type === 'th_open') {
        excluded = true
      } else if (token.type === 'heading_close' || token.type === 'th_close') {
        excluded = false
      } else if (token.type === 'inline' && !excluded && token.children) {
        token.children = markInline(token.children, ctx)
      }
    }
  })
}
