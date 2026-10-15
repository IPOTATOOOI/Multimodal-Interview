# Java / Spring Boot 后端

这是项目的 Java 21 / Spring Boot 实现，默认运行于 `8001` 端口，主要提供账号、用户资料、题库和面试历史等核心业务接口。

## 启动

配置统一读取仓库根目录 `.env`（模板见 `../.env.example`）：

```powershell
.\mvnw.cmd spring-boot:run
```

Linux/macOS：

```bash
./mvnw spring-boot:run
```

API 文档位于 `http://localhost:8001/swagger-ui.html`。完整配置、数据库初始化、前端切换方式和安全说明请阅读[项目根 README](../README.md)。
