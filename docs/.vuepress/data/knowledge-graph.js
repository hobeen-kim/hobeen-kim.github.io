// 좌표는 비율(0~1) 기반. 컴포넌트에서 width/height에 곱해서 사용.
export const nodes = [
  // Root — 중앙 상단
  { id: 'study-root', label: '공부', size: 44, status: 'active', link: null, x: 0.50, y: 0.08 },

  // === 스마트농업 — 좌측 ===
  { id: 'smart-agriculture', label: '스마트농업', size: 36, status: 'active', link: '/study/smart-agriculture/', x: 0.18, y: 0.22 },
  { id: 'isobus', label: 'ISOBUS', size: 28, status: 'active', link: '/study/isobus/', x: 0.06, y: 0.40 },
  { id: 'can-j1939', label: 'CAN / J1939', size: 22, status: 'planned', link: null, x: 0.03, y: 0.56 },
  { id: 'embedded', label: '임베디드\n시스템', size: 22, status: 'planned', link: null, x: 0.14, y: 0.56 },
  { id: 'isoxml', label: 'ISOXML', size: 22, status: 'planned', link: null, x: 0.08, y: 0.70 },
  { id: 'precision-ag', label: '정밀농업', size: 26, status: 'planned', link: null, x: 0.22, y: 0.40 },
  { id: 'rtk-gps', label: 'RTK-GPS', size: 22, status: 'planned', link: null, x: 0.30, y: 0.56 },
  { id: 'fmis', label: 'FMIS', size: 20, status: 'planned', link: null, x: 0.18, y: 0.70 },
  { id: 'crop-analysis', label: '작물 분석', size: 20, status: 'planned', link: null, x: 0.30, y: 0.70 },
  { id: 'agri-iot', label: '농업 IoT', size: 24, status: 'planned', link: null, x: 0.10, y: 0.22 },
  { id: 'telematics', label: '텔레매틱스', size: 20, status: 'planned', link: null, x: 0.03, y: 0.30 },
  { id: 'autonomous', label: '자율주행\n농기계', size: 22, status: 'planned', link: null, x: 0.32, y: 0.30 },

  // === 소프트웨어 — 우측 ===
  { id: 'software', label: '소프트웨어', size: 36, status: 'active', link: null, x: 0.82, y: 0.22 },
  { id: 'database', label: '데이터베이스', size: 26, status: 'active', link: '/study/database/', x: 0.70, y: 0.40 },
  { id: 'rdb', label: 'RDB', size: 20, status: 'planned', link: null, x: 0.62, y: 0.56 },
  { id: 'nosql', label: 'NoSQL', size: 20, status: 'planned', link: null, x: 0.72, y: 0.56 },
  { id: 'db-tuning', label: 'DB 성능\n최적화', size: 22, status: 'active', link: '/study/db-optimization/', x: 0.67, y: 0.68 },
  { id: 'backend', label: '백엔드', size: 26, status: 'planned', link: null, x: 0.88, y: 0.40 },
  { id: 'spring', label: 'Spring', size: 22, status: 'planned', link: null, x: 0.82, y: 0.56 },
  { id: 'api-design', label: 'API 설계', size: 20, status: 'planned', link: null, x: 0.92, y: 0.56 },
  { id: 'messaging', label: '메시징\n(Kafka)', size: 20, status: 'planned', link: null, x: 0.87, y: 0.68 },
  { id: 'infra', label: '인프라\n/ DevOps', size: 24, status: 'planned', link: null, x: 0.97, y: 0.30 },
  { id: 'aws', label: 'AWS', size: 20, status: 'planned', link: null, x: 0.95, y: 0.44 },
  { id: 'kubernetes', label: 'Kubernetes', size: 20, status: 'planned', link: null, x: 0.97, y: 0.56 },
  { id: 'cicd', label: 'CI / CD', size: 18, status: 'planned', link: null, x: 0.97, y: 0.68 },
  { id: 'architecture', label: '소프트웨어\n아키텍처', size: 24, status: 'planned', link: null, x: 0.78, y: 0.30 },
  { id: 'auth', label: '인증 / 인가', size: 24, status: 'planned', link: null, x: 0.60, y: 0.14 },
  { id: 'oauth', label: 'OAuth\n/ OIDC', size: 26, status: 'active', link: '/study/oauth/', x: 0.52, y: 0.20 },
  { id: 'keycloak', label: 'Keycloak', size: 24, status: 'active', link: '/study/keycloak/', x: 0.45, y: 0.27 },
  { id: 'network', label: '네트워크', size: 22, status: 'planned', link: null, x: 0.70, y: 0.22 },
  { id: 'os', label: '운영체제', size: 22, status: 'planned', link: null, x: 0.92, y: 0.22 },
  { id: 'data-engineering', label: '데이터\n엔지니어링', size: 24, status: 'planned', link: null, x: 0.60, y: 0.40 },

  // === AI — 하단 중앙 ===
  { id: 'ai', label: 'AI', size: 36, status: 'active', link: null, x: 0.50, y: 0.30 },
  { id: 'ai-agent-workflow', label: 'AI Agent\n워크플로우', size: 26, status: 'active', link: '/study/ai-agent-workflow/', x: 0.42, y: 0.44 },
  { id: 'machine-learning', label: '머신러닝', size: 28, status: 'planned', link: null, x: 0.42, y: 0.60 },
  { id: 'deep-learning', label: '딥러닝', size: 24, status: 'planned', link: null, x: 0.36, y: 0.75 },
  { id: 'computer-vision', label: '컴퓨터 비전', size: 24, status: 'planned', link: null, x: 0.52, y: 0.56 },
  { id: 'time-series', label: '시계열 예측', size: 22, status: 'planned', link: null, x: 0.50, y: 0.72 },
  { id: 'mlops', label: 'MLOps', size: 22, status: 'planned', link: null, x: 0.60, y: 0.56 },
]

export const edges = [
  // Root → 대분류
  { source: 'study-root', target: 'smart-agriculture' },
  { source: 'study-root', target: 'software' },
  { source: 'study-root', target: 'ai' },

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
  { source: 'software', target: 'data-engineering' },
  { source: 'database', target: 'rdb' },
  { source: 'database', target: 'nosql' },
  { source: 'database', target: 'db-tuning' },
  { source: 'backend', target: 'spring' },
  { source: 'backend', target: 'api-design' },
  { source: 'backend', target: 'messaging' },
  { source: 'infra', target: 'aws' },
  { source: 'infra', target: 'kubernetes' },
  { source: 'infra', target: 'cicd' },
  { source: 'software', target: 'auth' },
  { source: 'auth', target: 'oauth' },
  { source: 'oauth', target: 'keycloak' },

  // === AI ===
  { source: 'ai', target: 'ai-agent-workflow' },
  { source: 'ai', target: 'machine-learning' },
  { source: 'ai', target: 'computer-vision' },
  { source: 'ai', target: 'time-series' },
  { source: 'ai', target: 'mlops' },
  { source: 'machine-learning', target: 'deep-learning' },
  // 교차 엣지
  { source: 'crop-analysis', target: 'computer-vision' },
  { source: 'crop-analysis', target: 'time-series' },
]
