## 后端文件架构

- `main.py`: 程序的入口
- `dependencies.py`: 定义所有的依赖项
- `database.py`: 定义数据库模型与连接方式
- `router`: 定义所有的路由
    - `router`中子模块架构：
        - `crud.py`: 定义所有的数据库操作 
        - `router.py`: 定义有关的路由操作
        - `schemas.py`: 定义所有的数据模型
    - `anime`模块: 定义动漫查询有关的路由
