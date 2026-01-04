# EconPaper Pro - Windows 打包指南

本文档说明如何将 EconPaper Pro 打包为 Windows 桌面应用程序。

## 📋 目录

- [本地打包](#本地打包)
- [GitHub 云端打包](#github-云端打包)
- [自定义目录功能](#自定义目录功能)
- [常见问题](#常见问题)

---

## 🖥️ 本地打包

### 前提条件

1. Python 3.10 或更高版本
2. 安装所有项目依赖
3. 安装 PyInstaller

### 步骤

```bash
# 1. 进入项目目录
cd econpaper-main

# 2. 安装依赖
pip install -r requirements.txt
pip install pyinstaller

# 3. 运行打包命令
pyinstaller econpaper.spec

# 4. 打包完成后，可执行文件位于 dist/EconPaperPro/ 目录
```

### 打包选项

#### 标准版（带控制台）
默认配置会生成带控制台窗口的版本，方便查看日志输出。

#### 无控制台版
编辑 `econpaper.spec` 文件，将 `console=True` 改为 `console=False`：

```python
exe = EXE(
    ...
    console=False,  # 隐藏控制台窗口
    ...
)
```

#### 单文件版（便携版）
```bash
pyinstaller --onefile --name EconPaperPro-Portable main.py
```

---

## ☁️ GitHub 云端打包

使用 GitHub Actions 自动构建 Windows 应用程序。

### 配置步骤

1. **创建 GitHub 仓库**
   
   将项目代码推送到 GitHub 仓库。

2. **工作流文件**
   
   确保 `.github/workflows/build-windows.yml` 文件存在。

3. **触发构建**

   有两种方式触发构建：

   **方式一：推送标签（推荐用于发布）**
   ```bash
   # 创建并推送标签
   git tag v1.0.0
   git push origin v1.0.0
   ```

   **方式二：手动触发**
   1. 进入 GitHub 仓库页面
   2. 点击 "Actions" 标签
   3. 选择 "Build Windows Application"
   4. 点击 "Run workflow"
   5. 输入版本号，点击 "Run workflow"

4. **下载构建产物**
   
   构建完成后，可以在以下位置找到产物：
   - **Actions 页面**: 点击具体的工作流运行记录，下载 Artifacts
   - **Releases 页面**: 如果是通过标签触发，会自动创建 Release

### 工作流说明

构建工作流会生成两种版本：

| 版本 | 说明 | 文件名 |
|------|------|--------|
| 标准版 | 完整目录结构，启动更快 | `EconPaperPro-vX.X.X-windows-x64.zip` |
| 便携版 | 单个 exe 文件，方便携带 | `EconPaperPro-Portable.exe` |

---

## 📁 自定义目录功能

打包后的应用支持用户自定义数据存储目录和工作区目录。

### 首次运行

首次运行应用时，会弹出设置向导：

1. **数据存储目录**: 用于存储向量数据库、日志、缓存等
2. **工作区目录**: 用于存储临时文件和输出文件

### 目录结构

```
数据存储目录/
├── chroma_db/     # 向量数据库
├── logs/          # 日志文件
└── cache/         # 缓存文件

工作区目录/
└── output/        # 输出文件
```

### 修改目录

运行后可以在应用设置中修改目录路径。配置保存在：
- Windows: `%APPDATA%\EconPaperPro\launcher_config.json`

### 配置文件格式

```json
{
  "data_dir": "D:\\MyData\\EconPaperPro",
  "workspace_dir": "D:\\Documents\\EconPaperPro",
  "setup_completed": true
}
```

---

## ❓ 常见问题

### Q1: 打包后应用无法启动

**可能原因**:
- 缺少必要的依赖模块
- Python 版本不兼容

**解决方案**:
1. 确保 `hiddenimports` 列表包含所有必要模块
2. 使用 Python 3.10 或 3.11 版本
3. 检查控制台错误信息

### Q2: 打包体积过大

**解决方案**:
1. 使用 UPX 压缩：
   ```bash
   pip install upx
   pyinstaller --upx-dir=/path/to/upx econpaper.spec
   ```

2. 排除不必要的模块，编辑 `econpaper.spec`:
   ```python
   excludes = [
       'matplotlib',
       'scipy',
       'numpy.testing',
       # 添加更多不需要的模块
   ]
   ```

### Q3: Gradio 界面无法加载

**可能原因**:
- 静态资源文件未正确打包

**解决方案**:
确保 Gradio 的静态文件被包含：
```python
from PyInstaller.utils.hooks import collect_data_files
datas += collect_data_files('gradio')
```

### Q4: ChromaDB 无法初始化

**可能原因**:
- 数据目录权限问题
- 路径包含特殊字符

**解决方案**:
1. 确保数据目录有读写权限
2. 避免在路径中使用中文或特殊字符

### Q5: 如何添加应用图标

1. 准备 `.ico` 格式的图标文件
2. 修改 `econpaper.spec`:
   ```python
   APP_ICON = 'assets/icon.ico'
   ```
3. 重新打包

---

## 🔧 高级配置

### 添加版本信息

创建 `version_info.txt`:

```python
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    ...
  ),
  ...
)
```

在 `econpaper.spec` 中引用：
```python
exe = EXE(
    ...
    version='version_info.txt',
    ...
)
```

### 代码签名

对于商业发布，建议对 exe 进行代码签名：

```bash
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com EconPaperPro.exe
```

---

## 📝 更新日志

### v1.0.0
- 初始版本
- 支持 PyInstaller 打包
- 支持 GitHub Actions 云端构建
- 支持自定义数据目录和工作区目录
