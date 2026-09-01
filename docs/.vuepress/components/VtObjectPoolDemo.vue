<template>
  <ClientOnly>
    <div class="vt-demo">
      <div class="vt-demo__stage">
        <!-- VT 화면 -->
        <div class="vt-demo__screen-wrap">
          <div class="vt-demo__caption">VT 화면 (Data Mask 1001 + Soft Key Mask 1002)</div>
          <svg class="vt-demo__screen" viewBox="0 0 300 220" role="img" aria-label="VT 화면 시뮬레이터">
            <!-- Data Mask 배경 -->
            <rect x="0" y="0" width="240" height="220" :fill="C.maskBg" @click="onMaskClick" />

            <!-- Output String 8001 -->
            <g :class="hl(8001)" @click.stop="pick(8001)">
              <rect x="8" y="10" width="104" height="22" :fill="C.zone" />
              <text x="12" y="26" :fill="C.text" font-size="13">엔진 온도</text>
            </g>

            <!-- Output Number 8002 (Number Variable 9001 참조) -->
            <g :class="hl(8002)" @click.stop="pick(8002)">
              <rect x="116" y="10" width="60" height="22" :fill="C.zone" />
              <text x="146" y="26" :fill="C.num" font-size="15" text-anchor="middle"
                    font-family="ui-monospace, monospace">{{ temp }}</text>
            </g>
            <text x="180" y="26" :fill="C.dim" font-size="12">°C</text>

            <!-- Output Meter 8003 (같은 Number Variable 9001) -->
            <g :class="hl(8003)" @click.stop="pick(8003)">
              <circle cx="52" cy="86" r="34" :fill="C.zone" :stroke="C.line" stroke-width="1.5" />
              <path :d="meterArc" :stroke="C.accent" stroke-width="4" fill="none" stroke-linecap="round" />
              <line x1="52" y1="86" :x2="needle.x" :y2="needle.y" :stroke="C.num" stroke-width="2.5" />
              <circle cx="52" cy="86" r="3" :fill="C.num" />
              <text x="52" y="130" :fill="C.dim" font-size="10" text-anchor="middle">Output Meter</text>
            </g>

            <!-- Output Linear Bar Graph 8004 -->
            <g :class="hl(8004)" @click.stop="pick(8004)">
              <rect x="104" y="58" width="126" height="18" :fill="C.zone" :stroke="C.line" stroke-width="1" />
              <rect x="105" y="59" :width="barW" height="16" :fill="C.bar" />
              <text x="104" y="90" :fill="C.dim" font-size="10">Output Linear Bar Graph — 작업 속도 {{ speed }} km/h</text>
            </g>

            <!-- Input Number 8005 -->
            <g :class="hl(8005)" class="vt-demo__hit" @click.stop="editInputNumber">
              <text x="104" y="112" :fill="C.dim" font-size="10">목표 온도</text>
              <rect x="104" y="116" width="60" height="22" :fill="C.inputBg"
                    :stroke="focusId === 8005 ? C.accent : C.line" :stroke-width="focusId === 8005 ? 2 : 1" />
              <text x="134" y="132" :fill="C.text" font-size="14" text-anchor="middle"
                    font-family="ui-monospace, monospace">{{ target }}</text>
            </g>

            <!-- Input Boolean 8006 -->
            <g :class="hl(8006)" class="vt-demo__hit" @click.stop="toggleBoolean">
              <rect x="176" y="116" width="22" height="22" :fill="C.inputBg" :stroke="C.line" stroke-width="1" />
              <path v-if="autoMode" d="M181 127 l4 5 l9 -11" :stroke="C.accent" stroke-width="3" fill="none"
                    stroke-linecap="round" stroke-linejoin="round" />
              <text x="203" y="132" :fill="C.text" font-size="11">자동</text>
            </g>

            <!-- Button 8007 -->
            <g :class="hl(8007)" class="vt-demo__hit" @click.stop="pressButton">
              <rect x="8" y="152" width="94" height="30" rx="4"
                    :fill="btnDown ? C.accent : C.btnBg" :stroke="C.line" stroke-width="1.5" />
              <text x="55" y="172" :fill="btnDown ? C.maskBg : C.text" font-size="13" text-anchor="middle">적용</text>
            </g>

            <text x="8" y="200" :fill="C.dim" font-size="10">← 빈 영역을 누르면 Pointing Event</text>

            <!-- Soft Key Mask -->
            <rect x="240" y="0" width="60" height="220" :fill="C.skBg" />
            <g v-for="k in softKeys" :key="k.id" :class="hl(k.id)" class="vt-demo__hit"
               @click.stop="pressSoftKey(k)">
              <rect x="248" :y="k.y" width="44" height="44" rx="4"
                    :fill="skDown === k.id ? C.accent : C.btnBg" :stroke="C.line" stroke-width="1.5" />
              <text x="270" :y="k.y + 27" :fill="skDown === k.id ? C.maskBg : C.text"
                    font-size="12" text-anchor="middle">{{ k.label }}</text>
            </g>
          </svg>

          <!-- ECU → VT 조작 -->
          <div class="vt-demo__ecu">
            <div class="vt-demo__ecu-title">ECU → VT 명령 보내기</div>
            <label class="vt-demo__slider">
              <span>Number Variable 9001</span>
              <input type="range" min="0" max="120" v-model.number="sliderTemp" @change="sendChangeNumeric" />
              <b>{{ sliderTemp }}</b>
            </label>
            <p class="vt-demo__hint">
              Output Number 8002와 Output Meter 8003이 같은 Number Variable을 참조하므로
              <code>Change Numeric Value</code> 한 번으로 둘 다 갱신된다.
            </p>
          </div>
        </div>

        <!-- 메시지 로그 -->
        <div class="vt-demo__log-wrap">
          <div class="vt-demo__caption">
            <span>CAN 메시지 로그</span>
            <button class="vt-demo__clear" @click="log = []">지우기</button>
          </div>
          <div class="vt-demo__log" ref="logEl">
            <p v-if="!log.length" class="vt-demo__empty">
              화면의 오브젝트를 눌러 보자. VT가 내보내는 메시지가 여기에 쌓인다.
            </p>
            <div v-for="m in log" :key="m.seq" class="vt-demo__msg" :class="'is-' + m.dir">
              <div class="vt-demo__msg-head">
                <span class="vt-demo__tag">{{ m.dir === 'up' ? 'VT → ECU' : 'ECU → VT' }}</span>
                <span class="vt-demo__pgn">{{ m.pgn }}</span>
                <span class="vt-demo__fn">{{ m.name }}</span>
              </div>
              <div class="vt-demo__bytes">{{ m.bytes }}</div>
              <div class="vt-demo__desc">{{ m.desc }}</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 선택한 오브젝트 설명 -->
      <div class="vt-demo__info">
        <strong>{{ info.name }}</strong>
        <span class="vt-demo__type">Type {{ info.type }} · ID {{ info.id }}</span>
        <p>{{ info.desc }}</p>
      </div>
    </div>
  </ClientOnly>
</template>

<script setup>
import { ref, computed, nextTick } from 'vue'

const C = {
  maskBg: '#f4f6f8', skBg: '#dfe4ea', zone: '#ffffff', inputBg: '#ffffff',
  btnBg: '#e8ecf0', line: '#93a1ad', text: '#1f2933', dim: '#6b7684',
  num: '#1a5c3a', accent: '#2f6f4f', bar: '#5b9bd5',
}

const OBJECTS = {
  8001: { name: 'Output String', type: 11, desc: '고정 문자열을 그린다. Font Attributes(Type 23)를 참조해 크기·색을 정한다. 운전자가 눌러도 메시지가 나가지 않는 순수 출력 오브젝트다.' },
  8002: { name: 'Output Number', type: 12, desc: 'Number Variable(Type 21)을 참조해 숫자를 그린다. offset·scale·number_of_decimals 속성으로 raw 값을 표시 값으로 변환한다. 출력 전용이라 운전자 조작으로는 메시지가 나가지 않는다.' },
  8003: { name: 'Output Meter', type: 17, desc: '값을 원형 게이지로 그린다. 8002와 같은 Number Variable 9001을 참조하므로 ECU가 Change Numeric Value 한 번만 보내도 두 오브젝트가 함께 갱신된다.' },
  8004: { name: 'Output Linear Bar Graph', type: 18, desc: '값을 막대 길이로 그린다. min/max 속성 사이에서 값이 선형으로 매핑된다.' },
  8005: { name: 'Input Number', type: 9, desc: '운전자가 숫자를 입력한다. 포커스를 얻으면 VT Select Input Object, 입력을 확정하면 VT Change Numeric Value가 나간다. 값은 4바이트 리틀엔디언이다.' },
  8006: { name: 'Input Boolean', type: 7, desc: '체크박스형 입력. 활성화가 값을 바로 토글하는 원자적 트랜잭션이라 Select 메시지 없이 VT Change Numeric Value만 보낼 수 있다. 값은 1바이트다.' },
  8007: { name: 'Button', type: 6, desc: '화면 안의 버튼. 눌림·뗌마다 Button Activation이 나가고, 홀드 중에는 200 ms마다 still held(2)가 반복된다. 모든 VT가 지원해야 한다.' },
  7001: { name: 'Key (Soft Key)', type: 5, desc: 'Soft Key Mask에 놓이는 물리/터치 소프트키. 눌림·뗌마다 Soft Key Activation이 나간다. Key code 0은 알람 ACK 전용으로 예약돼 있다.' },
}
OBJECTS[7002] = OBJECTS[7001]
OBJECTS[7003] = OBJECTS[7001]

const softKeys = [
  { id: 7001, label: 'SK1', code: 1, y: 12 },
  { id: 7002, label: 'SK2', code: 2, y: 66 },
  { id: 7003, label: 'SK3', code: 3, y: 120 },
]

const temp = ref(85)
const sliderTemp = ref(85)
const speed = ref(8)
const target = ref(90)
const autoMode = ref(false)
const focusId = ref(null)
const selected = ref(8002)
const btnDown = ref(false)
const skDown = ref(null)
const log = ref([])
const logEl = ref(null)
let seq = 0
let tan = 1

const MASK_ID = 1001

const info = computed(() => {
  const o = OBJECTS[selected.value] || OBJECTS[8002]
  return { ...o, id: selected.value }
})

const barW = computed(() => Math.round((speed.value / 20) * 124))
const meterAngle = computed(() => -210 + (Math.min(temp.value, 120) / 120) * 240)
const needle = computed(() => {
  const r = (meterAngle.value * Math.PI) / 180
  return { x: (52 + 26 * Math.cos(r)).toFixed(1), y: (86 + 26 * Math.sin(r)).toFixed(1) }
})
const meterArc = computed(() => {
  const a0 = (-210 * Math.PI) / 180
  const a1 = (meterAngle.value * Math.PI) / 180
  const r = 29
  const large = meterAngle.value - -210 > 180 ? 1 : 0
  const x0 = 52 + r * Math.cos(a0), y0 = 86 + r * Math.sin(a0)
  const x1 = 52 + r * Math.cos(a1), y1 = 86 + r * Math.sin(a1)
  return `M ${x0.toFixed(1)} ${y0.toFixed(1)} A ${r} ${r} 0 ${large} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}`
})

const hl = (id) => (selected.value === id ? 'vt-demo__obj is-sel' : 'vt-demo__obj')
const hex = (n) => n.toString(16).toUpperCase().padStart(2, '0')
const lo = (n) => n & 0xff
const hi = (n) => (n >> 8) & 0xff
const nextTan = () => { tan = (tan % 15) + 1; return tan }

function push(dir, pgn, name, bytes, desc) {
  log.value.push({ seq: seq++, dir, pgn, name, bytes: bytes.map(hex).join(' '), desc })
  if (log.value.length > 40) log.value.shift()
  nextTick(() => { if (logEl.value) logEl.value.scrollTop = logEl.value.scrollHeight })
}

// VT → ECU : PGN 58880 (0xE600)
const UP = '0xE600 (58880)'
// ECU → VT : PGN 59136 (0xE700)
const DOWN = '0xE700 (59136)'

function pick(id) { selected.value = id }

function onMaskClick(e) {
  selected.value = 8001
  const r = e.currentTarget.getBoundingClientRect()
  const x = Math.round(((e.clientX - r.left) / r.width) * 240)
  const y = Math.round(((e.clientY - r.top) / r.height) * 220)
  const t = nextTan()
  push('up', UP, 'Pointing Event (fn 02)',
    [0x02, lo(x), hi(x), lo(y), hi(y), (t << 4) | 1, lo(MASK_ID), hi(MASK_ID)],
    `X=${x}, Y=${y} 위치가 눌렸다. Touch State=1(Pressed), TAN=${t}. 버튼·입력 오브젝트 위가 아닌 Data Mask 영역이라 이 메시지가 나간다.`)
}

function pressButton() {
  selected.value = 8007
  btnDown.value = true
  const t1 = nextTan()
  push('up', UP, 'Button Activation (fn 01)',
    [0x01, 0x01, lo(8007), hi(8007), lo(MASK_ID), hi(MASK_ID), 0x05, (t1 << 4) | 0x0f],
    `Object ID 8007 눌림(1 = pressed). Parent는 Data Mask ${MASK_ID}, Button key code 5, TAN=${t1}.`)
  setTimeout(() => {
    btnDown.value = false
    const t2 = nextTan()
    push('up', UP, 'Button Activation (fn 01)',
      [0x01, 0x00, lo(8007), hi(8007), lo(MASK_ID), hi(MASK_ID), 0x05, (t2 << 4) | 0x0f],
      `같은 버튼 뗌(0 = released). 홀드가 이어지면 200 ms마다 still held(2)가 반복되고, 300 ms 넘게 끊기면 Working Set은 released로 처리한다.`)
  }, 260)
}

function pressSoftKey(k) {
  selected.value = k.id
  skDown.value = k.id
  const t1 = nextTan()
  push('up', UP, 'Soft Key Activation (fn 00)',
    [0x00, 0x01, lo(k.id), hi(k.id), lo(MASK_ID), hi(MASK_ID), k.code, (t1 << 4) | 0x0f],
    `Key ${k.label}(Object ID ${k.id}) 눌림. Soft key code ${k.code}, Parent Data Mask ${MASK_ID}, TAN=${t1}.`)
  setTimeout(() => {
    skDown.value = null
    const t2 = nextTan()
    push('up', UP, 'Soft Key Activation (fn 00)',
      [0x00, 0x00, lo(k.id), hi(k.id), lo(MASK_ID), hi(MASK_ID), k.code, (t2 << 4) | 0x0f],
      `Key ${k.label} 뗌(0 = released).`)
  }, 260)
}

function toggleBoolean() {
  selected.value = 8006
  autoMode.value = !autoMode.value
  const v = autoMode.value ? 1 : 0
  const t = nextTan()
  push('up', UP, 'VT Change Numeric Value (fn 05)',
    [0x05, lo(8006), hi(8006), (t << 4) | 0x0f, v, 0x00, 0x00, 0x00],
    `Input Boolean 8006의 값이 ${v}로 바뀌었다. 값은 1바이트라 나머지 세 바이트는 0으로 채운다. 토글이 원자적이라 Select 메시지 없이 값만 보낸다.`)
}

function editInputNumber() {
  selected.value = 8005
  focusId.value = 8005
  const t1 = nextTan()
  push('up', UP, 'VT Select Input Object (fn 03)',
    [0x03, lo(8005), hi(8005), 0x01, 0x01, 0xff, 0xff, (t1 << 4) | 0x0f],
    `Input Number 8005가 포커스를 얻고(Byte 4 = 1) 데이터 입력용으로 열렸다(Byte 5 Bit 0 = 1).`)
  setTimeout(() => {
    target.value = target.value >= 120 ? 60 : target.value + 5
    const v = target.value
    const t2 = nextTan()
    push('up', UP, 'VT Change Numeric Value (fn 05)',
      [0x05, lo(8005), hi(8005), (t2 << 4) | 0x0f, v & 0xff, (v >> 8) & 0xff, (v >> 16) & 0xff, (v >> 24) & 0xff],
      `운전자가 ENTER로 ${v}를 확정했다. 값은 4바이트 리틀엔디언이다. 값이 그대로여도 ENTER를 누르면 전송된다.`)
    const t3 = nextTan()
    push('up', UP, 'VT Select Input Object (fn 03)',
      [0x03, lo(8005), hi(8005), 0x00, 0x00, 0xff, 0xff, (t3 << 4) | 0x0f],
      `입력이 닫히고 포커스를 잃었다(Byte 4 = 0).`)
    focusId.value = null
  }, 420)
}

function sendChangeNumeric() {
  selected.value = 8003
  const v = sliderTemp.value
  temp.value = v
  push('down', DOWN, 'Change Numeric Value command (A8)',
    [0xa8, lo(9001), hi(9001), 0xff, v & 0xff, (v >> 8) & 0xff, (v >> 16) & 0xff, (v >> 24) & 0xff],
    `Number Variable 9001의 값을 ${v}로 바꾼다. 이 변수를 참조하는 Output Number 8002와 Output Meter 8003이 함께 다시 그려진다.`)
}
</script>

<style scoped>
.vt-demo {
  border: 1px solid var(--vp-c-border);
  border-radius: 8px;
  padding: 14px;
  margin: 20px 0;
  background: var(--vp-c-bg-alt);
}
.vt-demo__stage { display: flex; gap: 14px; flex-wrap: wrap; }
.vt-demo__screen-wrap { flex: 1 1 340px; min-width: 300px; }
.vt-demo__log-wrap { flex: 1 1 300px; min-width: 260px; display: flex; flex-direction: column; }
.vt-demo__caption {
  font-size: 12px; color: var(--vp-c-text-mute, #888);
  margin-bottom: 6px; display: flex; justify-content: space-between; align-items: center;
}
.vt-demo__screen {
  width: 100%; border: 2px solid var(--vp-c-border); border-radius: 6px;
  display: block; background: #f4f6f8;
}
.vt-demo__obj { cursor: pointer; }
.vt-demo__obj.is-sel { outline: none; filter: drop-shadow(0 0 3px #2f6f4f); }
.vt-demo__hit:active { opacity: 0.85; }
.vt-demo__ecu {
  margin-top: 10px; padding: 10px; border: 1px solid var(--vp-c-border);
  border-radius: 6px; background: var(--vp-c-bg);
}
.vt-demo__ecu-title { font-size: 12px; font-weight: 700; margin-bottom: 8px; }
.vt-demo__slider { display: flex; align-items: center; gap: 8px; font-size: 12px; }
.vt-demo__slider input { flex: 1; }
.vt-demo__slider b { min-width: 30px; text-align: right; font-family: ui-monospace, monospace; }
.vt-demo__hint { font-size: 11px; color: var(--vp-c-text-mute, #888); margin: 8px 0 0; line-height: 1.5; }
.vt-demo__log {
  flex: 1; min-height: 300px; max-height: 460px; overflow-y: auto;
  border: 1px solid var(--vp-c-border); border-radius: 6px;
  background: var(--vp-c-bg); padding: 8px;
}
.vt-demo__empty { font-size: 12px; color: var(--vp-c-text-mute, #888); margin: 12px 6px; line-height: 1.6; }
.vt-demo__msg {
  border-left: 3px solid var(--vp-c-border); padding: 6px 8px; margin-bottom: 7px;
  background: var(--vp-c-bg-alt); border-radius: 0 4px 4px 0;
}
.vt-demo__msg.is-up { border-left-color: #2f6f4f; }
.vt-demo__msg.is-down { border-left-color: #5b9bd5; }
.vt-demo__msg-head { display: flex; gap: 6px; align-items: baseline; flex-wrap: wrap; font-size: 11px; }
.vt-demo__tag { font-weight: 700; }
.vt-demo__pgn { color: var(--vp-c-text-mute, #888); font-family: ui-monospace, monospace; }
.vt-demo__fn { font-weight: 600; }
.vt-demo__bytes {
  font-family: ui-monospace, monospace; font-size: 12.5px; letter-spacing: 0.5px;
  margin: 4px 0 3px; word-break: break-all;
}
.vt-demo__desc { font-size: 11px; color: var(--vp-c-text-mute, #888); line-height: 1.55; }
.vt-demo__clear {
  font-size: 11px; padding: 2px 8px; border: 1px solid var(--vp-c-border);
  border-radius: 4px; background: var(--vp-c-bg); cursor: pointer; color: inherit;
}
.vt-demo__info {
  margin-top: 12px; padding: 10px 12px; border-radius: 6px;
  background: var(--vp-c-bg); border: 1px solid var(--vp-c-border);
}
.vt-demo__info strong { font-size: 14px; }
.vt-demo__type {
  margin-left: 8px; font-size: 11px; color: var(--vp-c-text-mute, #888);
  font-family: ui-monospace, monospace;
}
.vt-demo__info p { margin: 6px 0 0; font-size: 12.5px; line-height: 1.65; }
@media (max-width: 719px) {
  .vt-demo__stage { flex-direction: column; }
  .vt-demo__log { min-height: 220px; }
}
</style>
