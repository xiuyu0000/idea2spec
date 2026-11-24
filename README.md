# idea2spec

A Claude skill (written in Chinese) that turns a product or software idea into an approved requirements contract — a `spec.md` that Claude Code can build from — through an evidence-backed challenge interview, round-by-round approval desks, cold reads and self-checks.

把一个产品或软件想法，经"有依据的挑战式访谈 + 审批台逐轮审批 + 冷读与自检"，梳理成可以直接交给 Claude Code 开发的需求契约 `spec.md`（项目级需求基线），并在基线之后管理变更、派生阶段契约与交接。

## 流程

| 阶段 | 做什么 | 出口 |
|---|---|---|
| 0 接收想法 | 逐字记下想法，确认"需求契约"的定义在手 | 读到想法与定义 |
| 1 立规矩 | 从定义推出访谈终止条件 T1–T7、初始议程和工作方式，请用户确认 | 记录目录建好，发出第一轮审批台 |
| 2 访谈 | 先调研再质疑；每轮用审批台请用户逐条拍板，反馈落盘为已批准决定 | 实质性缺口都已拍板，或已记为假设、待决 |
| 3 起草·冷读·签署 | 起草 spec.md；两个只读文档的子 Agent 冷读（设计者、验收者）；签署 | 用户批准为基线 v1.0 |
| 4 基线之后 | 变更提议、派生阶段契约（交互原型、MVP）、交接清单 | 交给 Claude Code |

四条底线：只有用户批准的才算需求；质疑要有依据；每轮落盘、不改写历史；对用户说白话。

## 产出
- `spec.md`：需求方、设计者、实现 Agent、独立验收者共同遵守的需求基线（"需求契约"的定义见 [references/contract-definition.md](references/contract-definition.md)）
- `interview/`：用户原话（逐字）、已批准决定、待决与假设、调研来源、每轮提案与反馈、spec 的历史版本与逐行对比、变更提议
- 按需：派生阶段契约、交接清单 `HANDOFF.md`

## 安装
- Claude Code：把仓库克隆到 `~/.claude/skills/idea2spec/`（本机所有项目可用），或项目里的 `.claude/skills/idea2spec/`。
- 其他支持 Agent Skills 的客户端：按它的方式安装整个目录，入口是 `SKILL.md`。

依赖：
- Python 3（`scripts/`）。
- 审批台 skill **interactive-approval-desk**，另行安装，默认放在本目录旁边的 `../approval_desk`。本 skill 按它的 v3.7.2 写；没有审批台时，idea2spec 改用 Markdown 提案文件加对话提问。
- Node 与 Playwright：审批台的自检要用。

## 用法
在 Claude 里说"用 idea2spec 把这个想法梳理成 spec.md"，附上想法。推荐按三段写：`<problem>` 要解决什么、`<scene>` 场景与已有约束、`<requirements>` 对访谈的要求。Claude 先给出终止条件和议程请你确认，之后每轮发一个审批台：你填完点"提交反馈"，回到对话说"反馈完成"。

## 目录
```
SKILL.md                     流程、底线、每轮收尾清单、新会话怎么接上
references/                  契约定义、终止条件、访谈轮（含审批台接口）、记录体系、spec 写法、冷读、基线与变更、教训
templates/                   记录与 spec 的模板；审批台每轮共用的设置（review_project.js、review_cfg.json）
scripts/init_interview.py    建 interview/ 记录目录、登记表与审批台的共用设置（不覆盖已有文件）
scripts/status.py            当前轮次、等待反馈的审批轮、下一个可用编号、未决事项、spec 版本、审批台版本
scripts/desk_codes.py        按记录生成审批台的代号表
scripts/check_spec.py        spec 的追溯与格式检查（--baseline 用于定稿前）
scripts/snapshot_spec.py     版本快照与逐行对比
```

```bash
python3 scripts/init_interview.py <项目> --name "项目名"
python3 scripts/status.py <项目>
python3 scripts/desk_codes.py <项目>
python3 scripts/check_spec.py <项目> [--baseline]
python3 scripts/snapshot_spec.py <项目> --version v1.0
```

## 来历
这套做法来自 2026 年 11 月一个内部平台的需求梳理：一段想法，经 8 轮审批台、7 轮冷读，得到已批准的基线 spec.md、签署的交互原型契约和交接清单。版本记录见 [CHANGELOG.md](CHANGELOG.md)。

## 许可
Apache License 2.0，见 [LICENSE](LICENSE)。
