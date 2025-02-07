import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'
const dir = '../_books'

export const getBooks = () => {
    const booksDirectory = path.join(__dirname, relativePath, dir)
    const files = fs.readdirSync(booksDirectory)

    return files
        .filter(file => file.endsWith('.md'))
        .filter(file => !file.startsWith('README'))
        .map(file => {
            const fullPath = path.join(booksDirectory, file)
            const fileContents = fs.readFileSync(fullPath, 'utf8')
            const { data, excerpt } = matter(fileContents, { excerpt: true, excerpt_separator: '<--! description -->' })

            const slug = file.replace(/\.md$/, '');

            const refinedExcerpt = excerpt.replace('<Header />', '')

            const thumbnailPath = path.join(__dirname, relativePath, `./public/images/${slug}`)

            //파일 중 thumbnail 을 찾음 (thumbnail.png 또는 thumbnail.jpg)
            if (fs.existsSync(`${thumbnailPath}/thumbnail.png`)) {
                data.thumbnail = `/images/${slug}/thumbnail.png`
            } else if(fs.existsSync(`${thumbnailPath}/thumbnail.jpg`)) {
                data.thumbnail = `/images/${slug}/thumbnail.jpg`
            } else {
                data.thumbnail = '/images/default-thumbnail.png'
            }

            return {
                slug,
                frontmatter: data,
                content: data.content,
                excerpt: refinedExcerpt,
                path: `/books/${file.replace(/\.md$/, '.html')}`
            }
        }).sort((a, b) => (new Date(b.frontmatter.date) - new Date(a.frontmatter.date)))
}