import isobus from './isobus.js'

export const glossaries = { isobus }

export const glossaryScopes = [
  { id: 'isobus', prefix: '_study/isobus/', page: '/study/isobus/appendix-glossary' },
]

export const seeLabel = (path) => {
  const slug = path.split('/').filter(Boolean).pop() ?? ''
  const chapter = /^(\d+)/.exec(slug)
  if (chapter) return `${Number(chapter[1])}장에서 자세히`
  return slug.startsWith('appendix') ? '부록에서 자세히' : '자세히 보기'
}
