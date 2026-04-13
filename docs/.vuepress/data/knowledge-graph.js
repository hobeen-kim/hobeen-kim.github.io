export const CATEGORY_COLORS = {
  root: '#F59E0B',
  protocol: '#10B981',
  application: '#3B82F6',
  hardware: '#64748B',
  data: '#F97316',
  iot: '#8B5CF6',
  sensor: '#F43F5E',
  ai: '#06B6D4',
}

export const nodes = [
  { id: 'smart-agriculture', label: '스마트농업', category: 'root', size: 40, status: 'active', link: null },
  { id: 'isobus', label: 'ISOBUS', category: 'protocol', size: 30, status: 'active', link: '/study/isobus/' },
  { id: 'can-j1939', label: 'CAN / J1939', category: 'protocol', size: 22, status: 'planned', link: null },
  { id: 'precision-ag', label: '정밀농업', category: 'application', size: 26, status: 'planned', link: null },
  { id: 'autonomous', label: '자율주행 농기계', category: 'application', size: 22, status: 'planned', link: null },
  { id: 'embedded', label: '임베디드 시스템', category: 'hardware', size: 22, status: 'planned', link: null },
  { id: 'isoxml', label: 'ISOXML / TaskData', category: 'data', size: 22, status: 'planned', link: null },
  { id: 'fmis', label: 'FMIS', category: 'data', size: 20, status: 'planned', link: null },
  { id: 'agri-iot', label: '농업 IoT', category: 'iot', size: 24, status: 'planned', link: null },
  { id: 'telematics', label: '텔레매틱스', category: 'iot', size: 20, status: 'planned', link: null },
  { id: 'rtk-gps', label: 'RTK-GPS', category: 'sensor', size: 22, status: 'planned', link: null },
  { id: 'crop-analysis', label: '작물 분석', category: 'ai', size: 20, status: 'planned', link: null },
]

export const edges = [
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
]
