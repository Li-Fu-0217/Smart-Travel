# 智慧旅游智能助手系统

面向旅游场景的全栈平台，核心能力：**旅游攻略 RAG 问答、旅游记录、旅游预约（防超卖）、行程模板与偏好提炼、智能助手（大模型 + 规则双模式）**。

## 项目简介

- **用户前台**（移动优先）：关怀看板、今日行程、行程规划与待办打卡、模板广场一键复制、预约/拼团报名、旅游记录、消息中心、智能助手聊天。
- **管理后台**：数据概览（8 KPI + 4 图表）、旅行者/行程/模板/预约/拼团/求助/攻略/记录/用户/日志/菜单管理，以及助手工具说明书与工具调用审计。
- **智能助手**：11 个工具、LangGraph ReAct（有 Key）与规则编排（无 Key，默认）双模式，待确认闸门防「助手自作主张下单」，工具级审计埋点。

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3.12 · FastAPI · SQLModel（钉死 0.0.22）· PyMySQL · LangGraph + LangChain · ChromaDB（本地嵌入） |
| 数据库 | MySQL 8（22 张表，`sql/system.sql` 为唯一权威 schema） |
| 前端 | Vue 3 · Vite · Element Plus · Pinia · ECharts · vue-router |
| 认证 | JWT + bcrypt（钉死 4.0.1）+ 图形验证码 |

## 架构图

```
┌──────────────────────────────┐
│   Vue 3 前端（两套端）          │
│   管理后台 /admin/* (ADMIN)    │
│   用户前台 /user/*  (USER)     │
└──────────────┬───────────────┘
               │ HTTP /api（Bearer JWT）
┌──────────────▼───────────────┐
│   FastAPI 后端（分层）          │
│   api → service → model(db)   │
│   权限闸门在 service 层        │
└───────┬──────────────┬───────┘
        │              │
┌───────▼──────┐  ┌────▼────────────────┐
│   MySQL 8    │  │  智能助手 app/agent/  │
│  (22 张表)   │  │  LangGraph ReAct     │
│              │  │  + ChromaDB(攻略向量) │
└──────────────┘  └─────────────────────┘
```

## 目录结构

```
travel-assistant/
├── README.md
├── ai操作记录.md            # 本地留痕（不进 git）
├── sql/system.sql           # 全量 schema + 种子（幂等，22 表）
├── docs/
│   ├── 施工规范.md           # 施工依据（不进 git）
│   └── 系统设计说明书.md      # 架构/分层/功能/数据库/智能体设计
├── fastapi/
│   ├── requirements.txt     # sqlmodel==0.0.22、bcrypt==4.0.1 钉死
│   ├── .env.example         # 全部配置项
│   ├── dev.bat              # Windows 一键启动
│   └── app/
│       ├── main.py          # 入口 + 异常处理器
│       ├── core/            # 配置 / 依赖注入 / 安全
│       ├── common/          # 常量词表 / Result / 异常
│       ├── db/              # 引擎与 session
│       ├── models/          # 22 张表映射
│       ├── schemas/         # 出入参（CamelModel）
│       ├── services/        # 业务逻辑（权限闸门在此）
│       ├── api/             # 路由（login/admin 双 router）
│       └── agent/           # 智能体（graph/react/tools/tool_catalog/memory/observation_format）
└── vue/
    ├── package.json
    ├── vite.config.js       # /api、/uploads 代理到 8000
    └── src/
        ├── api/             # 每后端模块一个封装文件
        ├── components/      # 公共组件（ItineraryCard/StatusBadge/...）
        ├── router/          # 路由 + 角色互斥守卫
        ├── layout/          # AdminLayout / FrontLayout
        ├── styles/theme.css # 设计 token + Element Plus 映射
        └── views/           # admin 14 页 + front 11 页
```

## 部署步骤

1. **初始化数据库**：`mysql -u root -p < sql/system.sql`（可重复执行，幂等）。
   ⚠️ **该脚本会对 22 张表 `DROP TABLE`，是清空操作**，不要在已有数据的库上随手执行。
2. **后端**：
   ```bash
   cd fastapi
   python -m venv .venv && .venv/Scripts/activate   # Windows
   pip install -r requirements.txt
   cp .env.example .env        # 填 DB_PASSWORD
   dev.bat                     # 或 .venv/Scripts/python.exe -m uvicorn app.main:app --port 8000
   ```
   后端在 `http://localhost:8000`，`/docs` 为 OpenAPI。
3. **前端**：
   ```bash
   cd vue
   npm install
   npm run dev                 # http://localhost:5173（/api 代理到 8000）
   ```
4. 浏览器访问 `http://localhost:5173/login`。

> ⚠️ 前端必须连着后端跑，单独打开 `dist` 产物接口会全部 404。

## Docker Compose 部署（推荐）

```bash
docker compose up -d --build
```
- 前端 http://localhost:8080（nginx 同源反代 /api 到后端）
- 后端 http://localhost:8000
- 库名 `travel_assistant_docker`（compose 独立 mysql 卷，**绝不碰宿主机 travel_assistant**）

⚠️ 首次启动会在**容器内**执行 `sql/system.sql`（22 张表 DROP + CREATE + 种子），数据存于 `mysql_data` 卷。

## 部署要点

- **必须同源反代 `/api`**：静态部署时把 `/api` 反向代理到后端 8000，否则产物里所有接口 404（实测挂静态服务时 `/api/auth/captcha` 就是 404）。
- **必须配 SPA 回退**：`try_files $uri $uri/ /index.html`，否则刷新与深链接 404。
- **不要**为部署改 `baseURL` 或引入 `.env`，保持零配置。

## 默认账号

| 账号 | 密码 | 角色 |
|---|---|---|
| admin | admin | 管理员（管理后台） |
| aaa ~ ggg | 123 | 普通用户（用户前台，各绑定一名家人） |

> 均为 bcrypt 哈希存储，见 `sql/system.sql` 种子。

## FAQ

- **Q：智能助手没有大模型 Key 能用吗？** 能。默认走「规则编排」模式，真实调用工具并写库；填入 `LLM_API_KEY` 且 `AGENT_DEMO_MODE=false` 后走大模型 ReAct。
- **Q：攻略检索没命中怎么办？** 种子语料词表有限，属已知召回限制；助手会用更短关键词重试，未命中时如实告知。
- **Q：管理员能进用户前台吗？** 不能。角色互斥：ADMIN 访问 `/user/*` 会重定向 403，反之亦然。
- **Q：数据建表能不能用 `create_all`？** 不能。`sql/system.sql` 是唯一权威 schema（含唯一约束，防超卖依赖它们）。
- **Q：时间字段为什么不能写 `Optional[datetime]=None`？** 会显式写 NULL 进 NOT NULL 列导致 1048；统一用 `default_factory=datetime.now`。

## 后续可优化方向

| 方向 | 本期不做的原因 |
|---|---|
| 助手流式输出（SSE 逐字 + 步骤实时推送） | 需同时改接口与前端，优先保证功能完整 |
| LangGraph 原生 `interrupt` 替代自研待确认机制 | 当前实现已满足需求，原生断点可统一多步审批 |
| Agent 评测集（标准问句 → 期望工具链回归） | 需人工构造用例，可回答「改提示词后能力是否退化」 |
| 多智能体/子图（规划师与预订分工） | 11 工具 + 单一 ReAct 环已够用，拆分属过度设计 |
| 中文嵌入模型升级（多语种 embedding） | 会引入额外模型下载，破坏「开箱即用、无需 Key」 |
| 外部天气/地图服务 | 引入 API Key 与网络依赖 |
| 消息推送（微信/短信/邮件） | 站内消息已覆盖闭环，外部通道涉及资质与成本 |
