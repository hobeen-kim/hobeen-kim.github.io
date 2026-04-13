import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'
const dir = '../_study'

export const getStudies = () => {
    const studyDirectory = path.join(__dirname, relativePath, dir)
    const entries = fs.readdirSync(studyDirectory, { withFileTypes: true })

    return entries
        .filter(entry => entry.isDirectory())
        .map(entry => {
            const slug = entry.name
            const readmePath = path.join(studyDirectory, slug, 'README.md')

            if (!fs.existsSync(readmePath)) {
                return null
            }

            const fileContents = fs.readFileSync(readmePath, 'utf8')
            const { data } = matter(fileContents)

            const thumbnailPath = path.join(__dirname, relativePath, `./public/images/${slug}`)

            if (fs.existsSync(`${thumbnailPath}/thumbnail.png`)) {
                data.thumbnail = `/images/${slug}/thumbnail.png`
            } else if (fs.existsSync(`${thumbnailPath}/thumbnail.jpg`)) {
                data.thumbnail = `/images/${slug}/thumbnail.jpg`
            } else {
                data.thumbnail = '/images/default-thumbnail.png'
            }

            return {
                slug,
                frontmatter: data,
                path: `/study/${slug}/`
            }
        })
        .filter(Boolean)
        .sort((a, b) => (new Date(b.frontmatter.date) - new Date(a.frontmatter.date)))
}
