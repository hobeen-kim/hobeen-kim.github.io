## 기본 포멧 (frontmatter)

### 1. 글

- Header, Footer, toc 는 빌드 타임 시 붙임

```angular2html
---
title: title 입니다.
date: 2025-02-03
tags:
  - 태그1
  - 태그2
description: description 입니다.
---

```

### 2. 짧은 글
> **주의!**
> 이미지는 넣은 후에 삭제해줘야 함 (이미지박스가 별도로 있음)
```angular2html
---
title: 짧은 글 제목
date: 2025-02-03
tags:
- 태그1
- 태그2
---
(이미지는 넣으면 안됩니다. 넣어도 되지만 이미지박스와 중복됨)
내용입니다.
1. 재밌다.
2. 재미없다?

```

### 3. 책

```angular2html
---
title: 그런 책을 읽었다.
bookName: 그런 책 - 현재의 기억
author: 나나나
date: 2025-02-03
tags:
  - vue
  - blog
---

<Header />

이것은 요약입니다. 저런 책은 최고다!!!
이것은 요약입니다. 저런 책은 최고다!!!
이것은 요약입니다. 저런 책은 최고다!!!
이것은 요약입니다. 저런 책은 최고다!!!
이것은 요약입니다. 저런 책은 최고다!!!
이것은 요약입니다. 저런 책은 최고다!!!
<description />

```

## _posts 에 세분류 추가

### 1. 디렉토리 생성
- docs/_posts/{category}/ 디렉토리 추가
- README.md 파일 추가
- README.md 파일에 아래 내용 추가
```markdown
---
sidebar: false
category: {category}
description: {설명}
---
<PostList/>
```

### 2. 카테고리 한글명 추가
- docs/.vuepress/utils/locale.js 파일에 category 한글명 추가

### 3. 설정 추가
- docs/.vuepress/config.mjs 파일 navbar 추가
```javascript{14,15,16,17}
children: [
    {
        text: '모두',
        link: '/posts/',
    },
    {
        text: '카프카',
        link: '/posts/kafka/',
    },
    {
        text: '스프링',
        link: '/posts/spring/',
    },
    {
        text: '{한글명}',
        link: '/{category}/',
    }
],
```

## navbar 추가

예시 : '기술' navbar 추가 (영어는 tech)

### 1. confg.mjs 파일 내용 추가

```javascript{27,28,29,30}
navbar: [
      {
        text: '글',
        children: [
          {
            text: '모두',
            link: '/posts/',
          },
          {
            text: '카프카',
            link: '/posts/kafka/',
          },
          {
            text: '스프링',
            link: '/posts/spring/',
          },
        ],
      },
      {
        text: '책',  // 포스트 목록 페이지로 이동
        link: '/books/',
      },
      {
        text: '짧은 글',  // 포스트 목록 페이지로 이동
        link: '/logs/',
      },
      {
        text: '기술',  // 포스트 목록 페이지로 이동
        link: '/techs/',
      },
```

### 2. _techs 디렉토리 생성

- docs/_techs/ 디렉토리 추가 및 README.md 파일 추가
- README.md 파일은 /techs/ 로 이동하면 html 로 보이는 파일임
- TechList.vue 는 아래에서 만들 예정

```markdown
---
sidebar: false
category: all
---
<TechList/>
```

그리고 docs/_techs/ 에 테스트용 md 파일 2개 정도 넣기

```markdown
---
title: 테크를 알아보자
date: 2025-02-03
tags:
  - vue
  - blog
---

뷰는 재밌다?

1. 재밌다.
2. 재미없다?


```

### 3. 빌드 파일 생성

- 빌드 시 모든 파일을 읽어서 목록을 만들기 위해 사용

```javascript
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { fileURLToPath } from 'url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const relativePath = '../'
const dir = '../_tech'

export const getTechs = () => {
    const booksDirectory = path.join(__dirname, relativePath, dir)
    const files = fs.readdirSync(techsDirectory)

    return files
        .filter(file => file.endsWith('.md'))
        .filter(file => !file.startsWith('README'))
        .map(file => {
            const fullPath = path.join(techsDirectory, file)
            const fileContents = fs.readFileSync(fullPath, 'utf8')
            const { data, excerpt } = matter(fileContents, { excerpt: true, excerpt_separator: '<!-- more -->' })

            const slug = file.replace(/\.md$/, '');

            return {
                slug,
                frontmatter: data,
                excerpt,
            }
        }).sort((a, b) => (new Date(b.frontmatter.date) - new Date(a.frontmatter.date)))
}
```

> 참고
> - excerpt 는 description 을 의미함

### 4. components 에 해당 vue 파일 추가(List)

- docs/.vuepress/components/TechList.vue 파일 추가
- __TECHS__ 를 사용하여 빌드 시 생성된 전역 변수 사용
  - tech.frontmatter 에 title, date, tags 등 frontmatter 가 있음
  - tech.excerpt 에 description 이 있음
  - tech.slug 에 링크 주소가 있음

```vue
<template>
<div>tech</div>
</template>

<script>
export default {
  name: "TechList",
  data() {
    return {
      techs: __TECHS__ || [], // 빌드 타임에 생성된 전역 변수 사용
    }
  },
}
</script>

<style scoped>

</style>
```

### 5. client.js 에 해당 vue 파일 추가

```javascript{6}
export default defineClientConfig({
    enhance({ app, router, siteData }) {
        app.component('PostList', PostList)
        app.component('LogList', LogList)
        app.component('BookList', BookList) 
        app.component('TechList', TechList) //추가
    },
    layouts: {
        CustomLayout,
    },
    setup() {},
    rootComponents: [],
})
```

### 6. 마무리

- root 에 있는 README.md 에 해당 카테고리에 관한 내용 추가
