#!/usr/bin/env python3
"""knowledge-graph.js 노드 좌표 겹침 점검·빈자리 추천.

사용법:
    python3 .claude/skills/study-add/scripts/kg_spot.py 0.79 0.47          # 후보 좌표 점검
    python3 .claude/skills/study-add/scripts/kg_spot.py 0.79 0.47 --suggest  # 근처 빈자리 추천

좌표는 화면 비율(0~1). 기본 최소 거리 0.06 (노드 원·라벨이 겹치지 않는 경험치).
"""
import argparse
import math
import os
import re
import subprocess
import sys


def load_nodes(path):
    text = open(path, encoding="utf-8").read()
    nodes = []
    for m in re.finditer(r"\{\s*id:\s*'([^']+)'[^}]*?x:\s*([0-9.]+),\s*y:\s*([0-9.]+)", text):
        nodes.append((m.group(1), float(m.group(2)), float(m.group(3))))
    return nodes


def nearest(nodes, x, y, k=5):
    return sorted(((math.hypot(nx - x, ny - y), nid, nx, ny) for nid, nx, ny in nodes))[:k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("x", type=float)
    ap.add_argument("y", type=float)
    ap.add_argument("--min", type=float, default=0.06)
    ap.add_argument("--suggest", action="store_true")
    args = ap.parse_args()

    root = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                          capture_output=True, text=True).stdout.strip()
    path = os.path.join(root, "docs", ".vuepress", "data", "knowledge-graph.js")
    nodes = load_nodes(path)
    if not nodes:
        sys.exit(f"노드를 읽지 못했다: {path}")

    def report(x, y):
        near = nearest(nodes, x, y)
        ok = near[0][0] >= args.min
        print(f"({x:.2f}, {y:.2f}) → {'OK' if ok else 'TOO CLOSE'} (최소 {args.min})")
        for d, nid, nx, ny in near:
            print(f"  {d:.3f}  {nid} ({nx}, {ny})")
        return ok

    if report(args.x, args.y) or not args.suggest:
        return
    # 나선형으로 0.01 간격 탐색해 가장 가까운 빈자리를 찾는다
    for r in range(1, 30):
        cands = []
        for i in range(-r, r + 1):
            for j in (-r, r):
                cands += [(args.x + i * 0.01, args.y + j * 0.01), (args.x + j * 0.01, args.y + i * 0.01)]
        cands = [(x, y) for x, y in cands if 0.02 <= x <= 0.98 and 0.05 <= y <= 0.95]
        cands.sort(key=lambda p: math.hypot(p[0] - args.x, p[1] - args.y))
        for x, y in cands:
            if nearest(nodes, x, y, 1)[0][0] >= args.min:
                print("\n추천:")
                report(round(x, 2), round(y, 2))
                return
    print("반경 0.3 안에 빈자리가 없다. --min을 낮추거나 다른 영역을 고르라.")


if __name__ == "__main__":
    main()
