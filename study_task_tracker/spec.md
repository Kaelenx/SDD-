# spec.md - 前后端学习任务追踪器需求规格说明

## 1. 项目概述

学习任务追踪器是一个前后端分离的小型 Web 项目。前端提供学习任务看板和表单，后端提供 REST API 和 JSON 数据持久化。项目目标是以可运行的前后端形态完整展示 SDD 标准流程：需求澄清、技术规划、编码测试、根因分析和构建交付。

## 2. 用户与场景

### 目标用户
- 需要管理课程作业、复习计划和练习任务的学生。
- 需要提交一个完整 SDD 学习成果项目的学生。

### 核心场景
1. 学生在网页表单中新增学习任务。
2. 学生在任务列表中查看全部、待完成或已完成任务。
3. 学生点击按钮将任务标记为完成。
4. 学生删除误建任务。
5. 学生通过顶部摘要查看全部、待完成、已完成和逾期数量。

## 3. 功能需求

| 编号 | 需求 | 验收标准 |
|------|------|----------|
| FR-01 | 前端新增任务 | 输入标题、课程、截止日期、优先级后，前端调用后端 API 创建任务 |
| FR-02 | 前端查看任务 | 页面可展示任务卡片，包含 ID、状态、优先级、截止日期、课程和标题 |
| FR-03 | 状态筛选 | 可按全部、待完成、已完成筛选任务 |
| FR-04 | 搜索与优先级筛选 | 可按标题、课程、ID 搜索，并按 high/medium/low 筛选 |
| FR-05 | 编辑任务 | 点击编辑后，表单进入编辑模式，可修改标题、课程、日期和优先级 |
| FR-06 | 完成任务 | 点击完成按钮后，后端状态更新为 done，页面刷新 |
| FR-07 | 删除任务 | 点击删除按钮后，后端删除任务，页面刷新 |
| FR-08 | 摘要统计 | 页面展示 total、pending、done、overdue 四项统计 |
| FR-09 | 完成进度 | 页面根据 done/total 展示完成率和进度条 |
| FR-10 | REST API | 后端提供任务 CRUD 相关 API，并返回 JSON |
| FR-11 | 数据持久化 | 任务数据保存在本地 JSON 文件，服务重启后可读取 |
| FR-12 | 静态资源服务 | 后端可直接服务 `frontend/` 下的 HTML、CSS、JS |

## 4. API 需求

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 健康检查 |
| GET | `/api/tasks?status=pending&priority=high&q=python` | 查询任务，status、priority、q 可选 |
| POST | `/api/tasks` | 新增任务 |
| PATCH | `/api/tasks/{id}` | 编辑任务 |
| PATCH | `/api/tasks/{id}/complete` | 标记任务完成 |
| DELETE | `/api/tasks/{id}` | 删除任务 |
| GET | `/api/summary` | 获取摘要统计 |

## 5. 数据定义

| 字段 | 类型 | 说明 | 约束 |
|------|------|------|------|
| id | str | 任务唯一标识 | 系统生成，不允许为空 |
| title | str | 任务标题 | 必填，1-80 字符 |
| course | str | 课程/主题 | 可选，默认 General，最长 40 字符 |
| due_date | str | 截止日期 | 必填，YYYY-MM-DD |
| priority | str | 优先级 | low、medium、high 之一 |
| status | str | 状态 | pending 或 done |
| created_at | str | 创建日期 | YYYY-MM-DD |
| completed_at | str/null | 完成日期 | 未完成时为 null |

## 6. 业务边界

### 范围内
- 浏览器页面交互。
- 后端 REST API。
- 本地 JSON 文件存储。
- 单用户任务管理。
- 任务新增、查询、筛选、完成、删除、摘要。
- 对输入数据、请求体和数据文件进行异常处理。

### 范围外
- 不做登录、多用户、权限管理。
- 不做数据库、云同步或消息提醒。
- 不做复杂搜索、标签体系、甘特图或日历集成。
- 不做部署到公网。

## 7. 异常边界

| 异常场景 | 处理方式 | 对应测试 |
|----------|----------|----------|
| 标题为空或超过 80 字符 | 后端返回 400 JSON 错误 | `test_invalid_payload_returns_bad_request`、`test_add_task_rejects_blank_title` |
| 课程名超过 40 字符 | 后端返回 400 JSON 错误 | `test_add_task_rejects_long_course` |
| 截止日期格式错误 | 后端返回 400 JSON 错误 | `test_add_task_rejects_invalid_due_date` |
| 优先级非法 | 后端返回 400 JSON 错误 | `test_add_task_rejects_invalid_priority` |
| 编辑任务输入非法 | 后端返回 400 JSON 错误 | `test_invalid_update_returns_bad_request` |
| 完成不存在任务 | 服务层抛出 TaskNotFoundError，API 返回 400 | `test_complete_missing_task_raises` |
| 删除不存在任务 | 服务层抛出 TaskNotFoundError，API 返回 400 | `test_delete_missing_task_raises` |
| 请求体不是合法 JSON | API 返回 400 JSON 错误 | `server.py` 中 `_read_json_body` |
| 数据文件不存在 | 后端按空列表处理 | `test_repository_returns_empty_when_file_missing` |
| 数据文件内容损坏 | 存储层抛出 StorageError | `test_repository_rejects_invalid_json` |

## 8. 非功能需求

| 类别 | 要求 |
|------|------|
| 可运行性 | Python 3.12 标准库即可启动后端和前端 |
| 可测试性 | 后端 API、服务层、存储层均有单元测试 |
| 可维护性 | 前端静态资源与后端 API 分离 |
| 可移植性 | 不依赖外部数据库或第三方 Python 包 |
| 可读性 | SDD 文档、任务、代码和测试保持一致 |
| 响应式 | 前端在桌面和移动宽度下都可使用 |

## 9. 验收标准

1. 根目录下存在 `spec.md`、`plan.md`、`tasks.md`、源码、前端文件和单元测试。
2. `spec.md` 覆盖需求、业务边界、异常边界。
3. `plan.md` 覆盖前后端架构、API、依赖、测试策略。
4. `tasks.md` 中任务与最终代码、测试文件一致。
5. 执行 `python -m unittest discover -s tests` 后全部测试通过。
6. 执行 `python tools/coverage_report.py` 后输出覆盖率。
7. 执行 `python -m study_tracker.server` 后浏览器可访问页面并完成新增、编辑、筛选、完成等核心流程。
