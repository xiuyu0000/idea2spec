---
name: reviews-index
description: 审批轮登记表：每轮的提案文件、Artifact 链接、反馈文件及其来源、对应对话轮次与审批台版本；附取回反馈的步骤和构建、自检命令。
---
# 审批轮登记

| 审批轮 | 主题 | 提案发出 | 反馈轮次 | 本地提案 | Artifact（托管审批台；反馈在其数据库 feedback/Rxx，进度在 drafts/Rxx） | 反馈文件（来源） | 审批台版本 | 状态 |
|---|---|---|---|---|---|---|---|---|

## 取回反馈的步骤（用户说"反馈完成"后）
1. 读该轮 Artifact 的数据库：collection=feedback，doc_id=Rxx，取 md 字段（工具名随环境，如 ArtifactData get、db_get）。
2. 同时看另外两种来源：用户贴在对话里的 Markdown（页面提交失败时说"没有提交成功"，请审批者把 Markdown 复制发过来），和本文件夹、"下载"文件夹里用户另存的 `Rxx_<主题>_feedback*.md`（页面上的"💾 另存一份 md 到本机"）。数据库里也可能是更早的一次提交。"下载"文件夹要用户授权才能看。
3. 比较每份的"- 导出时间："一行，把最新的一份原样写成 `Rxx_<主题>_feedback.md`；本文件夹里已有更新的文件时不覆盖。在上表"反馈文件"一栏写明用的是哪一份（数据库 / 对话里贴的 / 另存的文件），并告诉用户。
4. 都没有：数据库 drafts/Rxx 里是用户的进度和半成品 md，只能看进度、不能当反馈；请用户回到页面再点一次"提交反馈"，或复制 Markdown 发过来、另存一份放进本文件夹。

## 构建与自检（在 build/ 里；`<skill>` 是 idea2spec，`<desk>` 是审批台 skill interactive-approval-desk：https://github.com/xiuyu0000/interactive-approval-desk）
- 代号表：`python3 <skill>/scripts/desk_codes.py <项目>`（写出 build/codes.js）
- 构建：`python3 <desk>/round_template/build.py cfg_rXX.json`
- 自检：`NODE_PATH=<装有 playwright 的 node_modules> node <desk>/round_template/test.js Rxx`，结尾必须是"✓ 全部通过"
- 冷读材料：`NODE_PATH=… node <desk>/round_template/dumptext.js out.txt Rxx`（两遍：默认显示的，再全部展开的）
- 发布：Artifact 发布 `Rxx_<主题>_artifact.html`，声明 `capabilities: {db: {}, downloads: true}`；本地副本放本文件夹，发布版放 artifact/
