#!/usr/bin/env python3
"""检查需求契约（spec.md 或派生契约）的追溯与格式。只读，不改文件。

用法：
  python3 check_spec.py <项目目录> [--file spec.md] [--baseline] [--ac-types AT,INT,MR,PILOT]

错误（有错误时退出码为 1）：
  - 引用的 D-/F-/S-/CR- 编号没有登记（decisions.md、sources.md、changes/、本文件或基线 spec.md 的变更记录）
  - Q-/A- 编号既没登记在 open_items.md，也没在本文件的表格里定义
  - 功能需求（行首 **FR-域-nn 标题**）没有验收用例 ACn（方式），或找不到任何依据（"依据："、正文或分组标题里的 D/F/S/A 编号、引用的不变量）；验收方式不在允许列表；FR 编号重复
  - 不变量（表头含"验收用例"的表格里的 INV-nn 行）没写验收用例，或引用的 FR/AC 不存在
  - 加 --baseline 时：还有 [推断] 标记或模板占位
警告：
  - 功能需求编号不在审批台默认认得的形状里（FR-域-两位数，域只用大写字母）
  - 引用了已被取代的决定
  - 本文件定义了 Q/A，但没登记进 open_items.md
  - "待确认 / TBD /（待定）"、遗留的 HTML 注释、模板占位（不加 --baseline 时）、难以判定的词
说明：反引号里的内容与"修改前原文"一节（保存历史原文）不参与标记检查，也不算作 FR 定义。
"""
import argparse
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

WIDTH = {"D": "3,4", "F": "3,4", "CR": "3,4", "S": "2,3", "Q": "2,3", "A": "2,3"}
CODE = {p: re.compile(rf"(?<![A-Za-z0-9-])({p}-\d{{{w}}})(?!\d)") for p, w in WIDTH.items()}
FR_DEF = re.compile(r"^\*\*(FR-[A-Z][A-Z0-9]*-\d+)[\s\u3000*（(：:]")
FR_REF = re.compile(r"(FR-[A-Z][A-Z0-9]*-\d+)((?:\s*[、,，/和及与]?\s*AC\d+)+)")
AC = re.compile(r"AC(\d+)\s*[（(]\s*([A-Za-z]+)\s*[）)]")
HEADING = re.compile(r"^(#{1,6})\s+(.*)")
PLACEHOLDER = re.compile(r"FR-XXX|YYYY-MM-DD|<[\u4e00-\u9fff][^<>\n]{0,40}>")
VAGUE = ["智能处理", "优化体验", "基本完成", "尽量", "适当", "及时", "合理"]


def read(p):
    try:
        return p.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def table_rows(text):
    for line in (text or "").splitlines():
        s = line.strip()
        if not s.startswith("|") or re.fullmatch(r"\|[\s:|-]*", s):
            continue
        yield [c.strip() for c in s.strip("|").split("|")]


def tables(text):
    """按连续的表格行切分，返回 [(表头, [数据行])]。"""
    out, block = [], []
    for line in (text or "").splitlines() + [""]:
        s = line.strip()
        if s.startswith("|"):
            block.append(s)
            continue
        if block:
            cells = [[c.strip() for c in r.strip("|").split("|")] for r in block if not re.fullmatch(r"\|[\s:|-]*", r)]
            if cells:
                out.append((cells[0], cells[1:]))
            block = []
    return out


def first_col(text, prefix):
    pat = re.compile(rf"{prefix}-\d+")
    return {cells[0]: cells for cells in table_rows(text) if cells and pat.fullmatch(cells[0])}


def history_mask(lines):
    """标出"修改前原文"一节（到同级或更高级标题为止）。"""
    mask = [False] * len(lines)
    level = None
    for i, line in enumerate(lines):
        m = HEADING.match(line)
        if m:
            lv = len(m.group(1))
            if level is not None and lv <= level:
                level = None
            if "修改前原文" in m.group(2):
                level = lv
        mask[i] = level is not None
    return mask


def no_code_spans(line):
    return re.sub(r"`[^`]*`", "", line)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--file", default="spec.md", help="项目根目录下的契约文件，默认 spec.md")
    ap.add_argument("--baseline", action="store_true", help="定稿前检查：[推断] 与模板占位算错误")
    ap.add_argument("--ac-types", default="AT,INT,MR,PILOT", help="允许的验收方式，逗号分隔")
    a = ap.parse_args()

    root = Path(a.project_dir).expanduser()
    path = root / a.file
    text = read(path)
    if text is None:
        sys.exit(f"找不到 {path}")
    lines = text.splitlines()
    hist = history_mask(lines)
    allowed = {t.strip() for t in a.ac_types.split(",") if t.strip()}
    errors, warnings, notes = [], [], []

    reg = root / "interview" / "registry"
    dec = read(reg / "decisions.md")
    oi = read(reg / "open_items.md")
    src = read(reg / "sources.md")
    if dec is None:
        warnings.append("没找到 interview/registry/decisions.md，D/F 编号无法核对")
    d_rows, f_rows = first_col(dec, "D"), first_col(dec, "F")
    s_rows = first_col(src, "S")
    q_reg, a_reg = first_col(oi, "Q"), first_col(oi, "A")
    q_here, a_here = first_col(text, "Q"), first_col(text, "A")
    cr_known = set(first_col(text, "CR"))
    if a.file != "spec.md":
        cr_known |= set(first_col(read(root / "spec.md"), "CR"))
    changes = root / "interview" / "changes"
    if changes.is_dir():
        cr_known |= {m.group(1) for p in changes.glob("CR-*.md") if (m := re.match(r"(CR-\d+)", p.name))}

    # ---- 编号追溯 ----
    cited = defaultdict(lambda: defaultdict(list))  # prefix -> code -> [line numbers]
    for i, line in enumerate(lines, 1):
        for p, pat in CODE.items():
            for code in pat.findall(line):
                cited[p][code].append(i)

    def missing(prefix, known, label):
        for code, at in sorted(cited[prefix].items()):
            if code not in known:
                errors.append(f"{code} 被引用（第 {at[0]} 行等 {len(at)} 处），但没在{label}登记")

    if dec is not None:
        missing("D", d_rows, " decisions.md ")
        missing("F", f_rows, " decisions.md 的来源事实表")
    if src is not None or cited["S"]:
        missing("S", s_rows, " sources.md ")
    missing("CR", cr_known, " interview/changes/、本文件或 spec.md 的变更记录")
    for prefix, reg_rows, here in (("Q", q_reg, q_here), ("A", a_reg, a_here)):
        for code, at in sorted(cited[prefix].items()):
            if code not in reg_rows and code not in here:
                errors.append(f"{code} 被引用（第 {at[0]} 行），但 open_items.md 和本文件的表格里都没有定义")
        for code in sorted(here):
            if oi is not None and code not in reg_rows:
                warnings.append(f"{code} 在本文件里定义了，但没登记进 open_items.md")

    for code, row in sorted(d_rows.items()):
        status = row[-1] if len(row) >= 4 else ""
        if re.match(r"^(已被|作废|已作废|取消)", status) and code in cited["D"]:
            live = [n for n in cited["D"][code] if not hist[n - 1]]
            if live:
                warnings.append(f"{code} 的状态是“{status[:30]}”，仍在第 {live[0]} 行等处被引用")

    # ---- 功能需求与验收用例 ----
    blocks = {}
    order = []
    current = None
    heading = ""
    for i, line in enumerate(lines):
        if hist[i]:
            current = None
            continue
        m = FR_DEF.match(line)
        if m:
            fr = m.group(1)
            if fr in blocks:
                errors.append(f"{fr} 定义了两次（第 {blocks[fr]['line']} 行与第 {i + 1} 行）；以第一处为准检查")
                current = None
                continue
            blocks[fr] = {"line": i + 1, "text": [line], "heading": heading}
            order.append(fr)
            current = fr
            continue
        h = HEADING.match(line)
        if h or line.strip() == "---":
            if h:
                heading = h.group(2)
            current = None
            continue
        if current:
            blocks[current]["text"].append(line)

    ac_types = Counter()
    ac_index = {}
    inline_basis = []
    for fr in order:
        body = "\n".join(blocks[fr]["text"])
        acs = AC.findall(body)
        nums = {int(n) for n, _ in acs}
        ac_index[fr] = nums
        for n, t in acs:
            ac_types[t] += 1
            if t not in allowed:
                errors.append(f"{fr} AC{n} 的验收方式“{t}”不在允许列表（{'/'.join(sorted(allowed))}）")
        if not acs:
            errors.append(f"{fr}（第 {blocks[fr]['line']} 行）没有验收用例 ACn（方式）")
        if not re.search(r"依据\s*[:：]", body):
            context = body + "\n" + blocks[fr]["heading"]
            if any(CODE[p].search(context) for p in ("D", "F", "S", "A")) or "INV-" in body:
                inline_basis.append(fr)
            else:
                errors.append(f"{fr}（第 {blocks[fr]['line']} 行）没有依据：既没有“依据：”，正文与所在分组标题里也没有 D/F/S/A 编号或不变量")

    if not order and a.file == "spec.md":
        warnings.append("没找到行首 **FR-域-nn 标题** 格式的功能需求定义（格式见 references/spec-writing.md 第 2 节）")
    odd = [fr for fr in order if not re.fullmatch(r"FR-[A-Z]+-\d{2}", fr)]
    if odd:
        warnings.append(f"{'、'.join(odd[:8])}{'…' if len(odd) > 8 else ''} 不在审批台默认认得的代号形状里"
                        "（FR-域-两位数，域只用大写字母）：页面上会被当成没解释的代号；改编号，或生成审批台代号表时用 --shapes")
    if inline_basis:
        shown = "、".join(inline_basis[:8]) + ("…" if len(inline_basis) > 8 else "")
        notes.append(f"{len(inline_basis)} 条功能需求的依据写在标题、分组标题或正文里，没有单独的“依据：”（{shown}）")

    # ---- 不变量 ----
    inv_rows = {}
    for head, body_rows in tables(text):
        col = next((k for k, h in enumerate(head) if "验收用例" in h), None)
        if col is None:
            continue
        for row in body_rows:
            if row and re.fullmatch(r"INV-\d+", row[0]):
                inv_rows[row[0]] = row[col] if col < len(row) else ""
    for inv, accept in sorted(inv_rows.items()):
        refs = FR_REF.findall(accept)
        if not accept or accept in {"—", "-", "无"}:
            errors.append(f"{inv} 没有写验收用例")
            continue
        if not refs:
            warnings.append(f"{inv} 的验收用例“{accept[:40]}”里没认出 FR-…-nn ACn 形式的引用")
            continue
        for fr, acs in refs:
            if fr not in ac_index:
                errors.append(f"{inv} 引用的 {fr} 不存在")
                continue
            for n in re.findall(r"AC(\d+)", acs):
                if int(n) not in ac_index[fr]:
                    errors.append(f"{inv} 引用的 {fr} AC{n} 不存在")

    # ---- 标记与占位 ----
    def scan(pattern, label, as_error=False, limit=8):
        hits = []
        for i, line in enumerate(lines, 1):
            if hist[i - 1]:
                continue
            if re.search(pattern, no_code_spans(line)):
                hits.append(i)
        if hits:
            shown = "、".join(str(n) for n in hits[:limit]) + ("…" if len(hits) > limit else "")
            msg = f"{label}：{len(hits)} 行（第 {shown} 行）"
            (errors if as_error else warnings).append(msg)
        return hits

    if a.baseline:
        scan(r"\[推断\]", "还有 [推断] 标记", as_error=True)
    else:
        n_inf = sum(1 for i, l in enumerate(lines) if not hist[i] and "[推断]" in no_code_spans(l))
        if n_inf:
            notes.append(f"[推断] 标记 {n_inf} 处（草案正常；定稿前要清零）")
    scan(PLACEHOLDER.pattern, "模板占位没替换", as_error=a.baseline)
    scan(r"<!--", "遗留的 HTML 注释（模板说明）")
    scan(r"待确认(?!草案)|TBD|[（(【\[]待定[）)】\]]", "“待确认/TBD/（待定）”字样")
    for w in VAGUE:
        pattern = r"(?<!涉)及时" if w == "及时" else re.escape(w)  # “涉及时限”不算
        scan(pattern, f"难以判定的词“{w}”（确认是否给了判定方法）", limit=5)

    # ---- 输出 ----
    def field(name):
        for cells in table_rows(text):
            if len(cells) >= 2 and cells[0] == name:
                return cells[1].replace("**", "")
        return "?"

    print(f"检查 {a.file}：{field('版本')}｜{field('状态')[:60]}")
    types = "、".join(f"{t} {n}" for t, n in sorted(ac_types.items()))
    print(f"功能需求 {len(order)} 条；验收用例 {sum(ac_types.values())} 个（{types or '无'}）；不变量 {len(inv_rows)} 条")
    print("引用编号：" + "、".join(f"{p} {len(cited[p])} 个" for p in WIDTH if cited[p]))
    for n in notes:
        print("提示：" + n)
    print(f"\n错误 {len(errors)}")
    for e in errors:
        print("  ✗ " + e)
    print(f"警告 {len(warnings)}")
    for w in warnings:
        print("  ! " + w)
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
