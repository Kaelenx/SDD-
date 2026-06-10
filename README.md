# SDD 学习任务追踪器

这是一个用于 SDD 作业交付的前后端分离项目，完整覆盖需求澄清、技术规划、任务拆分、编码测试、根因分析和自测交付。

项目主体位于 [`study_task_tracker`](./study_task_tracker)。

## 项目功能

- 学习任务新增、编辑、完成、删除
- 状态筛选、优先级筛选、关键词搜索
- 任务备注、预计耗时、剩余小时统计
- 按课程统计任务数量、逾期数量和剩余工作量
- 勾选多条任务批量完成
- 导出任务、摘要和课程统计 JSON
- 前端使用原生 ES modules 拆分 API、状态、表单、渲染和入口模块
- 后端按 domain/application/infrastructure/web 分层

## 快速运行

PowerShell：

```powershell
cd study_task_tracker
$env:PYTHONPATH = "src"
python -m study_tracker.server --host 127.0.0.1 --port 8765
```

浏览器访问：

```text
http://127.0.0.1:8765
```

## 测试与覆盖率

```powershell
cd study_task_tracker
python -m unittest discover -s tests
python tools/coverage_report.py
```

当前验证结果：

- 单元测试/API 测试：35 个测试通过
- 源码覆盖率：86.4%
- 无第三方依赖，仅使用 Python 标准库和浏览器能力

## 目录结构

```text
study_task_tracker/
  frontend/
    index.html
    styles.css
    app/
      api.js
      dom.js
      form.js
      format.js
      main.js
      render.js
      state.js
  src/
    study_tracker/
      domain/
      application/
      infrastructure/
      web/
      server.py
  tests/
  tools/
  spec.md
  plan.md
  tasks.md
  self_test_report.md
  root_cause_analysis.md
```

## SDD 交付材料

- [`spec.md`](./study_task_tracker/spec.md)：需求规格、业务边界、异常边界
- [`plan.md`](./study_task_tracker/plan.md)：技术定义、架构、API、测试策略
- [`tasks.md`](./study_task_tracker/tasks.md)：任务拆分与代码一致性
- [`self_test_report.md`](./study_task_tracker/self_test_report.md)：自测调试报告
- [`root_cause_analysis.md`](./study_task_tracker/root_cause_analysis.md)：根因分析记录
