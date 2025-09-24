import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import { getPosts } from '../docs/.vuepress/utils/posts.js'
import { getLogs } from '../docs/.vuepress/utils/logs.js'
import { getBooks } from '../docs/.vuepress/utils/books.js'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// 사이트 기본 URL
const SITE_URL = 'https://hobeen-kim.github.io'

// 정적 페이지들
const STATIC_PAGES = [
  { url: '/', priority: '1.0', changefreq: 'weekly' },
  { url: '/resume/', priority: '1.0', changefreq: 'monthly' },
  { url: '/posts/', priority: '0.9', changefreq: 'weekly' },
  { url: '/books/', priority: '0.8', changefreq: 'monthly' },
  { url: '/logs/', priority: '0.8', changefreq: 'weekly' },
  // 카테고리 페이지들
  { url: '/posts/culture/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/tech/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/java/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/spring/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/infra/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/kafka/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/database/', priority: '0.7', changefreq: 'weekly' },
  { url: '/posts/conference/', priority: '0.7', changefreq: 'weekly' },
]

function formatDate(date) {
  if (!date) return new Date().toISOString().split('T')[0]
  return new Date(date).toISOString().split('T')[0]
}

function generateSitemap() {
  console.log('🚀 Sitemap 생성을 시작합니다...')
  
  // 데이터 수집
  const posts = getPosts()
  const books = getBooks()
  
  console.log(`📝 포스트: ${posts.length}개`)
  console.log(`📚 책: ${books.length}개`)
  
  let sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
`

  // 정적 페이지 추가
  STATIC_PAGES.forEach(page => {
    sitemap += `  <url>
    <loc>${SITE_URL}${page.url}</loc>
    <lastmod>${formatDate()}</lastmod>
    <changefreq>${page.changefreq}</changefreq>
    <priority>${page.priority}</priority>
  </url>
`
  })

  // 포스트 페이지 추가
  posts.forEach(post => {
    sitemap += `  <url>
    <loc>${SITE_URL}${post.path}</loc>
    <lastmod>${formatDate(post.frontmatter.date)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.6</priority>
  </url>
`
  })

  // 책 페이지 추가
  books.forEach(book => {
    sitemap += `  <url>
    <loc>${SITE_URL}${book.path}</loc>
    <lastmod>${formatDate(book.frontmatter.date)}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.5</priority>
  </url>
`
  })

  sitemap += `</urlset>`

  // sitemap.xml 파일 저장 (public 폴더에)
  const sitemapPath = path.join(__dirname, '../docs/.vuepress/public/sitemap.xml')
  fs.writeFileSync(sitemapPath, sitemap, 'utf8')
  
  console.log(`✅ Sitemap이 생성되었습니다: ${sitemapPath}`)
  console.log(`🌐 총 ${STATIC_PAGES.length + posts.length + books.length}개의 URL이 포함되었습니다.`)
  
  return sitemapPath
}

// 스크립트가 직접 실행될 때
if (import.meta.url === `file://${process.argv[1]}`) {
  try {
    generateSitemap()
  } catch (error) {
    console.error('❌ Sitemap 생성 중 오류가 발생했습니다:', error)
    process.exit(1)
  }
}

export { generateSitemap }
