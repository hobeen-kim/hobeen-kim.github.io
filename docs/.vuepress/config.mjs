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
        children: [
          {
            text: '모두',
            link: '/study/',
          },
          {
            text: 'ISOBUS',
            link: '/study/isobus/',
          },
        ],
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
          collapsible: false,
          children: [
            { text: '소개', link: '/study/isobus/' },
            { text: 'CH1. 통신의 기초', link: '/study/isobus/01-communication-basics' },
            { text: 'CH2. CAN 통신 입문', link: '/study/isobus/02-can-intro' },
            { text: 'CH3. CAN 물리 계층', link: '/study/isobus/03-can-physical' },
            { text: 'CH4. CAN 데이터 프레임', link: '/study/isobus/04-can-data-frame' },
            { text: 'CH5. CAN 중재와 우선순위', link: '/study/isobus/05-can-arbitration' },
            { text: 'CH6. CAN 에러 처리', link: '/study/isobus/06-can-error' },
            { text: 'CH7. CAN FD', link: '/study/isobus/07-can-fd' },
          ],
        },
        {
          text: 'SAE J1939',
          collapsible: false,
          children: [
            { text: 'CH8. J1939 입문', link: '/study/isobus/08-j1939-intro' },
            { text: 'CH9. J1939 메시지 구조', link: '/study/isobus/09-j1939-message' },
            { text: 'CH10. J1939 주소 체계', link: '/study/isobus/10-j1939-address' },
            { text: 'CH11. J1939 Transport Protocol', link: '/study/isobus/11-j1939-transport' },
          ],
        },
        {
          text: 'ISOBUS (ISO 11783)',
          collapsible: false,
          children: [
            { text: 'CH12. ISOBUS 개요', link: '/study/isobus/12-isobus-overview' },
            { text: 'CH13. 네트워크 아키텍처', link: '/study/isobus/13-isobus-architecture' },
            { text: 'CH14. 네트워크 관리', link: '/study/isobus/14-isobus-network-mgmt' },
          ],
        },
        {
          text: 'Virtual Terminal (VT)',
          collapsible: false,
          children: [
            { text: 'CH15. VT 기초', link: '/study/isobus/15-vt-basics' },
            { text: 'CH16. VT 오브젝트 풀', link: '/study/isobus/16-vt-object-pool' },
            { text: 'CH17. VT 명령어', link: '/study/isobus/17-vt-commands' },
          ],
        },
        {
          text: 'Task Controller (TC)',
          collapsible: false,
          children: [
            { text: 'CH18. TC 기초', link: '/study/isobus/18-tc-basics' },
            { text: 'CH19. TC 프로세스 데이터', link: '/study/isobus/19-tc-process-data' },
            { text: 'CH20. TC DDOP', link: '/study/isobus/20-tc-ddop' },
          ],
        },
        {
          text: '심화 및 실습',
          collapsible: false,
          children: [
            { text: 'CH21. 기타 기능', link: '/study/isobus/21-isobus-misc' },
            { text: 'CH22. 종합 실습', link: '/study/isobus/22-practice' },
          ],
        },
        {
          text: '부록',
          collapsible: false,
          children: [
            { text: '용어 사전', link: '/study/isobus/appendix-glossary' },
            { text: 'PGN/SPN 목록', link: '/study/isobus/appendix-pgn-spn' },
            { text: 'DDI 목록', link: '/study/isobus/appendix-ddi' },
            { text: '트러블슈팅', link: '/study/isobus/appendix-troubleshooting' },
            { text: '참고 자료', link: '/study/isobus/appendix-references' },
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
