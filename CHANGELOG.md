# 版本记录

- **v1.1.1（2026-11-24）**：加上 Apache-2.0 许可证（`LICENSE`），README 写明许可。
- **v1.1.0（2026-11-24）**：适配审批台 interactive-approval-desk v3.7.2，并整理为公开仓库。
  - 审批台接口（`references/interview-rounds.md` 第 5 节）按审批台 v3.5 起的用法重写：模板和自检取自审批台，不再复制进项目；cfg 必须写 `PROJECT`；输出 `Rxx_<主题>_proposal.html` 与 `_artifact.html`；`test.js` 全部通过才发布；两遍的审批者冷读；发布时声明 `db` 和 `downloads`。
  - 卡片设计（第 4 节）按 v3.7、v3.7.1：先定沙盘，不做就写 `NO_SANDBOX`；需要细看的卡用简报四格；按数据画图；选项两边都写；改动写成对照式的点；页面速览 `BRIEF`；`PREV` 的状态列。
  - 取回反馈（第 6 节）按 v3.7.2：同时找用户另存的 md，比较导出时间用最新的一份，并说明来源；草稿不能当反馈。
  - 新增 `templates/review_project.js`、`templates/review_cfg.json`（每轮共用的终止条件、名词与 cfg），由 `init_interview.py` 生成到 `interview/reviews/build/`；新增 `scripts/desk_codes.py`（按本 skill 的记录生成审批台代号表）；`status.py` 显示审批台版本和缺少的共用设置；`check_spec.py` 提示审批台认不出的功能需求编号。
  - 公开整理：去掉本机路径和首个项目的内部细节（本机信息放在不进仓库的 `local.md`）；审批台的默认位置改为本目录旁边的 `../approval_desk`；新增 README.md、CHANGELOG.md、VERSION。
- **v1.0.0（2026-11-15）**：首版（未公开）。从首个项目的过程提炼出阶段 0–4、底线、终止条件、访谈轮与反馈处理规则、记录体系、spec 写法、冷读、基线与变更、教训，以及模板和 4 个脚本（init_interview、status、check_spec、snapshot_spec）。按审批台 v3.4 写。
