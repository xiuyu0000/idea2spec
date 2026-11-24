# 记录体系

## 目录
```
<项目>/
├─ 需求契约概念说明.md      契约定义（上游权威）
├─ spec.md                 需求契约（草案 v0.x → 基线 v1.0 → v1.x）
├─ prototype_contract.md   （按需）派生契约
├─ mvp_contract.md         （按需）派生契约
├─ HANDOFF.md              （收尾）交接清单
└─ interview/
   ├─ INDEX.md             信息地图：目标、当前状态、目录、轮次表、编号体系、检索策略
   ├─ log/Txx.md           每轮对话：用户原话（逐字）+ Claude 回复 + 本轮决定 + 本轮动作
   ├─ registry/
   │  ├─ decisions.md      已批准决定 D-xxx（唯一的"已批准"来源）与来源事实 F-xxx
   │  ├─ open_items.md     议程、待决、假设 Q-xx、A-xx 及状态
   │  └─ sources.md        调研来源 S-xx
   ├─ research/            Rxx_evidence.md 调研简报；coldread.md 冷读记录；selfcheck.md 终止条件与自检
   ├─ reviews/             INDEX.md 审批轮登记；Rxx_<主题>_proposal.html；Rxx_<主题>_feedback.md；artifact/ 发布版；build/ 每轮的 cfg、数据与代号表（project.js、cfg_template.json、cfg_rXX.json、data_rXX.js、codes.js；模板取自审批台，不复制）
   ├─ spec_versions/       spec_vX.Y.md 快照与 diff_vA_vB.md 逐行对比
   ├─ changes/             CR-xxx_proposal.md 基线变更提议
   └─ _to_delete/          （需要时）没有删除权限时放误建的文件
```

## 编号
| 编号 | 含义 | 在哪 |
|---|---|---|
| Txx | 对话轮次（用户一条消息 + Claude 的处理） | log/ |
| Rxx、Rxx-nn | 审批轮与其中的条目 | reviews/ |
| D-xxx | 用户批准的决定 | decisions.md |
| F-xxx | 用户陈述的来源事实 | decisions.md |
| Q-xx | 议程、待决、冲突、澄清 | open_items.md；进 spec 的写在 §13 |
| A-xx | 假设（含外部依赖） | open_items.md；spec §11 |
| S-xx | 外部调研来源 | sources.md |
| CR-xxx | 基线变更 | changes/；spec §14.1 |
| FR-<域>-nn、ACn、INV-nn、NFR-nn、Mn、Gn、Nn | spec 内的功能需求、验收用例、不变量、非功能要求、指标、目标、明确不做 | spec.md |

- 编号只增不复用；没采用的编号保留空缺并说明（首个项目：M4 没被采用，编号空缺）。
- Rxx 在某个 T 发出，在下一个 T 收到反馈，二者都写进 reviews/INDEX.md。澄清轮会让反馈轮次顺延。
- 给用户看的页面里，代号都要能悬浮看到解释（审批台自动处理）；聊天回复里第一次提到代号时带上中文名。

## 各文件写法
- **log/Txx.md**（`templates/log_Txx.md`）：front matter 写 turn、date、status、related。"用户原话（逐字）"原样粘贴，包括标签与格式；附件写明文件名和是否收到。Claude 回复写要点，关键定义写全文（如终止条件）。"本轮获准决定"列 D 编号。"Claude 本轮动作"写改了哪些文件、发了哪轮审批台（链接）。被后续轮次修订的，status 写"已被 Txx 修订（哪部分）"。
- **decisions.md**（`templates/decisions.md`）：列"编号 / 决定 / 来源 / 状态"。决定写内容本身，单独读也能懂；来源写"Rxx-nn / Txx"或"Txx"；状态用：有效 / 有效（细节待 Rxx）/ 部分有效 / 有效（××部分已被 D-xxx 取代）/ 已被 D-xxx 取代 / 有效（经 CR-xxx 并入基线 vX.Y）。后续轮次把细节定下后，回头更新早先决定的状态。F 表列"编号 / 事实 / 来源"。
- **open_items.md**（`templates/open_items.md`）：列"编号 / 议题 / 类型 / 所在审批轮 / 状态"。类型：实质性缺口、澄清、冲突、冷读发现、遗漏补全、推断、范围、新阶段、开工参数、假设、外部依赖假设。状态：待定（决定人、时机）/ 已定（D-xxx）/ 部分已答（…）/ 记录在案 / 取消（D-xxx）。进 spec §11、§13 的 A、Q 也要在这里登记（check_spec.py 会提示漏登）。
- **sources.md**（`templates/sources.md`）：列"编号 / 来源 / 要点 / 置信 / 首次使用"；表头写核验日期。
- **reviews/INDEX.md**（`templates/reviews_INDEX.md`）：列"审批轮 / 主题（条数、重发说明）/ 提案发出 / 反馈轮次 / 本地提案 / Artifact / 反馈文件（来源：数据库、对话里贴的或用户另存的文件）/ 审批台版本 / 状态"；附取回反馈的步骤与构建、自检命令。
- **INDEX.md**（`templates/INDEX.md`）：每轮更新"当前状态"和轮次表；目录有变化就更新地图。
- **research/**：`Rxx_evidence.md`（`templates/evidence_Rxx.md`）、`coldread.md`（`templates/coldread.md`，所有轮次写在一个文件里）、`selfcheck.md`（`templates/selfcheck.md`）。

## 检索策略（写进 INDEX.md）
1. 新会话：INDEX.md → decisions.md → open_items.md → reviews/INDEX.md 里最新一轮的反馈；不需要通读 log。
2. 按编号定位：`grep -rn "R01-05" interview/`，`grep -rn "D-00" interview/registry/`，`grep -rn "S-08" interview/`。
3. 找用户原话：log/Txx.md 的"用户原话（逐字）"；引用需求来源以此为准。
4. 判断是否已批准：只看 decisions.md。提案 HTML 里的推荐不是决定；反馈经 Claude 整理写入 decisions.md 后才算。
5. 权威顺序：契约定义（方法）> decisions.md > 最新反馈 > log > 提案 HTML。后来的有效决定覆盖早先的，但不删除历史，在 decisions.md 标"已被 D-xxx 取代"。
6. 每轮收尾必做：见 SKILL.md 的收尾清单。

## 其他
- 没有删除权限时，误建的文件移到 interview/_to_delete/，在 INDEX.md 里说明，请用户自己删。
- 会话绑定 claude.ai Project 时，在项目里写一份指针文档（如 `claude/interview_INDEX.md`）：本地记录在哪、阶段与当前状态、契约版本、关键决定、待决、下一步、审批台 skill 的位置与版本。阶段变化时更新，平时不必频繁改。
