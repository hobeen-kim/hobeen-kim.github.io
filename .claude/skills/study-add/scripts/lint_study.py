#!/usr/bin/env python3
"""스터디 마크다운 기계 점검기.

사용법:
    python3 .claude/skills/study-add/scripts/lint_study.py <slug> [--pending] [--root <repo>]

    --pending  집필 도중용. 같은 스터디 안에서 아직 만들어지지 않은 파일을 가리키는
               링크·prev/next를 ERROR 대신 WARN으로 낮춘다(부록·다음 웨이브 챕터).
               최종 점검에서는 빼고 돌린다.

점검 항목 (ERROR는 빌드 실패·렌더링 깨짐, WARN은 규칙 위반·의심):
- frontmatter 필수 키, h1 제목
- 금지 패턴: <br/>, **bold**한글, 본문 {{ }}, GitHub callout, frontmatter 밖 ---,
  경어체 문장, 체크박스(- [ ]), mermaid 펜스
- 이미지 참조 파일 존재, light/dark 짝
- 내부 링크(/study/..., /posts/...) 대상 파일 존재
- prev/next 체인 상호 일치
- config.mjs sidebar 등록, knowledge-graph.js 노드 등록
- 챕터당 다이어그램 2개 이상

종료 코드: ERROR가 하나라도 있으면 1.
"""
import argparse
import os
import re
import sys

FM_KEYS = ("title", "description", "date", "tags")
CHAPTER_FM_KEYS = ("prev", "next")

RE_BR = re.compile(r"<br\s*/>")
RE_BOLD_HANGUL = re.compile(r"\*\*[^*\n]+?\*\*[가-힣]")
RE_MUSTACHE = re.compile(r"\{\{")
RE_CALLOUT = re.compile(r"^\s*>\s*\[!(TIP|NOTE|INFO|WARNING|IMPORTANT|CAUTION)\]", re.I)
RE_HONORIFIC = re.compile(r"(입니다|합니다|습니다|됩니다|있어요|해요)[.!?]?\s*$")
RE_TASK = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s")
RE_IMG = re.compile(r"!\[([^\]]*)\]\((/images/[^)\s]+)\)")
RE_LINK = re.compile(r"(?<!!)\[[^\]]*\]\((/(?:study|posts)/[^)\s]*)\)")
RE_INLINE_CODE = re.compile(r"`[^`\n]*`")
RE_FENCE = re.compile(r"^\s*(```|~~~)")


def find_root(start):
    cur = os.path.abspath(start)
    while cur != "/":
        if os.path.isdir(os.path.join(cur, "docs", ".vuepress")):
            return cur
        cur = os.path.dirname(cur)
    return None


def split_frontmatter(lines):
    """frontmatter dict, 본문 시작 줄 인덱스(0-based) 반환."""
    if not lines or lines[0].strip() != "---":
        return None, 0
    fm = {}
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return fm, i + 1
        m = re.match(r"^([A-Za-z_]+):\s*(.*)$", lines[i])
        if m:
            fm[m.group(1)] = m.group(2).strip().strip("'\"")
    return None, 0


def body_lines(lines, start):
    """코드 펜스 밖 본문 줄만 (줄번호, 인라인 코드 제거한 텍스트)으로 산출."""
    in_fence = False
    for i in range(start, len(lines)):
        line = lines[i]
        if RE_FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        yield i + 1, RE_INLINE_CODE.sub("", line)


def resolve_link(root, url):
    url = url.split("#")[0].split("?")[0]
    if url.endswith(".html"):
        url = url[:-5]
    if url.startswith("/study/"):
        rel = url[len("/study/"):]
        base = os.path.join(root, "docs", "_study", rel)
    else:
        rel = url[len("/posts/"):]
        base = os.path.join(root, "docs", "_posts", rel)
    if url.endswith("/"):
        return os.path.isfile(os.path.join(base, "README.md")) or \
            os.path.isfile(os.path.join(base, "index.md"))
    return os.path.isfile(base + ".md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--root", default=None)
    ap.add_argument("--pending", action="store_true")
    args = ap.parse_args()
    own_prefix = f"/study/{args.slug}/"

    def missing_level(url):
        return "WARN" if args.pending and url.startswith(own_prefix) else "ERROR"

    root = args.root or find_root(os.getcwd()) or find_root(os.path.dirname(__file__))
    if not root:
        sys.exit("repo root(docs/.vuepress가 있는 디렉토리)를 찾지 못했다. --root로 지정하라.")
    study_dir = os.path.join(root, "docs", "_study", args.slug)
    if not os.path.isdir(study_dir):
        sys.exit(f"스터디 디렉토리가 없다: {study_dir}")
    public = os.path.join(root, "docs", ".vuepress", "public")

    issues = []  # (level, file, line, msg)

    def add(level, f, line, msg):
        issues.append((level, f, line, msg))

    files = sorted(f for f in os.listdir(study_dir) if f.endswith(".md"))
    chain = {}  # page path -> (prev, next)

    for fname in files:
        path = os.path.join(study_dir, fname)
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().split("\n")
        fm, start = split_frontmatter(lines)
        is_readme = fname == "README.md"
        page = f"/study/{args.slug}/" if is_readme else f"/study/{args.slug}/{fname[:-3]}"

        if fm is None:
            add("ERROR", fname, 1, "frontmatter가 없다")
            fm, start = {}, 0
        for k in FM_KEYS:
            if k not in fm:
                add("ERROR", fname, 1, f"frontmatter '{k}' 누락")
        if not is_readme:
            for k in CHAPTER_FM_KEYS:
                if k not in fm:
                    add("WARN", fname, 1, f"frontmatter '{k}' 누락")
            chain[page] = (fm.get("prev"), fm.get("next"))

        head = lines[start:start + 6]
        if not any(l.startswith("# ") for l in head):
            if any("<Header" in l for l in head):
                add("WARN", fname, start + 1, "h1 대신 <Header /> — 새 챕터는 # 제목을 쓴다")
            else:
                add("ERROR", fname, start + 1, "frontmatter 직후 h1(# 제목)이 없다")
        if not is_readme and not fname.startswith("appendix") and \
                not any(re.match(r"^:::\s*details\s+확인 문제", l) for l in lines):
            add("WARN", fname, 0, "확인 문제(::: details 확인 문제) 없음")

        light_refs = 0
        prev_img = None
        for ln, text in body_lines(lines, start):
            if RE_BR.search(text):
                add("ERROR", fname, ln, "<br/> 사용 — Vue 컴파일 에러. <br>로 바꿔라")
            if RE_MUSTACHE.search(text):
                add("ERROR", fname, ln, "본문 {{ — Vue 보간으로 해석된다. 코드 블록/인라인 코드로 감싸라")
            if RE_BOLD_HANGUL.search(text):
                add("WARN", fname, ln, "**bold**한글 — <strong>bold</strong>한글로 바꿔라")
            if RE_CALLOUT.search(text):
                add("ERROR", fname, ln, "GitHub callout(> [!TIP]) — ::: tip 컨테이너를 써라")
            if text.strip() == "---":
                add("WARN", fname, ln, "frontmatter 밖 --- 수평선 — 제거하라")
            if RE_TASK.search(text):
                add("WARN", fname, ln, "체크박스(- [ ]) — 이 블로그는 렌더링하지 않는다. 일반 목록으로")
            if RE_HONORIFIC.search(text) and not text.lstrip().startswith((">", "|")):
                add("WARN", fname, ln, "경어체 문장 — 해라체(~이다/~한다)로")

            for m in RE_IMG.finditer(text):
                src = m.group(2)
                if not os.path.isfile(os.path.join(public, src.lstrip("/"))):
                    add("ERROR", fname, ln, f"이미지 파일 없음: {src}")
                if src.endswith("-light.png"):
                    light_refs += 1
                    prev_img = (ln, src)
                elif src.endswith("-dark.png"):
                    if not prev_img or prev_img[1] != src.replace("-dark.png", "-light.png") \
                            or prev_img[0] != ln - 1:
                        add("WARN", fname, ln, f"-dark.png 바로 윗줄에 짝 -light.png가 없다: {src}")
                    prev_img = None
            for m in RE_LINK.finditer(text):
                if not resolve_link(root, m.group(1)):
                    add(missing_level(m.group(1)), fname, ln, f"깨진 내부 링크: {m.group(1)}")

        # 본문 코드 펜스 안까지 포함해 mermaid 사용 여부만 확인
        if any(re.match(r"^\s*```mermaid", l) for l in lines):
            add("WARN", fname, 0, "mermaid 펜스 — 새 다이어그램은 matplotlib PNG로")
        if not is_readme and not fname.startswith("appendix") and light_refs < 2:
            add("WARN", fname, 0, f"다이어그램 {light_refs}개 — 챕터당 2개 이상 권장")

    # prev/next 체인
    for page, (prev, nxt) in chain.items():
        for kind, target in (("prev", prev), ("next", nxt)):
            if not target or target in ("false", "null"):
                continue
            if target.startswith("/") and not resolve_link(root, target):
                add(missing_level(target), page.rsplit("/", 1)[-1] + ".md", 1,
                    f"{kind} 대상 없음: {target}")
        if nxt and nxt in chain and chain[nxt][0] != page:
            add("WARN", page.rsplit("/", 1)[-1] + ".md", 1,
                f"next={nxt} 인데 그쪽 prev={chain[nxt][0]}")

    # sidebar
    cfg = os.path.join(root, "docs", ".vuepress", "config.mjs")
    if os.path.isfile(cfg):
        text = open(cfg, encoding="utf-8").read()
        if f"'/study/{args.slug}/':" not in text:
            add("ERROR", "config.mjs", 0, f"sidebar에 '/study/{args.slug}/' 블록이 없다")
        else:
            for fname in files:
                if fname == "README.md":
                    continue
                link = f"/study/{args.slug}/{fname[:-3]}"
                if f"'{link}'" not in text:
                    add("WARN", "config.mjs", 0, f"sidebar에 {link} 링크가 없다")

    # knowledge graph
    kg = os.path.join(root, "docs", ".vuepress", "data", "knowledge-graph.js")
    if os.path.isfile(kg):
        if f"link: '/study/{args.slug}/'" not in open(kg, encoding="utf-8").read():
            add("WARN", "knowledge-graph.js", 0, f"노드 link '/study/{args.slug}/' 가 없다")

    errors = [i for i in issues if i[0] == "ERROR"]
    warns = [i for i in issues if i[0] == "WARN"]
    for level, f, ln, msg in sorted(issues, key=lambda x: (x[1], x[2])):
        loc = f"{f}:{ln}" if ln else f
        print(f"[{level}] {loc} — {msg}")
    print(f"\n{args.slug}: 파일 {len(files)}개, ERROR {len(errors)}, WARN {len(warns)}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
