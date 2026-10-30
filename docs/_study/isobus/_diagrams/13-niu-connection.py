"""CH13 §8 NIU connection 수립과 virtual CF를 거친 메시지 전달 시퀀스 (light/dark PNG)."""
from _common import diagram

XA, XP1, XP2, XC = 12, 42, 58, 88


def msg(d, x1, x2, y, label, color=None, ls="-"):
    d.arrow(x1, y, x2, y, color=color, ls=ls)
    d.text((x1 + x2) / 2, y + 1.3, label, size=9)


def draw(d):
    P = d.P
    top = 51

    d.text((XA + XP1) / 2, top + 4.2, "Network 1", size=10, weight="bold", color=P["dim"])
    d.text((XP2 + XC) / 2, top + 4.2, "Network 2", size=10, weight="bold", color=P["dim"])

    d.box(XA - 8, top - 2, 16, 4, P["blue"])
    d.text(XA, top, "CF A (0x85)", size=10, weight="bold")
    d.box(XC - 8, top - 2, 16, 4, P["green"])
    d.text(XC, top, "CF C (0x86)", size=10, weight="bold")
    d.box(XP1 - 6, top - 2, (XP2 - XP1) + 12, 4, P["brown"])
    d.text((XP1 + XP2) / 2, top, "NIU B", size=10, weight="bold")
    d.text(XP1, top - 3.4, "P1", size=8.5, color=P["dim"])
    d.text(XP2, top - 3.4, "P2", size=8.5, color=P["dim"])

    for x in (XA, XC):
        d.arrow(x, top - 2.2, x, 5, color=P["edge"], lw=1.0, style="-", ls="--")
    for x in (XP1, XP2):
        d.arrow(x, top - 4.3, x, 33.2, color=P["edge"], lw=1.0, style="-", ls="--")
        d.arrow(x, 30.0, x, 5, color=P["edge"], lw=1.0, style="-", ls="--")

    msg(d, XA, XP1, 43.5, "N.NTX_Request (66, port 2)")
    msg(d, XP1, XA, 39.5, "N.NTX_Response (67: B, C, D)")
    msg(d, XA, XP1, 35.5, "N.OC_Request (192, NAME = C)")

    d.box(XP1 - 5, 30.2, 10, 2.8, P["purple"])
    d.text(XP1, 31.6, "C^ = 0x90", size=8.5, weight="bold")
    d.box(XP2 - 5, 30.2, 10, 2.8, P["purple"])
    d.text(XP2, 31.6, "A^ = 0x91", size=8.5, weight="bold")

    msg(d, XP1, XA, 27.0, "Address Claim C^", color=P["violet"])
    msg(d, XP2, XC, 27.0, "Address Claim A^", color=P["violet"])

    msg(d, XA, XP1, 21.5, "Request(DM2)  SA 0x85 -> DA 0x90")
    d.arrow(XP1, 19.5, XP2, 19.5, color=P["orange"], lw=1.4, ls="--")
    msg(d, XP2, XC, 17.5, "Request(DM2)  SA 0x91 -> DA 0x86")

    msg(d, XC, XP2, 12.5, "DM2 (SA 0x86)")
    d.arrow(XP2, 10.5, XP1, 10.5, color=P["orange"], lw=1.4, ls="--")
    msg(d, XP1, XA, 8.5, "DM2 (SA 0x90)")


diagram("13-niu-connection", draw, w=13, h=7.2, xmax=100, ymax=57)
