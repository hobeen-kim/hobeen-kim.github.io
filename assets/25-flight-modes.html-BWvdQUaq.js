import{_ as s,c as a,e as t,o as e}from"./app-DncCSHO0.js";const l={};function p(o,n){return e(),a("div",null,n[0]||(n[0]=[t(`<h1 id="ch25-비행-모드-구조" tabindex="-1"><a class="header-anchor" href="#ch25-비행-모드-구조"><span>CH25. 비행 모드 구조</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>Mode 베이스 클래스의 핵심 가상 함수(mode_number, init, run, requires_position, has_manual_throttle, is_autopilot)의 역할을 설명할 수 있다.</li><li>Stabilize, AltHold, Loiter 각 모드의 run() 루프가 제어 캐스케이드의 어느 계층에서 시작하는지 구분할 수 있다.</li><li>모드별 GPS 필요 여부·자동조종 여부·스로틀 형태를 표로 정리할 수 있다.</li><li>비행 모드 전환 시 init() 실패 조건을 이해한다.</li></ul></div><h2 id="_1-mode-베이스-클래스" tabindex="-1"><a class="header-anchor" href="#_1-mode-베이스-클래스"><span>1. Mode 베이스 클래스</span></a></h2><h3 id="모드-번호-열거형" tabindex="-1"><a class="header-anchor" href="#모드-번호-열거형"><span>모드 번호 열거형</span></a></h3><p>ArduCopter는 수십 개의 비행 모드를 지원한다. 각 모드는 고유한 번호를 가진다:</p><div class="language-cpp line-numbers-mode" data-highlighter="prismjs" data-ext="cpp" data-title="cpp"><pre><code><span class="line"><span class="token keyword">enum</span> <span class="token keyword">class</span> <span class="token class-name">Number</span> <span class="token operator">:</span> <span class="token base-clause"><span class="token keyword">uint8_t</span></span> <span class="token punctuation">{</span></span>
<span class="line">    STABILIZE  <span class="token operator">=</span>  <span class="token number">0</span><span class="token punctuation">,</span>  <span class="token comment">// 수동 자세 + 수동 스로틀</span></span>
<span class="line">    ACRO       <span class="token operator">=</span>  <span class="token number">1</span><span class="token punctuation">,</span>  <span class="token comment">// 수동 각속도 + 수동 스로틀</span></span>
<span class="line">    ALT_HOLD   <span class="token operator">=</span>  <span class="token number">2</span><span class="token punctuation">,</span>  <span class="token comment">// 수동 자세 + 자동 고도</span></span>
<span class="line">    AUTO       <span class="token operator">=</span>  <span class="token number">3</span><span class="token punctuation">,</span>  <span class="token comment">// 완전 자동 미션</span></span>
<span class="line">    GUIDED     <span class="token operator">=</span>  <span class="token number">4</span><span class="token punctuation">,</span>  <span class="token comment">// GCS/SDK 실시간 명령</span></span>
<span class="line">    LOITER     <span class="token operator">=</span>  <span class="token number">5</span><span class="token punctuation">,</span>  <span class="token comment">// 자동 수평 + 자동 고도</span></span>
<span class="line">    RTL        <span class="token operator">=</span>  <span class="token number">6</span><span class="token punctuation">,</span>  <span class="token comment">// 자동 귀환</span></span>
<span class="line">    CIRCLE     <span class="token operator">=</span>  <span class="token number">7</span><span class="token punctuation">,</span>  <span class="token comment">// 자동 원형 비행</span></span>
<span class="line">    LAND       <span class="token operator">=</span>  <span class="token number">9</span><span class="token punctuation">,</span>  <span class="token comment">// 자동 착륙</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line">    POSHOLD    <span class="token operator">=</span> <span class="token number">16</span><span class="token punctuation">,</span>  <span class="token comment">// 자동 위치 + 수동 오버라이드</span></span>
<span class="line">    BRAKE      <span class="token operator">=</span> <span class="token number">17</span><span class="token punctuation">,</span>  <span class="token comment">// 완전 제동</span></span>
<span class="line">    SMART_RTL  <span class="token operator">=</span> <span class="token number">21</span><span class="token punctuation">,</span>  <span class="token comment">// 경로 역추적 귀환</span></span>
<span class="line">    FLOWHOLD   <span class="token operator">=</span> <span class="token number">22</span><span class="token punctuation">,</span>  <span class="token comment">// Optical Flow 위치 유지</span></span>
<span class="line">    ZIGZAG     <span class="token operator">=</span> <span class="token number">24</span><span class="token punctuation">,</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line"><span class="token punctuation">}</span><span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>(ArduCopter/mode.h:77)</code></p><p>이 번호는 MAVLink <code>HEARTBEAT</code> 메시지의 <code>custom_mode</code> 필드로 GCS에 전달된다.</p><h3 id="핵심-가상-함수" tabindex="-1"><a class="header-anchor" href="#핵심-가상-함수"><span>핵심 가상 함수</span></a></h3><p><code>Mode</code> 클래스는 모든 구체 모드가 반드시 구현해야 하는 순수 가상 함수와 선택적 가상 함수를 정의한다:</p><div class="language-cpp line-numbers-mode" data-highlighter="prismjs" data-ext="cpp" data-title="cpp"><pre><code><span class="line"><span class="token keyword">class</span> <span class="token class-name">Mode</span> <span class="token punctuation">{</span></span>
<span class="line"><span class="token keyword">public</span><span class="token operator">:</span></span>
<span class="line">    <span class="token comment">// 모드 고유 번호 — 반드시 구현</span></span>
<span class="line">    <span class="token keyword">virtual</span> Number <span class="token function">mode_number</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token keyword">const</span> <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 모드 진입 — 실패하면 false 반환, 모드 전환 거부</span></span>
<span class="line">    <span class="token keyword">virtual</span> <span class="token keyword">bool</span> <span class="token function">init</span><span class="token punctuation">(</span><span class="token keyword">bool</span> ignore_checks<span class="token punctuation">)</span> <span class="token punctuation">{</span> <span class="token keyword">return</span> <span class="token boolean">true</span><span class="token punctuation">;</span> <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 매 루프(400Hz) 제어 계산 — 반드시 구현</span></span>
<span class="line">    <span class="token keyword">virtual</span> <span class="token keyword">void</span> <span class="token function">run</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// GPS 위치 추정이 필요한 모드인가</span></span>
<span class="line">    <span class="token keyword">virtual</span> <span class="token keyword">bool</span> <span class="token function">requires_position</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token keyword">const</span> <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 조종사가 스로틀을 직접 제어하는가</span></span>
<span class="line">    <span class="token keyword">virtual</span> <span class="token keyword">bool</span> <span class="token function">has_manual_throttle</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token keyword">const</span> <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 자동조종 모드인가(GPS 자율비행 포함)</span></span>
<span class="line">    <span class="token keyword">virtual</span> <span class="token keyword">bool</span> <span class="token function">is_autopilot</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token keyword">const</span> <span class="token operator">=</span> <span class="token number">0</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span><span class="token punctuation">;</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>(ArduCopter/mode.h:120~131)</code></p><p><code>run()</code>이 순수 가상(<code>= 0</code>)이라는 점이 핵심이다. 모드 객체가 존재한다면 반드시 실제 제어 코드가 있어야 한다. 메인 루프(<code>fast_loop</code>, 약 400Hz)는 <code>flightmode-&gt;run()</code>을 매 사이클 호출한다.</p><h3 id="제어-계층-cascade-복습" tabindex="-1"><a class="header-anchor" href="#제어-계층-cascade-복습"><span>제어 계층(cascade) 복습</span></a></h3><p>20장에서 다룬 제어 캐스케이드를 떠올리자:</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">조종사 입력</span>
<span class="line">   ↓</span>
<span class="line">[위치 루프]    — GPS 위치 오차 → 목표 속도</span>
<span class="line">   ↓</span>
<span class="line">[속도 루프]    — 속도 오차 → 목표 가속도/자세</span>
<span class="line">   ↓</span>
<span class="line">[자세 루프]    — 자세 오차 → 목표 각속도</span>
<span class="line">   ↓</span>
<span class="line">[각속도 루프]  — 각속도 오차 → 모터 출력</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>모드는 이 계층의 <strong>어느 입구부터 열어줄 것인가</strong>를 결정한다. Stabilize는 자세 루프만, AltHold는 수직 속도 루프 + 자세 루프, Loiter는 전체 루프를 사용한다.</p><h2 id="_2-mode-클래스-계층" tabindex="-1"><a class="header-anchor" href="#_2-mode-클래스-계층"><span>2. Mode 클래스 계층</span></a></h2><pre class="mermaid">classDiagram
    class Mode {
        +mode_number()* Number
        +init(bool)* bool
        +run()* void
        +requires_position()* bool
        +has_manual_throttle()* bool
        +is_autopilot()* bool
        #attitude_control
        #pos_control
        #wp_nav
        #motors
    }
    class ModeStabilize {
        +mode_number() STABILIZE
        +run() void
        +requires_position() false
        +has_manual_throttle() true
        +is_autopilot() false
    }
    class ModeAltHold {
        +mode_number() ALT_HOLD
        +init(bool) bool
        +run() void
        +requires_position() false
        +has_manual_throttle() false
        +is_autopilot() false
    }
    class ModeLoiter {
        +mode_number() LOITER
        +init(bool) bool
        +run() void
        +requires_position() true
        +has_manual_throttle() false
        +is_autopilot() false
    }
    class ModeAuto {
        +mode_number() AUTO
        +init(bool) bool
        +run() void
        +requires_position() true
        +has_manual_throttle() false
        +is_autopilot() true
    }
    class ModeGuided {
        +mode_number() GUIDED
        +init(bool) bool
        +run() void
        +requires_position() true
        +has_manual_throttle() false
        +is_autopilot() true
    }
    class ModeRTL {
        +mode_number() RTL
        +init(bool) bool
        +run() void
        +requires_position() true
        +has_manual_throttle() false
        +is_autopilot() true
    }
    Mode &lt;|-- ModeStabilize
    Mode &lt;|-- ModeAltHold
    Mode &lt;|-- ModeLoiter
    Mode &lt;|-- ModeAuto
    Mode &lt;|-- ModeGuided
    Mode &lt;|-- ModeRTL
</pre><h2 id="_3-stabilize-모드" tabindex="-1"><a class="header-anchor" href="#_3-stabilize-모드"><span>3. Stabilize 모드</span></a></h2><h3 id="특성" tabindex="-1"><a class="header-anchor" href="#특성"><span>특성</span></a></h3><table><thead><tr><th>항목</th><th>값</th></tr></thead><tbody><tr><td>requires_position()</td><td>false (GPS 불필요)</td></tr><tr><td>has_manual_throttle()</td><td>true</td></tr><tr><td>is_autopilot()</td><td>false</td></tr><tr><td>사용 제어 계층</td><td>자세 루프 + 각속도 루프</td></tr></tbody></table><h3 id="run-분석" tabindex="-1"><a class="header-anchor" href="#run-분석"><span>run() 분석</span></a></h3><div class="language-cpp line-numbers-mode" data-highlighter="prismjs" data-ext="cpp" data-title="cpp"><pre><code><span class="line"><span class="token keyword">void</span> <span class="token class-name">ModeStabilize</span><span class="token double-colon punctuation">::</span><span class="token function">run</span><span class="token punctuation">(</span><span class="token punctuation">)</span></span>
<span class="line"><span class="token punctuation">{</span></span>
<span class="line">    <span class="token comment">// 스틱 → 목표 롤/피치 각도</span></span>
<span class="line">    <span class="token keyword">float</span> target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">;</span></span>
<span class="line">    <span class="token function">get_pilot_desired_lean_angles_rad</span><span class="token punctuation">(</span></span>
<span class="line">        target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">,</span></span>
<span class="line">        attitude_control<span class="token operator">-&gt;</span><span class="token function">lean_angle_max_rad</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">,</span></span>
<span class="line">        attitude_control<span class="token operator">-&gt;</span><span class="token function">lean_angle_max_rad</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 스틱 → 목표 요 각속도</span></span>
<span class="line">    <span class="token keyword">float</span> target_yaw_rate_rads <span class="token operator">=</span> <span class="token function">get_pilot_desired_yaw_rate_rads</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 스로틀 → 스풀 상태 결정</span></span>
<span class="line">    <span class="token keyword">if</span> <span class="token punctuation">(</span>copter<span class="token punctuation">.</span>ap<span class="token punctuation">.</span>throttle_zero<span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">        motors<span class="token operator">-&gt;</span><span class="token function">set_desired_spool_state</span><span class="token punctuation">(</span></span>
<span class="line">            AP_Motors<span class="token double-colon punctuation">::</span>DesiredSpoolState<span class="token double-colon punctuation">::</span>GROUND_IDLE<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">}</span> <span class="token keyword">else</span> <span class="token punctuation">{</span></span>
<span class="line">        motors<span class="token operator">-&gt;</span><span class="token function">set_desired_spool_state</span><span class="token punctuation">(</span></span>
<span class="line">            AP_Motors<span class="token double-colon punctuation">::</span>DesiredSpoolState<span class="token double-colon punctuation">::</span>THROTTLE_UNLIMITED<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">float</span> pilot_desired_throttle <span class="token operator">=</span> <span class="token function">get_pilot_desired_throttle</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 자세 컨트롤러 호출 — 목표 롤/피치(각도) + 목표 요(각속도)</span></span>
<span class="line">    attitude_control<span class="token operator">-&gt;</span><span class="token function">input_euler_angle_roll_pitch_euler_rate_yaw_rad</span><span class="token punctuation">(</span></span>
<span class="line">        target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">,</span> target_yaw_rate_rads<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 스로틀 직접 출력 — 위치 컨트롤러 사용 안 함</span></span>
<span class="line">    attitude_control<span class="token operator">-&gt;</span><span class="token function">set_throttle_out</span><span class="token punctuation">(</span></span>
<span class="line">        pilot_desired_throttle<span class="token punctuation">,</span> <span class="token boolean">true</span><span class="token punctuation">,</span> g<span class="token punctuation">.</span>throttle_filt<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>(ArduCopter/mode_stabilize.cpp:9~64)</code></p><p><code>input_euler_angle_roll_pitch_euler_rate_yaw_rad</code>는 자세 컨트롤러(AC_AttitudeControl)에 <strong>각도 목표</strong>를 전달한다. 자세 컨트롤러 내부에서 현재 자세와의 오차를 계산해 각속도 목표를 생성하고, 각속도 PID를 통해 모터 출력을 결정한다.</p><p>중요한 점은 <code>set_throttle_out</code>을 직접 호출한다는 것이다. 위치 컨트롤러(<code>pos_control</code>)를 거치지 않으므로 고도는 조종사가 스로틀로 직접 제어한다. 손을 놓으면 그 자리에 멈추지 않고 천천히 내려간다.</p><h3 id="stabilize-흐름" tabindex="-1"><a class="header-anchor" href="#stabilize-흐름"><span>Stabilize 흐름</span></a></h3><pre class="mermaid">flowchart TD
    Stick[&quot;조종사 스틱 입력&lt;br&gt;RC_Channel::control_in&quot;] --&gt; Angles[&quot;get_pilot_desired_lean_angles_rad()&lt;br&gt;roll_rad, pitch_rad&quot;]
    Stick --&gt; Yaw[&quot;get_pilot_desired_yaw_rate_rads()&lt;br&gt;yaw_rate_rads&quot;]
    Stick --&gt; Thr[&quot;get_pilot_desired_throttle()&lt;br&gt;0.0 ~ 1.0&quot;]
    Angles --&gt; AC[&quot;attitude_control-&gt;&lt;br&gt;input_euler_angle_roll_pitch_euler_rate_yaw_rad()&quot;]
    Yaw --&gt; AC
    AC --&gt; PID[&quot;자세 PID&lt;br&gt;→ 각속도 목표&quot;]
    PID --&gt; Motor[&quot;motors-&gt;output()&quot;]
    Thr --&gt; ThrottleOut[&quot;attitude_control-&gt;&lt;br&gt;set_throttle_out()&quot;]
    ThrottleOut --&gt; Motor
</pre><h2 id="_4-althold-모드" tabindex="-1"><a class="header-anchor" href="#_4-althold-모드"><span>4. AltHold 모드</span></a></h2><h3 id="특성-1" tabindex="-1"><a class="header-anchor" href="#특성-1"><span>특성</span></a></h3><table><thead><tr><th>항목</th><th>값</th></tr></thead><tbody><tr><td>requires_position()</td><td>false (GPS 불필요)</td></tr><tr><td>has_manual_throttle()</td><td>false</td></tr><tr><td>is_autopilot()</td><td>false</td></tr><tr><td>사용 제어 계층</td><td>수직 속도 루프 + 자세 루프</td></tr></tbody></table><h3 id="run-분석-1" tabindex="-1"><a class="header-anchor" href="#run-분석-1"><span>run() 분석</span></a></h3><p>AltHold는 Stabilize와 비슷하지만 스로틀 부분이 다르다. 조종사의 스로틀 스틱은 **목표 상승/하강 속도(climb rate)**로 해석된다:</p><div class="language-cpp line-numbers-mode" data-highlighter="prismjs" data-ext="cpp" data-title="cpp"><pre><code><span class="line"><span class="token keyword">void</span> <span class="token class-name">ModeAltHold</span><span class="token double-colon punctuation">::</span><span class="token function">run</span><span class="token punctuation">(</span><span class="token punctuation">)</span></span>
<span class="line"><span class="token punctuation">{</span></span>
<span class="line">    <span class="token comment">// 수평 자세: Stabilize와 동일</span></span>
<span class="line">    <span class="token keyword">float</span> target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">;</span></span>
<span class="line">    <span class="token function">get_pilot_desired_lean_angles_rad</span><span class="token punctuation">(</span>target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">,</span> <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token keyword">float</span> target_yaw_rate_rads <span class="token operator">=</span> <span class="token function">get_pilot_desired_yaw_rate_rads</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 스로틀 스틱 → 목표 상승 속도 (m/s)</span></span>
<span class="line">    <span class="token keyword">float</span> target_climb_rate_ms <span class="token operator">=</span> <span class="token function">get_pilot_desired_climb_rate_ms</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    AltHoldModeState althold_state <span class="token operator">=</span> <span class="token function">get_alt_hold_state_D_ms</span><span class="token punctuation">(</span>target_climb_rate_ms<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token keyword">switch</span> <span class="token punctuation">(</span>althold_state<span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">case</span> AltHoldModeState<span class="token double-colon punctuation">::</span>Flying<span class="token operator">:</span></span>
<span class="line">        <span class="token comment">// 위치 컨트롤러에 목표 상승 속도 전달</span></span>
<span class="line">        pos_control<span class="token operator">-&gt;</span><span class="token function">D_set_pos_target_from_climb_rate_ms</span><span class="token punctuation">(</span>target_climb_rate_ms<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">        <span class="token keyword">break</span><span class="token punctuation">;</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line">    <span class="token punctuation">}</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 자세 컨트롤러 (수평)</span></span>
<span class="line">    attitude_control<span class="token operator">-&gt;</span><span class="token function">input_euler_angle_roll_pitch_euler_rate_yaw_rad</span><span class="token punctuation">(</span></span>
<span class="line">        target_roll_rad<span class="token punctuation">,</span> target_pitch_rad<span class="token punctuation">,</span> target_yaw_rate_rads<span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"></span>
<span class="line">    <span class="token comment">// 수직 위치 컨트롤러 실행 → 스로틀 자동 출력</span></span>
<span class="line">    pos_control<span class="token operator">-&gt;</span><span class="token function">D_update_controller</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>(ArduCopter/mode_althold.cpp:26~103)</code></p><p><code>D_set_pos_target_from_climb_rate_ms</code>는 현재 고도를 기준으로 목표 고도를 적분한다. <code>D_update_controller</code>는 목표 고도와 현재 고도의 오차를 PID로 처리해 스로틀을 자동 출력한다. 조종사는 스로틀에서 손을 놓으면(중립) 현재 고도를 유지하게 된다.</p><h2 id="_5-loiter-모드" tabindex="-1"><a class="header-anchor" href="#_5-loiter-모드"><span>5. Loiter 모드</span></a></h2><h3 id="특성-2" tabindex="-1"><a class="header-anchor" href="#특성-2"><span>특성</span></a></h3><table><thead><tr><th>항목</th><th>값</th></tr></thead><tbody><tr><td>requires_position()</td><td>true (GPS 필수)</td></tr><tr><td>has_manual_throttle()</td><td>false</td></tr><tr><td>is_autopilot()</td><td>false</td></tr><tr><td>사용 제어 계층</td><td>수평 위치 루프 + 수직 속도 루프 + 자세 루프</td></tr></tbody></table><p>Loiter는 수평 방향도 위치 컨트롤러가 관리한다. 스틱 중립에서 현재 GPS 위치를 유지하고, 스틱을 밀면 목표 위치가 이동한다. 강한 바람이 불어도 GPS 피드백으로 위치를 보정한다. <code>requires_position() = true</code>이므로 EKF GPS 위치 추정이 없으면 모드 전환이 거부된다.</p><h2 id="_6-모드별-제어-계층-비교" tabindex="-1"><a class="header-anchor" href="#_6-모드별-제어-계층-비교"><span>6. 모드별 제어 계층 비교</span></a></h2><table><thead><tr><th>모드</th><th>GPS 필요</th><th>수평 위치 루프</th><th>수직 위치 루프</th><th>스로틀</th><th>자동조종</th></tr></thead><tbody><tr><td>Stabilize</td><td>N</td><td>X</td><td>X</td><td>직접</td><td>N</td></tr><tr><td>Acro</td><td>N</td><td>X</td><td>X</td><td>직접</td><td>N</td></tr><tr><td>AltHold</td><td>N</td><td>X</td><td>O (수직)</td><td>자동</td><td>N</td></tr><tr><td>PosHold</td><td>Y</td><td>O (느슨)</td><td>O</td><td>자동</td><td>N</td></tr><tr><td>Loiter</td><td>Y</td><td>O</td><td>O</td><td>자동</td><td>N</td></tr><tr><td>Auto</td><td>Y</td><td>O</td><td>O</td><td>자동</td><td>Y</td></tr><tr><td>Guided</td><td>Y</td><td>O</td><td>O</td><td>자동</td><td>Y</td></tr><tr><td>RTL</td><td>Y</td><td>O</td><td>O</td><td>자동</td><td>Y</td></tr><tr><td>Land</td><td>Y</td><td>O</td><td>O</td><td>자동</td><td>Y</td></tr></tbody></table><p>&quot;수평 위치 루프 O&quot;는 <code>wp_nav</code> 또는 <code>pos_control</code>의 NE 축이 활성화됨을 의미한다.</p><pre class="mermaid">flowchart TB
    subgraph Stabilize[&quot;Stabilize — 자세만&quot;]
        S_input[&quot;스틱 roll/pitch/yaw&lt;br&gt;스틱 throttle&quot;] --&gt; S_att[&quot;attitude_control&lt;br&gt;자세 PID&quot;]
        S_att --&gt; S_mot[&quot;motors&quot;]
    end
    subgraph AltHold[&quot;AltHold — 수직 루프 추가&quot;]
        A_input[&quot;스틱 roll/pitch/yaw&lt;br&gt;스틱 = climb rate&quot;] --&gt; A_att[&quot;attitude_control&lt;br&gt;자세 PID&quot;]
        A_thr[&quot;pos_control D&lt;br&gt;수직 PID&lt;br&gt;→ 스로틀 자동&quot;] --&gt; A_mot[&quot;motors&quot;]
        A_att --&gt; A_mot
    end
    subgraph Loiter[&quot;Loiter — 수평+수직 루프&quot;]
        L_input[&quot;스틱 = 수평 속도 목표&lt;br&gt;스틱 = climb rate&quot;] --&gt; L_wp[&quot;wp_nav / pos_control NE&lt;br&gt;수평 PID → 자세 목표&quot;]
        L_wp --&gt; L_att[&quot;attitude_control&quot;]
        L_thr[&quot;pos_control D&lt;br&gt;수직 PID&quot;] --&gt; L_mot[&quot;motors&quot;]
        L_att --&gt; L_mot
    end
</pre><h2 id="_7-모드-전환과-init" tabindex="-1"><a class="header-anchor" href="#_7-모드-전환과-init"><span>7. 모드 전환과 init()</span></a></h2><p>비행 중 조종사가 모드 전환 스위치를 조작하면 <code>Copter::set_mode()</code>가 호출된다. 새 모드의 <code>init()</code>이 false를 반환하면 전환이 거부된다.</p><p>Auto 모드 전환 거부 조건의 예:</p><div class="language-cpp line-numbers-mode" data-highlighter="prismjs" data-ext="cpp" data-title="cpp"><pre><code><span class="line"><span class="token keyword">bool</span> <span class="token class-name">ModeAuto</span><span class="token double-colon punctuation">::</span><span class="token function">init</span><span class="token punctuation">(</span><span class="token keyword">bool</span> ignore_checks<span class="token punctuation">)</span></span>
<span class="line"><span class="token punctuation">{</span></span>
<span class="line">    <span class="token keyword">if</span> <span class="token punctuation">(</span>motors<span class="token operator">-&gt;</span><span class="token function">armed</span><span class="token punctuation">(</span><span class="token punctuation">)</span> <span class="token operator">&amp;&amp;</span> copter<span class="token punctuation">.</span>ap<span class="token punctuation">.</span>land_complete</span>
<span class="line">        <span class="token operator">&amp;&amp;</span> <span class="token operator">!</span>mission<span class="token punctuation">.</span><span class="token function">starts_with_takeoff_cmd</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">)</span> <span class="token punctuation">{</span></span>
<span class="line">        <span class="token function">gcs</span><span class="token punctuation">(</span><span class="token punctuation">)</span><span class="token punctuation">.</span><span class="token function">send_text</span><span class="token punctuation">(</span>MAV_SEVERITY_CRITICAL<span class="token punctuation">,</span></span>
<span class="line">            <span class="token string">&quot;Auto: Missing Takeoff Cmd&quot;</span><span class="token punctuation">)</span><span class="token punctuation">;</span></span>
<span class="line">        <span class="token keyword">return</span> <span class="token boolean">false</span><span class="token punctuation">;</span>   <span class="token comment">// 착지 + 아밍 상태에서 이륙 명령 없으면 거부</span></span>
<span class="line">    <span class="token punctuation">}</span></span>
<span class="line">    <span class="token punctuation">.</span><span class="token punctuation">.</span><span class="token punctuation">.</span></span>
<span class="line">    <span class="token keyword">return</span> <span class="token boolean">true</span><span class="token punctuation">;</span></span>
<span class="line"><span class="token punctuation">}</span></span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p><code>(ArduCopter/mode_auto.cpp:23~67)</code></p><p>Loiter 모드는 <code>requires_position() = true</code>이므로, 이를 체크하는 <code>Copter::set_mode()</code>에서 EKF GPS 위치 추정이 없으면 자동 거부된다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>Mode 베이스 클래스는 <code>mode_number()</code>, <code>run()</code>을 순수 가상으로 강제한다. <code>requires_position()</code>, <code>has_manual_throttle()</code>, <code>is_autopilot()</code>이 모드 특성을 선언한다.</li><li>Stabilize: 자세 루프만. 스로틀 직접 출력. GPS 불필요. <code>attitude_control-&gt;set_throttle_out()</code> 직접 호출.</li><li>AltHold: 자세 루프 + 수직 위치 루프. 스틱은 climb rate. <code>pos_control-&gt;D_set_pos_target_from_climb_rate_ms()</code> + <code>D_update_controller()</code>.</li><li>Loiter: 자세 + 수직 + 수평 위치 루프 모두. GPS 필수.</li><li>Auto/Guided/RTL은 <code>is_autopilot() = true</code>로, 모든 제어 루프를 FC가 자율 관리한다.</li><li>모드 전환 시 <code>init()</code> 실패는 전환 거부를 의미한다. Loiter 이상의 모드는 EKF GPS 위치 추정이 없으면 진입 자체가 차단된다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p><a href="/study/ardupilot/26-auto-mission">CH26. 자동 비행과 미션</a>에서는 AP_Mission의 명령 저장 구조, ModeAuto의 서브모드 디스패치, 이륙 시퀀스, Guided 모드의 외부 명령 주입, RTL 상태 머신을 분석한다.</p>`,54)]))}const c=s(l,[["render",p],["__file","25-flight-modes.html.vue"]]),d=JSON.parse('{"path":"/study/ardupilot/25-flight-modes.html","title":"CH25. 비행 모드 구조","lang":"en-US","frontmatter":{"title":"CH25. 비행 모드 구조","description":"ArduCopter의 비행 모드 시스템을 분석한다. Mode 추상 베이스 클래스의 가상 함수 계약, 수동 계열 모드(Stabilize/AltHold/Loiter)가 제어 루프의 어느 계층부터 개입하는지, 그리고 모드별 GPS·자동조종·스로틀 특성을 소스로 따라간다.","date":"2026-06-22T00:00:00.000Z","tags":["ArduPilot","비행모드","Stabilize","AltHold","Loiter","Mode","run루프","제어계층","UAV","임베디드"],"prev":"/study/ardupilot/24-rc-telemetry","next":"/study/ardupilot/26-auto-mission"},"headers":[{"level":1,"title":"CH25. 비행 모드 구조","slug":"ch25-비행-모드-구조","link":"#ch25-비행-모드-구조","children":[{"level":2,"title":"1. Mode 베이스 클래스","slug":"_1-mode-베이스-클래스","link":"#_1-mode-베이스-클래스","children":[{"level":3,"title":"모드 번호 열거형","slug":"모드-번호-열거형","link":"#모드-번호-열거형","children":[]},{"level":3,"title":"핵심 가상 함수","slug":"핵심-가상-함수","link":"#핵심-가상-함수","children":[]},{"level":3,"title":"제어 계층(cascade) 복습","slug":"제어-계층-cascade-복습","link":"#제어-계층-cascade-복습","children":[]}]},{"level":2,"title":"2. Mode 클래스 계층","slug":"_2-mode-클래스-계층","link":"#_2-mode-클래스-계층","children":[]},{"level":2,"title":"3. Stabilize 모드","slug":"_3-stabilize-모드","link":"#_3-stabilize-모드","children":[{"level":3,"title":"특성","slug":"특성","link":"#특성","children":[]},{"level":3,"title":"run() 분석","slug":"run-분석","link":"#run-분석","children":[]},{"level":3,"title":"Stabilize 흐름","slug":"stabilize-흐름","link":"#stabilize-흐름","children":[]}]},{"level":2,"title":"4. AltHold 모드","slug":"_4-althold-모드","link":"#_4-althold-모드","children":[{"level":3,"title":"특성","slug":"특성-1","link":"#특성-1","children":[]},{"level":3,"title":"run() 분석","slug":"run-분석-1","link":"#run-분석-1","children":[]}]},{"level":2,"title":"5. Loiter 모드","slug":"_5-loiter-모드","link":"#_5-loiter-모드","children":[{"level":3,"title":"특성","slug":"특성-2","link":"#특성-2","children":[]}]},{"level":2,"title":"6. 모드별 제어 계층 비교","slug":"_6-모드별-제어-계층-비교","link":"#_6-모드별-제어-계층-비교","children":[]},{"level":2,"title":"7. 모드 전환과 init()","slug":"_7-모드-전환과-init","link":"#_7-모드-전환과-init","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/ardupilot/25-flight-modes.md"}');export{c as comp,d as data};
