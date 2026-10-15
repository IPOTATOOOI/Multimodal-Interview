# AI 智能模拟面试系统

一个面向求职训练的前后端分离项目，涵盖账号、简历解析、智能问答、语音转写、面试评估、笔试、知识图谱和历史记录等功能。

本仓库同时保留了两套可独立启动的后端实现，同一前端可对不同技术栈进行适配：

| 后端 | 默认端口 | 适用范围 |
| --- | ---: | --- |
| Python / FastAPI | `8000` | 完整 AI 面试流程、简历与语音处理、RAG/知识图谱、管理接口 |
| Java / Spring Boot | `8001` | 账号、用户资料、题库、历史记录等核心业务接口 |

前端通过根目录 `.env` 中的 `VITE_API_BASE_URL` 切换后端。

## 技术栈

- 前端：Vue 3、TypeScript、Vite、Pinia、Vue Router、Element Plus、Tailwind CSS
- Python 后端：FastAPI、MySQL、Neo4j、Redis、RabbitMQ、ChromaDB、LangChain
- Java 后端：Java 21、Spring Boot、MyBatis/JPA、MySQL、Neo4j、Redis、JWT
- AI 与媒体：OpenAI 兼容接口、通义千问、智谱、讯飞、Whisper、OpenCV（均按需配置）

## 目录结构

```text
.
├─ frontend/                 # Vue 3 前端
├─ backend-py/               # Python / FastAPI 后端
│  ├─ app/                   # API、业务服务与数据访问
│  ├─ schema.sql             # 仅数据库结构，不含历史业务数据
│  └─ prepare.sql            # 可选的公共题库/岗位基础数据
├─ backend-java/             # Java / Spring Boot 后端
├─ .env.example              # 配置模板
└─ LICENSE
```

## 环境要求

- Node.js 22+ 与 npm
- Python 3.10 或 3.11
- Java 21
- MySQL 8+
- 按所用功能准备 Neo4j 5+、Redis、RabbitMQ


## 环境配置

1. 复制配置模板：

   ```powershell
   Copy-Item .env.example .env
   ```

2. 修改 `.env`，至少填写数据库密码以及 `SECRET_KEY`、`JWT_SECRET`。真实密钥不得提交。
3. 根据需要填写 Qwen、OpenAI、智谱或讯飞等第三方服务配置。


## 初始化数据库

先创建数据库，再导入结构：

```sql
CREATE DATABASE swcup CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

```powershell
mysql -u root -p swcup < backend-py/schema.sql
```

如需公共岗位、术语和题型基础数据，可继续导入：

```powershell
mysql -u root -p swcup < backend-py/prepare.sql
```

`schema.sql` 不包含用户、简历、面试记录等历史业务数据；`prepare.sql` 只用于初始化公开的参考数据。

## 启动前端

```powershell
Set-Location frontend
npm ci
npm run dev
```

默认访问 `http://localhost:5173`。

## 启动 Python 后端

在根目录 `.env` 中设置：

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

然后执行：

```powershell
Set-Location backend-py
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

接口文档位于 `http://localhost:8000/docs`。首次使用嵌入模型时可能会从模型仓库下载文件；也可以通过 `EMBEDDING_MODEL_PATH` 指向本地模型。

## 启动 Java 后端

在根目录 `.env` 中设置：

```dotenv
VITE_API_BASE_URL=http://localhost:8001
```

然后执行：

```powershell
Set-Location backend-java
.\mvnw.cmd spring-boot:run
```

接口文档位于 `http://localhost:8001/swagger-ui.html`。Linux/macOS 使用 `./mvnw spring-boot:run`。

## 构建与检查

```powershell
# 前端
Set-Location frontend
npm run build

# Java
Set-Location ..\backend-java
.\mvnw.cmd test
.\mvnw.cmd package -DskipTests

# Python 语法检查
Set-Location ..\backend-py
python -m compileall app
```


本项目采用 [MIT License](LICENSE)。
