"""CH12 NAME_A의 두 표기: 수치 표기(Byte 8부터)와 CAN 데이터 필드(Byte 1부터 전송) (light/dark PNG)."""
from _common import diagram

NAME = 0xA00882000D27A120
NUMERIC_BYTE8_FIRST = NAME.to_bytes(8, "big")
WIRE_BYTE1_FIRST = NAME.to_bytes(8, "little")


def draw(d):
    P = d.P
    x0, bw, gap = 28, 10.6, 1.2
    top_y, bottom_y, bh = 29, 9, 6.0

    d.text(25, top_y + bh / 2, "수치 표기\n(Byte 8부터)", size=9.2, ha="right", weight="bold")
    d.text(25, bottom_y + bh / 2, "CAN 데이터 필드\n(Byte 1부터 전송)", size=9.2, ha="right",
           weight="bold")

    def cx(slot):
        return x0 + slot * (bw + gap) + bw / 2

    highlight_by_numeric_slot = {0: P["accent"], 7: P["orange"]}
    for slot, b in enumerate(NUMERIC_BYTE8_FIRST):
        ec = highlight_by_numeric_slot.get(slot)
        d.box(cx(slot) - bw / 2, top_y, bw, bh, P["blue"], ec=ec, lw=2.0 if ec else 1.2)
        d.text(cx(slot), top_y + bh / 2, f"{b:02X}", size=12, weight="bold")
        d.text(cx(slot), top_y + bh + 2.0, f"Byte {8 - slot}", size=8.3, color=P["dim"])
    for wire_slot, b in enumerate(WIRE_BYTE1_FIRST):
        numeric_slot = 7 - wire_slot
        ec = highlight_by_numeric_slot.get(numeric_slot)
        d.box(cx(wire_slot) - bw / 2, bottom_y, bw, bh, P["green"], ec=ec,
              lw=2.0 if ec else 1.2)
        d.text(cx(wire_slot), bottom_y + bh / 2, f"{b:02X}", size=12, weight="bold")
        d.text(cx(wire_slot), bottom_y - 2.2, f"Byte {wire_slot + 1}", size=8.3,
               color=P["dim"])
        d.ax.plot([cx(numeric_slot), cx(wire_slot)], [top_y - 0.4, bottom_y + bh + 0.4],
                  color=ec or P["edge"], lw=1.8 if ec else 0.9, zorder=2)

    row_end = x0 + 8 * (bw + gap) - gap
    d.arrow(x0, 2.4, row_end, 2.4, color=P["dim"], lw=1.4)
    d.text(x0 - 1.0, 2.4, "먼저", size=8.2, ha="right", color=P["dim"])
    d.text(row_end + 0.6, 2.4, "나중", size=8.2, ha="left", color=P["dim"])


diagram("12-name-wire-order", draw, w=12.5, h=3.9, xmax=128, ymax=39)
