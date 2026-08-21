---
title: "표준 정리: Part 7 — Implement messages"
description: "ISO 11783-7(Implement messages application layer) — 트랙터-작업기 메시지와 파라미터, Amendment 1 변경 사항을 정리한 표준 요약이다."
date: 2026-08-21
tags: [ISOBUS, ISO11783, 표준정리]
---

# ISO 11783-7: Implement messages application layer 정리

::: info 이 문서에 대해
ISO 11783-7 표준 원문을 학습 목적으로 재구성한 <strong>비공식 요약·해설</strong>이다. 규범적 판단이 필요할 때는 반드시 원문 표준을 확인해야 한다.
:::

## 개요

ISO 11783-7은 ISO 11783 시리즈(총 14개 파트) 중 <strong>작업기(implement) 메시지 애플리케이션 계층</strong>을 정의하는 파트다. 트랙터와 작업기 사이, 그리고 작업기끼리 주고받는 메시지 집합을 규정한다. 문서 버전은 3판(2015-03-15)이며, 2판(2009)을 기술적으로 개정해 대체했다.

ISO 11783 전체는 ISO 11898-1(CAN) 기반의 농업·임업 장비용 직렬 데이터 네트워크를 규정한다. 트럭·버스용으로 개발된 SAE J1939 문서군과 공동으로 작성되어, J1939를 만족하는 전자 장치를 최소한의 변경으로 농기계에 쓸 수 있게 설계되었다. CAN 프로토콜 관련 특허(Robert Bosch GmbH)가 걸려 있을 수 있다는 점이 서문에 명시되어 있다.

:::warning 안전 주의
이 파트에 정의된 메시지로 작업기를 자동 제어할 때는 주의가 필요하다. 안전 모드(safe-mode) 동작은 ISO 11783-9(Tractor ECU)를 따른다.
:::

문서의 본문(1~3장)은 짧고, 실질 내용 대부분은 부속서에 있다.

| 구성 | 성격 | 내용 |
|---|---|---|
| 1~3장 | 본문 | 적용 범위, 인용 표준, 일반 요구사항(신호 특성, 메시지 포맷, 파라미터 범위) |
| Annex A | normative | 파라미터 정의(시간, 속도, 히치, PTO, 유압 밸브, 조명 등 수백 개) |
| Annex B | normative | Parameter group(PGN별 메시지 정의, 전송 주기·우선순위) |
| Annex C | informative | 트랙터 제어 메시지 예시 |
| Annex D | informative | 작업기에 의한 트랙터 기능 제어 구현 |

### 1장 Scope

이 파트는 네트워크의 implement messages application layer를 기술한다. 트랙터와 부착·견인·자주식 작업기 사이의 통신에 쓰는 메시지 집합을 규정하고, 센서·액추에이터·제어 요소·정보 저장/표시 장치 간 데이터 전송 방법과 포맷을 표준화하는 것이 목적이다.

### 2장 Normative references

ISO 639(언어 코드), ISO 11783-1/-3/-5/-6/-9/-10/-12, IEC 61162-3(NMEA 2000, 항법 데이터)이 필수 인용 표준이다. 항법 위치 파라미터를 IEC 61162-3에 위임하는 점이 특징이다.

## 3장 일반 요구사항과 권고

### 3.1 General — 메시지 집합의 범위

이 파트의 메시지 집합은 작업기가 트랙터로부터 필요로 하는 기본 정보 제공과, 트랙터-작업기 간 협조를 위한 제한적 제어를 지원하도록 설계되었다. 다루는 정보 범주는 다음과 같다.

- 시간(time)
- 대지 속도(ground speed)
- 이동 거리(distance)
- 항법(navigation)
- PTO(power take-off) 파라미터
- 3점 히치(three-point hitch)
- 일반 프로세스 데이터
- 조명(lighting) 기능 파라미터

메시지 중 일부는 고정 주기로 반복 송신되고, 일부는 요청(request) 시에만 송신된다. 메시지별 전송 요건은 Annex B에, 파라미터 정의는 Annex A에 있다.

### 3.2 Signal characterization

ISO 11783 네트워크는 어떤 ECU 안의 CF(control function)가 가진 최신 데이터를 같은/다른 ECU의 다른 CF가 쓸 수 있게 하는 것이 설계 의도다. CF·ECU 용어 정의는 ISO 11783-1을 따른다. <strong>신호의 물리적 취득 시점부터 송신까지의 지연은 해당 데이터의 반복 주기의 2배를 넘지 않을 것</strong>이 권고된다.

### 3.3 Message format

#### 3.3.1 기본 규칙

- PGN(parameter group number)이 파라미터 그룹의 라벨 역할을 한다.
- 그룹 내 각 파라미터는 문자(character), 스케일된 수치 데이터, 또는 1비트 이상의 기능 상태로 표현된다.
- 문자열은 왼쪽 문자부터 전송한다.
- 2바이트 이상의 수치 파라미터는 <strong>LSB(least significant byte) 먼저</strong> 전송한다(리틀 엔디언).
- 파라미터가 바이트 경계에 걸치면 하위 비트를 하위 바이트에, 나머지 상위 비트를 다음 바이트의 첫 비트부터 배치한다.

#### 3.3.2 데이터 타입 — Command vs Measured

모든 파라미터는 command 또는 measured 중 하나로 분류된다.

| 타입 | 의미 | 예 |
|---|---|---|
| Command | 송신 CF가 요구하는 목표 상태·설정값. 명령 수행의 확인은 보장되지 않는다 | PTO 체결, 보조 밸브 확장, 전조등 상향, 후방 히치 이동 |
| Measured | 송신 CF가 측정·관찰한 파라미터의 현재 값 | 대지 속도, 히치 위치, PTO 체결 상태, 작업기 in-work 상태 |

:::info 트랙터는 명령을 자동 실행하지 않는다
command는 "요청"이다. 트랙터는 받은 명령을 그대로 실행할 의무가 없고, 다른 트랙터 제어·운전 조건과 함께 고려해 <strong>트랙터 제어 시스템이 적절하다고 판단할 때만</strong> 실행한다. 제어 명령은 시스템에 운동·동력의 변화를 일으키므로 안전 판단이 트랙터 쪽에 남아 있는 구조다.
:::

#### 3.3.3 Parameter ranges — 값 범위 규약

전송 신호의 유효성 판정 범위(J1939와 동일한 관례)는 다음과 같다.

| 범위 이름 | 1 byte | 2 bytes | 4 bytes | ASCII |
|---|---|---|---|---|
| Valid signal | 0~250 (00~FA) | 0~64 255 (0000~FAFF) | 0~4 211 081 215 (…~FAFFFFFF) | 1~254 |
| Parameter-specific indicator | 251 (FB) | 64 256~64 511 (FBxx) | FBxxxxxx | 없음 |
| Reserved(향후 indicator) | 252~253 (FC~FD) | 64 512~65 023 | FCxxxxxx~FDxxxxxx | 없음 |
| Error indicator | 254 (FE) | 65 024~65 279 (FExx) | FExxxxxx | 0 |
| Not available/not installed/take no action | 255 (FF) | 65 280~65 535 (FFxx) | FFxxxxxx | 255 |

2비트 이산(discrete) 파라미터의 값 규약:

| 값 | Measured | Command |
|---|---|---|
| 00 | Disabled (Off, passive 등) | 기능 끄기 명령 |
| 01 | Enabled (On, active 등) | 기능 켜기 명령 |
| 10 | Error indicator | Reserved |
| 11 | Not available / not installed | Don't care — 현 상태 유지 |

에러 규칙: CF 고장으로 유효 데이터를 못 보내면 error indicator를 값 대신 넣는다. 단, <strong>측정값이 유효한데 정의된 범위를 초과한 경우에는 error indicator를 쓰지 않고</strong> 최소/최대 파라미터 값으로 잘라서 보낸다. 유효 여부를 판정할 수 없으면 error indicator를 보낸다.

예약 비트는 향후 호환성을 위해 원칙적으로 all 1("Not Available")로 채운다. 다만 Part 7 특유의 단일 비트 파라미터(기능 가용성 비트 등)는 메시지 정의에 따라 기본값이 0("not supported")인 경우가 있으므로 각 메시지 정의의 기대값을 따라야 한다.

#### 3.3.4 파라미터 그룹 확장

파라미터 그룹의 미정의 바이트는 향후 새 파라미터로 교체될 수 있다. 기존 그룹에 넣을 수 없으면 새 파라미터 그룹을 정의한다. 추가 절차는 ISO 11783-1을 따른다.

### 3.4 Implement configuration offsets

트랙터/작업기 연결 구성과 기준점(reference point) 간 오프셋은 항법 파라미터와 프로세스 데이터 메시지의 implement configuration에 사용된다. 상세는 ISO 11783-10을 따른다.

## Annex A — 파라미터 정의 (normative)

Annex A는 Part 7 메시지에 실리는 개별 파라미터를 정의한다. 각 파라미터는 데이터 길이, 분해능(resolution), 동작 범위, 타입(measured/command), SPN(suspect parameter number)으로 기술된다. 이하 주요 파라미터를 절 구조에 따라 정리한다.

### A.1~A.4 시간·날짜 파라미터

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Time (UTC) — A.1 | 3 bytes | Byte1: 0,25 s/bit (0~59,75 s), Byte2: 1 min/bit (0~59), Byte3: 1 h/bit (0~23) | Measured | 959/960/961 |
| Date — A.2 | 3 bytes | Byte1: 1 month/bit (1~12), Byte2: 0,25 d/bit (0,25~31,75 d), Byte3: 1 y/bit, 1985년 오프셋 (1985~2235) | Measured | 963/962/964 |
| Local minute offset — A.3 | 1 byte | 1 min/bit, −125 min 오프셋, −59~59 min | Measured | 1601 |
| Local hour offset — A.4 | 1 byte | 1 h/bit, −125 h 오프셋, −23~23 h | Measured | 1602 |

- 날짜의 day 필드가 0,25일 단위인 점에 주의: 값 1~4가 1일, 5~8이 2일을 뜻한다. month=0, day=0은 null이다.
- Local offset은 UTC에 더해서 지역 시각을 만드는 값이다. 본초자오선 동쪽(날짜변경선까지)이 양수, 서쪽이 음수다.
- <strong>Local hour offset = 125 (FA)이면 Time/Date 파라미터 자체가 UTC가 아니라 지역 시각</strong>이라는 의미다. 124(F9)는 "UTC이며 오프셋 미제공", −23~23은 "UTC + 지역 오프셋 제공", 그 외 범위는 시간 기준 불명으로 해석한다(Table A.1).
- 두 offset 파라미터 모두 2004-10-15 기술 정오표에서 SAE와 조화되면서 정의가 바뀌었다(구판: 0 오프셋, 0~59 min / −24 h 오프셋).

### A.5~A.11 기계 속도·거리·방향·키 스위치

| 파라미터 | 길이 | 분해능 | 범위 | 타입 | SPN |
|---|---|---|---|---|---|
| Ground-based machine speed — A.5 | 2 bytes | 0,001 m/s/bit | 0~64,255 m/s | Measured | 1859 |
| Ground-based machine distance — A.6 | 4 bytes | 0,001 m/bit | 0~4 211 081,215 m | Measured | 1860 |
| Ground-based machine direction — A.7 | 2 bits | 00=Reverse, 01=Forward, 10=Error, 11=N/A | — | Measured | 1861 |
| Wheel-based machine speed — A.8 | 2 bytes | 0,001 m/s/bit | 0~64,255 m/s | Measured | 1862 |
| Wheel-based machine distance — A.9 | 4 bytes | 0,001 m/bit | 0~4 211 081,215 m | Measured | 1863 |
| Wheel-based machine direction — A.10 | 2 bits | A.7과 동일 코딩 | — | Measured | 1864 |
| Key switch state — A.11 | 2 bits | 00=Off, 01=not Off, 10=Error, 11=N/A | — | Measured | 1865 |

- ground-based는 레이더 등 대지 기준 센서 측정값, wheel-based는 바퀴/테일샤프트 회전수로 계산한 값이다. 슬립이 있으면 두 값이 달라지므로 작업기는 용도에 맞게 선택한다.
- 거리 파라미터는 최대값(4 211 081,215 m)을 넘으면 0으로 리셋 후 다시 누적한다.
- 방향 파라미터는 속도가 0이면 마지막 진행 방향을 유지해 보고한다. 방향은 차체(chassis) 기준이며, 운전석이 뒤로 돌아가도(reversed operator station) 바뀌지 않는다.
- Key switch state는 트랙터/파워 유닛의 키 스위치 상태다. 엔진 시동 중 발생하는 순간적 전원 차단 같은 것은 반영하지 않는다.

### A.12~A.14 전원 유지 파라미터

| 파라미터 | 길이 | 내용 | 타입 | SPN |
|---|---|---|---|---|
| Maximum time of tractor power — A.12 | 1 byte | 현재 부하 기준 남은 전원 공급 가능 시간. 1 min/bit, 0~250 min. 추정치일 수 있음 | Measured | 1866 |
| Maintain ECU power — A.13 | 2 bits | 01 = 앞으로 2 s 더 ECU_PWR 유지 요청, 00 = 더 이상 불필요 | Command | 1867 |
| Maintain actuator power — A.14 | 2 bits | 01 = 앞으로 2 s 더 PWR(액추에이터 전원) 유지 요청, 00 = 더 이상 불필요 | Command | 1868 |

키 오프 후에도 작업기 ECU가 셧다운 처리(설정 저장 등)를 끝낼 때까지 트랙터 ECU에 전원 유지를 요청하는 메커니즘이다. 2초 단위로 계속 갱신 요청하는 구조다.

### A.15~A.17 작업기 상태 파라미터

모두 2비트, Measured이며 코딩은 01=해당 상태 성립, 00=불성립, 10=Error, 11=N/A 규약을 따른다.

| 파라미터 | 의미 | SPN |
|---|---|---|
| Implement transport state — A.15 | 작업기를 운반(transport)해도 되는 상태인지 | 1869 |
| Implement park state — A.16 | 작업기를 트랙터/파워 유닛에서 분리해도 되는 상태인지 | 1870 |
| Implement ready-to-work state — A.17 | 작업기가 연결되어 필드 작업 준비가 되었는지 | 1871 |

### A.18 Navigation location parameters

항법 위치 파라미터는 자체 정의하지 않고 <strong>IEC 61162-3(NMEA 2000)</strong>의 것을 그대로 사용한다. 위치는 트랙터/작업기의 NRP(Navigation Reference Point) 기준으로 보고한다. NRP와 좌표계 정의는 ISO 11783-10에 있다. GNSS 수신기만 있으면 안테나 위치가 NRP일 수 있고, roll/pitch 보정이 되어 있으면 지면 투영점일 수도 있다.

### A.19 히치 파라미터

3점 히치(front/rear) 관련 파라미터군이다. 위치는 전체 스트로크의 백분율로 표현한다: 0 % = 최하단, 100 % = 최상단.

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Front hitch position — A.19.1 | 1 byte | 0,4 %/bit, 0~100 % | Measured | 1872 |
| Rear hitch position — A.19.2 | 1 byte | 0,4 %/bit, 0~100 % | Measured | 1873 |
| Front hitch position command — A.19.3 | 1 byte | 0,4 %/bit, 0~100 % | Command | 1874 |
| Rear hitch position command — A.19.4 | 1 byte | 0,4 %/bit, 0~100 % | Command | 1875 |
| Front hitch in-work indication — A.19.5 | 2 bits | 00=out-of-work, 01=in-work | Measured | 1876 |
| Rear hitch in-work indication — A.19.6 | 2 bits | 00=out-of-work, 01=in-work | Measured | 1877 |

in-work indication은 히치가 조정 가능한 전환 임계값(switching threshold) 아래(in-work)인지 위(out-of-work)인지를 나타낸다. 임계값 결정 방법은 표준화되어 있지 않고 제조사 재량이다.

#### A.19.7~A.19.10 견인력(draft) 파라미터

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Front draft — A.19.7 | 2 bytes | 10 N/bit, −320 000 N 오프셋, −320 000~322 550 N | Measured | 1878 |
| Rear draft — A.19.8 | 2 bytes | 동일 | Measured | 1879 |
| Front nominal lower link force — A.19.9 | 1 byte | 0,8 %/bit, −100 % 오프셋, −100~100 % | Measured | 1880 |
| Rear nominal lower link force — A.19.10 | 1 byte | 동일 | Measured | 1881 |

- draft는 작업기가 히치에 가하는 겉보기 수평력이다. 양수 = 트랙터 진행 방향과 반대로 작용하는 힘(즉 견인 저항).
- nominal lower link force는 로어 링크의 힘 센서에서 얻는 견인력 지표다. draft와 대략 선형 관계이며 히치 위치가 고정이면 비례한다고 볼 수 있다. draft control의 원시 데이터로 쓰인다.

#### A.19.11~A.19.12 Hitch position limit status

Front(SPN 5150)/Rear(SPN 5151) 히치의 <strong>지속형(persistent) 위치 명령</strong>에 대해 Tractor ECU가 현재 어떤 제한을 걸고 있는지 보고하는 3비트 measured 파라미터다.

| 값 | 의미 |
|---|---|
| 000 | Not limited |
| 001 | Operator limited/controlled — 요청 실행 불가 |
| 010 | Limited High — 더 낮은 명령값만 반영됨 |
| 011 | Limited Low — 더 높은 명령값만 반영됨 |
| 100~101 | Reserved |
| 110 | Non-recoverable fault |
| 111 | Not available (파라미터 미지원) |

- Limited High/Low는 일시적일 수 있다. 예: 큰 setpoint 변경이 램프 레이트로 제한되는 동안 이 비트를 세워 제어값 응답 지연에 의한 windup(및 오버슛)을 막는다.
- non-recoverable fault는 <strong>작업기 관점에서</strong> 회복 불가라는 뜻이다. 트랙터 안에서 운전자가 조치하면 해소되어 "Operator limited/controlled"로 바뀔 수 있다.

#### A.19.13~A.19.14 Hitch exit/reason code

Front(SPN 5816)/Rear(SPN 5819) 히치가 원격 명령을 받을 수 없는 이유, 또는 가장 최근에 원격 명령 수용을 중단한 이유를 나타내는 6비트 measured 파라미터다. 이 코드 체계는 이후 PTO·보조 밸브에도 거의 동일하게 반복된다.

| 값 | 의미 |
|---|---|
| 000000 | No reason / all clear |
| 000001 | 요구되는 운전자 존재/주의(presence/awareness) 수준 미검출 |
| 000010 | 작업기가 기능 제어를 해제(released)함 |
| 000011 | 운전자가 기능을 override |
| 000100 | 운전자 조작기가 유효 위치에 있지 않음 |
| 000101 | Remote command timeout |
| 000110 | Remote command 범위 초과/무효 |
| 000111 | 기능 미교정(not calibrated) |
| 001000 | Operator control fault |
| 001001 | Function fault |
| 010100 | 유압유 부족(hydraulic oil level too low) |
| 010101 | Hitch locked out |
| 110001~111101 | Manufacturer specific |
| 111110 | Error |
| 111111 | Not available (파라미터 미지원) |
| 나머지 | Reserved |

### A.20 PTO 파라미터

PTO(power take-off) 관련 파라미터는 front/rear 대칭으로 정의된다.

#### 속도 파라미터 (A.20.1~A.20.6)

모두 2 bytes, 0,125 (1/min)/bit, 0~8 031,875 1/min 범위로 동일하다.

| 파라미터 | 타입 | SPN(front/rear) |
|---|---|---|
| PTO output shaft speed — A.20.1/A.20.2 | Measured | 1882 / 1883 |
| PTO output shaft speed set point (현재 설정값 보고) — A.20.3/A.20.4 | Measured | 1884 / 1885 |
| PTO output shaft speed set point — Command — A.20.5/A.20.6 | Command | 1886 / 1887 |

:::info 기존 트랙터의 PTO 속도 유효성
체결 클러치 앞단에서 PTO 속도를 측정하는 기존 트랙터에서는 PTO가 체결(engaged)된 동안에만 속도가 유효하고, 해제 시에는 not available이 된다.
:::

#### 상태·모드 파라미터 (A.20.7~A.20.18)

모두 2비트이며, measured는 00=해제/540 모드, 01=체결/1 000 모드, 10=Error, 11=N/A, command는 00/01=기능 명령, 10=Reserved, 11=Don't care 규약이다.

| 파라미터 | 의미 | 타입 | SPN(front/rear) |
|---|---|---|---|
| PTO engagement — A.20.7/A.20.8 | PTO 체결/해제 상태 | Measured | 1888 / 2408 |
| PTO mode — A.20.9/A.20.10 | 00=540 r/min 모드, 01=1 000 r/min 모드 | Measured | 1889 / 1890 |
| PTO economy mode — A.20.11/A.20.12 | 이코노미 모드 체결 여부 | Measured | 1891 / 1892 |
| PTO engagement — Command — A.20.13/A.20.14 | 체결/해제 명령 | Command | 1893 / 1894 |
| PTO mode — Command — A.20.15/A.20.16 | 540/1 000 모드 선택 명령 | Command | 1895 / 1896 |
| PTO economy mode — Command — A.20.17/A.20.18 | 이코노미 모드 체결/해제 명령 | Command | 1897 / 1898 |

economy mode는 더 낮은 엔진 회전수에서 540 또는 1 000 r/min PTO 속도를 내는 모드다.

#### 요청 상태·제한 상태·이유 코드 (A.20.19~A.20.28)

트랙터 ECU가 작업기의 PTO 요청 처리 결과를 피드백하는 파라미터군이다. 히치와 같은 패턴이 반복된다.

<strong>Request status</strong> (2비트, Measured) — 일시적(transient/one-shot) 요청에 대한 상태:

| 파라미터 | SPN |
|---|---|
| Front PTO engagement request status — A.20.19 | 5152 |
| Front PTO mode request status — A.20.20 | 5153 |
| Front PTO economy mode request status — A.20.21 | 5154 |
| Rear PTO engagement request status — A.20.23 | 5156 |
| Rear PTO mode request status — A.20.24 | 5157 |
| Rear PTO economy mode request status — A.20.25 | 5158 |

공통 코딩: 00 = 외부 요청 수락(운전자 개입 없음), 01 = Control override(운전자/트랙터 시스템 override로 최근 외부 요청 무시됨), 10 = Error, 11 = Not available.

<strong>Shaft speed limit status</strong> (3비트, Measured) — 지속형 속도 명령에 대한 제한 상태. 코딩은 hitch position limit status(A.19.11)와 동일: Front — A.20.22 (SPN 5155), Rear — A.20.26 (SPN 5159).

<strong>Exit/reason code</strong> (6비트, Measured) — PTO가 원격 명령을 받지 못하는 이유. 코딩은 hitch exit/reason code와 거의 동일하되 010100이 "Invalid PTO gear"인 점만 다르다: Front — A.20.27 (SPN 5817), Rear — A.20.28 (SPN 5820).

### A.21 보조 밸브(auxiliary valve) 파라미터

#### A.21.1 밸브 번호 규약

- 보조 유압 밸브는 0번부터 시작해 장치의 최대 밸브 수까지 순차 번호를 붙인다.
- 트랙터의 보조 밸브에는 이 번호에 대응하는 라벨을 물리적으로 표기해야 한다. 브로드캐스트되는 밸브 번호는 작업기/장비가 실제 연결된 밸브의 라벨 번호와 일치해야 한다.
- 밸브 번호는 밸브의 위치나 장착 방식과 무관하다.
- "power beyond" 기술을 쓰는 시스템에서는 <strong>0번 밸브가 power beyond 제어 밸브</strong>를 가리킨다.

#### A.21.2~A.21.14 밸브 0번 파라미터 (이후 밸브 1~15에 동일 패턴 반복)

Annex A는 밸브 0번에 대해 아래 파라미터 세트를 정의하고, 이후 절에서 나머지 밸브에 같은 정의를 반복한다.

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN(밸브 0) |
|---|---|---|---|---|
| Extend port measured flow — A.21.2 | 1 byte | 1 %/bit, −125 % 오프셋, −125~125 % | Measured | 1899 |
| Retract port measured flow — A.21.3 | 1 byte | 동일 | Measured | 1900 |
| Extend port estimated flow — A.21.4 | 1 byte | 동일 | Estimated | 1901 |
| Retract port estimated flow — A.21.5 | 1 byte | 동일 | Estimated | 1902 |
| Valve state — A.21.6 | 4 bits | 아래 코딩 | Measured | 1903 |
| Extend port pressure — A.21.7 | 2 bytes | 5 kPa/bit, 0~321 275 kPa | Measured | 1904 |
| Retract port pressure — A.21.8 | 2 bytes | 동일 | Measured | 1905 |
| Return port pressure — A.21.9 | 1 byte | 16 kPa/bit, 0~4 000 kPa | Measured | 1906 |
| Port flow — Command — A.21.10 | 1 byte | 0,4 %/bit, 0~100 % | Command | 1907 |
| Valve state — Command — A.21.11 | 4 bits | 아래 코딩 | Command | 1908 |
| Fail safe mode — Command — A.21.12 | 2 bits | 00=Block, 01=Float | Command | 1909 |
| Fail safe mode — A.21.13 | 2 bits | 00=Block, 01=Float | Measured | 1910 |
| Measured flow limit status — A.21.14 | 3 bits | limit status 공통 코딩 | Measured | — |

flow 값의 의미: 0 % = 흐름 없음, 100 % = 최대 흐름, −100 % = 이 포트를 통해 트랙터로 되돌아오는 최대 흐름. estimated flow는 밸브 명령 위치에서 추정한 값이므로 <strong>피드백 제어에 쓸 때 주의</strong>가 필요하다(실측 아님).

<strong>Valve state 코딩</strong> (measured / command):

| 값 | Measured (A.21.6) | Command (A.21.11) |
|---|---|---|
| 0000 | Blocked | Block |
| 0001 | Extend | Extend |
| 0010 | Retract | Retract |
| 0011 | Floating | Float |
| 0100~1101(cmd는 ~1110) | Reserved | Reserved |
| 1110 | Error indication | — |
| 1111 | Not available | Don't care |

상태 의미: Blocked = 밸브 닫힘, 유량 없음(압력은 걸려 있을 수 있음). Floating = 제어 유량 없이 밸브 포트가 탱크에 직결되어 액추에이터가 미는 대로 유체가 드나드는 상태. Extend = extend 포트에서 유량 제어, 유체는 retract 포트로 복귀. Retract = 그 반대. float가 켜지면 작업기가 구동하는 대로 트랙터와 유체가 오갈 수 있다.

#### A.21.14~A.21.16 밸브 0 상태 보고 파라미터

- Measured flow limit status — A.21.14 (SPN 5160), Estimated flow limit status — A.21.15 (SPN 5161): 지속형 flow 명령에 대한 제한 상태. 3비트, 코딩은 limit status 공통(000=Not limited ~ 111=N/A).
- Exit/reason code — A.21.16 (SPN 5800): 6비트. 히치의 exit/reason code와 동일 체계이되 010101이 "Valve locked out"이다.

#### A.21.17~A.21.32 밸브 1~15

이 파트는 <strong>밸브 0번과 15번의 파라미터만 명시</strong>하고, 밸브 1~14는 데이터 구조·정의가 동일하며 밸브 번호와 SPN만 다르다고 규정한다(A.21.17). 밸브 15의 파라미터(A.21.18~A.21.32)는 밸브 0과 완전히 같은 세트다: measured/estimated flow(SPN 2335~2338), valve state(2339), extend/retract/return port pressure(2340~2342), port flow command(2343), state command(2344), fail safe mode command/measured(2345/2346), measured/estimated flow limit status(5190/5191), exit/reason code(5815).

#### A.21.33~A.21.50 General-purpose valve 파라미터

특정 번호에 묶이지 않은 범용(general-purpose) 밸브에 대해 같은 패턴의 파라미터를 별도 SPN으로 정의한다. 밸브 0/15와 다른 점은 assembly 관련 파라미터가 추가된다는 것이다.

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Extend/Retract port measured flow — A.21.33/34 | 1 byte | 1 %/bit, −125 % 오프셋 | Measured | 2937/2938 |
| Extend/Retract port estimated flow — A.21.35/36 | 1 byte | 동일 | Measured(추정값) | 2939/2940 |
| Valve state — A.21.37 | 4 bits | 밸브 상태 공통 코딩 | Measured | 2932 |
| Extend/Retract port pressure — A.21.38/39 | 2 bytes | 5 kPa/bit, 0~321 275 kPa | Measured | 2941/2942 |
| Return port pressure — A.21.40 | 1 byte | 16 kPa/bit, 0~4 000 kPa | Measured | 2943 |
| Port flow — Command — A.21.41 | 1 byte | 0,4 %/bit, 0~100 % | Command | 2944 |
| Valve state — Command — A.21.42 | 4 bits | 공통 코딩 | Command | 2933 |
| Fail safe mode — Command / Measured — A.21.43/44 | 2 bits | 00=Block, 01=Float | Command/Measured | 2935/2934 |
| Load sense pressure — A.21.45 | 2 bytes | 5 kPa/bit | Measured | 4086 |
| Pilot pressure — A.21.46 | 1 byte | 16 kPa/bit, 0~4 000 kPa | Measured | 4087 |
| Valve assembly load sense pressure — A.21.47 | 2 bytes | 5 kPa/bit | Measured | 4088 |
| Valve assembly supply pressure — A.21.48 | 2 bytes | 5 kPa/bit | Measured | 4089 |
| Measured / Estimated limit status — A.21.49/50 | 3 bits | limit status 공통 코딩 | Measured | 5192/5193 |

- load sense pressure는 해당 밸브의 work port A/B 중 현재 측정 압력의 최대값이다.
- valve assembly load sense pressure는 2개 이상 밸브로 구성될 수 있는 밸브 어셈블리의 집합 load sense 압력 중 최대값이고, assembly supply pressure는 어셈블리로 들어오는 유압 공급 포트 압력이다.

### A.22 조명(lighting) 파라미터

조명 파라미터는 조명 종류별로 <strong>Command / Measured 쌍</strong>으로 정의되는 2비트 파라미터의 나열이다. 코딩은 전부 동일하다.

| 값 | Command | Measured |
|---|---|---|
| 00 | Deactivate | Deactivated |
| 01 | Activate | Activated |
| 10 | Reserved | Fault detected |
| 11 | Don't care | Not available |

조명 종류별 SPN(A.22.1~A.22.19, 계속됨):

| 조명 | Command SPN | Measured SPN |
|---|---|---|
| High-beam headlights | 2347 | 2348 |
| Low-beam headlights | 2349 | 2350 |
| Alternate headlights | 2351 | 2352 |
| Tractor front low-mounted work lights | 2353 | 2354 |
| Tractor front high-mounted work lights | 2355 | 2356 |
| Tractor underside-mounted work lights | 2357 | 2358 |
| Tractor rear low-mounted work lights | 2359 | 2360 |
| Tractor rear high-mounted work lights | 2361 | 2362 |
| Tractor side low-mounted work lights | 2363 | 2364 |

alternate headlights는 low-beam만 있는 대체 위치 램프로, 로더나 제설기 장착 시 주 전조등이 가려지는 경우를 위한 것이다.

나머지 조명(A.22.20~A.22.62)도 같은 Command/Measured 쌍 구조다.

| 조명 | Command SPN | Measured SPN | 비고 |
|---|---|---|---|
| Tractor side high-mounted work lights | 2365 | 2366 | |
| Left-turn signal lights | 2367 | 2368 | 트랙터 + 연결된 모든 작업기의 좌측 방향지시등 |
| Right-turn signal lights | 2369 | 2370 | 우측 방향지시등 |
| Left stop lights | 2371 | 2372 | 트랙터·작업기의 좌측 제동등 |
| Right stop lights | 2373 | 2374 | 우측 제동등 |
| Centre stop lights | 2375 | 2376 | 중앙 제동등 |
| Tractor marker (position) lights | 2377 | 2378 | 전방 포지션등, 후방 적색 테일등, 측면 황색 러닝등, 번호판등, 계기·스위치 백라이트 포함 |
| Implement marker (position) lights | 2379 | 2380 | 작업기 쪽 동일 구성 |
| Tractor clearance lights | 2381 | 2382 | 상부 장착 clearance·centre ID 램프 |
| Implement clearance lights | 2383 | 2384 | |
| Rotating beacon light | 2385 | 2386 | slow-moving vehicle 표시등. activate 시 컨트롤러가 저속 차량 표시 기능에 맞게 조명을 조작해야 함 |
| Tractor front fog lights | 2387 | 2388 | |
| Rear fog lights | 2389 | 2390 | 트랙터/작업기 후방 안개등 |
| Back-up lights and alarm horn | 2391 | 2392 | 후진등 및 후진 경보 |
| Implement OEM option 1 light | 2395 | 2396 | 탱크 점검등·주입등 등 OEM 특수 목적 조명 |
| Implement OEM option 2 light | 2397 | 2398 | |
| Implement left forward work lights | 2597 | 2598 | 작업기 좌측단의 전방향 작업등 |
| Implement right forward work lights | 2406 | 2407 | |
| Implement left-facing work lights | 2399 | 2400 | 작업기 좌측단 바깥을 비추는 작업등 |
| Implement right-facing work lights | 2401 | 2402 | |
| Implement rear work lights | 2405 | 2394 | 트럭의 후진등에 해당 |
| Daytime running lights | 2403 | 2404 | 주간주행등. 주로 도로 주행용 |

조명 관련 나머지 파라미터:

- <strong>Lighting data message request — Command</strong> — A.22.63 (SPN 2393, 2 bits): 모든 조명 컨트롤러에 전체 조명 상태를 담은 lighting data 메시지 송신을 요청. 01 = data requested.
- <strong>Background illumination level — Command</strong> — A.22.64 (SPN 1487, 1 byte, 0,4 %/bit, 0~100 %): 계기·조작부 백라이트 밝기 설정.

### A.23 언어·단위 파라미터 (language command)

운전자가 원하는 언어·표시 형식·단위계를 네트워크의 모든 CF에 전파하는 command 파라미터군이다. VT 등 표시 장치가 이를 따라 표시를 통일한다.

| 파라미터 | 길이 | 값 | SPN |
|---|---|---|---|
| Language code — A.23.1 | 2 bytes | ISO 639 2문자 코드(7-bit ISO Latin 1). 예: en, de, fr, nl | 2410 |
| Decimal symbol — A.23.2 | 2 bits | 00=콤마, 01=포인트, 11=No action | 2411 |
| Date format — A.23.3 | 1 byte | 0=ddmmyyyy, 1=ddyyyymm, 2=mmyyyydd, 3=mmddyyyy, 4=yyyymmdd, 5=yyyyddmm, 6~250=Reserved | 2412 |
| Time format — A.23.4 | 2 bits | 00=24 h, 01=12 h(am/pm), 11=No action | 2413 |

<strong>단위계 파라미터</strong> (A.23.5, 모두 2 bits, Command). 공통적으로 00=Metric, 01=Imperial, 11=No action이고, volume/mass만 Imperial(01)과 US(10)를 구분한다.

| 단위 | 값 구성 | SPN |
|---|---|---|
| Distance units — A.23.5.2 | Metric(km, m) / Imperial·US(mile, ft) | 2414 |
| Area units — A.23.5.3 | Metric(ha, m²) / Imperial·US(acre, ft²) | 2415 |
| Volume units — A.23.5.4 | Metric(L) / Imperial(gallon) / US(gallon) | 2416 |
| Mass units — A.23.5.5 | Metric(t, kg) / Imperial(long ton, lb) / US(short ton, lb) | 2417 |
| Temperature units — A.23.5.6 | Metric(°C, K) / Imperial·US(°F) | 5194 |
| Pressure units — A.23.5.7 | Metric(kPa, Pa) / Imperial·US(psi) | 5195 |
| Force units — A.23.5.8 | Metric(N) / Imperial·US(lbf) | 5196 |
| Units system — A.23.5.9 | 위에 명시되지 않은 그 외 단위의 표시 체계: Metric/Imperial/US | 5197 |

### A.23.6~A.23.7 Repetition rate

특정 PGN 메시지의 송신 주기를 제어·보고하는 파라미터다.

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Repetition rate — Command — A.23.6 | 2 bytes | 1 ms/bit, 0~64 255 | Command | 2418 |
| Repetition rate — A.23.7 | 2 bytes | 1 ms/bit, 0~64 255 | Measured | 5198 |

command 값 0은 "기본 주기 사용", 65 535는 "변경 요청 없음"을 뜻한다.

### A.24 Working set 파라미터

| 파라미터 | 길이 | 내용 | 타입 | SPN |
|---|---|---|---|---|
| Number of members in working set — A.24.1 | 8 bits | working set의 멤버 수. 1~250 | — | 2409 |
| NAME of working set member — A.24.2 | 8 bytes | ISO 11783-5 형식의 NAME. 0~2^64−1 | Measured | 2845 |

- working set은 <strong>working set master의 NAME</strong>으로 식별되며, 이 NAME은 이 파라미터를 담은 메시지의 source address(SA)와 연결된다.
- 한 멤버(특정 NAME으로 식별, CF가 아님)는 동시에 하나의 working set에만 속할 수 있다.
- 멤버의 NAME은 그 멤버가 source address를 claim할 때 사용한 NAME과 동일해야 한다. 상세는 ISO 11783-1과 -6을 따른다.

### A.25 Implement operating state 파라미터

| 파라미터 | 길이 | 타입 | SPN |
|---|---|---|---|
| Implement operating state — Command — A.25.1 | 2 bits | Command | 5139 |
| Implement Start/Stop operations — A.25.2 | 2 bits | Measured | 5203 |
| Stop all implement operations — A.25.3 | 2 bits | Measured | 5140 |
| Stop all implement operations transition number — A.25.4 | 1 byte | Measured | 7443 |

- <strong>Implement operating state — Command</strong>: 연결된 작업기 시스템의 운용 상태를 설정한다. 00 = field working state, 01 = transport state, 10 = park state, 11 = take no action. (A.15~A.17의 measured 상태와 대응하는 command다.)
- <strong>Implement Start/Stop operations</strong>: 작업기 동작을 시작/허용하는 스위치·운전자 입력의 상태. 작업기가 작업 위치에 놓였거나 운전자가 스위치를 ON에 둔 결과일 수 있다. "Master ON/OFF" 스위치라고도 부른다. 00 = stop/disable, 01 = start/enable.
- <strong>Stop all implement operations</strong>: VT, auxiliary control input, TECU, task controller, sequence control master의 조작·메시지 명령으로 활성화된 <strong>모든 기능을 즉시 정지</strong>시키는 운전자 입력 상태. 00 = stop, 01 = permit all implements to operation ON.

:::warning Stop all implement operations의 안전 요건
- 이 스위치는 운전자가 <strong>언제나</strong> 접근 가능해야 하며, 작업기 운용 중 사용 가능한 모든 운전자 위치에 각각 존재해야 한다. 배치·조작은 ISO 15077 요구사항을 따라야 한다.
- 이 스위치로 전체 정지가 발생한 뒤 "permit" 상태가 되어도 작업기가 <strong>바로 재시작되지 않는다.</strong> 재시작은 start/stop("Master ON/OFF") 스위치 등 별도 수단으로만 해야 한다.
- 작업기는 정지 수단을 이 입력에만 의존해서는 안 되고, 전용 start/stop 스위치·VT 소프트키·정지 기능에 할당된 auxiliary input 등 <strong>정상 정지 수단을 별도로 제공</strong>해야 한다.
:::

- <strong>Transition number</strong>: 전원 인가 후 Stop all implement operations 파라미터가 Permit(01)→Stop(00)으로 전이한 횟수. 0~255, 최대값 보고 후 다음 전이에서 0으로 리셋. 수신 측이 정지 이벤트 누락을 감지할 수 있게 한다.

### A.26 트랙터 제어(tractor control) 파라미터

연결된 작업기나 task controller가 견인 트랙터의 동작을 제어하고 시스템 전체 성능을 최적화하는 데 쓰는 파라미터군이다. <strong>트랙터는 각 제어 모드의 제약을 스스로 판단해 적절한 경우에만 명령을 승인(acknowledge)해야 한다.</strong>

#### A.26.2 Tractor control mode commands (구판 방식 — deprecated)

:::warning 3판에서 deprecated
A.26.2의 트랙터 제어 모드 명령은 3판(2015)부터 <strong>deprecated이며 신규 설계에 사용해서는 안 된다.</strong> 아래 내용은 기존 시스템 이해를 위한 것이다.
:::

작업기·task controller·운전자(VT의 Tractor ECU 인터페이스)가 Tractor ECU의 선택적 기능 제어 모드를 설정하는 5비트 command(SPN 5204)다. 동력·속도·슬립 최적화와 진행 방향 제어의 조합을 달성한다.

| 값 | 모드 |
|---|---|
| 00000 | Disable remote control |
| 00001 | Enable cruise control |
| 00010 / 00011 | Enable front / rear hitch slip control |
| 00100 / 00101 | Enable front / rear PTO slip control |
| 00110 | Enable reduce speed slip control |
| 00111 | Enable auxiliary valve slip control |
| 01000 | Enable maximum draft power control |
| 01001 / 01010 | Enable constant PTO speed control / + cruise control 조합 |
| 01011 | Enable minimum engine speed control |
| 01100 | Enable combined engine economy, cruise control |
| 01101 / 01110 | Enable front / rear PTO torque control |
| 01111 / 10000 | Enable front / rear draft force control |
| 10001~11110 | Reserved |
| 11111 | Don't care |

주요 모드 해설:

- <strong>Cruise control</strong>: 트랙터가 고정 대지 속도를 유지한다. 속도원(wheel/ground/navigation)은 현재 운용 조건에서 가장 정확한 측정을 트랙터가 스스로 선택한다(ISO 11783-9 참조).
- <strong>Slip control</strong>: 트랙터-토양 접촉면 동력 손실을 줄이기 위해 구동륜 슬립을 제한하는 명령들. 전략별 장단점이 있다.
  - Rear hitch slip control — 히치 장착 작업기의 작업 깊이를 조정해 견인력을 줄이고 하중을 트랙터 후방으로 이전한다. 2WD·MFWD에서는 후륜 하중 증가로 견인력이 개선되지만 4WD·트랙형에서는 효과가 거의 없다. 깊이 조정 때문에 작업 깊이가 일정하지 않게 된다.
  - Front hitch slip control / Auxiliary valve slip control — 전방 장착/견인식 작업기의 깊이를 조정해 견인력을 줄이지만 유효한 하중 이전은 없다. 역시 깊이가 불규칙해진다.
  - Front/rear PTO slip control — PTO 속도를 조정해 견인 저항을 줄인다(파워 해로처럼 PTO 속도에 따라 견인 저항이 줄어드는 작업기용). 일정한 작업 깊이와 총 출력(PTO+드로바) 극대화가 가능하지만, 엔진 속도와 독립적으로 PTO 속도를 조정할 수 있어야 한다.
  - Reduce speed slip control — 차량의 대지 속도를 낮춰 견인 요구를 줄인다. 깊이는 일정하지만 최대 출력보다 낮게 운용된다.
- <strong>Maximum draft power mode</strong>: 변속비를 교대로 바꿔(엔진 rpm이 일정 수준 떨어지면 감속, 회복·초과하면 증속) 견인 동력을 최대화하는 파워트레인 전략.
- <strong>Constant PTO speed mode</strong>: 일정 PTO 속도 제어. cruise control과의 조합 모드도 있다.
- <strong>Minimum engine speed mode</strong>: 소음·연료 소비를 줄이도록 엔진 속도·스로틀·기어비를 조정.
- <strong>Economy engine control mode</strong>: 최소 연료 소비를 목표로 엔진 속도·스로틀·기어비 조정(cruise와 조합).
- <strong>PTO torque control mode</strong>: PTO 구동 작업기를 과부하로부터 보호.
- <strong>Draft force control</strong>: 히치 장착 작업기의 작업 깊이를 조정해 견인력을 낮추고 하중을 후방 이전(rear) / 하중 이전 없이 견인력만 감소(front).

#### A.26.3 Tractor control command value parameters

제어 모드 명령과 함께 작업기가 Tractor ECU에 보내는 목표값(set point) 파라미터다.

| 파라미터 | 길이 | 분해능·범위 | 기본값 | SPN |
|---|---|---|---|---|
| Commanded vehicle speed — A.26.3.2 | 2 bytes | 0,001 m/s/bit, 0~64,255 m/s | 0 | 5205 |
| Commanded PTO speed — A.26.3.3 | 2 bytes | 0,125 1/min/bit, 0~8 031,875 1/min | 850 | 5206 |
| Commanded hitch position — A.26.3.4 | 1 byte | 0,4 %/bit, 0~100 % | 0 | 5207 |
| Commanded PTO torque — A.26.3.5 | 1 byte | 0,4 %/bit, 0~100 % | 0 | 5208 |
| Commanded auxiliary valve slip control — A.26.3.6 | 2 bytes | 아래 구조 | — | — |
| Commanded draft force — A.26.3.7 | 1 byte | 1 000 N/bit, −100 000 N 오프셋, −100 000~150 000 N | 0 | 5212 |

Commanded auxiliary valve slip control(2 bytes)의 구조:

| 필드 | 위치 | 내용 | SPN |
|---|---|---|---|
| Auxiliary valve flow | Byte 1 | slip control 기능 내 flow 목표값. 0,4 %/bit, 0~100 % | 5209 |
| Auxiliary valve state | Byte 2, bits 8~5 | 0000=Block, 0001=Extend, 0010=Retract, 0011=Float, 1111=Don't care | 5210 |
| Auxiliary valve number | Byte 2, bits 4~1 | 대상 밸브 번호 0~15 (limit 값에도 동일 번호 사용) | 5211 |

#### A.26.4 Tractor control mode command response parameters

Tractor ECU가 현재 설정된 선택 기능 제어 모드를 <strong>보고</strong>하는 5비트 measured 파라미터(SPN 5213)다. command(A.26.2)와 달리 cruise control이 속도원별로 세분되어 있어 코드 표가 다르다.

| 값 | 모드 |
|---|---|
| 00000 | Disable remote control |
| 00001 / 00010 / 00011 | Ground / Wheel / Navigation speed cruise control |
| 00100 / 00101 | Front / Rear hitch slip control |
| 00110 / 00111 | Front / Rear PTO slip control |
| 01000 | Reduce speed slip control |
| 01001 | Auxiliary valve slip control |
| 01010 | Maximum draft power control |
| 01011 | Constant PTO speed control |
| 01100 / 01101 / 01110 | Constant PTO speed + ground/wheel/navigation speed cruise |
| 01111 | Minimum engine speed control |
| 10000 / 10001 / 10010 | Engine economy + ground/wheel/navigation speed cruise |
| 10011 / 10100 | Front / Rear PTO torque control |
| 10101 / 10110 | Front / Rear draft force control |
| 10111~11110 | Reserved |
| 11111 | Not available |

A.26.4.2~A.26.4.10은 이 표의 부분집합을 모드 계열별(cruise, slip, max draft power, constant PTO speed, min engine speed, economy, PTO torque, draft control)로 나눠 다시 기술한 것이다.

#### A.26.5 Tractor control value response parameters

트랙터가 수락해 적용 중인 목표값을 보고하는 measured 파라미터군이다. command 값 파라미터(A.26.3)와 1:1 대응한다.

| 파라미터 | 길이 | 분해능·범위 | 타입 | SPN |
|---|---|---|---|---|
| Vehicle speed set point — A.26.5.2 | 2 bytes | 0,001 m/s/bit, 0~64,255 m/s | Measured | 5214 |
| PTO speed set point — A.26.5.3 | 2 bytes | 0,125 1/min/bit, 0~8 031,875 1/min | Measured | 5215 |
| Hitch position set point — A.26.5.4 | 1 byte | 0,4 %/bit, 0~100 % | Measured | 5216 |
| PTO torque set point — A.26.5.5 | 1 byte | 0,4 %/bit, 0~100 % | Measured | 5217 |
| Maximum slip set point — A.26.5.6 | 1 byte | 0,4 %/bit, 0~100 % | Measured/Estimated | 5218 |
| Auxiliary valve slip control — A.26.5.7 | 2 bytes | 아래 구조 | Measured | — |

- Maximum slip set point는 slip control 기능 내에서 확정된(settled) 보조 밸브의 최대 flow를 보고한다. 대상 밸브는 valve number로, 포트 선택은 auxiliary valve slip control mode command 안에서 지정된다.
- Auxiliary valve slip control(response)의 구조는 command(A.26.3.6)와 동일: Byte 1 = valve flow(SPN 5219, 0,4 %/bit, Measured/Estimated), Byte 2 bits 8~5 = valve state(SPN 5220), bits 4~1 = valve number(SPN 5221, 0~15).


## A.26.5.8~A.26.8 Tractor 제어 세트포인트·리밋 파라미터 (계속)

### A.26.5.8 Draft force set point

전방 또는 후방 lower link의 견인력(draft force) 명령 세트포인트 값을 보고하는 파라미터다.

| 항목 | 값 |
|---|---|
| Data length | 2 bytes |
| Resolution | 10 N/bit |
| Offset | −320 000 N |
| Data range | −320 000 N ~ 322 550 N |
| Unit | Newton |
| Type | Measured |
| SPN | 5222 |

### A.26.6 Tractor control limit parameters

임플리먼트가 Tractor ECU에 명령한 세트포인트에 대해, 트랙터 컨트롤러가 적용 중인 리밋 값 설정을 보고하는 파라미터 그룹이다.

| 절 | 파라미터 | 길이 | Resolution | Offset | Range | Type | SPN |
|---|---|---|---|---|---|---|---|
| A.26.6.2 | Draft force limit set point | 1 byte | 1 kN/bit | −100 kN | −100~150 kN | Measured | 5223 |
| A.26.6.3 | PTO torque limit set point | 1 byte | 0,4 %/bit | 0 % | 0~100 % | Measured | 5224 |
| A.26.6.4 | Absolute maximum PTO torque limit set point 540 rpm | 1 byte | 30 N·m/bit | 0 | 0~7 500 N·m | Measured | 5225 |
| A.26.6.5 | Auxiliary valve flow limit set point | 1 byte | 0,4 %/bit | 0 % | 0~100 % | Measured/Estimated | 5226 |

- A.26.6.5의 auxiliary valve 번호는 auxiliary valve flow command로 지정된다. slip control 기능 내에서 확정된 유량 리밋을 뜻한다.

### A.26.7 Tractor control limit status

지속형(persistent) 명령 파라미터에 대해 Tractor ECU의 현재 리밋 상태를 보고한다. 3 bits, Type: Measured, SPN 5227.

| 값 | 의미 |
|---|---|
| 000 | Not limited |
| 001 | Operator limited/controlled (요청을 수행할 수 없음) |
| 010 | Limited high (더 낮은 명령 값만 변화를 만든다) |
| 011 | Limited low (더 높은 명령 값만 변화를 만든다) |
| 100~101 | Reserved |
| 110 | Non-recoverable fault |
| 111 | Not available (파라미터 미지원) |

:::info 해석 포인트
Limited high/low 상태는 일시적일 수 있다. 예를 들어 큰 세트포인트 변경이 ramp rate로 제한되는 동안 이 상태를 유지해, 제어량 응답 지연으로 인한 windup(및 후속 overshoot)을 막는 용도로 쓴다. Non-recoverable fault는 <strong>임플리먼트 관점</strong>에서 복구 불가라는 뜻이다. 트랙터 쪽에서 운전자가 조치하면 "Operator limited/controlled" 상태로 바뀔 수 있다.
:::

### A.26.8 Tractor control limit command parameters

임플리먼트가 트랙터 컨트롤러에 명령하는 리밋 값(command) 파라미터 그룹이다. A.26.6과 같은 물리량이지만 Type이 Command다.

| 절 | 파라미터 | 길이 | Resolution | Offset | Range | SPN |
|---|---|---|---|---|---|---|
| A.26.8.2 | Draft force limit set point command | 1 byte | 1 kN/bit | −100 kN | −100~150 kN | 5228 |
| A.26.8.3 | PTO torque limit set point command | 1 byte | 0,4 %/bit | 0 % | 0~100 % | 5229 |
| A.26.8.4 | Absolute maximum PTO torque limit set point 540 r/min command | 1 byte | 30 N·m/bit | 0 | 0~7 500 N·m | 5230 |
| A.26.8.5 | Auxiliary valve flow limit set point command | 1 byte | 0,4 %/bit | 0 % | 0~100 % | 5231 |

## A.27 Tractor facility parameters

Tractor ECU의 기능(facility)을 요청하고 보고하는 데 쓰는 파라미터들이다.

| 절 | 파라미터 | 길이 | Type | SPN | 값 정의 |
|---|---|---|---|---|---|
| A.27.2 | Tractor ECU class request | 2 bits | Command | 5232 | 00=TECU class 1, 01=class 2, 10=class 3, 11=Not requested |
| A.27.3 | Tractor facility request | 1 bit | Command | 5233 | 0=Facility not required, 1=Facility required |
| A.27.4 | Tractor ECU class response | 2 bits | Measured | 5234 | 00=class 1, 01=class 2, 10=class 3, 11=Not available |
| A.27.5 | Tractor facility response | 1 bit | Measured | 5235 | 0=Facility not available, 1=Facility available |
| A.27.6 | Tractor facility reserved bit indicator | 2 bits | Measured | 5236 | 0=Reserved bits are 0, 1=Reserved bits are 1 |
| A.27.7 | Tractor facility request – Limit/request status reporting | 1 bit | Measured | 7445 | 0=보고 불요, 1=보고 요구 |
| A.27.8 | Tractor facility response – Limit/request status reporting | 1 bit | Measured | 7444 | 0=보고 불가, 1=보고 가능 |

:::tip A.27.6 reserved bit indicator가 존재하는 이유
표준 준수 규칙상 reserved bit는 1로 채워야 하는데, 과거 판에서는 tractor facility bit에 대한 예외를 명시하지 않았다. 구버전 장비와의 하위 호환을 판별하기 위해 "이 메시지의 reserved bit가 0인지 1인지"를 알려주는 파라미터가 별도로 필요했다.
:::

A.27.7/A.27.8은 트랙터의 상태 메시지에 포함되는 limit status·request status 파라미터(A.19.11, A.20.19 등)의 보고를 요구/지원하는지 나타낸다.

## A.28 Guidance commands

자동 조향(guidance) 관련 파라미터 그룹이다. Guidance 시스템(경로 계산 주체)과 machine steering system(조향 실행 주체) 간의 명령·상태 교환에 쓴다.

### A.28.1 Curvature command / A.28.2 Estimated curvature

- <strong>Curvature command</strong> (SPN 5237, Command): guidance 시스템이 조향 시스템에 요구하는 지면 기준 목표 경로 곡률. 순간 선회 반경의 역수로 표현하며, 전진 중 운전자 기준 오른쪽 선회가 양수다.
- <strong>Estimated curvature</strong> (SPN 5238, Measured): 조향 시스템이 추정한 현재 선회 곡률. 부호 규약은 동일하다.

| 항목 | 값 (두 파라미터 공통) |
|---|---|
| Data length | 2 bytes |
| Resolution | 0,25 km⁻¹/bit, offset −8 032 km⁻¹ |
| Data range | −8 032 ~ 8 031,75 km⁻¹ |

### A.28.3 Curvature command status

guidance 시스템이 이 명령으로 조향을 제어하려는 의도가 있는지 나타낸다. 2 bits, Type: Command, SPN 5239.

| 값 | 의미 |
|---|---|
| 00 | Not intended to steer |
| 01 | Intended to steer |
| 10 | Reserved |
| 11 | Not available |

### A.28.4 Request reset command status

조향 시스템이 guidance 시스템에게 Curvature command status를 "Intended to steer"에서 "Not intended to steer"로 되돌리라고 요청하는 파라미터다. 2 bits, Measured, SPN 5240. 00=Reset not required, 01=Reset required, 10=Error indication, 11=Not available.

### A.28.5 Steering input position status

수동 조향(스티어링 휠)이 guidance 동작에 적합한 위치(예: 중립)에 있는지를 조향 시스템이 알린다. 2 bits, Measured, SPN 5241. 00=Not the correct position, 01=Correct position, 10=Error indication, 11=Not available.

### A.28.6 Steering system readiness

조향 시스템이 guidance 동작을 막을 결함 없이 준비됐는지 알린다. 2 bits, Measured, SPN 5242. 00=System is not ready, 01=System is ready, 10=Error indication, 11=Not available.

### A.28.7 Mechanical system lockout

운전자가 자동 조향 기능을 물리적으로 차단할 수 있는 lockout 스위치의 상태다. 2 bits, Measured, SPN 5243. 00=Not active, 01=Active, 10=Error indication, 11=Not available.

### A.28.8 Guidance limit status

지속형 guidance 명령에 대한 조향 시스템의 현재 리밋 상태다. 3 bits, Measured, SPN 5726. 값 정의는 A.26.7 Tractor control limit status와 동일하다(000=Not limited ~ 111=Not available). 마찬가지로 ramp rate 제한 중 일시적으로 Limited high/low가 될 수 있고, non-recoverable fault는 임플리먼트 관점의 판단이다.

### A.28.9 Guidance system command exit/reason code

guidance 시스템이 원격 명령을 현재 받을 수 없는 이유, 또는 가장 최근에 원격 명령 수용을 중단한 이유를 나타낸다. 6 bits, Measured, SPN 5725.

| 값 | 의미 |
|---|---|
| 000000 | No reason/all clear |
| 000001 | 요구되는 운전자 재석(presence/awareness) 미감지 |
| 000010 | 임플리먼트가 기능 제어를 해제 |
| 000011 | 운전자 override |
| 000100 | 운전자 컨트롤이 유효 위치가 아님 |
| 000101 | Remote command timeout |
| 000110 | Remote command 범위 초과/무효 |
| 000111 | 기능 미보정(not calibrated) |
| 001000 | 운전자 컨트롤 fault |
| 001001 | 기능 fault |
| 001010~010011 | Reserved |
| 010100 | 유압유 레벨 과소 |
| 010101 | 유압유 온도 과소 |
| 010110 | 변속 기어 상태가 원격 명령 불허(주차 등) |
| 010111 | 차속 과소 |
| 011000 | 차속 과대 |
| 011001 | 다른 guidance 시스템 활성 |
| 011010 | 제어 유닛 진단 모드 |
| 011011~110000 | Reserved |
| 110001~111101 | Manufacturer specific |
| 111110 | Error |
| 111111 | Not available |

## A.29 ISOBUS compliance certification parameters

ISOBUS 적합성 인증 메시지에 실리는 파라미터들이다. 3판(2015)에서 기능성(functionality) 통신 방식이 ISO 11783-12로 옮겨가면서 상당수 파라미터가 deprecated 됐다.

### 핵심 파라미터

| 절 | 파라미터 | 길이 | SPN | 비고 |
|---|---|---|---|---|
| A.29.1 | Compliance test protocol publication year | 6 bits | 4313 | 1 year/bit, 2000년 offset, 범위 2000~2061 |
| A.29.2 | Compliance test protocol revision | 5 bits(3판)/3 bits(2판) | 4314 | 아래 참조 |
| A.29.3 | Certification laboratory type | 2 bits(3판)/3 bits(2판) | 4315 | 아래 참조 |
| A.29.4 | Compliance certification laboratory ID | 11 bits | 4316 | 시험 수행 랩의 manufacturer code. self-certified CF면 address claim PGN의 manufacturer code와 일치. ISO 11783-1:2007 Table B.6 기준 |
| A.29.18 | Compliance certification reference number | 16 bits | 4330 | 인증 랩이 부여한 참조 번호. Lab ID·CF Manufacturer ID와 조합해 시험 파일을 고유 식별 |
| A.29.19 | ISOBUS Compliance Certification message revision | 1 bit | 7446 | 0=2판 형식, 1=3판 이후 형식 |

<strong>A.29.2 revision 해석</strong>: A.29.19가 "1"(3판 이후)이면 5 bits, 1/bit, 0~30의 숫자 revision suffix다. "0"(2판)이면 3 bits로 알파벳 suffix를 표현한다 — 000=First revision(무suffix), 001=Second(A), 010=Third(B), 011=Fourth(C), 100~110=Reserved, 111=Not available.

<strong>A.29.3 laboratory type 해석</strong>: 3판 기준 2 bits — 00=Non-certified laboratory/self-certification, 01=AEF certified laboratory, 10=Reserved, 11=Not available. 3판 이전에는 3 bits로 000=self-test, 001=EU certified, 010=NA certified, 011~110=Reserved, 111=Not available이었다.

### Deprecated된 certification type 비트들 (A.29.5~A.29.17)

3판부터 기능성 정의·통신 방식 변경(ISO 11783-12 참조)으로 모두 deprecated 됐다. 각각 1 bit, Measured이며 0=Not certified, 1=Certification test performed.

| 절 | 대상 | SPN |
|---|---|---|
| A.29.5 | Minimum CF | 4317 |
| A.29.6 | TECU Class 1 | 4318 |
| A.29.7 | TECU Class 2 | 4319 |
| A.29.8 | TECU Class 3 | 4320 |
| A.29.9 | Class 3 ECU | 4321 |
| A.29.10 | Virtual terminal | 4322 |
| A.29.11 | VT working set master | 4323 |
| A.29.12 | VT working set member | 4324 |
| A.29.13 | Task controller | 4325 |
| A.29.14 | TC working set master | 4326 |
| A.29.15 | TC working set member | 4327 |
| A.29.16 | File server | 4328 |
| A.29.17 | GPS receiver | 4329 |

## A.30 Selected speed control parameters

머신이 여러 속도 소스 중 스스로 선택한 "대표 속도"와 관련된 파라미터 그룹이다. Machine selected speed 계열은 트랙터가 wheel/ground/navigation 기반 속도 중 현재 상황을 가장 잘 대표한다고 판단한 값을 하나로 제공한다.

### A.30.1 Machine selected speed

| 항목 | 값 |
|---|---|
| Data length | 2 bytes |
| Default value | 0 |
| Resolution | 0,001 m/s/bit (상위 바이트 0,256 m/s/bit) |
| Offset | 0 m/s |
| Data range | 0 ~ 64 255 |
| Type | Measured |
| SPN | 4305 |

### A.30.2 Machine selected distance

Machine selected speed 값을 적분한 실제 주행 거리. 4 bytes, 0,001 m/bit, 0~4 211 081,215 m, Measured, SPN 4306. 최대값을 넘으면 0으로 리셋 후 다시 누적한다.

### A.30.3 Machine selected direction

머신의 현재 주행 방향. 2 bits, Measured, SPN 4309. 00=Reverse, 01=Forward, 10=Error indication, 11=Not available. Forward/Reverse는 <strong>섀시의 정상 주행 방향</strong> 기준이며, 운전석이 반전돼도 바뀌지 않는다.

### A.30.4 Machine selected speed source

현재 machine speed 파라미터로 보고 중인 속도 소스를 나타낸다. 3 bits, Measured, SPN 4308.

| 값 | 의미 |
|---|---|
| 000 | Wheel-based speed |
| 001 | Ground-based speed |
| 010 | Navigation-based speed |
| 011 | Blended speed |
| 100 | Simulated speed |
| 101~110 | Reserved |
| 111 | Not available |

- <strong>Simulated speed</strong>: 머신이 실제로 움직이지 않을 때 임플리먼트 동작을 가능하게 하려고 시스템이 생성한 속도다.
- <strong>Blended speed</strong>: 운전자 또는 제조사가 정한 로직으로 여러 실제 속도 소스를 조합한 속도다. 예: ground 기반 속도가 0,5 m/s 미만이면 wheel 속도로 전환.

### A.30.5~A.30.7 속도 명령·리밋

| 절 | 파라미터 | 길이 | Resolution | Type | SPN | 설명 |
|---|---|---|---|---|---|---|
| A.30.5 | Machine selected speed set point command | 2 bytes | 0,001 m/s/bit | Command | 4310 | 선택 소스 기준 속도 명령 세트포인트 |
| A.30.6 | Machine selected direction command | 2 bits | — | Command | 4312 | 00=Reverse, 01=Forward, 10=Error, 11=N/A. 섀시 기준 방향 |
| A.30.7 | Machine selected speed set point limit | 2 bytes | 0,001 m/s/bit | Command | 4311 | 머신이 트랙터에 알리는 자신의 최대 허용 속도 |

### A.30.8 Machine selected speed limit status

지속형 명령 파라미터에 대한 Tractor ECU의 현재 속도 리밋 상태. 3 bits, Measured, SPN 4307. 값 정의는 A.26.7과 동일하다(000=Not limited, 001=Operator limited/controlled, 010=Limited high, 011=Limited low, 110=Non-recoverable fault, 111=Not available). ramp rate 제한 중 일시적 Limited high/low 상태가 가능하다는 주석도 동일하다.

### A.30.9 Machine selected speed exit/reason code

차량 속도 제어 유닛이 원격 명령을 받을 수 없는 이유(또는 최근 중단 사유)를 나타낸다. 6 bits, Measured, SPN 5818. 값 체계는 A.28.9 guidance exit/reason code와 거의 같다.

| 값 | 의미 |
|---|---|
| 000000 | No reason/all clear |
| 000001 | 운전자 재석 미감지 |
| 000010 | 임플리먼트가 기능 제어 해제 |
| 000011 | 운전자 override |
| 000100 | 운전자 컨트롤이 유효 위치가 아님 |
| 000101 | Remote command timeout |
| 000110 | Remote command 범위 초과/무효 |
| 000111 | 기능 미보정 |
| 001000 | 운전자 컨트롤 fault |
| 001001 | 기능 fault |
| 001010~010101 | Reserved |
| 010110 | 변속 기어 상태가 원격 명령 불허(주차 등) |
| 010111~110000 | Reserved |
| 110001~111101 | Manufacturer specific |
| 111110 | Error |
| 111111 | Not available |

## A.31 Operator direction reversed

보고되는 주행 방향이 <strong>운전자 관점</strong>에서 반전됐는지를 나타낸다. 예를 들어 운전석이 뒤로 돌려져 있어 "전진"이 실제로는 운전자를 뒤로 이동시키는 경우다. 2 bits, Type: Command, SPN 5244. 00=Not reversed, 01=Reversed, 10=Error indication, 11=Not available.

## A.32 Drive strategy parameters

트랙터의 구동 전략(drive strategy) 우선순위 구조를 다루는 파라미터 그룹이다. 구동 전략은 연비/연료 소비와 엔진 토크 여유(torque reserve) 사이의 균형을 결정한다. 우선순위 1(최상위)~4(최하위) 슬롯 각각에 현재 활성 모드를 보고(Measured)하고, 임플리먼트가 변경을 요청(Command)할 수 있다.

### 모드 값 정의 (A.32.1~A.32.4, A.32.7~A.32.10 공통, 8 bits)

| 값 | 의미 |
|---|---|
| 0x00 | Enable maximum draft power control |
| 0x01 | Enable constant PTO speed control |
| 0x02 | Enable wheel speed/PTO speed ratio control (request 계열에서는 "combined wheel/PTO speed ratio control") |
| 0x03 | Enable minimum engine speed control |
| 0x04 | Enable engine economy control |
| 0x05 | Enable maximum hydraulic power control |
| 0x06 | Enable maximum electric power control |
| 0x07~0xEC | Reserved |
| 0xED~0xFC | Manufacturer specific modes |
| 0xFD | Requested mode not supported (보고 계열) / Reserved (request 계열) |
| 0xFE | Error or reserved |
| 0xFF | Not available/Don't care |

Manufacturer specific 모드는 표준에 매핑되지 않은 모드를 트랙터가 보고하고, 임플리먼트가 그 모드에 동기화할 수 있게 하기 위한 것이다.

### 파라미터 목록

| 절 | 파라미터 | Type | SPN |
|---|---|---|---|
| A.32.1 | Drive strategy priority 1 (최상위 현재값) | Measured | 5727 |
| A.32.2 | Drive strategy priority 2 | Measured | 5728 |
| A.32.3 | Drive strategy priority 3 | Measured | 5729 |
| A.32.4 | Drive strategy priority 4 (최하위 현재값) | Measured | 5730 |
| A.32.7 | Drive strategy priority 1 request | Command | 5733 |
| A.32.8 | Drive strategy priority 2 request | Command | 5734 |
| A.32.9 | Drive strategy priority 3 request | Command | 5735 |
| A.32.10 | Drive strategy priority 4 request | Command | 5736 |

### A.32.5 Drive strategy request state

일회성(transient/one-shot) Drive Strategy 요청에 대한 트랙터의 상태 보고다. 2 bits, Type: Command, SPN 5731.

| 값 | 의미 |
|---|---|
| 00 | External Request Accepted. 이후 운전자 개입 없음 |
| 01 | Control override (가장 최근 외부 요청 무시됨) |
| 10 | Error indication |
| 11 | Not available/Not Installed |

### A.32.6 Drive strategy exit/reason code

drive strategy 서브시스템이 원격 명령을 받을 수 없는 이유(또는 최근 중단 사유)다. 6 bits, Measured, SPN 5732. 값 체계는 A.30.9와 동일하다(000000=all clear ~ 111111=Not available, 010110=변속 기어 불허, 110001~111101=Manufacturer specific 등).

### A.32.11 Restore operator drive strategy setting request

자동화(automation) 종료 시점 이전의 운전자 drive strategy 설정으로 복원하라고 요청하는 파라미터다. 2 bits, Command, SPN 5737. 00=No Request(복원 원치 않을 때 송신), 01=Restore Operator Drive Strategy Setting, 10=Error indication, 11=Not available.

## A.33 Implement in-work state

임플리먼트가 트랙터/동력 유닛에 연결되어 작업(work) 상태에 있음을 나타낸다. 2 bits, Measured, SPN 7447. 00=Not in work state, 01=In work state, 10=Error indication, 11=Not available.

## A.34 Heartbeat sequence number

heartbeat 메시지의 시퀀스 번호다. heartbeat 메시지는 CF가 송신하는 메시지·파라미터 통신의 무결성을 판단하는 데 쓰인다. 8 bits, Type: Current Value, SPN 7345.

| 값 | 의미 |
|---|---|
| 0~250 | 유효한 증가 카운터 값 |
| 251 | 카운터 초기값 |
| 252, 253 | 장래 정의용 예약. 수신 CF는 이 값을 담은 heartbeat 메시지를 무시해야 한다 |
| 254 | Error indication |
| 255 | Not available |

시퀀스 번호 검증 방법과 송수신 CF의 필요 조치는 B.33 Heartbeat message에 규정된다. 이 SPN 진단에는 다음 FMI를 쓸 수 있다: FMI 10(Abnormal Rate of Change), 11(Root Cause not Known), 12(Bad Intelligent Device or Component), 19(Received Network Data in Error). 송신자·수신자 모두 이 FMI로 heartbeat 처리 오류로 인한 기능 저하나 오류 상태의 원인을 표시할 수 있다.

## Annex B (normative) — Parameter groups

Annex B는 Part 7의 모든 메시지(PGN)를 정의한다. 각 메시지의 PGN, 송신 주기, 우선순위, 바이트 배치를 규정하고 필드 정의는 Annex A를 참조한다. 아래에 메시지별 핵심 정보를 정리한다.

### B.1 Time/Date — PGN 65254 (0x00FEE6)

- 송신: On request, 8 bytes, priority 6, PF 254/PS 230
- Bytes 1~3: Time (UTC, A.1) / Bytes 4~6: Date (A.2) / Byte 7: Local minute offset (A.3) / Byte 8: Local hour offset (A.4)

### B.2 Ground-based speed and distance — PGN 65097 (0x00FE49)

Tractor ECU가 임플리먼트 버스에 보내는 대지 기준(ground-based) 속도·거리·주행 방향 메시지다.

- 송신 주기: 100 ms, 8 bytes, priority 3, PF 254/PS 73
- Bytes 1,2: Ground-based machine speed (A.5) / Bytes 3~6: Ground-based machine distance (A.6) / Byte 7: Reserved / Byte 8 bits 2,1: Ground-based machine direction (A.7)

:::warning 저속 구간 정확도
wheel 기반·ground 기반 속도 모두 정확도가 속도 의존적이며 저속에서 저하된다. 저속에서는 wheel 기반 정보가 100 ms 주기로 갱신되지 않을 수 있다.
:::

### B.3 Wheel-based speed and distance — PGN 65096 (0x00FE48)

Tractor ECU가 보내는 휠 기준 속도·거리 메시지로, start/stop 스위치 상태·key switch 상태·운전석 반전 여부까지 포함한다.

- 송신 주기: 100 ms, 8 bytes, priority 3, PF 254/PS 72
- Bytes 1,2: Wheel-based machine speed (A.8) / Bytes 3~6: Wheel-based machine distance (A.9) / Byte 7: Maximum time of tractor power (A.12)
- Byte 8: bits 8,7 Operator direction reversed (A.31) · bits 6,5 Start/stop state (A.25.2) · bits 4,3 Key switch state (A.11) · bits 2,1 Wheel-based machine direction (A.10)

이그니션 키를 끈 뒤에도 ECU_PWR·PWR을 유지해 이 메시지를 추가 2초간 송신해야 한다(엔진 크랭킹 중에는 불요). 이 2초가 아래 B.4 Maintain power 요청의 트리거 창이 된다.

### B.4 Maintain power — PGN 65095 (0x00FE47)

임플리먼트 버스의 임의 CF가 "이그니션 OFF를 알리는 wheel-based speed and distance 메시지를 받은 뒤에도 2초간 전원을 끄지 말라"고 Tractor ECU에 요청하는 메시지다. 연결된 임플리먼트의 운용 상태도 함께 실린다.

- 송신: 이그니션 ON→OFF 전환 메시지 수신 후 필요 시, 또는 파라미터 상태 변화 시. 8 bytes, priority 6, PF 254/PS 71
- Byte 1: bits 8,7 Maintain ECU power (A.13) · bits 6,5 Maintain actuator power (A.14)
- Byte 2: bits 8,7 Implement transport state (A.15) · bits 6,5 Implement park state (A.16) · bits 4,3 Implement ready-to-work state (A.17) · bits 2,1 Implement in-work state (A.33)
- Bytes 3~8: Reserved

### B.5 Navigation location system messages

ISO 11783 네트워크는 IEC 61162-3(NMEA 2000)의 항법 위치 메시지를 사용해야 한다. 권장(최소) 메시지는 "GNSS position data", "Position delta, high precision rapid update", "COG & SOG, Rapid Update", "GNSS pseudo-range noise statistics"다. 복수 데이터 프레임이 필요한 메시지는 ISO 11783-3의 transport protocol이 아니라 <strong>NMEA fast packet protocol</strong>을 써야 한다.

### B.6 Secondary or front hitch status — PGN 65094 (0x00FE46)

전방 히치 파라미터 측정값 메시지. 100 ms, 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Byte 1 | Front hitch position (A.19.1) |
| Byte 2 bits 8,7 | Front hitch in-work indication (A.19.5) |
| Byte 2 bits 6~4 | Front hitch position limit status (A.19.11) |
| Byte 3 | Front nominal lower link force (A.19.9) |
| Bytes 4,5 | Front draft (A.19.7) |
| Byte 6 bits 6~1 | Front hitch exit/reason code (A.19.13) |
| 나머지 | Reserved |

### B.7 Primary or rear hitch status — PGN 65093 (0x00FE45)

후방 히치 파라미터 측정값 메시지. 100 ms, 8 bytes, priority 3. 구조는 B.6과 대칭이다: Byte 1 Rear hitch position (A.19.2), Byte 2 bits 8,7 Rear hitch in-work indication (A.19.6), bits 6~4 Rear hitch position limit status (A.19.12), Byte 3 Rear nominal lower link force (A.19.10), Bytes 4,5 Rear draft (A.19.8), Byte 6 bits 6~1 Rear hitch exit/reason code (A.19.14).

### B.8 Secondary or front PTO output shaft — PGN 65092 (0x00FE44)

전방 PTO 출력축 측정값 메시지. engaged 상태에서 100 ms, 그 외에는 on request. 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Bytes 1,2 | Front PTO output shaft speed (A.20.1) |
| Bytes 3,4 | Front PTO output shaft speed set point (A.20.3) |
| Byte 5 bits 8,7 | Front PTO engagement (A.20.7) |
| Byte 5 bits 6,5 | Front PTO mode (A.20.9) |
| Byte 5 bits 4,3 | Front PTO economy mode (A.20.11) |
| Byte 5 bits 2,1 | Front PTO engagement request status (A.20.19) |
| Byte 6 bits 8,7 | Front PTO mode request status (A.20.20) |
| Byte 6 bits 6,5 | Front PTO economy mode request status (A.20.21) |
| Byte 6 bits 4~2 | Front PTO shaft speed limit status (A.20.22) |
| Byte 7 bits 6~1 | Front PTO exit/reason code (A.20.27) |
| 나머지 | Reserved |

### B.9 Primary or rear PTO output shaft — PGN 65091 (0x00FE43)

후방 PTO 출력축 측정값 메시지. 구조·주기는 B.8과 대칭이다(engaged 시 100 ms). Bytes 1,2 Rear PTO output shaft speed (A.20.2), Bytes 3,4 set point (A.20.4), Byte 5: engagement (A.20.8)/mode (A.20.10)/economy mode (A.20.12)/engagement request status (A.20.23), Byte 6: mode request status (A.20.24)/economy mode request status (A.20.25)/shaft speed limit status (A.20.26), Byte 7 bits 6~1: Rear PTO exit/reason code (A.20.28).

### B.10 Hitch and PTO commands — PGN 65090 (0x00FE42)

히치 위치, PTO 축 세트포인트 속도, PTO engagement를 제어하는 명령 메시지다. 활성 시 100 ms, 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Byte 1 | Front hitch position command (A.19.3) |
| Byte 2 | Rear hitch position command (A.19.4) |
| Bytes 3,4 | Front PTO output shaft speed set point command (A.20.5) |
| Bytes 5,6 | Rear PTO output shaft speed set point command (A.20.6) |
| Byte 7 bits 8,7 / 6,5 | Front / Rear PTO engagement (A.20.13 / A.20.14) |
| Byte 8 bits 8,7 / 6,5 | Front / Rear PTO mode command (A.20.15 / A.20.16) |
| Byte 8 bits 4,3 / 2,1 | Front / Rear PTO economy mode command (A.20.17 / A.20.18) |

### B.11 Auxiliary valve 0 estimated flow — PGN 65040 (0x00FE10)

auxiliary valve 0번의 추정 유량 메시지. 이 밸브는 "power beyond" 제어에 쓰인다. 100 ms, 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Byte 1 | Extend port estimated flow (A.21.4) |
| Byte 2 | Retract port estimated flow (A.21.5) |
| Byte 3 bits 8,7 | Fail safe mode (A.21.13) |
| Byte 3 bits 4~1 | Valve state (A.21.6) |
| Byte 4 bits 8~6 | Limit status (A.21.15) |
| Byte 5 bits 6~1 | Exit/reason code (A.21.16) |
| 나머지 | Reserved |

### B.12 Auxiliary valve 0 measured flow — PGN 65056 (0x00FE20)

auxiliary valve 0번의 측정값 메시지("power beyond" 제어용). 100 ms, 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Byte 1 | Extend port measured flow (A.21.2) |
| Byte 2 | Retract port measured flow (A.21.3) |
| Bytes 3,4 | Extend port pressure (A.21.7) |
| Bytes 5,6 | Retract port pressure (A.21.8) |
| Byte 7 | Return port pressure (A.21.9) |
| Byte 8 bits 8~6 | Limit status (A.21.14) |

### B.13 Auxiliary valve 0 command — PGN 65072 (0x00FE30)

auxiliary valve 0번 유량 제어 명령. 활성 시 100 ms, 8 bytes, priority 3.

| 위치 | 내용 |
|---|---|
| Byte 1 | Port flow command (A.21.10) |
| Byte 3 bits 8,7 | Fail safe mode command (A.21.12) |
| Byte 3 bits 4~1 | State command (A.21.11) |
| 나머지 | Reserved |

### B.14 Auxiliary valve 1~14 messages

이 표준은 valve 0과 valve 15 메시지만 명시적으로 정의한다. valve 1~14의 메시지 정의는 valve 15에 대한 B.15/B.16/B.17과 동일하며, valve 번호만 다르다. PGN은 규칙적으로 배정된다.

| Valve n | Estimated flow | Measured flow | Command |
|---|---|---|---|
| 0 | 65040 (0xFE10) | 65056 (0xFE20) | 65072 (0xFE30) |
| 1 | 65041 (0xFE11) | 65057 (0xFE21) | 65073 (0xFE31) |
| 2 | 65042 (0xFE12) | 65058 (0xFE22) | 65074 (0xFE32) |
| ... | ... | ... | ... |
| 14 | 65054 (0xFE1E) | 65070 (0xFE2E) | 65086 (0xFE3E) |
| 15 | 65055 (0xFE1F) | 65071 (0xFE2F) | 65087 (0xFE3F) |

즉 estimated flow는 0xFE10+n, measured flow는 0xFE20+n, command는 0xFE30+n이다 (n=0~15, 단 valve 15 command는 0xFE3F).

### B.15 Auxiliary valve 15 estimated flow — PGN 65055 (0x00FE1F)

100 ms, 8 bytes, priority 3. Byte 1: extend port estimated flow (A.21.20), Byte 2: retract port estimated flow (A.21.21), Byte 3: fail safe mode (A.21.29)/valve state (A.21.22), Byte 4 bits 8~6: estimated limit status (A.21.49), Byte 5 bits 6~1: exit/reason code (A.21.32).

### B.16 Auxiliary valve 15 measured flow — PGN 65071 (0x00FE2F)

100 ms, 8 bytes, priority 3. Byte 1: extend port measured flow (A.21.18), Byte 2: retract port measured flow (A.21.19), Bytes 3,4: extend port pressure (A.21.23), Bytes 5,6: retract port pressure (A.21.24), Byte 7: return port pressure (A.21.25), Byte 8 bits 8~6: limit status (A.21.30).

### B.17 Auxiliary valve 15 command — PGN 65087 (0x00FE3F)

활성 시 100 ms, 8 bytes, priority 3. Byte 1: port flow command (A.21.26), Byte 3: fail safe mode command (A.21.28)/state command (A.21.27).

### B.18 Lighting command — PGN 65089 (0x00FE41)

트랙터가 트랙터·부착 임플리먼트의 모든 조명 컨트롤러에 보내는 전역(global) 메시지다. 트랙터/임플리먼트의 작업등·주행등 파라미터가 분리되어 있고, 특수 장비를 위한 임플리먼트 OEM 옵션 조명 명령과 공통 marking/signalling 파라미터가 제공된다.

운용 규칙:

- 램프 상태 변화 시마다, 그리고 방향지시등·비상등 동기화를 위해 주기적으로 송신한다.
- 상태 값은 켬(ON)/끔(OFF)을 지시하며, 점멸(flashing)은 ON/OFF를 교대로 담은 메시지를 반복 송신해 구현한다.
- <strong>최소 1초에 1회</strong>는 lighting command를 송신해야 하며, 전체 조명 기준 초당 10 메시지를 넘지 않는다.
- 지역 법규에 맞는 램프 명령 조합을 구성하는 것은 트랙터 설계자의 책임이다.

8 bytes, priority 3, PF 254/PS 65.

| Byte | bits 8,7 | bits 6,5 | bits 4,3 | bits 2,1 |
|---|---|---|---|---|
| 1 | High-beam headlights (A.22.1) | Low-beam headlights (A.22.3) | Alternate headlights (A.22.5) | Daytime running lights (A.22.61) |
| 2 | Left-turn signal (A.22.21) | Right-turn signal (A.22.23) | Rotating beacon (A.22.39) | Tractor front fog (A.22.41) |
| 3 | Left stop (A.22.25) | Right stop (A.22.27) | Centre stop (A.22.29) | Back-up lights and alarm horn (A.22.51) |
| 4 | Tractor marker (A.22.31) | Implement marker (A.22.33) | Tractor clearance (A.22.35) | Implement clearance (A.22.37) |
| 5 | Tractor rear high-mounted work (A.22.15) | Tractor rear low-mounted work (A.22.13) | Tractor underside-mounted work (A.22.11) | Rear fog (A.22.43) |
| 6 | Tractor front high-mounted work (A.22.9) | Tractor front low-mounted work (A.22.7) | Tractor side high-mounted work (A.22.19) | Tractor side low-mounted work (A.22.17) |
| 7 | Implement left forward work (A.22.53) | Implement right forward work (A.22.55) | Implement OEM option 1 (A.22.47) | Implement OEM option 2 (A.22.49) |
| 8 | Implement rear work (A.22.45) | Implement left-facing work (A.22.57) | Implement right-facing work (A.22.59) | Lighting data message request command (A.22.63) |

(모든 항목은 command 파라미터다.)

### B.19 Lighting data — PGN 65088 (0x00FE40)

lighting command 메시지 안의 lighting data 요청에 대한 응답이다. 요청을 받으면 트랙터·임플리먼트의 <strong>각 조명 컨트롤러</strong>가 Tractor ECU로 이 메시지를 송신해야 하고, 트랙터는 이를 통해 어느 조명 계통이 동작 중인지 판단한다. 램프 감지(lamp-sensing) 능력이 있는 컨트롤러는 전구 고장도 보고해야 한다 — 많은 지역에서 법적 요구사항이다.

- 송신: As requested, 8 bytes, priority 6, PF 254/PS 64
- 바이트 배치는 B.18과 동일한 구조로, 각 위치에 command가 아닌 <strong>상태 파라미터</strong>(A.22.2, A.22.4, ... 짝수 절)가 실린다. Byte 8 bits 2,1은 Reserved다.

### B.20 Background lighting level command — PGN 53248 (0x00D000)

계기·스위치 등 배경 조명(background lighting) 상태를 제어하는 메시지다. 배경 조명 레벨이 바뀔 때마다 송신하며, 메시지 간 최대 5초 간격을 지킨다.

- 8 bytes, priority 3, PDU format 208(destination-specific, PS=DA)
- Byte 1: Background illumination level (A.22.64), Bytes 2~8: Reserved

### B.21 Language command — PGN 65039 (0x00FE0F)

연결된 시스템이 사용할 언어·날짜/시간 형식·측정 단위를 ISO 11783 버스의 모든 CF에 알리는 전역 메시지다.

동작 규칙(해설):

- 시스템의 power-on과 address claim이 끝나면 <strong>VT가 이 메시지를 송신</strong>해야 한다.
- 원하는 언어를 임플리먼트 CF가 지원하지 않을 때를 대비해 Tractor ECU와 설치된 VT에 기본 언어가 저장되어 있어야 한다.
- VT는 연결된 임플리먼트(풀)의 지원 언어 목록을 운전자가 보고 선택할 수 있는 방법을 제공해야 한다.
- 공장 초기 상태의 VT처럼 운전자가 언어를 고른 적이 없으면, VT는 Tractor ECU에서 기본 언어를 요청해 자신의 기본 언어로 저장한다.
- 운전자가 언어를 설정한 뒤에는 <strong>VT의 language 메시지가 Tractor ECU의 기본 언어보다 항상 우선</strong>한다. 선택된 언어는 다음 power-up에 쓰이도록 Tractor ECU·VT(또는 둘 다)에 저장한다.

- 송신: 시스템 초기화 시 및 on request. 8 bytes, priority 6, PF 254/PS 15
- Bytes 1,2: Language code (A.23.1)
- Byte 3: bits 8,7 Decimal symbol (A.23.2) · bits 6,5 Time format (A.23.4)
- Byte 4: Date format (A.23.3)
- Byte 5: bits 8,7 Distance units (A.23.5.2) · 6,5 Area units (A.23.5.3) · 4,3 Volume units (A.23.5.4) · 2,1 Mass units (A.23.5.5)
- Byte 6: bits 8,7 Temperature units (A.23.5.6) · 6,5 Pressure units (A.23.5.7) · 4,3 Force units (A.23.5.8) · 2,1 Units system (A.23.5.9)
- Bytes 7,8: Reserved

### B.22 Flexible repetition rates

#### B.22.1 Request for repetition rate — PGN 52224 (0x00CC00)

메시지 사용자 필요에 맞게 버스 대역폭을 조정할 수 있게 하는 메커니즘이다. 특정 PGN의 사용자는 원하는 송신 주기를 요청할 수 있고, 0x0000을 보내면 기본 주기를 요청하는 것이다. 요청된 PGN의 소스는 가능하다면 요청을 존중한다.

프로토콜 규칙:

- CF가 이 메시지를 상시 모니터링할 의무는 없다. 고정 타이밍 제어 루프가 필요한 시스템 등 요청 주기를 쓸 수 없거나 원치 않는 CF는 무시해도 된다.
- 요청자는 요청 송신 후 <strong>250 ms</strong> 동안 response for repetition rate가 없으면 요청이 수락되지 않은 것으로 간주해야 한다.
- 새 주기를 수락하는 소스는 response for repetition rate를 보내고 <strong>250 ms 대기 후</strong> 새 주기로 전환해야 한다.
- 다른 주기 요청을 받은 뒤 250 ms 이내에 0x0000(기본 주기) 요청도 받으면 기본 주기를 사용해야 한다.

- On request, 8 bytes, priority 6, PDU format 204(destination-specific)
- Bytes 1~3: 주기를 요청할 대상 PGN (ISO 11783-3 형식) / Bytes 4,5: Repetition rate command (A.23.6) / Bytes 6~8: Reserved

#### B.22.2 Response for repetition rate — PGN 65038 (0x00FE0E)

주기 변경 요청에 대한 전역 응답 메시지다. 데이터 필드는 요청과 같은 구조이며, repetition rate 값에는 송신자의 <strong>실제 값</strong>이 실린다. On request, 8 bytes, priority 6, PF 254/PS 14. Bytes 1~3: 요청의 PGN, Bytes 4,5: Repetition rate (A.23.7), Bytes 6~8: 요청과 동일.

### B.23 Working set messages

#### B.23.1 General — working set 개념

working set은 여러 control function(CF)이 분산 프로세스로서 <strong>하나의 애플리케이션을 이루는</strong> 경우의 통신을 지원한다. 각 CF는 고유 NAME을 가지며, 하나의 ECU 안에 있을 수도, 네트워크에 연결된 서로 다른 ECU에 있을 수도 있다. 서로 다른 NAME들이 하나의 임플리먼트로 기능해야 할 때 working set을 쓴다.

- working set마다 하나의 CF가 <strong>working set master</strong>로 지정된다. master의 주소는 one-to-many 통신에서 "global"의 부분집합처럼 쓰이고, service provider(수신 CF)가 여러 CF를 하나의 working set으로 묶어 인식할 수 있게 한다. 실제 통신은 결국 one-to-one이 되며, service provider는 working set 대상 데이터 대부분을 master의 주소로 보낸다.
- 표시 데이터 같은 메시지는 개별 멤버가 직접 보낼 수 있다. working set 멤버에게 온 요청에 대한 응답은 수신 CF(service provider)가 <strong>요청한 working set master에게</strong> 보낸다. 이 구조 덕에 transport protocol로 멤버에게 응답을 보낼 수 있다. 멤버는 다른 멤버 앞으로 온 목적지 지정 메시지를 감시할 의무가 없다.
- 네트워크의 다른 CF는 master에게 보내거나, 필요하면 멤버에게 직접 보내는 방식으로 working set과 상호작용할 수 있다. 멤버로부터 받은 메시지는 해당 working set에 속한 것으로 해석해야 한다.
- Task controller 명령은 <strong>working set master에게만</strong> 보낸다. master가 멤버들에게 명령을 전달하는 방법은 그 working set 설계의 고유(proprietary) 영역이다.

예: 파종기(planter)가 row마다 하나씩 Working Set Member를 두고 master가 총괄한다. 연결된 VT는 master와 각 멤버의 명령을 받고, 각 멤버는 자기 row의 표시를 갱신한다.

working set 정의에는 두 메시지가 필요하다 — 크기를 정의하는 master 메시지와 멤버를 식별하는 member 메시지. 둘 다 master가 송신한다. 실제 활용 방식은 각 응용 계층 문서(ISO 11783-6, -10 등)에서 제한·변형될 수 있다.

#### B.23.2 Working Set Master message — PGN 65037 (0x00FE0D)

working set에 몇 명의 멤버가 있는지 알리는 메시지다. master 자신도 멤버 수에 포함된다. 이 메시지의 source address가 master의 NAME과 연결되며, working set은 master의 NAME으로 식별할 수 있다.

- As required, 8 bytes, priority 7, PF 254/PS 13
- Byte 1: Number of members in working set (A.24.1), Bytes 2~8: Reserved

#### B.23.3 Working Set Member message — PGN 65036 (0x00FE0C)

특정 working set의 개별 멤버를 식별하는 메시지다(master의 SA가 어느 working set인지 식별). master가 보내는 이 메시지의 개수는 <strong>멤버 수 − 1</strong>이다. master의 NAME은 별도 메시지 없이 master의 address claim에서 얻는다. working set과 통신하는 CF는 member 메시지를 정확한 개수만큼 받았는지 검증해 전체 멤버를 식별해야 한다.

- As required, 8 bytes, priority 7, PF 254/PS 12
- Bytes 1~8: 해당 멤버의 NAME (멤버가 claim한 SA로 식별, A.24.2)

#### B.23.4 Working Set application rules

"service provider"는 working set과 별도 개체로서 통신하는 network control function이다(단일 ECU일 수도, ECU 내 여러 CF 중 하나일 수도 있다). 기술 대상 working set의 멤버는 아니지만 다른 working set의 멤버/master일 수는 있다.

적용 규칙:

- <strong>a) 메시지 순서와 재시도</strong> — working-set-master 메시지 뒤에는 반드시 적정 개수(크기 − 1)의 working-set-member 메시지가 따라와야 한다. 멤버 정의를 정확한 개수만큼 받지 못한 service provider는 master에게 working-set-master PGN을 요청하고, master는 요청을 받으면 master 메시지 + 멤버 메시지 전체를 다시 보내 set을 완전하게 정의해야 한다. working set을 쓰지 않는 애플리케이션은 working set 메시지를 무시하고 다른 CF들과 직접 통신하면 된다. 응용 계층 문서에 다른 규정이 없는 한, service provider는 <strong>최소 3회</strong> 완전한 멤버 목록 획득에 실패하면 그 working set을 무시할 수 있다.
- <strong>b) 타이밍</strong> — working set은 멤버들의 NAME으로 정의된다. working-set-member 메시지는 100 ms 간격으로 송신된다. 마지막 member 메시지 후 <strong>350 ms</strong>가 지나면 수신자는 master가 모든 멤버 NAME 송신을 마쳤다고 간주해야 한다.
- <strong>c) 멤버의 개별성</strong> — 멤버도 네트워크의 개별 CF이므로 개별 CF로서 통신한다. fault 메시지는 각 CF의 SA에서 송신되고, fault table 클리어·프로그램 파라미터 등의 명령은 대상 CF의 개별 SA로 보내야 한다. 멤버는 자신에게 오지 않은 프로그래밍을 전체 멤버가 수락하는 일 없이, master로의 개별 통신을 허용하도록 프로그래밍되어야 한다.
- <strong>d) 유일 소속과 재정의</strong> — 각 CF는 <strong>둘 이상의 working set 멤버가 될 수 없다</strong>. 기존 master가 새 working-set-master 메시지를 내면 service provider는 이전 정의를 새 정의로 교체해야 한다. 변경이 필요하면 master가 재정의 책임을 지며, working set이 더 이상 필요 없으면 멤버 수 0인 master 메시지를 보내야 한다.
- <strong>e) NAME 변경</strong> — master가 NAME을 바꾸면 새 working set을 만들어야 한다. 이전 working set은 더 이상 존재하지 않지만 d)의 클린업(멤버 수 0 송신) 전까지 service provider 메모리에 정의가 남을 수 있다. 멤버 중복의 감지·정정 책임은 그 working set의 service provider에 있다. service provider는 주기적으로 중복·미사용 working set을 점검해 메모리를 회수하는 식으로 자원을 관리해야 한다.
- <strong>f) master SA 변경</strong> — master의 SA 변경은 set 정의를 바꾸지 않는다. service provider는 새 address claim 수신 시 SA-NAME 연계를 갱신하고, 멤버들은 working set 통신 수신에 쓰는 주소를 바꿔야 한다.
- <strong>g) 멤버 SA 변경</strong> — 멤버가 SA를 바꾸면 service provider는 새 SA를 해당 working set과 다시 연계해야 한다. working set은 NAME으로 정의되므로, NAME이 그대로라면 SA 변경은 새 address claim 수신 처리만으로 대응할 수 있다.
- <strong>h) 멤버 NAME 관리 책임</strong> — working set 멤버 전원의 NAME을 파악하는 책임은 master에 있다. 멤버가 네트워크에 들어오거나 나가면 master가 working set 정의를 갱신해야 한다. service provider는 member 메시지에 명시된 총원 그대로 working set을 만들고, 멤버들이 주소를 claim할 때 SA를 붙여 나간다.

### B.24 Tractor control messages

#### B.24.1 Tractor control mode command — PGN 65035 (0x00FE0B) [deprecated]

3판부터 <strong>deprecated이며 신규 설계에 쓰면 안 된다</strong>. task controller 또는 임플리먼트가 Tractor ECU로 보내는 메시지로, 하나의 메시지에 두 개의 명령이 실린다. 다수의 명령 모드가 상호 배타적이라 이렇게 묶었다.

- 송신 주기: 기본 100 ms, closed-loop cruise control은 최대 10 ms. slip control 기능 설정은 10초에 1회 + 상태 변화 시. <strong>15초 동안 갱신이 없으면 Tractor ECU는 no-slip control로 복귀한다.</strong>
- 8 bytes, priority 3. Byte 1/2 bits 8~4: mode command number 1/2 (A.26.2.1), Bytes 3,4 / 6,7: command value number 1/2 (A.26.3), Byte 5/8: limit command number 1/2 (A.26.8)

#### B.24.2 Tractor control command tractor response — PGN 65034 (0x00FE0A) [deprecated]

역시 3판부터 deprecated. 명령마다(on every command) 응답으로 송신한다. Byte 1/2: mode response number 1/2 (A.26.4) + limit status number 1/2 (A.26.7), Bytes 3,4 / 6,7: value response number 1/2 (A.26.5), Byte 5/8: control limit number 1/2 (A.26.6).

#### B.24.3 Tractor facility response message — PGN 65033 (0x00FE09)

임플리먼트 CF나 task controller의 트랙터 클래스·기능 요청에 대한 트랙터의 응답이다. power-up 시 1회, 이후 on request로 송신한다. 8 bytes, priority 3.

각 facility 비트는 A.27.5(response)의 1 bit 정의(0=불가, 1=가능)를 따른다.

| 위치 | 내용 |
|---|---|
| Byte 1 bits 8,7 | Tractor class (A.27.4) |
| Byte 1 bits 6~1 | <strong>Class 1 facilities</strong>: key switch, maximum time tractor power, maintain power, wheel-based speed, ground-based speed, engine speed |
| Byte 2 bits 8~4 | Class 1 계속: rear hitch position, rear in work, rear PTO shaft speed, rear PTO shaft engagement, 최소 조명 세트(기존 트레일러 커넥터 수준) |
| Byte 2 bit 3 | Language command storage in Tractor ECU |
| Byte 2 bits 2,1 | Reserved — 0으로 설정 |
| Byte 3 bits 8~1 | <strong>Class 2 facilities</strong>: time date, ground-based distance, ground-based direction, wheel-based distance, wheel-based direction, rear draft, full implement lighting message set, estimated/measured auxiliary valve status |
| Byte 4 bits 8~3 | <strong>Class 3 facilities</strong>: rear hitch position command, rear PTO speed command, rear PTO engagement command, auxiliary valve commands, Limit/request status reporting (A.27.8), rear PTO mode/gear command |
| Byte 4 bits 2,1 | Reserved — 0 |
| Byte 5 bits 8~1 | <strong>Addendum N</strong>: navigational system high-output position, navigational system position data, navigational pseudo-range noise statistics, (reserved), operator external light controls, machine selected speed, machine selected speed control, direction control |
| Byte 6 bits 8~1 | <strong>Addendum F</strong>(front 계열): front hitch position, front in work, front PTO shaft speed, front PTO shaft engagement, front draft, front hitch position command, front PTO speed command, front PTO engagement command |
| Byte 7 bit 8 | front PTO mode/gear command |
| Byte 7 bit 2 / bit 1 | External Guidance Status and Commands / Drive Strategy Status and Commands |
| Byte 8 bit 1 | Reserved bit indicator (A.27.6) — reserved bit가 0임을 나타내려면 0으로 설정 |
| 그 외 | Reserved — 0 |

:::warning 하위 호환 처리 (Byte 8/Bit 1)
Byte 8/Bit 1이 "1"이면 다음 비트들은 "Reserved"로 간주해야 한다: Byte 2 bits 1,2 · Byte 4 bits 1~4 · Byte 5 bits 1~5 · Byte 7 bits 1~8 · Byte 8 bits 2~8. 신규 facility 지원을 "1"로 표시할 수 있으려면 reserved bit는 "0"이어야 하는데, 이전 판에서는 이를 명시하지 않아 관례대로 "1"로 채워졌기 때문에 이 판별 비트가 필요하다.
:::

주의: 3판부터 최소 조명 세트(Byte 2 bit 4)는 Classification 1 요구사항이 아니라 <strong>Classification 2</strong> 요구사항이다.

#### B.24.4 Required tractor facilities message — PGN 65032 (0x00FE08)

임플리먼트 CF/task controller가 Tractor ECU에 원하는 트랙터 클래스·기능을 <strong>요청</strong>하는 메시지다. On request, 8 bytes, priority 3. 바이트·비트 배치는 B.24.3과 완전히 동일하되, 각 비트가 A.27.3(request: 0=불요, 1=요구), Byte 1 bits 8,7이 A.27.2(class request), Byte 4 bit 4가 A.27.7(Limit/request status reporting 요구)로 해석된다. Byte 8/Bit 1의 reserved bit indicator 규칙(NOTE 1·2)도 동일하다.

### B.25 General-purpose valve messages

#### B.25.1 General

general-purpose valve 메시지는 ISO 11783 네트워크에 연결된 <strong>컨트롤러 내장형 유압 밸브</strong>용이다. TECU를 통하거나, TECU를 master로 하는 Working Set을 통하거나, 임플리먼트 버스에서 통신하는 closed system을 통해 임플리먼트 버스의 컨트롤러와 인터페이스하는 폐쇄 시스템에서 사용한다. auxiliary valve 메시지(B.11~B.17)와 달리 <strong>destination-specific</strong>(PDU1 형식)이다.

#### B.25.2 General-purpose valve estimated flow — PGN 50688 (0x00C600)

100 ms, 8 bytes, priority 3, PF 198(DA). Byte 1: extend port estimated flow (A.21.35), Byte 2: retract port estimated flow (A.21.36), Byte 3: fail safe mode (A.21.44)/valve state (A.21.37), Byte 4 bits 8~6: limit status (A.21.50).

#### B.25.3 General-purpose valve measured flow — PGN 50432 (0x00C500)

100 ms, 8 bytes, priority 3, PF 197(DA). Byte 1: extend port measured flow (A.21.18), Byte 2: retract port measured flow (A.21.34), Bytes 3,4: extend port pressure (A.21.38), Bytes 5,6: retract port pressure (A.21.39), Byte 7: return port pressure (A.21.40), Byte 8 bits 8~6: limit status (A.21.49).

#### B.25.4 General-purpose valve command — PGN 50176 (0x00C400)

활성 시 100 ms, 8 bytes, priority 3, PF 196(DA). Byte 1: port flow command (A.21.41), Byte 3: fail safe mode (A.21.44)/valve state (A.21.37).

#### B.25.5 General-purpose valve load sense pressure — PGN 1792 (0x000700)

밸브의 load sense 압력·pilot 압력 측정값 메시지다. 밸브 어셈블리가 지원하면 어셈블리의 load sense·supply 압력도 함께 제공한다. 활성 시 100 ms, 8 bytes, priority 6, PF 07(DA). Bytes 1,2: valve load sense pressure (A.21.45), Byte 3: pilot pressure (A.21.46), Bytes 4,5: assembly load sense pressure (A.21.47), Bytes 6,7: assembly supply pressure (A.21.48).

### B.26 Guidance system messages

#### B.26.1 Guidance system command — PGN 44288 (0x00AD00)

자동 guidance 제어 시스템이 machine steering system(TECU가 대표)에 보내는 메시지다. 조향 명령을 전달하는 동시에 guidance 시스템과 조향 제어 시스템 사이의 <strong>heartbeat</strong> 역할을 한다.

- 100 ms, 8 bytes, priority 3, PF 173(destination-specific)
- Bytes 1,2: Curvature command (A.28.1) / Byte 3 bits 2,1: Curvature command status (A.28.3) / 나머지: Reserved

#### B.26.2 Guidance machine status — PGN 44032 (0x00AC00)

machine steering system이 guidance 제어 시스템에 주는 피드백 메시지다. 조향 제어 시스템의 정보·상태를 guidance 시스템에 제공한다.

- 100 ms, 8 bytes, priority 3, PF 172(destination-specific)

| 위치 | 내용 |
|---|---|
| Bytes 1,2 | Estimated curvature (A.28.2) |
| Byte 3 bits 8,7 | Request reset command status (A.28.4) |
| Byte 3 bits 6,5 | Steering input position status (A.28.5) |
| Byte 3 bits 4,3 | Steering system readiness (A.28.6) |
| Byte 3 bits 2,1 | Mechanical system lockout (A.28.7) |
| Byte 4 bits 8~6 | Guidance limit status (A.28.8) |
| Byte 5 bits 6~1 | Guidance system command exit/reason code (A.28.9) |
| 나머지 | Reserved |

### B.27 ISOBUS compliance certification message — PGN 64834 (0x00FD42)

특정 ECU의 적합성 인증 상태를 보고한다. On request, 8 bytes, priority 6, PF 253/PS 66.

3판(현행) 형식:

| 위치 | 내용 |
|---|---|
| Byte 1 bits 8,7 | compliance test protocol revision의 LSBits(2–1) (A.29.2) |
| Byte 1 bits 6~1 | compliance test protocol publication year (A.29.1) |
| Byte 2 bits 8~6 | certification lab ID 하위 비트 (A.29.4) |
| Byte 2 bits 5,4 | protocol revision의 MSBits(5–4) (A.29.2) |
| Byte 2 bits 3,2 | certification laboratory type (A.29.3) |
| Byte 2 bit 1 | protocol revision의 bit 3 (A.29.2) |
| Byte 3 | certification lab ID 상위 비트 (A.29.4) |
| Bytes 4,5 | Reserved — 0 |
| Byte 6 bit 8 | ISOBUS Compliance Certification message revision (A.29.19) |
| Byte 6 bits 7~1 | Reserved — 0 |
| Bytes 7,8 | Compliance certification reference number (A.29.18) |

3판부터 기능성(functionality)의 구성·통신이 바뀌었다(ISO 11783-12 참조). 3판 이전 형식은 Byte 4에 Minimum CF/TECU Class 1~3/Class 3 ECU/VT/VT WS master/VT WS member 비트, Byte 5에 Task controller/TC WS master/TC WS member/File server/GPS receiver 비트(A.29.5~A.29.17)를 실었고 revision 필드가 3 bits + MSBit 구성이었다.

### B.28 Machine selected speed messages

#### B.28.1 Machine selected speed — PGN 61474 (0x00F022)

현재 machine selected speed·방향·소스 파라미터를 제공하는 메시지다. 100 ms, 8 bytes, priority 3, PF 240/PS 34.

| 위치 | 내용 |
|---|---|
| Bytes 1,2 | Machine selected speed (A.30.1) |
| Bytes 3~6 | Machine selected distance (A.30.2) |
| Byte 7 bits 6~1 | Machine selected speed exit/reason code (A.30.9) |
| Byte 8 bits 8~6 | Machine selected speed limit status (A.30.8) |
| Byte 8 bits 5~3 | Machine selected speed source (A.30.4) |
| Byte 8 bits 2,1 | Machine selected direction (A.30.3) |

#### B.28.2 Machine selected speed command — PGN 64835 (0x00FD43)

머신 속도·방향 제어 메시지다. 100 ms, 8 bytes, priority 3, PF 253/PS 67. Bytes 1,2: speed set point command (A.30.5), Bytes 3,4: speed set point limit (A.30.7), Byte 8 bits 2,1: direction command (A.30.6).

### B.29 Implement operating state command — PGN 64771 (0x00FD03)

Tractor ECU가 임플리먼트 버스로 보내는, 현재 명령된 임플리먼트 운용 상태 메시지다(임업·농업 임플리먼트 대상). 1초 주기 + 상태 변화 시, 8 bytes, priority 3, PF 253/PS 03. Byte 8 bits 2,1: Implement operating state command (A.25.1), 나머지 Reserved.

### B.30 All implements stop operations switch state — PGN 64770 (0x00FD02)

임플리먼트 버스에 연결된 임의 CF가 송신할 수 있는, all implement stop operations 스위치(ISB)의 현재 상태 방송 메시지다. 연결된 시스템의 <strong>각 운전자 위치마다 이 스위치가 최소 1개</strong> 있어야 한다.

동작 규칙(해설):

- 임의 CF로부터 "Stop implement operations"(A.25.3) 값의 방송을 받으면 <strong>모든 임플리먼트는 전체 동작 정지 절차를 시작해야 한다</strong>.
- 임플리먼트는 모든 동작을 끄기 전에 failsafe 상태로 진입해야 한다. 자동화 모드(PTO, auxiliary valve, 트랙터 이동 등)로 동작 중이라면, Tractor ECU에 자동화 모드 종료를 요청하기 전에 failsafe 상태로 들어갈 수 있다.
- 정지 후, 임플리먼트의 working set master는 Stop All Implement Operations 스위치 활성화로 동작이 정지됐음을 운전자에게 알려야 한다.
- working set master는 Stop All Implement Operations를 지원한다면 홈 화면에 아이콘·기능명 등의 표시를 넣어야 한다.
- Working Set은 각 ISB 서버의 첫 메시지 수신 시점부터 transition number를 추적해야 하며, Stop all implement operations 상태 전환 없이 transition 수만 증가하면 <strong>오류로 간주하고 대응</strong>해야 한다.

- 1초 주기 + 상태 변화 시, 8 bytes, priority 3, PF 253/PS 02
- Byte 7: Stop all implement operations transition number (A.25.4) / Byte 8 bits 2,1: All implement stop operations switch state (A.25.3) / 나머지 Reserved

### B.31 Drive strategy status — PGN 64717 (0x00FCCD)

트랙터가 임플리먼트에 현재 drive strategy 우선순위 구조(파워트레인 기능들의 우선순위)를 알리는 메시지다. 500 ms, 8 bytes, priority 6, PF 252/PS 205.

| 위치 | 내용 |
|---|---|
| Byte 1~4 | Drive strategy priority 1~4 (A.32.1~A.32.4) |
| Byte 7 bits 8,7 | Drive strategy request state (A.32.5) |
| Byte 8 bits 6~1 | Drive strategy exit/reason code (A.32.6) |
| 나머지 | Reserved |

### B.32 Drive strategy command — PGN 64718 (0x00FCCE)

임플리먼트가 트랙터에 파워트레인 drive strategy 우선순위 구조 변경을 요청하는 메시지다. 500 ms 주기 + PGN 내 데이터 변화 시 송신하되 <strong>100 ms보다 빠르게는 보내지 않는다</strong>. 8 bytes, priority 3, PF 252/PS 206.

| 위치 | 내용 |
|---|---|
| Byte 1~4 | Drive strategy priority 1~4 request (A.32.7~A.32.10) |
| Byte 8 bits 2,1 | Restore Operator drive strategy setting request (A.32.11) |
| 나머지 | Reserved |

### B.33 Heartbeat message

#### 배경과 목적

heartbeat 메시지는 <strong>ISO 25119(농기계 기능안전) 적합 시스템을 ISO 11783 프로토콜 위에 구현</strong>할 수 있도록 정의됐다. 시퀀스 번호 파라미터를 제공해 hardware category 2 시스템에서 medium 수준 진단 커버리지(DC medium) 요구를 다음 방식으로 충족한다.

- 통신 경로에 다른 컨트롤러가 개입하든 아니든, 데이터 소스에서 데이터 소비자까지 <strong>end-to-end 검증</strong>을 제공한다.
- 하나의 데이터 소스 CF가 보내는 단일 heartbeat 메시지를 <strong>여러 소비 CF가 공유</strong>해 통신을 검증할 수 있다.

#### B.33.1 구현 요구사항

hardware category 2 시스템에서 DC medium을 충족하려면 ISO 11783 CAN 프로토콜에 다음 제어 수단이 있어야 한다.

- a) safety critical path의 각 서브시스템은 안전 관련 기능에 필요한 메시지를 송신해, 수신 측이 watchdog 기능(메시지 반복 대비 타임아웃 감시)을 수행할 수 있게 한다.
- b) safety critical path의 각 서브시스템은 요청 시 시퀀스 번호를 담은 Heartbeat 메시지를 송신한다.
- c) safety critical path의 각 수신 시스템은 해당 데이터 소스의 Heartbeat 메시지를 검사해야 한다.
- d) Heartbeat 검사가 실패하면 수신 시스템은 <strong>안전 상태(safe state)로 진입</strong>해야 한다.
- e) Heartbeat 메시지의 샘플 레이트는 안전 관련 CAN 메시지의 샘플 레이트 이상이어야 한다.

CF가 송신하는 어떤 메시지든 safety critical path의 일부가 될 수 있으므로, <strong>네트워크의 모든 CF는 요청 시 heartbeat 메시지를 송신할 수 있어야 한다</strong>. safety critical path의 판별 방법은 AEF 가이드라인(ISO 25119와 ISOBUS 정렬)에 정의된다. CF가 송신하는 모든 메시지의 내용은 송신 전 내부적으로 검증돼야 하며, heartbeat는 그 위에 네트워크 통신을 추가로 보증하는 장치다 — heartbeat가 정해진 주기로 송신되고 시퀀스 번호가 유효 범위에서 증가하는 동안, 소스 CF가 정상 동작하며 모든 메시지에 올바른 데이터를 제공하고 있다는 의미가 된다.

#### B.33.2 Heartbeat message 정의 — PGN 61668 (0x00F0E4)

CF가 송신하는 메시지·파라미터 통신의 무결성 판단에 쓴다. 네트워크에 여러 인스턴스가 있을 수 있고, 요청을 받으면 각 CF는 적절한 시퀀스 번호로 이 메시지를 송신해야 한다.

- 100 ms, <strong>1 byte</strong>, priority 3, PF 240/PS 228
- Byte 1: Heartbeat sequence number (A.34)

#### B.33.3 Heartbeat message 처리

<strong>요청(B.33.3.1)</strong> — 대역폭 절약을 위해 CF는 기본적으로 heartbeat를 송신하지 않는다. 다른 CF의 정보를 critical path에 쓰는 CF(A)는 그 CF(B)에게 heartbeat를 요청해야 한다. 절차:

1. 소비 CF(A)가 heartbeat 메시지에 대해 <strong>100 ms 주기의 Request for Repetition rate</strong>(B.22.1)를 보낸다.
2. 제공 CF(B)가 heartbeat 송신을 시작하고, CF(A)는 검증을 시작한다.
3. CF(B)가 요청을 존중할 수 없으면 응답하지 않는다. <strong>250 ms</strong> 내 repetition rate 응답이 없으면 CF(A)는 요청 거절로 간주하고 위험도 평가(risk assessment)에 따라 적절히 대응한다.
4. 이미 어떤 CF가 heartbeat를 제공 중이면, 소비 CF는 그 CF에 중복 요청을 보내면 안 된다.

<strong>시퀀스 번호 규칙(B.33.3.2)</strong> — CF 초기화 시(전원 인가, 리셋, VT-status 메시지 송신 시작 등) 시퀀스 번호를 <strong>251</strong>로 1회 설정한다. 이후 송신 시마다 1씩 증가시키며 0~250을 순환한다(250 초과 시 0으로 리셋). 송신할 때마다 반드시 갱신한다.

<strong>시퀀스 번호 검증(B.33.3.3)</strong> — 소비 CF는 이전 시퀀스 번호를 저장해 두고 현재 heartbeat의 번호가 +1 증가했는지 비교한다. 이전 값이 250 또는 251(초기화)이면 현재 값은 0이어야 한다. 그 외에는 통신 오류로 판정한다.

- 값 254는 <strong>송신 측 오류 상태</strong>를 뜻한다. 수신자는 heartbeat 시스템을 오류 상태로 취급하고 위험도 평가에 따라 대응한다.
- 값 255는 not available이며, 송신 CF가 shutdown 상태로 <strong>네트워크에서 정상적으로(gracefully) 이탈</strong>할 때 써야 한다. 수신 CF는 운전자에게 알리고 안전 상태로 진입할 수 있다.

수신 측 평가 규칙:

| # | 조건 | 판정 |
|---|---|---|
| 1 | 현재·이전 메시지의 번호가 같고 255가 아님 | Heartbeat Sequence Error State |
| 2 | 현재 값이 252~253 | 메시지 무시 (예약 값) |
| 3 | 현재 값이 254 | Heartbeat Transmission Error State |
| 4 | 현재 값이 251 | 송신 CF 리셋으로 인식하고 자신의 번호를 송신 값에 동기화 |
| 5 | 현재 값이 255이고 이전 값이 255가 아님 | Heartbeat Graceful Shutdown Initialization State |
| 6 | (250 roll-over 고려 시) 증가폭이 3 초과 | Heartbeat Sequence Error State — 즉 최대 3개까지의 heartbeat 유실은 허용된다 |
| 7 | Sequence Error State 진입 후 | <strong>연속 8개</strong>의 올바른 순차 heartbeat를 수신해야 Operational State로 복귀 |

<strong>타이밍 검증(B.33.3.4)</strong> — 소비 CF는 heartbeat의 주기도 검증해야 하며, 반복 주기가 <strong>300 ms를 초과하면</strong> 통신 오류로 판정한다.

<strong>오류 시 대응(B.33.3.5)</strong> — 통신 오류가 감지되면 CF는 위험도 평가에 따라 적절히 대응해야 한다. 안전 상태 진입과 운전자 통지가 대표적인 대응이다.

## Annex C (informative) — Tractor control messages 예시

:::warning 3판에서의 위상
3판부터 Tractor Remote Control 메시지(B.24.1/B.24.2)가 deprecated 되어, 해당 메시지 정의가 없는 시스템에는 이 Annex가 더 이상 적용되지 않는다. 아래는 레거시 시스템 이해용 참고다.
:::

### C.1 초기화·오류 복구·배경

임플리먼트/task controller와 트랙터(TECU 경유) 사이에 제어 루프를 구성할 때의 권장 절차다. 적합성 요건은 아니지만, TECU 구현자들이 실제로 적용해 온 방식이라 성공 확률이 높다.

핵심 원리:

- <strong>현재값 일치 후 수락</strong> — 트랙터가 원격 명령을 수락하게 하려면, 임플리먼트 컨트롤러가 먼저 자신의 명령 값을 트랙터가 현재 송신 중인 값에 일치시켜야 한다. 그러면 트랙터가 limit status를 바꾸고 변경 명령을 받아들이기 시작한다. 이렇게 하면 임플리먼트가 운전자 조작 상황을 최신으로 반영한 상태에서 매끄럽게 요청 값으로 전환할 수 있다.
- <strong>운전자 개입 시</strong> — 운전자가 임플리먼트 요청 진행을 막는 조작(예: 히치를 수동으로 올려 auxiliary depth control 요청을 무효화)을 하면, 트랙터는 요청이 수락되지 않았고 상태가 operator limited/controlled임을 알린다. 임플리먼트는 리밋을 받아들이고 해제를 기다리거나, 운전자 인터페이스를 통해 리밋 해제를 요청할 수 있다.
- <strong>통신 실패 시</strong> — 트랙터는 operator limited/controlled로 전환하거나 non-recoverable error를 신호해야 한다. 어느 쪽인지는 복구에 필요한 조치에 달렸다. 원격 모드 복귀 전 트랙터 네트워크에서 운전자 개입이 필요하면 non-recoverable fault를 보고해야 한다. 필요한 운전자 개입의 내용은 트랙터 설계자 재량이다.
- <strong>재개</strong> — 트랙터가 operator limited/controlled로 복귀하면 임플리먼트는 현재 트랙터 설정에 값을 일치시켜 외부 명령을 재개해야 한다.
- <strong>초기 값 획득</strong> — 트랙터는 임플리먼트 버스의 명령에 대한 응답으로만 현재 명령 값을 보내므로, 임플리먼트는 시동 후 "Not Requested"(ALL ONES) 명령을 보내 현재 트랙터 명령을 얻어야 한다. 트랙터는 이 명령에 동작하지 않고 현재 값으로 응답한다.
- <strong>미지원 명령</strong> — 특정 명령을 트랙터가 지원하지 않으면 해당 limit status에 "Not Available"로 응답한다. 임플리먼트 요청에 미지원 명령이 하나라도 섞여 있으면 트랙터는 그 요청의 <strong>모든</strong> 원격 명령 값을 수락하지 않는다.
- limit high/low 제어 모드는 물리적·운전자 설정 리밋(예: 히치 상한)에 도달했을 때 트랙터가 보낸다. 임플리먼트는 이동이 제한됐고 그 방향의 추가 세트포인트 변경이 무시됨을 알 수 있다. 세트포인트 변화율 제한(ramp) 때문에 일시적일 수 있고, ramp가 목표에 도달하면 "Not limited"로 돌아온다.

### C.2 Cruise control 예시

차량 속도 단일 제어 모드다. mode command number 1과 value number 1만 쓰고 2번 계열은 모두 "Not Requested"(ALL ONES)로 채운다. 메시지 교환 시나리오(PGN 65035 명령 / 65034 응답):

| 단계 | 방향 | 핵심 내용 |
|---|---|---|
| 1 | 임플리먼트→트랙터 | mode #1=00001(cruise control), value #1=0xFFFF(Not Requested)로 현재 명령 값 요청 |
| 2 | 트랙터→임플리먼트 | 원격 모드 진입 없이 응답. limit status #1=001(Operator Limited/Controlled), value #1=600(현재 속도 0,6 m/s) |
| 3 | 임플리먼트→트랙터 | value #1=600 — 현재 속도에 일치시킨 세트포인트 요청 |
| 4 | 트랙터→임플리먼트 | 수락 응답. limit status #1=000(Not Limited), value #1=600 |
| 5 | 임플리먼트→트랙터 | value #1=500 — 0,5 m/s로 감속 요청 |
| 6 | 트랙터→임플리먼트 | 수락. limit status #1=000(remote mode), value #1=500 |

### C.3 Combined constant PTO speed + cruise control 예시

PTO 정속과 차량 속도를 <strong>한 메시지에 두 명령</strong>으로 함께 제어하는 모드다. mode command #1=01010(Combined PTO & cruise)에 value #1이 PTO 절, value #2가 cruise 절을 가리킨다. 예시는 운전자가 최대 속도 5 km/h를 설정해 둔 상태에서 임플리먼트가 이를 초과(2 m/s=7,2 km/h)하려는 상황이다.

- 임플리먼트 요청: value #1=4320(540 r/min), value #2=2000(2 m/s)
- 트랙터 응답: value #1=4320 수락(limit status #1=000 Not Limited), value #2=<strong>1389(1,389 m/s=5 km/h)로 클램프</strong>, limit status #2=010(Limited High)

### C.4 Auxiliary valve slip control + cruise control 예시

auxiliary valve 유량 가변으로 슬립을 제어하면서 속도도 함께 제어하는 다중 제어 모드다. mode #1=00111(Valve slip control), mode #2=00001(Cruise control). value #1은 복합 필드다 — bits 16~9: 유량 값(예: 25=10 % flow), bits 8~5: 밸브 상태(0001=Extend), bits 4~1: 밸브 번호(0010=Valve 2). value #2=1389(1,389 m/s). 두 명령 간 우선순위는 없으며, 파라미터 세트가 유지되는 한 #1/#2를 뒤바꿔도 된다.

## Annex D (informative) — 임플리먼트에 의한 트랙터 기능 제어 구현 지침

임플리먼트 명령·원격 제어 메시지의 취지는 제어권을 운전자에게서 임플리먼트로 넘기는 것이 아니라, <strong>트랙터가 자신의 전체 제어 체계 안에 임플리먼트 컨트롤러의 능력을 편입</strong>할 수단을 주는 것이다.

- 이 파라미터들을 임플리먼트 컨트롤러의 고속 제어 루프에서 조정하는 것은 권장되지 않는다. 세트포인트 변경에 대한 응답 시간은 CAN 버스 지연, 트랙터 내부 필터링·지연 등 여러 변수에 좌우되며 시스템마다 다르다.
- <strong>operating envelope</strong> — 임플리먼트의 히치 위치 명령은 "요청"일 뿐이며, 트랙터는 운전자가 설정한 리밋·조작과 조율한 뒤 수행한다. 운전자 컨트롤과 설정이 임플리먼트가 변경할 수 있는 "운용 범위(envelope)"를 정의한다. 히치가 좋은 예다: 위치·상한·하한 운전자 설정에 더해 대부분 시스템에는 현재 draft에 따라 히치 위치/하한을 연속 조정하는 "draft-mix" 설정이 있고, 이들이 모두 임플리먼트의 히치 위치 명령을 제한한다.
- <strong>persistent command</strong> — 히치 명령처럼, 리밋 조건이 해소되면 목표 위치를 향해 계속 움직이는 명령. 예: 운전자가 draft-mix를 조정해 이동 범위를 넓히면 진행이 재개된다.
- <strong>transient command</strong> — PTO engagement처럼 일시적 성격의 명령. 즉시 충족될 수 없으면 트랙터가 무시한다. 예: 캡 내 컨트롤로 PTO가 비활성화돼 있으면 engage 명령은 무시되고, 이후 캡 컨트롤이 허용으로 바뀌어도 임플리먼트가 <strong>새 "engage" 명령을 보내기 전까지</strong> PTO는 걸리지 않는다.
- <strong>persistent command 초기화</strong> — rear hitch 같은 기능의 외부 제어를 시작하려면, 임플리먼트 컨트롤러는 먼저 rear hitch status PGN의 히치 위치 파라미터와 <strong>같은 값</strong>을 담은 hitch and PTO command PGN을 보내야 한다. 트랙터가 수락하면 rear hitch position limit status에 "Not Limited"(000)로 응답한다.
- 제어를 요청하지 않거나 기능 제어를 반납할 때는 명령에 "Not Requested"(ALL ONES)를 보내야 한다.
- <strong>transient command 초기화</strong>도 유사하다. 임플리먼트가 현재 트랙터 파라미터 값을 명령 PGN으로 보내고, 트랙터가 해당 request status에 "External Request Accepted"로 응답하면 이후 명령이 수락·수행된다. 운전자 조작이나 외부 명령을 막는 조건이 생기면 트랙터는 해당 request status에 "Driver control" 또는 "Error"를 보고해야 한다.

## Bibliography (Part 7)

- ISO 11898-1:2003 — CAN data link layer/physical signalling
- SAE J1939 — Recommended Practice for a Serial Control and Communications Vehicle Network
- AEF guideline for the alignment of ISOBUS systems with ISO 25119 (heartbeat의 safety critical path 판별 근거 문서)

## Amendment 1 (2018) 주요 변경 사항

ISO 11783-7:2015/Amd.1:2018 (2018-06)은 3판 본문을 수정·확장한다. 핵심 주제는 세 가지다: <strong>히치 roll/pitch/yaw 제어의 추가</strong>, <strong>auxiliary/general-purpose valve의 고분해능 유량 파라미터</strong>, <strong>운전자 재석(operator presence) 상태 메시지</strong>. 그 밖에 언어 명령에 country code가 추가되고 조명·언어 메시지 규정이 정비됐다.

### 1) 기존 조항 자구 수정

- Clause 2: 인용 표준에 <strong>ISO 3166-1</strong>(country codes) 추가 — 아래 Language command 확장의 근거.
- A.5/A.6 (ground-based speed/distance): 정의를 "휠 슬립에 영향받지 않는 센서(radar, GPS, <strong>LIDAR</strong>, stationary object tracking 등)로 측정한 실제 대지 속도/거리"로 교체 — 허용 센서 예시가 넓어졌다.
- A.19.7/A.19.8 (front/rear draft): "양수 값은 트랙터의 전진 방향에 반대로 작용하는 힘"으로 문구를 교체하고, forward/reverse는 섀시의 정상 주행 방향 기준이며 운전석 반전과 무관하다는 NOTE를 추가. A.19.9(front nominal lower link force)에도 동일한 취지의 문구 교체.

### 2) A.19 확장 — 히치 roll/pitch/yaw 파라미터 (A.19.15~A.19.50 신설)

전·후방 3점 히치의 자세(roll·pitch·yaw)를 측정·명령하는 파라미터 세트가 대거 추가됐다. 구조는 front/rear 대칭이며, 축마다 angle(측정) + limit status + exit/reason code + sensitivity(측정/명령) + angle command로 구성된다.

<strong>공통 데이터 형식</strong>:

- roll/pitch angle 및 command: 2 bytes, 0,002 °/bit, −64° offset, 범위 −64°~64,51°
- yaw angle 및 command: 2 bytes, 1/128 °/bit, −200° offset, 범위 −200°~200°
- sensitivity 및 command: 1 byte, 0,4 %/bit, 0~100 % — 제어 루프 게인의 백분율. 0 %는 최소 게인(0 부근이면 루프가 반응하지 않을 수 있음), 100 %는 최대 게인
- limit status: 3 bits, 본문 A.26.7과 동일한 값 체계(000=Not limited ~ 111=Not available)
- exit/reason code: 6 bits, 본문 A.19.13 계열과 유사하되 <strong>010101="Hitch locked out"</strong> 항목이 있는 값 체계

<strong>각도 부호 규약</strong>: roll은 트랙터 후축과의 수평 정렬 기준으로, 주행 방향을 바라볼 때 반시계 회전이 음수·시계 회전이 양수다. pitch는 상·하부 부착점의 수직 정렬 기준으로, 트랙터 좌측에서 볼 때 반시계 방향이 양수다. yaw는 히치 z축 기준 각도로, 위에서 볼 때 반시계 회전이 양수다.

<strong>SPN 목록</strong>:

| 파라미터 | Front SPN | Rear SPN |
|---|---|---|
| Hitch roll angle | 7790 | 7802 |
| Hitch roll limit status | 7791 | 7803 |
| Hitch roll exit/reason code | 7792 | 7804 |
| Hitch roll sensitivity | 7800 | 7812 |
| Hitch roll command | 7796 | 7808 |
| Hitch roll sensitivity command | 7797 | 7809 |
| Hitch pitch angle | 7793 | 7805 |
| Hitch pitch limit status | 7794 | 7806 |
| Hitch pitch exit/reason code | 7795 | 7807 |
| Hitch pitch sensitivity | 7801 | 7813 |
| Hitch pitch command | 7798 | 7810 |
| Hitch pitch sensitivity command | 7799 | 7811 |
| Hitch yaw angle | 9714 | 9720 |
| Hitch yaw angle reference frame | 9721 | 9721 |
| Hitch yaw angle actual control mode | 9716 | 9722 |
| Hitch yaw limit status | 9717 | 9723 |
| Hitch yaw exit/reason code | 9718 | 9724 |
| Hitch yaw command | 9719 | 9725 |

<strong>Yaw angle reference frame</strong> (4 bits): 0000=Main body of the machine, 0001=Body of the hitch, 0010=Direction of travel, 1110=Non-recoverable fault, 1111=Not available. 전륜 조향 트랙터에는 machine main body 기준이 권장되고, crab steering 가능 트랙터에는 direction of travel, 굴절식(articulated) 트랙터의 전방 히치에는 body of the hitch 기준이 적합하다.

<strong>Yaw angle actual control mode</strong> (4 bits): 트랙터에서 활성인 제어 모드를 나타낸다 — 0000=Disabled(운송 등으로 yaw 고정), 0001=직접 유압 밸브 제어(수동), 0010=Floating mode, 0011=자동 1:1(인접 조향 휠 추종), 0100=자동 N:1(basic curvature contour mode), 0101=자동 position control, 1110=Error, 1111=Not available. <strong>yaw command(A.19.32/A.19.50)가 유효하려면 actual control mode가 0101(position control)이어야 한다.</strong>

### 3) A.21 확장 — 고분해능 밸브 유량 파라미터 (A.21.51~A.21.60 신설)

기존 1-byte(0,4 %/bit) 유량 파라미터의 분해능 한계를 보완하는 2-byte 파라미터들이 추가됐다.

| 절 | 파라미터 | 형식 | SPN |
|---|---|---|---|
| A.21.51 | Aux valve 0 high resolution estimated flow | 2 bytes, 0,004 %/bit, −125 % offset, 범위 −125~+132,02 % (운용 −100~+100 %), Estimated | 9732 |
| A.21.52 | Aux valve 0 Resolution mode — Command | 2 bits, Status | 7872 |
| A.21.53 | Aux valve 0 port flow — Extended Resolution Command | 2 bytes, 0,001 562 5 %/bit, 0~100 %, Command | 7856 |
| A.21.54 | Aux valve 15 high resolution estimated flow | A.21.51과 동일 형식 | 9747 |
| A.21.55 | Aux valve 15 Resolution mode — Command | 2 bits, Status | 7887 |
| A.21.56 | Aux valve 15 port flow — Extended Resolution Command | A.21.53과 동일 형식 | 7871 |
| A.21.57 | GP valve extend port high resolution estimated flow | A.21.51과 동일 형식 | 9728 |
| A.21.58 | GP valve retract port high resolution estimated flow | A.21.51과 동일 형식 | 9729 |
| A.21.59 | GP valve port flow — Extended Resolution Command | A.21.53과 동일 형식 | 9727 |
| A.21.60 | General-purpose valve exit/reason code | 5 bits, Measured (10001="Valve locked out" 포함) | 9730 |

해석 규칙:

- estimated flow에서 0 %=무유량, +100 %=extend port 최대 유량, −100 %=retract port 최대 유량. <strong>estimated(측정 아님)이므로 피드백 제어에 쓸 때 주의</strong>가 필요하다. "not available"(all 1's)이면 기존 저분해능 파라미터만 유효하다.
- Resolution mode command: 00=표준 분해능 파라미터만 유효, 01=확장·표준 둘 다 유효, 11=Don't care.
- Extended Resolution Command가 "not available"이 아니면 유효 값을 담고 있으며, 이때 <strong>저분해능 파라미터에도 항상 (더 낮은 분해능의) 유효 값을 함께 실어야 한다</strong> — 구형 수신기와의 호환 유지 장치다.

### 4) A.23.1 교체 — Language code + Country code

언어가 "Language code + 선택적 Country code"로 재정의됐다. country code는 방언(dialect) 구분에 쓴다(예: es-MX, es-AR).

- <strong>A.23.1.1 Language code</strong> (SPN 2410): 2 bytes, ISO 639 두 글자 소문자 코드(nl, fr, en, de 등). Command.
- <strong>A.23.1.2 Country code</strong> (SPN 9731, 신설): 2 bytes, ISO 3166-1 alpha-2 대문자 코드(NL, FR, GB, US, DE 등). 두 문자 모두 all 1's면 country code 미지정. Command.

### 5) A.28.10 신설 — Guidance system remote engage switch status

Remote Engage Switch의 상태다. 차량이 guidance 시스템용 engage 스위치를 자체 제공할 수 있게 한다. 2 bits, Measured, SPN 9726. 00=Disengage guidance commands, 01=Engage guidance commands, 10=Error indication, 11=Not available/Take no Action.

### 6) A.35 신설 — Operator presence parameters

운전자 재석·주의(awareness) 상태를 네트워크로 방송하기 위한 파라미터 그룹이다.

<strong>A.35.1 Operator status sequence counter</strong> (8 bits, SPN 5141) — operator status PGN 송신 횟수 카운터다(경과 시간 정보 아님). 동작·검증 규칙은 B.33 heartbeat 시퀀스 번호와 같은 골격이다: 초기화 시 251(0xFB), 이후 0~250 순환(modulus 250), 값이 갱신된 operator status PGN 송신마다 +1, 송신자별 독립. 252~253 예약(수신 무시), 254 오류, 255 not available(메시지 내 다른 SPN도 모두 not available임을 의미). 수신자는 첫 수신 값을 초기값으로 삼고, 동일 값 반복(255 제외)·254 수신·roll-over 고려 증가폭 3 초과 시 error state로 판정한다. 최대 3개 유실 허용, error state에서 <strong>연속 8개</strong> 정상 수신 시 operational state 복귀, 251 수신 시 송신자 리셋으로 인식하고 동기화 — heartbeat와 동일한 규칙 세트다. 수신자는 이 카운터로 송신자가 유효한 네트워크 연결을 유지 중인지, 해당 SA에서 이 메시지를 보내는 CF가 유일한지 판단한다.

<strong>A.35.2 Operator presence state</strong> (2 bits, SPN 9711) — 운전자 재석 감지 시스템의 현재 상태. 00=Operator Not Present, 01=Operator Present, 10=Error, 11=Not available/Not Installed.

<strong>A.35.3 Operator awareness state</strong> (2 bits, SPN 9712) — 운전자가 기계를 안전하게 조작할 필요 작업을 수행할 수 있는 상태(alert & engaged)인지. 00=Operator Not Aware, 01=Operator Aware, 10=Error, 11=Not available/Not Installed.

<strong>A.35.4 Operator presence and awareness status checksum</strong> (8 bits, SPN 9713) — operator status 메시지 앞 56 데이터 비트에 대한 <strong>CRC-8-CCITT</strong>(0x07/0xE0/0x83) 체크섬. CAN 송신 전 데이터 손상 검증용이다. 체크섬 실패 메시지는 시퀀스 오류로 취급하며, 수신 장치는 presence/awareness 상태를 값 2("error indicator") 수신처럼 처리한다. 체크섬 실패로 error state에 들어간 경우도 연속 8개 정상 메시지 수신 후 복귀한다.

### 7) Annex B 확장 — 히치 자세 메시지 6종 신설

B.6(front hitch status) 뒤에 B.6.2~B.6.6, B.7(rear hitch status) 뒤에 B.7.2~B.7.6이 추가됐다. 모두 100 ms 주기, 8 bytes다(sensitivity 메시지만 변화 시 100 ms + 무변화 시 1 s 주기, priority 6; 나머지는 priority 3).

| 메시지 | PGN | 주요 내용 |
|---|---|---|
| B.6.2 Secondary or front hitch roll and pitch | 61695 (0x00F0FF) | Bytes 1,2 roll angle · Byte 3 roll limit status · Byte 4 roll exit/reason · Bytes 5,6 pitch angle · Byte 7 pitch limit status · Byte 8 pitch exit/reason |
| B.6.3 Front hitch roll and pitch sensitivity | 64527 (0x00FC0F) | Byte 1 roll sensitivity, Byte 2 pitch sensitivity |
| B.6.4 Front hitch roll and pitch command | 61696 (0x00F100) | Bytes 1,2 roll command · Byte 3 roll sensitivity command · Bytes 4,5 pitch command · Byte 6 pitch sensitivity command |
| B.6.5 Secondary or front hitch yaw | 64387 (0x00FB83) | Bytes 1,2 yaw angle · Byte 3 reference frame + actual control mode · Byte 4 yaw limit status · Byte 5 yaw exit/reason |
| B.6.6 Front hitch yaw command | 61758 (0x00F13E) | Bytes 1,2 yaw command |
| B.7.2 Primary or rear hitch roll and pitch | 61697 (0x00F101) | B.6.2와 대칭 (rear 파라미터) |
| B.7.3 Rear hitch roll and pitch sensitivity | 64526 (0x00FC0E) | B.6.3과 대칭 |
| B.7.4 Rear hitch roll and pitch command | 61698 (0x00F102) | B.6.4와 대칭 |
| B.7.5 Primary or rear hitch yaw | 64386 (0x00FB82) | B.6.5와 대칭 |
| B.7.6 Rear hitch yaw command | 61759 (0x00F13F) | B.6.6과 대칭 |

### 8) 기존 Annex B 메시지의 바이트 배치 변경

reserved였던 바이트들이 고분해능 파라미터로 채워졌다.

- <strong>B.11</strong> (aux valve 0 estimated flow): Bytes 7,8 → Aux valve 0 high resolution estimated flow (A.21.51)
- <strong>B.13</strong> (aux valve 0 command): Byte 2 bits 2,1 → Resolution mode command (A.21.52), Bytes 4,5 → Extended Resolution port flow command (A.21.53)
- <strong>B.15</strong> (aux valve 15 estimated flow): Bytes 7,8 → A.21.54
- <strong>B.17</strong> (aux valve 15 command): Byte 2 bits 2,1 → A.21.55, Bytes 4,5 → A.21.56
- <strong>B.25.2</strong> (GP valve estimated flow): Bytes 5,6 → extend port high res (A.21.57), Bytes 7,8 → retract port high res (A.21.58)
- <strong>B.25.4</strong> (GP valve command): Bytes 4,5 → Extended Resolution Command (A.21.59)
- <strong>B.26.2</strong> (Guidance machine status): Byte 5 bits 8,7 → Remote Engage Switch Status (A.28.10) — 기존 reserved 자리
- <strong>B.21</strong> (Language command): Bytes 1,2 → Language code (A.23.1.1), <strong>Bytes 7,8(기존 reserved) → Country code</strong>

### 9) B.18 Lighting command 규정 변경

3번째 문단이 교체되고 새 문단이 추가됐다. 핵심 변화:

- 교체된 문단에서 "지역 법규 조합 구성은 트랙터 설계자 책임" 문구와 초당 10 메시지 상한 문구가 빠지고, 점멸은 ON/OFF 교대 송신으로 "전달(communicated)"된다는 표현으로 정리됐다. 최소 1초 1회 송신 요구는 유지된다.
- 신설 문단: <strong>임플리먼트의 형식승인(homologated) 조명 제어는 7핀 조명 커넥터로 수행해야 하며, 임플리먼트 버스의 Lighting Command 메시지에 의존해서는 안 된다.</strong> Lighting Command 메시지는 비형식승인 조명 제어와 진단 용도로 쓸 수 있다.

### 10) B.21 Language command 요청 방식 명확화

네트워크에 Language command 소스가 <strong>여러 개</strong> 있을 수 있으므로, destination-global 요청은 서로 다른 설정의 응답을 여럿 받을 수 있다. 따라서 CF는 <strong>자신이 서비스를 이용 중인 CF에게 destination-specific 요청</strong>을 보내는 것이 권장된다. 예: Working Set이 네트워크에서 VT를 여러 대 발견하면, 자신의 UI를 게시 중인 VT의 SA에서 온 Language command 데이터를 써야 한다.

### 11) B.33.3.6 신설 — Operator status 메시지 — PGN 64388 (0x00FB84)

heartbeat 절(B.33.3.5) 뒤에 추가된 운전자 상태 방송 메시지다.

- operator presence: 운전자가 기계 조작에 올바르고 적절한 위치에 있는 상태. operator awareness: 운전자가 안전 조작에 필요한 작업을 수행할 수 있는 현재 능력(alert & engaged).
- 송신: 1 000 ms 주기 + Presence/Awareness 상태 변화 시, 단 <strong>200 ms보다 빠르게는 송신하지 않는다</strong>. 8 bytes, priority 3, PF 251/PS 132.

| 위치 | 내용 |
|---|---|
| Byte 1 | Operator Status Sequence Counter (A.35.1) |
| Byte 2 bits 8~5 | Reserved (1로 채워 송신) |
| Byte 2 bits 4,3 | Operator Awareness State (A.35.3) |
| Byte 2 bits 2,1 | Operator Presence State (A.35.2) |
| Bytes 3~7 | Reserved |
| Byte 8 | Operator Presence and Awareness Status Checksum (A.35.4) |

### 12) Annex D 추가 — TIM 예고

Annex D 말미에 다음 취지의 문단이 추가됐다: AEF가 <strong>"Tractor-Implement Management"(TIM)</strong>라는 새 기능성을 정의 중이며, 이 문서의 트랙터 제어 관련 메시지·파라미터 일부를 결국 대체하거나 최소한 불필요하게 만들 것으로 예상된다. 영향(및 잠재적 deprecation) 가능성이 큰 메시지로 front/rear hitch roll·pitch command, Hitch and PTO commands, auxiliary valve 0/1~14/15 command, Tractor control mode command, Guidance system command, Machine selected speed command, Drive strategy command가 열거됐다. 즉 <strong>명령(command) 계열 메시지 전반이 TIM으로 이관될 방향</strong>임을 표준 스스로 예고한 것이다.
