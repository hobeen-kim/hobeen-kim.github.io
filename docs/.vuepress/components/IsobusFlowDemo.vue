<template>
  <ClientOnly>
    <div class="fx">
      <div class="fx__bar">
        <button class="fx__btn fx__btn--main" @click="toggle">{{ running ? '⏸' : '▶' }}</button>
        <button class="fx__btn" @click="restart">↺</button>
        <span class="fx__stage-name">{{ stageLabel }}</span>
        <label class="fx__speed">속도
          <input type="range" min="0.5" max="3" step="0.5" v-model.number="speed" />
          <b>{{ speed }}×</b>
        </label>
      </div>

      <svg class="fx__svg" viewBox="0 0 620 430" @click="onSvgClick">
        <!-- ═══ 상단: 버스와 노드 ═══ -->
        <text x="10" y="16" :fill="c.dim" font-size="10">ISOBUS 버스</text>

        <!-- 버스 라인 -->
        <line x1="70" y1="78" x2="560" y2="78" :stroke="c.line" stroke-width="3" />
        <line x1="70" y1="78" x2="560" y2="78" :stroke="c.acc" stroke-width="3"
              :stroke-dasharray="busDash" opacity="0.25" />

        <!-- 노드 -->
        <g v-for="n in nodes" :key="n.k">
          <line :x1="n.x" y1="78" :x2="n.x" :y2="n.y" :stroke="c.line" stroke-width="1.5" />
          <rect :x="n.x - 52" :y="n.y" width="104" height="46" rx="5"
                :fill="c.card" :stroke="active(n.k) ? c.acc : c.line"
                :stroke-width="active(n.k) ? 2.5 : 1.2" />
          <text :x="n.x" :y="n.y + 17" :fill="c.tx" font-size="11.5" font-weight="700"
                text-anchor="middle">{{ n.name }}</text>
          <text :x="n.x" :y="n.y + 31" :fill="c.dim" font-size="9" text-anchor="middle">{{ n.sub }}</text>
          <!-- 보유 데이터 칩 -->
          <g v-for="(s, si) in n.stores" :key="s.k">
            <rect :x="n.x - 48 + si * 34" :y="n.y + 34" width="31" height="9" rx="2"
                  :fill="hasStore(s.k) ? c.chipOn : c.chipOff"
                  :opacity="hasStore(s.k) ? 1 : 0.35" />
            <text :x="n.x - 32.5 + si * 34" :y="n.y + 41" font-size="6"
                  :fill="hasStore(s.k) ? c.chipTx : c.dim" text-anchor="middle">{{ s.t }}</text>
          </g>
        </g>

        <!-- 날아다니는 패킷 -->
        <g v-for="p in flying" :key="p.id">
          <rect :x="p.x - 26" :y="p.y - 8" width="52" height="16" rx="3"
                :fill="p.up ? c.pkUp : c.pkDn" />
          <text :x="p.x" :y="p.y + 4" font-size="8" font-weight="700"
                fill="#fff" text-anchor="middle">{{ p.tag }}</text>
        </g>

        <!-- VT 화면 미니 -->
        <g>
          <rect x="18" y="132" width="104" height="58" rx="4" :fill="c.vtBg" :stroke="c.line" stroke-width="1.5" />
          <text x="26" y="148" :fill="c.vtTx" font-size="8">살포량</text>
          <text x="70" y="172" :fill="vtLive ? c.acc : c.dim" font-size="21" font-weight="700"
                text-anchor="middle" font-family="ui-monospace, monospace">{{ vtLive ? vtValue : '—' }}</text>
          <text x="108" y="186" :fill="c.vtTx" font-size="7.5" text-anchor="end">L/ha</text>
        </g>
        <text x="70" y="203" :fill="c.dim" font-size="8" text-anchor="middle">VT 화면</text>

        <!-- ═══ 하단: 밭 ═══ -->
        <text x="10" y="228" :fill="c.dim" font-size="10">처방 맵 (위에서 본 밭)</text>
        <text x="610" y="228" :fill="c.dim" font-size="8.5" text-anchor="end">색 = 목표 살포량</text>

        <!-- 격자 셀 -->
        <g v-for="cell in cells" :key="cell.id">
          <rect :x="cell.x" :y="cell.y" :width="CW" :height="CH"
                :fill="rateColor(cell.rate)" :stroke="c.bg" stroke-width="1" />
        </g>
        <!-- 이미 지나간 자취 -->
        <rect v-if="phase === 'run'" x="74" :y="FY" :width="Math.max(0, tx - 74)" :height="ROWS * CH"
              :fill="c.tx" opacity="0.07" />

        <!-- 붐 + 섹션 -->
        <g v-if="phase === 'run'">
          <line :x1="tx" :y1="FY" :x2="tx" :y2="FY + ROWS * CH" :stroke="c.tx" stroke-width="1" opacity="0.5" />
          <g v-for="(s, si) in sections" :key="si">
            <rect :x="tx - 8" :y="FY + si * CH + 2" width="16" :height="CH - 4" rx="2"
                  :fill="rateColor(s)" :stroke="c.tx" stroke-width="1.2" />
          </g>
          <!-- 트랙터 -->
          <g :transform="`translate(${tx + 8}, ${FY + ROWS * CH / 2 - 11})`">
            <rect x="0" y="3" width="24" height="16" rx="3" :fill="c.trac" />
            <rect x="20" y="6" width="9" height="10" rx="2" :fill="c.trac" />
            <circle cx="6" cy="21" r="4.5" :fill="c.tx" />
            <circle cx="22" cy="20" r="3" :fill="c.tx" />
            <circle cx="6" cy="1" r="4.5" :fill="c.tx" />
            <circle cx="22" cy="2" r="3" :fill="c.tx" />
          </g>
        </g>

        <!-- 섹션 번호 -->
        <g v-if="phase === 'run'">
          <text v-for="i in ROWS" :key="i" x="66" :y="FY + (i - 1) * CH + CH / 2 + 3"
                :fill="c.dim" font-size="7.5" text-anchor="end">섹션{{ i }}</text>
        </g>

        <!-- 범례 -->
        <g v-for="(lg, li) in legend" :key="lg.v">
          <rect :x="420 + li * 50" y="404" width="11" height="11" rx="2" :fill="rateColor(lg.v)" />
          <text :x="435 + li * 50" y="413" :fill="c.dim" font-size="8">{{ lg.t }}</text>
        </g>
      </svg>

      <div class="fx__cap">
        <span class="fx__cap-tag" :class="msg.up ? 'up' : 'dn'">{{ msg.pgn }}</span>
        <span class="fx__cap-txt">{{ msg.text }}</span>
      </div>
      <p class="fx__hint">{{ hint }}</p>
    </div>
  </ClientOnly>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const COLS = 14, ROWS = 6, CW = 38, CH = 26, FX0 = 74, FY = 238
const RATES = [0, 150, 200, 250]

// 처방 맵: 셀마다 목표 살포량 (구획 경계가 섹션마다 다르게 지나가도록 구성)
const MAP = []
for (let r = 0; r < ROWS; r++) {
  const row = []
  for (let cIdx = 0; cIdx < COLS; cIdx++) {
    const band = Math.floor((cIdx + r * 1.6) / 3.5) % 3
    row.push(RATES[band + 1])
  }
  MAP.push(row)
}
const cells = []
for (let r = 0; r < ROWS; r++)
  for (let cIdx = 0; cIdx < COLS; cIdx++)
    cells.push({ id: r + '-' + cIdx, x: FX0 + cIdx * CW, y: FY + r * CH, rate: MAP[r][cIdx] })

const nodes = [
  { k: 'vt', name: 'VT', sub: '트랙터 화면', x: 130, y: 96,
    stores: [{ k: 'vt_pool', t: '풀' }, { k: 'vt_screen', t: '화면' }] },
  { k: 'tc', name: 'TC', sub: 'Task Controller', x: 315, y: 96,
    stores: [{ k: 'tc_ddop', t: 'DDOP' }, { k: 'tc_task', t: '태스크' }] },
  { k: 'ecu', name: '작업기 ECU', sub: '살포기', x: 500, y: 96,
    stores: [{ k: 'e_vt', t: 'VT풀' }, { k: 'e_ddop', t: 'DDOP' }] },
]
const legend = [{ v: 150, t: '150' }, { v: 200, t: '200' }, { v: 250, t: '250 L/ha' }]

// ── 타임라인 (초) ──
const SCRIPT = [
  { t: 0.4, from: 'ecu', to: 'tc', tag: 'EE00', pgn: 'PGN 60928', up: true,
    text: 'Address Claim — 작업기가 NAME을 실어 주소를 확보한다' },
  { t: 2.0, from: 'ecu', to: 'vt', tag: 'C0', pgn: 'PGN 59136', up: true,
    text: 'Get Memory — 오브젝트 풀 8000바이트를 받을 수 있는지 묻는다' },
  { t: 3.4, from: 'vt', to: 'ecu', tag: 'C0 ✓', pgn: 'PGN 58880', up: false,
    text: 'Get Memory response — VT version 6, 메모리 충분' },
  { t: 4.8, from: 'ecu', to: 'vt', tag: '11 풀', pgn: 'PGN 59136 + ETP', up: true,
    text: 'Object Pool Transfer — 화면 정의를 ETP로 쪼개 올린다', slow: true, gain: 'vt_pool' },
  { t: 7.4, from: 'ecu', to: 'vt', tag: '12 끝', pgn: 'PGN 59136', up: true,
    text: 'End of Object Pool — VT가 파싱하고 화면을 띄운다', gain: 'vt_screen' },
  { t: 9.0, from: 'ecu', to: 'tc', tag: 'Label?', pgn: 'PGN 51968', up: true,
    text: 'Request Structure Label — TC가 이 DDOP를 이미 갖고 있나 확인' },
  { t: 10.4, from: 'ecu', to: 'tc', tag: 'DDOP', pgn: 'PGN 51968 + ETP', up: true,
    text: 'DDOP 전송 — 섹션 6개와 쓸 수 있는 DDI를 선언한다', slow: true, gain: 'tc_ddop' },
  { t: 13.0, from: 'ecu', to: 'tc', tag: 'ON', pgn: 'PGN 51968', up: true,
    text: 'Object-pool Activate — TC가 이제 이 작업기의 구조를 안다' },
  { t: 14.4, from: 'vt', to: 'tc', tag: 'TASK', pgn: 'USB 파일', up: false,
    text: 'TASKDATA.XML + 격자 바이너리 — 처방 맵이 파일로 들어온다', gain: 'tc_task' },
]
const RUN_AT = 16.2

const t = ref(0)
const running = ref(true)
const speed = ref(1)
const fired = ref(new Set())
const stores = ref(new Set(['e_vt', 'e_ddop']))
const flying = ref([])
const msg = ref({ pgn: '', text: '전원을 켜는 중…', up: true })
let raf = null, last = 0, pid = 0

const phase = computed(() => (t.value < RUN_AT ? 'setup' : 'run'))
const stageLabel = computed(() =>
  t.value < 1.6 ? '① 주소 확보' : t.value < 8.6 ? '② VT 연결'
  : t.value < 14.2 ? '③ TC 연결' : t.value < RUN_AT ? '④ 태스크 로드' : '⑤ 작업 중')
const hint = computed(() => phase.value === 'setup'
  ? '연결 단계 — 작업기가 플래시에 든 두 오브젝트 풀을 VT와 TC에 각각 올린다.'
  : '작업 단계 — 붐 섹션마다 구획이 다르므로 섹션별로 다른 살포량이 내려간다. 색이 바뀌는 순간이 Value command가 나가는 시점이다.')

// 트랙터 위치
const tx = computed(() => {
  if (phase.value !== 'run') return FX0
  const d = (t.value - RUN_AT) * 26
  return FX0 + (d % (COLS * CW))
})
const colIdx = computed(() => Math.min(COLS - 1, Math.floor((tx.value - FX0) / CW)))
const sections = computed(() =>
  phase.value === 'run' ? MAP.map((row) => row[colIdx.value]) : new Array(ROWS).fill(0))
const vtLive = computed(() => stores.value.has('vt_screen'))
const vtValue = computed(() => {
  if (phase.value !== 'run') return 0
  return Math.round(sections.value.reduce((a, b) => a + b, 0) / ROWS)
})
const busDash = computed(() => `6 ${6 + Math.sin(t.value * 3) * 2}`)

const c = {
  bg: 'transparent', tx: 'var(--vp-c-text, #24292f)', dim: 'var(--vp-c-text-mute, #7c8794)',
  line: 'var(--vp-c-border, #99a)', card: 'var(--vp-c-bg, #fff)', acc: '#2f6f4f',
  chipOn: '#2f6f4f', chipOff: 'var(--vp-c-border, #ccc)', chipTx: '#fff',
  vtBg: '#1d2b23', vtTx: '#9fc3ad', trac: '#c2620a',
  pkUp: '#2f6f4f', pkDn: '#3f7fbf',
}
const RCOL = { 0: 'var(--vp-c-border, #ccc)', 150: '#cfe3d3', 200: '#7fb894', 250: '#2f6f4f' }
const rateColor = (v) => RCOL[v] || RCOL[0]
const hasStore = (k) => stores.value.has(k)
const active = (k) => flying.value.some((p) => p.f === k || p.tgt === k)

function nodeX(k) { return (nodes.find((n) => n.k === k) || {}).x || 300 }

function fire(s) {
  const id = ++pid
  flying.value.push({
    id, f: s.from, tgt: s.to, tag: s.tag, up: s.up,
    x: nodeX(s.from), y: 78, t0: t.value, dur: s.slow ? 2.2 : 1.1,
    x0: nodeX(s.from), x1: nodeX(s.to),
  })
  msg.value = { pgn: s.pgn, text: s.text, up: s.up }
  if (s.gain) setTimeout(() => stores.value.add(s.gain), 600)
}

let lastSecs = null
function tick(ts) {
  if (!last) last = ts
  const dt = Math.min(0.05, (ts - last) / 1000) * speed.value
  last = ts
  if (running.value) t.value += dt

  SCRIPT.forEach((s, i) => {
    if (!fired.value.has(i) && t.value >= s.t) { fired.value.add(i); fire(s) }
  })

  flying.value = flying.value.filter((p) => {
    const k = (t.value - p.t0) / p.dur
    p.x = p.x0 + (p.x1 - p.x0) * Math.min(1, k)
    p.y = 78 - Math.sin(Math.min(1, k) * Math.PI) * 16
    return k < 1.15
  })

  if (phase.value === 'run') {
    const key = sections.value.join(',')
    if (lastSecs !== null && key !== lastSecs) {
      const id = ++pid
      flying.value.push({ id, f: 'tc', tgt: 'ecu', tag: 'CB00', up: false,
        x: nodeX('tc'), y: 78, t0: t.value, dur: 0.9, x0: nodeX('tc'), x1: nodeX('ecu') })
      msg.value = { pgn: 'PGN 51968', up: false,
        text: `구획이 바뀌었다 — Value command로 섹션별 setpoint(${sections.value.join(' / ')} L/ha)를 내린다` }
      setTimeout(() => {
        const i2 = ++pid
        flying.value.push({ id: i2, f: 'ecu', tgt: 'vt', tag: 'A8', up: true,
          x: nodeX('ecu'), y: 78, t0: t.value, dur: 0.9, x0: nodeX('ecu'), x1: nodeX('vt') })
      }, 500 / speed.value)
    }
    lastSecs = key
  }
  raf = requestAnimationFrame(tick)
}

function toggle() { running.value = !running.value; last = 0 }
function restart() {
  t.value = 0; fired.value = new Set(); stores.value = new Set(['e_vt', 'e_ddop'])
  flying.value = []; lastSecs = null; running.value = true; last = 0
  msg.value = { pgn: '', text: '전원을 켜는 중…', up: true }
}
function onSvgClick() { toggle() }

onMounted(() => { raf = requestAnimationFrame(tick) })
onUnmounted(() => { if (raf) cancelAnimationFrame(raf) })
</script>

<style scoped>
.fx { border: 1px solid var(--vp-c-border); border-radius: 8px; padding: 12px; margin: 20px 0; background: var(--vp-c-bg-alt); }
.fx__bar { display: flex; align-items: center; gap: 8px; margin-bottom: 8px; flex-wrap: wrap; }
.fx__btn { font-size: 13px; padding: 3px 11px; border: 1px solid var(--vp-c-border); border-radius: 5px; background: var(--vp-c-bg); color: inherit; cursor: pointer; }
.fx__btn--main { font-weight: 700; min-width: 42px; }
.fx__stage-name { font-size: 12px; font-weight: 700; color: #2f6f4f; }
.fx__speed { margin-left: auto; font-size: 11px; display: flex; align-items: center; gap: 6px; }
.fx__speed input { width: 84px; }
.fx__svg { width: 100%; display: block; background: var(--vp-c-bg); border-radius: 6px; border: 1px solid var(--vp-c-border); cursor: pointer; }
.fx__cap { margin-top: 9px; display: flex; gap: 8px; align-items: baseline; flex-wrap: wrap; }
.fx__cap-tag { font-size: 10px; font-family: ui-monospace, monospace; padding: 2px 7px; border-radius: 3px; color: #fff; flex: none; }
.fx__cap-tag.up { background: #2f6f4f; }
.fx__cap-tag.dn { background: #3f7fbf; }
.fx__cap-txt { font-size: 12.5px; line-height: 1.6; }
.fx__hint { font-size: 11px; opacity: 0.7; margin: 7px 0 0; line-height: 1.6; }
</style>
