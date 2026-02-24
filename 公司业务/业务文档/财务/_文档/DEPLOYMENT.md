# 🚀 报销助手部署指南

本文档提供将报销助手部署到云端的完整指南。

## 📋 前置准备

### 环境变量清单

| 变量名         | 必需 | 说明                         | 示例                             |
| -------------- | ---- | ---------------------------- | -------------------------------- |
| `SECRET_KEY`   | ✅   | JWT 签名密钥                 | `openssl rand -hex 32` 生成      |
| `DATABASE_URL` | ❌   | PostgreSQL URL (默认 SQLite) | `postgresql://user:pass@host/db` |

---

## 🐳 本地 Docker 测试

```bash
# 1. 构建镜像
docker build -t reimbursement-agent .

# 2. 运行容器
docker run -p 8000:8000 \
  -e SECRET_KEY=$(openssl rand -hex 32) \
  reimbursement-agent

# 3. 访问 http://localhost:8000
```

---

## ☁️ Railway 部署 (推荐)

Railway 提供免费层，支持自动检测 Dockerfile。

### 步骤

1. **推送代码到 GitHub**

   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **连接 Railway**
   - 访问 [railway.app](https://railway.app)
   - 点击 "New Project" → "Deploy from GitHub Repo"
   - 选择你的仓库

3. **配置环境变量**
   - 在 Railway 项目设置中添加：
     - `SECRET_KEY`: 使用 `openssl rand -hex 32` 生成强随机字符串
     - `DATABASE_URL`: (可选) 如需 PostgreSQL，可在 Railway 中添加 Postgres 插件

4. **部署完成**
   - Railway 自动检测 `Dockerfile` 并构建
   - 部署成功后会提供公网 URL

---

## 🎨 Render 部署

### 步骤

1. 访问 [render.com](https://render.com) 创建新 Web Service
2. 连接 GitHub 仓库
3. 配置：
   - **Environment**: Docker
   - **Build Command**: (留空，使用 Dockerfile)
   - **Environment Variables**: 同上

---

## ✅ 生产环境检查清单

- [x] `SECRET_KEY` 从环境变量读取 (已实现)
- [x] `DATABASE_URL` 支持 PostgreSQL (已实现)
- [x] CORS 中间件已添加 (已实现)
- [ ] 配置速率限制 (Rate Limiting) - 可选
- [ ] 配置 HTTPS (Railway/Render 自动提供)
- [ ] 配置自定义域名

---

## 🔧 故障排除

### 常见问题

1. **端口绑定失败**
   - 确保 `PORT` 环境变量（Railway 自动设置）被正确使用
   - Dockerfile 已暴露 8000 端口

2. **数据库连接失败**
   - 检查 `DATABASE_URL` 格式是否正确
   - PostgreSQL URL 需以 `postgresql://` 开头（非 `postgres://`）

3. **OCR 识别失败**
   - Dockerfile 已安装 `tesseract-ocr` 和 `tesseract-ocr-chi-sim`
   - 如需其他语言包，修改 Dockerfile

---

## 📁 相关文件

- `Dockerfile` - 容器构建配置
- `railway.json` - Railway 特定配置
- `requirements.txt` - Python 依赖
