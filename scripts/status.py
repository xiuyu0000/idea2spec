#!/usr/bin/env python3
"""显示 idea2spec 访谈的当前状态：spec 版本、对话轮次、审批轮与反馈、下一个可用编号、未决事项、变更与快照、审批台版本。

用法：python3 status.py <项目目录> [--spec spec.md] [--desk 审批台目录]

只读，不改任何文件。新会话开场、每轮收尾时各跑一次。
"""
import argparse
import re
import sys
from pathlib import Path

CLOSED = ("已定", "取消", "已取消", "记录在案", "已结案")
DESK_VERSION = "3.7.1"  # 本 skill 按这个版本的审批台（开源版）写；与 SKILL.md 依赖一节一致，适配新版时一起改
DESK_REPO = "https://github.com/xiuyu0000/interactive-approval-desk"
SKILL_DIR = Path(__file__).resolve().parent.parent
DESK_PLACES = "<项目>/skills/interactive-approval-desk、本 skill 旁边的 ../interactive-approval-desk、../approval_desk"


def find_desk(root, explicit=None):
    if explicit:  # 指定了就只认它，不悄悄换成别处的
        c = Path(explicit).expanduser()
        return c if (c / "round_template" / "build.py").is_file() else None
    cands = [root / "skills" / "interactive-approval-desk",      # 项目里固定版本的副本
             SKILL_DIR.parent / "interactive-approval-desk",     # 和本 skill 装在同一个 skills 目录（开源仓库的名字）
             SKILL_DIR.parent / "approval_desk"]                 # 旧的文件夹名
    for c in cands:
        if (c / "round_template" / "build.py").is_file():
            return c
    return None


def vtuple(v):
    """'3.7.1' → (3, 7, 1)；认不出时返回 None。"""
    m = re.fullmatch(r"v?(\d+(?:\.\d+)*)", (v or "").strip())
    if not m:
        return None
    t = [int(x) for x in m.group(1).split(".")]
    while len(t) > 1 and t[-1] == 0:
        t.pop()
    return tuple(t)


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return None


def table_rows(text):
    for line in (text or "").splitlines():
        s = line.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*", s):
            continue
        yield [c.strip() for c in s.strip("|").split("|")]


def coded(text, prefix):
    pat = re.compile(rf"{prefix}-\d+")
    return [cells for cells in table_rows(text) if cells and pat.fullmatch(cells[0])]


def n_of(code):
    return int(re.findall(r"\d+", code)[-1])


def summary(codes, prefix, width, seen=frozenset()):
    ns = sorted(set(n_of(c) for c in codes))
    top = max(ns + list(seen) + [0])
    nxt = f"→ 下一个 {prefix}-{top + 1:0{width}d}"
    if not ns:
        head = "无"
    else:
        head = f"{prefix}-{ns[0]:0{width}d}..{prefix}-{ns[-1]:0{width}d}（{len(ns)} 条）"
    extra = sorted(set(seen) - set(ns))
    note = ""
    if extra:
        shown = "、".join(f"{prefix}-{n:0{width}d}" for n in extra[:10]) + ("…" if len(extra) > 10 else "")
        note = f"\n  文中出现但没登记：{shown}（若是有效条目就补登记；编号不要再用）"
    return f"{head} {nxt}{note}"


def header_field(text, name):
    for cells in table_rows(text):
        if len(cells) >= 2 and cells[0] == name:
            return cells[1].replace("**", "")
    return None


def short(s, n):
    s = re.sub(r"\s+", " ", s or "")
    return s if len(s) <= n else s[:n] + "…"


def vkey(v):
    return tuple(int(x) for x in re.findall(r"\d+", v))


def mentions(root, prefixes):
    """收集项目里所有 .md 文件中出现过的编号（含未登记的），用来避免重复使用旧编号。"""
    found = {p: set() for p in prefixes}
    width = {"D": "3,4", "F": "3,4", "CR": "3,4", "Q": "2,3", "A": "2,3", "S": "2,3"}
    pats = {p: re.compile(rf"(?<![A-Za-z0-9-]){p}-(\d{{{width.get(p, '2,4')}}})(?!\d)") for p in prefixes}
    for f in root.rglob("*.md"):
        if any(part.startswith(".") for part in f.relative_to(root).parts):
            continue
        text = re.sub(r"`[^`\n]*`", "", read(f) or "")  # 反引号里多是示例，不算
        for p, pat in pats.items():
            found[p].update(n for n in (int(x) for x in pat.findall(text)) if n > 0)
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--spec", default="spec.md")
    ap.add_argument("--desk", help=f"审批台 skill 的目录；默认依次找 {DESK_PLACES}")
    a = ap.parse_args()
    root = Path(a.project_dir).expanduser()
    iv = root / "interview"
    if not iv.is_dir():
        sys.exit(f"没找到 {iv}；先运行 init_interview.py")
    hints = []
    seen = mentions(root, ["D", "F", "Q", "A", "S"])
    print(f"项目：{root}")

    spec = read(root / a.spec)
    if spec is None:
        print(f"契约：{a.spec} 尚未起草")
    else:
        ver = header_field(spec, "版本") or "?"
        st = header_field(spec, "状态") or "?"
        n_inf = sum(re.sub(r"`[^`]*`", "", l).count("[推断]") for l in spec.splitlines())
        print(f"契约：{a.spec} {ver}｜{short(st, 70)}｜[推断] {n_inf} 处")
        if n_inf and "已批准基线" in st:
            hints.append(f"{a.spec} 状态是已批准基线，但还有 {n_inf} 处 [推断]")

    logs = sorted((p for p in (iv / "log").glob("T*.md") if re.fullmatch(r"T\d+", p.stem)), key=lambda p: vkey(p.stem))
    if logs:
        last = logs[-1].stem
        print(f"对话轮次：最新 {last}（共 {len(logs)} 个 log）→ 下一轮 T{n_of(last) + 1:02d}")
    else:
        print("对话轮次：还没有 log → 下一轮 T01")

    rv = read(iv / "reviews" / "INDEX.md")
    rounds = [c for c in table_rows(rv) if c and re.fullmatch(r"R\d+", c[0])]
    if rounds:
        waiting = []
        for c in rounds:
            has_fb = any((iv / "reviews").glob(f"{c[0]}_*feedback.md"))
            if not has_fb:
                waiting.append(c[0])
        last = rounds[-1]
        topic = last[1] if len(last) > 1 else ""
        print(f"审批轮：{rounds[0][0]}..{last[0]}（最新：{short(topic, 40)}）→ 下一个 R{n_of(last[0]) + 1:02d}")
        if waiting:
            print(f"  等待反馈：{'、'.join(waiting)}（没有对应的 *_feedback.md）")
            hints.append(f"{'、'.join(waiting)} 等待用户说'反馈完成'")
    else:
        print("审批轮：还没有 → 下一个 R01")

    dec = read(iv / "registry" / "decisions.md")
    d_rows, f_rows = coded(dec, "D"), coded(dec, "F")
    print("已批准决定：" + summary([c[0] for c in d_rows], "D", 3, seen["D"]))
    pending = [c[0] for c in d_rows if c[-1] and ("部分有效" in c[-1] or ("待" in c[-1] and "取代" not in c[-1]))]
    if pending:
        more = "…" if len(pending) > 12 else ""
        print(f"  状态里还写着'部分有效/待…'的：{'、'.join(pending[:12])}{more}（定下来了就回头更新状态）")
    print("来源事实：" + summary([c[0] for c in f_rows], "F", 3, seen["F"]))

    oi = read(iv / "registry" / "open_items.md")
    q_rows, a_rows = coded(oi, "Q"), coded(oi, "A")
    print("议程与待决：" + summary([c[0] for c in q_rows], "Q", 2, seen["Q"]))
    print("假设：" + summary([c[0] for c in a_rows], "A", 2, seen["A"]))
    open_items = [c for c in q_rows + a_rows if not c[-1].startswith(CLOSED)]
    if open_items:
        print(f"  未结（{len(open_items)}）：")
        for c in open_items:
            topic = c[1] if len(c) > 1 else ""
            print(f"    {c[0]} {short(topic, 36)}｜{short(c[-1], 48)}")

    src = read(iv / "registry" / "sources.md")
    print("调研来源：" + summary([c[0] for c in coded(src, "S")], "S", 2, seen["S"]))

    crs = sorted((iv / "changes").glob("CR-*.md")) if (iv / "changes").is_dir() else []
    if crs:
        items = []
        for p in crs:
            m = re.search(r"^status:\s*(.+)$", read(p) or "", re.M)
            items.append(f"{p.name.split('_')[0]}（{short(m.group(1) if m else '?', 30)}）")
        nxt = max(n_of(p.name.split("_")[0]) for p in crs) + 1
        print(f"变更：{'；'.join(items)} → 下一个 CR-{nxt:03d}")
    else:
        print("变更：无 → 下一个 CR-001")

    snaps = [p for p in (iv / "spec_versions").glob("spec_v*.md") if re.fullmatch(r"spec_v\d+(\.\d+)*", p.stem)] \
        if (iv / "spec_versions").is_dir() else []
    if snaps:
        latest = max(snaps, key=lambda p: vkey(p.stem))
        print(f"快照：最新 {latest.name}（共 {len(snaps)} 个）")
        if spec is not None:
            m = re.match(r"v\d+(?:\.\d+)*", header_field(spec, "版本") or "")
            ver = m.group(0) if m else ""
            same = iv / "spec_versions" / f"spec_{ver}.md"
            if ver and not same.exists():
                hints.append(f"{a.spec} 是 {ver}，还没有这个版本的快照（最新是 {latest.name}）：跑 snapshot_spec.py --version {ver}")
            elif ver and read(same) != spec:
                old_lines, new_lines = (read(same) or "").splitlines(), spec.splitlines()
                changed = sum(1 for x, y in zip(old_lines, new_lines) if x != y) + abs(len(old_lines) - len(new_lines))
                hints.append(f"{a.spec} 与快照 {same.name} 不一致（约 {changed} 行不同）：快照之后又改过内容。"
                             f"改的是需求内容就升版本再快照；只是补记录就用 --force 重新快照")
    else:
        print("快照：无")

    desk = find_desk(root, a.desk)
    if desk:
        v = (read(desk / "VERSION") or "").strip() or "?"
        print(f"审批台：v{v}（{desk}）；本 skill 按 v{DESK_VERSION} 写")
        have, want = vtuple(v), vtuple(DESK_VERSION)
        if have is None:
            hints.append(f"认不出审批台的版本（{desk / 'VERSION'}）：确认它是 {DESK_REPO} 的克隆")
        elif have > want:
            hints.append(f"审批台 v{v} 比本 skill 按的 v{DESK_VERSION} 新：先读审批台 CHANGELOG.md 里 v{DESK_VERSION} 之后的条目和 "
                         "round_template/README.md 末尾的升级对照，按需调整 interview-rounds.md 第 4–6 节")
        elif have < want:
            hints.append(f"审批台 v{v} 比本 skill 按的 v{DESK_VERSION} 旧：先更新（git -C {desk} pull，或重新克隆 {DESK_REPO}）")
    else:
        if a.desk:
            print(f"审批台：--desk 指定的 {a.desk} 不是审批台 skill（里面没有 round_template/build.py）")
        else:
            print(f"审批台：没找到（默认依次找 {DESK_PLACES}）")
            hints.append(f"装审批台：git clone {DESK_REPO} {SKILL_DIR.parent / 'interactive-approval-desk'}（或用 --desk 指定已有的目录）")
    build = iv / "reviews" / "build"
    missing = [n for n in ("project.js", "cfg_template.json") if not (build / n).exists()]
    if missing:
        hints.append(f"interview/reviews/build/ 缺 {'、'.join(missing)}（审批台每轮共用的设置）：再跑一次 init_interview.py 补上，它不覆盖已有文件")

    if hints:
        print("\n提示：")
        for h in hints:
            print("  -", h)


if __name__ == "__main__":
    main()
