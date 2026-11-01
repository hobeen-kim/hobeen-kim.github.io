"""51장 2절 FS 파일 계층(옛 21장 mermaid graph TD를 옮김): FS, 볼륨, 디렉터리, 파일 (light/dark PNG)."""
from _common import diagram

COLS = {"fs": (2, 18), "vol": (23, 45), "dir": (50, 70), "file": (75, 99)}
H = 6.0


def node(d, col, yc, title, sub=None, fc=None):
    x0, x1 = COLS[col]
    d.box(x0, yc - H / 2, x1 - x0, H, fc)
    if sub:
        d.text((x0 + x1) / 2, yc + 1.2, title, size=9.5, weight="bold")
        d.text((x0 + x1) / 2, yc - 1.4, sub, size=8.3, color=d.P["dim"])
    else:
        d.text((x0 + x1) / 2, yc, title, size=9.2)


def link(d, c0, y0, c1, y1):
    d.arrow(COLS[c0][1] + 0.3, y0, COLS[c1][0] - 0.3, y1, color=d.P["edge"], lw=1.3)


def draw(d):
    P = d.P
    for col, label in (("fs", "볼륨 목록 \\\\"), ("vol", "볼륨"), ("dir", "디렉터리"), ("file", "파일")):
        x0, x1 = COLS[col]
        d.text((x0 + x1) / 2, 52, label, size=9.5, color=P["accent"], weight="bold")

    y_f = [45, 37, 26, 18]
    y_d1, y_d2 = (y_f[0] + y_f[1]) / 2, (y_f[2] + y_f[3]) / 2
    y_v1, y_v2 = (y_d1 + y_d2) / 2, 7
    y_fs = (y_v1 + y_v2) / 2

    node(d, "fs", y_fs, "File Server", "(ISO 11783-13)", P["blue"])
    node(d, "vol", y_v1, "Volume: FLASH", "(내부 저장소)", P["green"])
    node(d, "vol", y_v2, "Volume: VOL_B", "(이동식 매체)", P["green"])
    node(d, "dir", y_d1, "Directory:", "prescriptions", P["brown"])
    node(d, "dir", y_d2, "Directory:", "logs", P["brown"])
    for y, name in zip(y_f, ("prescription_map_2026.xml", "field_boundary.shp",
                             "task_log_20260413.xml", "as_applied_20260413.bin")):
        node(d, "file", y, name, fc=P["chip"])

    link(d, "fs", y_fs, "vol", y_v1)
    link(d, "fs", y_fs, "vol", y_v2)
    link(d, "vol", y_v1, "dir", y_d1)
    link(d, "vol", y_v1, "dir", y_d2)
    link(d, "dir", y_d1, "file", y_f[0])
    link(d, "dir", y_d1, "file", y_f[1])
    link(d, "dir", y_d2, "file", y_f[2])
    link(d, "dir", y_d2, "file", y_f[3])


diagram("51-fs-hierarchy", draw, w=12, h=5.8, xmax=101, ymax=56)
