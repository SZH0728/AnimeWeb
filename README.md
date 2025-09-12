# AnimeWeb 动漫信息网站

⚠️ **重要声明：此项目已停止维护** ⚠️

这个版本的AnimeWeb项目已经停止维护，重构版本：[AnimeWebV2](https://github.com/SZH0728/AnimeWebV2)

---

一个用于展示和查询动漫信息的Web应用程序，包含前后端两部分。

## 项目结构

```
AnimeWeb/
├── backend/           # 后端服务
│   ├── routers/       # API路由
│   │   └── anime/     # 动漫相关API
│   ├── database.py    # 数据库模型和连接
│   ├── main.py        # 应用入口
│   └── config.ini     # 配置文件
└── frontend/          # 前端界面
    ├── src/           # 源代码
    │   ├── views/     # 页面组件
    │   ├── component/ # 公共组件
    │   └── router/    # 路由配置
    └── package.json   # 前端依赖配置
```

## 技术栈

### 后端 (Python)
- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速(高性能)的Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包和ORM
- [PyMySQL](https://pymysql.readthedocs.io/) - Python MySQL客户端库
- [MariaDB](https://mariadb.org/) - 关系型数据库

### 前端 (JavaScript)
- [Vue.js 3](https://v3.vuejs.org/) - 渐进式JavaScript框架
- [Vue Router](https://router.vuejs.org/) - Vue.js官方路由管理器
- [Bootstrap](https://getbootstrap.com/) - 响应式前端框架
- [Axios](https://axios-http.com/) - 基于Promise的HTTP客户端
- [Vite](https://vitejs.dev/) - 前端构建工具

## 功能特性

- 动漫列表展示与分页
- 按季度筛选动漫
- 动漫详情查看
- 动漫评分历史图表展示
- 关键词搜索功能
- 响应式设计，支持多设备访问

## 环境要求

### 后端
- Python 3.8+
- MariaDB/MySQL数据库
- pip包管理器

### 前端
- Node.js 14+
- npm包管理器

## 安装与配置

### 后端配置

1. 安装依赖包：
```bash
pip install fastapi uvicorn sqlalchemy pymysql mariadb
```

2. 配置数据库：
在 `backend/config.ini` 中修改数据库配置：
```ini
[database]
user = your_username
password = your_password
host = localhost
port = 3306
dbname = anime
```

3. 运行后端服务：
```bash
cd backend
python main.py
```

### 前端配置

1. 安装依赖：
```bash
cd frontend
npm install
```

2. 开发环境运行：
```bash
npm run dev
```

3. 构建生产版本：
```bash
npm run build
```

## API接口

所有API接口均以 `/anime` 为前缀：

- `GET /anime/list` - 获取动漫列表
- `GET /anime/season` - 按季度获取动漫列表
- `GET /anime/detail/{id}` - 获取动漫详情
- `GET /anime/score/{id}` - 获取动漫评分历史
- `GET /anime/webinfo` - 获取网站信息
- `GET /anime/search` - 搜索动漫

## 部署

### 后端部署
使用以下命令启动生产环境服务：
```bash
uvicorn main:app --host 0.0.0.0 --port 60000
```

或者使用Gunicorn等WSGI服务器进行部署。

### 前端部署
构建项目并部署生成的静态文件：
```bash
npm run build
```

将 `dist` 目录中的文件部署到Web服务器。
