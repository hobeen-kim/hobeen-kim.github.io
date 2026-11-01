"""CH55 §3 VT 메인 화면(Data Mask 0x0010)과 설정 화면(Data Mask 0x0011) 구성과 전환 (light/dark PNG)."""
from _common import diagram


def chip(d, x, y, w, h, fc, title, sub, size=8.5):
    d.box(x, y, w, h, fc)
    d.text(x + w / 2, y + h * 0.64, title, size=size, weight="bold")
    d.text(x + w / 2, y + h * 0.28, sub, size=7.5, color=d.P["dim"])


def draw(d):
    P = d.P
    # Main screen group
    d.box(1, 6, 44.5, 42, P["gray"], ec=P["accent"])
    d.text(3, 45.8, "메인 화면", size=10.5, weight="bold", ha="left", color=P["accent"])
    d.text(14, 45.8, "Data Mask 0x0010", size=9, ha="left", color=P["dim"])
    d.box(3, 8, 32, 32, P["chip"])

    d.box(4.5, 29.5, 29, 9, P["blue"])
    d.text(5.5, 37.3, "Container 0x0050", size=7.5, ha="left", color=P["dim"])
    chip(d, 5.8, 30.4, 13, 5.2, P["green"], "Engine RPM", "0x0060")
    chip(d, 20.1, 30.4, 12.6, 5.2, P["green"], "1600 rpm", "0x0020")

    d.box(4.5, 19, 29, 9, P["blue"])
    d.text(5.5, 26.8, "Container 0x0051", size=7.5, ha="left", color=P["dim"])
    chip(d, 5.8, 19.9, 13, 5.2, P["green"], "Speed (km/h)", "0x0061")
    chip(d, 20.1, 19.9, 12.6, 5.2, P["green"], "8.5 km/h", "0x0021")

    chip(d, 4.5, 9.8, 29, 7, P["green"], "WORKING", "Work Status  Output String 0x0022", size=9.5)

    d.text(40.3, 42.6, "Soft Key Mask\n0x0040", size=7.5, color=P["dim"])
    for y, name, oid in [(32.5, "Settings", "0x0041"), (24.5, "Work ON", "0x0042"),
                         (16.5, "Work OFF", "0x0043")]:
        chip(d, 36.5, y, 7.6, 6.5, P["brown"], name, oid, size=8)

    # Settings screen group
    d.box(54.5, 6, 44.5, 42, P["gray"], ec=P["accent"])
    d.text(56.5, 45.8, "설정 화면", size=10.5, weight="bold", ha="left", color=P["accent"])
    d.text(67.5, 45.8, "Data Mask 0x0011", size=9, ha="left", color=P["dim"])
    d.box(56.5, 8, 32, 32, P["chip"])
    chip(d, 59, 19.5, 27, 9, P["purple"], "Target Rate  0x0030", "Input Number  0~600 L/ha", size=9.5)

    d.text(93.8, 42.6, "소프트키", size=7.5, color=P["dim"])
    chip(d, 90, 9.5, 7.6, 6.5, P["brown"], "Back", "to Main", size=8)

    # Settings key -> settings screen
    d.arrow(44.1, 35.75, 54.5, 35.75)
    d.text(49.3, 38.3, "Settings 키", size=8.5, color=P["accent"])

    # Back key -> main screen (routed under both groups)
    lw = 1.8
    d.ax.plot([93.8, 93.8], [9.5, 3.0], color=P["accent"], lw=lw, zorder=4)
    d.ax.plot([93.8, 23.25], [3.0, 3.0], color=P["accent"], lw=lw, zorder=4)
    d.arrow(23.25, 3.0, 23.25, 6.0)
    d.text(58.5, 1.4, "Back 키", size=8.5, color=P["accent"])


diagram("55-vt-screen-layout", draw, w=12, h=6, xmax=100, ymax=50)
