# 学习任务追踪器

一个用于 SDD 作业交付的小型前后端分离项目。前端使用 HTML/CSS/JavaScript，后端使用 Python 标准库提供 REST API 和静态资源服务。

## 功能

- 新增、编辑、完成、删除学习任务
- 按状态和优先级筛选
- 按标题、课程或任务 ID 搜索
- 展示全部、待完成、已完成、逾期数量和完成率进度条
- 记录任务备注和预计小时
- 按课程统计任务数量、逾期和剩余小时
- 勾选多条任务批量完成
- 导出任务、摘要和课程统计 JSON

## 快速运行

PowerShell：

```powershell
cd E:\Project_Code\Codex\SD\study_task_tracker
$env:PYTHONPATH = "src"
python -m study_tracker.server --host 127.0.0.1 --port 8765
```

浏览器访问：

```text
http://127.0.0.1:8765
```

## 运行测试

```powershell
python -m unittest discover -s tests
python tools/coverage_report.py
```

## 交付文件

| 文件/目录 | 说明 |
|-----------|------|
| `spec.md` | 需求规格，包含业务边界和异常边界 |
| `plan.md` | 技术定义，包含前后端架构、API、依赖、测试策略 |
| `tasks.md` | 任务拆分与最终代码一致性记录 |
| `frontend/` | 前端页面、样式和 ES module 交互逻辑 |
| `frontend/app/` | 前端 API、状态、表单、渲染和入口模块 |
| `src/study_tracker/domain/` | 领域实体、校验规则和异常 |
| `src/study_tracker/application/` | 业务用例服务 |
| `src/study_tracker/infrastructure/` | JSON 存储适配器 |
| `src/study_tracker/web/` | HTTP 路由、静态资源服务和序列化 |
| `src/study_tracker/server.py` | 保持 `python -m study_tracker.server` 可运行的入口 |
| `tests/` | 单元测试和 API 测试 |
| `tools/coverage_report.py` | 覆盖率统计脚本 |
| `self_test_report.md` | 自测调试报告 |
| `root_cause_analysis.md` | 根因分析记录 |
