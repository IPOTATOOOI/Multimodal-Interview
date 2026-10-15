# Vue 前端

基于 Vue 3、TypeScript 和 Vite 的智能模拟面试前端。

```powershell
npm ci
npm run dev
```

前端从仓库根目录 `.env` 读取配置，通过 `VITE_API_BASE_URL` 选择 Python 或 Java 后端：

```dotenv
# 完整 AI 功能
VITE_API_BASE_URL=http://localhost:8000

# 或 Java 核心业务后端
# VITE_API_BASE_URL=http://localhost:8001
```

构建检查：

```powershell
npm run build
```

`npm run type-check` 是额外的严格类型检查。部分历史 WebGL 与文档编辑器组件尚有存量类型问题，但不阻断 Vite 生产构建。

完整环境配置和双后端启动说明请阅读[项目根 README](../README.md)。
