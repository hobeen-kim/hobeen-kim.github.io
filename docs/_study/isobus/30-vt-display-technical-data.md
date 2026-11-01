---
title: "VT 화면 구성과 기술 데이터"
description: "VT 화면의 Data Mask·Soft Key 영역 규칙과 오브젝트 풀·Working Set의 기본 규칙을 익히고, 작업기가 VT의 버전·메모리·화면 크기를 묻는 기술 데이터 메시지를 바이트로 읽는다."
date: 2026-04-13
tags: [ISOBUS, VT, Virtual Terminal, ISO-11783-6, Soft Key, 기술 데이터]
prev: /study/isobus/29-vt-basics
next: /study/isobus/31-vt-connection
---

# VT 화면 구성과 기술 데이터

::: info 학습 목표
- VT 화면이 Data Mask 영역과 Soft Key Mask 영역으로 나뉘는 이유와 크기 규칙을 설명할 수 있다.
- 물리·가상·내비게이션 Soft Key를 구분하고, 키가 많을 때 페이지가 어떻게 나뉘는지 계산할 수 있다.
- Object ID와 NULL 같은 오브젝트 풀 기본 규칙과, Working Set(WS) 안의 Master·Member 역할 분담을 설명할 수 있다.
- 기술 데이터 메시지로 VT의 버전, 메모리, 화면 크기, 글꼴을 묻고 응답 바이트를 읽을 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [29장 Virtual Terminal(VT) 기초](/study/isobus/29-vt-basics), [12장 주소와 NAME](/study/isobus/12-j1939-address-name)
- 이 장에서 처음 나오는 말
  - Soft Key designator: Soft Key 하나의 라벨을 그리는 화면 칸.
  - 물리·가상·내비게이션 Soft Key: VT가 늘 내주는 키 수, Soft Key Mask 하나에 담을 수 있는 키 수, 그중 페이지 넘김에 쓰는 키 수.
  - Object ID: 풀 안에서 오브젝트 하나를 가리키는 16비트 번호. `0xFFFF`는 "아무것도 가리키지 않음(NULL)"이다.
  - Working Set Master와 Member: 작업기를 대표해 VT를 상대하는 장치와, 같은 작업기를 이루는 나머지 장치.
  - 기술 데이터 메시지(technical data message): 작업기가 VT에게 버전, 메모리, 화면 크기, 글꼴 같은 능력을 묻는 질문과 그 답.
:::

남의 집 벽에 그림을 걸려면 먼저 벽 크기와 못 자리를 재야 한다. 작업기도 VT(Virtual Terminal, 트랙터 운전석의 공용 화면)에 자기 화면을 띄우기 전에 화면이 얼마나 큰지, 버튼은 몇 개인지, 어떤 글꼴을 그릴 수 있는지 VT에게 묻고 거기에 맞춘다. 이 장은 VT 화면의 구조와 오브젝트 풀의 기본 규칙을 보고, 작업기가 VT의 능력을 묻는 기술 데이터 메시지를 바이트로 읽는다.

## 1. 화면의 두 영역: Data Mask와 Soft Key Mask

[29장](/study/isobus/29-vt-basics)에서는 VT 화면이 Data Mask 영역과 Soft Key Mask 영역으로 나뉜다고만 했다. 이 절에서는 두 영역의 크기와 배치 규칙을 본다. 표준은 Soft Key가 물리 키보다 많을 때 VT가 페이지를 넘기는 규칙까지 정한다(2절). VT Server를 구현한다면 이 절과 다음 절이 화면 레이아웃 명세다.

![Soft Key가 세로로 붙은 VT와 가로로 붙은 VT. 두 VT 모두 Data Mask 영역은 정사각형이고, Soft Key designator 칸에는 키 번호가 붙는다. 세로 배치는 오른쪽 열 맨 위가 1번이고 아래로 1~6, 다음 열은 왼쪽에 7~12가 붙는다. 가로 배치는 윗줄 왼쪽이 1번이고 오른쪽으로 1~6, 아랫줄이 7~12다. 세로 배치 화면의 남는 부분은 VT 독자 정보 영역이다](/images/study-isobus/30-vt-screen-areas-light.png)
![Soft Key가 세로로 붙은 VT와 가로로 붙은 VT. 두 VT 모두 Data Mask 영역은 정사각형이고, Soft Key designator 칸에는 키 번호가 붙는다. 세로 배치는 오른쪽 열 맨 위가 1번이고 아래로 1~6, 다음 열은 왼쪽에 7~12가 붙는다. 가로 배치는 윗줄 왼쪽이 1번이고 오른쪽으로 1~6, 아랫줄이 7~12다. 세로 배치 화면의 남는 부분은 VT 독자 정보 영역이다](/images/study-isobus/30-vt-screen-areas-dark.png)

그림은 같은 규칙을 따르는 VT 두 대다. 왼쪽은 Soft Key가 화면 옆에 세로로, 오른쪽은 화면 아래에 가로로 붙어 있다. 칸 하나가 Soft Key 하나의 라벨 자리(designator)이고, 칸 안의 숫자는 키 번호다.

### Data Mask 영역: 왜 정사각형인가

- VT는 Data Mask와 Alarm Mask를 그릴 영역을 따로 예약해야 한다. Alarm Mask는 경고를 띄울 때 쓰는 화면 한 장이다([39장](/study/isobus/39-vt-alarm-activation)).
- 정사각형인 이유는 원문이 직접 밝힌다. 이 장에서 "원문"은 ISO 11783-6(VT를 정하는 표준 문서) 자체를 말한다. VT마다 화면 방향(가로·세로)이 다르므로 어느 방향에서도 같은 풀이 제대로 보이도록 정사각형을 골랐고, 이 종횡비(가로세로 비율)는 엄격히 강제된다.
- 최소 크기는 200 × 200, version 6 이상은 480 × 480이다. 그보다 크면 어떤 정사각형이든 된다(240, 320, 600, 800, 1024 …).
- 최소값은 "쓸 수 있는 Data Mask 영역"에 대한 것이지 물리 해상도를 제한하지 않는다. 남는 화면은 차량 데이터·VT 통계 같은 독자 정보에 쓰라고 권한다.
- WS는 Get Hardware response Byte 5~8(X-Pixels·Y-Pixels)로 실제 크기를 알고, 풀을 설계한 크기와 다르면 위치·크기·폰트를 스케일한다. 스케일(scale)은 비율에 맞춰 늘리거나 줄이는 일이고, 초기화 7단계([31장](/study/isobus/31-vt-connection))에서 한다. 스케일 규칙은 [32장](/study/isobus/32-vt-object-pool-basics)에서 간단히, [34장](/study/isobus/34-vt-layout-color)에서 자세히 다룬다.

VT 에뮬레이터는 PC에서 VT처럼 동작하는 시험용 프로그램이다. 이런 프로그램을 만들 때 다음을 틀리기 쉽다.

::: warning VT 에뮬레이터 구현 함정
Get Hardware response의 Y-Pixels는 "Data Mask가 정사각형이므로 항상 X와 같다". 개발 PC의 직사각형 창 크기를 그대로 X·Y로 보고하면 표준 위반이다. 창이 직사각형이면 짧은 변에 맞춘 정사각형을 Data Mask로 쓰고 나머지는 독자 영역으로 둔다.
:::

### Soft Key Mask 영역과 designator

- Soft Key 라벨 영역(Soft Key Mask area)은 Data Mask 영역과 따로 예약한다. 붙어 있어도, 떨어져 있어도 되지만 Data Mask 영역의 일부여서는 안 된다.
- 키마다 라벨을 그리는 칸이 <strong>Soft Key designator</strong>다. 화면 방향과 무관하게 최소 60 × 32 픽셀이고 version 6 이상은 60 × 60이다. 텍스트·그래픽·둘 다 넣을 수 있다.
- designator 사이에는 눈에 띄는 구분(예: 1픽셀 선)을 둬야 하고, 그 선은 designator 영역 <strong>밖</strong>에 그린다. 최소 크기를 지킬 수 없을 때만 경계 위에 그어도 된다.
- 실제 designator 크기는 Get Number of Soft Keys response Byte 5·6으로 보고된다(8절). Working Set object의 descriptor도 이 크기 안에 들어가야 하고 넘치는 부분은 잘린다. descriptor는 VT가 WS를 운전자에게 보여 줄 때 쓰는 작은 이름표다(5절).

::: tip 정리
- Data Mask는 어느 화면 방향에서도 같게 보이도록 정사각형이 강제된다. 최소 200 × 200, version 6은 480 × 480이다.
- Soft Key 라벨 칸(designator)은 최소 60 × 32, version 6은 60 × 60이고, Data Mask 영역 밖에 따로 둔다.
:::

<small>근거: ISO 11783-6 4.5.2, 4.5.3.1, 4.6.6.2, 4.6.8, D.5, D.9</small>

## 2. Soft Key 개수와 페이지 넘김

이 절에서는 Soft Key를 세는 세 가지 개수와, 작업기가 물리 키보다 많은 키를 보냈을 때 VT가 페이지를 나누는 규칙을 본다.

### 물리·가상·내비게이션 Soft Key

표준은 Soft Key를 세 가지 "개수"로 나눈다. 셋의 관계는 <strong>내비게이션 < 물리 ≤ 가상</strong>이다.

- <strong>물리 Soft Key</strong>: VT가 active WS에 상시 내주는 키의 개수다. active WS는 지금 화면에 보이면서 입력을 받는 WS다. 실제 버튼일 필요는 없고 터치스크린 위 버튼이어도 된다. version 4 이상은 최소 6개, version 3 이하는 개수 요구가 없다.
- <strong>가상 Soft Key</strong>: Soft Key Mask 하나에 담을 수 있는 키 수다. version 4 이상은 정확히 64, version 3 이하는 최대 64이면서 최소한 보고한 물리 키 수만큼은 지원한다.
- <strong>내비게이션 Soft Key</strong>: 물리 키 가운데 페이지 넘김에 쓰는 개수다. 물리 키 수보다 작아야 하고, 물리 키를 쓰지 않는 전용 넘김 수단이 있으면 0으로 보고한다.

물리 키 번호는 배치 방향으로 정해진다(1절 그림). 세로 배치는 키 1이 오른쪽 맨 위이고 아래로 늘어나며, 첫 열이 차면 다음 열은 <strong>왼쪽</strong>에 붙는다. 가로 배치는 키 1이 맨 윗줄 왼쪽이고 오른쪽으로 늘어나며, 줄이 차면 아래 줄로 내려간다. 터치스크린 매트릭스처럼 방향이 애매하면 세로 배치 규칙을 따른다.

### 페이지 넘김 계산

WS가 Soft Key Mask에 물리 키보다 많은 키를 넣으면 VT가 넘김 수단을 제공한다. 책장을 넘기듯 한 번에 보이는 키 묶음을 바꿔 가며 보여 주는 것이다. Soft Key Mask의 목록에는 키 대신 Object Pointer(다른 오브젝트를 가리키는 오브젝트)를 넣을 수도 있는데, 이 Pointer가 NULL을 가리키면 아래 5번 규칙이 적용된다.

1. 키 수 ≤ 물리 키 수이면 모든 키가 물리 키로 바로 닿아야 하고, VT는 넘김 수단을 두면 <strong>안 된다</strong>.
2. 키 수가 더 많으면 <strong>스크롤이 아니라 그룹 단위 페이지</strong>로 넘긴다. 한 그룹 = 물리 키 수 − 내비게이션 키 수다.
3. 내비게이션 키는 모든 페이지에서 같은 물리 위치에 있어야 한다. 특정 페이지에서 비활성화할 수는 있지만 없앨 수는 없다.
4. 마지막 페이지는 다 차지 않을 수 있고, 남는 designator는 쓰지 않는다.
5. NULL Object ID(`0xFFFF`)를 가리키는 Pointer는 자리를 예약해 빈칸을 만든다. 단 목록 끝에 몰린 NULL Pointer는 자리를 예약하지 않고 페이지 계산에서도 빠진다.

아래 그림은 원문에 실린 예와 같은 VT(물리 6, 가상 64, 내비게이션 1 → 그룹 5)에 13칸짜리 목록을 올린 경우다. 끝의 NULL 둘이 빠져 11칸이 남고, 5·5·1칸으로 세 페이지가 된다. 6번 물리 키는 모든 페이지에서 "다음 그룹" 키다.

![물리 Soft Key 6개·내비게이션 1개인 VT에서 13칸 Soft Key 목록이 끝의 NULL 두 칸을 빼고 5·5·1칸씩 세 페이지로 나뉘고, 6번 키가 모든 페이지에서 다음 그룹 키로 쓰이는 모습](/images/study-isobus/15-soft-key-paging-light.png)
![물리 Soft Key 6개·내비게이션 1개인 VT에서 13칸 Soft Key 목록이 끝의 NULL 두 칸을 빼고 5·5·1칸씩 세 페이지로 나뉘고, 6번 키가 모든 페이지에서 다음 그룹 키로 쓰이는 모습](/images/study-isobus/15-soft-key-paging-dark.png)

계산을 단계별로 따라가면 다음과 같다.

1. 목록 13칸에서 끝에 몰린 NULL 2칸을 뺀다. 11칸이 남는다.
2. 11칸은 물리 키 6개보다 많으므로 페이지로 나눈다.
3. 한 그룹은 6 − 1 = 5칸이다.
4. 11칸을 5칸씩 자르면 5, 5, 1칸이므로 3페이지다. 가운데 NULL 2칸(3번째, 9번째)은 빈칸으로 자리를 차지한다.

::: details 페이지 나누기를 코드로 검산하기
아래 코드는 위 규칙을 그대로 옮긴 함수로 그림의 예와 "끝 NULL을 빼면 한 페이지에 들어가는" 예를 확인한다.

```python
def soft_key_pages(keys, physical, navigation):
    """keys: Soft Key Mask 목록. None은 NULL Object ID를 가리키는 Pointer."""
    keys = list(keys)
    while keys and keys[-1] is None:       # 끝의 NULL은 자리를 예약하지 않는다
        keys.pop()
    if len(keys) <= physical:              # 다 들어가면 넘김 수단을 두지 않는다
        return [keys]
    group = physical - navigation
    return [keys[i:i + group] for i in range(0, len(keys), group)]


mask = ["K1", "K2", None, "K3", "K4", "K5", "K6", "K7", None, "K8", "K9", None, None]
assert soft_key_pages(mask, physical=6, navigation=1) == [
    ["K1", "K2", None, "K3", "K4"],
    ["K5", "K6", "K7", None, "K8"],
    ["K9"],
]
# 끝 NULL을 빼면 물리 키 수 이하 → 한 페이지, 넘김 키 없음
assert soft_key_pages(["K1", "K2", None, "K3", None, None, None], 6, 1) == [["K1", "K2", None, "K3"]]
print("페이지 계산 검증 통과")
```
가운데 NULL은 자리를 예약하므로 키 수에 넣었다. 실행하면 `페이지 계산 검증 통과`가 출력된다.
:::

Soft Key를 눌렀을 때 오가는 Soft Key Activation 메시지는 [36장](/study/isobus/36-vt-commands-basics)에서 다룬다.

::: tip 정리
- Data Mask는 정사각형이 강제되고(v6 최소 480), 실제 크기는 Get Hardware response Byte 5~8로 읽는다.
- designator 크기는 Get Number of Soft Keys response Byte 5·6, 가상·물리 키 수는 Byte 7·8, 넘김 키 수는 Byte 2다.
- 페이지는 "물리 − 내비게이션" 단위로 나뉜다. 끝 NULL은 계산에서 빠지고 가운데 NULL은 빈칸을 만든다.
:::

<small>근거: ISO 11783-6 4.5.3.2~4.5.3.5</small>

## 3. 오브젝트 풀 기본 규칙

이 절부터 6절까지는 풀을 다루는 기본 규칙, WS를 이루는 CF(Control Function, 제어 기능)들의 역할 분담, 비슷한 장비를 구분하는 법, 언어·단위 처리를 본다. CF는 네트워크에서 주소 하나를 갖고 기능 하나를 맡는 단위이고, ECU(전자 제어 장치) 하나에 CF가 여럿 있을 수도 있다. 오브젝트 하나하나의 정의는 [32장](/study/isobus/32-vt-object-pool-basics)과 [33장](/study/isobus/33-vt-object-records)이 다룬다.

### 오브젝트 풀 규칙

- 풀은 한 WS의 운전자 인터페이스 정의 전체를 이루는 오브젝트 집합이고, 초기화 때 오브젝트 풀 전송 절차([32장](/study/isobus/32-vt-object-pool-basics))로 VT에 올라간다.
- Object ID는 <strong>한 WS의 풀 안에서만</strong> 유일하면 된다. 서로 다른 WS의 풀은 같은 ID를 써도 되므로, VT 쪽 저장 구조는 WS마다 ID 공간을 따로 둬야 한다.
- `0xFFFF`(65535)는 NULL Object ID다. 그리기 문맥에서 NULL은 "그 자리에 아무것도 그리지 않는다"는 뜻이다.
- 오브젝트는 마스크에서 활성화되기 <strong>전에</strong> 완전히 기술돼 있어야 한다. 풀이 하나도 없을 때 VT가 무엇을 보여 줄지는 VT 독자 사항이다.
- VT는 버전 라벨이 다르면 같은 WS의 풀 여러 개를 비휘발성 메모리(전원이 꺼져도 내용이 남는 저장소)에 둘 수 있다. 원문 예는 "언어만 다른 풀들"이다([31장](/study/isobus/31-vt-connection)).

Object ID가 풀 안에서만 유일하다는 것은 아파트 동마다 호수를 따로 매기는 것과 같다. A동 101호와 B동 101호는 다른 집이다. 그래서 VT는 Object ID만이 아니라 "어느 WS의 101번인가"를 함께 기억해야 한다.

### 처리 순서와 계층 깊이 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

부모가 나열한 순서대로 depth-first로 처리한다. depth-first(깊이 우선)는 한 가지를 끝까지 내려간 뒤 돌아오는 순서다. 자식이 또 자식을 가지면 그 가지를 끝까지 처리한 뒤 부모로 돌아온다.

version 5 이상 VT는 계층 깊이를 최소 30까지 지원해야 하고, version 4 이하는 규정이 없다. 깊이는 Data Mask·Alarm Mask·Window Mask·Soft Key Mask·Key Group에서 시작해 자식으로 한 단계 내려갈 때마다 1씩 는다. Object Pointer가 가리키는 대상은 자식으로 세고, 속성 칸에 ID만 적힌 "참조"는 세지 않는다(원문 예: Working Set object가 속성으로 갖는 Data Mask).

아래 예에서 Container는 오브젝트 여러 개를 묶는 상자, Output Number는 숫자를 보여 주는 오브젝트, Font Attributes는 글꼴 속성을 담은 오브젝트다.

```text
Data Mask 1000                  시작
└─ Container 2000               +1
   └─ Object Pointer 2100       +2
      └─ Output Number 3000     +3  ← Pointer의 대상도 자식으로 센다
         (Font Attributes 4000)     세지 않음: 속성 칸에 ID로 적힌 참조
```

Font Attributes는 원문 예와 같은 속성 참조로 보아 세지 않았다. 마스크 자신을 0으로 셀지 1로 셀지는 원문이 숫자로 못 박지 않았으므로, WS는 30단계에 여유를 두고 설계하는 편이 안전하다(추론).

::: tip 정리
- Object ID는 WS의 풀 안에서만 유일하다. NULL은 `0xFFFF`이고, v5 이상 VT는 깊이 30 이상을 처리한다.
:::

<small>근거: ISO 11783-6 4.6.1</small>

## 4. Working Set의 역할 분담과 응답 목적지

이 절에서는 여러 CF가 한 작업기를 이룰 때 누가 VT를 상대하는지, VT의 응답이 누구에게 가는지 본다.

여러 CF가 한 작업기를 이루면 그 묶음이 Working Set이다(Working Set Master 메시지 PGN 65037(0xFE0D)은 [26장](/study/isobus/26-isobus-network-mgmt)). PGN(Parameter Group Number)은 메시지의 종류를 가리키는 번호다. 회사로 치면 Master는 대표 창구이고 Member는 같은 회사의 다른 직원이다.

- WS마다 CF 하나가 Working Set Master다. Master는 VT 사용권을 확보하고, 초기 풀을 제공하고, 멤버들의 NAME을 Working Set Master/Member 메시지로 VT에 알린다. NAME은 장치를 식별하는 64비트 이름이다([12장](/study/isobus/12-j1939-address-name)).
- Member가 Master 전용 명령을 보내거나, WS 멤버로 식별되지 않은 CF가 WS 전용 명령을 보내면 VT는 Acknowledgement(NACK)로 답한다. NACK는 "처리하지 않겠다"는 부정 응답이다([10장](/study/isobus/10-j1939-request-ack)).
- 풀이 로드된 뒤에는 어느 멤버든 데이터를 주고 속성을 바꿀 수 있다. 다만 운전자가 입력 필드에 넣은 값은 <strong>항상 Master</strong>에게 간다.
- VT는 멤버를 가질 수 없고 Working Set Master/Member 메시지를 보내서도 안 된다.

### 응답은 누구에게 가나

VT 응답의 목적지는 WS 버전(Working Set Maintenance)과 VT 버전(Get Memory response)의 조합으로 정해진다. 이 규칙이 ISO 11783-1(ISOBUS 전체의 공통 요구를 정하는 문서)의 "응답은 WS Master에게만" 규정보다 우선한다.

| WS 버전 | VT 버전 | 명령 응답의 목적지 |
|---|---|---|
| 3 이하 | 무관 | WS Master |
| 4 이상 | 3 이하 | WS Master |
| 4 이상 | 4 이상 | 명령을 보낸 CF(originator) |

앞의 두 조합에서는 Member가 자기 명령의 응답을 찾으려고 VT가 Master에게 보내는 destination-specific 메시지를 모두 엿들어야 하고, Master는 짝을 모르는 응답을 받는다. destination-specific 메시지는 목적지 주소를 하나로 정해 보내는 1:1 메시지다. 마지막 조합에서야 TP(8바이트보다 긴 데이터를 여러 프레임으로 나눠 보내는 규칙, [15장](/study/isobus/15-tp-bam-cmdt))로 오는 응답(예: Get Supported WideChars response)을 Member가 직접 받을 수 있다. 판정은 한 줄이다.

```python
def response_destination(ws_ver: int, vt_ver: int, originator_sa: int, master_sa: int) -> int:
    return originator_sa if (ws_ver >= 4 and vt_ver >= 4) else master_sa
```

WS 버전과 VT 버전이 모두 4 이상일 때만 명령을 보낸 CF의 주소(`originator_sa`)를 돌려주고, 아니면 Master의 주소(`master_sa`)를 돌려준다.

### 하위 호환 규칙

- WS는 낮은 버전 VT에 높은 버전 메시지를 보내면 안 되고(예: version 4 명령을 version 2 VT에), VT도 낮은 버전 WS에 높은 버전 메시지를 보내면 안 된다. 받은 쪽의 반응은 예측할 수 없다. NACK를 줄 수도, 무시할 수도 있다.
- 연결된 VT가 WS의 기능 요구를 못 맞추면(필요한 version 4 기능이 없는 version 2 VT, 쓸모없을 만큼 작은 Data Mask 등) WS는 <strong>최소 호환 풀</strong>을 보내 운전자에게 비호환을 알려야 한다. 최소 호환 풀은 그 VT에서도 뜨는 작은 풀로, 이 VT에서는 작업기를 제대로 쓸 수 없다고 알리는 데 쓴다.
- version 5 이상 VT와 WS는 각각 VT Unsupported VT Function / Unsupported VT Function 메시지를 지원해야 한다. 그래서 모르는 기능에 대한 반응이 예측 가능해진다([31장](/study/isobus/31-vt-connection)).

::: tip 정리
- WS마다 Master가 하나 있고, Master가 VT 사용권을 얻고 풀을 올린다. 운전자 입력값은 항상 Master에게 간다.
- 응답 목적지는 WS·VT가 모두 v4 이상일 때만 originator이고, 나머지는 WS Master다.
:::

<small>근거: ISO 11783-6 4.6.2, Table 1</small>

## 5. 비슷한 Working Set 여러 대: Instance와 표시 번호

이 절에서는 같은 제조사의 비슷한 장비가 여러 대 붙었을 때 운전자가 화면의 WS를 어떻게 구분하는지 본다.

같은 제조사의 겉모습이 비슷한 WS가 한 네트워크에 여럿 붙으면(같은 제조사 스프레이어 2대, 비슷한 보조 입력 장치 2대 이상) 운전자는 화면의 WS가 어느 장비인지 알 수 없다. 표준은 두 가지를 요구한다.

1. <strong>NAME의 Instance 필드로 구분한다</strong>. instance는 같은 종류의 장비 가운데 몇 번째인지 나타내는 번호로, NAME 안에 들어 있다. 왼쪽→오른쪽, 그다음 앞→뒤, 그다음 아래→위 순으로 낮은 instance부터 배치하라고 권한다. 제조사는 구성 수단을 줘야 한다. instance를 보고 위치를 찾게 하거나(장비 라벨에 instance 표시, 하네스 배선이 위치에 따라 instance를 자동 설정), 위치를 보고 instance를 정하게 한다(장비의 instance 스위치, Data Mask 위 설정 화면, 서비스 툴의 commanded name 메시지).
2. <strong>WS 번호를 화면에 보인다</strong>. Working Set object(descriptor)에는 반드시, 보이는 마스크에는 가능하면 번호를 표시한다. 번호 규칙은 제조사가 정하되 Function Instance·Device Class Instance·ECU Instance와 엮으라고 권하고(예: 번호 = Function Instance + 1), 같은 제조사의 비슷한 장비는 모두 같은 규칙을 써야 한다.

하네스(harness)는 장비에 깔린 전선 묶음이다. commanded name 메시지는 서비스 툴이 다른 장치의 NAME 일부를 바꾸라고 명령하는 메시지다([14장](/study/isobus/14-name-management-init)).

VT는 WS를 운전자에게 나타낼 때마다 descriptor를 쓴다(통신 알람, 보조 입력 할당 화면 등). 번호가 없으면 할당 화면에서 두 스프레이어가 똑같이 보인다. NAME에서 Function Instance는 Byte 5의 bit 8~4, ECU Instance는 bit 3~1이다(NAME 구조는 [12장](/study/isobus/12-j1939-address-name)). NAME의 비트 번호는 1부터 센다(bit 8이 최상위).

| 장비 | NAME Byte 5 | Function Instance | 표시 번호(FI + 1) |
|---|---|---|---|
| 스프레이어 A | `0x00` | 0 | 1 |
| 스프레이어 B | `0x08` | 1 | 2 |

스프레이어 B를 풀어 읽어 보자. `0x08`은 2진수 `0000 1000`이다. 위쪽 다섯 비트(bit 8~4) `00001`이 Function Instance = 1이고, 아래 세 비트(bit 3~1) `000`이 ECU Instance = 0이다. 그래서 표시 번호는 1 + 1 = 2다.

::: tip 정리
- 비슷한 장비는 NAME Instance로 구분하고 descriptor에 번호(예: FI + 1)를 보인다.
:::

<small>근거: ISO 11783-6 4.6.3, 4.6.4, 4.6.8, ISO 11783-5 Table 1</small>

## 6. 언어·형식·단위: Language command

이 절에서는 운전자가 고른 언어와 단위를 VT가 작업기들에게 어떻게 알리고, 작업기가 그 값을 받아 무엇을 하는지 본다.

표준은 VT가 ISO 11783-7(트랙터와 작업기가 주고받는 응용 메시지를 정하는 문서)의 메시지 일부를 지원하고 직접 보내도록 요구한다. 그 대표가 PGN 65039(0xFE0F) <strong>Language command</strong>다. 이 메시지가 언어, 소수점·날짜·시간 형식, 단위계를 실어 나른다. 운전자가 VT에서 "독일어, 미터법"을 고르면 VT가 이 메시지로 모든 작업기에 알리고, 작업기들이 자기 화면을 거기에 맞추는 식이다.

### VT가 할 일

VT 쪽 의무의 핵심은 세 가지다.

- 표준 언어·형식·단위 메시지("standard setups")를 전원 인가 때와 운전자가 바꿀 때마다 보낸다. standard setups는 비휘발성 메모리에 저장했다가 초기화 때 복원한다.
- 모든 WS가 알려 온 언어와 VT가 지원하는 관련 언어의 <strong>합집합 목록</strong>을 만들어 운전자가 고르게 한다. 이 목록은 비휘발성 메모리에 저장하면 안 되고, WS가 떠나면 줄여도 된다. 고른 언어를 VT 자신이 지원하지 않으면 독자 방법으로 적절한(또는 기본) 언어로 바꾼다.
- 글로벌로 온 요청과 자기에게 온 요청 모두에 Language command로 답한다. 글로벌(global)은 특정 상대가 아니라 모두에게 보낸 것이다. 언어 코드(ISO 639-1)와 국가 코드(ISO 3166-1)를 함께 싣는 것이 권장된다.

### WS가 Language command를 받았을 때 할 일

아래 목록의 shall은 원문이 "반드시 해야 한다"고 정한 것이다. 원문은 should(권한다)와 can(해도 된다)도 구분해 쓴다.

1. <strong>어느 송신원의 값을 쓸지 고른다.</strong> Language command를 보내는 CF는 여럿일 수 있다(VT 여러 대, TECU). TECU는 트랙터 ECU다([22장](/study/isobus/22-tractor-ecu)). ISO 11783-7의 2018년 개정판(Amd1)은 서비스를 받는 CF에 destination-specific으로 요청하고, 자기 UI를 게시하는 VT의 SA(Source Address, 메시지를 보낸 장치의 주소)에서 온 값을 쓰라고 권한다.
2. <strong>풀을 고친다.</strong> 문자열 교체, 단위 선택, 오프셋·스케일 변경으로 풀을 선택된 언어·단위에 맞춘다. 런타임 변경 명령은 [36장](/study/isobus/36-vt-commands-basics)에 있다. 언어만 다른 풀을 서로 다른 라벨로 저장해 두고 맞는 것을 Load하는 방법도 3절의 "언어만 다른 풀" 예와 맞는다([31장](/study/isobus/31-vt-connection)).
3. <strong>지원하지 않으면 기본값으로.</strong> 고른 언어·형식·단위를 지원하지 않으면 독자 방법으로 적절한(또는 기본) 설정을 고른다(shall).
4. <strong>VT마다 따로 맞춘다.</strong> standard setups는 풀을 게시하는 VT 기준으로 구성하므로 VT마다 다를 수 있다(예: 보조 입력 오브젝트는 Function Instance 0 VT에, 나머지 풀은 다른 VT에).
5. <strong>언제든 다시 온다.</strong> VT는 운전자가 바꿀 때마다 보내므로 초기화 때 한 번 읽고 끝내면 안 된다.

WS의 지원 언어 목록은 처음에 Working Set object로 알리고, Working Set Special Controls object로 대체할 수 있다(언어 + 국가 코드). 초기화 중 언어 메시지를 아직 못 받았고 표현이 언어·단위에 의존하면 VT에 요청할 수 있다(초기화 6단계, [31장](/study/isobus/31-vt-connection)).

요청은 PGN 59904(0xEA00) Request 메시지에 PGN 65039를 리틀엔디언 3바이트로 실은 `0F FE 00`이다. 65039는 16진수로 `0x00FE0F`이고, 낮은 자리 바이트부터 적으면 `0F FE 00`이 된다. Request는 VT↔ECU PGN이 아니라 ISO 11783-3(데이터 링크 계층을 정하는 문서)의 메시지이고 DLC가 3으로 정해져 있다. DLC(Data Length Code)는 CAN 프레임에 실린 데이터 바이트 수다. 그래서 [31장](/study/isobus/31-vt-connection)에서 볼 "VT 메시지는 `FF`로 8바이트를 채운다" 규칙의 대상이 아니다.

### Language command 바이트 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

바이트 배치는 다음과 같다. 국가 코드(Byte 7~8)는 ISO 11783-7의 2018년 개정판(Amd1)에서 정해졌다. 각 값의 뜻은 [25장](/study/isobus/25-settings-safety-messages)과 [부록 Part 7](/study/isobus/appendix-iso-part07)에 있다. 이 표의 비트 번호는 ISO 11783-7 방식대로 1부터 센다(bit 8이 최상위).

| Byte | 내용 |
|---|---|
| 1~2 | Language code: ISO 639 두 글자, 소문자(예: `de` = `64 65`) |
| 3 | bit 8·7 소수점 기호(00 쉼표, 01 점), bit 6·5 시간 형식(00 24시간, 01 12시간), bit 4~1 예약 |
| 4 | 날짜 형식(0 = ddmmyyyy … 5 = yyyyddmm) |
| 5 | bit 8·7 거리, 6·5 면적, 4·3 부피, 2·1 질량 단위 |
| 6 | bit 8·7 온도, 6·5 압력, 4·3 힘, 2·1 Units system |
| 7~8 | Country code: ISO 3166-1 alpha-2, 대문자(예: `DE` = `44 45`). 두 글자 모두 all 1이면 국가 코드 없음 |

독일어·독일, 쉼표 소수점, 24시간, ddmmyyyy, 전부 미터법이면 `64 65 0F 00 00 00 44 45`다. Byte 3의 예약 비트 4개는 ISO 11783-7의 일반 규칙(예약 비트는 모두 1로 채운다, [23장](/study/isobus/23-implement-messages-basics))대로 1로 채워 `0x0F`가 된다. 바이트별로 읽으면 다음과 같다.

1. Byte 1~2 `64 65`: 문자 `d`(`0x64`)와 `e`(`0x65`), 언어 "de"(독일어)다.
2. Byte 3 `0F` = `0000 1111`: bit 8·7 = 00(쉼표), bit 6·5 = 00(24시간), bit 4~1 = 1111(예약)이다.
3. Byte 4 `00`: 날짜 형식 0 = ddmmyyyy다.
4. Byte 5·6 `00 00`: 단위 칸이 모두 00, 즉 모두 미터법이다.
5. Byte 7~8 `44 45`: 문자 `D`, `E`, 국가 "DE"(독일)다.

::: details NAME·Language command 검산
아래 코드는 5절의 NAME 표시 번호, 위 Language command 8바이트, Request 3바이트를 조립해 확인한다.

```python
def function_instance(name: bytes) -> int:
    return name[4] >> 3                      # Byte 5의 bit 8~4


assert function_instance(bytes([0, 0, 0, 0, 0x00, 0, 0, 0])) + 1 == 1
assert function_instance(bytes([0, 0, 0, 0, 0x08, 0, 0, 0])) + 1 == 2

decimal_comma, time_24h, reserved = 0b00, 0b00, 0b1111
byte3 = decimal_comma << 6 | time_24h << 4 | reserved
lang = b"de" + bytes([byte3, 0, 0x00, 0x00]) + b"DE"
assert lang.hex(" ").upper() == "64 65 0F 00 00 00 44 45"

request = (65039).to_bytes(3, "little")
assert request.hex(" ").upper() == "0F FE 00"
print("NAME·Language command 검증 통과")
```
`name[4]`는 0부터 세는 파이썬 인덱스라 Byte 5를 가리킨다. `>> 3`은 아래 세 비트(ECU Instance)를 버리고 위 다섯 비트만 남긴다.
:::

::: tip 정리
- Language command(`0xFE0F`)는 자기 풀을 게시하는 VT의 값을 쓰고, 운용 중에도 다시 올 수 있다.
- VT는 언어·형식·단위를 전원 인가 때와 운전자가 바꿀 때마다 보내고, WS는 그 값에 맞춰 풀을 고친다.
:::

<small>근거: ISO 11783-6 4.6.5, 4.6.6.2, Annex I, ISO 11783-7 B.21, A.23, 3.3, ISO 11783-3 5.4.3</small>

## 7. 기술 데이터 메시지: VT의 능력을 묻는다

이 절에서는 작업기가 풀을 올리기 전에 VT의 능력을 묻는 기술 데이터 메시지의 공통 규칙을 보고, 그 가운데 가장 먼저 쓰는 Get Memory를 바이트로 읽는다.

기술 데이터 메시지는 초기화 7단계([31장](/study/isobus/31-vt-connection))에서 WS가 VT의 능력을 묻는 메시지들이다. 모두 ECU→VT PGN 59136(0xE700) 요청과 VT→ECU PGN 58880(0xE600) 응답의 쌍이고 destination-specific이다. 공통 규칙은 다음과 같다.

- 매크로 안에서 쓸 수 없다. 매크로는 이벤트가 생기면 VT가 실행하도록 풀에 넣어 둔 명령 목록이다([38장](/study/isobus/38-vt-macro-input)). WS Master·Member뿐 아니라 어떤 CF든 보낼 수 있다.
- 응답 값은 VT 버전에 따라 달라질 수 있지만 WS 버전에 맞춰 바꾸지 않는다. VT가 아직 WS 버전을 모를 수 있기 때문이다.
- Byte 1 상위 니블 `1100`이 Get Technical Data 계열이라 코드가 `0xC0`~`0xC7`에 모여 있다. 니블(nibble)은 4비트, 즉 16진수 한 자리다. `0xC0`(=192)~`0xC7`(=199)은 2진수로 `1100 0000`~`1100 0111`이라 앞 네 비트가 모두 `1100`이다.
- 요청 대부분은 Byte 1만 의미가 있고 Byte 2~8은 `FF`다(예: Get Hardware = `C7 FF FF FF FF FF FF FF`). 예외는 Get Memory(Byte 3~6), Get Supported Widechars(Byte 2~6), Screen Capture(Byte 2~3)다.

| 코드 | 메시지 | 응답에서 읽는 것 |
|---|---|---|
| `0xC0` | Get Memory | VT 버전, 메모리 여유 |
| `0xC2` | Get Number of Soft Keys | designator 크기, 키 개수 |
| `0xC3` | Get Text Font Data | 폰트 크기·스타일 비트마스크 |
| `0xC7` | Get Hardware | 부팅 시간, 색 모드, 입력·오디오 장치, Data Mask 크기 |
| `0xC1` | Get Supported Widechars | 코드 플레인별 지원 문자 범위(v4 이상) |
| `0xC4` | Get Window Mask Data | User-Layout 배경색(v4 이상) |
| `0xC5` | Get Supported Objects | 지원 오브젝트 타입 목록(v4 이상) |
| `0xC6` | Screen Capture | 화면 캡처 결과(v6 이상) |

비트마스크(bitmask)는 비트 하나하나가 기능 하나의 지원 여부를 나타내는 바이트다. 표의 나머지 메시지는 8절에서 예제 바이트로 읽는다.

### Get Memory(`0xC0`): 버전과 메모리

표의 uint32는 부호 없는 32비트(4바이트) 정수이고, LE는 리틀 엔디언(낮은 자리 바이트가 먼저)이다.

| Byte | 요청 | 응답 |
|---|---|---|
| 1 | `C0` | `C0` |
| 2 | `FF` | Version Number([29장](/study/isobus/29-vt-basics) 5절 표) |
| 3 | Memory Required(uint32, LE) 시작 | Status: 0 = 메모리가 충분할 수 있다, 1 = 부족하다(풀 전송 금지) |
| 4~6 | Memory Required 계속 | `FF` |
| 7~8 | `FF` | `FF` |

- <strong>버전만 알고 싶으면 Memory Required = 0</strong>으로 보낸다(should). 응답의 버전으로 실제 필요량을 계산해 다시 보내면 된다. 이 메시지로 메모리를 할당하는 VT라면, 값이 0이거나 보낸 CF가 아직 WS Master로 식별되지 않았을 때는 할당하지 말아야 한다.
- Memory Required는 version 3 이하에서 풀의 바이트 수다. Graphics Context를 지원하는 version 4 이상에서는 여기에 Graphics Context 오브젝트(GCO)마다의 추정 저장량을 더한다. GCO는 작업기가 명령으로 점, 선, 그림을 그려 넣는 캔버스 오브젝트라 픽셀을 저장할 메모리가 따로 든다.
- GCO 하나는 `RoundUp(width ÷ PixelsPerByte) × height`로 어림하고, PixelsPerByte는 Graphic Type이 0(모노)이면 8, 1(16색)이면 2, 2(256색)면 1이다. RoundUp은 올림이고, PixelsPerByte는 한 바이트에 담기는 픽셀 수다. 실제로는 알린 양보다 적게 보내도 된다.
- Status 0이 "충분하다"가 아니라 "충분할 <strong>수 있다</strong>"인 이유를 원문이 밝힌다. 오브젝트 저장에는 오버헤드(데이터 말고 관리에 더 드는 공간)가 있어 풀 내용을 정확히 알기 전엔 단정할 수 없다. 실제 부족은 End of Object Pool response Byte 2 bit 1(전송 중 메모리 고갈)로 드러난다.
- Status 1이면 WS Master는 풀을 보내면 안 된다(shall not). 기능을 줄인 풀 크기로 다시 물을 수 있다.

예: 29장 7절의 98바이트 풀에 200 × 100 Graphics Context 하나를 더해 16색 VT에 올린다고 하자. GCO도 풀 안의 오브젝트이므로 풀 자체가 먼저 커진다. GCO 레코드 34바이트(Graphics Context 레코드는 Transparency colour 필드에서 끝나고 매크로 목록 필드가 없다)와, 이 GCO를 담는 Data Mask의 자식 참조 6바이트(Object ID 2 + X 2 + Y 2)가 더해져 풀은 98 + 34 + 6 = 138바이트다. 여기에 GCO 저장량 `RoundUp(200 ÷ 2) × 100 = 10 000`을 더하면 Memory Required = 10 138 = `0x279A`, 요청은 `C0 FF 9A 27 00 00 FF FF`다.

단계별로 다시 보면 다음과 같다.

1. 풀 크기: 98 + 34 + 6 = 138바이트.
2. 16색 VT이므로 PixelsPerByte = 2다. GCO 저장량 = RoundUp(200 ÷ 2) × 100 = 100 × 100 = 10 000.
3. 합계 138 + 10 000 = 10 138 = `0x0000279A`.
4. 리틀 엔디언 4바이트로 쓰면 `9A 27 00 00`이다. 앞에 `C0 FF`, 뒤에 예약 `FF FF`를 붙인다.

::: tip 정리
- 기술 데이터 메시지는 작업기가 VT의 능력을 묻는 질문과 답이다. 코드는 `0xC0`~`0xC7`이다.
- Get Memory 응답으로 VT 버전과 메모리 상태를 읽는다. 버전만 알고 싶으면 Memory Required = 0으로 묻는다.
- Status 0은 "충분할 수 있다"이고, Status 1이면 풀을 보내면 안 된다.
:::

<small>근거: ISO 11783-6 Annex C, C.2.2, C.2.5, D.1~D.3, Table B.59</small>

## 8. 기술 데이터 응답 읽기 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절에서는 나머지 기술 데이터 메시지의 응답을 예제 바이트로 하나씩 읽는다. 이 절의 비트 번호는 VT 메시지 방식대로 0부터 센다(bit 7이 최상위).

### Get Number of Soft Keys(`0xC2`)

응답 `C2 01 FF FF 50 50 40 06`을 읽어 보자. `0x50`은 80, `0x40`은 64다.

| Byte | 값 | 필드 | 뜻 |
|---|---|---|---|
| 2 | `01` | Navigation Soft Keys | 넘김에 쓰는 물리 키 1개. version 3 이하 VT는 `FF`(예약)이므로 255개로 읽으면 안 된다 |
| 3~4 | `FF FF` | 예약 | |
| 5·6 | `50 50` | X Dots·Y Dots | designator 80 × 80 픽셀 |
| 7 | `40` | Virtual Soft Keys | 64개(version 4 이상은 항상 64, version 3 이하는 6~64) |
| 8 | `06` | Physical Soft Keys | 물리 키 6개 |

80 × 80 designator와 물리 키 6개이므로 version 6 요구(60 × 60 이상, [29장](/study/isobus/29-vt-basics) 5절)와 version 4 이상 요구(물리 6 이상)를 모두 만족한다. 2절 그림의 VT가 이 응답을 보내는 VT다.

### Get Text Font Data(`0xC3`)

응답 Byte 2~5는 `FF`이고, Byte 6~8에 비트마스크 세 개가 온다.

- Byte 6 small 크기: bit 0~6 = 8 × 8, 8 × 12, 12 × 16, 16 × 16, 16 × 24, 24 × 32, 32 × 32. 6 × 8은 기본 폰트라 비트가 없어서 `0x00`이면 "6 × 8만 지원"이다.
- Byte 7 large 크기: bit 0~6 = 32 × 48, 48 × 64, 64 × 64, 64 × 96, 96 × 128, 128 × 128, 128 × 192.
- Byte 8 스타일: bit 0~6 = Bold, Crossed out, Underlined, Italics, Inverted, Flash inverted, Flash hidden. bit 7 = 비례 폰트 렌더링으로, version 4에서 생겼지만 비트마스크라 version 3 이하 WS에게도 보낼 수 있다. WS는 모르는 비트를 무시하면 된다.

예: `C3 FF FF FF FF 1F 01 1F` → small 8 × 8·8 × 12·12 × 16·16 × 16·16 × 24(+ 기본 6 × 8), large 32 × 48, 스타일 Bold·Crossed out·Underlined·Italics·Inverted다. 이 VT가 version 6를 보고한다면 version 6 요구(크기·스타일 전부, [29장](/study/isobus/29-vt-basics) 5절) 위반이다.

`1F`는 2진수 `0001 1111`이라 bit 0~4가 1이다. 그래서 small 목록과 스타일 목록의 앞 다섯 개가 켜진다. `01`은 bit 0만 1이라 large는 32 × 48 하나다.

### Get Hardware(`0xC7`)

응답 `C7 1E 02 31 E0 01 E0 01`을 읽어 보자.

![Get Hardware response 8바이트 배치. Byte 1 C7은 Get Hardware, Byte 2 1E는 Boot time 30초, Byte 3 02는 Graphic Type 256색, Byte 4 31은 Hardware 비트, Byte 5·6 E0 01은 X-Pixels 480, Byte 7·8 E0 01은 Y-Pixels 480이다. 아래에 Byte 4 0x31 = 0011 0001을 bit 7부터 bit 0까지 펼쳐 bit 5 Button 동시 활성, bit 4 물리 Soft Key 동시 활성, bit 0 터치스크린이 1임을 보인다](/images/study-isobus/30-get-hardware-response-light.png)
![Get Hardware response 8바이트 배치. Byte 1 C7은 Get Hardware, Byte 2 1E는 Boot time 30초, Byte 3 02는 Graphic Type 256색, Byte 4 31은 Hardware 비트, Byte 5·6 E0 01은 X-Pixels 480, Byte 7·8 E0 01은 Y-Pixels 480이다. 아래에 Byte 4 0x31 = 0011 0001을 bit 7부터 bit 0까지 펼쳐 bit 5 Button 동시 활성, bit 4 물리 Soft Key 동시 활성, bit 0 터치스크린이 1임을 보인다](/images/study-isobus/30-get-hardware-response-dark.png)

| Byte | 값 | 필드 | 뜻 |
|---|---|---|---|
| 2 | `1E` | Boot time | 전원 인가·리셋부터 첫 VT Status까지 최대 30초. 모르면 `FF`. version 4에서 도입됐고 이전 버전도 써도 된다 |
| 3 | `02` | Graphic Type | 0 = 모노크롬(색 0·1), 1 = 16색(0~15), 2 = 256색(0~255, 모든 Picture Graphic 형식) |
| 4 | `31` | Hardware | `0011 0001` → bit 0 터치스크린 + Pointing Event, bit 4 물리 Soft Key 동시 활성(모든 조합), bit 5 Button 동시 활성(모든 조합) |
| 5~6 | `E0 01` | X-Pixels | Data Mask 가로 480 |
| 7~8 | `E0 01` | Y-Pixels | 세로 480(항상 X와 같음) |

Byte 4의 나머지 비트는 bit 1 포인팅 장치 + Pointing Event, bit 2 다중 주파수 오디오, bit 3 음량 조절 오디오, bit 6 드래그를 Pointing Event로 보고(bit 0 또는 1이 있어야 함), bit 7 드래그 중간 좌표(bit 6이 있어야 함)다. bit 4~7은 version 4 이상에만 있다. Pointing Event는 운전자가 화면을 누른 좌표를 VT가 작업기에 알리는 메시지다([39장](/study/isobus/39-vt-alarm-activation)). Boot time은 다중 VT 환경에서 "선호 VT를 얼마나 기다릴지"를 정하는 데 쓴다([31장](/study/isobus/31-vt-connection)).

### Get Supported Widechars(`0xC1`, version 4 이상)

WideString(UTF-16)에서 VT가 실제로 그릴 수 있는 문자 범위를 묻는다. WideString은 글자를 UTF-16(유니코드 글자를 2바이트 단위로 적는 방식)으로 담은 문자열이고, WideChar는 그 글자 하나다. 코드 플레인(code plane)은 유니코드 문자 번호를 65,536개씩 나눈 구역이며, 플레인 0에 대부분의 현대 문자가 들어 있다.

- 요청: Byte 2 = 코드 플레인(0~16), Byte 3~4 = 첫 WideChar, Byte 5~6 = 마지막 WideChar(첫 ≤ 마지막), Byte 7~8 = `FF`. 한 메시지는 플레인 하나만 묻는다.
- 응답(가변 길이): Byte 2 = 코드 플레인, Byte 3~6 = 물은 범위 반향, Byte 7 = Error Codes(bit 0 하위 범위 255개 초과, bit 1 코드 플레인 오류, bit 4 기타), Byte 8 = 범위 개수(오류면 0), Byte 9~ = {첫, 마지막} WideChar 쌍(쌍당 4바이트). 8바이트를 넘으면 TP로 온다. 큰 범위 하나 대신 작은 범위로 여러 번 물으면 응답 프레임을 줄일 수 있다.
- 꼭 물어야 하는 메시지는 아니다. VT는 미지원 문자가 섞여도 WideString을 표시하고, 코드 플레인 0 응답에는 WideChar 최소 문자 집합이 들어간다. 최소 문자 집합은 version 4 이상 VT가 반드시 그려야 하는 글자 목록으로, [35장](/study/isobus/35-vt-pool-transfer-charset)에서 본다.

표준에 실린 예(최소 문자 집합만 지원하는 VT에 `0x0000`~`0x3FFF`를 물은 경우)의 앞부분은 다음과 같다.

```text
요청  C1 00 00 00 FF 3F FF FF
응답  C1 00 00 00 FF 3F 00 0F | 20 00 7E 00 | A0 00 7E 01 | … (범위 15개)
      헤더: 플레인 0, 범위 반향, 오류 0, 범위 15   0x0020~0x007E  0x00A0~0x017E
```

응답 Byte 8의 `0F`는 범위 개수 15다. 그 뒤로 4바이트씩 {첫 글자, 마지막 글자} 쌍이 이어진다. 첫 쌍 `20 00 7E 00`은 리틀 엔디언으로 `0x0020`~`0x007E`, 즉 영문자·숫자·기호가 든 기본 라틴 문자 범위다.

### Get Window Mask Data(`0xC4`)·Get Supported Objects(`0xC5`)

<strong>Get Window Mask Data</strong>는 Window Mask를 지원하는 version 4 이상 VT에만 쓴다. Window Mask는 여러 WS의 작은 창을 한 화면(User-Layout)에 모아 보여 줄 때 쓰는 창이다([34장](/study/isobus/34-vt-layout-color)). 응답 Byte 2 = User-Layout Data Mask 배경색, Byte 3 = User-Layout Soft Key Mask의 Key Cell 배경색, Byte 4~8 = `FF`다. Free Form이 아닌 Window Mask는 배경색·투명도를 VT가 정하므로, WS가 창 내용을 VT 배경에 맞춰 설계할 때 이 값을 쓴다.

<strong>Get Supported Objects</strong>는 VT가 지원하는 오브젝트 타입 목록을 묻는다.

- 응답 Byte 2 = 뒤따르는 바이트 수다. 원문은 "미래 호환을 위해 타입 개수와 같다고 보장하지 않는다"고 못 박는다.
- Byte 3~ = 지원 타입을 <strong>오름차순</strong>으로 1바이트씩 나열한다. 파싱 중 `FF`를 만나면 목록 끝이고 뒤는 무시한다.
- VT는 필수 타입 전부와 지원하는 선택 타입 전부를 넣는다. 독점 타입은 접속한 WS에 따라 달리 넣거나 아예 빼도 되고, 넣었더라도 그 타입이 든 풀을 거부할 수 있다. 독점 타입은 제조사가 자기 제품끼리 쓰려고 정의한 종류다. Auxiliary Input Type 1·Auxiliary Function Type 1(옛 보조 입력 방식인 AUX-O의 오브젝트)은 넣으면 안 된다.
- 지원 타입이 6개만 넘어도 응답이 8바이트를 넘어 한 프레임에 들어가지 않는다. 수신 측은 TP로 오는 가변 길이 응답까지 받을 준비를 하는 편이 안전하다(추론).

`FF`를 목록 끝 표시로 쓸 수 있는 이유는 종류 번호를 나눠 둔 방식에 있다. VT 오브젝트 종류 번호는 다음처럼 나뉜다([32장의 오브젝트 종류 표](/study/isobus/32-vt-object-pool-basics) 참고).

| 종류 번호 | 쓰임 |
|---|---|
| 0~48 | 표준 오브젝트(version 6 기준 전부 배정) |
| 49~239 | 예약(나중을 위해 비워 둠) |
| 240~254 | 제조사 정의(독점) 오브젝트 |
| 255 | 어떤 오브젝트에도 배정하지 않음 |

255는 어떤 오브젝트에도 배정되지 않고 비어 있다. 그래서 목록 끝 표시 `FF`(255)가 실제 종류 번호와 겹칠 일이 없다. 표준의 종류 번호 표도 255 칸에 "Get Supported Objects를 참고하라"는 표시만 붙여 둔다. 표준에 이유가 직접 적혀 있지는 않지만, 이 충돌을 피하려는 것으로 보인다(추론).

목록에 없다고 그 오브젝트를 풀에서 빼야 하는 것은 아니다. VT는 목록에 없는 비독점 오브젝트도 <strong>파싱은</strong> 해야 하므로(기능은 지원하지 않아도 됨) WS는 같은 풀을 여러 VT에 쓸 수 있다([34장](/study/isobus/34-vt-layout-color)). 다만 그런 오브젝트를 겨냥해 명령을 보내면 VT는 0이 아닌 Error Code로 답하고, 그 값은 VT 설계에 따른다. 원문에 실린 예는 Graphics Context를 목록에 넣지 않은 VT에 그 오브젝트를 겨냥한 Change Background Colour를 보내 오류 응답을 받는 경우다.

::: details 원문을 가진 독자를 위한 메모
- Get Supported Objects response(D.15)의 Data length는 원문에 8 bytes로 적혀 있다. 지원 타입이 6개를 넘으면 8바이트에 들어가지 않으므로, 본문은 TP로 오는 가변 길이 응답을 받을 준비를 하라고 적었다.
- Table A.1은 오브젝트 타입 255를 "Reserved for future use (see D.14)"로 둔다. 본문의 "종류 번호 표도 255 칸에 Get Supported Objects를 참고하라는 표시만 붙여 둔다"는 이 칸을 말한다. 49~239는 같은 표에서 "Reserved for future use", 240~254는 Manufacturer Defined Objects다.
:::

### Screen Capture(`0xC6`, version 6 이상)

VT에 무손실 화면 캡처를 요청한다. 주로 시험 시스템용이라 VT는 기본 비활성으로 두고 독자 조작으로만 켜게 할 수 있다.

- 요청: Byte 2 = Item(0 = 화면 이미지, 240~255 제조사 독점), Byte 3 = Path(1 = VT가 접근하는 저장소·이동식 미디어, 240~255 제조사 독점), Byte 4~8 = `FF`. 매크로에서 쓸 수 없다.
- 응답: Byte 2~3 = 요청 반향, Byte 4 = Error Codes(bit 0 비활성, bit 1 전송 버퍼 사용 중, bit 2 Item 미지원, bit 3 Path 미지원, bit 4 이동식 미디어 가득 참·없음, bit 5 기타). 오류가 없고 Path = 1이면 Byte 5~6 = 이미지 번호(uint16)다.
- VT는 이미지 번호를 파일 이름에 넣고(예: `IMG00001.PNG`) 캡처마다 늘린다. 파일 시스템 상태에 따라 1부터 시작하지 않을 수 있다.

VT 화면을 자동으로 확인해야 하는 SIL 검증 환경이라면, 실 VT에서 회귀 비교용 화면을 얻는 데 이 명령을 쓸 수 있다(활용 예). SIL(Software-in-the-Loop)은 실제 장비 대신 소프트웨어를 돌려 시험하는 방식이고, 회귀 비교는 무언가를 바꾼 뒤에도 화면이 예전과 같은지 대조하는 일이다.

::: details 기술 데이터 응답 디코딩 코드
아래 코드는 이 절의 응답 예제를 해석하는 함수와, 7절의 Get Memory 계산을 `assert`로 확인한다.

```python
import math

SMALL = ["8x8", "8x12", "12x16", "16x16", "16x24", "24x32", "32x32"]
LARGE = ["32x48", "48x64", "64x64", "64x96", "96x128", "128x128", "128x192"]
STYLE = ["Bold", "Crossed out", "Underlined", "Italics", "Inverted",
         "Flash inverted", "Flash hidden", "Proportional"]


def bits(mask, names):
    return [n for i, n in enumerate(names) if mask >> i & 1]


def decode_soft_keys(f):
    assert f[0] == 0xC2
    return {"navigation": None if f[1] == 0xFF else f[1], "x_dots": f[4],
            "y_dots": f[5], "virtual": f[6], "physical": f[7]}


def decode_font(f):
    assert f[0] == 0xC3
    return {"small": ["6x8"] + bits(f[5], SMALL), "large": bits(f[6], LARGE),
            "style": bits(f[7], STYLE)}


def decode_hardware(f):
    assert f[0] == 0xC7
    return {"boot_s": None if f[1] == 0xFF else f[1], "graphic": f[2], "hw": f[3],
            "x": int.from_bytes(f[4:6], "little"), "y": int.from_bytes(f[6:8], "little")}


def parse_supported_objects(f):
    assert f[0] == 0xC5
    types = []
    for b in f[2:2 + f[1]]:
        if b == 0xFF:                       # 목록 끝
            break
        types.append(b)
    return types


assert decode_soft_keys(bytes.fromhex("C2 01 FF FF 50 50 40 06")) == {
    "navigation": 1, "x_dots": 80, "y_dots": 80, "virtual": 64, "physical": 6}

font = decode_font(bytes.fromhex("C3 FF FF FF FF 1F 01 1F"))
assert font["small"] == ["6x8", "8x8", "8x12", "12x16", "16x16", "16x24"]
assert font["large"] == ["32x48"]
assert font["style"] == ["Bold", "Crossed out", "Underlined", "Italics", "Inverted"]

hw = decode_hardware(bytes.fromhex("C7 1E 02 31 E0 01 E0 01"))
assert hw == {"boot_s": 30, "graphic": 2, "hw": 0x31, "x": 480, "y": 480}
assert [i for i in range(8) if hw["hw"] >> i & 1] == [0, 4, 5]

# 설명용으로 줄인 목록: Working Set(0)·Data Mask(1)·Alarm Mask(2)만 지원하는 VT
assert parse_supported_objects(bytes.fromhex("C5 03 00 01 02 FF FF FF")) == [0, 1, 2]

pool = 98 + 34 + 6                          # §6 풀 + GCO 레코드(B.59) + Data Mask 자식 참조
gco = math.ceil(200 / 2) * 100              # 16색 VT의 200x100 Graphics Context 저장량
req = bytes([0xC0, 0xFF]) + (pool + gco).to_bytes(4, "little") + b"\xFF\xFF"
assert pool == 138 and pool + gco == 10_138
assert req.hex(" ").upper() == "C0 FF 9A 27 00 00 FF FF"
print("기술 데이터 디코딩 검증 통과")
```
실행하면 `기술 데이터 디코딩 검증 통과`가 출력된다. 주석의 "§6 풀"은 옛 장 번호로 지금의 29장 7절 98바이트 풀이고, "GCO 레코드(B.59)"는 7절에서 본 34바이트짜리 Graphics Context 레코드다.
:::

<small>근거: ISO 11783-6 4.1.1, 4.6.28, 4.7.15.1, D.5, D.7, D.9~D.17, Table A.1, Table K.8</small>

::: tip 핵심 정리
- Data Mask는 정사각형이고(최소 200 × 200, version 6은 480 × 480), Soft Key 라벨 칸(designator)은 그 밖에 따로 둔다.
- Soft Key는 물리·가상·내비게이션 개수로 나뉘고, 키가 물리 키보다 많으면 "물리 − 내비게이션" 단위 페이지로 넘긴다.
- Object ID는 WS의 풀 안에서만 유일하고 `0xFFFF`는 NULL이다. WS마다 Master가 VT를 상대하며, 응답은 버전 조합에 따라 Master나 명령을 보낸 CF에게 간다.
- 작업기는 기술 데이터 메시지(`0xC0`~`0xC7`)로 VT의 버전, 메모리, Soft Key, 글꼴, 하드웨어, 지원 오브젝트를 묻고 거기에 풀을 맞춘다.
:::

::: details 확인 문제
1. VT의 Data Mask 영역이 정사각형이어야 하는 이유는 무엇인가? version 6 VT의 최소 크기는?
2. 물리 Soft Key 6개, 내비게이션 1개인 VT에 끝에 NULL이 없는 12칸짜리 Soft Key Mask를 올리면 몇 페이지가 되고, 각 페이지에 몇 칸이 들어가는가?
3. 서로 다른 두 WS의 풀에 Object ID 100이 각각 있다. 문제가 되는가?
4. 작업기가 VT 버전만 알고 싶다. Get Memory 요청 8바이트를 써라.
5. (계산) 16색 version 4 VT에 Graphics Context 두 개(100 × 50, 101 × 40)가 든 12 000바이트 풀(GCO 레코드 포함)을 올린다. Get Memory의 Memory Required 값과 요청 프레임을 구하라.
6. (디코딩) Get Supported Objects 응답 `C5 03 00 01 02 FF FF FF`에서 지원 타입 목록을 읽어라. `FF`를 만나면 목록이 끝났다고 볼 수 있는 이유는 무엇인가?

**답 가이드**
1. VT마다 화면 방향(가로·세로)이 달라도 같은 풀이 제대로 보이게 하려는 것이다. version 6은 최소 480 × 480이다.
2. 12칸은 물리 키 6개보다 많으므로 페이지로 나눈다. 한 그룹은 6 − 1 = 5칸이므로 5, 5, 2칸으로 3페이지다. 6번 물리 키는 모든 페이지에서 넘김 키다.
3. 문제없다. Object ID는 한 WS의 풀 안에서만 유일하면 된다. VT는 WS마다 ID 공간을 따로 관리한다.
4. Memory Required = 0으로 보낸다: `C0 FF 00 00 00 00 FF FF`. 응답 Byte 2로 버전을 읽는다.
5. 12 000바이트에는 GCO 레코드가 이미 들어 있으므로 저장량만 더한다. GCO1 = RoundUp(100 ÷ 2) × 50 = 2 500, GCO2 = RoundUp(101 ÷ 2) × 40 = 51 × 40 = 2 040이다. 합계 12 000 + 2 500 + 2 040 = 16 540 = `0x409C`이므로 요청은 `C0 FF 9C 40 00 00 FF FF`다.
6. Byte 2 `03`은 뒤따르는 바이트 수 3이고, 목록은 0(Working Set), 1(Data Mask), 2(Alarm Mask)다. 오브젝트 종류 번호 255는 어떤 오브젝트에도 배정되지 않아 실제 종류와 겹치지 않으므로 `FF`를 목록 끝 표시로 쓸 수 있다.
:::

## 다음 챕터

- 다음: [31장 VT 연결 관리: 초기화, 감시, 셧다운](/study/isobus/31-vt-connection)
