const fs = require('fs').promises;
const path = require('path');

async function addTocToFiles(directory) {
    try {
        const files = await fs.readdir(directory);

        for (const file of files) {
            const fullPath = path.join(directory, file);
            const stat = await fs.stat(fullPath);

            if (stat.isDirectory()) {
                //post 디렉토리만 처리
                if(file !== '_posts') {
                    continue;
                }
                // 재귀적으로 하위 디렉토리 처리
                await addTocToFiles(fullPath);
            } else if (
                file.endsWith('.md') &&
                file !== 'README.md' &&
                file !== 'index.md' &&
                !file.startsWith('.')
            ) {
                let content = await fs.readFile(fullPath, 'utf8');

                // frontmatter가 있는지 확인
                if (content.startsWith('---')) {
                    const secondDash = content.indexOf('---', 3);
                    if (secondDash !== -1) {
                        // frontmatter 다음에 [[toc]] 추가
                        const beforeToc = content.slice(0, secondDash + 3);
                        const afterToc = content.slice(secondDash + 3);

                        // [[toc]]가 이미 있는지 확인
                        if (!content.includes('[[toc]]')) {
                            content = `${beforeToc}\n\n[[toc]]\n${afterToc}`;
                            await fs.writeFile(fullPath, content, 'utf8');
                            console.log(`Added TOC to ${fullPath}`);
                        }
                    }
                } else {
                    // frontmatter가 없는 경우 파일 시작 부분에 [[toc]] 추가
                    if (!content.includes('[[toc]]')) {
                        content = `[[toc]]\n\n${content}`;
                        await fs.writeFile(fullPath, content, 'utf8');
                        console.log(`Added TOC to ${fullPath}`);
                    }
                }
            }
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

async function addHeaderToFiles(directory) {
    try {
        const files = await fs.readdir(directory);

        for (const file of files) {
            const fullPath = path.join(directory, file);
            const stat = await fs.stat(fullPath);

            if (stat.isDirectory()) {
                //post, book 디렉토리만 처리
                if(file !== '_posts' && file !== '_books') {
                    continue;
                }
                // 재귀적으로 하위 디렉토리 처리
                await addHeaderToFiles(fullPath);
            } else if (
                file.endsWith('.md') &&
                file !== 'README.md' &&
                file !== 'index.md' &&
                !file.startsWith('.')
            ) {
                let content = await fs.readFile(fullPath, 'utf8');

                if (content.includes('<Header />')) {
                    // header가 이미 있는 경우 pass
                    continue;
                }

                // frontmatter가 있는지 확인
                if (content.startsWith('---')) {
                    const secondDash = content.indexOf('---', 3);
                    if (secondDash !== -1) {
                        // frontmatter 다음에 <Header /> 추가
                        const beforeHeader = content.slice(0, secondDash + 3);
                        const afterHeader = content.slice(secondDash + 3);

                        content = `${beforeHeader}\n<Header />\n${afterHeader}`;
                        await fs.writeFile(fullPath, content, 'utf8');
                        console.log(`Added Header to ${fullPath}`);
                    }
                } else {
                    content = `<Header />\n\n${content}`;
                    await fs.writeFile(fullPath, content, 'utf8');
                    console.log(`Added Header to ${fullPath}`);
                }
            }
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

async function addFooterToFiles(directory) {
    try {
        const files = await fs.readdir(directory);

        for (const file of files) {
            const fullPath = path.join(directory, file);
            const stat = await fs.stat(fullPath);

            if (stat.isDirectory()) {
                //post, book 디렉토리만 처리
                if(file !== '_posts' && file !== '_books') {
                    continue;
                }
                // 재귀적으로 하위 디렉토리 처리
                await addFooterToFiles(fullPath);
            } else if (
                file.endsWith('.md') &&
                file !== 'README.md' &&
                file !== 'index.md' &&
                !file.startsWith('.')
            ) {
                let content = await fs.readFile(fullPath, 'utf8');

                // footer가 있는지 확인
                if (content.includes('<Footer />')) {
                    // footer가 이미 있는 경우 pass
                    continue;
                }

                // footer 추가
                content = `${content}\n<Footer />`;

                await fs.writeFile(fullPath, content, 'utf8');
                console.log(`Added Header to ${fullPath}`);
            }
        }
    } catch (error) {
        console.error('Error processing files:', error);
    }
}

// 시작 디렉토리 설정 (VuePress 문서 디렉토리)
const docsDirectory = path.join(__dirname, '../docs');

addTocToFiles(docsDirectory)
    .then(() => console.log('Completed adding TOC to markdown files'))
    .catch(error => console.error('Error:', error));

addHeaderToFiles(docsDirectory)
    .then(() => console.log('Completed adding header to markdown files'))
    .catch(error => console.error('Error:', error));

addFooterToFiles(docsDirectory)
    .then(() => console.log('Completed adding footer to markdown files'))
    .catch(error => console.error('Error:', error));