"""CH22 §5 TASKDATA 디렉터리 파일 세트와 참조 관계 (light/dark PNG)."""
from _common import diagram

LINKS = [
    # (y, chip text in TASKDATA.XML, [(file name, sub label), ...])
    (37.0, 'PFD > PLN > LSG > PNT   J="PNT00001"', [("PNT00001.BIN", "Point 레코드 (v4)")]),
    (29.5, 'GRD   G="GRD00001"', [("GRD00001.BIN", "셀 값 (type 1·2)")]),
    (21.0, 'TLG   A="TLG00001"', [("TLG00001.XML", "레코드 구조 헤더"), ("TLG00001.BIN", "로그 레코드")]),
    (11.5, 'XFR   A="TSK00002"  B="1"', [("TSK00002.XML", "루트 요소 XFC")]),
    (5.0, 'AFE   A="LINKLIST.XML"  D="1"', [("LINKLIST.XML", "루트 ISO11783LinkList (v4)")]),
]


def draw(d):
    P = d.P
    d.box(1.5, 1.0, 97, 47.5, P["gray"], ec=P["accent"])
    d.text(4, 46.3, "TASKDATA/", size=11, weight="bold", ha="left", color=P["accent"])

    d.box(4, 2.2, 42, 41.6, P["blue"])
    d.text(25, 42.0, "TASKDATA.XML", size=11, weight="bold")
    d.text(25, 39.9, "<ISO11783_TaskData>", size=8.5, color=P["dim"])

    d.box(6, 17.2, 38, 16.6, P["chip"], ec=P["edge"], lw=1.0)
    d.text(7.2, 32.6, "TSK", size=9, weight="bold", ha="left", color=P["dim"])

    fx, fw, fh = 60, 33, 4.6
    for y, chip, files in LINKS:
        d.box(8, y - 1.7, 34, 3.4, P["chip"])
        d.text(9.2, y, chip, size=8.5, ha="left")
        if len(files) == 1:
            targets = [y]
        else:
            targets = [y + 2.7, y - 2.7]
        for (name, sub), ty in zip(files, targets):
            d.box(fx, ty - fh / 2, fw, fh, P["brown"])
            d.text(fx + fw / 2, ty + 0.9, name, size=9.5, weight="bold")
            d.text(fx + fw / 2, ty - 1.1, sub, size=8)
            d.arrow(42, y, fx, ty)


diagram("22-taskdata-fileset", draw, w=12, h=6, xmax=100, ymax=50)
