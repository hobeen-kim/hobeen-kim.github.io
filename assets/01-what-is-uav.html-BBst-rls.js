import{_ as n,c as o,f as e,o as d}from"./app-DFRPTWct.js";const r={};function l(a,t){return d(),o("div",null,t[0]||(t[0]=[e(`<h1 id="uav란-무엇인가" tabindex="-1"><a class="header-anchor" href="#uav란-무엇인가"><span>UAV란 무엇인가</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>UAV(무인항공기)와 무인이동체의 개념을 정의하고, ArduPilot이 지원하는 6종 차량을 구분할 수 있다.</li><li>멀티콥터가 4개 로터 추력의 차이로 자세를 제어하는 원리를 설명할 수 있다.</li><li>왜 멀티콥터가 본질적으로 불안정(unstable)한지, 이것이 제어 시스템에 어떤 요구를 만드는지 이해한다.</li><li>오토파일럿이 하는 일을 &quot;센서 → 상태추정 → 제어 → 액추에이터&quot; 폐루프로 설명할 수 있다.</li><li>이후 챕터(스케줄러, 센서, EKF, 제어 루프)가 왜 필요한지 전체 그림을 그릴 수 있다.</li></ul></div><h2 id="_1-uav-드론-무인이동체" tabindex="-1"><a class="header-anchor" href="#_1-uav-드론-무인이동체"><span>1. UAV, 드론, 무인이동체</span></a></h2><p><strong>UAV(Unmanned Aerial Vehicle)</strong>는 조종사가 탑승하지 않고 비행하는 항공기를 통칭한다. 일상에서는 &#39;드론(drone)&#39;이라는 단어가 더 흔히 쓰이지만, 드론은 원래 군용 표적기를 가리키는 말이었다. 현재는 멀티콥터·고정익·헬리콥터 형태의 소형 무인기를 두루 드론이라 부른다.</p><p>더 넓은 범주는 <strong>무인이동체(UxV)</strong>다. 공중을 나는 UAV뿐 아니라 지상을 달리는 UGV(Unmanned Ground Vehicle), 수면을 항행하는 USV(Unmanned Surface Vehicle), 수중을 유영하는 UUV(Unmanned Underwater Vehicle)까지 포함한다. ArduPilot은 이 모든 종류를 하나의 오픈소스 코드베이스로 지원한다.</p><h3 id="ardupilot이-지원하는-6종-차량" tabindex="-1"><a class="header-anchor" href="#ardupilot이-지원하는-6종-차량"><span>ArduPilot이 지원하는 6종 차량</span></a></h3><p>ArduPilot 레포지토리(<code>/tmp/ardupilot_study/</code>) 최상위 디렉토리를 보면 차량 타입별 디렉토리가 그대로 존재한다(<code>README.md</code> 참고).</p><table><thead><tr><th>디렉토리</th><th>차량 타입</th><th>대표 플랫폼</th></tr></thead><tbody><tr><td><code>ArduCopter/</code></td><td>멀티콥터 / 헬리콥터</td><td>쿼드콥터, 헥사콥터, 전통 헬리</td></tr><tr><td><code>ArduPlane/</code></td><td>고정익 / 틸트로터 VTOL</td><td>일반 비행기, QuadPlane</td></tr><tr><td><code>Rover/</code></td><td>지상차량 / 보트</td><td>4륜 로버, 스키드 스티어 보트</td></tr><tr><td><code>ArduSub/</code></td><td>잠수정 (ROV)</td><td>수중 드론, ROV</td></tr><tr><td><code>Blimp/</code></td><td>비행선 (Blimp)</td><td>소형 실내 비행선</td></tr><tr><td><code>AntennaTracker/</code></td><td>안테나 추적기</td><td>지상국 안테나 자동 추적</td></tr></tbody></table><p><code>README.md</code>는 ArduPilot을 다음과 같이 소개한다.</p><blockquote><p>&quot;ArduPilot is the most advanced, full-featured, and reliable open source autopilot software available. It has been under development since 2010 by a diverse team of professional engineers, computer scientists, and community contributors.&quot;</p></blockquote><p>6개 차량 모두 <code>libraries/</code> 폴더의 공통 라이브러리(AP_HAL, AP_GPS, AP_Baro, AP_AHRS, EKF3 등)를 공유한다. 차량 타입별로 추가 라이브러리만 교체하는 구조다. 이 공유 구조는 03장에서 자세히 다룬다.</p><pre class="mermaid">mindmap
  root((ArduPilot 차량))
    ArduCopter
      쿼드콥터
      헥사콥터
      옥토콥터
      전통 헬리콥터
    ArduPlane
      고정익
      VTOL QuadPlane
      글라이더
    Rover
      지상 차량
      보트 / USV
    ArduSub
      ROV 잠수정
      AUV
    Blimp
      실내 비행선
    AntennaTracker
      안테나 추적기
</pre><h2 id="_2-오토파일럿이란-무엇인가" tabindex="-1"><a class="header-anchor" href="#_2-오토파일럿이란-무엇인가"><span>2. 오토파일럿이란 무엇인가</span></a></h2><p>비행기를 조종한다는 것은 매 순간 기체의 자세와 위치를 파악하고 그에 맞게 제어 입력을 내리는 일이다. 사람이 이 일을 직접 하면 RC 조종기(수동 조종), 자동화 장치가 대신 하면 <strong>오토파일럿(autopilot)</strong>이다.</p><p>오토파일럿의 핵심은 <strong>폐루프 제어(closed-loop control)</strong>다. 단순히 미리 짜둔 명령을 순서대로 실행하는 것이 아니라, 실제 측정값과 목표값의 차이(오차)를 계속 보면서 제어 입력을 조정한다. 세 단계가 반복된다.</p><ol><li><strong>측정</strong> — IMU(자이로·가속도계), GPS, 기압계, 나침반 등 센서로 현재 상태를 측정한다.</li><li><strong>추정</strong> — 노이즈가 많은 센서 데이터를 EKF(Extended Kalman Filter)로 융합해 자세·위치·속도를 추정한다.</li><li><strong>제어</strong> — 목표값과 추정값의 오차를 PID 컨트롤러로 계산해 각 모터·서보에 출력한다.</li></ol><p>이 세 단계가 초당 수백 번 반복된다. ArduCopter의 기본 루프 속도는 400 Hz다(<code>libraries/AP_Scheduler/AP_Scheduler.cpp:44</code> — <code>SCHEDULER_DEFAULT_LOOP_RATE 400</code>).</p><pre class="mermaid">flowchart LR
    SENSOR[&quot;센서\\nIMU · GPS · Baro\\n나침반 · 광류센서&quot;]
    EKF[&quot;상태추정\\nEKF3 / AHRS\\n자세·위치·속도&quot;]
    CTL[&quot;비행 제어\\nPID 컨트롤러\\n자세·위치 루프&quot;]
    ACT[&quot;액추에이터\\nESC · 모터\\n서보&quot;]
    WORLD[&quot;물리 세계\\n기체 운동&quot;]

    SENSOR --&gt;|&quot;센서 데이터&quot;| EKF
    EKF --&gt;|&quot;추정 상태&quot;| CTL
    CTL --&gt;|&quot;제어 명령&quot;| ACT
    ACT --&gt;|&quot;추력·토크&quot;| WORLD
    WORLD --&gt;|&quot;다음 상태 변화&quot;| SENSOR
</pre><p>각 단계는 이 스터디의 별도 섹션으로 깊이 다룬다. 지금은 &quot;폐루프가 초당 수백 번 돌아야 한다&quot;는 사실만 기억하면 충분하다.</p><h2 id="_3-멀티콥터-비행-원리" tabindex="-1"><a class="header-anchor" href="#_3-멀티콥터-비행-원리"><span>3. 멀티콥터 비행 원리</span></a></h2><p>멀티콥터는 여러 개의 로터(rotor)가 만드는 추력으로 날아다닌다. 가장 흔한 형태는 <strong>쿼드콥터(quadrotor)</strong> — 로터 4개.</p><h3 id="_3-1-추력으로-자세를-바꾸는-방법" tabindex="-1"><a class="header-anchor" href="#_3-1-추력으로-자세를-바꾸는-방법"><span>3.1 추력으로 자세를 바꾸는 방법</span></a></h3><p>각 모터는 위로 향하는 추력(thrust)을 발생시킨다. 4개 모터의 추력 합이 중력보다 크면 기체가 뜨고, 같으면 제자리에 뜨고, 작으면 내려온다.</p><p>자세 제어는 4개 모터 추력의 <strong>차이(差)</strong>로 이루어진다.</p><ul><li><strong>Roll(좌우 기울기)</strong> — 좌측 두 모터를 올리고 우측 두 모터를 낮추면 우측으로 기운다.</li><li><strong>Pitch(앞뒤 기울기)</strong> — 앞 두 모터를 낮추고 뒤 두 모터를 올리면 앞으로 기운다.</li><li><strong>Yaw(좌우 방향 회전)</strong> — 모터는 회전하면서 토크 반작용(Newton의 제3법칙)이 기체에 전달된다. 쿼드콥터는 대각선 방향 두 모터가 시계방향, 나머지 두 모터가 반시계방향으로 돌도록 설계된다. 같은 방향 모터 두 개의 속도를 올리면 그 반작용으로 기체가 반대 방향으로 돈다.</li><li><strong>Throttle(상승/하강)</strong> — 4개 모터를 동시에 올리거나 낮춘다.</li></ul><p>이 네 가지 제어 입력(roll, pitch, yaw, throttle)이 모터 믹싱 행렬을 통해 4개 모터 속도 명령으로 변환된다. 모터 믹싱은 23장에서 다룬다.</p><h3 id="_3-2-본질적-불안정성" tabindex="-1"><a class="header-anchor" href="#_3-2-본질적-불안정성"><span>3.2 본질적 불안정성</span></a></h3><p>고정익 항공기는 날개 형상 덕분에 기류를 가르며 스스로 수평을 유지하려는 경향(양의 정적 안정성)이 있다. 하지만 멀티콥터는 <strong>본질적으로 불안정(inherently unstable)</strong>하다.</p><p>로터 하나라도 정지하면 기체는 즉시 한쪽으로 기울기 시작하며, 아무런 제어 없이는 1초도 안 돼 추락한다. 중력과 로터 추력이 정확히 균형을 이루지 않는 한, 기체는 항상 어느 방향으로든 가속한다. 이것이 사람이 손으로 멀티콥터 균형을 잡기 어려운 이유다.</p><p>그러므로 오토파일럿은 <strong>매우 빠르게, 매우 자주</strong> 모터 속도를 조정해야 한다. ArduCopter가 400 Hz 루프를 사용하는 이유가 바로 여기에 있다. 이 요구사항이 뒤에서 다룰 스케줄러(07장)의 설계 동기다.</p><div class="hint-container tip"><p class="hint-container-title">고정익과의 차이</p><p>고정익(ArduPlane)은 양력이 날개에서 나오므로 기본 안정성이 있다. 그래서 ArduPlane의 기본 루프 속도는 50 Hz다(<code>libraries/AP_Scheduler/AP_Scheduler.cpp:46</code> — <code>SCHEDULER_DEFAULT_LOOP_RATE 50</code>). 멀티콥터 400 Hz와 8배 차이가 난다. &quot;왜 스케줄러가 그렇게 설계됐는가&quot;는 이 물리적 차이에서 시작한다.</p></div><pre class="mermaid">flowchart TD
    subgraph Quad[&quot;쿼드콥터 — 4개 모터&quot;]
        M1[&quot;모터 1\\n반시계&quot;]
        M2[&quot;모터 2\\n시계&quot;]
        M3[&quot;모터 3\\n반시계&quot;]
        M4[&quot;모터 4\\n시계&quot;]
        FRAME[&quot;기체 프레임&quot;]
        M1 --- FRAME
        M2 --- FRAME
        M3 --- FRAME
        M4 --- FRAME
    end
    subgraph CTRL[&quot;제어 입력 → 모터 조합&quot;]
        TH[&quot;Throttle\\n4개 동시 조절&quot;]
        ROLL[&quot;Roll\\n좌우 모터 차이&quot;]
        PITCH[&quot;Pitch\\n전후 모터 차이&quot;]
        YAW[&quot;Yaw\\n대각 모터 차이\\n토크 반작용&quot;]
    end
    CTRL --&gt; Quad
</pre><h2 id="_4-ardupilot-오토파일럿-개관-—-이-스터디의-지도" tabindex="-1"><a class="header-anchor" href="#_4-ardupilot-오토파일럿-개관-—-이-스터디의-지도"><span>4. ArduPilot 오토파일럿 개관 — 이 스터디의 지도</span></a></h2><p>ArduPilot이 비행 중에 실제로 하는 일을 한 눈에 보면 다음과 같다.</p><pre class="mermaid">flowchart TD
    subgraph HW[&quot;하드웨어 계층&quot;]
        IMU[&quot;IMU\\n가속도계 + 자이로&quot;]
        GPS2[&quot;GPS&quot;]
        BARO[&quot;기압계&quot;]
        MAG[&quot;나침반&quot;]
        RC2[&quot;RC 수신기&quot;]
    end
    subgraph HAL[&quot;HAL — 하드웨어 추상화&quot;]
        DRIVER[&quot;센서 드라이버\\nSPI·I2C·UART&quot;]
        SCHED[&quot;AP_Scheduler\\n400 Hz 루프&quot;]
    end
    subgraph EST[&quot;상태추정&quot;]
        AHRS2[&quot;AHRS / DCM\\n자세 추정&quot;]
        EKF2[&quot;EKF3\\n위치·속도 추정&quot;]
    end
    subgraph CTL2[&quot;비행 제어&quot;]
        ATT2[&quot;자세 제어\\nAC_AttitudeControl&quot;]
        POS2[&quot;위치·경로\\nAC_PosControl · AC_WPNav&quot;]
        PID3[&quot;PID 루프\\nAC_PID&quot;]
    end
    subgraph OUT2[&quot;출력&quot;]
        MIX2[&quot;모터 믹싱\\nAP_MotorsMulticopter&quot;]
        ESC2[&quot;ESC / 모터&quot;]
    end
    subgraph GCS2[&quot;통신&quot;]
        MAV[&quot;MAVLink\\nGCS 통신&quot;]
        LOG[&quot;DataFlash\\n비행 로그&quot;]
    end

    HW --&gt; HAL --&gt; EST --&gt; CTL2 --&gt; OUT2
    RC2 --&gt; CTL2
    CTL2 --&gt; GCS2
</pre><p>각 블록이 이 스터디에서 다루는 섹션이다.</p><table><thead><tr><th>블록</th><th>스터디 섹션</th></tr></thead><tbody><tr><td>HAL / 하드웨어 추상화</td><td>섹션 2 (04~06장)</td></tr><tr><td>AP_Scheduler</td><td>섹션 3 (07~08장)</td></tr><tr><td>센서 드라이버</td><td>섹션 4 (09~13장)</td></tr><tr><td>AHRS / EKF3</td><td>섹션 5 (14~18장)</td></tr><tr><td>PID / 자세·위치 제어</td><td>섹션 6 (19~23장)</td></tr><tr><td>RC 입력 / 비행 모드</td><td>섹션 7 (24~26장)</td></tr><tr><td>MAVLink / 안전 / 로그</td><td>섹션 8 (27~31장)</td></tr><tr><td>SITL / 스크립팅 / 통합</td><td>섹션 9 (32~34장)</td></tr></tbody></table><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>UAV는 조종사 없이 비행하는 무인항공기다. ArduPilot은 6종(멀티콥터·고정익·로버·잠수정·비행선·안테나추적기)을 하나의 코드베이스로 지원한다(<code>README.md</code>).</li><li>오토파일럿은 센서 → 상태추정 → 제어 → 액추에이터의 폐루프를 초당 수백 번 반복한다.</li><li>멀티콥터는 본질적으로 불안정하다. 4개 모터 추력 차이로 자세를 제어하며, ArduCopter는 이 때문에 400 Hz 제어 루프를 사용한다(<code>AP_Scheduler.cpp:44</code>).</li><li>고정익은 기본 안정성이 있어 50 Hz로도 충분하다. 이 차이가 이후 스케줄러·실시간성 챕터의 출발점이다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><p><a href="/study/ardupilot/02-embedded-basics">02. 임베디드 시스템 기초</a> — ArduPilot이 동작하는 하드웨어(MCU), RTOS, 실시간성 개념을 다룬다.</p>`,40)]))}const i=n(r,[["render",l],["__file","01-what-is-uav.html.vue"]]),s=JSON.parse('{"path":"/study/ardupilot/01-what-is-uav.html","title":"UAV란 무엇인가","lang":"en-US","frontmatter":{"title":"UAV란 무엇인가","description":"드론의 정의와 종류, 멀티콥터의 비행 원리, 오토파일럿이 필요한 이유, ArduPilot이 지원하는 6종 차량 개관.","date":"2026-06-22T00:00:00.000Z","tags":["ArduPilot","UAV","드론","멀티콥터","오토파일럿","비행 원리"],"prev":"/study/ardupilot/","next":"/study/ardupilot/02-embedded-basics"},"headers":[{"level":1,"title":"UAV란 무엇인가","slug":"uav란-무엇인가","link":"#uav란-무엇인가","children":[{"level":2,"title":"1. UAV, 드론, 무인이동체","slug":"_1-uav-드론-무인이동체","link":"#_1-uav-드론-무인이동체","children":[{"level":3,"title":"ArduPilot이 지원하는 6종 차량","slug":"ardupilot이-지원하는-6종-차량","link":"#ardupilot이-지원하는-6종-차량","children":[]}]},{"level":2,"title":"2. 오토파일럿이란 무엇인가","slug":"_2-오토파일럿이란-무엇인가","link":"#_2-오토파일럿이란-무엇인가","children":[]},{"level":2,"title":"3. 멀티콥터 비행 원리","slug":"_3-멀티콥터-비행-원리","link":"#_3-멀티콥터-비행-원리","children":[{"level":3,"title":"3.1 추력으로 자세를 바꾸는 방법","slug":"_3-1-추력으로-자세를-바꾸는-방법","link":"#_3-1-추력으로-자세를-바꾸는-방법","children":[]},{"level":3,"title":"3.2 본질적 불안정성","slug":"_3-2-본질적-불안정성","link":"#_3-2-본질적-불안정성","children":[]}]},{"level":2,"title":"4. ArduPilot 오토파일럿 개관 — 이 스터디의 지도","slug":"_4-ardupilot-오토파일럿-개관-—-이-스터디의-지도","link":"#_4-ardupilot-오토파일럿-개관-—-이-스터디의-지도","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/ardupilot/01-what-is-uav.md"}');export{i as comp,s as data};
