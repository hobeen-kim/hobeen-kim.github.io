"""관측성 스터디 다이어그램 공통 헬퍼 (matplotlib → PNG)."""
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


# palette
C_BG = "#0f1216"
C_EDGE = "#5b6570"
C_TEXT = "#e6e8eb"
C_DIM = "#9aa2ab"
C_ACCENT = "#4fd1c5"
C_BLUE = "#2e4a5a"
C_GREEN = "#3a5a3f"
C_BROWN = "#5a4638"
C_PURPLE = "#4a3d63"
C_GRAY = "#26313a"
C_ORANGE = "#e0a86b"
C_VIOLET = "#b9a3e0"

OUT_DIR = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "..", "..", ".vuepress", "public", "images", "study-observability"))


def new_fig(w=15, h=9.2, xmax=100, ymax=62):
    set_korean_font()
    fig, ax = plt.subplots(figsize=(w, h))
    fig.patch.set_facecolor(C_BG)
    ax.set_facecolor(C_BG)
    ax.set_xlim(0, xmax)
    ax.set_ylim(0, ymax)
    ax.axis("off")
    return fig, ax


def make_helpers(ax):
    def box(x, y, w, h, fc, ec=C_EDGE, lw=1.4, r=0.03, alpha=1.0):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0.02,rounding_size={r*20}",
            linewidth=lw, edgecolor=ec, facecolor=fc, alpha=alpha,
            mutation_aspect=1))

    def text(x, y, s, size=11, color=C_TEXT, weight="normal",
             ha="center", va="center", style="normal"):
        ax.text(x, y, s, fontsize=size, color=color, fontweight=weight,
                ha=ha, va=va, style=style, zorder=5)

    def arrow(x1, y1, x2, y2, color=C_ACCENT, lw=2.0, style="-|>",
              rad=0.0, ls="-"):
        ax.add_patch(FancyArrowPatch(
            (x1, y1), (x2, y2), arrowstyle=style, mutation_scale=16,
            linewidth=lw, color=color, connectionstyle=f"arc3,rad={rad}",
            linestyle=ls, zorder=4))

    return box, text, arrow


def save(fig, name):
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, name)
    fig.savefig(out, dpi=170, facecolor=C_BG)
    print("saved", out)
