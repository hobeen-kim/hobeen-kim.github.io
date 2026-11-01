r"""52장 3절 경로 해석: current directory가 \\VOL_B\LOGS\일 때 요청 경로가 가리키는 위치 (light/dark PNG)."""
from _common import diagram

STEP_X = 8
# (row y, level, label, width)
NODES = {
    "root": (56, 0, r"\\ (볼륨 목록)", 17),
    "volb": (51, 1, "VOL_B", 10),
    "logs": (46, 2, "LOGS", 9),
    "task": (41, 3, "TASK.XML", 12),
    "cfg": (36, 2, "CFG", 8),
    "cfg_a": (31, 3, "A.TXT", 9),
    "mcmc_b": (26, 2, "MCMC0123", 13),
    "mcmc_b_a": (21, 3, "A.TXT", 9),
    "flash": (16, 1, "FLASH", 9),
    "mcmc_f": (11, 2, "MCMC0123", 13),
    "mcmc_f_a": (6, 3, "A.TXT", 9),
}
CHILDREN = {
    "root": ["volb", "flash"],
    "volb": ["logs", "cfg", "mcmc_b"],
    "logs": ["task"],
    "cfg": ["cfg_a"],
    "mcmc_b": ["mcmc_b_a"],
    "flash": ["mcmc_f"],
    "mcmc_f": ["mcmc_f_a"],
}
# (label y, request path, rule, target node)
REQUESTS = [
    (56, r"\\", "볼륨 목록", "root"),
    (41, "TASK.XML", "current directory 기준", "task"),
    (33.6, r"..\CFG\A.TXT", "..은 상위 디렉터리", "cfg_a"),
    (28.4, r"\CFG\A.TXT", r"\ 하나: current volume 루트", "cfg_a"),
    (21, r"~\A.TXT", "~: 전용 디렉터리", "mcmc_b_a"),
    (6, r"\\FLASH\~\A.TXT", "볼륨 이름 뒤의 ~", "mcmc_f_a"),
]
H = 3.6


def x0(key):
    return 3 + NODES[key][1] * STEP_X


def draw(d):
    P = d.P
    for parent, kids in CHILDREN.items():
        xv = x0(parent) + 2.5
        y_top = NODES[parent][0] - H / 2
        y_last = NODES[kids[-1]][0]
        d.arrow(xv, y_top, xv, y_last, color=P["edge"], lw=1.1, style="-")
        for k in kids:
            d.arrow(xv, NODES[k][0], x0(k), NODES[k][0], color=P["edge"], lw=1.1, style="-")

    for key, (y, level, label, w) in NODES.items():
        is_dir = "." not in label or key == "root"
        fc = P["green"] if level == 1 else (P["brown"] if is_dir else P["chip"])
        if key == "root":
            fc = P["blue"]
        ec = P["accent"] if key == "logs" else None
        d.box(x0(key), y - H / 2, w, H, fc, ec=ec, lw=2.2 if key == "logs" else 1.4)
        d.text(x0(key) + w / 2, y, label, size=9)
    lx = x0("logs") + NODES["logs"][3] + 1.5
    d.text(lx, NODES["logs"][0], "current directory", size=9, color=P["accent"], ha="left", weight="bold")

    for y, path, rule, target in REQUESTS:
        d.box(66, y - 2.1, 32, 4.2, P["gray"])
        d.text(67.5, y + 0.8, path, size=9, ha="left", weight="bold")
        d.text(67.5, y - 1.0, rule, size=7.8, ha="left", color=P["dim"])
        ty = NODES[target][0]
        tx = x0(target) + NODES[target][3] + 0.6
        d.arrow(65.6, y, tx, ty, lw=1.3, color=P["accent"])

    d.text(82, 60.5, "요청 경로", size=9.5, color=P["dim"], weight="bold")
    d.text(16, 60.5, "FS 안의 실제 위치", size=9.5, color=P["dim"], weight="bold")


diagram("52-fs-path-resolution", draw, w=12, h=6.8, xmax=100, ymax=63)
