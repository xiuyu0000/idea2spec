#!/usr/bin/env python3
"""按 idea2spec 的记录生成审批台的代号表（默认写到 interview/reviews/build/codes.js）。

用法：
  python3 desk_codes.py <项目目录> [--desk 审批台目录] [--out 输出文件] [--shapes code_shapes.json] [--dry-run]

按权威顺序收集项目里已有的文件（越权威越靠前；同一个代号以先出现的为准），没有的跳过：
  spec.md → 根目录其余的 *_contract.md（派生契约）→ interview/registry/decisions.md → open_items.md
  → sources.md → interview/INDEX.md → interview/reviews/INDEX.md → interview/reviews/*_feedback.md
然后调用审批台的 scripts/build_codes.py。审批台按这个顺序找：--desk、<项目>/skills/interactive-approval-desk、
本 skill 旁边的 ../approval_desk。本 skill 的编号都在审批台默认认得的形状里，一般不需要 --shapes。
"""
import argparse
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent


def find_desk(root, explicit=None):
    if explicit:  # 指定了就只认它，不悄悄换成别处的
        c = Path(explicit).expanduser()
        return c if (c / "scripts" / "build_codes.py").is_file() and (c / "round_template").is_dir() else None
    cands = [root / "skills" / "interactive-approval-desk",
              SKILL_DIR.parent / "approval_desk",
              SKILL_DIR.parent / "interactive-approval-desk"]
    for c in cands:
        if (c / "scripts" / "build_codes.py").is_file() and (c / "round_template").is_dir():
            return c
    return None


def sources(root):
    iv = root / "interview"
    files = [root / "spec.md"]
    files += sorted(p for p in root.glob("*_contract.md"))
    files += [iv / "registry" / "decisions.md", iv / "registry" / "open_items.md", iv / "registry" / "sources.md",
              iv / "INDEX.md", iv / "reviews" / "INDEX.md"]
    files += sorted((iv / "reviews").glob("*_feedback.md")) if (iv / "reviews").is_dir() else []
    return [p for p in files if p.is_file()]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir")
    ap.add_argument("--desk", help="审批台 skill 的目录")
    ap.add_argument("--out", help="输出文件；默认 interview/reviews/build/codes.js")
    ap.add_argument("--shapes", help="传给 build_codes.py 的 --shapes（项目另有编号形状时）")
    ap.add_argument("--dry-run", action="store_true", help="只列出会用哪些文件，不生成")
    a = ap.parse_args()

    root = Path(a.project_dir).expanduser().resolve()
    if not (root / "interview").is_dir():
        sys.exit(f"没找到 {root / 'interview'}；先运行 init_interview.py")
    desk = find_desk(root, a.desk)
    if not desk:
        if a.desk:
            sys.exit(f"--desk 指定的 {a.desk} 不是审批台 skill（里面要有 scripts/build_codes.py 和 round_template/）")
        sys.exit("找不到审批台 skill：用 --desk 指定它的目录（默认找 <项目>/skills/interactive-approval-desk、本 skill 旁边的 ../approval_desk）")
    files = sources(root)
    if not files:
        sys.exit("项目里还没有可以收集代号的文件（decisions.md 等）")
    out = Path(a.out).expanduser() if a.out else root / "interview" / "reviews" / "build" / "codes.js"

    print(f"审批台：{desk}")
    print("收集（越靠前越权威）：")
    for p in files:
        print("  ", p.relative_to(root))
    if a.dry_run:
        return
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [sys.executable, str(desk / "scripts" / "build_codes.py"), "--out", str(out)]
    if a.shapes:
        cmd += ["--shapes", str(Path(a.shapes).expanduser())]
    cmd += [str(p) for p in files]
    sys.stdout.flush()  # 先把上面的清单打出来，再让 build_codes.py 输出
    r = subprocess.run(cmd)
    sys.exit(r.returncode)


if __name__ == "__main__":
    main()
