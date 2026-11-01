---
title: "종합 실습 (3): grid, TimeLog, Point 바이너리"
description: "처방 맵을 grid 바이너리 파일로 만들어 위치로 셀 값을 찾고, TimeLog 헤더에 맞춰 작업 기록 레코드를 만들고 해독하며, Point 바이너리와 LINKLIST.XML 첨부 파일을 읽는다."
date: 2026-04-13
tags: [ISOBUS, ISOXML, TaskController, Binary, Python]
prev: /study/isobus/56-practice-isoxml
next: /study/isobus/appendix-glossary
---

# 종합 실습 (3): grid, TimeLog, Point 바이너리

::: info 학습 목표
- grid type 1과 type 2 바이너리 파일의 차이를 설명하고, GPS 좌표에서 셀 번호와 바이트 위치를 계산할 수 있다.
- TimeLog 헤더 XML만 보고 바이너리 레코드의 바이트 배치를 계산해 디코딩할 수 있다.
- 바이너리 파일을 읽을 때 흔한 실수(길이 어긋남, 배치 하드코딩, 정렬 패딩)를 피할 수 있다.
- Point 바이너리와 LINKLIST.XML이 무엇을 위해 있는지 설명할 수 있다.
:::

::: tip 시작하기 전에
- 먼저 읽을 장: [56장 종합 실습 (2)](/study/isobus/56-practice-isoxml), [55장 종합 실습 (1)](/study/isobus/55-practice-log-vt-tc)
- 이 장에서 처음 나오는 말
  - 바이너리 파일: 글자가 아니라 바이트 값을 그대로 담은 파일. 텍스트 편집기로 열면 깨져 보이고, 16진수 보기로 읽는다
  - grid: 밭을 같은 크기의 칸으로 나눈 격자. 칸마다 처방 값을 담는다
  - 셀(cell): 격자의 칸 하나
  - 리틀 엔디언: 여러 바이트로 된 값에서 낮은 자리 바이트를 먼저 적는 순서
  - 레코드: 바이너리 파일 안에서 같은 구조로 반복되는 한 덩어리
  - TimeLog: 시각, 위치, 측정값을 레코드로 쌓은 작업 기록 파일
:::

표 계산 프로그램의 표를 CSV로 저장하면 사람이 읽을 수 있지만 파일이 커진다. 바이너리 파일은 "칸의 순서와 크기만 미리 약속하고 값만 빽빽이 적은 장부"와 같다. 약속을 알아야 읽을 수 있고, 한 칸만 어긋나도 뒤가 모두 틀어진다. 태스크 파일 세트는 이 약속을 XML 쪽에 적고 값은 바이너리 파일에 담는다. 이 장에서는 그런 파일 세 가지(처방 맵 grid, 작업 기록 TimeLog, 정밀 좌표 Point)를 직접 만들고 읽는다.

::: info 실습 전체 준비물
- 파이썬 3. 기본 라이브러리(`struct`, `math`, `datetime`, `decimal`, `xml.etree`)만 쓴다.
- `struct` 한 줄 복습: `struct.pack("<i", 15000)`은 15000을 리틀 엔디언(`<`) 4바이트 부호 있는 정수(`i`)로 바꾼다. 이 장에 나오는 형식 문자는 `B`(u8), `H`(u16), `I`(u32), `i`(i32), `q`(i64)다. u는 부호 없는 정수, i는 부호 있는 정수이고, 숫자는 비트 수다(u16 = 2바이트).
- 만든 바이트를 파일로 저장해 16진수로 보고 싶다면 `open("GRD00001.BIN", "wb").write(t2)`처럼 저장한 뒤 터미널에서 `xxd GRD00001.BIN`으로 본다.
- 본문의 "(추론)"은 표준 문서에 직접 적힌 규칙이 아니라 이 글이 다른 규칙에서 끌어낸 판단이라는 표시다.
:::

## 1. 실습 1: 처방 맵을 grid 바이너리로

::: info 실습 안내
- 목표: 55장의 2×2 처방을 type 1과 type 2 grid 파일로 만들고, GPS 위치 다섯 개로 다시 읽어 같은 값이 나오는지 확인한다.
- 필요한 지식: [56장](/study/isobus/56-practice-isoxml) 4절과 6절(TSK, TZN, PDV, GRD 요소), [55장](/study/isobus/55-practice-log-vt-tc) 4절의 처방
- 준비물: 파이썬 3, 1.4절의 `grid_demo.py`
:::

grid의 셀 값은 바이너리 파일로만 정의할 수 있다. XML의 GRD 요소는 격자의 위치·크기·파일 이름만 적고, 셀 값은 `GRD00001.BIN`에 들어간다.

### 1.1 GRD가 정하는 격자와 셀 순서

GRD 요소의 속성은 다음과 같다. WGS84는 GPS가 쓰는 지구 좌표 기준이고, 위도·경도는 도(°) 단위다.

| 속성 | 뜻 | 형식 |
|---|---|---|
| `A` GridMinimumNorthPosition | 격자의 최소 북위 = 남쪽 모서리 | `xs:decimal`, −90~90, WGS84 |
| `B` GridMinimumEastPosition | 격자의 최소 동경 = 서쪽 모서리 | `xs:decimal`, −180~180 |
| `C` GridCellNorthSize | 셀 하나의 남북 크기(도) | `xs:double`, 0~1 |
| `D` GridCellEastSize | 셀 하나의 동서 크기(도) | `xs:double`, 0~1 |
| `E` GridMaximumColumn | 동쪽 방향 셀 개수 | 0~2³²−1 |
| `F` GridMaximumRow | 북쪽 방향 셀 개수 | 0~2³²−1 |
| `G` Filename | `GRD` + 5자리 숫자 | `xs:ID`, 8자 |
| `H` Filelength | 셀 파일 길이(바이트) | 선택 |
| `I` GridType | 1 또는 2 | 필수 |
| `J` TreatmentZoneCode | type 2의 템플릿 TZN 코드 | 선택 |

셀 순서는 표준이 정해 두었다. 최소 북·동 위치(원점)의 셀에서 시작해 같은 행 안에서 동쪽으로 열 번호가 올라가고, 행이 끝나면 북쪽 다음 행의 맨 서쪽 열에서 다시 시작한다. 책을 읽을 때 한 줄을 왼쪽에서 오른쪽으로 읽고 다음 줄로 넘어가는 것과 같은데, 줄이 아래가 아니라 위(북쪽)로 쌓인다는 점만 다르다. 표준 문서의 그림도 원점을 격자 남서 모서리에 두고, 셀 0(row 0, column 0)을 남서쪽 끝 셀로, 14번째 셀(row 0, column 13)을 같은 행 동쪽 끝 셀로 그린다. 셀 자체에는 순서 정보가 없으므로 격자는 빠짐없는 오름차순 배열이어야 한다.

이 규칙을 식으로 쓰면 다음과 같다. `floor`는 소수점 아래를 버리는 내림이다.

```
row    = floor((위도 - A) / C)        0 <= row < F 일 때만 격자 안
col    = floor((경도 - B) / D)        0 <= col < E 일 때만 격자 안
index  = row * E + col
offset = index * (셀당 바이트)
```

![2×2 격자에서 남서 모서리 원점(A, B)부터 셀 0·1(row 0)을 동쪽으로, 이어서 셀 2·3(row 1)을 읽는 순서와, 같은 처방을 type 1(셀당 1바이트 TZN 코드 01 02 03 04)과 type 2(셀당 int32 리틀 엔디언 16바이트)로 담은 바이트 배치](/images/study-isobus/22-grid-cell-order-light.png)
![2×2 격자에서 남서 모서리 원점(A, B)부터 셀 0·1(row 0)을 동쪽으로, 이어서 셀 2·3(row 1)을 읽는 순서와, 같은 처방을 type 1(셀당 1바이트 TZN 코드 01 02 03 04)과 type 2(셀당 int32 리틀 엔디언 16바이트)로 담은 바이트 배치](/images/study-isobus/22-grid-cell-order-dark.png)

왼쪽 그림은 이 실습의 2×2 격자다. 주황색 화살표가 파일 안의 셀 순서(셀 0 → 1 → 2 → 3)다. 오른쪽은 같은 처방을 type 1과 type 2 파일로 담은 바이트다. 위치 하나로 값을 찾는 과정을 단계별로 따라가면 아래와 같다.

![GPS 위치 37.5015, 127.0005에서 원점을 빼고 셀 크기로 나눠 내림해 row 1, col 0을 얻고, 셀 번호 2와 type 2 바이트 위치 8을 거쳐 바이트 10 27 00 00을 10000으로 읽어 100 kg/ha를 얻는 여섯 단계](/images/study-isobus/57-gps-to-cell-lookup-light.png)
![GPS 위치 37.5015, 127.0005에서 원점을 빼고 셀 크기로 나눠 내림해 row 1, col 0을 얻고, 셀 번호 2와 type 2 바이트 위치 8을 거쳐 바이트 10 27 00 00을 10000으로 읽어 100 kg/ha를 얻는 여섯 단계](/images/study-isobus/57-gps-to-cell-lookup-dark.png)

### 1.2 type 1과 type 2

grid 파일은 두 종류다. type 1은 칸마다 "몇 번 구역인지"만 적고, type 2는 칸마다 값 자체를 적는다.

| 항목 | type 1 | type 2 |
|---|---|---|
| GRD `I` / `J` | 1 / 없음 | 2 / 템플릿 TZN 코드 |
| 셀 값 | 그 셀이 속한 TZN 코드 1개(unsigned 8-bit) | 템플릿 TZN의 PDV마다 값 1개(signed 32-bit) |
| 셀당 크기 | 1바이트 | 4 × 템플릿 PDV 수 |
| 처방 값이 있는 곳 | XML의 TZN·PDV(구역 수만큼) | 바이너리(XML TZN은 틀만) |
| 맞는 경우 | 처방이 몇 단계 구역으로 나뉠 때. grid가 TZN 조회표 역할 | 셀마다 값이 달라 구역으로 묶이지 않을 때 |
| 바이트 순서 | 1바이트라 없음 | ISO 11783-6과 같은 규칙 = 리틀 엔디언 |

두 type 모두 TZN 하나에 PDV 여러 개를 넣어 여러 변수를 위치 기반으로 함께 제어할 수 있다. type 2의 레코드는 템플릿 TZN에 정의한 PDV 순서대로 값이 이어진다. 표준 문서의 type 2 예제는 템플릿 PDV가 DDI 0001·0006·001A 세 개라서 셀마다 12바이트이고, 첫 셀의 값 (11100)(15000)(190)은 `5C 2B 00 00 98 3A 00 00 BE 00 00 00`이다. 11100은 16진수로 0x00002B5C이고, 리틀 엔디언이라 낮은 자리 `5C`부터 `5C 2B 00 00`으로 적는다. 15000(0x3A98)과 190(0xBE)도 같은 방식이다.

같은 처방을 type 1로 쓰면 템플릿 대신 값마다 TZN을 하나씩 두고 바이너리에는 코드만 남긴다. TZN 0(기본값)과 TZN 9(필드 밖)는 56장 6절과 같다.

```xml
<TZN A="1" B="150 kg/ha"><PDV A="0006" B="15000" C="PDT1" E="VPN1"/></TZN>
<TZN A="2" B="200 kg/ha"><PDV A="0006" B="20000" C="PDT1" E="VPN1"/></TZN>
<TZN A="3" B="100 kg/ha"><PDV A="0006" B="10000" C="PDT1" E="VPN1"/></TZN>
<TZN A="4" B="180 kg/ha"><PDV A="0006" B="18000" C="PDT1" E="VPN1"/></TZN>
<GRD A="37.500" B="127.000" C="0.001" D="0.001" E="2" F="2"
     G="GRD00001" H="4" I="1"/>
```

이때 `GRD00001.BIN`은 `01 02 03 04` 네 바이트다. TC는 바이트 `03`을 읽으면 TZN 3을 찾아 그 안의 PDV 값 10000(100 kg/ha)을 쓴다.

### 1.3 크기 계산: 파일 길이와 셀의 실제 크기

- <strong>파일 길이</strong>는 E × F × 셀당 바이트다. 이 예제는 type 1이 2 × 2 × 1 = 4바이트, type 2(PDV 1개)가 2 × 2 × 4 = 16바이트이고, 이 값을 GRD `H`에 적는다. 셀에 순서 정보가 없으므로 길이가 한 바이트만 어긋나도 뒤의 모든 셀이 밀린다. 읽기 전에 파일 길이를 먼저 확인하는 편이 안전하다(추론).
- <strong>TC 쪽 상한</strong>: TC-GEO는 grid type 1·2 처리가 필수이고 최소 350행 × 350열을 지원해야 한다. 이 크기면 type 1은 122,500바이트, type 2는 PDV 1개일 때 490,000바이트, PDV 3개일 때 1,470,000바이트다. FMIS가 처방 해상도를 정할 때 이 범위 안에 두면 최소 사양 TC도 받을 수 있다(추론).
- <strong>각도 셀의 실제 크기</strong>: 위도 37.5° 부근에서 위도 1°는 약 110,987 m, 경도 1°는 약 88,424 m다(WGS84 근사식으로 계산한 값이고, 표준 문서에 있는 값은 아니다). 따라서 0.001° 셀은 남북 111.0 m × 동서 88.4 m, 약 9,814 m²(0.98 ha)다. 56장 6절의 필지 0.002° × 0.002°는 약 39,256 m²이고, 이 값을 PFD `D`에 적었다. 같은 C·D라도 고위도로 갈수록 동서 폭이 cos(위도)에 비례해 줄어든다.

### 1.4 Python으로 GRD 바이너리 만들고 다시 읽기

55장 4.2절의 GPS 궤적 다섯 점을 type 1·type 2 파일 양쪽에서 조회해 같은 값이 나오는지 assert로 확인한다. `assert`는 조건이 거짓이면 그 자리에서 프로그램을 멈추는 확인 문장이다. 코드는 네 부분으로 되어 있다.

- `GRD`, `RATES_KG_HA`: 격자 정의와 처방(남쪽 행부터, 서쪽에서 동쪽으로).
- `build_type1`, `build_type2`: 셀 값을 파일 순서대로 바이트로 만든다.
- `cell_index`: 1.1절의 식으로 위치를 셀 번호로 바꾼다. 격자 밖이면 `None`이다.
- `read_type1`, `read_type2`: 파일 길이를 먼저 확인하고 셀 값을 읽는다.

::: details grid_demo.py (실행 검증)
```python
"""Build and read back ISOXML grid binary files (ISO 11783-10 6.8.1.1, 8.6.2, D.27)."""
import math
import struct

GRD = {
    "A": 37.500,   # GridMinimumNorthPosition (south edge)
    "B": 127.000,  # GridMinimumEastPosition (west edge)
    "C": 0.001,    # GridCellNorthSize [deg]
    "D": 0.001,    # GridCellEastSize [deg]
    "E": 2,        # GridMaximumColumn (cells toward east)
    "F": 2,        # GridMaximumRow (cells toward north)
}

# Section 4.2 prescription in kg/ha, row 0 = south row, west -> east
RATES_KG_HA = [
    [150, 200],  # row 0: 37.500 .. 37.501
    [100, 180],  # row 1: 37.501 .. 37.502
]


def kg_ha_to_ddi6(kg_ha):
    # DDI 6 Setpoint Mass Per Area Application Rate [mg/m2]: 150 kg/ha = 15000 (D.41 example 1)
    return round(kg_ha * 100)


def cells_in_file_order(grid_2d):
    """Row 0 first, columns west to east inside each row (6.8.1.1)."""
    return [value for row in grid_2d for value in row]


def build_type1(zone_codes):
    """Grid type 1: one unsigned 8-bit TreatmentZoneCode per cell."""
    return bytes(zone_codes)


def build_type2(records):
    """Grid type 2: per cell, one signed 32-bit value per template PDV, little endian."""
    return b"".join(struct.pack("<%di" % len(rec), *rec) for rec in records)


def cell_index(grd, lat, lon):
    col = math.floor((lon - grd["B"]) / grd["D"])
    row = math.floor((lat - grd["A"]) / grd["C"])
    if 0 <= col < grd["E"] and 0 <= row < grd["F"]:
        return row * grd["E"] + col
    return None


def read_type1(blob, grd, lat, lon):
    assert len(blob) == grd["E"] * grd["F"], "file length != E*F"
    idx = cell_index(grd, lat, lon)
    return None if idx is None else blob[idx]


def read_type2(blob, grd, n_pdv, lat, lon):
    rec_size = 4 * n_pdv
    assert len(blob) == grd["E"] * grd["F"] * rec_size, "file length != E*F*4*nPDV"
    idx = cell_index(grd, lat, lon)
    if idx is None:
        return None
    return struct.unpack_from("<%di" % n_pdv, blob, idx * rec_size)


if __name__ == "__main__":
    # Type 1: zone codes 1..4 -> TZN 1=150, 2=200, 3=100, 4=180 kg/ha
    zone_of_rate = {150: 1, 200: 2, 100: 3, 180: 4}
    tzn_value = {code: kg_ha_to_ddi6(rate) for rate, code in zone_of_rate.items()}
    t1 = build_type1([zone_of_rate[r] for r in cells_in_file_order(RATES_KG_HA)])

    # Type 2: template TZN with a single PDV (DDI 0006)
    t2 = build_type2([(kg_ha_to_ddi6(r),) for r in cells_in_file_order(RATES_KG_HA)])

    print("GRD00001.BIN type 1 (%d bytes):" % len(t1), t1.hex(" ").upper())
    print("GRD00001.BIN type 2 (%d bytes):" % len(t2), t2.hex(" ").upper())

    gps_trace = [  # same trace as section 4.2
        (37.5005, 127.0005, 150),
        (37.5005, 127.0015, 200),
        (37.5015, 127.0005, 100),
        (37.5015, 127.0015, 180),
        (37.5025, 127.0025, None),  # outside the grid
    ]
    for lat, lon, expected in gps_trace:
        code = read_type1(t1, GRD, lat, lon)
        v2 = read_type2(t2, GRD, 1, lat, lon)
        rate1 = None if code is None else tzn_value[code] / 100
        rate2 = None if v2 is None else v2[0] / 100
        assert rate1 == rate2 == (None if expected is None else float(expected))
        print(f"({lat:.4f},{lon:.4f}) idx={cell_index(GRD, lat, lon)} "
              f"type1 TZN={code} type2 raw={v2} -> {rate2} kg/ha")

    # Size check for the TC-GEO minimum grid (F.2.2: 350 rows x 350 columns)
    n = 350 * 350
    print("350x350: type1 =", n, "bytes, type2 (1 PDV) =", n * 4, "bytes, type2 (3 PDV) =", n * 12, "bytes")
    print("all assertions passed")
```
:::

코드 주석의 "Section 4.2"는 55장 4.2절을 가리킨다.

### 1.5 실행하고 결과 확인

1. 위 코드를 `grid_demo.py`로 저장한다.
2. `python3 grid_demo.py`를 실행한다.
3. 아래 결과가 나오고 마지막 줄이 `all assertions passed`면 성공이다.

실행 결과:

```
GRD00001.BIN type 1 (4 bytes): 01 02 03 04
GRD00001.BIN type 2 (16 bytes): 98 3A 00 00 20 4E 00 00 10 27 00 00 50 46 00 00
(37.5005,127.0005) idx=0 type1 TZN=1 type2 raw=(15000,) -> 150.0 kg/ha
(37.5005,127.0015) idx=1 type1 TZN=2 type2 raw=(20000,) -> 200.0 kg/ha
(37.5015,127.0005) idx=2 type1 TZN=3 type2 raw=(10000,) -> 100.0 kg/ha
(37.5015,127.0015) idx=3 type1 TZN=4 type2 raw=(18000,) -> 180.0 kg/ha
(37.5025,127.0025) idx=None type1 TZN=None type2 raw=None -> None kg/ha
350x350: type1 = 122500 bytes, type2 (1 PDV) = 490000 bytes, type2 (3 PDV) = 1470000 bytes
all assertions passed
```

결과는 이렇게 읽는다.

- 첫 두 줄이 만든 파일이다. type 2의 첫 4바이트 `98 3A 00 00`을 거꾸로 읽으면 0x00003A98 = 15000, 곧 150 kg/ha다. 나머지 세 칸도 4바이트씩 20000, 10000, 18000이다.
- 가운데 다섯 줄이 위치 조회 결과다. 셋째 줄 `idx=2`는 1.1절 그림의 계산과 같고, type 1의 TZN 3과 type 2의 원시값 10000이 모두 100 kg/ha를 가리킨다.
- `350x350` 줄은 1.3절의 최소 사양 격자 크기 계산이다.

다섯 번째 점은 격자 밖이라 셀 값이 없다. 이 예제는 필지 경계를 격자와 같은 사각형으로 두었으므로 격자 밖이 곧 필지 밖이고, TC는 TSK `J`가 가리키는 필드 밖 TZN(값 0)을 보낸다. 55장 4.2절 시뮬레이터가 격자 밖에서 0을 돌려준 동작이 파일 세트에서는 이렇게 표현된다. 필지 안이면서 격자 밖인 위치에서 TC가 무엇을 보내야 하는지는 표준 문서에서 찾지 못했다.

::: warning grid 구현 함정
- <strong>`E`·`F`는 개수다.</strong> 이름은 GridMaximumColumn·Row지만 표준의 설명은 "동·북 방향 셀 개수"다. 최대 인덱스로 읽으면 한 줄씩 어긋난다.
- <strong>`A`·`B`는 셀 중심이 아니라 격자 모서리다.</strong> 셀 (row, col)의 중심은 (A + (row + 0.5) × C, B + (col + 0.5) × D)다.
- <strong>grid에는 XML 헤더 파일이 없다.</strong> TimeLog(2절)와 달리 grid는 바이너리 파일 하나와 `TASKDATA.XML` 안의 GRD 요소로 정의한다. 표준 문서 안에 이와 다르게 읽히는 문장이 있어 아래 메모에 적어 두었다. 이 글은 GRD 요소 정의와 grid 바이너리 예제를 따랐다.
- <strong>확장자 대소문자</strong>: 파일 이름은 모두 대문자로 쓰는 것이 규칙이지만, 표준 문서 안에도 접미사를 `.bin`·`.xml`처럼 소문자로 적은 곳이 있다. 쓸 때는 대문자로 쓰고, 읽을 때는 대소문자를 가리지 않고 찾는 편이 안전하다(추론).
- <strong>경계 위의 점</strong>을 어느 셀에 넣을지는 표준 문서에서 찾지 못했다. 위 코드는 floor로 남·서 경계를 그 셀에 넣는다. 경계 근처에서는 부동소수 오차로 이웃 셀로 넘어갈 수 있으니, `xs:decimal`인 `A`·`B`는 문자열을 `Decimal`로 파싱하면 오차를 줄일 수 있다(추론). 예를 들어 네 칸이 만나는 점 (37.501, 127.001)은 정확히 계산하면 row 1, col 1(셀 3, 180 kg/ha)이다. 그런데 float로 계산하면 37.501 − 37.500이 0.000999…로 조금 작게 나와 row 0, col 1(셀 1, 200 kg/ha)이 된다. 55장 시뮬레이터는 목록에서 먼저 나온 칸을 고르므로 같은 점에 150을 돌려준다.
:::

::: details 원문을 가진 독자를 위한 메모
- 셀 순서 규칙과 그림은 ISO 11783-10:2015 6.8.1.1과 Figure 4, grid 파일 정의는 8.6.2와 D.27에 있다. type 2 세 PDV 예제는 8.6.2 예2다.
- 6.8.1.1은 grid 파일 정의마다 바이너리와 XML 헤더 두 파일이 생긴다고 적지만, 8.6.2와 D.27은 grid당 바이너리 파일 하나와 GRD 요소로 정의한다. XML 헤더 두 파일 구조는 TLG의 것이다.
- 8.5는 파일 이름을 모두 대문자로 쓰라고 하지만, 6.8.1.1은 접미사를 `.bin`·`.xml`로 적고 그림도 `GRD00001.bin`처럼 소문자를 쓴다.
:::

<small>근거: ISO 11783-10 6.8.1.1, 8.5, 8.6.2, D.27, D.50, F.2.2; ISO 11783-6 C.2</small>

## 2. 실습 2: TimeLog로 작업 기록 남기기

::: info 실습 안내
- 목표: TC가 남기는 작업 기록 파일(`TLG00001.XML`과 `TLG00001.BIN`)을 만들고, 헤더만 보고 레코드를 해독한다.
- 필요한 지식: [56장](/study/isobus/56-practice-isoxml) 6절과 7절(DLT, TLG), 이 장 1절의 리틀 엔디언 읽기
- 준비물: 파이썬 3, 2.3절의 `tlg_demo.py`
:::

56장 7절에서 TC가 TSK에 넣은 `<TLG A="TLG00001" C="1"/>`이 가리키는 파일을 만든다. DLT가 요청한 값은 이 바이너리 로그에 쌓인다.

### 2.1 TLG = XML 헤더 + 바이너리 레코드

TimeLog는 두 파일로 이루어진다. XML 헤더가 "레코드에 무엇을 어떤 순서로 넣는지"를 정하고, 바이너리 파일에 레코드가 시간 순서로 쌓인다. 앞의 비유로 말하면 헤더가 장부의 칸 약속이고, 바이너리가 장부의 줄들이다.

- 태스크 파일의 TLG는 TIM·PTN·DLV를 직접 담지 않고 파일 두 개를 가리킨다. 레코드 구조를 정하는 XML 헤더(`TLG00001.XML`)와 바이너리 로그(`TLG00001.BIN`)다. 두 파일 이름은 파일 세트의 모든 TLG 사이에서 유일해야 한다.
- 헤더의 TIM은 type 4(effective)여야 하고, TLG `C`(TimeLogType)는 현행 방식인 1이다.
- <strong>값이 빈 속성(`""`)은 레코드마다 바이너리에 기록되는 필드</strong>이고, 값이 있는 속성은 모든 레코드에 공통인 고정값이다.
- 빈 속성은 헤더에 어떤 순서로 적어도 되지만, 바이너리 안의 값 순서는 표준이 정한 필드 순서(2.2절 표)를 따른다. 그 표에 없는 속성은 바이너리에 쓸 수 없다. 그래서 DLV의 `A`(DDI)와 `C`(장치 요소)는 반드시 헤더에 고정값으로 적고, 바이너리에는 `B`(값)만 들어간다.
- DLV는 헤더에 정의한 순서대로 0, 1, 2 … 번호(DLVn)를 받는다. 레코드에는 실제로 담은 값의 개수 #DLV와 (DLVn, 값) 쌍이 이어진다. 그래서 레코드마다 담는 DLV 집합이 달라도 되고, #DLV가 1바이트라 한 레코드에 최대 255개다.

이 실습의 헤더는 다음과 같다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<TIM A="" D="4">
  <PTN A="" B="" D="" H="" I=""/>
  <DLV A="0006" B="" C="DET-2"/>
  <DLV A="0007" B="" C="DET-2"/>
</TIM>
```

한 줄씩 읽으면 다음과 같다.

- `TIM A=""`: 시작 시각을 레코드마다 기록한다. `D="4"`(effective)는 모든 레코드에 공통인 고정값이다.
- `PTN A="" B="" D="" H="" I=""`: 위도, 경도, 측위 상태, GPS UTC 시각, GPS UTC 날짜를 레코드마다 기록한다. 고도(`C`)와 정확도 정보(`E`·`F`·`G`)는 기록하지 않는다.
- `DLV A="0006" B="" C="DET-2"`: DDI 6(설정 살포량) 값을 기록한다. 어느 DDI인지와 어느 장치 요소인지는 헤더에 고정하고, 값(`B`)만 레코드에 들어간다. 이 DLV가 DLVn 0이다.
- 둘째 DLV(DDI 7, 실제 살포량)가 DLVn 1이다.

### 2.2 필드별 바이트 배치와 단위

위 헤더가 만드는 레코드다. 오프셋은 레코드 시작에서 몇 번째 바이트인지(0부터)를 뜻한다. N/A는 값을 모를 때 넣는 특수값이다. 값을 모를 때 0을 넣으면 "0도"나 "자정"과 구별할 수 없으므로, 모든 비트를 1로 채운 값(`FF…`)을 "값 없음" 표시로 쓴다.

| 오프셋 | 필드 | XML | 타입 | 단위·인코딩 | N/A |
|---|---|---|---|---|---|
| 0 | TimeStart 시각 | TIM `A` | u32 | 로컬 시간 자정 이후 ms | FFFFFFFF₁₆ |
| 4 | TimeStart 날짜 | TIM `A` | u16 | 로컬 1980-01-01 이후 일수 | FFFF₁₆ |
| 6 | PositionNorth | PTN `A` | i32 | 10⁻⁷도, WGS-84 | FFFFFFFF₁₆ |
| 10 | PositionEast | PTN `B` | i32 | 10⁻⁷도, WGS-84 | FFFFFFFF₁₆ |
| 14 | PositionStatus | PTN `D` | u8 | 0 no fix, 1 GNSS, 2 DGNSS, 3 Precise GNSS, 4 RTK fixed, 5 RTK float, 6 DR, 7 수동 입력, 8 시뮬레이트, 9~13 예약, 14 오류, 15 값 없음 | FF₁₆ |
| 15 | GpsUtcTime | PTN `H` | u32 | UTC 자정 이후 ms | FFFFFFFF₁₆ |
| 19 | GpsUtcDate | PTN `I` | u16 | UTC 1980-01-01 이후 일수 | FFFF₁₆ |
| 21 | #DLV | 없음 | u8 | 뒤따르는 (DLVn, 값) 쌍의 수 | 없음 |
| 22 | DLVn | 없음 | u8 | 헤더 DLV 순번(0부터) | 없음 |
| 23 | ProcessDataValue | DLV `B` | i32 | DDI 정의대로 | 없음 |

고정부는 22바이트이고 DLV 하나마다 5바이트가 붙는다. 헤더에서 PTN `C`를 비우면 East 뒤에 i32 PositionUp(mm)이, `E`·`F`·`G`를 비우면 Status 뒤에 u16 PDOP, u16 HDOP(둘 다 0.1 단위), u8 위성 수가 끼어든다.

표준이 정한 필드 순서 전체는 다음과 같다. 헤더에서 빈 속성으로 고른 필드만 이 순서대로 레코드에 들어가고, 13·14번은 #DLV 개수만큼 반복된다. PDOP와 HDOP는 위성 배치에 따른 위치 정확도 지표로, 작을수록 좋다.

| 순서 | 필드 | XML | 타입 | 단위·인코딩 | N/A |
|---|---|---|---|---|---|
| 1 | TimeStart 시각 | TIM `A` | u32 | 로컬 자정 이후 ms | FFFFFFFF₁₆ |
| 2 | TimeStart 날짜 | TIM `A` | u16 | 로컬 1980-01-01 이후 일수 | FFFF₁₆ |
| 3 | PositionNorth | PTN `A` | i32 | 10⁻⁷도 | FFFFFFFF₁₆ |
| 4 | PositionEast | PTN `B` | i32 | 10⁻⁷도 | FFFFFFFF₁₆ |
| 5 | PositionUp | PTN `C` | i32 | WGS-84 타원체 기준 mm | FFFFFFFF₁₆ |
| 6 | PositionStatus | PTN `D` | u8 | 위 표의 상태 코드 | FF₁₆ |
| 7 | PDOP | PTN `E` | u16 | 0.1 단위 | FFFF₁₆ |
| 8 | HDOP | PTN `F` | u16 | 0.1 단위 | FFFF₁₆ |
| 9 | NumberOfSatellites | PTN `G` | u8 | 사용한 위성 수 | FF₁₆ |
| 10 | GpsUtcTime | PTN `H` | u32 | UTC 자정 이후 ms | FFFFFFFF₁₆ |
| 11 | GpsUtcDate | PTN `I` | u16 | UTC 1980-01-01 이후 일수 | FFFF₁₆ |
| 12 | #DLV | 없음 | u8 | 뒤따르는 (DLVn, 값) 쌍의 수 | 없음 |
| 13 | DLVn | 없음 | u8 | 헤더 DLV 순번(0부터) | 없음 |
| 14 | ProcessDataValue | DLV `B` | i32 | DDI 정의대로 | 없음 |

![TLG00001.XML 헤더의 TIM·PTN·DLV 빈 속성이 TLG00001.BIN 레코드 0의 32바이트로 펼쳐지는 모습. 오프셋 0의 TimeStart부터 21의 #DLV까지 고정부 22바이트와 22~31의 DLVn·PDV 두 쌍](/images/study-isobus/22-timelog-record-light.png)
![TLG00001.XML 헤더의 TIM·PTN·DLV 빈 속성이 TLG00001.BIN 레코드 0의 32바이트로 펼쳐지는 모습. 오프셋 0의 TimeStart부터 21의 #DLV까지 고정부 22바이트와 22~31의 DLVn·PDV 두 쌍](/images/study-isobus/22-timelog-record-dark.png)

그림의 위쪽이 헤더, 아래쪽이 2.4절에서 만들 레코드 0의 실제 바이트다. 같은 색끼리 짝이다. 헤더의 빈 속성 하나가 바이트 몇 개로 펼쳐지는지 보면 된다.

- <strong>바이트 순서</strong>: TimeLog 규정에는 바이트 순서를 정한 문장이 없다. 같은 바이너리 파일 규정 안에서 grid는 int32에 ISO 11783-6의 규칙을 적용하라고 하고, ISO 11783-6(VT를 정하는 표준 문서)은 1바이트보다 큰 값을 리틀 엔디언으로 보낸다. 그래서 이 실습은 TLG도 리틀 엔디언으로 쓰고 읽는다(추론).
- <strong>위치 분해능</strong>: 10⁻⁷도는 위도 방향으로 약 11.1 mm다. 경도 ±180°도 ±1,800,000,000이라 int32(최대 2,147,483,647) 안에 들어간다.
- <strong>시간대</strong>: v4가 XML 시각에 시간대를 붙일 수 있게 했어도 바이너리의 TimeStart는 계속 로컬 시간이다. v4 이전에는 TLG에 UTC와 로컬 시간이 함께 기록된 경우에만 둘의 차로 시간대를 계산할 수 있었다. 이 헤더가 GpsUtcTime·Date를 함께 비워 둔 이유다.

### 2.3 Python으로 레코드 만들고 디코딩하기

헤더의 빈 속성 목록에서 레코드 형식을 만들고, 55장 4.2절 궤적을 따라 레코드 여섯 개를 쓴 뒤 다시 읽는다. 두 번째 레코드는 실제 살포량만 바뀐 경우라 DLV가 하나뿐이다. 코드의 중심은 세 함수다.

- `parse_header`: 필드 순서표(`TABLE3`)를 차례로 보며 헤더에서 값이 빈 속성만 골라 `struct` 형식 문자열을 만든다. 이 헤더라면 `<IHiiBIHB`가 된다.
- `encode_record`: 고정부를 그 형식으로 쓰고, (DLVn, 값) 쌍을 `<Bi`(1바이트 + 4바이트)로 이어 붙인다.
- `decode`: 파일 처음부터 고정부를 읽고, #DLV만큼 쌍을 읽고, 다음 레코드로 넘어가기를 반복한다.

::: details tlg_demo.py (실행 검증)
```python
"""Write and decode an ISOXML TimeLog binary file (ISO 11783-10 8.6.3, Table 3, D.49)."""
import datetime as dt
import struct
import xml.etree.ElementTree as ET

TLG_HEADER = """<?xml version="1.0" encoding="UTF-8"?>
<TIM A="" D="4">
  <PTN A="" B="" D="" H="" I=""/>
  <DLV A="0006" B="" C="DET-2"/>
  <DLV A="0007" B="" C="DET-2"/>
</TIM>
"""

# Table 3 order: (element, attribute, field name, struct code)
TABLE3 = [
    ("TIM", "A", "time_ms", "I"),     # local ms since midnight
    ("TIM", "A", "date", "H"),        # local days since 1980-01-01
    ("PTN", "A", "north", "i"),       # 1e-7 deg
    ("PTN", "B", "east", "i"),        # 1e-7 deg
    ("PTN", "C", "up", "i"),          # mm
    ("PTN", "D", "status", "B"),
    ("PTN", "E", "pdop", "H"),        # 0.1
    ("PTN", "F", "hdop", "H"),        # 0.1
    ("PTN", "G", "sats", "B"),
    ("PTN", "H", "utc_ms", "I"),
    ("PTN", "I", "utc_date", "H"),
]
EPOCH = dt.date(1980, 1, 1)


def parse_header(xml_text):
    """Return (fixed-part struct format, field names, DLV definitions in header order)."""
    tim = ET.fromstring(xml_text)
    ptn = tim.find("PTN")
    present = {"TIM": tim.attrib, "PTN": {} if ptn is None else ptn.attrib}
    fmt, names = "<", []
    for elem, attr, name, code in TABLE3:
        if present[elem].get(attr) == "":
            fmt += code
            names.append(name)
    dlvs = [(d.get("A"), d.get("C")) for d in tim.findall("DLV")]
    for ddi, det in dlvs:
        assert ddi and det, "DDI and DeviceElementIdRef must be fixed values"
    return fmt + "B", names + ["n_dlv"], dlvs


def encode_record(fmt, names, values, dlv_items):
    fixed = [values[n] for n in names[:-1]] + [len(dlv_items)]
    out = struct.pack(fmt, *fixed)
    for n, v in dlv_items:
        out += struct.pack("<Bi", n, v)
    return out


def decode(blob, fmt, names, dlvs):
    size, off, records = struct.calcsize(fmt), 0, []
    while off < len(blob):
        rec = dict(zip(names, struct.unpack_from(fmt, blob, off)))
        off += size
        rec["dlv"] = {}
        for _ in range(rec.pop("n_dlv")):
            n, v = struct.unpack_from("<Bi", blob, off)
            off += 5
            rec["dlv"][dlvs[n][0]] = v
        records.append(rec)
    return records


def as_fields(local, utc, lat, lon, status):
    ms = lambda t: ((t.hour * 60 + t.minute) * 60 + t.second) * 1000 + t.microsecond // 1000
    return {
        "time_ms": ms(local), "date": (local.date() - EPOCH).days,
        "north": round(lat * 1e7), "east": round(lon * 1e7), "status": status,
        "utc_ms": ms(utc), "utc_date": (utc.date() - EPOCH).days,
    }


if __name__ == "__main__":
    fmt, names, dlvs = parse_header(TLG_HEADER)
    print("record fixed part:", fmt, struct.calcsize(fmt), "bytes;", names)

    kst = dt.timezone(dt.timedelta(hours=9))
    start = dt.datetime(2026, 4, 13, 9, 30, 0, tzinfo=kst)
    # (seconds, lat, lon, [(DLVn, value), ...]) -- DLV0 = DDI 6, DLV1 = DDI 7
    log = [
        (0,  37.5005, 127.0005, [(0, 15000), (1, 14820)]),
        (5,  37.50052, 127.00093, [(1, 14950)]),  # only DLV1 changed
        (10, 37.5005, 127.0015, [(0, 20000), (1, 19750)]),
        (20, 37.5015, 127.0005, [(0, 10000), (1, 10110)]),
        (30, 37.5015, 127.0015, [(0, 18000), (1, 17940)]),
        (40, 37.5025, 127.0025, [(0, 0), (1, 0)]),
    ]
    blob = b""
    for sec, lat, lon, items in log:
        local = (start + dt.timedelta(seconds=sec)).replace(tzinfo=None)
        utc = (start + dt.timedelta(seconds=sec)).astimezone(dt.timezone.utc)
        blob += encode_record(fmt, names, as_fields(local, utc, lat, lon, 4), items)

    print("TLG00001.BIN length:", len(blob))
    print("record 0:", blob[:32].hex(" ").upper())
    print("record 1:", blob[32:59].hex(" ").upper())

    recs = decode(blob, fmt, names, dlvs)
    assert len(recs) == len(log)
    for rec, (sec, lat, lon, items) in zip(recs, log):
        assert abs(rec["north"] / 1e7 - lat) < 1e-9 and abs(rec["east"] / 1e7 - lon) < 1e-9
        assert rec["dlv"] == {dlvs[n][0]: v for n, v in items}
        offset_h = ((rec["time_ms"] - rec["utc_ms"]) / 3_600_000) + (rec["date"] - rec["utc_date"]) * 24
        assert offset_h == 9
    r0 = recs[0]
    print("decoded 0:", EPOCH + dt.timedelta(days=r0["date"]),
          dt.timedelta(milliseconds=r0["time_ms"]), r0["north"] / 1e7, r0["east"] / 1e7,
          "status", r0["status"], r0["dlv"])
    print("decoded 1:", recs[1]["dlv"])
    print("time zone from local - UTC:", offset_h, "h")
    print("all assertions passed")
```
:::

코드의 `TABLE3`은 2.2절의 필드 순서표를 그대로 옮긴 목록이다.

### 2.4 실행하고 결과 확인

1. 위 코드를 `tlg_demo.py`로 저장한다.
2. `python3 tlg_demo.py`를 실행한다.
3. 아래 결과가 나오고 마지막 줄이 `all assertions passed`면 성공이다.

실행 결과:

```
record fixed part: <IHiiBIHB 22 bytes; ['time_ms', 'date', 'north', 'east', 'status', 'utc_ms', 'utc_date', 'n_dlv']
TLG00001.BIN length: 187
record 0: C0 D9 09 02 08 42 48 1F 5A 16 08 BD B2 4B 04 40 77 1B 00 08 42 02 00 98 3A 00 00 01 E4 39 00 00
record 1: 48 ED 09 02 08 42 10 20 5A 16 D4 CD B2 4B 04 C8 8A 1B 00 08 42 01 01 66 3A 00 00
decoded 0: 2026-04-13 9:30:00 37.5005 127.0005 status 4 {'0006': 15000, '0007': 14820}
decoded 1: {'0007': 14950}
time zone from local - UTC: 9.0 h
all assertions passed
```

`<IHiiBIHB`의 `<`는 리틀 엔디언이면서 정렬 패딩이 없다는 뜻이다. 패딩이 들어가는 기본 정렬(`@`)로 쓰면 고정부 크기가 달라지므로 바이너리 파일 형식에는 항상 `<`를 쓴다. 파일 길이 187바이트는 2-DLV 레코드 다섯 개(32 × 5)와 1-DLV 레코드 하나(27)를 더한 값이다.

### 2.5 바이트로 따라가기: 레코드 0

레코드 0의 32바이트를 2.2절 표의 오프셋대로 끊어 읽으면 다음과 같다. 여러 바이트로 된 값은 리틀 엔디언이라 거꾸로 읽는다.

| 바이트 | 값 | 뜻 |
|---|---|---|
| `C0 D9 09 02` | 0x0209D9C0 = 34,200,000 | 로컬 09:30:00.000 |
| `08 42` | 0x4208 = 16,904 | 1980-01-01 + 16,904일 = 2026-04-13 |
| `48 1F 5A 16` | 0x165A1F48 = 375,005,000 | 37.5005° |
| `08 BD B2 4B` | 0x4BB2BD08 = 1,270,005,000 | 127.0005° |
| `04` | 4 | RTK fixed |
| `40 77 1B 00` | 0x001B7740 = 1,800,000 | UTC 00:30:00.000 |
| `08 42` | 16,904 | UTC로도 같은 날 |
| `02` | 2 | (DLVn, 값) 두 쌍 |
| `00` `98 3A 00 00` | DLV0 = 15,000 | DDI 6 설정값 150 kg/ha |
| `01` `E4 39 00 00` | DLV1 = 14,820 | DDI 7 실제값 148.2 kg/ha |

로컬 − UTC = 34,200,000 − 1,800,000 = 32,400,000 ms = 9시간이다. 레코드 1은 `… 01 01 66 3A 00 00`으로 끝난다. #DLV = 1, DLVn = 1이므로 DDI 7만 14,950(149.5 kg/ha)으로 기록됐다. DLT `G="100"`이 정한 변화 임계값을 넘은 실제값만 남은 것이다.

::: warning TLG 디코더 함정
- <strong>레코드 길이가 가변이다.</strong> #DLV에 따라 레코드마다 길이가 달라 임의의 위치부터 읽을 수 없다. 처음부터 순서대로 읽어야 하고, 한 번 어긋나면 뒤의 모든 레코드가 깨진다.
- <strong>고정부 형식은 헤더가 정한다.</strong> 디코더에 필드 배치를 하드코딩하면 다른 TC가 PTN `C`나 `G`를 비운 헤더를 쓸 때 레코드 경계가 밀린다. 2.3절처럼 헤더의 빈 속성에서 형식을 만든다.
- <strong>위치 N/A 값이 실제 좌표와 겹친다.</strong> PositionNorth·East의 N/A는 FFFFFFFF₁₆인데 i32로 읽으면 −1, 곧 −0.0000001°다. 표준은 이 충돌을 따로 다루지 않으니 PositionStatus(0 no fix, 15 값 없음)와 함께 판단하는 편이 안전하다(추론).
- <strong>DLV가 없는 헤더</strong>: 헤더에 DLV가 하나도 없을 때 #DLV 바이트를 쓰는지는 표준에서 확인하지 못했다. 필드 순서표는 #DLV를 조건 없이 목록에 둔다.
:::

::: details 원문을 가진 독자를 위한 메모
- 2.2절의 필드 순서표는 ISO 11783-10:2015 8.6.3의 Table 3이다. TLG 요소와 파일 이름 규칙은 D.49, 시간대 계산 규칙은 D.48에 있다.
- 바이트 순서 추론의 근거는 8.6.2(grid int32에 ISO 11783-6 규칙 적용)와 ISO 11783-6 C.2(리틀 엔디언)다.
:::

<small>근거: ISO 11783-10 8.6.2, 8.6.3, D.48, D.49; ISO 11783-6 C.2</small>

## 3. Point 데이터 바이너리 파일 (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 다음 절로 가도 된다.
:::

필지 경계 같은 PNT 요소들을 XML 대신 바이너리로 보낼 수 있다(v4). 목적은 정밀도다. 바이너리에서 North·East는 64비트 정수이고 단위가 10⁻¹⁶도다. 헤더 방식은 TLG와 같아서, PNT 요소에서 빈 속성이 바이너리 필드가 되고 값이 있는 속성은 모든 레코드의 고정값이 된다. 바이너리 안의 필드 순서는 아래 표와 같다.

| 순서 | 필드 | XML | 타입 | 단위 | N/A |
|---|---|---|---|---|---|
| 1 | PointType | PNT `A` | u8 | PointType 열거값 | FF₁₆ |
| 2 | PositionNorth | PNT `C` | i64 | 10⁻¹⁶도, WGS-84 | FFFFFFFFFFFFFFFF₁₆ |
| 3 | PositionEast | PNT `D` | i64 | 10⁻¹⁶도, WGS-84 | FFFFFFFFFFFFFFFF₁₆ |
| 4 | PositionUp | PNT `E` | i32 | mm, WGS-84 타원체 기준 | FFFFFFFF₁₆ |
| 5 | PointColour | PNT `F` | u8 | ISO 11783-6 팔레트 | FF₁₆ |
| 6 | PointHorizontalAccuracy | PNT `H` | u16 | RMS 오차 mm | FFFF₁₆ |
| 7 | PointVerticalAccuracy | PNT `I` | u16 | RMS 오차 mm | FFFF₁₆ |

표준 문서의 예제 헤더는 `<PNT A="2" C="" D="" E="" F="1" J="PNT00001" K="40"/>`다. PointType 2와 색 1은 고정이고, 레코드는 North 8 + East 8 + Up 4 = 20바이트다. `K`(파일 길이) 40이므로 점이 두 개다. XML의 PNT `H`·`I`는 m 단위 소수(0.0~65.0)지만 바이너리는 mm 단위 u16이다. 옮길 때 1000을 곱해야 한다. 180° × 10¹⁶ = 1.8 × 10¹⁸은 int64 최댓값(약 9.22 × 10¹⁸)보다 작다.

10⁻¹⁶도 단위 정수는 18~19자리라 float(유효 숫자 15~17자리)를 거치면 끝자리가 틀어진다. 예를 들어 `37.5005123456789`를 float로 곱하면 375005123456788992가 되어 Decimal로 계산한 375005123456789000과 8만큼 다르다. 좌표는 문자열에서 `Decimal`로 바로 정수로 바꾼다. Point 규정에도 바이트 순서 문장이 없으므로 TimeLog와 같은 추론으로 리틀 엔디언을 썼다.

아래는 점 하나(위도 37.50052, 경도 127.00093, 고도 50 mm)를 레코드로 만든 것이다.

```python
>>> import struct
>>> from decimal import Decimal
>>> rec = struct.pack("<qqi", int(Decimal("37.50052") * 10**16), int(Decimal("127.00093") * 10**16), 50)
>>> len(rec), rec.hex(" ").upper()
(20, '00 A0 EC 16 3E 49 34 05 00 48 F1 C3 BA FA 9F 11 32 00 00 00')
```

결과는 이렇게 확인한다. 앞 8바이트 `00 A0 EC 16 3E 49 34 05`를 거꾸로 읽으면 0x0534493E16ECA000 = 375005200000000000, 곧 37.50052 × 10¹⁶이다. 다음 8바이트가 경도 1270009300000000000이고, 마지막 4바이트 `32 00 00 00`이 고도 50 mm다. 합쳐서 20바이트다.

::: details 원문을 가진 독자를 위한 메모
- Point 바이너리의 필드 순서표는 ISO 11783-10:2015 8.6.4의 Table 4, 예제 헤더는 D.38 예2다.
:::

<small>근거: ISO 11783-10 8.6.4, D.38</small>

## 4. 사전 정의 첨부 파일 LINKLIST.XML (심화)

::: info 처음 읽는다면
이 절은 직접 구현할 때 필요한 세부다. 처음에는 건너뛰고 핵심 정리로 가도 된다.
:::

파일 세트의 ID(`TSK1`, `PFD-3` …)는 그 파일 세트 안에서만 유일하다. 다음에 주고받는 파일 세트에서는 같은 필지가 다른 ID를 받을 수 있다. FMIS 데이터베이스의 키나 UUID(전 세계에서 겹치지 않게 만든 128비트 식별자)와 오래 묶어 두려면 따로 매핑이 필요하다. v4는 이를 위해 사전 정의 첨부 파일 `LINKLIST.XML`을 두었다.

- TASKDATA.XML에 AFE(AttachedFile, 첨부 파일)로 첨부를 알린다. AFE `A`는 대문자 8.3 파일 이름(이름 8자 + 확장자 3자), `B`는 보존 여부(1 = TC가 보존할 필요 없음, 2 = 보존했다가 FMIS로 반송), `C`는 제조사 GS1 GLN(국제 표준 사업자 식별 번호)이고 ISO 사전 정의 첨부면 비운다. `D`는 파일 유형으로 1~127이 ISO 사전 정의, 128~254가 제조사 정의이며 1이 LINKLIST다.
- LINKLIST.XML은 TASKDATA.XML 하나당 최대 1개이고 이름은 대문자 `LINKLIST.XML`로 고정이다. 루트는 `ISO11783LinkList`(VersionMajor 4 이상, ManagementSoftware 이름·버전과 DataTransferOrigin 필수)다.
- 루트 아래 LGP(LinkGroup)가 키 유형 하나의 링크를 묶고, 그 안의 LNK가 `A` 객체 ID와 `B` 키 값(최대 255자)을 잇는다.
- LGP `B` 유형은 1 UUID, 2 제조사 고유 키(GLN 필수), 3 고유하게 해석되는 URI(LGP `D` 네임스페이스 + LNK `B`), 4 정보성 URI다. 4는 홈페이지 같은 휘발성 링크용이라 식별·매핑에 쓰면 안 된다.
- UUID는 ISO/IEC 9834-8(RFC 4122 호환)의 버전 4(랜덤)로 만든다. MICS에서 새로 만든 요소의 UUID는 GLN이 빈 type 1 그룹에 넣고, GLN이 빈 그룹들 안에서는 요소 하나에 Link가 최대 1개다.

TASKDATA.XML에 넣는 첨부 알림이다. LINKLIST.XML을 ISO 사전 정의 유형 1로 첨부하고, TC가 보존했다가 돌려주도록(`B="2"`) 했다.

```xml
<AFE A="LINKLIST.XML" B="2" C="" D="1"/>
```

LINKLIST.XML 본문이다. UUID 그룹(`B="1"`) 하나에 필지 PFD1과 태스크 TSK1의 UUID를 이었다.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<ISO11783LinkList VersionMajor="4" VersionMinor="0"
    ManagementSoftwareManufacturer="StudyFMIS" ManagementSoftwareVersion="1.0"
    DataTransferOrigin="1">
  <LGP A="LGP1" B="1">
    <LNK A="PFD1" B="{3F2A6C1E-8B4D-4E21-9A7C-5D0E1F2A3B4C}"/>
    <LNK A="TSK1" B="{B7E19C40-2D5F-4A8B-8C3E-6F1A2B3C4D5E}"/>
  </LGP>
</ISO11783LinkList>
```

SIL 플랫폼처럼 같은 필지·태스크를 여러 번 주고받는 환경이라면, 파일 세트마다 새로 붙는 `TSK1` 같은 ID 대신 이 UUID를 데이터베이스 키로 쓰면 왕복 후에도 같은 객체를 찾을 수 있다(추론).

<small>근거: ISO 11783-10 D.3, E.1, E.2, E.3, E.4, E.4.1, E.4.4</small>

::: tip 핵심 정리
- grid 원점 (A, B)는 남서 모서리이고, 셀 순서는 행 우선(동쪽으로 열, 북쪽으로 행)이다. index = row × E + col.
- type 1은 셀당 u8 TZN 코드, type 2는 셀당 (int32 리틀 엔디언 × 템플릿 PDV 수)이다. 파일 길이 = E × F × 셀당 바이트.
- TLG는 헤더의 빈 속성이 바이너리 필드다. 레코드 = 헤더가 고른 필드(필드 순서표 순서) + #DLV + (DLVn, PDV) × #DLV이고, TimeStart는 로컬 시간이다.
- 바이너리 형식은 항상 리틀 엔디언, 정렬 패딩 없이(`<`) 읽고, 형식은 헤더에서 만든다.
- Point 바이너리는 좌표를 10⁻¹⁶도 단위 int64로 담아 정밀도를 높이고, LINKLIST.XML은 파일 세트 ID를 UUID 같은 오래가는 키에 잇는다.
:::

::: details 확인 문제
1. (개념) type 1 grid와 type 2 grid에서 처방 값은 각각 어디에 들어 있나?
2. (개념) TimeLog 헤더에서 값이 빈 속성(`""`)과 값이 있는 속성은 각각 무엇을 뜻하나?
3. (개념) 바이너리 파일을 `struct`로 읽을 때 형식 문자열 앞에 `<`를 붙이는 이유는?
4. (계산형) `<GRD A="37.500" B="127.000" C="0.001" D="0.001" E="2" F="2" G="GRD00001" I="2" J="1"/>`의 템플릿 TZN 1에 PDV가 세 개(DDI 0001, 0006, 001A) 있다. 좌표 (37.5015, 127.0005)의 값 세 개는 파일의 몇 번째 바이트부터 몇 바이트를 읽어야 하나? GRD `H`에는 얼마를 적어야 하나?
5. (디코딩형) TLG 헤더가 `<TIM A="" D="4"><PTN A="" B="" D=""/><DLV A="0006" B="" C="DET1"/><DLV A="0007" B="" C="DET1"/></TIM>`이다. 레코드 `80 EE 36 00 08 42 48 1F 5A 16 08 BD B2 4B 01 01 01 E4 39 00 00`을 해석하라.
6. (장애 진단형) FMIS가 어떤 TC가 돌려준 TLG00001.BIN을 읽는데, 첫 레코드부터 위도·경도는 맞지만 그 뒤 값이 엉망이고 두 번째 레코드부터는 시각도 틀린다. 헤더는 `<PTN A="" B="" C="" D=""/>`이고, 디코더는 표준 문서의 TimeLog 예제 헤더(`<PTN A="" B="" D=""/>`)에 맞춰 고정부를 `<IHiiB`(TimeStart 시각·날짜, North, East, Status)로 하드코딩해 두었다. 원인과 고칠 점은?

**답 가이드**
1. type 1은 처방 값이 XML의 TZN·PDV에 있고, 바이너리에는 셀마다 TZN 코드만 있다. type 2는 XML의 템플릿 TZN이 틀만 정하고, 값은 바이너리에 셀마다 들어 있다.
2. 빈 속성은 레코드마다 바이너리에 기록되는 필드이고, 값이 있는 속성은 모든 레코드에 공통인 고정값이다.
3. `<`는 리틀 엔디언이면서 정렬 패딩 없이 읽으라는 뜻이다. 기본 정렬(`@`)로 읽으면 필드 사이에 패딩이 끼어 필드 위치와 고정부 크기가 어긋난다.
4. row = floor((37.5015 − 37.500) / 0.001) = 1, col = floor((127.0005 − 127.000) / 0.001) = 0, index = 1 × 2 + 0 = 2다. 레코드 크기는 4 × 3 = 12바이트라 오프셋 24부터 12바이트(24~35)를 읽고, 순서대로 DDI 0001·0006·001A 값이다. `H` = 2 × 2 × 12 = 48.
5. 고정부는 u32 + u16 + i32 + i32 + u8 + #DLV u8 = 16바이트다. `80 EE 36 00` = 3,600,000 ms = 로컬 01:00:00, `08 42` = 2026-04-13, 위도 37.5005°, 경도 127.0005°, PositionStatus 1(GNSS fix), #DLV = 1, DLVn = 1 → 헤더 두 번째 DLV인 DDI 0007의 값 `E4 39 00 00` = 14,820(148.2 kg/ha). 레코드 길이는 16 + 5 = 21바이트다.
6. 헤더가 PTN `C`(PositionUp)를 비웠으므로 필드 순서표상 East 뒤, Status 앞에 i32 4바이트가 있다. 하드코딩한 디코더는 PositionUp의 첫 바이트를 Status로, 그다음 바이트를 #DLV로 읽어 (DLVn, 값) 쌍을 엉뚱한 위치에서 찾고, 가변 길이라 두 번째 레코드부터 경계가 통째로 밀린다. 2.3절 코드처럼 헤더의 빈 속성 목록에서 필드 순서표 순서로 고정부 형식을 매번 만들어야 한다. 바이트 순서는 리틀 엔디언(`<`)으로, 정렬 패딩 없이 읽는다.
:::

## 다음 챕터

- 다음: [부록: 용어집](/study/isobus/appendix-glossary)
