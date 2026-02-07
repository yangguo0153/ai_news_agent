# GitHub Actions 踩坑记录

## [2026-01-18] 子目录项目的 Workflow 不触发

- **现象**: Actions 页面空白，显示 "no workflows"
- **原因**: `.github/workflows/` 必须在仓库根目录，不能在子目录里
- **解决**:
  1. 把 `.github/` 移到仓库根
  2. 在 workflow 里用 `defaults.run.working-directory: ./子目录` 指定工作路径

## [2026-01-18] Secrets 配置后仍报错

- **现象**: `未设置 OPENAI_API_KEY`
- **原因**: Secret 的 **Name** 必须精确匹配代码中的环境变量名
- **解决**: 检查 Name 有无多余空格，Value 中不要包含 `KEY=` 前缀

## [2026-01-18] LiteLLM 导入失败

- **现象**: `ImportError: Missing dependency... fastapi`
- **原因**: litellm 新版有可选依赖未自动安装
- **解决**: 在 `pyproject.toml` 中显式添加 `fastapi>=0.100.0`
