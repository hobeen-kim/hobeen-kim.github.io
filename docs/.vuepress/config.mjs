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
      '/study/smart-agriculture/': [
        {
          text: '스마트농업 개론',
          collapsible: false,
          children: [
            { text: '소개', link: '/study/smart-agriculture/' },
            { text: 'CH1. 스마트농업이란', link: '/study/smart-agriculture/01-what-is-smart-agriculture' },
            { text: 'CH2. 기술 지도', link: '/study/smart-agriculture/02-technology-map' },
          ],
        },
        {
          text: '센싱과 데이터',
          collapsible: false,
          children: [
            { text: 'CH3. 농업 IoT와 센서', link: '/study/smart-agriculture/03-iot-sensors' },
            { text: 'CH4. 항공·위성 센싱', link: '/study/smart-agriculture/04-aerial-satellite' },
            { text: 'CH5. 측위와 자동조향', link: '/study/smart-agriculture/05-gnss-autosteer' },
          ],
        },
        {
          text: '통신과 제어',
          collapsible: false,
          children: [
            { text: 'CH6. 농기계 통신', link: '/study/smart-agriculture/06-machine-communication' },
            { text: 'CH7. 정밀농업', link: '/study/smart-agriculture/07-precision-agriculture' },
            { text: 'CH8. 스마트 관개', link: '/study/smart-agriculture/08-smart-irrigation' },
          ],
        },
        {
          text: '자동화와 지능화',
          collapsible: false,
          children: [
            { text: 'CH9. 자율주행 농기계', link: '/study/smart-agriculture/09-autonomous-machinery' },
            { text: 'CH10. 농업 로보틱스', link: '/study/smart-agriculture/10-agri-robotics' },
            { text: 'CH11. AI와 농업', link: '/study/smart-agriculture/11-ai-agriculture' },
          ],
        },
        {
          text: '플랫폼과 생태계',
          collapsible: false,
          children: [
            { text: 'CH12. 농업 데이터', link: '/study/smart-agriculture/12-agri-data' },
            { text: 'CH13. 스마트팜 개요', link: '/study/smart-agriculture/13-smart-farm' },
            { text: 'CH14. 생태계와 표준화', link: '/study/smart-agriculture/14-ecosystem' },
          ],
        },
      ],
      '/study/database/': [
        {
          text: '기초',
          collapsible: false,
          children: [
            { text: '소개', link: '/study/database/' },
            { text: 'CH1. 데이터베이스란', link: '/study/database/01-what-is-database' },
            { text: 'CH2. 관계형 모델', link: '/study/database/02-relational-model' },
          ],
        },
        {
          text: 'SQL',
          collapsible: false,
          children: [
            { text: 'CH3. DDL과 DCL', link: '/study/database/03-ddl-dcl' },
            { text: 'CH4. SQL 기초', link: '/study/database/04-sql-basics' },
            { text: 'CH5. JOIN과 서브쿼리', link: '/study/database/05-join-subquery' },
            { text: 'CH6. 집계와 윈도우 함수', link: '/study/database/06-aggregation-window' },
            { text: 'CH7. DB 객체', link: '/study/database/07-db-objects' },
          ],
        },
        {
          text: '설계',
          collapsible: false,
          children: [
            { text: 'CH8. 정규화', link: '/study/database/08-normalization' },
            { text: 'CH9. 데이터 모델링', link: '/study/database/09-data-modeling' },
          ],
        },
        {
          text: '내부 구조',
          collapsible: false,
          children: [
            { text: 'CH10. 스토리지 엔진', link: '/study/database/10-storage-engine' },
            { text: 'CH11. 트랜잭션', link: '/study/database/11-transaction' },
            { text: 'CH12. 실행 계획', link: '/study/database/12-execution-plan' },
          ],
        },
        {
          text: '튜닝',
          collapsible: false,
          children: [
            { text: 'CH13. 인덱스 전략', link: '/study/database/13-index-strategy' },
            { text: 'CH14. 쿼리 튜닝', link: '/study/database/14-query-tuning' },
          ],
        },
        {
          text: '운영과 확장',
          collapsible: false,
          children: [
            { text: 'CH15. 운영과 보안', link: '/study/database/15-operation-security' },
            { text: 'CH16. 분산 데이터베이스', link: '/study/database/16-distributed-db' },
            { text: 'CH17. 데이터 웨어하우스', link: '/study/database/17-data-warehouse' },
          ],
        },
      ],
      '/study/db-optimization/': [
        {
          text: '쿼리 최적화',
          collapsible: false,
          children: [
            { text: '소개', link: '/study/db-optimization/' },
            { text: 'CH1. 슬로우 쿼리 진단', link: '/study/db-optimization/01-slow-query' },
            { text: 'CH2. 인덱스가 안 타는 경우', link: '/study/db-optimization/02-index-not-used' },
            { text: 'CH3. N+1 쿼리 문제', link: '/study/db-optimization/03-n-plus-one' },
            { text: 'CH4. 쿼리 리팩토링', link: '/study/db-optimization/04-query-refactoring' },
          ],
        },
        {
          text: '스키마 최적화',
          collapsible: false,
          children: [
            { text: 'CH5. Soft Delete', link: '/study/db-optimization/05-soft-delete' },
            { text: 'CH6. 반정규화 실전', link: '/study/db-optimization/06-denormalization' },
          ],
        },
        {
          text: '인프라 최적화',
          collapsible: false,
          children: [
            { text: 'CH7. 캐시와 Redis', link: '/study/db-optimization/07-cache-redis' },
            { text: 'CH8. 커넥션 관리', link: '/study/db-optimization/08-connection-pool' },
            { text: 'CH9. DB 마이그레이션', link: '/study/db-optimization/09-migration' },
          ],
        },
        {
          text: '모니터링과 운영',
          collapsible: false,
          children: [
            { text: 'CH10. 모니터링 지표', link: '/study/db-optimization/10-monitoring' },
            { text: 'CH11. PostgreSQL 운영', link: '/study/db-optimization/11-postgresql' },
            { text: 'CH12. MySQL InnoDB', link: '/study/db-optimization/12-mysql-innodb' },
          ],
        },
      ],
      '/study/ai-agent-workflow/': [
        {
          text: '원칙',
          collapsible: false,
          children: [
            { text: '소개', link: '/study/ai-agent-workflow/' },
            { text: 'CH1. 대원칙', link: '/study/ai-agent-workflow/01-core-principles' },
          ],
        },
        {
          text: '에이전트 설계',
          collapsible: false,
          children: [
            { text: 'CH2. 어떤 에이전트를 만들 것인가', link: '/study/ai-agent-workflow/02-agent-design' },
            { text: 'CH3. 에이전트 간 소통', link: '/study/ai-agent-workflow/03-communication' },
            { text: 'CH4. TypeScript 레지스트리 훅 구현', link: '/study/ai-agent-workflow/04-registry-hook' },
            { text: 'CH5. 에이전트 정의 파일 작성법', link: '/study/ai-agent-workflow/05-agent-definition-files' },
          ],
        },
        {
          text: '운영',
          collapsible: false,
          children: [
            { text: 'CH6. 문서화 체계', link: '/study/ai-agent-workflow/06-documentation' },
            { text: 'CH7. 에이전트 헌법', link: '/study/ai-agent-workflow/07-constitution' },
            { text: 'CH8. Scaffold', link: '/study/ai-agent-workflow/08-scaffold' },
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
