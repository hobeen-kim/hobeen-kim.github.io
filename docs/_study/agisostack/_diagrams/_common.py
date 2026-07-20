"""관측성 스터디 다이어그램 공통 헬퍼 (matplotlib → 라이트/다크 PNG 2벌).

사용법:
    from _common import diagram

    def draw(d):
        P = d.P
        d.box(2, 2, 24, 8, P["blue"])
        d.text(14, 6, "Retrieval\n(scrape manager)")
        d.arrow(26, 6, 34, 6, color=P["accent"])

    diagram("05-core-components", draw, w=12, h=6, ymax=40)

diagram()이 라이트/다크 팔레트로 각각 렌더링해
{name}-light.png / {name}-dark.png 두 장을 저장한다.

스타일 원칙 (가벼운 보조 그림):
- 그림에는 구조(노드·그룹·화살표·라벨)만 담는다. 설명은 본문 몫이다.
- 대제목·부제·하단 요약 문장을 넣지 않는다.
- 범례는 색이 정보를 담을 때만 최소로.
- figsize는 내용 크기에 맞춘다 (기본 12×6, 복잡하면 14×8 정도까지).
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D  # noqa: F401 (re-export)


def set_korean_font():
    avail = {f.name for f in fm.fontManager.ttflist}
    for name in ("AppleSDGothicNeo", "Apple SD Gothic Neo", "AppleGothic",
                 "NanumGothic", "Malgun Gothic", "Noto Sans CJK KR"):
        if name in avail:
            plt.rcParams["font.family"] = name
            break
    plt.rcParams["axes.unicode_minus"] = False


PALETTES = {
    "dark": {
        "bg": "#0f1216",
        "text": "#e6e8eb",
        "dim": "#9aa2ab",
        "accent": "#4fd1c5",
        "edge": "#5b6570",
        "blue": "#2e4a5a",
        "green": "#3a5a3f",
        "brown": "#5a4638",
        "purple": "#4a3d63",
        "gray": "#26313a",
        "chip": "#1b232a",     # 그룹 박스 안 작은 칩
        "orange": "#e0a86b",   # 보조 화살표·라벨
        "violet": "#b9a3e0",   # 보조 화살표·라벨
    },
    "light": {
        "bg": "#ffffff",
        "text": "#24292f",
        "dim": "#57606a",
        "accent": "#0f766e",
        "edge": "#8c959f",
        "blue": "#dbe9f6",
        "green": "#dcefdc",
        "brown": "#f3e8d9",
        "purple": "#e8e2f4",
        "gray": "#eef1f4",
        "chip": "#f6f8fa",
        "orange": "#c2620a",
        "violet": "#7c5cbf",
    },
}

OUT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", ".vuepress", "public", "images", "study-agisostack"))


class _Ctx:
    """draw 콜백에 넘겨주는 그리기 컨텍스트."""

    def __init__(self, fig, ax, P):
        self.fig = fig
        self.ax = ax
        self.P = P

    def box(self, x, y, w, h, fc, ec=None, lw=1.4, r=0.03, alpha=1.0):
        self.ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r*20}",
            linewidth=lw, edgecolor=ec or self.P["edge"], facecolor=fc,
            alpha=alpha, mutation_aspect=1))

    def text(self, x, y, s, size=11, color=None, weight="normal",
             ha="center", va="center", style="normal"):
        self.ax.text(x, y, s, fontsize=size, color=color or self.P["text"],
                     fontweight=weight, ha=ha, va=va, style=style, zorder=5)

    def arrow(self, x1, y1, x2, y2, color=None, lw=1.8, style="-|>",
              rad=0.0, ls="-"):
        self.ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=14,
            linewidth=lw, color=color or self.P["accent"],
            connectionstyle=f"arc3,rad={rad}", linestyle=ls, zorder=4))

    def legend(self, handles, loc="lower left", anchor=(0.005, 0.005), fontsize=8.5):
        self.ax.legend(handles=handles, loc=loc, bbox_to_anchor=anchor,
                       fontsize=fontsize, framealpha=0.0,
                       labelcolor=self.P["dim"])


def diagram(name, draw, w=12, h=6, xmax=100, ymax=50):
    """라이트/다크 두 벌을 렌더링해 {name}-light.png / {name}-dark.png 저장."""
    set_korean_font()
    os.makedirs(OUT_DIR, exist_ok=True)
    for theme, P in PALETTES.items():
        fig, ax = plt.subplots(figsize=(w, h))
        fig.patch.set_facecolor(P["bg"])
        ax.set_facecolor(P["bg"])
        ax.set_xlim(0, xmax)
        ax.set_ylim(0, ymax)
        ax.axis("off")
        draw(_Ctx(fig, ax, P))
        plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
        out = os.path.join(OUT_DIR, f"{name}-{theme}.png")
        fig.savefig(out, dpi=170, facecolor=P["bg"])
        plt.close(fig)
        print("saved", out)
