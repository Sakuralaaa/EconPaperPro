# EconPaper Pro 综合优化计划 v2.5 (已完成)

## 📋 优化项目总览

| 优先级 | 优化类别 | 优化项 | 状态 | 影响范围 |
|--------|----------|--------|------|----------|
| **P0** | 核心体验 | 流式输出支持 | ✅ 已完成 | LLM交互 |
| **P0** | 核心体验 | 精确进度显示 | ✅ 已完成 | 所有任务页面 |
| **P0** | 核心体验 | 智能重试机制 | ✅ 已完成 | API调用 |
| **P0** | 核心体验 | 学术搜索页DualOutputFrame | ✅ 已完成 | 搜索页面 |
| **P1** | 交互增强 | 差异对比高亮 | ✅ 已完成 | 降重/降AI页面 |
| **P1** | 交互增强 | 输入验证与警告 | ✅ 已完成 | 所有输入框 |
| **P1** | 交互增强 | 快捷键可视化提示 | ✅ 已完成 | 全局 |
| **P2** | 数据管理 | 历史记录与撤销 | ✅ 已完成 | 全局 |
| **P2** | 数据管理 | 用户偏好设置 | ✅ 已完成 | 设置页面 |
| **P2** | 数据管理 | API用量统计 | ✅ 已完成 | 设置页面 |
| **P3** | 高级功能 | 深色主题 | ✅ 已完成 | 全局UI |
| **P3** | 高级功能 | 预设模板 | ✅ 已完成 | 退修页面 |
| **P3** | 高级功能 | 批量处理 | ✅ 已完成 | 所有处理页面 |
| **P3** | 高级功能 | Word导出 | ✅ 已完成 | 导出功能 |
| **P3** | 高级功能 | AI模型切换 | ✅ 已完成 | 设置页面 |

---

## 🚀 P0 - 核心体验优化

### 1. 流式输出支持

**问题**：当前 LLM 返回完整结果后才显示，长任务时用户体验差。

**实现方案**：

```python
# 新增组件: StreamingTextOutput
class StreamingTextOutput(tk.Frame):
    """支持流式更新的文本输出框"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent)
        self.text = scrolledtext.ScrolledText(...)
        self._streaming = False
        self._buffer = []
    
    def start_streaming(self):
        """开始流式接收"""
        self.clear()
        self._streaming = True
    
    def append_chunk(self, chunk: str):
        """追加文本块"""
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, chunk)
        self.text.see(tk.END)  # 自动滚动
        self.text.config(state=tk.DISABLED)
    
    def end_streaming(self):
        """结束流式接收"""
        self._streaming = False
```

**修改文件**：
- `ui/components.py`: 新增 `StreamingTextOutput` 组件
- `core/llm.py`: 优化 `invoke_stream()` 方法
- `ui/native_app.py`: 任务回调使用流式输出

**架构图**：

```
用户触发任务
     │
     ▼
TaskManager.submit()
     │
     ▼
LLM.invoke_stream() ──┐
     │                │
     ▼                │
for chunk in stream:  │
     │                │
     ├── UI更新队列 ◄─┘
     │
     ▼
StreamingTextOutput.append_chunk()
     │
     ▼
用户实时看到内容
```

---

### 2. 精确进度显示

**问题**：只有脉冲动画，用户不知道实际进度。

**实现方案**：

```python
# 增强进度组件
class PreciseProgressBar(tk.Frame):
    """精确进度条组件"""
    
    def __init__(self, parent):
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            self,
            variable=self.progress_var,
            maximum=100
        )
        
        # 进度详情
        self.detail_label = tk.Label(...)  # "处理第 3/10 句..."
        self.eta_label = tk.Label(...)      # "预计剩余: 45秒"
        self.speed_label = tk.Label(...)    # "速度: 2.3句/秒"
    
    def update_progress(
        self, 
        current: int, 
        total: int,
        message: str = ""
    ):
        """更新进度"""
        percent = (current / total) * 100
        self.progress_var.set(percent)
        self.detail_label.config(text=f"处理第 {current}/{total} 项")
        
        # 计算ETA
        if hasattr(self, '_start_time'):
            elapsed = time.time() - self._start_time
            speed = current / elapsed if elapsed > 0 else 0
            remaining = (total - current) / speed if speed > 0 else 0
            self.eta_label.config(text=f"预计剩余: {int(remaining)}秒")
```

**效果示例**：
```
[████████████░░░░░░░░] 60%
处理第 6/10 句... | 预计剩余: 12秒 | 速度: 1.8句/秒
```

---

### 3. 智能重试机制

**问题**：API 失败直接报错，用户需要手动重试。

**实现方案**：

```python
# core/retry.py - 新建重试模块
import time
from functools import wraps
from typing import Callable, Optional

class RetryConfig:
    """重试配置"""
    MAX_RETRIES = 3
    INITIAL_DELAY = 1.0  # 秒
    BACKOFF_FACTOR = 2.0
    RETRYABLE_ERRORS = (
        ConnectionError,
        TimeoutError,
        # OpenAI 特定错误
    )

def with_retry(
    max_retries: int = RetryConfig.MAX_RETRIES,
    on_retry: Optional[Callable] = None
):
    """重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = RetryConfig.INITIAL_DELAY
            last_error = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RetryConfig.RETRYABLE_ERRORS as e:
                    last_error = e
                    if attempt < max_retries:
                        if on_retry:
                            on_retry(attempt + 1, max_retries, str(e))
                        time.sleep(delay)
                        delay *= RetryConfig.BACKOFF_FACTOR
                    else:
                        raise
            
            raise last_error
        return wrapper
    return decorator
```

**使用方式**：

```python
# 在 LLM 调用中应用
@with_retry(
    max_retries=3,
    on_retry=lambda a, m, e: notify(f"重试 {a}/{m}...")
)
def invoke(self, prompt: str, **kwargs):
    return self.client.chat.completions.create(...)
```

---

### 4. 学术搜索页应用 DualOutputFrame

**问题**：搜索页仍使用单一文本框，与其他页面不一致。

**修改位置**：`ui/native_app.py` 的 `_create_search_page()` 方法

**改动**：
```python
# 将 self.search_result 替换为 DualOutputFrame
self.search_dual_output = DualOutputFrame(
    right_panel,
    height=15,
    show_actions=True,
    on_send_to=lambda t, c: self.workflow.send_to_page(t, c, "search")
)
self.search_dual_output.pack(fill=tk.BOTH, expand=True)

# 添加流转按钮
self.search_dual_output.add_flow_button("引用到论文", "optimize", "📖")
```

---

## 🎨 P1 - 交互增强

### 5. 差异对比高亮

**问题**：降重/降AI 结果难以看出具体修改点。

**实现方案**：

```python
# 新增组件: DiffViewFrame
class DiffViewFrame(tk.Frame):
    """差异对比视图组件"""
    
    def __init__(self, parent):
        # 左侧：原文
        self.left_panel = tk.Frame(...)
        self.left_text = scrolledtext.ScrolledText(...)
        
        # 右侧：改后
        self.right_panel = tk.Frame(...)
        self.right_text = scrolledtext.ScrolledText(...)
        
        # 配置高亮标签
        self.left_text.tag_configure("deleted", background="#FECACA", overstrike=True)
        self.right_text.tag_configure("added", background="#BBF7D0")
    
    def set_diff(self, original: str, modified: str):
        """设置差异内容"""
        import difflib
        
        # 计算差异
        differ = difflib.Differ()
        diff = list(differ.compare(
            original.split(), 
            modified.split()
        ))
        
        # 渲染左侧（原文+删除标记）
        for item in diff:
            if item.startswith('- '):
                self.left_text.insert(tk.END, item[2:] + " ", "deleted")
            elif item.startswith('  '):
                self.left_text.insert(tk.END, item[2:] + " ")
        
        # 渲染右侧（改后+新增标记）
        for item in diff:
            if item.startswith('+ '):
                self.right_text.insert(tk.END, item[2:] + " ", "added")
            elif item.startswith('  '):
                self.right_text.insert(tk.END, item[2:] + " ")
```

**效果示意**：
```
┌─────────────────────┐ ┌─────────────────────┐
│ 原文                │ │ 改后                │
├─────────────────────┤ ├─────────────────────┤
│ 本文研究了...       │ │ 本研究探讨了...     │
│ ~~~~表明~~~~        │ │ [揭示]              │
│ ~~~~首先~~~~        │ │ [从一个角度来看]    │
└─────────────────────┘ └─────────────────────┘
```

---

### 6. 输入验证与警告

**实现方案**：

```python
# 增强 TextInputWithCount 组件
class TextInputWithCount(tk.Frame):
    def __init__(
        self, 
        parent, 
        max_chars: int = 50000,  # 字符限制
        warn_threshold: float = 0.8,  # 80%时警告
        **kwargs
    ):
        self.max_chars = max_chars
        self.warn_threshold = warn_threshold
        # ...
        
        self.warning_label = tk.Label(
            self,
            text="",
            fg=ModernStyle.WARNING,
            font=(ModernStyle.FONT_FAMILY, ModernStyle.FONT_SIZE_XS)
        )
    
    def _update_count(self, event=None):
        """更新字数统计和警告"""
        content = self.get_content()
        char_count = len(content)
        
        # 字数统计
        self.count_label.config(text=f"字数: {char_count}")
        
        # 警告检查
        ratio = char_count / self.max_chars
        if ratio >= 1.0:
            self.warning_label.config(
                text=f"⚠️ 超出限制 ({char_count}/{self.max_chars})，可能导致处理失败",
                fg=ModernStyle.ERROR
            )
            self.border_frame.config(bg=ModernStyle.ERROR)
        elif ratio >= self.warn_threshold:
            self.warning_label.config(
                text=f"⚡ 接近限制 ({char_count}/{self.max_chars})，建议分段处理",
                fg=ModernStyle.WARNING
            )
            self.border_frame.config(bg=ModernStyle.WARNING)
        else:
            self.warning_label.config(text="")
            self.border_frame.config(bg=ModernStyle.BORDER)
```

---

### 7. 快捷键可视化提示

**实现方案**：

```python
# 新增快捷键提示面板
class ShortcutsPanel:
    """快捷键提示浮层"""
    
    SHORTCUTS = [
        ("Ctrl+1~5", "切换页面"),
        ("Ctrl+S", "保存设置"),
        ("Ctrl+,", "打开设置"),
        ("Escape", "取消任务"),
        ("F1", "查看帮助"),
    ]
    
    def __init__(self, parent):
        self.parent = parent
        self.panel = None
    
    def show(self):
        """显示快捷键面板"""
        if self.panel:
            return
        
        self.panel = tk.Toplevel(self.parent)
        self.panel.wm_overrideredirect(True)
        self.panel.attributes("-topmost", True)
        
        # 居中显示
        x = self.parent.winfo_x() + self.parent.winfo_width() // 2 - 150
        y = self.parent.winfo_y() + self.parent.winfo_height() // 2 - 100
        self.panel.geometry(f"300x200+{x}+{y}")
        
        # 渲染快捷键列表
        for key, desc in self.SHORTCUTS:
            row = tk.Frame(self.panel)
            tk.Label(row, text=key, font=("Consolas", 11, "bold")).pack(side=tk.LEFT)
            tk.Label(row, text=desc).pack(side=tk.RIGHT)
            row.pack(fill=tk.X, padx=10, pady=5)
```

---

## 📁 P2 - 数据管理

### 8. 历史记录与撤销

**实现方案**：

```python
# 新建 core/history.py
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class HistoryEntry:
    """历史记录条目"""
    id: str
    timestamp: str
    action: str  # diagnose, optimize, dedup, deai, revision
    input_preview: str  # 前100字符
    output_preview: str
    input_full: str
    output_full: str
    metadata: dict = None

class HistoryManager:
    """历史记录管理器"""
    
    MAX_ENTRIES = 50
    HISTORY_FILE = Path.home() / ".econpaper" / "history.json"
    
    def __init__(self):
        self.entries: List[HistoryEntry] = []
        self._load()
    
    def add(self, action: str, input_text: str, output_text: str, metadata: dict = None):
        """添加历史记录"""
        entry = HistoryEntry(
            id=f"{action}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            action=action,
            input_preview=input_text[:100],
            output_preview=output_text[:100],
            input_full=input_text,
            output_full=output_text,
            metadata=metadata
        )
        
        self.entries.insert(0, entry)
        self.entries = self.entries[:self.MAX_ENTRIES]
        self._save()
    
    def get_recent(self, n: int = 10, action: str = None) -> List[HistoryEntry]:
        """获取最近记录"""
        if action:
            filtered = [e for e in self.entries if e.action == action]
            return filtered[:n]
        return self.entries[:n]
    
    def restore(self, entry_id: str) -> Optional[HistoryEntry]:
        """恢复指定记录"""
        for entry in self.entries:
            if entry.id == entry_id:
                return entry
        return None
    
    def _load(self):
        """从文件加载"""
        if self.HISTORY_FILE.exists():
            with open(self.HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entries = [HistoryEntry(**e) for e in data]
    
    def _save(self):
        """保存到文件"""
        self.HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump([asdict(e) for e in self.entries], f, ensure_ascii=False, indent=2)
```

**UI 集成**：
```python
# 在各页面添加历史记录按钮
history_btn = ModernButton(
    toolbar,
    text="📜 历史记录",
    command=self._show_history_panel,
    tooltip="查看处理历史"
)
```

---

### 9. 用户偏好设置

**实现方案**：

```python
# 新建 config/preferences.py
@dataclass
class UserPreferences:
    """用户偏好配置"""
    
    # 界面设置
    theme: str = "light"  # light, dark
    font_size: int = 12
    sidebar_collapsed: bool = False
    
    # 处理设置
    default_dedup_strength: int = 3
    auto_save_history: bool = True
    show_progress_details: bool = True
    
    # API 设置
    default_model: str = ""
    timeout_seconds: int = 60
    max_retries: int = 3
    
    # 导出设置
    default_export_format: str = "md"  # md, txt, docx
    
    @classmethod
    def load(cls) -> "UserPreferences":
        """加载偏好设置"""
        prefs_file = Path.home() / ".econpaper" / "preferences.json"
        if prefs_file.exists():
            with open(prefs_file, 'r') as f:
                return cls(**json.load(f))
        return cls()
    
    def save(self):
        """保存偏好设置"""
        prefs_file = Path.home() / ".econpaper" / "preferences.json"
        prefs_file.parent.mkdir(parents=True, exist_ok=True)
        with open(prefs_file, 'w') as f:
            json.dump(asdict(self), f, indent=2)
```

---

### 10. API 用量统计

**实现方案**：

```python
# 新建 core/usage.py
@dataclass
class UsageStats:
    """API 用量统计"""
    
    total_calls: int = 0
    total_tokens: int = 0
    total_input_chars: int = 0
    total_output_chars: int = 0
    calls_by_action: Dict[str, int] = field(default_factory=dict)
    daily_stats: Dict[str, dict] = field(default_factory=dict)
    
    def record(self, action: str, input_chars: int, output_chars: int, tokens: int = 0):
        """记录一次调用"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        self.total_calls += 1
        self.total_tokens += tokens
        self.total_input_chars += input_chars
        self.total_output_chars += output_chars
        
        self.calls_by_action[action] = self.calls_by_action.get(action, 0) + 1
        
        if today not in self.daily_stats:
            self.daily_stats[today] = {"calls": 0, "tokens": 0}
        self.daily_stats[today]["calls"] += 1
        self.daily_stats[today]["tokens"] += tokens
```

---

## 🎯 P3 - 高级功能

### 11. 深色主题

```python
# 扩展 ModernStyle 类
class DarkStyle(ModernStyle):
    """深色主题"""
    
    # 覆盖颜色定义
    BG_MAIN = "#1E1E1E"
    BG_SECONDARY = "#2D2D2D"
    BG_SIDEBAR = "#252526"
    BG_CARD = "#2D2D2D"
    BG_HOVER = "#3E3E3E"
    BG_INPUT = "#1E1E1E"
    
    TEXT_PRIMARY = "#E0E0E0"
    TEXT_SECONDARY = "#A0A0A0"
    TEXT_MUTED = "#6B6B6B"
    
    BORDER = "#404040"
    
    PRIMARY = "#4FC3F7"
    PRIMARY_LIGHT = "#263238"

# 主题切换方法
def switch_theme(theme: str):
    """切换主题"""
    if theme == "dark":
        style_class = DarkStyle
    else:
        style_class = ModernStyle
    
    # 重新配置所有样式
    style_class.configure_styles(root)
    
    # 递归更新所有组件颜色
    update_widget_colors(root, style_class)
```

---

### 12. 预设模板

```python
# 新建 data/templates.py
REVISION_TEMPLATES = {
    "general_response": """
感谢审稿人的宝贵意见。针对您提出的问题，我们做出如下回应：

{response_content}

我们已根据建议对论文进行了修改，相关改动见论文第{page_number}页。
""",
    
    "data_clarification": """
感谢审稿人对数据问题的关注。

关于数据来源：{data_source}
样本期间：{sample_period}
样本量：{sample_size}

我们已在论文中补充了详细说明。
""",
    
    "methodology_defense": """
感谢审稿人对研究方法的质疑。

我们选择{method_name}方法的原因如下：
1. {reason_1}
2. {reason_2}

同时，我们进行了{robustness_test}作为稳健性检验，结果表明...
"""
}
```

---

### 13-16. 其他高级功能

- **批量处理**：支持多文件上传，队列处理
- **Word导出**：使用 python-docx 库导出标准格式
- **AI模型切换**：设置页面添加模型选择下拉框
- **智能分段**：使用正则识别章节标题

---

## 📐 系统架构更新

```
┌─────────────────────────────────────────────────────────────┐
│                     EconPaper Pro v2.5                      │
├─────────────────────────────────────────────────────────────┤
│  UI Layer (ui/)                                             │
│  ├── native_app.py      # 主应用                           │
│  ├── components.py      # 公共组件                         │
│  │   ├── StreamingTextOutput   [NEW]                       │
│  │   ├── PreciseProgressBar    [NEW]                       │
│  │   ├── DiffViewFrame         [NEW]                       │
│  │   ├── ShortcutsPanel        [NEW]                       │
│  │   └── DualOutputFrame       [EXISTING]                  │
│  └── themes.py          # 主题管理 [NEW]                    │
├─────────────────────────────────────────────────────────────┤
│  Core Layer (core/)                                         │
│  ├── llm.py             # LLM 客户端                       │
│  ├── retry.py           # 重试机制 [NEW]                    │
│  ├── history.py         # 历史管理 [NEW]                    │
│  └── usage.py           # 用量统计 [NEW]                    │
├─────────────────────────────────────────────────────────────┤
│  Config Layer (config/)                                     │
│  ├── settings.py        # 应用配置                         │
│  ├── preferences.py     # 用户偏好 [NEW]                    │
│  └── templates.py       # 预设模板 [NEW]                    │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (data/)                                         │
│  ├── ~/.econpaper/                                          │
│  │   ├── history.json   # 处理历史                         │
│  │   ├── preferences.json # 用户偏好                       │
│  │   └── usage.json     # 用量统计                         │
│  └── templates/         # 预设模板                         │
└─────────────────────────────────────────────────────────────┘
```

---

## ⏱️ 实施时间线

### 第一阶段：P0 核心体验（建议首先实施）
1. 流式输出支持
2. 精确进度显示
3. 智能重试机制
4. 搜索页 DualOutputFrame

### 第二阶段：P1 交互增强
5. 差异对比高亮
6. 输入验证
7. 快捷键提示

### 第三阶段：P2 数据管理
8. 历史记录
9. 用户偏好
10. API统计

### 第四阶段：P3 高级功能
11-16. 按需实施

---

## ✅ 优化总结 (2026-01-08)

EconPaper Pro 已成功从单一脚本架构转型为**专业级多线程桌面应用**。

### 核心技术突破：
1. **异步流式架构**：通过 `StreamingTextOutput` 和 `root.after` 循环，实现了 AI 内容的逐字实时渲染，彻底解决了 UI 卡顿问题。
2. **双重输出系统**：`DualOutputFrame` 实现了“结果内容”与“分析报告”的物理分离，极大提升了学术生产力。
3. **智能工作流**：`WorkflowConnector` 允许数据在诊断、优化、降重、搜索、退修五个模块间无缝流转，支持“作为背景参考”等高级逻辑。
4. **工业级稳定性**：引入 `TaskManager` 线程池管理、SQLite 历史持久化、以及基于指数退避算法的智能重试机制。
5. **细节交互**：支持深色模式、批量文件处理、Word 导出、快捷键绑定及实时字数统计。

*计划完成时间：2026-01-08*
*版本：v2.5 最终优化版*