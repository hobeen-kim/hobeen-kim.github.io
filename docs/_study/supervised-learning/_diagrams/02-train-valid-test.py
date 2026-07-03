"""CH2 train/valid/test 3분할 — 각 조각의 역할과 사용 시점 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 전체 데이터 바
    total_x, total_w = 6, 88
    d.text(total_x, 43, "전체 데이터", size=10, weight="bold", ha="left")

    parts = [
        ("Train", 0.6, P["blue"], "모델이 학습(fit)", "여러 번 반복해서 봄"),
        ("Valid", 0.2, P["green"], "튜닝·모델 선택", "간접적으로 정보 누출"),
        ("Test", 0.2, P["brown"], "최종 성능 1회 측정", "배포 전 마지막에만"),
    ]
    x = total_x
    for name, frac, fc, role, note in parts:
        w = total_w * frac
        d.box(x, 30, w, 9, fc)
        d.text(x + w / 2, 34.5, f"{name}\n{int(frac*100)}%", size=10, weight="bold")
        # 역할 설명 칩
        d.box(x + 0.5, 12, w - 1, 12, P["chip"])
        d.text(x + w / 2, 20, role, size=8.6)
        d.text(x + w / 2, 15.5, note, size=7.8, color=P["dim"], style="italic")
        d.arrow(x + w / 2, 30, x + w / 2, 24.5, color=P["edge"], lw=1.2)
        x += w

    # 순서 화살표
    d.text(total_x, 5.5, "학습 → 검증(반복) → 최종 테스트 (한 방향, 되돌아가지 않음)",
           size=8.6, color=P["dim"], ha="left", style="italic")
    d.arrow(total_x, 8, total_x + total_w, 8, color=P["accent"], lw=1.6)


diagram("02-train-valid-test", draw, w=12, h=5.2, ymax=48)
