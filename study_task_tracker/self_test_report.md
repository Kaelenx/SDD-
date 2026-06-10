# self_test_report.md - 自测调试报告

## 1. 自测环境

| 项目 | 内容 |
|------|------|
| 操作系统 | Windows |
| Python | 3.12.12 |
| 依赖 | Python 标准库、浏览器 |
| 测试日期 | 2026-06-10 |

## 2. 测试命令

```powershell
python -m unittest discover -s tests
python tools/coverage_report.py
$env:PYTHONPATH = "src"
python -m study_tracker.server --host 127.0.0.1 --port 8765
```

## 3. 测试结果

| 测试项 | 命令/方式 | 结果 |
|--------|-----------|------|
| 后端/API/服务/存储单元测试 | `python -m unittest discover -s tests` | 35 个测试全部通过 |
| 覆盖率 | `python tools/coverage_report.py` | 总行覆盖率 86.4%，命令正常退出 |
| 后端健康检查 | `GET /api/health` | 返回 `{"status": "ok"}` |
| 浏览器冒烟测试 | 打开 `http://127.0.0.1:8765` | 页面正常渲染 |
| 前端新增任务 | 浏览器表单提交 | 新增 T0001，摘要 total=1、pending=1 |
| 前端完成任务 | 点击任务卡片“完成”按钮 | 状态变为已完成，摘要 done=1、pending=0 |
| 前端搜索与优先级筛选 | 搜索“升级验证”并选择高优先级 | 只显示匹配任务 |
| 前端编辑任务 | 点击编辑、修改标题、保存 | 标题更新为“升级验证任务-已编辑” |
| 完成率进度条 | 完成 1/2 个任务 | 完成率显示 50% |
| 任务备注和预计小时 | 新增任务时填写备注与 3.5 小时 | 列表显示备注和小时 |
| 课程统计 | 新增数据结构课程任务 | 课程统计面板显示数据结构课程汇总 |
| 批量完成 | 勾选 T0003、T0004 并点击完成所选 | 两项任务批量完成，完成率 100% |
| 批量选择状态修复 | 批量完成后切到待完成空列表 | 选择数清零，按钮禁用 |
| 工程化前端模块加载 | 打开页面检查 module script | `frontend/app/main.js` 正常加载 |
| 工程化后核心交互 | 新增“工程化验证任务” | 摘要和课程统计正常刷新 |
| 浏览器控制台 | 读取 error 级别日志 | 无错误 |
| 清理后刷新 | 删除演示数据后刷新页面 | 页面显示“暂无任务”，摘要均为 0 |

覆盖率明细：

| 文件 | 覆盖率 |
|------|--------|
| `src/study_tracker/__init__.py` | 100.0% |
| `src/study_tracker/application/task_service.py` | 96.6% |
| `src/study_tracker/domain/task.py` | 87.2% |
| `src/study_tracker/infrastructure/json_repository.py` | 88.4% |
| `src/study_tracker/web/http_server.py` | 74.5% |
| `src/study_tracker/web/serializers.py` | 100.0% |
| Total | 86.4% |

## 4. 交付检查

| 检查项 | 结果 |
|--------|------|
| `spec.md` 完整性 | 通过 |
| `plan.md` 前后端架构和依赖 | 通过 |
| 任务与代码一致 | 通过 |
| 后端 API 单元测试通过 | 通过 |
| 覆盖率输出 | 通过 |
| 前端页面正常运行 | 通过 |
