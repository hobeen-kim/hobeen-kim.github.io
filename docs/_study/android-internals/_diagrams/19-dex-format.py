"""CH19 DEX 파일 포맷 — header와 인덱스 테이블, data 영역 구조."""
from _common import diagram


def draw(d):
    P = d.P

    # 좌: 파일 섹션 순서
    d.box(4, 5, 34, 40, P["gray"], ec=P["accent"], lw=1.6)
    d.text(21, 42, "classes.dex", size=10.5, weight="bold", color=P["accent"])
    secs = [
        ("header", "magic·checksum·signature·오프셋", P["purple"]),
        ("string_ids", "문자열 상수 인덱스", P["blue"]),
        ("type_ids", "타입(클래스) 인덱스", P["blue"]),
        ("proto_ids", "메서드 시그니처", P["green"]),
        ("field_ids", "필드 인덱스", P["green"]),
        ("method_ids", "메서드 인덱스 (16bit)", P["brown"]),
        ("class_defs", "클래스 정의", P["brown"]),
        ("data / code_item", "바이트코드·문자열 본문", P["chip"]),
    ]
    for i, (name, desc, fc) in enumerate(secs):
        y = 37.5 - i * 4.2
        d.box(6, y, 30, 3.5, fc)
        d.text(11, y + 1.75, name, size=8, weight="bold", ha="left")
        d.text(35, y + 1.75, desc, size=6.6, color=P["dim"], ha="right")

    # 우: 참조 관계
    d.box(46, 14, 50, 26, P["chip"])
    d.text(71, 37, "인덱스는 서로를 참조", size=9.5, weight="bold", color=P["dim"])
    d.box(50, 27, 18, 6, P["brown"])
    d.text(59, 30, "method_id", size=8.5, weight="bold")
    d.box(74, 30, 18, 5, P["blue"])
    d.text(83, 32.5, "type_id", size=8)
    d.box(74, 22, 18, 5, P["green"])
    d.text(83, 24.5, "proto_id", size=8)
    d.box(74, 15, 18, 5, P["blue"])
    d.text(83, 17.5, "string_id (이름)", size=7.6)
    d.arrow(68, 31, 74, 32.5, color=P["orange"])
    d.text(71, 33.6, "정의 클래스", size=6.6, color=P["orange"])
    d.arrow(68, 30, 74, 24.5, color=P["orange"])
    d.text(71, 27.6, "시그니처", size=6.6, color=P["orange"])
    d.arrow(68, 29, 74, 17.5, color=P["orange"])
    d.text(71, 21.6, "메서드명", size=6.6, color=P["orange"])

    d.text(71, 10, "여러 DEX가 문자열/타입 풀을 공유 → 앱 전체 크기 절감",
           size=7.6, color=P["dim"])


diagram("19-dex-format", draw, w=13, h=6, ymax=46)
