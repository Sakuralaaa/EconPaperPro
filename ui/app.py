# -*- coding: utf-8 -*-
"""
Gradio 主应用模块
创建完整的 Web UI 应用
"""

import gradio as gr
from typing import Optional, Tuple
from ui.styles import CUSTOM_CSS
from ui.components import (
    create_score_display,
    create_diff_display,
    create_diagnosis_card,
    create_processing_status,
    create_search_result_card
)


def create_app() -> gr.Blocks:
    """
    创建 Gradio 应用
    
    Returns:
        gr.Blocks: Gradio 应用实例
    """
    
    # ==================== 回调函数 ====================
    
    def diagnose_paper(file, text_content):
        """诊断论文"""
        try:
            from agents.master import MasterAgent
            
            agent = MasterAgent()
            
            # 获取内容
            if file is not None:
                # Validate file type
                file_name = file.name.lower()
                if file_name.endswith(".pdf"):
                    file_type = "pdf"
                elif file_name.endswith(".docx"):
                    file_type = "docx"
                else:
                    return "不支持的文件格式，请上传 PDF 或 Word 文档", ""
                
                with open(file.name, "rb") as f:
                    content = f.read()
                
                # 检查文件是否为空
                if len(content) == 0:
                    return "上传的文件为空，请检查文件内容", ""
                
                report = agent.diagnose_only(content, file_type=file_type)
            elif text_content:
                # 检查文本内容是否太短
                text_content = text_content.strip()
                if len(text_content) < 100:
                    return "论文内容过短，请粘贴完整的论文内容（至少100字）", ""
                
                report = agent.diagnose_only(text_content)
            else:
                return "请上传文件或粘贴论文内容", ""
            
            # 格式化诊断结果
            from agents.diagnostic import DiagnosticAgent
            diagnostic = DiagnosticAgent()
            formatted = diagnostic.format_report(report)
            
            # 创建评分展示
            scores = {
                result.dimension: result.score 
                for result in report.dimensions.values()
            }
            score_html = create_score_display(scores, report.overall_score)
            
            return formatted, score_html
            
        except ValueError as e:
            return f"配置错误: {str(e)}", ""
        except Exception as e:
            return f"诊断失败: {str(e)}", ""
    
    def optimize_paper(file, text_content, stage, target_journal, sections):
        """优化论文"""
        try:
            from agents.master import MasterAgent
            
            agent = MasterAgent()
            
            # 获取内容
            if file is not None:
                # Validate file type
                file_name = file.name.lower()
                if file_name.endswith(".pdf"):
                    file_type = "pdf"
                elif file_name.endswith(".docx"):
                    file_type = "docx"
                else:
                    return "不支持的文件格式，请上传 PDF 或 Word 文档", ""
                
                with open(file.name, "rb") as f:
                    content = f.read()
                
                # 检查文件是否为空
                if len(content) == 0:
                    return "上传的文件为空，请检查文件内容", ""
            elif text_content:
                content = text_content.strip()
                file_type = None
                
                # 检查文本内容是否太短
                if len(content) < 100:
                    return "论文内容过短，请粘贴完整的论文内容（至少100字）", ""
            else:
                return "请上传文件或粘贴论文内容", ""
            
            # 处理选择的部分
            section_list = list(sections) if sections else None
            
            # 验证至少选择了一个部分
            if not section_list:
                return "请至少选择一个要优化的部分", ""
            
            result = agent.process_paper(
                content,
                stage=stage,
                file_type=file_type,
                sections_to_optimize=section_list,
                target_journal=target_journal if target_journal else None
            )
            
            if result.status != "success":
                return f"优化失败: {result.message}", ""
            
            # 格式化结果
            output_parts = []
            diff_html = ""
            
            for section, opt_result in result.optimizations.items():
                if opt_result.success:
                    output_parts.append(f"## {section.upper()}\n\n{opt_result.optimized}")
                    
                    # 取第一个部分的对比
                    if not diff_html:
                        diff_html = create_diff_display(
                            opt_result.original[:500],
                            opt_result.optimized[:500],
                            f"{section} 修改对比"
                        )
            
            if not output_parts:
                return "未能生成任何优化结果，请检查论文内容是否完整", ""
            
            return "\n\n---\n\n".join(output_parts), diff_html
            
        except ValueError as e:
            return f"配置错误: {str(e)}", ""
        except Exception as e:
            return f"优化失败: {str(e)}", ""
    
    def process_dedup(text, strength, preserve_terms):
        """降重处理"""
        try:
            from engines.dedup import DedupEngine
            
            if not text:
                return "请输入文本", "", ""
            
            text = text.strip()
            if len(text) < 20:
                return "文本过短，请输入至少20个字符", "", ""
            
            engine = DedupEngine()
            terms = [t.strip() for t in preserve_terms.split(",") if t.strip()] if preserve_terms else None
            
            result = engine.process(text, strength=int(strength), preserve_terms=terms)
            
            report = engine.get_dedup_report(result)
            diff_html = create_diff_display(result.original, result.processed, "降重对比")
            
            return result.processed, report, diff_html
            
        except ValueError as e:
            return f"配置错误: {str(e)}", "", ""
        except Exception as e:
            return f"处理失败: {str(e)}", "", ""
    
    def process_deai(text):
        """降AI处理"""
        try:
            from engines.deai import DeAIEngine
            
            if not text:
                return "请输入文本", "", ""
            
            text = text.strip()
            if len(text) < 20:
                return "文本过短，请输入至少20个字符", "", ""
            
            engine = DeAIEngine()
            result = engine.process(text)
            
            report = engine.get_report(result)
            diff_html = create_diff_display(result.original, result.processed, "降AI对比")
            
            return result.processed, report, diff_html
            
        except ValueError as e:
            return f"配置错误: {str(e)}", "", ""
        except Exception as e:
            return f"处理失败: {str(e)}", "", ""
    
    def process_both(text, strength, preserve_terms):
        """降重 + 降AI"""
        try:
            from engines.dedup import DedupEngine
            from engines.deai import DeAIEngine
            
            if not text:
                return "请输入文本", "", ""
            
            text = text.strip()
            if len(text) < 20:
                return "文本过短，请输入至少20个字符", "", ""
            
            # 先降重
            dedup_engine = DedupEngine()
            terms = [t.strip() for t in preserve_terms.split(",") if t.strip()] if preserve_terms else None
            dedup_result = dedup_engine.process(text, strength=int(strength), preserve_terms=terms)
            
            # 再降AI
            deai_engine = DeAIEngine()
            deai_result = deai_engine.process(dedup_result.processed)
            
            # 合并报告
            report = f"""# 综合处理报告

## 降重处理
{dedup_engine.get_dedup_report(dedup_result)}

## 降AI处理
{deai_engine.get_report(deai_result)}
"""
            diff_html = create_diff_display(text, deai_result.processed, "综合对比")
            
            return deai_result.processed, report, diff_html
            
        except ValueError as e:
            return f"配置错误: {str(e)}", "", ""
        except Exception as e:
            return f"处理失败: {str(e)}", "", ""
    
    def search_academic(query, source, limit):
        """学术搜索"""
        try:
            if not query:
                return "请输入搜索关键词"
            
            query = query.strip()
            if len(query) < 2:
                return "搜索关键词过短，请输入至少2个字符"
            
            if source == "Google Scholar":
                from knowledge.search.google_scholar import search_google_scholar, format_results
                results = search_google_scholar(query, limit=int(limit))
                return format_results(results)
            else:
                from knowledge.search.cnki import search_cnki, format_results
                results = search_cnki(query, limit=int(limit))
                return format_results(results)
                
        except Exception as e:
            return f"搜索失败: {str(e)}"
    
    def process_revision(comments, paper_summary):
        """处理退修"""
        try:
            from agents.revision import RevisionAgent
            
            if not comments:
                return "请粘贴审稿意见", ""
            
            comments = comments.strip()
            if len(comments) < 20:
                return "审稿意见过短，请粘贴完整的审稿意见", ""
            
            agent = RevisionAgent()
            result = agent.process_comments(comments, paper_summary)
            
            formatted = agent.format_result(result)
            
            return formatted, result.response_letter
            
        except ValueError as e:
            return f"配置错误: {str(e)}", ""
        except Exception as e:
            return f"处理失败: {str(e)}", ""
    
    def search_exemplars(query, category):
        """搜索范例"""
        try:
            from knowledge.exemplars import ExemplarManager
            
            if not query:
                return "请输入搜索关键词"
            
            query = query.strip()
            if len(query) < 2:
                return "搜索关键词过短，请输入至少2个字符"
            
            manager = ExemplarManager()
            cat = category if category != "全部" else None
            results = manager.search(query, category=cat, limit=5)
            
            if not results:
                return "未找到相关范例，请尝试其他关键词"
            
            return manager.format_for_display(results)
            
        except ValueError as e:
            return f"配置错误: {str(e)}"
        except Exception as e:
            return f"搜索失败: {str(e)}"
    
    # ==================== 创建应用 ====================
    
    with gr.Blocks(
        title="EconPaper Pro - 经管论文智能优化",
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS
    ) as app:
        
        # 标题
        gr.Markdown("# 📚 EconPaper Pro")
        gr.Markdown("### 经管学术论文智能优化系统")
        
        with gr.Tabs():
            
            # ========== Tab 1: 论文诊断 ==========
            with gr.TabItem("🔍 论文诊断"):
                with gr.Row():
                    with gr.Column(scale=1):
                        diag_file = gr.File(
                            label="上传论文 (PDF/Word)",
                            file_types=[".pdf", ".docx"]
                        )
                        diag_text = gr.Textbox(
                            label="或粘贴论文内容",
                            placeholder="在此粘贴论文全文...",
                            lines=10
                        )
                        diag_btn = gr.Button("🔍 开始诊断", variant="primary")
                    
                    with gr.Column(scale=1):
                        diag_score_html = gr.HTML(label="评分概览")
                        diag_output = gr.Markdown(label="诊断报告")
                
                diag_btn.click(
                    fn=diagnose_paper,
                    inputs=[diag_file, diag_text],
                    outputs=[diag_output, diag_score_html]
                )
            
            # ========== Tab 2: 深度优化 ==========
            with gr.TabItem("⚙️ 深度优化"):
                with gr.Row():
                    with gr.Column(scale=1):
                        opt_file = gr.File(
                            label="上传论文 (PDF/Word)",
                            file_types=[".pdf", ".docx"]
                        )
                        opt_text = gr.Textbox(
                            label="或粘贴论文内容",
                            placeholder="在此粘贴论文内容...",
                            lines=8
                        )
                        
                        opt_stage = gr.Radio(
                            label="优化阶段",
                            choices=["draft", "submission", "revision", "final"],
                            value="submission",
                            info="初稿重构/投稿优化/退修回应/终稿定稿"
                        )
                        
                        opt_journal = gr.Dropdown(
                            label="目标期刊",
                            choices=["", "经济研究", "管理世界", "金融研究", "中国工业经济", "会计研究", "其他"],
                            value=""
                        )
                        
                        opt_sections = gr.CheckboxGroup(
                            label="优化部分",
                            choices=["title", "abstract", "introduction", "literature", "theory", "methodology", "results", "conclusion"],
                            value=["abstract", "introduction"]
                        )
                        
                        opt_btn = gr.Button("⚙️ 开始优化", variant="primary")
                    
                    with gr.Column(scale=1):
                        opt_output = gr.Markdown(label="优化结果")
                        opt_diff = gr.HTML(label="修改对比")
                
                opt_btn.click(
                    fn=optimize_paper,
                    inputs=[opt_file, opt_text, opt_stage, opt_journal, opt_sections],
                    outputs=[opt_output, opt_diff]
                )
            
            # ========== Tab 3: 降重降AI ==========
            with gr.TabItem("🔧 降重降AI"):
                with gr.Row():
                    with gr.Column(scale=1):
                        dedup_text = gr.Textbox(
                            label="输入文本",
                            placeholder="在此粘贴需要处理的文本...",
                            lines=10
                        )
                        
                        dedup_strength = gr.Slider(
                            label="降重强度",
                            minimum=1,
                            maximum=5,
                            step=1,
                            value=3,
                            info="1=轻微, 5=强力"
                        )
                        
                        dedup_terms = gr.Textbox(
                            label="保留术语（逗号分隔）",
                            placeholder="DID, 工具变量, 固定效应...",
                            lines=1
                        )
                        
                        with gr.Row():
                            dedup_btn = gr.Button("📉 降重", variant="primary")
                            deai_btn = gr.Button("🤖 降AI", variant="secondary")
                            both_btn = gr.Button("⚡ 双重处理", variant="secondary")
                    
                    with gr.Column(scale=1):
                        dedup_output = gr.Textbox(label="处理结果", lines=8)
                        dedup_report = gr.Markdown(label="处理报告")
                        dedup_diff = gr.HTML(label="修改对比")
                
                dedup_btn.click(
                    fn=process_dedup,
                    inputs=[dedup_text, dedup_strength, dedup_terms],
                    outputs=[dedup_output, dedup_report, dedup_diff]
                )
                
                deai_btn.click(
                    fn=process_deai,
                    inputs=[dedup_text],
                    outputs=[dedup_output, dedup_report, dedup_diff]
                )
                
                both_btn.click(
                    fn=process_both,
                    inputs=[dedup_text, dedup_strength, dedup_terms],
                    outputs=[dedup_output, dedup_report, dedup_diff]
                )
            
            # ========== Tab 4: 学术搜索 ==========
            with gr.TabItem("🔎 学术搜索"):
                with gr.Row():
                    with gr.Column(scale=1):
                        search_query = gr.Textbox(
                            label="搜索关键词",
                            placeholder="输入关键词，如：数字经济 企业创新",
                            lines=1
                        )
                        
                        search_source = gr.Radio(
                            label="搜索来源",
                            choices=["Google Scholar", "知网 CNKI"],
                            value="Google Scholar"
                        )
                        
                        search_limit = gr.Slider(
                            label="结果数量",
                            minimum=5,
                            maximum=20,
                            step=5,
                            value=10
                        )
                        
                        search_btn = gr.Button("🔎 搜索", variant="primary")
                    
                    with gr.Column(scale=2):
                        search_output = gr.Markdown(label="搜索结果")
                
                search_btn.click(
                    fn=search_academic,
                    inputs=[search_query, search_source, search_limit],
                    outputs=[search_output]
                )
            
            # ========== Tab 5: 退修助手 ==========
            with gr.TabItem("📝 退修助手"):
                with gr.Row():
                    with gr.Column(scale=1):
                        rev_comments = gr.Textbox(
                            label="审稿意见",
                            placeholder="粘贴审稿人的意见...",
                            lines=10
                        )
                        
                        rev_summary = gr.Textbox(
                            label="论文摘要（可选）",
                            placeholder="可粘贴论文摘要，帮助生成更精准的回应...",
                            lines=4
                        )
                        
                        rev_btn = gr.Button("📝 生成回应", variant="primary")
                    
                    with gr.Column(scale=1):
                        rev_output = gr.Markdown(label="解析结果")
                        rev_letter = gr.Textbox(label="回应信", lines=10)
                
                rev_btn.click(
                    fn=process_revision,
                    inputs=[rev_comments, rev_summary],
                    outputs=[rev_output, rev_letter]
                )
            
            # ========== Tab 6: 知识库 ==========
            with gr.TabItem("📖 知识库"):
                with gr.Row():
                    with gr.Column(scale=1):
                        kb_query = gr.Textbox(
                            label="搜索范例",
                            placeholder="输入关键词搜索范例...",
                            lines=1
                        )
                        
                        kb_category = gr.Dropdown(
                            label="分类筛选",
                            choices=["全部", "introduction", "literature", "hypothesis", "methodology", "empirical", "conclusion"],
                            value="全部"
                        )
                        
                        kb_btn = gr.Button("🔍 搜索", variant="primary")
                    
                    with gr.Column(scale=2):
                        kb_output = gr.Markdown(label="范例展示")
                
                kb_btn.click(
                    fn=search_exemplars,
                    inputs=[kb_query, kb_category],
                    outputs=[kb_output]
                )
            
            # ========== Tab 7: 设置 ==========
            with gr.TabItem("⚙️ 设置"):
                gr.Markdown("""
                ## ⚙️ 系统设置

                ### 当前配置
                
                配置项存储在 `.env` 文件中，请根据需要修改。

                | 配置项 | 说明 |
                |-------|------|
                | LLM_API_BASE | LLM API 地址 |
                | LLM_API_KEY | LLM API 密钥 |
                | LLM_MODEL | LLM 模型名称 |
                | EMBEDDING_API_BASE | 嵌入模型 API 地址 |
                | EMBEDDING_API_KEY | 嵌入模型 API 密钥 |
                | EMBEDDING_MODEL | 嵌入模型名称 |
                | SERPAPI_KEY | SerpAPI 密钥（用于 Google Scholar 搜索） |

                ### 使用说明

                1. **论文诊断**: 上传 PDF/Word 文件或粘贴文本，获取多维度诊断报告
                2. **深度优化**: 选择优化阶段和目标期刊，对论文各部分进行优化
                3. **降重降AI**: 输入文本，选择处理方式，获取改写后的内容
                4. **学术搜索**: 搜索 Google Scholar 或知网文献
                5. **退修助手**: 粘贴审稿意见，生成回应策略和回应信
                6. **知识库**: 搜索和浏览顶刊论文范例

                ### 注意事项

                - 所有论文内容仅在本地处理，通过配置的 API 进行 LLM 调用
                - 长文档会自动分段处理
                - 建议配置 API 密钥后使用完整功能
                """)
        
        # 页脚
        gr.Markdown("""
        ---
        <p style="text-align: center; color: #718096; font-size: 0.9rem;">
            EconPaper Pro v1.0 | 面向青年学者的经管论文智能优化系统
        </p>
        """)
    
    return app


if __name__ == "__main__":
    app = create_app()
    app.launch()
