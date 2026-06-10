# tasks.md - 任务拆分与代码一致性记录

| 任务 ID | 任务内容 | 产物文件 | 验证方式 | 状态 |
|---------|----------|----------|----------|------|
| T-01 | 编写前后端需求规格，明确业务和异常边界 | `spec.md` | 人工检查验收项 | Done |
| T-02 | 编写前后端技术计划，明确架构和依赖 | `plan.md` | 人工检查架构、API、依赖描述 | Done |
| T-03 | 实现任务实体、校验和异常 | `src/study_tracker/models.py` | `tests/test_service.py` | Done |
| T-04 | 实现 JSON 存储读写 | `src/study_tracker/store.py` | `tests/test_store.py` | Done |
| T-05 | 实现学习任务服务层，包含新增、筛选、编辑、完成、删除、摘要 | `src/study_tracker/service.py` | `tests/test_service.py` | Done |
| T-06 | 实现 REST API 和静态资源后端，包含搜索筛选与编辑接口 | `src/study_tracker/server.py` | `tests/test_api.py` | Done |
| T-07 | 实现前端页面、样式和交互，包含搜索、筛选、编辑和完成进度 | `frontend/index.html`、`frontend/styles.css`、`frontend/app.js` | 浏览器冒烟测试 | Done |
| T-08 | 实现单元测试和覆盖率脚本 | `tests/`、`tools/coverage_report.py` | `python -m unittest discover -s tests`、`python tools/coverage_report.py` | Done |
| T-09 | 完成自测、根因分析和交付检查 | `self_test_report.md`、`root_cause_analysis.md` | 自测报告 | Done |

## 一致性规则

- 每个实现任务必须能在源码、前端文件或测试文件中找到对应产物。
- 若代码范围调整，必须同步更新本文件。
- 交付前所有任务状态应为 Done。
