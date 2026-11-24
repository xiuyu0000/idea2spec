#!/usr/bin/env python3
"""建立 idea2spec 的 interview/ 记录目录、登记表与审批台的共用设置。

用法：
  python3 init_interview.py <项目目录> --name "项目名" [--project-id ID] [--date YYYY-MM-DD] [--definition 契约定义文件]

- 建 interview/ 下的 log、registry、research、reviews（含 artifact、build）、spec_versions、changes；
- 从 templates/ 生成 INDEX.md、decisions.md、open_items.md、sources.md、reviews/INDEX.md；
- 在 interview/reviews/build/ 生成审批台每轮共用的 project.js 与 cfg_template.json（填好 PROJECT 和路径提示）；
- 项目根目录没有《需求契约概念说明.md》时，复制 --definition 指定的文件，默认用本 skill 的 references/contract-definition.md。

--project-id 是审批台的项目标识（只用字母、数字、_、-，最长 24 个字符；本地打开的审批台页面靠它区分项目的浏览器存储）。
不写时用项目文件夹名；文件夹名不合规时，cfg_template.json 里留"【填写】"并提示。
不覆盖任何已有文件，所以对已有的项目再跑一次，只会补上缺的部分；输出新建与跳过的清单。
"""
import argparse
import datetime as dt
import json
import re
import shutil
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = SKILL_DIR / "templates"
DEFAULT_DEFINITION = SKILL_DIR / "references" / "contract-definition.md"
DEFINITION_NAME = "需求契约概念说明.md"
PROJECT_ID = re.compile(r"^[A-Za-z0-9_-]{1,24}$")

DIRS = [
    "interview/log",
    "interview/registry",
    "interview/research",
    "interview/reviews/artifact",
    "interview/reviews/build",
    "interview/spec_versions",
    "interview/changes",
]

FILES = [  # (模板, 目标)：替换 {{PROJECT}}、{{DATE}}
    ("INDEX.md", "interview/INDEX.md"),
    ("decisions.md", "interview/registry/decisions.md"),
    ("open_items.md", "interview/registry/open_items.md"),
    ("sources.md", "interview/registry/sources.md"),
    ("reviews_INDEX.md", "interview/reviews/INDEX.md"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("project_dir", help="项目文件夹")
    ap.add_argument("--name", required=True, help="项目名，写进 INDEX.md")
    ap.add_argument("--project-id", help="审批台的项目标识；默认用项目文件夹名")
    ap.add_argument("--date", default=dt.date.today().isoformat(), help="默认今天")
    ap.add_argument("--definition", help="用户自己的契约定义文件；默认用本 skill 附带的定义")
    args = ap.parse_args()

    root = Path(args.project_dir).expanduser()
    if not root.is_dir():
        sys.exit(f"项目目录不存在：{root}")
    folder = root.resolve().name
    pid = args.project_id or folder
    pid_ok = bool(PROJECT_ID.match(pid))
    if args.project_id and not pid_ok:
        sys.exit("--project-id 只能用字母、数字、_、-，最长 24 个字符")

    created, skipped, notes = [], [], []
    for d in DIRS:
        p = root / d
        if not p.is_dir():
            p.mkdir(parents=True, exist_ok=True)
            created.append(d + "/")

    for tpl, target in FILES:
        p = root / target
        if p.exists():
            skipped.append(target)
            continue
        text = (TEMPLATES / tpl).read_text(encoding="utf-8")
        text = text.replace("{{PROJECT}}", args.name).replace("{{DATE}}", args.date)
        p.write_text(text, encoding="utf-8")
        created.append(target)

    # 审批台每轮共用的设置
    build = root / "interview" / "reviews" / "build"
    p = build / "project.js"
    if p.exists():
        skipped.append("interview/reviews/build/project.js")
    else:
        shutil.copyfile(TEMPLATES / "review_project.js", p)
        created.append("interview/reviews/build/project.js（终止条件按 D-001 改写）")
    p = build / "cfg_template.json"
    if p.exists():
        skipped.append("interview/reviews/build/cfg_template.json")
    else:
        cfg = json.loads((TEMPLATES / "review_cfg.json").read_text(encoding="utf-8"))
        cfg["PROJECT"] = pid if pid_ok else "【填写：项目标识，只用字母、数字、_、-，最长 24 个字符】"
        cfg["REVIEW_PATH_HINT"] = f"{folder}/interview/reviews"
        p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        created.append(f"interview/reviews/build/cfg_template.json（PROJECT = {cfg['PROJECT']}）")
        if not pid_ok:
            notes.append(f"文件夹名“{folder}”不能当审批台的项目标识：在 cfg_template.json 里填 PROJECT，或重跑时加 --project-id")

    definition = root / DEFINITION_NAME
    if definition.exists():
        skipped.append(DEFINITION_NAME)
    else:
        src = Path(args.definition).expanduser() if args.definition else DEFAULT_DEFINITION
        if not src.is_file():
            sys.exit(f"找不到契约定义文件：{src}")
        shutil.copyfile(src, definition)
        created.append(f"{DEFINITION_NAME}（来自 {src.name}）")

    if created:
        print("已新建：")
        for c in created:
            print("  +", c)
    else:
        print("没有新建任何东西。")
    if skipped:
        print("已存在，未改动：")
        for s in skipped:
            print("  =", s)
    for n in notes:
        print("提示：" + n)
    print("\n下一步：写 interview/log/T01.md（用户原话逐字，模板见 templates/log_Txx.md），"
          "用户确认后在 decisions.md 记 D-001 终止条件、D-002 产出范围、D-003 工作方式，"
          "并按 D-001 改写 interview/reviews/build/project.js 里的终止条件。")


if __name__ == "__main__":
    main()
