import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'

export const getPosts = () => {
    const postsDirectory = path.join(__dirname, relativePath, '../_posts')
    const categories = fs.readdirSync(postsDirectory)

    const posts = [];

    categories
        .filter(file => !file.startsWith('README'))
        .forEach(category => {
            const categoryPosts = getPostsByCategory(category)
            posts.push(...categoryPosts)
        })

    return posts
        .sort((a, b) => (new Date(b.frontmatter.date) - new Date(a.frontmatter.date)))
}

const getPostsByCategory = (category) => {
    const postsDirectory = path.join(__dirname, relativePath, '../_posts', category)
    const files = fs.readdirSync(postsDirectory)

    return files
        .filter(file => file.endsWith('.md'))
        .filter(file => !file.startsWith('README'))
        .map(file => {
            const fullPath = path.join(postsDirectory, file)
            const fileContents = fs.readFileSync(fullPath, 'utf8')
            const { data } = matter(fileContents)

            const slug = file.replace(/\.md$/, '');
            // 썸네일 이미지 경로
            const thumbnailPath = path.join(__dirname, relativePath, `./public/images/${slug}`)

            //파일 중 thumbnail 을 찾음 (thumbnail.png 또는 thumbnail.jpg)
            if (fs.existsSync(`${thumbnailPath}/thumbnail.png`)) {
                data.thumbnail = `/images/${slug}/thumbnail.png`
            } else if(fs.existsSync(`${thumbnailPath}/thumbnail.jpg`)) {
                data.thumbnail = `/images/${slug}/thumbnail.jpg`
            } else {
                data.thumbnail = `/images/${category}/default-thumbnail.png`
            }

            return {
                slug,
                frontmatter: data,
                excerpt: data.description,
                category,
                path: `/posts/${category}/${file.replace(/\.md$/, '.html')}`
            }
        })
}