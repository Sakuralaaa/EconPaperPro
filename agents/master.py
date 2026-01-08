# -*- coding: utf-8 -*-
"""
主控Agent模块
编排完整的论文优化流程
"""

from typing import Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from parsers.structure import StructureRecognizer
from parsers.pdf_parser import PDFParser
from parsers.docx_parser import DocxParser
from agents.diagnostic import DiagnosticAgent, FullDiagnosisReport
from agents.optimizer import OptimizerAgent, OptimizationResult


@dataclass
class ProcessingResult:
    """处理结果"""
    stage: str
    paper_structure: Dict
    diagnosis: Optional[FullDiagnosisReport] = None
    optimizations: Dict[str, OptimizationResult] = field(default_factory=dict)
    status: str = "success"
    message: str = ""


class MasterAgent:
    """
    主控Agent
    
    编排完整的论文优化流程，支持四个阶段：
    1. 初稿重构 (draft)
    2. 投稿优化 (submission)
    3. 退修回应 (revision)
    4. 终稿定稿 (final)
    
    使用示例:
        agent = MasterAgent()
        result = agent.process_paper(paper_text, stage="submission")
    """
    
    def __init__(self):
        """初始化主控Agent"""
        self.pdf_parser = PDFParser()
        self.docx_parser = DocxParser()
        self.structure_recognizer = StructureRecognizer()
        self.diagnostic_agent = DiagnosticAgent()
    
    def process_paper(
        self,
        content: Union[str, bytes],
        stage: str = "submission",
        file_type: Optional[str] = None,
        sections_to_optimize: Optional[List[str]] = None,
        target_journal: Optional[str] = None
    ) -> ProcessingResult:
        """
        处理论文
        
        Args:
            content: 论文内容（文本或文件字节）
            stage: 处理阶段
            file_type: 文件类型（pdf/docx/text）
            sections_to_optimize: 要优化的部分
            target_journal: 目标期刊
            
        Returns:
            ProcessingResult: 处理结果
        """
        try:
            # 1. 解析文档
            if isinstance(content, bytes):
                if file_type == "pdf":
                    text = self.pdf_parser.parse_bytes(content)
                elif file_type == "docx":
                    text = self.docx_parser.parse_bytes(content)
                else:
                    text = content.decode("utf-8")
            elif isinstance(content, str):
                text = content
            else:
                text = str(content)
            
            # 2. 识别结构
            paper_structure = self.structure_recognizer.recognize(text)
            
            # 3. 执行诊断
            diagnosis = self.diagnostic_agent.diagnose(text)
            
            # 4. 执行优化
            optimizer = OptimizerAgent(stage=stage)
            
            if target_journal:
                optimizations = optimizer.optimize_for_journal(
                    paper_structure, target_journal
                )
            else:
                optimizations = optimizer.optimize(
                    paper_structure,
                    diagnosis=diagnosis.dimensions,
                    sections=sections_to_optimize
                )
            
            return ProcessingResult(
                stage=stage,
                paper_structure=paper_structure,
                diagnosis=diagnosis,
                optimizations=optimizations,
                status="success",
                message="论文处理完成"
            )
            
        except Exception as e:
            return ProcessingResult(
                stage=stage,
                paper_structure={},
                status="error",
                message=f"处理失败: {str(e)}"
            )
    
    def diagnose_only(
        self,
        content: Union[str, bytes],
        file_type: Optional[str] = None,
        focus: Optional[List[str]] = None,
        on_progress: Optional[Callable[[int, int, str], None]] = None
    ) -> FullDiagnosisReport:
        """
        仅执行诊断
        
        Args:
            content: 论文内容
            file_type: 文件类型
            focus: 聚焦的诊断维度
            
        Returns:
            FullDiagnosisReport: 诊断报告
        """
        # 解析文档
        if isinstance(content, bytes):
            if file_type == "pdf":
                text = self.pdf_parser.parse_bytes(content)
            elif file_type == "docx":
                text = self.docx_parser.parse_bytes(content)
            else:
                text = content.decode("utf-8")
        elif isinstance(content, str):
            text = content
        else:
            text = str(content)
        
        return self.diagnostic_agent.diagnose(text, focus=focus, on_progress=on_progress)
    
    def optimize_section(
        self,
        section_name: str,
        content: str,
        context: Optional[str] = None,
        stage: str = "submission"
    ) -> OptimizationResult:
        """
        优化单个部分
        
        Args:
            section_name: 部分名称
            content: 部分内容
            context: 上下文
            stage: 优化阶段
            
        Returns:
            OptimizationResult: 优化结果
        """
        optimizer = OptimizerAgent(stage=stage)
        return optimizer.optimize_single_section(section_name, content, context)
    
    def get_workflow(self, stage: str) -> List[str]:
        """
        获取指定阶段的工作流程
        
        Args:
            stage: 阶段名称
            
        Returns:
            List[str]: 工作流程步骤
        """
        workflows = {
            "draft": [
                "1. 解析论文内容",
                "2. 识别论文结构",
                "3. 执行全面诊断",
                "4. 重构薄弱部分",
                "5. 完善整体逻辑",
            ],
            "submission": [
                "1. 解析论文内容",
                "2. 识别论文结构",
                "3. 执行全面诊断",
                "4. 优化创新表达",
                "5. 规范方法描述",
                "6. 打磨语言表达",
            ],
            "revision": [
                "1. 解析论文内容",
                "2. 识别论文结构",
                "3. 对照审稿意见",
                "4. 针对性修改",
                "5. 准备回应信",
            ],
            "final": [
                "1. 解析论文内容",
                "2. 识别论文结构",
                "3. 检查格式规范",
                "4. 校对细节问题",
                "5. 生成最终版本",
            ],
        }
        
        return workflows.get(stage, workflows["submission"])
    
    def parse_file(
        self,
        file_path: str
    ) -> Dict:
        """
        解析文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict: 解析后的论文结构
        """
        if file_path.endswith(".pdf"):
            text = self.pdf_parser.parse(file_path)
        elif file_path.endswith(".docx"):
            text = self.docx_parser.parse(file_path)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        
        return self.structure_recognizer.recognize(text)
