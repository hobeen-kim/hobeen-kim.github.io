export const nodes = [
  // Root
  { id: 'study-root', label: '공부', size: 44, status: 'active', link: null },

  // === 스마트농업 브랜치 ===
  { id: 'smart-agriculture', label: '스마트농업', size: 36, status: 'active', link: '/study/smart-agriculture/' },
  { id: 'isobus', label: 'ISOBUS', size: 28, status: 'active', link: '/study/isobus/' },
  { id: 'can-j1939', label: 'CAN / J1939', size: 22, status: 'planned', link: null },
  { id: 'precision-ag', label: '정밀농업', size: 26, status: 'planned', link: null },
  { id: 'autonomous', label: '자율주행\n농기계', size: 22, status: 'planned', link: null },
  { id: 'embedded', label: '임베디드\n시스템', size: 22, status: 'planned', link: null },
  { id: 'isoxml', label: 'ISOXML', size: 22, status: 'planned', link: null },
  { id: 'fmis', label: 'FMIS', size: 20, status: 'planned', link: null },
  { id: 'agri-iot', label: '농업 IoT', size: 24, status: 'planned', link: null },
  { id: 'telematics', label: '텔레매틱스', size: 20, status: 'planned', link: null },
  { id: 'rtk-gps', label: 'RTK-GPS', size: 22, status: 'planned', link: null },
  { id: 'crop-analysis', label: '작물 분석', size: 20, status: 'planned', link: null },

  // === 소프트웨어 브랜치 ===
  { id: 'software', label: '소프트웨어', size: 36, status: 'active', link: null },
  // 곁가지 (depth 2)
  { id: 'database', label: '데이터베이스', size: 26, status: 'active', link: '/study/database/' },
  { id: 'backend', label: '백엔드', size: 26, status: 'planned', link: null },
  { id: 'infra', label: '인프라\n/ DevOps', size: 24, status: 'planned', link: null },
  { id: 'architecture', label: '소프트웨어\n아키텍처', size: 24, status: 'planned', link: null },
  { id: 'network', label: '네트워크', size: 22, status: 'planned', link: null },
  { id: 'os', label: '운영체제', size: 22, status: 'planned', link: null },
  // depth 3 — 데이터베이스
  { id: 'rdb', label: 'RDB', size: 20, status: 'planned', link: null },
  { id: 'nosql', label: 'NoSQL', size: 20, status: 'planned', link: null },
  { id: 'db-tuning', label: 'DB 튜닝', size: 18, status: 'planned', link: null },
  // depth 3 — 백엔드
  { id: 'spring', label: 'Spring', size: 22, status: 'planned', link: null },
  { id: 'api-design', label: 'API 설계', size: 20, status: 'planned', link: null },
  { id: 'messaging', label: '메시징\n(Kafka)', size: 20, status: 'planned', link: null },
  // depth 3 — 인프라
  { id: 'aws', label: 'AWS', size: 20, status: 'planned', link: null },
  { id: 'kubernetes', label: 'Kubernetes', size: 20, status: 'planned', link: null },
  { id: 'cicd', label: 'CI / CD', size: 18, status: 'planned', link: null },
  // depth 2 — 데이터 엔지니어링 (소프트웨어 하위)
  { id: 'data-engineering', label: '데이터\n엔지니어링', size: 24, status: 'planned', link: null },

  // === AI 브랜치 ===
  { id: 'ai', label: 'AI', size: 36, status: 'active', link: null },
  { id: 'machine-learning', label: '머신러닝', size: 28, status: 'planned', link: null },
  { id: 'deep-learning', label: '딥러닝', size: 24, status: 'planned', link: null },
  { id: 'computer-vision', label: '컴퓨터 비전', size: 24, status: 'planned', link: null },
  { id: 'time-series', label: '시계열 예측', size: 22, status: 'planned', link: null },
  { id: 'mlops', label: 'MLOps', size: 22, status: 'planned', link: null },
]

export const edges = [
  // Root → 대분류
  { source: 'study-root', target: 'smart-agriculture' },
  { source: 'study-root', target: 'software' },

  // === 스마트농업 ===
  { source: 'smart-agriculture', target: 'isobus' },
  { source: 'smart-agriculture', target: 'precision-ag' },
  { source: 'smart-agriculture', target: 'agri-iot' },
  { source: 'smart-agriculture', target: 'autonomous' },
  { source: 'isobus', target: 'can-j1939' },
  { source: 'isobus', target: 'isoxml' },
  { source: 'isobus', target: 'embedded' },
  { source: 'precision-ag', target: 'rtk-gps' },
  { source: 'precision-ag', target: 'fmis' },
  { source: 'precision-ag', target: 'crop-analysis' },
  { source: 'agri-iot', target: 'telematics' },
  { source: 'autonomous', target: 'rtk-gps' },
  { source: 'isoxml', target: 'fmis' },

  // === 소프트웨어 ===
  { source: 'software', target: 'database' },
  { source: 'software', target: 'backend' },
  { source: 'software', target: 'infra' },
  { source: 'software', target: 'architecture' },
  { source: 'software', target: 'network' },
  { source: 'software', target: 'os' },
  // 데이터베이스 하위
  { source: 'database', target: 'rdb' },
  { source: 'database', target: 'nosql' },
  { source: 'database', target: 'db-tuning' },
  // 백엔드 하위
  { source: 'backend', target: 'spring' },
  { source: 'backend', target: 'api-design' },
  { source: 'backend', target: 'messaging' },
  // 인프라 하위
  { source: 'infra', target: 'aws' },
  { source: 'infra', target: 'kubernetes' },
  { source: 'infra', target: 'cicd' },
  // 데이터 엔지니어링 (소프트웨어 하위)
  { source: 'software', target: 'data-engineering' },

  // === AI ===
  { source: 'study-root', target: 'ai' },
  { source: 'ai', target: 'machine-learning' },
  { source: 'ai', target: 'computer-vision' },
  { source: 'ai', target: 'time-series' },
  { source: 'ai', target: 'mlops' },
  { source: 'machine-learning', target: 'deep-learning' },
  // 교차 엣지 (스마트농업 ↔ AI)
  { source: 'crop-analysis', target: 'computer-vision' },
  { source: 'crop-analysis', target: 'time-series' },
]
