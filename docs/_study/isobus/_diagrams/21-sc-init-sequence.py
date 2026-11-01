"""CH21 §3.3 SC 초기화 메시지 흐름: ISO 11783-14 4.4.2, Figure 6~8 재구성 (light/dark PNG)."""
from _common import diagram

VT, SCM, SCC = 10, 42, 86

# (from, to, label, response?)
ROWS = [
    (SCM, VT, "SCMOP 업로드 (External Object Pointer = NULL)", False),
    (SCM, SCC, "SCMasterStatus 0x95: Active, Ready (연속)", False),
    (SCC, SCM, "SCClientStatus 0x96: Initialization 1회 후 Disabled 연속", False),
    (SCC, SCM, "SCMasterCapabilityRequest 0x90", False),
    (SCM, SCC, "SCMasterCapabilityResponse 0x90 (10바이트, TP)", True),
    (SCC, VT, "SCCOP 업로드 (Part 6)", False),
    (SCC, SCM, "SCDVersionRequest 0x01", False),
    (SCM, SCC, "SCDVersionResponse 0x01", True),
    (SCC, SCM, "SCDConfigurationLabelRequest 0x02", False),
    (SCM, SCC, "SCDConfigurationLabelResponse 0x02", True),
    (SCC, SCM, "SCMasterMemoryRequest 0x91 (SCD 바이트 수)", False),
    (SCM, SCC, "SCMasterMemoryResponse 0x91 (00 = 진행)", True),
    (SCC, SCM, "SCDTransfer 0x03 (TP / ETP)", False),
    (SCM, SCC, "SCDTransferResponse 0x03", True),
    (SCC, SCM, "SCDLoadCommand 0x07", False),
    (SCM, SCC, "SCDLoadResponse 0x07", True),
    (SCC, SCM, "SCDActivationCommand 0x04", False),
    (SCM, SCC, "SCMasterStatus 0x95: busy 비트 2 (SCD 파싱 중)", False),
    (SCM, SCC, "SCDActivationResponse 0x04 (00 = 정상)", True),
    (SCC, SCM, "SCDStoreCommand 0x06 (선택)", False),
    (SCM, SCC, "SCDStoreCommandResponse 0x06", True),
    (SCM, VT, "External Object Pointer 설정 (Change Attribute)", False),
    (SCM, SCC, "SCStateCommand 0x30: Enabled", False),
    (SCC, SCM, "SCClientStatus 0x96: Enabled, Ready", False),
]

Y0, STEP = 88.0, 3.5


def row_y(i):
    return Y0 - i * STEP - (0.8 if i >= 12 else 0) - (0.8 if i >= 16 else 0)


def draw(d):
    P = d.P

    for x, name in ((VT, "VT\n(function instance 0)"), (SCM, "SCM"), (SCC, "SCC")):
        d.box(x - 9, 92.5, 18, 6, P["blue"] if name == "SCM" else P["chip"])
        d.text(x, 95.5, name, size=10, weight="bold")
        d.arrow(x, 92.3, x, 2.5, color=P["edge"], lw=1.0, style="-", ls="--")

    # alt 구간: SCDTransfer 또는 SCDLoadCommand
    top, mid, bot = row_y(12) + 2.4, row_y(13) - 1.3, row_y(15) - 1.3
    d.box(36.5, bot, 62, top - bot, P["gray"], ec=P["orange"], lw=1.1, alpha=0.55)
    d.arrow(36.5, mid, 98.5, mid, color=P["orange"], lw=1.0, style="-", ls="--")
    d.text(37.5, top - 1.1, "alt", size=8.5, color=P["orange"], weight="bold", ha="left")
    d.text(88, row_y(12) - 0.4, "SCD 없음\n또는 불일치", size=8, color=P["dim"], ha="left")
    d.text(88, row_y(14) - 0.4, "저장된 SCD\n사용", size=8, color=P["dim"], ha="left")

    for i, (a, b, label, resp) in enumerate(ROWS):
        y = row_y(i)
        d.arrow(a, y, b, y, lw=1.4, ls="--" if resp else "-")
        if VT in (a, b) and SCC in (a, b):
            lx = 26
        elif VT in (a, b):
            lx = (VT + SCM) / 2
        else:
            lx = (SCM + SCC) / 2
        d.text(lx, y + 1.15, label, size=8.3)


diagram("21-sc-init-sequence", draw, w=12, h=11.5, xmax=100, ymax=100)
