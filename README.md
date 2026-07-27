# AnimeWeb

AnimeWeb 是一个只读的番剧评分展示站点。它基于已采集并保存到 PostgreSQL 的 Bangumi 条目元数据和每日评分快照，提供季度浏览、作品搜索、榜单、条目详情及评分历史趋势。

> 页面数据来自本项目数据库中保存的抓取快照，并非实时数据。不同作品展示的评分、评价人数和综合排名可能对应不同的快照日期；AnimeWeb 与 Bangumi 没有官方隶属关系。
 
## 功能概览

- 浏览数据库已收录的季度番剧，按最新评分筛选和分页查看。
- 按原名、译名或别名搜索番剧。
- 浏览最高评分榜与最多人评价榜。
- 查看条目资料、最新评分、评价人数、Bangumi 综合排名和每日评分历史。
- 支持展示外链封面，或由后端提供内部封面资源。

## 技术栈

| 层级 | 技术 |
| --- | --- |
| 前端 | Vue 3、TypeScript、Vite、Vue Router |
| UI 与可视化 | Tailwind CSS、daisyUI、ECharts |
| 前端数据边界 | Zod |
| 后端 | FastAPI、Pydantic、Uvicorn |
| 数据访问 | SQLAlchemy Async、asyncpg |
| 数据库 | PostgreSQL |

## 架构

```text
Browser
  │
  ▼
Vue 3 SPA (frontend/)
  │  /api — Vite development proxy
  ▼
FastAPI (backend/, port 8000)
  │  async, read-only sessions
  ▼
PostgreSQL
  ├── subjects  # 条目静态元数据
  └── ratings   # 按日采集的评分快照
```

- 前端开发服务器会将 `/api` 请求代理到 `http://localhost:8000`。
- 后端在启动时装配路由、服务、缓存、日志和数据库资源。
- 数据库请求使用只读事务，并应用配置的 SQL 语句超时。
- 首页、季度和榜单首屏可使用进程内 TTL 缓存；该缓存不作为共享或持久化缓存。
- API JSON 使用 `snake_case` 字段；封面二进制资源独立于 JSON API 提供。

## 目录结构

```text
AnimeWeb/
├── backend/                # FastAPI 应用、服务层、数据访问和配置
│   ├── api/routers/        # REST API 路由
│   ├── core/               # 配置、日志和异常处理
│   ├── data/               # SQLAlchemy 异步数据库访问
│   └── requirements.txt    # Python 依赖
├── frontend/               # Vue 3 单页应用
│   ├── src/api/            # HTTP 客户端与 API 契约
│   ├── src/router/         # 前端路由
│   └── src/views/          # 页面视图
└── LICENSE                 # GNU GPL v3
```

## 前置条件

- Node.js `>= 20.19.0`
- npm
- Python `3.14.3`（项目虚拟环境位于 `.venv`）
- 可访问的 PostgreSQL 实例
- 已准备好与本项目数据模型兼容的 `subjects` 和 `ratings` 数据

项目只负责读取已有数据；仓库当前不提供数据库建表、迁移、爬取或数据导入命令。

## 本地开发

前端和后端需分别启动。请先完成后端配置并保证 PostgreSQL 中已有可查询的数据。

### 1. 配置后端

后端默认读取 `backend/config.ini`；也可以通过 `ANIMEWEB_CONFIG_PATH` 指向其他 INI 文件：

```bash
export ANIMEWEB_CONFIG_PATH="/path/to/config.ini"
```

配置文件需要包含以下段落：

| 配置段 | 用途 |
| --- | --- |
| `[database]` | PostgreSQL 异步 DSN、连接池、连接与语句超时 |
| `[cache]` | 首页、季度和榜单缓存开关与 TTL |
| `[home]` | 首页最新季度及榜单预览数量 |
| `[pagination]` | 默认页码、页大小和最大页大小 |
| `[images]` | 封面策略，例如 `internal` 或 `external` |
| `[app]` | 应用调试开关 |
| `[logging]` | 日志格式、目录、保留数量和第三方日志抑制设置 |

`[logging]` 中还必须提供 `info_backup_count` 和 `error_backup_count`。数据库 DSN 必须使用 SQLAlchemy/asyncpg 可识别的 PostgreSQL 异步连接格式，例如以 `postgresql+asyncpg://` 开头。

### 2. 启动后端

在仓库根目录创建/使用 Python 虚拟环境并安装依赖：

```bash
source "D:/poject/AnimeWeb/.venv/Scripts/activate"
pip install -r backend/requirements.txt
python -m uvicorn backend.main:create_app --factory --reload --port 8000
```

Windows Git Bash 中，每次执行 Python 命令时都应在同一命令行中激活虚拟环境。例如：

```bash
source "D:/poject/AnimeWeb/.venv/Scripts/activate" && python -m uvicorn backend.main:create_app --factory --reload --port 8000
```

后端启动后，本地交互式 API 文档位于 `http://localhost:8000/docs`。

### 3. 启动前端

在另一个终端中执行：

```bash
cd frontend
npm ci
npm run dev
```

Vite 默认通过 `/api` 将 API 请求代理到 `http://localhost:8000`。终端会输出前端访问地址。

## 前端环境变量

以下为 Vite 构建时环境变量，均可选。它们会进入前端产物，因此不能放置密钥。

| 变量 | 默认值 | 说明 |
| --- | ---: | --- |
| `VITE_API_BASE_URL` | `/api` | API 根路径；可为根路径或绝对 HTTP(S) URL |
| `VITE_DEFAULT_PAGE` | `1` | 默认页码，必须是正整数 |
| `VITE_DEFAULT_PAGE_SIZE` | `20` | 默认每页数量，范围为 `1`–`100` |
| `VITE_DEFAULT_MIN_TOTAL` | `0` | 默认最低评价人数，必须为非负整数 |

使用 Vite 开发服务器时建议保留 `VITE_API_BASE_URL=/api`，以启用开发代理。

## API 概览

所有 JSON API 均为只读 `GET` 接口，基础路径为 `/api`，日期字段使用 `YYYY-MM-DD`。分页接口使用 `page` 和 `page_size`，其中 `page` 从 `1` 开始，`page_size` 默认 `20`、最大 `100`。

| 接口 | 说明 |
| --- | --- |
| `GET /api/home` | 获取首页的最新季度、最高评分和最多人评价预览 |
| `GET /api/seasons` | 获取已收录季度 |
| `GET /api/subjects` | 获取季度目录；需要 `year`、`season`，可选 `min_total`、分页参数 |
| `GET /api/search` | 搜索原名、译名和别名；需要非空 `q`，可选分页参数 |
| `GET /api/rankings/top-score` | 最高评分榜；可选 `min_total` 和分页参数 |
| `GET /api/rankings/most-rated` | 最多人评价榜；可选分页参数 |
| `GET /api/subjects/{bgm_id}` | 获取单个 Bangumi 条目详情 |
| `GET /api/subjects/{bgm_id}/ratings` | 获取条目的日评分快照历史 |
| `GET /images/{bgm_id}` | 获取内部封面二进制资源（仅内部封面策略可用） |

- `bgm_id` 为正整数 Bangumi 条目 ID。
- `season` 仅接受 `winter`、`spring`、`summer`、`fall`。
- 所有最新评分均取每个条目自身日期最新的一条评分记录；不同条目的快照日期可能不同。
- 评分历史按日期升序返回，不会填补缺失日期或插值；不超过 30 条时完整返回，超过 30 条时按 `ceil(总记录数 / 30)` 间隔从最新快照反向采样，且始终包含最新快照。
- 条目不存在时返回 `404` 和 `SUBJECT_NOT_FOUND`；参数非法时返回 `400` 和 `INVALID_PARAMETER`。

错误响应格式：

```json
{
  "error": {
    "code": "SUBJECT_NOT_FOUND",
    "message": "未找到 bgm_id 为 12345 的条目"
  }
}
```

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。
