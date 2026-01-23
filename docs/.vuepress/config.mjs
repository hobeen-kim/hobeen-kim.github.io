import { viteBundler } from '@vuepress/bundler-vite'
import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'
import {getPosts} from "./utils/posts.js";
import path from 'path'
import {getCategories} from "./utils/categories.js";
import {getLogs} from "./utils/logs.js";
import {getBooks} from "./utils/books.js";

const theme = {
  extends: defaultTheme({
    // 네비게이션 바 설정
    navbar: [
      {
        text: '글',
        children: [
          {
            text: '모두',
            link: '/posts/',
          },
          {
            text: '아키텍처',
            link: '/posts/architecture/',
          },
          {
            text: '기술',
            link: '/posts/tech/',
          },
          {
            text: '자바',
            link: '/posts/java/',
          },
          {
            text: '스프링',
            link: '/posts/spring/',
          },
          {
            text: '인프라',
            link: '/posts/infra/',
          },
          {
            text: '카프카',
            link: '/posts/kafka/',
          },
          {
            text: '데이터베이스',
            link: '/posts/database/',
          },
          {
            text: '컨퍼런스',
            link: '/posts/conference/',
          },
          {
            text: '개발 문화',
            link: '/posts/culture/',
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
        text: '이력서',  // 포스트 목록 페이지로 이동
        link: '/resume/',
      },
    ],
    // 테마 설정 추가
    colorMode: 'auto',
    colorModeSwitch: true,
    //favicon
    head: [
      ['link', { rel: 'icon', href: '/images/favicon.ico' }]
    ],
    sidebarDepth: 0,
    lastUpdated: false,
    contributors: false,
  }),
  //custom layout
  layout: {
    CustomLayout: path.resolve(__dirname, './theme/layouts/CustomLayout.vue'),
  },
}

export default defineUserConfig({
  // 블로그 제목과 설명
  title: '앤디 블로그',
  description: '안녕하세요! 소프트웨어 엔지니어 앤디입니다.',
  theme:theme,
  markdown: {
    headers: {
      level: [1, 2, 3]  // h1부터 포함
    },
    toc: {
      level: [1, 2, 3]  // h2
    }
  },
  bundler: viteBundler({
    viteOptions: {
      optimizeDeps: {
        include: ['html2pdf.js']
      },
      build: {
        rollupOptions: {
        }
      }
    },
    vuePluginOptions: {},
  }),
  // 블로그 플러그인 설정
  plugins: [
    [
      '@vuepress/register-components',
      {
        componentsDir: path.resolve(__dirname, './theme/'),
      },
    ],
  ],
  // 전역 변수로 포스트 데이터 제공
  define: {
    __POSTS__: getPosts(),
    __CATEGORIES__: getCategories(),
    __LOGS__: getLogs(),
    __BOOKS__: getBooks(),
  }
})
