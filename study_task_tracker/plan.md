# plan.md - 前后端技术定义与实现计划

## 1. 技术选型

| 项目 | 选择 | 原因 |
|------|------|------|
| 后端语言 | Python 3.12 | 环境已具备，标准库可完成 HTTP 服务 |
| 后端框架 | `http.server` | 标准库，无需安装依赖，适合小型作业 |
| API 格式 | REST + JSON | 前后端交互清晰，便于测试 |
| 前端 | HTML + CSS + JavaScript | 零构建步骤，浏览器直接运行 |
| 数据存储 | JSON 文件 | 轻量、可读、便于单元测试 |
| 单元测试 | unittest | Python 标准库 |
| 覆盖率 | 自定义 `sys.settrace` 脚本 | 不依赖第三方 coverage 包 |

## 2. 项目结构

```text
study_task_tracker/
  spec.md
  plan.md
  tasks.md
  README.md
  root_cause_analysis.md
  self_test_report.md
  frontend/
    index.html
    styles.css
    app.js
  src/
    study_tracker/
      __init__.py
      models.py
      store.py
      service.py
      server.py
  tests/
    test_api.py
    test_service.py
    test_store.py
  tools/
    coverage_report.py
```

## 3. 架构设计

采用前后端分离结构：

| 层 | 文件 | 职责 |
|----|------|------|
| 前端页面 | `frontend/index.html` | 页面结构、表单、任务列表 |
| 前端样式 | `frontend/styles.css` | 响应式布局、表单、任务卡片、摘要区样式 |
| 前端逻辑 | `frontend/app.js` | 调用 REST API、渲染列表、处理筛选、编辑和按钮交互 |
| HTTP/API 层 | `src/study_tracker/server.py` | 静态资源服务、REST 路由、JSON 请求响应 |
| 服务层 | `src/study_tracker/service.py` | 新增、查询、完成、删除、摘要 |
| 领域层 | `src/study_tracker/models.py` | 任务实体、校验规则、领域异常 |
| 存储层 | `src/study_tracker/store.py` | JSON 文件读写 |

调用方向：

```text
Browser UI -> fetch('/api/...') -> server.py -> StudyTaskService -> JsonTaskRepository -> JSON file
                                      |
                                      -> frontend static files
```

## 4. API 设计

### GET `/api/tasks`

查询任务。可选 query：`status=pending|done`、`priority=high|medium|low`、`q=关键词`。

### POST `/api/tasks`

请求体：

```json
{
  "title": "完成单元测试练习",
  "course": "软件工程",
  "due_date": "2026-06-10",
  "priority": "high"
}
```

### PATCH `/api/tasks/{id}/complete`

标记任务完成。

### PATCH `/api/tasks/{id}`

编辑任务标题、课程、截止日期和优先级。

### DELETE `/api/tasks/{id}`

删除任务。

### GET `/api/summary`

返回：

```json
{
  "total": 1,
  "pending": 0,
  "done": 1,
  "overdue": 0
}
```

## 5. 数据存储设计

默认数据文件为 `data/tasks.json`，运行时也可通过 `--data-file` 指定。

```json
[
  {
    "id": "T0001",
    "title": "完成前后端作业",
    "course": "软件工程",
    "due_date": "2026-06-10",
    "priority": "high",
    "status": "pending",
    "created_at": "2026-06-10",
    "completed_at": null
  }
]
```

## 6. 前端交互设计

| 区域 | 交互 |
|------|------|
| 摘要区 | 展示全部、待完成、已完成、逾期数量 |
| 进度条 | 根据 done/total 展示完成率 |
| 新增任务表单 | 输入标题、课程、日期、优先级后提交 |
| 编辑模式 | 点击编辑后复用表单保存任务修改，可取消编辑 |
| 筛选工具栏 | 支持搜索、优先级筛选、状态筛选 |
| 任务卡片 | 展示任务信息，支持编辑、完成和删除 |
| 消息区 | 显示新增、完成、删除或错误提示 |

## 7. 测试策略

| 测试类型 | 覆盖内容 |
|----------|----------|
| API 测试 | 健康检查、静态页面、创建、列表、搜索筛选、编辑、完成、删除、非法输入 |
| 服务层测试 | 业务校验、ID 生成、搜索筛选、编辑、状态流转、摘要 |
| 存储层测试 | 文件不存在、空文件、正常读写、非法 JSON、非法任务结构 |
| 覆盖率脚本 | 统计 `src/study_tracker` 下源码行覆盖率 |
| 浏览器冒烟测试 | 打开页面、提交任务、完成任务、查看摘要 |

## 8. 风险与对策

| 风险 | 影响 | 对策 |
|------|------|------|
| 评审环境无法安装依赖 | 项目不可运行 | 使用 Python 和浏览器标准能力 |
| API 与前端字段不一致 | 页面提交失败 | API 测试和浏览器冒烟测试共同验证 |
| JSON 数据损坏 | 后端异常 | 转换为 StorageError 并返回受控错误 |
| 覆盖率脚本过慢 | 验收命令不稳定 | 只跟踪 `src/study_tracker` 源码 |

## 9. 运行方式

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
