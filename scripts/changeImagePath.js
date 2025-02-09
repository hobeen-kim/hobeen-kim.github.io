const fs = require('fs').promises;
const path = require('path');

async function imagePathChange(directory) {
    try {
        const files = await fs.readdir(directory);

        for (const file of files) {
            const fullPath = path.join(directory, file);
            const stat = await fs.stat(fullPath);

            if (stat.isDirectory()) {
                //post, books, logs 디렉토리만 처리
                if(!file.includes('_posts') && !file.includes('_books') && !file.includes('_logs')) {
                    continue;
                }
                // 재귀적으로 하위 디렉토리 처리
                await imagePathChange(fullPath);
            } else if (
                file.endsWith('.md') &&
                !file.startsWith('.')
            ) {
                let content = await fs.readFile(fullPath, 'utf8');

                content = content.replace('../../.vuepress/public', '');

                await fs.writeFile(fullPath, content, 'utf8');

                console.log(`changed image path in ${fullPath}`);
            }
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

// 시작 디렉토리 설정 (VuePress 문서 디렉토리)
const docsDirectory = path.join(__dirname, '../docs');

imagePathChange(docsDirectory)
    .then(() => console.log('Completed adding TOC to markdown files'))
    .catch(error => console.error('Error:', error));