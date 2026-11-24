#!/usr/bin/env python3
"""把契约文件存成版本快照，并写出与上一个快照的逐行对比。

用法：
  python3 snapshot_spec.py <项目目录> --version v1.1 [--file spec.md] [--note "变更 CR-001"] [--force]

命名沿用首个项目：
  spec.md               -> interview/spec_versions/spec_v1.1.md 与 diff_v1.0_v1.1.md
  prototype_contract.md -> interview/spec_versions/prototype_contract_v1.0.md 与 prototype_contract_diff_v0.2_v1.0.md
对比用 unified diff（不带上下文行），放在 ```diff 代码块里。已有同名快照时拒绝覆盖，除非加 --force。
"""
import argparse
import difflib
import re
import sys
from pathlib import Path

VER = re.compile(r"^v\d+(\.\d+)*$")


def vkey(v):
    return tuple(int(x) for x in v[1:].split("."))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--version", required=True, help="如 v0.3、v1.0、v1.2")
    ap.add_argument("--file", default="spec.md", help="项目根目录下的契约文件，默认 spec.md")
    ap.add_argument("--note", default="", help="写进对比标题括号里的说明，如“变更 CR-002”")
    ap.add_argument("--force", action="store_true", help="覆盖已有的同名快照")
    a = ap.parse_args()

    if not VER.match(a.version):
        sys.exit("版本号写成 v1.2 这样的格式")
    root = Path(a.project_dir).expanduser()
    src = root / a.file
    if not src.is_file():
        sys.exit(f"找不到 {src}")

    stem = src.stem
    outdir = root / "interview" / "spec_versions"
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / f"{stem}_{a.version}.md"
    if target.exists() and not a.force:
        sys.exit(f"{target.relative_to(root)} 已存在；确认要覆盖时加 --force")

    previous = []
    pat = re.compile(rf"^{re.escape(stem)}_(v\d+(?:\.\d+)*)\.md$")
    for p in outdir.iterdir():
        m = pat.match(p.name)
        if m and vkey(m.group(1)) < vkey(a.version):
            previous.append((vkey(m.group(1)), m.group(1), p))
    prev = max(previous) if previous else None
    out = None
    if prev:
        pv = prev[1]
        name = f"diff_{pv}_{a.version}.md" if stem == "spec" else f"{stem}_diff_{pv}_{a.version}.md"
        out = outdir / name
        if out.exists() and not a.force:
            sys.exit(f"{out.relative_to(root)} 已存在；确认要覆盖时加 --force")

    text = src.read_text(encoding="utf-8")
    target.write_text(text, encoding="utf-8")
    print("快照：", target.relative_to(root))
    if not prev:
        print("没有更早的快照，不写对比。")
        return

    _, pv, pp = prev
    old = pp.read_text(encoding="utf-8").splitlines()
    new = text.splitlines()
    diff = list(difflib.unified_diff(old, new, fromfile=pp.name, tofile=target.name, lineterm="", n=0))
    added = sum(1 for l in diff if l.startswith("+") and not l.startswith("+++"))
    removed = sum(1 for l in diff if l.startswith("-") and not l.startswith("---"))
    longest = max([len(m) for m in re.findall(r"`+", "\n".join(diff))] + [2])
    fence = "`" * max(3, longest + 1)
    label = "spec" if stem == "spec" else stem
    title = f"# {label} {pv} → {a.version} 逐行对比" + (f"（{a.note}）" if a.note else "")
    out.write_text(f"{title}\n\n{fence}diff\n" + "\n".join(diff) + f"\n{fence}\n", encoding="utf-8")
    print(f"对比：{out.relative_to(root)}（对照 {pp.name}；新增 {added} 行，删除 {removed} 行）")


if __name__ == "__main__":
    main()
