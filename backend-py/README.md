# Python / FastAPI 后端

这是项目功能覆盖最完整的后端实现，默认运行于 `8000` 端口，包含智能面试、简历处理、语音转写、评估、题库、RAG/知识图谱及管理接口。

## 启动

配置统一读取仓库根目录 `.env`（模板见 `../.env.example`）：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

- API 文档：`http://localhost:8000/docs`
- 数据库结构：`schema.sql`
- 可选公共初始化数据：`prepare.sql`
- 额外开发/可视化依赖：`requirements-tools.txt`

大型模型、上传文件、日志、音视频和向量库都是运行时资源，不在仓库中分发。完整配置、数据库初始化和安全说明请阅读[项目根 README](../README.md)。
