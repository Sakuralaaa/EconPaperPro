# 📚 EconPaper Pro

**经管学术论文智能优化系统** - 原生桌面应用，双击即用

> 版本：v0.4.2 | 更新日期：2026-01-05

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 **论文诊断** | 多维度评估论文质量，输出详细诊断报告 |
| ⚙️ **深度优化** | 按阶段、按部分智能优化论文内容 |
| 🔧 **降重降AI** | 智能降低查重率和AI检测率 |
| 🔎 **学术搜索** | Google Scholar / 知网文献检索 + AI智能筛选 |
| 📝 **退修助手** | 分析审稿意见，生成逐条回应策略 |
| 📊 **期刊级别** | CSSCI/北核/SSCI Q1-Q2 期刊筛选 |

---

## 🆕 最新更新 (v0.4.2)

- ✨ **首次使用引导** - 打开应用自动引导配置 API
- 📝 **实时字数统计** - 所有文本框显示字数/词数
- ℹ️ **关于页面** - 版本信息和帮助链接
- 🔒 **操作前检查** - 未配置 API 时友好提示
- 📁 **存储目录配置** - 自定义数据目录，避免占用 C 盘
- 🔑 **Google Scholar 认证** - 登录账号绕过搜索限制

---

## � 快速开始

### 方式一：下载运行（推荐）

1. 从 [Releases](../../releases) 下载 `EconPaperPro-Windows.zip`
2. 解压后双击 `EconPaperPro.exe` 运行
3. **首次使用会自动弹出引导窗口**，按提示配置 API 密钥

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

---

## ⚙️ 配置说明

应用支持多种 API 供应商，在「系统设置」页面可一键切换：

| 供应商 | API 地址 | 推荐模型 |
|--------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | gpt-4o-mini |
| DeepSeek | `https://api.deepseek.com/v1` | deepseek-chat |
| 硅基流动 | `https://api.siliconflow.cn/v1` | Qwen/Qwen2.5-72B-Instruct |
| Ollama 本地 | `http://localhost:11434/v1` | llama3.2 |

### 存储配置

可自定义数据存储位置，避免占用 C 盘空间：

| 配置项 | 说明 | 默认位置 |
|--------|------|----------|
| 数据目录 | 日志、缓存、向量库 | `~/.econpaper/` |
| 工作区目录 | 导出文件存放 | `~/Documents/EconPaper/` |

---

## 📁 项目结构

```
.
├── main.py          # 程序入口
├── ui/              # 界面模块（原生 tkinter）
│   └── native_app.py # 主应用窗口
├── agents/          # AI 智能体
├── engines/         # 处理引擎（降重、降AI）
├── parsers/         # 文档解析（PDF、Word）
├── knowledge/       # 知识库与学术搜索
│   └── search/      # Google Scholar、CNKI 爬虫
├── config/          # 配置管理（.env）
├── core/            # 核心功能
└── data/            # 示例数据
```

---

## 📋 系统要求

- Windows 10/11
- 无需 Python 环境（使用打包版本）
- 需要网络连接（调用 LLM API）
- 推荐：Chrome 浏览器（用于 Google 账号认证）

---

## 🐛 常见问题

**Q: 首次打开提示未配置 API？**
A: 点击「前往设置」，选择供应商并填写 API 密钥即可。

**Q: Google Scholar 搜索频繁失败？**
A: 点击「去认证」登录 Google 账号，可显著提高搜索成功率。

**Q: 占用 C 盘空间太大？**
A: 在设置页面配置「数据目录」到其他盘符。

---

## 📄 许可证

MIT License

