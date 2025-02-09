import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'
const dir = '../_logs/all'

export const getLogs = () => {
    const logsDirectory = path.join(__dirname, relativePath, dir)
    const files = fs.readdirSync(logsDirectory)

    return files
        .filter(file => file.endsWith('.md'))
        .filter(file => !file.startsWith('README'))
        .map(file => {
            const fullPath = path.join(logsDirectory, file)
            const fileContents = fs.readFileSync(fullPath, 'utf8')
            const data = matter(fileContents)

            const slug = file.replace(/\.md$/, '');

            return {
                slug,
                frontmatter: data.data,
                content: data.content,
                images: getImages(slug)
            }
        }).sort((a, b) => (new Date(b.frontmatter.date) - new Date(a.frontmatter.date)))
}

export const getImages = (slug) => {
    const imagesDirectory = path.join(__dirname, relativePath, 'public/images/', slug)
    try {
        fs.accessSync(imagesDirectory, fs.constants.R_OK)
    } catch (err) {
        return []
    }
    const files = fs.readdirSync(imagesDirectory)

    return files
        .filter(file => file.endsWith('.jpg') || file.endsWith('.jpeg') || file.endsWith('.png'))
        .map(file => {
            return {
                name: file,
            }
        })
}