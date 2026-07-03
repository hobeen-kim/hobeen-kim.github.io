"""CH20 trace tree — root span과 parent/child 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(cx, cy, title, meta, fc, bw=30, bh=6.6):
        d.box(cx - bw / 2, cy - bh / 2, bw, bh, fc)
        d.text(cx, cy + 1.2, title, size=11, weight="bold")
        d.text(cx, cy - 1.5, meta, size=8.5, color=P["accent"])

    node(50, 44, "root span: API Gateway", "trace_id=abc123 · span_id=a1", P["blue"], bw=42, bh=7)
    node(50, 32, "span: Order Service", "parent=a1 · span_id=b2", P["green"], bw=34)
    node(27, 20, "span: Payment Service", "parent=b2 · span_id=c3", P["brown"])
    node(72, 20, "span: Inventory Service", "parent=b2 · span_id=d4", P["brown"])
    node(27, 8, "span: DB Query (SELECT)", "parent=c3 · span_id=e5", P["gray"])

    d.arrow(50, 40.5, 50, 35.4, color=P["accent"])
    d.arrow(44, 28.6, 33, 23.4, color=P["accent"])
    d.arrow(56, 28.6, 66, 23.4, color=P["accent"])
    d.arrow(27, 16.6, 27, 11.4, color=P["accent"])


diagram("20-trace-tree", draw, w=13, h=6.5, ymax=52)
