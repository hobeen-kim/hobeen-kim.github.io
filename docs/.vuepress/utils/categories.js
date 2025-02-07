import path from "path";
import {fileURLToPath} from "url";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'

export const getCategories = () => {
    const postsDirectory = path.join(__dirname, relativePath, '../_posts')
    const categories = fs.readdirSync(postsDirectory)

    return categories
        .filter(file => !file.startsWith('README'))
        .map(category => {
            return {
                name: category,
            }
        })
}