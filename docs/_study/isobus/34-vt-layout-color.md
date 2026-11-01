---
title: "VT 화면 배치, User-Layout, 색"
description: "VT가 오브젝트를 어디에 어떤 순서로 그리는지, 여러 Working Set의 창을 한 화면에 모으는 User-Layout, 색 번호가 실제 색이 되는 과정을 익힌다."
date: 2026-04-13
tags: [ISOBUS, VT, Object Pool, User-Layout, Colour, ISO-11783-6]
prev: /study/isobus/33-vt-object-records
next: /study/isobus/35-vt-pool-transfer-charset
---

# VT 화면 배치, User-Layout, 색

::: info 학습 목표
- 오브젝트 위치가 부모 기준 상대 좌표라는 것과, 겹치거나 영역을 넘칠 때 VT가 어떻게 그리는지 설명할 수 있다.
- 화면 크기가 다른 VT에 풀을 맞출 때 무엇을 누가 스케일하는지 말할 수 있다.
- User-Layout이 여러 Working Set의 작은 창을 한 화면에 모으는 방식(Window Mask, Key Group, Window Cell)을 설명할 수 있다.
- 오브젝트의 색 번호가 Colour Map과 팔레트를 거쳐 실제 색이 되는 순서를 따라갈 수 있다.
- VT의 색 깊이와 버전에 맞지 않는 색, 그림, 오브젝트를 풀에서 걸러 낼 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [32장 VT 오브젝트 풀 기초](/study/isobus/32-vt-object-pool-basics), [33장 오브젝트 레코드](/study/isobus/33-vt-object-records), [30장 VT 화면 구성과 기술 데이터](/study/isobus/30-vt-display-technical-data)
- 이 장에서 처음 나오는 말
  - 상대 좌표: 부모 오브젝트의 왼쪽 위 모서리를 (0, 0)으로 잡고 잰 위치
  - 클리핑(clipping): 정해진 영역 밖으로 나간 그림을 잘라 내는 것
  - 스케일링(scaling): 설계한 크기를 VT 화면 크기에 맞게 늘리거나 줄이는 것
  - User-Layout: 운전자가 여러 Working Set의 작은 창을 골라 한 화면에 모아 보는 VT 기능
  - 팔레트(palette): 색 번호마다 실제 색을 적어 둔 256칸짜리 표
  - Colour Map: 색 번호를 다른 색 번호로 바꿔 주는 표
:::

같은 오브젝트 풀을 화면 크기와 색 수가 다른 여러 VT에 올려도 비슷하게 보여야 한다. 이 장은 그 약속을 지키는 규칙을 ISO 11783-6(VT를 정하는 표준 문서)에서 골라 본다. 가구 배치도에 방 모서리에서 잰 거리를 적어 두면 방을 옮겨도 배치가 그대로이듯, VT 오브젝트의 위치도 부모 기준으로 적는다. 색도 물감 이름이 아니라 색 견본표의 번호로 적어 두어서, 견본표만 바꾸면 화면 색이 한꺼번에 바뀐다.

## 1. 좌표와 그리는 순서

이 절에서는 VT(Virtual Terminal, 운전석의 공용 화면 단말)가 오브젝트를 어디에, 어떤 순서로, 어디까지 그리는지 본다. "같은 풀이 VT마다 다르게 보인다"는 문제는 대부분 이 규칙에서 나온다. 먼저 그림으로 세 규칙을 한꺼번에 본다.

![좌표와 그리기 순서: 왼쪽은 Data Mask 좌상단 (0, 0) 기준으로 (20, 40)에 놓인 Container와 그 안 (10, 5)의 Input Number가 절대 (30, 45)에 그려지고 같은 Container가 (20, 120)에 한 번 더 포함된 모습, 오른쪽은 목록 2번이 1번 위에 겹쳐 그려지고 부모 밖으로 나간 3번의 바깥 부분이 잘리는 모습](/images/study-isobus/16-coordinates-overlay-light.png)
![좌표와 그리기 순서: 왼쪽은 Data Mask 좌상단 (0, 0) 기준으로 (20, 40)에 놓인 Container와 그 안 (10, 5)의 Input Number가 절대 (30, 45)에 그려지고 같은 Container가 (20, 120)에 한 번 더 포함된 모습, 오른쪽은 목록 2번이 1번 위에 겹쳐 그려지고 부모 밖으로 나간 3번의 바깥 부분이 잘리는 모습](/images/study-isobus/16-coordinates-overlay-dark.png)

그림은 이렇게 읽는다.

- 왼쪽(좌표): x는 오른쪽, y는 아래쪽으로 커진다. Input Number(숫자를 입력받는 칸)의 위치 (10, 5)는 Data Mask(작업기 화면 한 장)가 아니라 Container의 왼쪽 위에서 잰 값이다.
- 오른쪽(겹침과 잘림): 부모의 자식 목록에서 2번이 1번보다 뒤에 있으므로 2번이 위에 보인다. 3번은 부모 영역 밖으로 나간 부분이 잘린다.

쉽게 말하면 방 안 가구 배치도와 같다. 책상 위치를 "방 왼쪽 위 모서리에서 오른쪽으로 10, 아래로 5"처럼 방 기준으로 적어 두면, 방을 통째로 옮겨도 방 안 배치는 그대로다. 나중에 들여놓은 가구가 먼저 놓인 가구를 가리고, 벽 밖으로 튀어나간 부분은 보이지 않는다. 비유와 다른 점도 하나 있다. VT에서는 같은 방(Container)을 여러 곳에 동시에 둘 수 있다.

### 좌표계와 상대 위치

- 단위는 따로 밝히지 않는 한 물리 픽셀이다. x는 오른쪽, y는 아래쪽으로 커지고, 좌표는 부호 있는 값이며, 원점 (0, 0)은 <strong>부모 오브젝트의 좌상단</strong>(왼쪽 위 모서리)이다.
- 위치는 자식 레코드가 아니라 <strong>부모 레코드의 자식 목록</strong>에 들어 있다. 그래서 같은 Container(여러 오브젝트를 한 덩어리로 묶는, 그려지지 않는 상자)를 여러 마스크의 여러 위치에 넣어 재사용할 수 있다.
- 화면상 절대 위치는 조상들의 위치를 더한 값이다. Data Mask 안 (20, 40)에 놓인 Container 속 (10, 5)의 Input Number는 절대 (30, 45)에 그려진다. x는 20 + 10 = 30, y는 40 + 5 = 45로 계산한다.
- 좌표가 signed(부호 있는 값)라 음수도 쓸 수 있고, 부모 영역 밖으로 나간 부분은 잘린다(아래 클리핑).
- 런타임에 위치를 바꾸는 명령은 Change Child Location과 Change Child Position이다([37장](/study/isobus/37-vt-command-details)).

### 겹침과 그리는 순서

- 두 오브젝트가 같은 자리를 차지하는 마스크를 VT는 반드시 지원해야 한다(shall). <strong>목록에서 나중에 나온 오브젝트가 위에</strong> 그려진다.
  - 표준 문장의 shall은 "반드시 해야 한다", should는 "그렇게 하는 것이 권고된다"는 뜻이다. 이 장에서도 이 구분을 괄호로 남긴다.
- 오브젝트가 바뀌면 그 위에 겹쳐 있다가 손상된 오브젝트도 다시 그린다(refresh event). 모든 오브젝트가 명시적이거나 암시된 직사각형 크기를 갖는 것도 겹침 판정을 쉽게 하려는 것이다.
- Container를 숨기면 VT는 그 영역을 부모 마스크 배경색으로 채우고, 그 과정에서 영향받은 다른 오브젝트를 다시 그린다. 이 중간 화면이 운전자 눈에 보이지 않게 구현해도 된다. 표준이 예로 드는 경우다.
- v6(VT 버전 6, 버전 설명은 [29장](/study/isobus/29-vt-basics))에서 Colour Palette(7절)로 알파값을 바꾸면 겹친 영역을 합성한다. 알파(α)는 불투명도다. 255면 완전히 불투명하고, 값이 작을수록 아래 색이 더 비친다.
  - 합성색 = 위 색 × α/255 + 아래 색 × (255 − α)/255이고, 맨 아래부터 한 겹씩 계산해 그 결과를 다음 겹의 "아래 색"으로 쓴다.
  - 흰 배경(255) 위의 50 % 회색(128, α = 128)은 191, 검정(0) 위에서는 64가 된다. 흰 배경이면 128 × 128/255 = 64.25와 255 × 127/255 = 127을 더해 191.25, 정수로 191이다.
  - 불투명한 오브젝트를 반투명 오브젝트 위에 올리면 섞이지 않는다.

### 클리핑: 영역 밖은 잘린다

- 크기가 정해진(또는 암시된) 오브젝트는 그 밖에 그려지는 것을 <strong>픽셀 단위로</strong> 잘라낸다. 텍스트와 숫자도 자동 줄바꿈 여부와 상관없이 같다.
- 클리핑 경계가 되는 영역은 다음과 같다.
  - Container의 Width·Height
  - Button Face(버튼의 면)
  - Soft Key designator(Key의 자식과 Working Set 식별 오브젝트가 그려지는 소프트키 칸)
  - Window Mask 영역(5절)
- 출력 도형(선, 사각형 같은 그림 오브젝트)에서 선 두께가 1보다 크면 두께가 안쪽, 바깥쪽, 가운데 중 어디로 자랄지는 VT 재량이다. 그래도 선이 잘리지 않게 오브젝트 영역 안에 들어가야 한다.

정리하면, 위치는 부모 기준으로 적고, 겹치면 목록 뒤쪽이 위에 오며, 정해진 크기 밖은 잘린다. 이 세 규칙만 알아도 VT 화면이 어떻게 그려질지 대부분 예측할 수 있다.

<small>근거: ISO 11783-6 4.4, 4.6.11.1, 4.6.12, 4.6.13, 4.6.15, 4.7.5, B.1, B.4, B.6, B.7, B.10.1</small>

## 2. 스케일링: 화면 크기가 다른 VT에 맞추기

이 절에서는 같은 풀을 화면 크기가 다른 VT에 맞추는 일을 누가, 언제, 어떻게 하는지 본다. VT마다 Data Mask의 픽셀 크기와 갖춘 폰트가 다르기 때문에 이 일이 필요하다.

쉽게 말하면 같은 도면을 A4와 A3 용지에 맞춰 확대하거나 축소해 인쇄하는 일이다. 다만 VT는 대부분의 확대를 스스로 해 주지 않는다. [32장](/study/isobus/32-vt-object-pool-basics)에서 본 대로 기본 책임은 Working Set(WS, VT에 화면을 올리는 작업기 쪽 ECU 묶음)에 있다. WS가 Get Hardware 같은 기술 데이터 메시지로 VT의 화면 크기를 물은 뒤, 오브젝트 위치와 크기, 폰트를 직접 바꿔 보낸다.

![스케일링 예: 200 x 200 기준 Data Mask의 (10, 20)에 놓인 120 x 30 오브젝트가 480 x 480 VT에서는 2.4배인 (24, 48)의 288 x 72가 되고, 24 x 32 글자 칸은 57.6 x 76.8 영역으로 늘어나 그 안에 들어가는 48 x 64 폰트를 고르는 모습](/images/study-isobus/34-scaling-example-light.png)
![스케일링 예: 200 x 200 기준 Data Mask의 (10, 20)에 놓인 120 x 30 오브젝트가 480 x 480 VT에서는 2.4배인 (24, 48)의 288 x 72가 되고, 24 x 32 글자 칸은 57.6 x 76.8 영역으로 늘어나 그 안에 들어가는 48 x 64 폰트를 고르는 모습](/images/study-isobus/34-scaling-example-dark.png)

### 누가 스케일하나

대상별로 정리하면 다음과 같다.

| 대상 | 스케일하는 쪽 |
|---|---|
| 일반 오브젝트의 위치·크기 | WS |
| 폰트(best-fit 선택, VT 지원 확인) | WS |
| Soft Key designator 안 오브젝트(Key 자식, Working Set 식별 오브젝트) | WS |
| Picture Graphic | VT(Width 기준) |
| Window Mask type 0(free form)과 그 자식 | WS |
| Window Mask type 1 이상 | VT(Window Icon·Button은 WS가 미리 스케일하고 VT가 더 스케일할 수 있다) |
| Key Group의 자식 | WS |

표를 줄이면 이렇다. VT가 스스로 늘이고 줄이는 것은 Picture Graphic(비트맵 그림)과 표준 창(Window Mask type 1 이상, 5절)뿐이다. 나머지는 모두 WS가 계산해서 보낸다. best-fit은 주어진 칸에 가장 잘 맞는 폰트를 고르는 일이다.

::: details 원문을 가진 독자를 위한 메모
표의 행별 근거 조항: 일반 오브젝트의 위치·크기 4.6.16.2, 폰트 4.6.16.3, Soft Key designator 안 오브젝트 4.6.16.2·B.1, Picture Graphic 4.6.16.4, Window Mask type 0과 type 1 이상 4.7.6, Key Group의 자식 4.7.11.
:::

### 언제, 얼마나

- 시점은 전송 전과 후 어느 쪽이든 된다. 단 전송한 풀이 그 VT에서 무효여서는 안 된다. 흑백 VT에 컬러 오브젝트를 보내 놓고 나중에 흑백으로 고치는 식은 허용되지 않는다.
- 예: 200 × 200 기준으로 설계한 풀을 Data Mask가 480 × 480인 VT(Get Hardware response로 확인)에 맞추면 배율은 2.4다. (10, 20)에 놓인 120 × 30 오브젝트는 (24, 48)의 288 × 72가 된다.
  - 배율은 480 ÷ 200 = 2.4다. 위치는 10 × 2.4 = 24, 20 × 2.4 = 48이고, 크기는 120 × 2.4 = 288, 30 × 2.4 = 72다.

### 폰트 고르기

- VT가 반드시 갖춘 폰트는 6 × 8 하나뿐이다. 나머지 크기는 VT마다 다르므로 Get Text Font Data response로 확인한다(전체 목록은 3절).
- Font size는 고정폭 폰트 15종에 붙인 번호다. 0이 6 × 8, 9가 48 × 64, 14가 128 × 192다.
- 폰트도 같은 배율이면 24 × 32가 57.6 × 76.8 영역이 된다. 표준은 best-fit 알고리즘을 정의하지 않으므로 여기서는 "폭과 높이를 넘지 않는 가장 큰 지원 폰트"로 고른다고 가정한다. 그러면 48 × 64(Font size 9)이고, VT가 Get Text Font Data response에서 32 × 32까지만 보고했다면 32 × 32다.
- 반대로 480 기준 풀을 200 VT로 줄이면 12 × 16이 5 × 6.7이 되어 하한인 6 × 8을 쓴다. 이때 글자가 필드 가장자리에서 잘리거나 이웃 글자와 겹칠 수 있다.

### Soft Key designator는 가로와 세로 배율이 다를 수 있다

- Soft Key designator 크기는 Get Number of Soft Keys response의 X Dots·Y Dots로 알 수 있고([30장](/study/isobus/30-vt-display-technical-data)), 최소 60 × 32(v6+는 60 × 60)다. v6+는 "VT 버전 6 이상"을 줄여 쓴 것이다.
- Data Mask와 달리 정사각형이 아니라 X와 Y의 배율이 다를 수 있다. 60 × 32 기준 디자인을 80 × 80 designator에 맞추면 1.33배와 2.5배다.
- 표준은 이때 축을 따로 스케일할지 정하지 않고, 크기와 폰트를 따로 스케일하면 잘림이나 겹침이 생길 수 있다고만 경고한다. 두 배율 중 작은 쪽으로 맞추는 편이 안전하다. 표준이 정한 방법은 아니고, 잘림을 피하려는 추론이다.

::: details 파이썬으로 좌표·합성·스케일 계산 검산해 보기
1~2절의 좌표 덧셈, 알파 합성, 배율, 폰트 고르기와 5절의 Window Cell·아이콘 크기를 한 번에 검산하는 코드다. `best_fit`은 위에서 가정한 "넘지 않는 가장 큰 폰트" 규칙이다.

```python
import math

# 4.6.12 상대 좌표 → 절대 좌표: 위치는 부모 레코드에 들어 있다
chain = [(20, 40), (10, 5)]          # Data Mask 안 Container 위치, Container 안 Input Number 위치
assert tuple(map(sum, zip(*chain))) == (30, 45)


# 4.6.13 알파 합성(v6): 아래에서 위로 한 겹씩 계산한다
def blend(src, dst, alpha):
    return src * alpha / 255 + dst * (255 - alpha) / 255


assert int(blend(128, 255, 128)) == 191     # 흰 배경 위 50 % 회색
assert int(blend(128, 0, 128)) == 64        # 검정 사각형 위 50 % 회색
assert blend(0, 191, 255) == 0              # 불투명한 위 오브젝트는 섞이지 않는다

# 4.6.16 스케일링: 200x200으로 설계한 풀을 480x480 VT에 맞춘다
k = 480 / 200
assert (round(10 * k), round(20 * k), round(120 * k), round(30 * k)) == (24, 48, 288, 72)

FONTS = [(6, 8), (8, 8), (8, 12), (12, 16), (16, 16), (16, 24), (24, 32), (32, 32),
         (32, 48), (48, 64), (64, 64), (64, 96), (96, 128), (128, 128), (128, 192)]


def best_fit(w, h, supported):
    """예시 규칙(표준은 알고리즘을 정하지 않는다): 폭·높이를 넘지 않는 가장 큰 폰트."""
    fits = [f for f in supported if f[0] <= w and f[1] <= h]
    return max(fits, key=lambda f: f[0] * f[1]) if fits else (6, 8)  # 6x8 하한


assert best_fit(24 * k, 32 * k, FONTS) == (48, 64)                    # Font size 9
assert best_fit(24 * k, 32 * k, FONTS[:8]) == (32, 32)               # 큰 폰트 미지원 VT
assert best_fit(12 * 200 / 480, 16 * 200 / 480, FONTS) == (6, 8)     # 축소 시 6x8 하한

# Soft Key designator: 60x32로 설계 → VT가 80x80을 보고(X·Y 배율이 다르다)
assert (round(80 / 60, 3), 80 / 32) == (1.333, 2.5)

# 4.7.5 Window Cell 크기(내림)와 4.7.15.3 Window Icon 영역(셀 높이의 90 %, 내림)
for side, cell, icon in [(200, (100, 33), 29), (480, (240, 80), 72), (800, (400, 133), 119)]:
    c = (side // 2, side // 6)
    assert c == cell
    assert math.floor(c[1] * 0.9) == icon
assert (100 * 2, 33 * 2) == (200, 66)        # 200x200에서 2x2 Window Mask

# 4.7 Figure 30: Key 안 구현체 식별 아이콘 = designator 높이의 60 %(내림), 정사각형
assert math.floor(32 * 0.6) == 19 and math.floor(80 * 0.6) == 48

print("배치·스케일 계산 검산 통과")
```

실행하면 마지막 줄에서 `배치·스케일 계산 검산 통과`가 출력된다. 계산이 하나라도 어긋나면 그 줄의 `assert`에서 멈춘다.
:::

정리하면, 스케일은 거의 모두 WS가 하고 VT는 Picture Graphic과 표준 창만 맡는다. 폰트는 VT가 실제로 가진 크기 중에서 골라야 한다.

<small>근거: ISO 11783-6 4.5.3, 4.6.16, 4.7.6, 4.7.11, B.1, C.2.1, D.5, D.7</small>

## 3. 글자와 도형을 그리는 규칙 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

이 절은 VT가 글자(폰트)와 선, 채우기를 실제 픽셀로 옮기는 규칙을 모았다. 같은 풀이 VT마다 몇 픽셀씩 다르게 보이는 이유가 여기에 있다.

### 폰트 렌더링

- 고정폭 폰트(모든 글자의 폭이 같은 폰트)는 Font size 0 = 6 × 8부터 14 = 128 × 192까지 15종이다. VT에 꼭 있어야 하는 것은 6 × 8 normal(스타일 없는 보통 글자)뿐이고, 나머지 크기와 스타일은 Get Text Font Data response의 Byte 6·7(크기 비트마스크)과 Byte 8(스타일)로 확인한다.
- 스타일을 켜도 글자는 폰트 상자를 넘으면 안 된다. 표준의 예로, 8 × 10 폰트의 bold italic도 8 × 10 안에 들어가야 한다.
- Font style 비트는 다음과 같다.

| 비트 | 스타일 |
|---|---|
| 0 | Bold(굵게) |
| 1 | Crossed out(취소선) |
| 2 | Underlined(밑줄) |
| 3 | Italic(기울임) |
| 4 | Inverted(글자색과 배경색 뒤집기) |
| 5 | 반전 깜빡임 |
| 6 | 숨김 깜빡임(5보다 우선) |
| 7 | 비례폭 렌더링(v4+) |

- <strong>비례폭(proportional)</strong>은 글자마다 폭이 다른 폰트로, v4+ VT의 선택 기능이다.
  - Font style bit 7이 1이면 Font size는 크기 코드가 아니라 높이 픽셀 값(8~N)이 되고, 폭은 글자마다 다르다. N은 Get Text Font Data response가 보고한 가장 큰 고정폭 폰트의 높이다.
  - 예를 들어 Byte 6 = `10`(16 × 24), Byte 7 = `02`(48 × 64)이면 가장 큰 폰트가 48 × 64라 N = 64이고, 비례폭 높이는 8~64를 1픽셀 단위로 쓸 수 있다.
  - 비례폭을 지원하지 않는 VT에 비례폭 Font Attributes가 든 풀을 보내면 풀이 거부되고, Change Font Attributes로 요청하면 오류 응답이 온다. 그래서 WS는 쓰기 전에 지원 여부를 먼저 물어야 한다(shall).
- 정렬(Justification)의 bit 0~1은 수평(0 왼쪽, 1 가운데, 2 오른쪽), bit 2~3은 수직(0 위, 1 가운데, 2 아래, v4+)이다. v4부터는 픽셀 단위로 정렬한다.
  - 왼쪽: 앞 공백을 지우지 않는다. 자동 줄바꿈이 없으면 넘친 부분이 오른쪽에서 잘린다.
  - 가운데: 앞뒤 공백을 모두 지우고 픽셀 단위로 가운데 맞춘다. 넘치면 양쪽이 잘린다.
  - 오른쪽: 뒤 공백을 지운다. 넘치면 왼쪽이 잘린다.
  - 자동 줄바꿈이면 줄마다 같은 규칙을 쓰고 빈 줄은 지우지 않는다. 입력 중에는 VT가 정렬을 미뤄도 된다.
- 자동 줄바꿈(Options bit 1)은 다음 글자에서 끊을 곳을 찾는다.
  - 공백 `0x20`(=32)
  - soft hyphen `0xAD`(=173): 평소에는 보이지 않고, 그 자리에서 실제로 줄이 나뉠 때만 보인다.
  - hyphen `0x2D`(=45): Wrap on Hyphen 비트가 켜졌을 때만
  - 끊을 곳이 없으면 마지막으로 온전히 보이는 글자 뒤에서 끊는다. 다음 줄 첫머리의 공백은 지운다. NBSP(`0xA0`(=160), 줄을 나누지 않는 공백)는 일반 글자처럼 다룬다.
- 제어 문자(v4+): CR(Carriage Return, 줄 처음으로), LF(Line Feed, 다음 줄로), CRLF는 한 번의 줄 끝이고 LFCR은 줄 끝 두 번이다. BS(백스페이스)처럼 문자 표에서 표시 대상이 아닌 문자는 무시한다(문자 표는 [35장](/study/isobus/35-vt-pool-transfer-charset)). `0x00`(WideString은 `0x0000`)을 만나면 정의된 길이보다 앞이어도 거기서 표시를 끝낸다.
- 렌더링 정확도: Output Meter(바늘 계기)의 바늘 모양, 막대그래프의 눈금, 비스듬한 선의 그리기 알고리즘은 VT 재량이라 VT마다 픽셀 단위로 같지 않다. 픽셀 단위 일치가 필요하면 Width = Actual width인 Picture Graphic을 쓴다. 표시 폭(Width)을 원본 그림 폭(Actual width)과 같게 두면 VT가 그림을 늘이거나 줄이지 않기 때문이다.

### 선과 채우기

- 점은 정사각형 붓(점이 붓의 왼쪽 위)이나 선 방향으로 돌린 붓으로 찍고, 안티에일리어싱(경계를 부드럽게 보이도록 중간색을 섞는 처리)도 허용된다.
- 라인 아트 패턴(선에 넣는 점선 무늬)을 꼭짓점을 지나며 이어 갈지(continuous) 새로 시작할지(restarting)는 VT가 고른다. 시작점은 일관되게 잡는 것이 권고다. 다각형은 첫 점, 사각형은 좌상단, 타원은 시작 각이다.
- 채우기는 flood fill·boundary fill(경계를 만날 때까지 번져 나가며 칠하는 방식)이 아니라 <strong>scan-line 방식이어야 한다</strong>(shall). scan-line은 가로줄 하나씩 안쪽 구간을 계산해 칠하는 방식이다. 번져 나가는 방식은 겹친 오브젝트가 경계를 끊을 수 있고 성능도 나쁘다. 테두리에 해당하는 픽셀은 빼고 내부만 채운다.
- 패턴 채우기는 Picture Graphic 원본을 스케일 없이 쓰고, 패턴 좌상단을 VT의 물리 Data Mask(또는 해당 designator, User-Layout Window Mask) 좌상단에 고정해 가로와 세로로 반복한다. 그래서 서로 다른 오브젝트의 무늬가 어긋나지 않고 이어진다. 투명·깜빡임 옵션은 무시한다.

정리하면, 글자와 도형은 VT마다 몇 픽셀씩 다를 수 있다. 픽셀까지 같아야 하는 그림은 Picture Graphic으로 만든다.

<small>근거: ISO 11783-6 4.6.19.2~4.6.19.6, 4.6.20, 4.6.21, B.10.1, B.14.2, D.7</small>

## 4. VT가 지원하지 않는 오브젝트

이 절에서는 VT가 지원하지 않는 오브젝트가 풀에 섞여 있을 때 어떻게 되는지 본다. VT는 버전과 제조사마다 지원하는 오브젝트가 다르므로, WS가 VT마다 풀을 따로 만들지 않으려면 이 규칙이 필요하다.

쉽게 말하면 모르는 단어가 섞인 편지를 받아도 끝까지 읽어 내고 그 단어만 건너뛰는 것과 같다. 다만 편지를 쓰는 쪽(WS)은 받는 쪽이 아예 읽을 수 없는 새 문법(더 높은 버전의 오브젝트)으로 써서는 안 된다.

- 원칙은 <strong>"파싱은 하되 기능은 지원하지 않는다"</strong>이다. 파싱(parsing)은 바이트열을 레코드 하나하나로 나누고 뜻을 읽어 내는 일이다.
  - VT는 표준에 정의된 모든 오브젝트 종류([32장의 오브젝트 종류 표](/study/isobus/32-vt-object-pool-basics) 참고)를 기능 지원 여부와 상관없이 파싱할 수 있어야 한다.
  - v4+ VT는 지원 목록에 없는 비고유 오브젝트(제조사가 따로 정의한 것이 아닌 표준 오브젝트)도 파싱해야 한다.
  - 덕분에 WS는 같은 풀을 여러 VT에 그대로 쓸 수 있다.
- 다만 WS가 보낼 수 있는 오브젝트는 Get Memory response가 보고한 VT 버전과 호환되는 것까지다. v4 VT에 v6 오브젝트인 Colour Palette(Type 45)를 보내면 안 된다.
- WS는 지원하지 않는 오브젝트에 명령을 보내지 않는 것이 권고다(should). 보내면 VT는 0이 아닌 오류 코드로 응답하며, 구체적인 값은 VT 설계에 따라 다르다. 표준이 드는 예는 Graphics Context를 지원하지 않는 VT에 Change Background Colour를 보내 오류 응답을 받는 경우다.
- 지원 목록은 Get Supported Objects 메시지로 묻는다([30장](/study/isobus/30-vt-display-technical-data)).
- 오브젝트별 규칙도 있다.
  - 지원하지 않는 window type의 Window Mask는 파싱한 뒤 무시하고 오류를 내지 않는다(5절).
  - Graphics Context(WS가 운영 중에 직접 그림을 그리는 캔버스 오브젝트)를 지원하지 않는 VT는 그것을 NULL을 가리키는 Object Pointer처럼 다룬다. 그리지 않지만 열린 Input List에서 선택할 수 있는 자리는 차지한다.
  - 제조사 정의 오브젝트(240~254)는 제조사 코드가 다른 VT에 보내지 않는 것이 권고다.

정리하면, VT는 모르는 오브젝트도 읽고 넘어가지만, WS는 VT 버전보다 새로운 오브젝트를 보내지 말고 지원하지 않는 오브젝트에 명령을 보내지 않아야 한다.

<small>근거: ISO 11783-6 4.6.28, 4.7.1.2, A.1, A.1.1, B.18, D.14</small>

## 5. User-Layout: 여러 Working Set을 한 화면에

평소 VT 화면에는 활성 WS 하나의 Data Mask만 보인다. User-Layout은 운전자가 여러 WS의 작은 창(Window Mask)과 키 묶음(Key Group)을 골라 한 화면에 모아 보는 기능이다. 예를 들어 파종기의 작업 속도와 분무기의 탱크 잔량을 한 화면에 나란히 놓을 수 있다.

쉽게 말하면 스마트폰 홈 화면에 여러 앱의 위젯을 모아 두는 것과 비슷하다. 칸을 나누고 배치를 정하는 것은 홈 화면(VT)이고, 위젯 안의 내용(창 안의 값)은 각 앱(WS)이 채운다. 위젯과 다른 점도 있다. 창 크기는 픽셀이 아니라 정해진 칸 단위로만 정해진다.

이 절에서 쓰는 말은 다음과 같다.

- Window Mask: WS가 User-Layout에 내놓는 작은 창 오브젝트
- Key Group: WS가 User-Layout의 소프트키 영역에 내놓는 Key 1~4개 묶음
- Window Cell: User-Layout 화면을 2열 × 6행으로 나눈 한 칸

![User-Layout 화면: 2열 6행 Window Cell 격자 위에 2x1, 1x2, 1x1, 2x2 Window Mask가 배치되고 한 셀은 비어 배경색으로 남은 User-Layout Data Mask와, Key 1개·2개·3개짜리 Key Group이 Key Cell에 놓인 User-Layout Soft Key Mask](/images/study-isobus/16-user-layout-grid-light.png)
![User-Layout 화면: 2열 6행 Window Cell 격자 위에 2x1, 1x2, 1x1, 2x2 Window Mask가 배치되고 한 셀은 비어 배경색으로 남은 User-Layout Data Mask와, Key 1개·2개·3개짜리 Key Group이 Key Cell에 놓인 User-Layout Soft Key Mask](/images/study-isobus/16-user-layout-grid-dark.png)

그림 왼쪽은 User-Layout Data Mask다. 2열 × 6행 칸 위에 크기가 다른 Window Mask가 놓인다. 2x1은 폭 2칸, 높이 1칸이라는 뜻이다. 아무것도 놓지 않은 칸은 배경색으로 남는다. 오른쪽은 User-Layout Soft Key Mask로, Key 1개·2개·3개짜리 Key Group이 소프트키 칸에 놓인다.

### 최소 요구와 참여 방법

- User-Layout 전체가 v4+ 전용이고 선택 기능이다. 그래도 v4+ VT는 지원 여부와 상관없이 Window Mask와 Key Group을 <strong>파싱해야 한다</strong>.
- 지원한다면 최소한 free form(type 0) Window Mask는 지원해야 하고 나머지 window type은 선택이다.
- 지원하지 않는 type의 Window Mask는 파싱한 뒤 무시하며 오류를 내지 않고, 운전자 선택 목록에도 띄우지 않는다.
- 참여하려는 WS는 Window Mask·Key Group을 풀에 넣어 올리기만 하면 된다. 지원하지 않는 VT는 파싱 후 버리므로 풀을 VT별로 고칠 필요가 없다.

### User-Layout Data Mask와 Window Cell

- User-Layout Data Mask는 <strong>VT가 소유한</strong> 특수 Data Mask다. 개수 제한은 없고, VT는 운전자가 이 화면들로 들어갈 수단을 제공해야 한다. 크기는 표준 Data Mask와 같고 2열 × 6행의 Window Cell 격자로 나뉜다.
- 셀 크기는 폭 = Data Mask 폭 ÷ 2, 높이 = Data Mask 높이 ÷ 6이고 둘 다 내림한다. 200 × 200이면 100 × 33, 480 × 480이면 240 × 80, 800 × 800이면 400 × 133이다. 200 ÷ 6 = 33.3…을 내리면 33이 된다.
- Window Mask의 픽셀 크기는 차지한 셀 크기와 정확히 같아야 한다. 200 × 200에서 2 × 2 Window Mask는 200 × 66이다. 레코드의 Width(1~2)·Height(1~6)는 픽셀이 아니라 <strong>셀 칸 수</strong>이고 type 0일 때만 쓰인다.
- 배치는 운전자가 VT 고유 매핑 화면에서 정한다. VT는 셀에 맞지 않는 Window Mask를 고르지 못하게 막고, 고른 배치를 비휘발성 메모리(전원이 꺼져도 남는 메모리)에 저장했다가 다음 전원 투입 때 복원한다. 그 Window Mask를 제공한 WS가 없으면 셀은 배경색으로 비운다.
- Options bit 0(Available)이 0이면 매핑 목록에 나오지 않고, 이미 배치돼 있었다면 셀을 비운다. 이 상태는 런타임에 바뀔 수 있다.
- VT는 Window Mask의 바깥 1픽셀 둘레에 테두리를 그릴 수 있고, 그 테두리는 Window Mask 영역 <strong>안쪽</strong>에 그린다(그릴지는 VT 재량). 그래서 type 0이면 자식을 가장자리 1픽셀에 붙이지 않는 것이 권고다. 영역 밖 픽셀은 잘린다.

### Window Mask 레코드: type 1 예제 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

window type 0은 WS가 자식을 직접 배치하는 free form이고, 1~18은 VT가 배치와 모양을 정하는 표준 창이다. type 1(1 × 1 Numeric Output Value with Units, 값과 단위를 보여 주는 한 칸짜리 창)은 참조 2개(#1 Output Number = 값, #2 Output String = 단위)를 받고, VT는 제목 11자, 값 5자, 단위 5자를 보여 줘야 한다.

아래 표는 [33장](/study/isobus/33-vt-object-records)의 예제 풀에서 Window Mask에 잡아 둔 ID 100으로 만든 레코드다. Byte 번호는 1부터 센다. 2바이트 값은 리틀 엔디언이라 낮은 자리 바이트가 먼저 온다. 예를 들어 `64 00`은 0x0064 = 100이다.

| Byte | hex | 필드 | 값 |
|---|---|---|---|
| 1~3 | `64 00 22` | Object ID, Type | 100, Window Mask(34) |
| 4~5 | `01 01` | Width, Height(셀 수) | type 0에서만 쓰인다 |
| 6 | `01` | Window Type | 1 |
| 7 | `00` | Background Colour(AID 1) | type 1 이상이면 VT가 무시 |
| 8 | `01` | Options(AID 2) | bit 0 Available = 1, bit 1 Transparent = 0 |
| 9~10 | `65 00` | Name(AID 3) | Output String 101: 매핑 화면에 쓰는 이름(VT는 20자 이상 표시) |
| 11~12 | `66 00` | Window Title | Output String 102: type 0이면 NULL이어야 한다 |
| 13~14 | `67 00` | Window Icon | Picture Graphic 103: type 1 이상이면 필수 |
| 15 | `02` | 참조 수 | 2 |
| 16 | `00` | 자식 수 | type 1 이상이면 0 |
| 17 | `00` | 매크로 수 | 0 |
| 18~21 | `68 00 69 00` | 참조 | Output Number 104, Output String 105 |

첫 세 바이트 `64 00 22`는 Object ID 0x0064 = 100과 Type `22`(=34) = Window Mask다. 마지막 `68 00 69 00`은 참조 두 개로, 0x0068 = 104(값을 보여 줄 Output Number)와 0x0069 = 105(단위를 보여 줄 Output String)다.

- 이벤트(그 일이 일어날 때 매크로를 실행할 수 있는 시점): On Show·On Hide(VT On User-Layout Hide/Show message에 Show·Hide를 담아 보낸다), On Refresh, On Change Background Colour, On Change Child Location·Position, On Change Attribute, On Pointing Event press·release(free form만).
- AID(Attribute ID, Change Attribute로 바꿀 때 쓰는 속성 번호): Background Colour(1), Options(2), Name(3).
- type 1 이상에서 VT는 배치, 색, 폰트를 직접 정하고 참조 오브젝트의 서식 속성을 무시할 수 있다. 그래도 숫자·문자열 필드의 최소 글자 수는 보여야 하고, 숫자의 스케일·서식 속성(Options bit 1~3, 변수 참조, Value, Offset, Scale, Number of decimals, Format)은 지켜야 한다. Window Title과 Window Icon 중 적어도 하나는 반드시 표시한다.
- Window Icon 영역은 셀 높이의 90 %(내림)인 정사각형이다. 200 × 200이면 29 × 29, 480 × 480이면 72 × 72다. WS는 아이콘을 이 크기로 미리 스케일하거나 런타임에 Width로 맞춘다. 아이콘이 영역보다 크면 VT가 가운데 맞추고 잘라내며, 작으면 VT가 원하는 곳에 놓는다(가로와 세로를 따로 판단). 셀·아이콘 계산은 2절 끝의 검산 코드에 함께 넣었다.
- 바 그래프가 든 표준 창(type 7, 16)에서 VT는 Min·Max가 표시 단위라고 가정할 수 없으므로 눈금에 값을 적지 않는 것이 권고다.

### Key Group과 User-Layout Soft Key Mask

- User-Layout Data Mask마다 User-Layout Soft Key Mask가 정확히 하나 있다. Key Cell(Key Group의 Key가 놓이는 소프트키 칸) 수는 VT가 정하되 최대 64개이고, 물리 Soft Key보다 많으면 Soft Key Mask와 같은 페이징(여러 쪽으로 넘겨 보기)을 제공한다. Key Cell 하나는 일반 Soft Key designator와 같은 크기다.
- Key Group은 Key(또는 Key를 가리키는 Object Pointer) 1~4개의 묶음이다. 포인터를 따라간 뒤 Key가 4개를 넘으면 안 된다. 운전자는 묶음을 쪼개 배치할 수 없고 페이지 경계를 넘겨서도 안 된다.
- 레코드 예: `78 00 23 03 79 00 FF FF 01 00 7A 00` → Object ID 120, Type 35, Options(1) = `03`(Available + Transparent), Name(2) = Output String 121, Key Group Icon = NULL(VT 고유 표현), Key 수 1, 매크로 0, Key 122.
  - 앞에서부터 풀면 `78 00` = 0x0078 = 120, `23` = 35(Key Group), `03` = Options(bit 0 Available과 bit 1 Transparent가 켜짐), `79 00` = 121, `FF FF` = NULL(가리키는 오브젝트가 없다는 뜻의 ID 65535), `01` = Key 1개, `00` = 매크로 0개, `7A 00` = 122다.
- Transparent(bit 1)를 켜면 VT는 자식 Key들의 배경색을 무시하고 스스로 정한다. 모든 키의 배경을 통일하려는 것이라 투명이 권고다. 반대로 Key Group Icon에는 투명 배경을 쓰지 않는 것이 권고다. 매핑 화면의 배경색을 설계자가 모르기 때문이다.
- 키가 어느 WS 것인지 알아보게 해야 한다. 같은 화면에 "STOP" 키가 셋이면 운전자가 헷갈린다. 표준은 designator 높이의 60 %(내림) 크기 정사각형 식별 아이콘을 왼쪽 아래에 두는 배치를 권한다. 60 × 32 designator면 19 × 19, 80 × 80이면 48 × 48이다.
- 이벤트는 On Change Attribute 하나이고, AID는 Options(1), Name(2)이다. 자식 Key의 스케일은 WS 몫이다.
- Window Mask는 특정 Key Group이 화면에 있다고 가정하면 안 된다. 무엇을 배치할지는 운전자가 정하기 때문이다.

### 입력과 화면 갱신

- User-Layout Data Mask가 표시 중이면 어느 WS가 보낸 Select Input Object 명령(입력 칸을 고르는 명령)도 실행되지 않고 오류 응답이 간다. 마스크 소유자가 VT이기 때문이다. 내비게이션 순서(입력 칸 사이를 옮겨 다니는 순서)는 VT가 정한다.
- 입력 오브젝트 이벤트에 걸린 매크로는 실행된다. 하지만 그 WS가 활성 WS가 아니므로 눈에 보이는 효과가 없을 수 있다. 예를 들어 매크로의 Change Active Mask는 효과가 없다.
- 운전자가 Window Mask 안의 입력 오브젝트를 활성화하면 VT는 VT Status message의 Byte 2(활성 WS의 주소)를 `FF`, `FE` 또는 VT 자신의 SA(Source Address, 보낸 장치의 주소)로 바꾸고, VT On User-Layout Hide/Show message로도 WS에 알린다.
- 값 갱신은 WS 책임이다. 무엇이 화면에 보이는지는 VT Status가 아니라 <strong>VT On User-Layout Hide/Show message</strong>로 안다([39장](/study/isobus/39-vt-alarm-activation)). VT는 Window Mask·Key Group이 나타나거나 사라질 때마다 오브젝트별로 이 메시지를 보낸다. WS가 타임아웃되면 VT는 그 WS의 Window Mask·Key Group을 화면에서 지운다.
- VT는 Window Mask·Key Group을 User-Layout 밖의 비VT 화면과 영역(VT 기능 밖에서 제조사가 설계한 화면 등)에서도 쓸 수 있다. 그래서 WS는 VT Status의 SA와 상관없이 Hide/Show message를 보고 보이는 것을 갱신해야 한다.

### 새 Window Mask·Key Group을 올릴 때 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

런타임에 같은 타입의 새 오브젝트를 올리는 것은 표준이 허용한다(부분 갱신, [35장](/study/isobus/35-vt-pool-transfer-charset)). Window Mask·Key Group을 교체하면 VT는 아래 규칙에 따라 화면과 저장된 매핑을 고친다. 요점은 다음과 같다.

| 바뀐 내용 | VT 동작 |
|---|---|
| 외형만(배경색·옵션·자식 등) 또는 window type | 보이면 다시 그린다 |
| Available → not available | 보이면 그 영역을 배경색으로 비운다 |
| Window Mask 크기 축소 | 다시 그리고, 비게 된 셀은 비우고 저장된 매핑을 고친다 |
| Window Mask 크기 확대 | 지금 자리에서 늘어난 칸이 비어 있으면 매핑을 넓히고, 아니면 매핑에서 빼고 원래 셀을 비운다 |
| Key Group의 Key 수 감소 | 다시 그리고, 남는 키 자리를 비우고 매핑을 고친다 |
| Key Group의 Key 수 증가 | 같은 페이지에서 위치를 바꾸지 않고 들어갈 빈 자리가 있으면 넓히고, 없으면 매핑에서 빼고 원래 자리를 비운다 |

어떤 경우에도 다른 Key Group의 위치는 바뀌지 않는다.

정리하면, User-Layout은 VT가 소유한 화면에 여러 WS의 Window Mask와 Key Group을 운전자가 골라 놓는 기능이다. WS는 이 오브젝트들을 풀에 넣어 두고, Hide/Show message를 보고 화면에 보이는 것만 갱신하면 된다.

<small>근거: ISO 11783-6 4.7(4.7.1.2~4.7.16), B.19, B.20, H.20</small>

## 6. 색 제어: 색 번호가 실제 색이 되기까지

이 절에서는 오브젝트에 적힌 색이 화면의 실제 색이 되는 과정을 본다. 오브젝트의 색 속성(배경색, 글자색, 선 색 등)과 비트맵 픽셀 값은 RGB가 아니라 <strong>팔레트 인덱스(색 번호)</strong>다. 번호가 실제 색이 되기까지 단계가 몇 개 있고, WS는 그중 두 곳(Colour Map과 팔레트)을 바꿀 수 있다.

RGB는 빨강(R), 초록(G), 파랑(B) 세 성분의 세기로 색을 적는 방식이다. `FF0000`처럼 두 자리씩 R, G, B 순서로 끊어 읽는다. 여기에 불투명도 알파(A)를 앞에 붙이면 ARGB다.

쉽게 말하면 페인트 가게의 색 견본표와 같다. 주문서(오브젝트)에는 "12번"이라고만 적고, 견본표(팔레트)가 12번이 빨강이라고 알려 준다. 견본표를 바꾸면 주문서를 고치지 않아도 화면 전체 색이 한꺼번에 바뀐다. Colour Map은 주문서의 번호를 견본표에 넘기기 전에 다른 번호로 바꿔 적는 대조표다.

![색 해석 경로: 오브젝트 색 속성(인덱스 0~255)이 Colour Map(색 번호 → 다른 색 번호)과 WS 팔레트(표준 팔레트 또는 Colour Palette의 ARGB)를 거쳐 v6 알파 합성 후 화면 픽셀이 되고, Working Set Special Controls가 로드 직후 초기 선택을, Select Colour Map or Palette 명령이 운영 중 전환을 맡는 흐름](/images/study-isobus/16-colour-pipeline-light.png)
![색 해석 경로: 오브젝트 색 속성(인덱스 0~255)이 Colour Map(색 번호 → 다른 색 번호)과 WS 팔레트(표준 팔레트 또는 Colour Palette의 ARGB)를 거쳐 v6 알파 합성 후 화면 픽셀이 되고, Working Set Special Controls가 로드 직후 초기 선택을, Select Colour Map or Palette 명령이 운영 중 전환을 맡는 흐름](/images/study-isobus/16-colour-pipeline-dark.png)

색 번호는 다음 순서로 실제 색이 된다.

1. 오브젝트의 색 속성에서 색 번호(0~255)를 읽는다.
2. 이 WS가 Colour Map을 쓰고 있으면 번호를 Colour Map이 가리키는 번호로 바꾼다. 쓰지 않으면 그대로 둔다.
3. WS 팔레트에서 그 번호의 색(ARGB)을 찾는다. 기본은 표준 팔레트이고, v6에서는 Colour Palette로 다시 정의한 값이 쓰인다.
4. 알파가 255(불투명)보다 작으면 아래에 있는 색과 섞는다(1절의 합성식).
5. 그 결과가 화면 픽셀이 된다.

로드 직후 처음 쓸 Colour Map과 Colour Palette는 Working Set Special Controls(7절)가 정한다. 운영 중에 바꾸려면 Select Colour Map or Palette 명령을 보낸다([37장](/study/isobus/37-vt-command-details)). 아래 그림은 같은 단계를 예 세 개로 따라간 것이다.

![색 번호를 따라가는 예 세 개: 배경색 0은 Colour Map이 없으면 표준 팔레트 0번 000000 검정, 0과 1을 맞바꾸는 Colour Map을 거치면 1번 FFFFFF 흰색이 되고, 배경색 2는 v6 Colour Palette가 2번을 알파 80의 009900으로 다시 정의하면 아래 색과 섞인 반투명 초록이 된다](/images/study-isobus/34-colour-lookup-steps-light.png)
![색 번호를 따라가는 예 세 개: 배경색 0은 Colour Map이 없으면 표준 팔레트 0번 000000 검정, 0과 1을 맞바꾸는 Colour Map을 거치면 1번 FFFFFF 흰색이 되고, 배경색 2는 v6 Colour Palette가 2번을 알파 80의 009900으로 다시 정의하면 아래 색과 섞인 반투명 초록이 된다](/images/study-isobus/34-colour-lookup-steps-dark.png)

### 표준 팔레트

표준 팔레트는 256칸이고 그중 232~255의 24칸은 VT 고유다(VT 제조사가 정한다). 0~15는 이름 있는 16색이다.

| 번호 | 이름 | RGB | 번호 | 이름 | RGB |
|---|---|---|---|---|---|
| 0 | Black | `000000` | 8 | Grey | `999999` |
| 1 | White | `FFFFFF` | 9 | Blue | `0000FF` |
| 2 | Green | `009900` | 10 | Lime | `00FF00` |
| 3 | Teal | `009999` | 11 | Cyan | `00FFFF` |
| 4 | Maroon | `990000` | 12 | Red | `FF0000` |
| 5 | Purple | `990099` | 13 | Magenta | `FF00FF` |
| 6 | Olive | `999900` | 14 | Yellow | `FFFF00` |
| 7 | Silver | `CCCCCC` | 15 | Navy | `000099` |

RGB `009900`은 R = `00`, G = `99`, B = `00`으로 읽는다. 16진수 `99`는 153이라 중간 밝기의 초록이다. 나머지 칸은 다음 규칙을 따른다.

- 16~231은 웹 안전색 큐브(성분값 `00 33 66 99 CC FF`, 6 × 6 × 6 = 216색)를 오름차순으로 늘어놓은 것이다. 웹 안전색 큐브는 R, G, B를 각각 여섯 단계 중 하나로 고른 216가지 색이다.
  - 그래서 인덱스 = 16 + 36·r + 6·g + b(r, g, b는 0~5단계)로 계산된다. 표준이 이 식을 적어 둔 것은 아니고, 표의 배열에서 유도한 식이다.
  - 예를 들어 64는 64 − 16 = 48 = 36 × 1 + 6 × 2 + 0이라 (r, g, b) = (1, 2, 0)이다. 단계값으로 바꾸면 `33 66 00`이다.
- 앞 16색이 큐브 안에 한 번 더 나오므로 256색 모드도 고유한 색이 256개는 아니다. 예를 들어 0번 Black `000000`은 16번과 같은 색이다.
- v6부터 모든 칸에 알파가 있고 기본값은 255(불투명)다. 그래서 v5 이하와 그대로 호환된다.

### 색 깊이별 처리

VT마다 낼 수 있는 색의 수(색 깊이)가 다르다. 풀은 그 VT가 낼 수 있는 색만 써야 한다.

- 색 모드는 셋이다. 단색(유효 코드 0~1), 16색(0~15), 256색(0~255). 상위 모드를 지원하는 VT는 하위 모드도 지원해야 한다.
- VT의 모드는 Get Hardware response의 Byte 3(Graphic Type)으로 안다([30장](/study/isobus/30-vt-display-technical-data)).

| Graphic Type | 색 모드 | 쓸 수 있는 색 코드 | 쓸 수 있는 Picture Graphic |
|---|---|---|---|
| 0 | 단색 | 0·1 | 단색만 |
| 1 | 16색 | 0~15 | 단색·16색 |
| 2 | 256색 | 모든 색(0~255) | 모든 형식 |

- 따라서 16색 VT에 보내는 풀에는 색 코드 16 이상이나 Format 2(8비트) Picture Graphic이 있으면 안 된다. 전송 전에 VT에 맞춘 "깨끗한" 풀을 만들어야 하고, 무효 색이 든 풀을 보낸 뒤 명령으로 고치는 방식은 허용되지 않는다.
- v5 이하 VT는 16색·256색 모드를 회색조로 구현해도 된다.

정리하면, 오브젝트에는 색 번호만 적고 실제 색은 팔레트가 정한다. 풀에 넣는 색 번호와 그림 형식은 VT의 색 모드 안에 있어야 한다.

<small>근거: ISO 11783-6 4.8, A.3(Table A.4), C.2.1, D.9</small>

## 7. 색을 바꾸는 오브젝트와 투명

이 절에서는 WS가 색을 바꿀 때 쓰는 세 오브젝트와, 아래가 비쳐 보이게 하는 장치들을 본다. 6절의 단계에서 Colour Map은 2단계, Colour Palette는 3단계를 바꾸고, Working Set Special Controls는 처음에 어느 것을 쓸지 정한다.

| 오브젝트 | Type | 버전 | 하는 일 |
|---|---|---|---|
| Colour Map | 39 | v4·v5 선택, v6 필수 | 색 번호를 다른 색 번호로 바꾼다 |
| Colour Palette | 45 | v6부터 | 번호별 실제 색(ARGB)을 다시 정의한다 |
| Working Set Special Controls | 47 | v6부터 | 풀을 처음 그리기 전에 쓸 Colour Map과 Colour Palette를 정한다 |

### Colour Map: 색 번호를 다른 번호로 바꾸는 표(Type 39)

- v4·v5에서는 선택, v6에서는 필수다. 색 인덱스를 다른 인덱스로 바꾸는 표다. 풀에 여러 개 둘 수 있고, 로드 직후 VT는 기본 Colour Map을 쓴다. 바꾸려면 Select Colour Map or Palette 명령을 보낸다([37장](/study/isobus/37-vt-command-details)).
- 항목 수는 2, 16, 256 중 하나이고 VT 능력보다 적으면 안 된다. 많은 것은 괜찮다. 256칸 맵을 단색 VT에 보내면 VT는 0·1번만 쓴다.
- 레코드 예(16색 VT용, 0과 1을 맞바꿔 화면을 반전): `5A 00 27 10 00` + `01 00 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F` → Object ID 90, Type 39, 항목 수 16, 0번 → 1, 1번 → 0, 나머지는 그대로. 표준이 예로 드는 시나리오(색을 뒤집었다가 다시 되돌리는 예)다.
  - 앞에서부터 풀면 `5A 00` = 0x005A = 90, `27` = 39(Colour Map), `10 00` = 0x0010 = 16(항목 수)이다. 그다음 16바이트가 0번부터 15번까지의 "바꿀 번호"다. 첫 바이트 `01`은 "0번 색을 1번으로", 둘째 바이트 `00`은 "1번 색을 0번으로"라는 뜻이다.
- 이 WS의 풀에만 적용되고 다른 WS 화면은 바뀌지 않는다. 허용 명령은 Get Attribute Value뿐이라 맵 내용을 바꾸려면 오브젝트를 다시 보낸다.

### Colour Palette: 색 자체를 다시 정의하기(Type 45, v6)

- 0번부터 N개(최대 256)의 색을 ARGB로 다시 정의한다. 일부만 바꿀 수도 있지만 항상 0번부터 센다. 값은 리틀엔디언이라 바이트 순서가 <strong>B, G, R, A</strong>다.
  - 색 하나를 32비트 수 0xAARRGGBB로 생각하면 된다. 리틀 엔디언은 낮은 자리 바이트(BB)부터 보내므로 바이트로는 BB, GG, RR, AA 순이 된다.
- 레코드 예(0~2번 재정의, 2번 Green을 50 % 투명): `5B 00 2D 00 03 00` + `00 00 00 FF` + `FF FF FF FF` + `00 99 00 80` → Object ID 91, Type 45, Options 0(예약), 색 3개 = 불투명 검정, 불투명 흰색, α = `80`인 `009900`. 18바이트다.
  - 앞에서부터 풀면 `5B 00` = 91, `2D` = 45(Colour Palette), `00` = Options, `03 00` = 색 3개다. 세 번째 색 `00 99 00 80`은 B = `00`, G = `99`, R = `00`, A = `80`(=128)이므로 RGB `009900`(표준 2번 Green)에 알파 128이다.
  - 길이는 앞부분 6바이트 + 색 3개 × 4바이트 = 18바이트다.
- 풀 갱신으로 새 Colour Palette가 오면 VT는 그 WS의 팔레트를 먼저 표준 팔레트로 되돌린 뒤 새 값을 적용한다.
- AID는 Options(1, 예약)이고, 허용 명령은 Change Attribute와 Get Attribute Value다.
- 아래에 무엇이 깔릴지 설계자가 모르는 곳에는 투명을 쓰지 않는 것이 권고다. Data Mask 배경(그 아래 색을 모른다), External Object Pointer(다른 WS의 오브젝트를 자기 화면에 끌어와 보여 주는 오브젝트)로 다른 WS 화면에 참조될 수 있는 Button이 그 예다.

### Working Set Special Controls: 처음 쓸 색 표 고르기(Type 47, v6)

- 풀에 0개 또는 1개 둔다. 지정한 Colour Map과 Colour Palette를 풀을 처음 그리기 전에 활성화한다. NULL이면 각각 Colour Map 없음, 표준 팔레트다.
- "Number of bytes to follow"(뒤따르는 바이트 수) 필드로 확장할 수 있게 설계됐다. 길이를 앞에 적어 두므로 속성이 늘어나도 레코드 끝을 찾을 수 있다. 이 오브젝트나 AID 2 이상의 속성이 없으면 VT는 NULL과 같은 값으로 처리한다.
- 언어·국가 코드 쌍을 넣으면 Working Set 오브젝트의 언어 목록은 무시된다.
- 레코드 예: `5C 00 2F 09 00 5A 00 5B 00 01 6B 6F 4B 52` → Object ID 92, Type 47, 뒤따르는 9바이트, Colour Map 90, Colour Palette 91, 언어 쌍 1개 "ko"·"KR".
  - 앞에서부터 풀면 `5C 00` = 92, `2F` = 47, `09 00` = 뒤따르는 9바이트, `5A 00` = Colour Map 90, `5B 00` = Colour Palette 91, `01` = 언어 쌍 1개, `6B 6F` = ASCII "ko"(한국어), `4B 52` = ASCII "KR"(대한민국)이다. 9바이트는 2 + 2 + 1 + 2 + 2를 더한 값이다.
- v6 VT가 Select Colour Map or Palette 명령을 처리하면 이 오브젝트의 속성도 그에 맞게 갱신된다.

### 투명을 만드는 세 가지 장치

| 장치 | 효과 |
|---|---|
| Options의 Transparent 비트 | 오브젝트 배경을 칠하지 않아 아래가 비친다. Input String·Input Number·Output String·Output Number의 bit 0, Button bit 3, Window Mask bit 1 |
| Picture Graphic의 Transparency colour | Options bit 0이 1일 때 이 인덱스의 픽셀만 아래가 비친다 |
| 팔레트 알파(v6) | 색 자체가 반투명이라 겹친 영역이 섞인다(1절 합성식) |

Key Group의 Transparent 비트는 이름은 같지만 뜻이 다르다. 아래가 비치는 것이 아니라 VT가 자식 Key의 배경색을 무시하고 직접 정한다(5절). 채우기 패턴으로 쓰인 Picture Graphic은 투명 옵션을 무시한다(3절).

::: details 원문을 가진 독자를 위한 메모
표의 행별 근거 조항: Options의 Transparent 비트 B.7~B.9·B.19, Picture Graphic의 Transparency colour B.12.1, 팔레트 알파 4.6.13·B.26. Key Group의 Transparent 비트는 B.20, 채우기 패턴의 투명 무시는 4.6.21이다.
:::

::: details 파이썬으로 팔레트·Colour Map·Colour Palette 검산해 보기
6~7절의 표준 팔레트 계산, 세 레코드의 바이트 조립, 색 번호를 실제 색으로 푸는 과정을 검산하는 코드다. `resolve`가 6절의 1~3단계를 그대로 옮긴 함수다.

```python
LEVELS = [0x00, 0x33, 0x66, 0x99, 0xCC, 0xFF]
NAMED = ["000000", "FFFFFF", "009900", "009999", "990000", "990099", "999900", "CCCCCC",
         "999999", "0000FF", "00FF00", "00FFFF", "FF0000", "FF00FF", "FFFF00", "000099"]


def standard_rgb(i):
    """A.3 표준 팔레트(알파는 기본 FF). 232~255는 VT 고유라 None."""
    if i < 16:
        return NAMED[i]
    if i <= 231:
        r, g, b = (i - 16) // 36, (i - 16) // 6 % 6, (i - 16) % 6
        return "%02X%02X%02X" % (LEVELS[r], LEVELS[g], LEVELS[b])
    return None


# Table A.4에서 몇 칸을 골라 대조
assert standard_rgb(16) == "000000" and standard_rgb(21) == "0000FF"
assert standard_rgb(64) == "336600" and standard_rgb(128) == "9900CC"
assert standard_rgb(192) == "CCFF66" and standard_rgb(231) == "FFFFFF"
assert standard_rgb(232) is None
# 앞 16색은 큐브 안에 다시 나온다(NOTE: 256색 모드도 256개 고유색이 아니다)
assert all(NAMED[i] in {standard_rgb(j) for j in range(16, 232)} for i in range(16))


u16 = lambda v: v.to_bytes(2, "little")
argb = lambda a, r, g, b: bytes([b, g, r, a])   # 리틀엔디언 → B, G, R, A 순

# Colour Map(ID 90): 16색 VT용, 0과 1을 맞바꾼다(Figure 32)
cmap = [1, 0] + list(range(2, 16))
colour_map = u16(90) + bytes([39]) + u16(len(cmap)) + bytes(cmap)
assert colour_map.hex(" ").upper() == (
    "5A 00 27 10 00 01 00 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F")

# Colour Palette(ID 91, v6): 0~2번만 다시 정의, 2번(Green)을 50 % 투명으로
entries = [argb(0xFF, 0, 0, 0), argb(0xFF, 0xFF, 0xFF, 0xFF), argb(0x80, 0x00, 0x99, 0x00)]
palette = u16(91) + bytes([45, 0]) + u16(len(entries)) + b"".join(entries)
assert palette.hex(" ").upper() == (
    "5B 00 2D 00 03 00 00 00 00 FF FF FF FF FF 00 99 00 80")
assert len(palette) == 6 + 4 * 3

# Working Set Special Controls(ID 92, v6): 처음부터 Colour Map 90·Palette 91, 언어 ko-KR
body = u16(90) + u16(91) + bytes([1]) + b"ko" + b"KR"
wssc = u16(92) + bytes([47]) + u16(len(body)) + body
assert wssc.hex(" ").upper() == "5C 00 2F 09 00 5A 00 5B 00 01 6B 6F 4B 52"


def resolve(index, colour_map=None, ws_palette=None):
    """오브젝트 색 속성 → (Colour Map) → (WS 팔레트) → ARGB"""
    if colour_map is not None:
        index = colour_map[index]
    if ws_palette and index in ws_palette:
        return ws_palette[index]
    return "FF" + standard_rgb(index)


assert resolve(0) == "FF000000"
assert resolve(0, colour_map=cmap) == "FFFFFFFF"                  # 0이 흰색으로 보인다
assert resolve(2, ws_palette={2: "80009900"}) == "80009900"       # 2번만 반투명
print("색 계산 검산 통과")
```

실행하면 `색 계산 검산 통과`가 출력된다. 마지막 세 `assert`가 위 그림의 예 1~3과 같은 결과를 확인한다.
:::

정리하면, Colour Map은 번호를, Colour Palette는 번호의 실제 색을 바꾸고, Working Set Special Controls는 처음에 쓸 둘을 고른다. 투명은 배경을 칠하지 않는 비트, 그림의 투명색, 팔레트 알파 세 가지로 만든다.

<small>근거: ISO 11783-6 4.6.13, 4.6.21, 4.8, B.7~B.9, B.12.1, B.17, B.19, B.20, B.26, B.29, F.60</small>

::: tip 핵심 정리
- 오브젝트 위치는 부모 왼쪽 위를 (0, 0)으로 한 상대 좌표이고, 부모 레코드의 자식 목록에 들어 있다. 목록에서 나중에 나온 오브젝트가 위에 그려지고, 정해진 크기 밖은 픽셀 단위로 잘린다.
- 스케일은 원칙적으로 WS 몫이다. VT가 스스로 하는 것은 Picture Graphic과 표준 창(Window Mask type 1 이상)뿐이다.
- VT는 지원하지 않는 오브젝트도 파싱은 해야 하지만, WS는 VT 버전보다 새 오브젝트를 보내면 안 된다.
- User-Layout은 v4부터의 선택 기능이지만 Window Mask·Key Group 파싱은 의무이고, 화면에 보이는지는 VT On User-Layout Hide/Show message로 안다.
- 색 속성은 색 번호다. 번호 → Colour Map → WS 팔레트(표준 또는 v6 Colour Palette) 순으로 풀리고, VT 색 깊이를 넘는 색과 그림은 풀에 넣으면 안 된다.
:::

::: details 확인 문제
1. Data Mask 안 (30, 10)에 놓인 Container 속 (5, 20)에 Output String이 있다. 이 Output String은 화면의 어느 절대 좌표에 그려지는가? 같은 Container를 같은 Data Mask의 (30, 100)에도 넣으면 Output String은 어디에 한 번 더 보이는가?
2. 부모의 자식 목록에 A, B 순서로 나열된 두 오브젝트가 같은 자리에 겹친다. 어느 쪽이 위에 보이는가? B가 부모 영역 밖으로 10픽셀 튀어나가면 그 부분은 어떻게 되는가?
3. 배경색 속성이 12인 Output String이 있다. Colour Map과 Colour Palette를 쓰지 않으면 화면에 무슨 색이 보이는가? 12번을 0번으로 바꾸는 Colour Map을 쓰면 어떻게 되는가?
4. 480 × 480 VT의 User-Layout Data Mask에서 Window Cell 한 칸의 크기와, 폭 1칸·높이 2칸짜리 Window Mask의 픽셀 크기는 얼마인가?
5. (설계) 200 × 200, 256색 VT를 기준으로 만든 풀을 Data Mask 480 × 480, 16색(Graphic Type 1)인 v4 VT에 올리려 한다. 풀에는 Format 2(8비트) Picture Graphic과 색 코드 200을 쓰는 Fill Attributes, 그리고 Colour Palette(Type 45)가 있다. 전송 전에 무엇을 바꿔야 하는가?

**답 가이드**
1. (35, 30)이다. x는 30 + 5, y는 10 + 20으로 계산한다. 같은 Container를 (30, 100)에도 넣으면 (35, 120)에도 보인다. 위치가 자식이 아니라 부모 레코드의 목록에 있기 때문이다.
2. 목록에서 나중에 나온 B가 위에 보인다. 부모 밖으로 나간 10픽셀은 픽셀 단위로 잘려 보이지 않는다.
3. 표준 팔레트 12번 Red(`FF0000`)다. 12번을 0번으로 바꾸는 Colour Map을 쓰면 0번 Black(`000000`)으로 보인다. 이 Colour Map은 이 WS의 화면에만 적용된다.
4. 셀은 480 ÷ 2 = 240, 480 ÷ 6 = 80이라 240 × 80이다. 폭 1칸·높이 2칸이면 240 × 160이다.
5. 세 가지를 바꾼다.
   - (1) 위치와 크기를 2.4배로 스케일하고 폰트를 VT가 보고한 크기 중에서 best-fit으로 다시 고른다. Picture Graphic의 크기는 VT가 Width로 스케일하므로 Width만 맞추면 된다.
   - (2) 16색 VT는 Format 2 그림을 지원하지 않으므로 Format 1(4비트) 이하로 바꾸고, 색 코드 200은 0~15 중 하나로 바꾼다. 무효 색을 보낸 뒤 명령으로 고치는 것은 허용되지 않는다.
   - (3) Colour Palette는 v6 오브젝트라 v4 VT에 보내면 안 된다. 색 배치를 바꾸고 싶다면 Colour Map(16칸)을 쓰되, v4·v5에서는 선택 기능이므로 Get Supported Objects로 지원 여부부터 확인한다.
:::

## 다음 챕터

- 다음: [35장 오브젝트 풀 전송 심화와 문자 집합](/study/isobus/35-vt-pool-transfer-charset)
