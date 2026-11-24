---
name: interview-index
description: {{PROJECT}}需求访谈的信息地图与检索策略。任何新会话先读本文件。
updated: {{DATE}}（T01）
---
# 访谈信息地图（INDEX）

**目标**：通过访谈产出《需求契约》spec.md，供 Claude Code 使用。定义见 ../需求契约概念说明.md；何时结束见访谈终止条件 T1–T7（用户批准后记入 decisions.md）。
**当前状态**：阶段 0 接收想法。下一步：拟定访谈终止条件，等用户确认。

## 1. 目录地图
```
<项目>/
├─ 需求契约概念说明.md        "需求契约"定义（上游权威）
├─ spec.md                    需求契约（尚未起草）
└─ interview/
   ├─ INDEX.md                本文件：地图 + 轮次表 + 检索策略
   ├─ log/Txx.md              每轮对话：用户原话（逐字）+ Claude 回复 + 本轮决定
   ├─ registry/
   │  ├─ decisions.md         已批准决定 D-xxx（唯一的"已批准"来源）与来源事实 F-xxx
   │  ├─ open_items.md        议程、待决、假设 Q-xx、A-xx 及状态
   │  └─ sources.md           调研来源 S-xx（链接、要点、置信）
   ├─ research/               Rxx_evidence.md 调研简报；coldread.md 冷读记录；selfcheck.md 终止条件与自检
   ├─ spec_versions/          spec.md 的历史版本（spec_vX.Y.md）与相邻版本的逐行对比（diff_vA_vB.md）
   ├─ changes/                基线变更提议（CR-xxx_proposal.md；批准后写入 spec §14.1）
   └─ reviews/
      ├─ INDEX.md             审批轮登记：提案文件、Artifact 链接、反馈文件、对应轮次
      ├─ Rxx_<主题>_proposal.html   审批台本地完整副本
      ├─ Rxx_<主题>_feedback.md     用户反馈（提案↔反馈对照），由 Claude 从 Artifact 数据库落盘
      ├─ artifact/            Artifact 发布版页面
      └─ build/               每轮审批台的 cfg、数据与代号表（project.js 为每轮共用的设置；模板取自审批台 skill，不复制）
```

## 2. 轮次表
| 轮次 | 内容 | 产出 | 关联 |
|---|---|---|---|
| T01 | 初始想法 | | log/T01.md |

## 3. 编号体系
- **Txx** 对话轮次；**Rxx** 审批轮（Rxx-nn 为条目）；**D-xxx** 已批准决定；**F-xxx** 用户陈述的来源事实；**Q-xx** 议程/待决；**A-xx** 假设；**S-xx** 调研来源；**CR-xxx** 基线变更。
- 审批轮与对话轮次的关系：Rxx 在某个 T 发出提案，在下一个 T 收到反馈，二者都写在 reviews/INDEX.md。

## 4. 检索策略
1. **新会话开场**：依次读 INDEX.md → registry/decisions.md → registry/open_items.md → reviews/INDEX.md 里最新一轮的 feedback.md。不需要通读 log。
2. **按编号定位**：`grep -rn "R01-05" interview/`、`grep -rn "D-00" interview/registry/`、`grep -rn "S-08" interview/`。
3. **找用户原话**：log/Txx.md 的"用户原话（逐字）"一节；引用需求来源时以此为准。
4. **判断是否已批准**：只有 decisions.md 里的 D-编号算"已批准决定"。提案 HTML 里的推荐不是决定；反馈 md 经 Claude 整理后才写入 decisions.md。
5. **权威顺序（冲突时）**：需求契约概念说明（方法） > decisions.md > 最新 feedback.md > log > 提案 HTML。后来的有效决定覆盖早先的，但不删除历史，在 decisions.md 标"已被 D-xxx 取代"。
6. **每轮收尾 Claude 必做**：写 log/Txx.md；更新 decisions.md、open_items.md、reviews/INDEX.md、本文件的当前状态与轮次表；新来源进 sources.md；spec 有改动就快照。
