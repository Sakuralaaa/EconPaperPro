# EconPaper Pro

📚 经管学术论文智能优化系统 - 面向青年学者的论文深度重构优化 Agent 系统

## 🎯 核心功能

1. **论文诊断** - 多维度分析论文质量（结构、逻辑、方法论、创新性、写作）
2. **深度优化** - 支持初稿重构、投稿优化、退修回应、终稿定稿四个阶段
3. **降重引擎** - 学术级文本改写，降低重复率
4. **降AI引擎** - 消除AI写作痕迹，使文本更具人类学者风格
5. **学术搜索** - 集成 Google Scholar 和 知网(CNKI) 搜索
6. **知识库** - 顶刊范例库、方法论知识库，支持 RAG 检索

## 🛠️ 技术特点

- **LLM调用**: 通过 OpenAI 兼容接口，支持任意兼容服务商（OpenAI、DeepSeek、硅基流动、Ollama等）
- **嵌入模型**: 通过 OpenAI 兼容接口调用
- **前端**: 使用 Gradio 构建本地 Web UI
- **向量库**: 使用 ChromaDB 本地存储
- **部署**: 纯本地运行，无需服务器，隐私安全

## 📦 安装

```bash
# 克隆项目
git clone https://github.com/your-username/econpaper-pro.git
cd econpaper-pro

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

## ⚙️ 配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的 API 配置
# 必须配置：LLM_API_BASE, LLM_API_KEY, LLM_MODEL
# 可选配置：EMBEDDING_* (嵌入模型), SERPAPI_KEY (学术搜索)
```

## 🚀 启动

```bash
python main.py
```

启动后在浏览器中打开 `http://127.0.0.1:7860` 即可使用。

## 📁 项目结构

```
econpaper-pro/
├── main.py                 # 主入口
├── requirements.txt        # 依赖
├── .env.example           # 环境变量模板
│
├── config/                # 配置模块
│   └── settings.py        # 配置管理（pydantic-settings）
│
├── core/                  # 核心模块
│   ├── llm.py             # LLM客户端（OpenAI兼容）
│   ├── embeddings.py      # 嵌入模型客户端
│   └── prompts.py         # 提示词模板库
│
├── agents/                # Agent模块
│   ├── master.py          # 主控Agent
│   ├── diagnostic.py      # 诊断Agent
│   ├── optimizer.py       # 优化Agent
│   └── revision.py        # 退修Agent
│
├── engines/               # 处理引擎
│   ├── dedup.py           # 降重引擎
│   ├── deai.py            # 降AI引擎
│   └── similarity.py      # 相似度检测
│
├── knowledge/             # 知识库
│   ├── vector_store.py    # 向量库管理
│   ├── exemplars.py       # 范例管理
│   └── search/            # 学术搜索
│
├── parsers/               # 文档解析
│   ├── pdf_parser.py      # PDF解析
│   ├── docx_parser.py     # Word解析
│   └── structure.py       # 论文结构识别
│
├── ui/                    # 用户界面
│   ├── app.py             # Gradio主应用
│   ├── components.py      # UI组件
│   └── styles.py          # CSS样式
│
└── data/                  # 数据目录
    ├── exemplars/         # 顶刊范例
    └── chroma_db/         # 向量数据库
```

## 📖 使用说明

### 1. 论文诊断
上传论文文件（PDF/Word）或粘贴内容，系统将从结构完整性、逻辑严密性、方法规范性、创新贡献、写作规范五个维度进行诊断分析。

### 2. 深度优化
根据论文阶段（初稿/投稿/退修/终稿）选择相应优化策略，系统针对不同部分（引言、文献综述、假设、实证等）进行专业优化。

### 3. 降重降AI
输入需要处理的文本，选择降重强度（1-5级），系统保留专业术语的同时进行学术级改写。降AI功能可消除AI写作痕迹。

### 4. 学术搜索
输入关键词，搜索 Google Scholar 或知网文献，获取相关论文信息。

### 5. 退修助手
粘贴审稿意见，系统自动解析并生成回应策略和回应信模板。

## ⚠️ 注意事项

- 所有论文内容仅在本地处理，不会上传到第三方服务（除了配置的LLM API）
- 请确保配置正确的 API 密钥
- 长文档会自动分段处理以避免超出 token 限制

## 📄 许可证

MIT License
