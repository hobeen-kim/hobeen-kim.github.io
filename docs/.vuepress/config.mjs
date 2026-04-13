import { viteBundler } from '@vuepress/bundler-vite'
import { defaultTheme } from '@vuepress/theme-default'
import { defineUserConfig } from 'vuepress'
import {getPosts} from "./utils/posts.js";
import path from 'path'
import {getCategories} from "./utils/categories.js";
import {getLogs} from "./utils/logs.js";
import {getBooks} from "./utils/books.js";
import {getStudies} from "./utils/studies.js";

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
        text: '책',
        link: '/books/',
      },
      {
        text: '짧은 글',
        link: '/logs/',
      },
      {
        text: '공부하기',
        link: '/study/',
      },
      {
        text: '이력서',
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
    sidebar: {
      '/study/isobus/': [
        {
          text: '통신과 CAN 기초',
          children: [
            '/study/isobus/',
            '/study/isobus/01-communication-basics',
            '/study/isobus/02-can-intro',
            '/study/isobus/03-can-physical',
            '/study/isobus/04-can-data-frame',
            '/study/isobus/05-can-arbitration',
            '/study/isobus/06-can-error',
            '/study/isobus/07-can-fd',
          ],
        },
        {
          text: 'SAE J1939',
          children: [
            '/study/isobus/08-j1939-intro',
            '/study/isobus/09-j1939-message',
            '/study/isobus/10-j1939-address',
            '/study/isobus/11-j1939-transport',
          ],
        },
        {
          text: 'ISOBUS (ISO 11783)',
          children: [
            '/study/isobus/12-isobus-overview',
            '/study/isobus/13-isobus-architecture',
            '/study/isobus/14-isobus-network-mgmt',
          ],
        },
        {
          text: 'Virtual Terminal (VT)',
          children: [
            '/study/isobus/15-vt-basics',
            '/study/isobus/16-vt-object-pool',
            '/study/isobus/17-vt-commands',
          ],
        },
        {
          text: 'Task Controller (TC)',
          children: [
            '/study/isobus/18-tc-basics',
            '/study/isobus/19-tc-process-data',
            '/study/isobus/20-tc-ddop',
          ],
        },
        {
          text: '심화 및 실습',
          children: [
            '/study/isobus/21-isobus-misc',
            '/study/isobus/22-practice',
          ],
        },
        {
          text: '부록',
          children: [
            '/study/isobus/appendix-glossary',
            '/study/isobus/appendix-pgn-spn',
            '/study/isobus/appendix-ddi',
            '/study/isobus/appendix-troubleshooting',
            '/study/isobus/appendix-references',
          ],
        },
      ],
    },
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
      },
      ssr: {
        noExternal: ['@vue/devtools-api', '@vue/devtools-kit'],
      },
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
  extendsMarkdown: (md) => {
    const origFence = md.renderer.rules.fence
    md.renderer.rules.fence = (tokens, idx, options, env, self) => {
      const token = tokens[idx]
      if (token.info.trim() === 'mermaid') {
        return `<pre class="mermaid">${md.utils.escapeHtml(token.content)}</pre>`
      }
      return origFence(tokens, idx, options, env, self)
    }
  },
  // 전역 변수로 포스트 데이터 제공
  define: {
    __POSTS__: getPosts(),
    __CATEGORIES__: getCategories(),
    __LOGS__: getLogs(),
    __BOOKS__: getBooks(),
    __STUDIES__: getStudies(),
  }
})
