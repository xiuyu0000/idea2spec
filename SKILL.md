---
name: idea2spec
description: 把一个产品或软件想法，经"有依据的挑战式访谈 + 审批台逐轮审批 + 冷读与自检"，梳理成可直接交给 Claude Code 开发的需求契约 spec.md（项目级需求基线），并在基线之后管理变更、派生阶段契约与交接。用户想把想法、场景或需求描述变成 spec.md、需求契约、PRD 或规格说明，要求先访谈、质疑、挖掘需求；或要继续某个 interview/ 目录下的需求访谈（说"反馈完成"、追问某个审批条目、要改基线、要出原型或 MVP 契约）时使用。与开源的审批台 skill interactive-approval-desk 配合使用。
---

# idea2spec：从一个想法到可用的需求契约

这套做法来自一个内部平台的需求梳理（2026-11-06 至 11-15，对话 T01–T17，审批轮 R01–R08；下文称"首个项目"）：从一段想法出发，经 8 轮审批台、7 轮冷读，得到已批准基线 spec.md v1.2、已签署的交互原型契约和交接清单，交给 Claude Code 开发。

下文 `<skill>` 指本 skill 所在目录；`<desk>` 指审批台 skill interactive-approval-desk（开源：https://github.com/xiuyu0000/interactive-approval-desk）所在目录，默认是和本 skill 并排的 `../interactive-approval-desk`（两个仓库都克隆进同一个 skills 目录时就是这样；脚本也认项目里固定版本的 `skills/interactive-approval-desk/` 和旧的文件夹名 `../approval_desk`）；`<项目>` 指用户的项目文件夹。本目录里有 `local.md` 时先读它：它只在本机、不进仓库，写着本机的范例项目和依赖位置；拿不准格式时去范例项目看实物。

## 产出
- **spec.md**：需求契约——需求方、设计者、实现 Agent、独立验收者共同遵守的项目级需求基线。定义见 `references/contract-definition.md`（用户原文，方法的上游权威；与本 skill 其他内容冲突时以它为准）。
- **interview/**：全过程记录——用户原话（逐字）、已批准决定、待决与假设、调研来源、每轮提案与反馈、spec 历史版本与逐行对比、变更提议。任何新会话读信息地图就能接上。
- 按需：派生阶段契约（交互原型、MVP）与交接清单 HANDOFF.md。

## 底线（贯穿全程）
1. **只认批准。** 只有 `interview/registry/decisions.md` 里的 D-编号算已批准决定。Claude 的建议、推断、审批台上的推荐都不是需求。spec 中每条需求标来源：D 已批准决定 / F 用户陈述的事实 / S 调研来源 / A 假设 / Q 待决；未获批准的补充规则标 `[推断]`，基线里不能再有。
2. **质疑要有依据。** 挑战用户的想法前先调研，给出处、置信度和替代方案。不新增没有依据的功能、岗位、指标、审批或流程。只有会实质改变目标、范围、权限或验收的缺口才交给用户；其余记为假设或待决，写明影响、决定人和时机，继续推进不受影响的部分。
3. **落盘，不改写历史。** 每轮收尾都写文件。被取代的决定标"已被 D-xxx 取代"，保留原文；基线批准后的任何修改都走变更记录。不虚构批准：文件状态始终写明是"待确认草案"还是"已批准基线"。
4. **白话。** 给用户看的一切用最直白的话；必要的专业词和代号在审批台上带悬浮解释。

## 依赖
- **审批台**：interactive-approval-desk skill（`<desk>`），开源在 https://github.com/xiuyu0000/interactive-approval-desk（MIT）。没装时，把它克隆到和本 skill 同一个 skills 目录：`git clone https://github.com/xiuyu0000/interactive-approval-desk ~/.claude/skills/interactive-approval-desk`（本 skill 装在别处时，克隆到它旁边）。每个需要用户批准的提案都用它生成审批台。本 skill 按它的开源版 **v3.7.1** 写（这个版本号也写在 `scripts/status.py` 的 `DESK_VERSION`，适配新版时一起改），用仓库里的最新版。第一次用之前读它的 `SKILL.md`、`round_template/README.md`（cfg 与数据的全部字段）和 `references/review-cards.md`（卡片怎么写）。`status.py` 会比较 `<desk>/VERSION`：比 3.7.1 新时，先读 `<desk>/CHANGELOG.md` 里 3.7.1 之后的条目和 `round_template/README.md` 末尾的升级对照，再按需调整 `references/interview-rounds.md` 第 4–6 节；比 3.7.1 旧时先更新审批台（`git -C <desk> pull`）。找不到审批台时问用户位置；用户同意不用审批台时，才改用 Markdown 提案文件加对话提问，提案与反馈照样落盘。
- **自检环境**：审批台的自检 `test.js` 和冷读材料 `dumptext.js` 要用 Node 和装有 Playwright 的 `node_modules`（用 `NODE_PATH` 指过去）；没有就先装，自检不能跳过。
- **子 Agent**：冷读要启动只读契约文件的独立子 Agent（终止条件 T7 的规定，用户批准终止条件即同意这种做法）；审批台发布前的审批者冷读也交给子 Agent。
- **文件访问**：会话要能读写项目文件夹，并能读本 skill 目录与 `<desk>`；在桌面应用里就是把这几个文件夹都连接到会话。取回反馈时可能要看"下载"文件夹，那需要用户另外授权。
- **思考程度**：建议 high。Claude 不能自己切换，请用户在应用里调。

## 流程

| 阶段 | 首个项目的轮次 | 出口条件 |
|---|---|---|
| 0 接收想法 | T01 | 读到想法与契约定义 |
| 1 立规矩 | T02–T03 | 用户确认终止条件 T1–T7、产出范围、工作方式（记为 D-001..D-003）；interview/ 建好；发出 R01 |
| 2 访谈 | R01–R03 | 议程里的实质性缺口都由用户拍板，或已记为假设/待决并指定决定人与时机 |
| 3 起草·冷读·签署 | R04–R06 | 冷读：设计者"阻塞：无"，验收者问题全部改写；自检通过；用户明确批准 → 基线 v1.0 |
| 4 基线之后 | R07 起 | 变更按 CR 并入；按需派生契约签署；交接清单 |

规模随项目调整：小想法可以一两轮访谈加一轮签署；不变的是只认批准、记录落盘、冷读、签署。

### 阶段 0：接收想法
1. 逐字记下用户的想法。推荐（不强求）用户按三段写：`<problem>` 要解决什么、`<scene>` 场景与已有约束、`<requirements>` 对访谈的要求。
2. 确认契约定义在手：项目文件夹里的《需求契约概念说明.md》；没有就用 `references/contract-definition.md`（`init_interview.py` 会复制过去）。用户说附了文件但没读到时，直说没收到，不要凭猜测起草终止条件——首个项目 T01 就因附件没到，终止条件在 T02 全部重拟。
3. 契约定义已在手时，阶段 0 与阶段 1 的第 1–2 步合并成第一个回复：对需求的理解（一段话）；思考程度建议与理由；终止条件草案；初始议程；请用户确认的事项。写法见 `references/termination-conditions.md`。

### 阶段 1：立规矩
1. 从契约定义推出本项目的**访谈终止条件 T1–T7**（全部满足才输出 spec），列出**初始议程**（实质性缺口，Q-01 起）。
2. 请用户确认：① T1–T7；② 本次只产出 spec.md，设计文档与任务文档之后由 Claude Code 派生；③ 工作方式——记录落盘到 interview/ 并维护信息地图与检索策略；需要批准的提案都用审批台；反馈存 interview/reviews/ 并关联对话轮次；用户说"反馈完成"后 Claude 去读。
3. 用户确认后：`python3 <skill>/scripts/init_interview.py <项目> --name "<项目名>"` 建目录、登记表和审批台的共用设置（`interview/reviews/build/` 下的 `project.js` 与 `cfg_template.json`；项目文件夹名不只由字母、数字、`_`、`-` 组成时加 `--project-id`）；写 log/T01..（用户原话逐字）；记 D-001 终止条件、D-002 产出范围、D-003 工作方式；按 D-001 改写 `project.js` 里终止条件的说明。
4. 进入阶段 2，发出 R01。

### 阶段 2：访谈轮（循环；细节见 `references/interview-rounds.md`）
**发出一轮**
1. 选题：从议程里挑一组相互依赖的议题。顺序参考：目标、问题与范围 → 交付、验收与协作规则 → 口径、风险、部署与数据。上一轮遗留的冲突、歧义、未答项优先。R01 必含一条"现在最痛的是什么、代价是什么"，请用户讲一个真实案例——它是后面所有取舍的锚。
2. 调研与质疑：要挑战的点先查证，写 `interview/research/Rxx_evidence.md`，新来源登记 S-编号（置信度、核验日期）。
3. 设计这一轮：先定要不要沙盘——这一轮讲的是"有哪些东西、谁产生、谁修改、谁能看到、怎么流动"（角色、数据对象、端到端流程）就做；不做就写一句为什么。再写卡片：一张卡一个决定，分组卡一点一个决定；需要细看的卡用简报四格开头（你在决定什么 / 我推荐与你会失去什么 / 实话 / 不同意会怎样），能画成图的不写成段落，完整的理由照样写进正文、由页面收进折叠；每个选项都写好处和代价；按信息形态选卡（分组确认 / 多选一 / 可多选 / 填写 / 单条确认）；标来源（你已定 / 推断 / 冷读 / 建议）与分量（需要细看 / 可快速确认）。凡是复述用户说过的话，先对照 log 原话与 decisions.md。
4. 生成审批台：在 `interview/reviews/build/` 写这一轮的 cfg 与数据（每轮相同的设置在 `project.js`），用 `desk_codes.py` 生成代号表，构建；`test.js` 全部通过才能往下走；做两遍的审批者冷读；发布为带数据库和另存能力的 Artifact，确认数据库可用；本地留副本，登记 `reviews/INDEX.md`。每轮放上一轮反馈的处理对照（PREV）、议程进度（AGENDA）和页面速览（BRIEF）。步骤与命令见 `references/interview-rounds.md` 第 5 节。
5. 回复用户：这一轮讲什么、几条、哪几条需要细看；请用户填完点"提交反馈"后说"反馈完成"。本轮到此结束，不替用户作答。

**收到"反馈完成"**
1. 取回反馈：读该轮 Artifact 数据库 `feedback/Rxx` 的 md；同时看用户贴在对话里的 Markdown（页面提交失败时说"没有提交成功"，请审批者把 Markdown 复制发过来）和另存的 `Rxx_<主题>_feedback*.md`（`interview/reviews/`、"下载"文件夹），比较"导出时间"，把最新的一份原样写成 `interview/reviews/Rxx_<主题>_feedback.md`，并告诉用户用的是哪一份（`references/interview-rounds.md` 第 6 节）。
2. 逐条处理（规则表见 interview-rounds.md 第 6 节）：批准 → D；评论里的事实 → F；只写评论没选选项 → 以评论为准记 D 并注明；勾选与评论对不上、评论与已批准决定冲突 → 记 Q，下一轮问，不自行调和；未答的填写项 → 留在议程；评论带出的新能力 → 下一轮提议，不自行加入范围。
3. 收尾（见下方清单）。
4. 判断：实质性议程都已定（或已有假设/待决安排）→ 阶段 3；否则发下一轮。

**用户追问某条的意思（澄清轮）**：用白话 + 场景 + 例子回答。发现是自己写错了，直接承认，改措辞，必要时记 F 或新增条目，重建后在原链接重新发布：本地副本先备份；条目含义变了，把数据里的 `KEY` 升到 `Rxx-feedback-v2`，旧答案和旧草稿不再套用；反馈轮次顺延，记进 log 与 reviews/INDEX.md。用户对审批台的呈现提意见，改审批台 skill 本身（在它的模板里改、写 CHANGELOG、升 VERSION，见 interview-rounds.md 第 8 节），再重建当前轮。澄清轮的 log 写"本轮决定：无（澄清）"。

### 阶段 3：起草、冷读、签署
1. 按 `templates/spec_skeleton.md` 与 `references/spec-writing.md` 起草 spec.md v0.1（状态"待确认草案"）。一开始就写好 §0.5 权威顺序（含基线之后的决定如何生效、派生契约能做什么）。
2. `python3 <skill>/scripts/check_spec.py <项目>`：追溯、格式、遗留标记。
3. 冷读（`references/cold-read.md`）：同时启动两个独立子 Agent，只读契约文件——设计者视角列阻塞问题，验收者视角列不可判定项与矛盾。能由已批准决定直接推出的澄清直接改，标"（第 N 轮冷读修订）"；涉及范围、权限、可见范围、验收标准的记 Q 交用户；新补的规则标 `[推断]`。记录写 `interview/research/coldread.md`。
4. 签署轮：审批台列出冲突、推断（按主题分组）、冷读结果，最后一条问"本轮之后 spec 怎么处理"（多选一，每个选项写好处与代价；推荐：修订 → 冷读 → 批准为基线 v1.0）。
5. 修订 → 冷读 → 确认，循环。要不要再开一轮由 Claude 判断：有按用户简短评论展开的新流程（含推断细节），或冷读发现权限空缺 → 再开一轮"只核对、不重谈"；否则展示修改处后定稿（标准见 `references/baseline-and-change.md`）。
6. 定稿：写入最后一轮结论；去掉 `[推断]` 与"待确认"；最后一次冷读；自检（`templates/selfcheck.md`：T1–T7 与契约定义第七节 7 问）；`check_spec.py --baseline` 无错误；状态改为"已批准基线 v1.0"，记 D-编号。
7. 每次升版本：`python3 <skill>/scripts/snapshot_spec.py <项目> --version vX.Y`，存快照与逐行对比。

### 阶段 4：基线之后（`references/baseline-and-change.md`）
- **定稿修订**（由已批准决定直接推出、不改目标范围权限的修订）不单独开轮，但必须在下一轮审批台逐组列出（对照式的点：位置、现在的写法 → 改后的写法），交用户核对。
- **变更**：改需求内容的修改写 `interview/changes/CR-xxx_proposal.md` → 审批台批准（同样用对照式的点）→ 并入 spec，文中标"（CR-xxx）"，§14.1 记变更，§14.2 留原文 → 升 v1.x → 快照。
- **派生契约**（用户要分阶段交付时，如交互原型、MVP）：只能裁剪基线范围、补充阶段要求、写明经批准的限时过渡做法；不能改基线需求。方案审批 → 起草 → 冷读 → 签署。
- **交接**：写 HANDOFF.md（`templates/HANDOFF.md`）；会话绑定 claude.ai Project 时，在项目里维护一份指向本地记录的指针文档。

## 每轮收尾清单
- [ ] `log/Txx.md`：用户原话逐字；Claude 回复要点（终止条件这类关键定义写全文）；本轮决定；本轮动作
- [ ] `registry/decisions.md`：新增 D、F；被取代的标注
- [ ] `registry/open_items.md`：新增或更新 Q、A（进 spec §11、§13 的也要登记）
- [ ] `registry/sources.md`：新来源 S
- [ ] `reviews/INDEX.md`：本轮提案、Artifact 链接、反馈文件及其来源（数据库 / 对话里贴的 / 用户另存的文件）、审批台版本、轮次
- [ ] `INDEX.md`：当前状态、轮次表
- [ ] spec 有改动：版本号、修订记录、快照与对比
- [ ] `python3 <skill>/scripts/status.py <项目>` 核对编号、待决与审批台版本

## 新会话接续
先跑 `status.py`，再依次读：`interview/INDEX.md` → `registry/decisions.md` → `registry/open_items.md` → `reviews/INDEX.md` 里最新一轮的反馈文件。要找用户原话查 `log/Txx.md`。冲突时的权威顺序：契约定义 > decisions.md > 最新反馈 > log > 提案 HTML。

## 最容易出错的地方（全部见 `references/lessons.md`）
- 复述用户说过的事实前，对照 log 原话（首个项目把"人上传纪要、Agent 起草共识与待办"写成了"会议纪要起草"）。
- 评论和已批准决定冲突、勾选和评论对不上：下一轮问，不要自己调和。
- "提醒""通知""同步"这类动词，要写清发到哪里、谁收、处理后变成什么状态（首个项目漏了收件箱）。
- 外部最佳实践只是建议：用户否决了"时长只看 ≥5 人汇总"，改为按个人统计、只对开发者可见。
- 用户说"默认可行"的外部条件，记为假设，并写不成立时系统怎么表现。
- 基线之后的研发安排与派生契约的权限，在 §0.5 一开始就写好，否则得事后改基线（首个项目 CR-002 ①②）。
- 冷读子 Agent 不能读访谈记录，否则会用背景知识补上文档的空白。
- 审批台：不预填任何答案；发布后条目含义变了要升 `KEY`；`test.js` 没通过不发布（这几条审批台已内置，用它的最新版）。"反馈完成"时数据库可能是空的或旧的：网络一断，v3.7.1 的提交就会失败，页面请审批者把 Markdown 复制发过来；所以先看对话里贴的和另存的 md，比较导出时间，不要一上来就请用户重填。

## 文件
- `references/contract-definition.md`：需求契约定义（用户原文）
- `references/termination-conditions.md`：终止条件 T1–T7、初始议程、第一个回复的写法
- `references/interview-rounds.md`：选题、调研与质疑、挖掘、条目设计、审批台接口、反馈处理规则、澄清轮、改审批台
- `references/records.md`：目录、编号、各文件写法、检索策略
- `references/spec-writing.md`：spec 各节写法与格式约定（check_spec.py 依赖这些约定）
- `references/cold-read.md`：冷读规则与子 Agent 提示词
- `references/baseline-and-change.md`：签署、定稿判断、版本、变更、派生契约、交接
- `references/lessons.md`：教训（现象 → 规则 → 出处）
- `templates/`：INDEX、log_Txx、decisions、open_items、sources、reviews_INDEX、evidence_Rxx、coldread、selfcheck、CR_proposal、spec_skeleton、HANDOFF；审批台的共用设置 review_project.js、review_cfg.json（init_interview.py 复制到 `interview/reviews/build/`）
- `scripts/init_interview.py`：建 interview/ 目录、登记表与审批台的共用设置（不覆盖已有文件）
- `scripts/status.py`：当前轮次、待反馈的审批轮、下一个可用编号、未决事项、spec 版本与快照、审批台版本
- `scripts/desk_codes.py`：按本 skill 的记录生成审批台的代号表 codes.js（调用审批台的 build_codes.py）
- `scripts/check_spec.py`：追溯与格式检查（`--baseline` 用于定稿前）
- `scripts/snapshot_spec.py`：版本快照与逐行对比
- `README.md`、`CHANGELOG.md`、`VERSION`：仓库说明、版本记录与当前版本；`local.md`（如有）：本机说明，不进仓库
