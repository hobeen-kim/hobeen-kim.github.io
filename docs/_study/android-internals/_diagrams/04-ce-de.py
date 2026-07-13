"""CH4 CE/DE 스토리지 — FBE 하에서 부팅 단계별로 열리는 저장 영역."""
from _common import diagram


def draw(d):
    P = d.P

    # 타임라인 축
    d.arrow(6, 8, 94, 8, color=P["edge"], lw=1.4)
    d.text(50, 4.5, "부팅 → 사용자 인증(PIN/패턴) 진행 방향", size=9,
           color=P["dim"])

    stages = [
        (8, 24, "부트 초기", "키 없음\n어떤 앱 데이터도\n복호화 불가", P["gray"]),
        (36, 24, "Direct Boot", "DE 키 언락\n/data/user_de 접근\ndirectBootAware 앱 동작", P["blue"]),
        (66, 26, "사용자 인증 후", "CE 키 언락\n/data/user/0 접근\n일반 앱 전체 동작", P["green"]),
    ]
    for x, w, title, body, fc in stages:
        d.box(x, 14, w, 20, fc)
        d.text(x + w / 2, 31, title, size=10, weight="bold", color=P["accent"])
        d.text(x + w / 2, 22, body, size=9)
        # 축 위 마커
        d.arrow(x + w / 2, 14, x + w / 2, 9, color=P["edge"], lw=1.1)

    # 스토리지 영역 라벨
    d.text(50, 40, "FBE(File-Based Encryption): 파일마다 키가 다름 — CE는 자격증명, DE는 기기 키로 보호",
           size=8.5, color=P["dim"], ha="center", style="italic")


diagram("04-ce-de", draw, w=12, h=5.2, ymax=44)
