# 📚 EconPaper Pro

**经管学术论文智能优化系统** - 原生桌面应用，双击即用

---

## ✨ 核心功能

| 功能 | 说明 |
|------|------|
| 🔍 **论文诊断** | 多维度评估论文质量，输出详细诊断报告 |
| ⚙️ **深度优化** | 按阶段、按部分智能优化论文内容 |
| 🔧 **降重降AI** | 智能降低查重率和AI检测率 |
| 🔎 **学术搜索** | Google Scholar / 知网文献检索 |
| 📝 **退修助手** | 分析审稿意见，生成回应策略 |

---

## 🚀 快速开始

### 方式一：下载运行（推荐）

1. 从 [Releases](../../releases) 下载 `EconPaperPro-Windows.zip`
2. 解压后双击 `EconPaperPro.exe` 运行
3. 首次使用在「系统设置」中配置 API 密钥

### 方式二：源码运行

```bash
# 安装依赖
pip install -r requirements.txt

# 运行应用
python main.py
```

---

## ⚙️ 配置说明

在「系统设置」页面配置以下参数：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| LLM API Base | API 服务地址 | `https://api.openai.com/v1` |
| LLM API Key | API 密钥 | `sk-xxx...` |
| LLM Model | 模型名称 | `gpt-4` |

支持任何兼容 OpenAI 格式的 API。

---

## 📁 项目结构

```
.
├── main.py          # 程序入口
├── ui/              # 界面模块（原生 tkinter）
├── agents/          # AI 智能体
├── engines/         # 处理引擎（降重、降AI）
├── parsers/         # 文档解析（PDF、Word）
├── knowledge/       # 知识库与学术搜索
├── config/          # 配置管理
├── core/            # 核心功能
└── data/            # 示例数据
```

---

## 📋 系统要求

- Windows 10/11
- 无需 Python 环境（使用打包版本）
- 需要网络连接（调用 LLM API）

---

## 📄 许可证

MIT License

