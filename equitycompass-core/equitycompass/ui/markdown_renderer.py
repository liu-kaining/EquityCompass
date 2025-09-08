"""
Markdown 渲染器 - 提供 Markdown 到 HTML 的转换功能
"""

import markdown
import re
from typing import Dict, Any, Optional
from markdown.extensions import codehilite, fenced_code, tables, toc


class MarkdownRenderer:
    """Markdown 渲染器"""
    
    def __init__(self, extensions: list = None, extension_configs: Dict[str, Any] = None):
        """
        初始化 Markdown 渲染器
        
        Args:
            extensions: Markdown 扩展列表
            extension_configs: 扩展配置
        """
        self.extensions = extensions or [
            'codehilite',
            'fenced_code', 
            'tables',
            'toc',
            'nl2br',
            'attr_list'
        ]
        
        self.extension_configs = extension_configs or {
            'codehilite': {
                'css_class': 'highlight',
                'use_pygments': True,
                'noclasses': False,
            },
            'toc': {
                'permalink': True,
                'permalink_title': '永久链接',
            }
        }
        
        self.md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
    
    def render(self, markdown_text: str, **kwargs) -> str:
        """
        渲染 Markdown 文本为 HTML
        
        Args:
            markdown_text: Markdown 文本
            **kwargs: 额外参数
            
        Returns:
            渲染后的 HTML
        """
        if not markdown_text:
            return ""
        
        # 预处理 Markdown 文本
        processed_text = self._preprocess(markdown_text)
        
        # 渲染为 HTML
        html = self.md.convert(processed_text)
        
        # 后处理 HTML
        processed_html = self._postprocess(html)
        
        return processed_html
    
    def _preprocess(self, text: str) -> str:
        """
        预处理 Markdown 文本
        
        Args:
            text: 原始 Markdown 文本
            
        Returns:
            处理后的文本
        """
        # 清理开头的多余空格和换行
        text = text.strip()
        text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)
        
        # 处理可能的 HTML 实体
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # 处理标题中的粗体格式 - 移除标题中的粗体标记
        text = re.sub(r'^# \*\*(.*?)\*\*', r'# \1', text, flags=re.MULTILINE)
        text = re.sub(r'^## \*\*(.*?)\*\*', r'## \1', text, flags=re.MULTILINE)
        text = re.sub(r'^### \*\*(.*?)\*\*', r'### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^#### \*\*(.*?)\*\*', r'#### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^##### \*\*(.*?)\*\*', r'##### \1', text, flags=re.MULTILINE)
        text = re.sub(r'^###### \*\*(.*?)\*\*', r'###### \1', text, flags=re.MULTILINE)
        
        return text
    
    def _postprocess(self, html: str) -> str:
        """
        后处理 HTML
        
        Args:
            html: 渲染后的 HTML
            
        Returns:
            处理后的 HTML
        """
        # 添加自定义 CSS 类
        html = self._add_css_classes(html)
        
        # 处理表格样式
        html = self._enhance_tables(html)
        
        # 处理代码块样式
        html = self._enhance_code_blocks(html)
        
        return html
    
    def _add_css_classes(self, html: str) -> str:
        """添加自定义 CSS 类"""
        # 为段落添加类
        html = re.sub(r'<p>', '<p class="markdown-paragraph">', html)
        
        # 为标题添加类
        html = re.sub(r'<h1>', '<h1 class="markdown-h1">', html)
        html = re.sub(r'<h2>', '<h2 class="markdown-h2">', html)
        html = re.sub(r'<h3>', '<h3 class="markdown-h3">', html)
        html = re.sub(r'<h4>', '<h4 class="markdown-h4">', html)
        html = re.sub(r'<h5>', '<h5 class="markdown-h5">', html)
        html = re.sub(r'<h6>', '<h6 class="markdown-h6">', html)
        
        # 为列表添加类
        html = re.sub(r'<ul>', '<ul class="markdown-list">', html)
        html = re.sub(r'<ol>', '<ol class="markdown-list">', html)
        
        return html
    
    def _enhance_tables(self, html: str) -> str:
        """增强表格样式"""
        # 为表格添加 Bootstrap 类
        html = re.sub(r'<table>', '<table class="table table-striped table-hover">', html)
        html = re.sub(r'<thead>', '<thead class="table-dark">', html)
        
        return html
    
    def _enhance_code_blocks(self, html: str) -> str:
        """增强代码块样式"""
        # 为代码块添加容器
        html = re.sub(
            r'<pre><code class="language-(\w+)">',
            r'<div class="code-block"><pre><code class="language-\1">',
            html
        )
        html = re.sub(r'</code></pre>', '</code></pre></div>', html)
        
        return html
    
    def get_css_styles(self) -> str:
        """
        获取 Markdown 渲染的 CSS 样式
        
        Returns:
            CSS 样式字符串
        """
        return """
        .markdown-content {
            line-height: 1.8;
            color: #2c3e50;
            font-size: 15px;
            text-indent: 0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: transparent;
            padding: 2rem;
            border-radius: 8px;
            min-height: auto;
            max-height: none;
            overflow: visible;
        }
        
        .markdown-content > *:first-child {
            margin-top: 0;
            padding-top: 0;
        }
        
        .markdown-content > p:first-child {
            text-indent: 0;
            margin-left: 0;
            padding-left: 0;
        }
        
        .markdown-h1, .markdown-h2, .markdown-h3, 
        .markdown-h4, .markdown-h5, .markdown-h6 {
            margin-top: 2.5rem;
            margin-bottom: 1.5rem;
            color: #1a202c;
            font-weight: 700;
            line-height: 1.3;
            letter-spacing: -0.025em;
        }
        
        .markdown-h1 { font-size: 2.2rem; }
        .markdown-h2 { font-size: 1.8rem; }
        .markdown-h3 { font-size: 1.5rem; }
        .markdown-h4 { font-size: 1.3rem; }
        .markdown-h5 { font-size: 1.1rem; }
        .markdown-h6 { font-size: 1rem; }
        
        .markdown-paragraph {
            margin-bottom: 1.5rem;
            text-align: justify;
        }
        
        .markdown-list {
            margin-bottom: 1.5rem;
            padding-left: 2rem;
        }
        
        .markdown-list li {
            margin-bottom: 0.5rem;
        }
        
        .code-block {
            margin: 1.5rem 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .code-block pre {
            margin: 0;
            padding: 1rem;
            background: #f8f9fa;
            border: none;
            border-radius: 0;
        }
        
        .code-block code {
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
            font-size: 14px;
            line-height: 1.5;
        }
        
        .table {
            margin: 1.5rem 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .table th {
            font-weight: 600;
            border: none;
        }
        
        .table td {
            border: none;
            border-bottom: 1px solid #dee2e6;
        }
        
        .table-striped tbody tr:nth-of-type(odd) {
            background-color: rgba(0,0,0,0.02);
        }
        
        .table-hover tbody tr:hover {
            background-color: rgba(0,0,0,0.05);
        }
        
        blockquote {
            border-left: 4px solid #007bff;
            padding-left: 1rem;
            margin: 1.5rem 0;
            font-style: italic;
            color: #6c757d;
        }
        
        img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        a {
            color: #007bff;
            text-decoration: none;
        }
        
        a:hover {
            color: #0056b3;
            text-decoration: underline;
        }
        
        strong {
            font-weight: 700;
            color: #1a202c;
        }
        
        em {
            font-style: italic;
            color: #4a5568;
        }
        """
    
    def render_with_styles(self, markdown_text: str, include_css: bool = True) -> str:
        """
        渲染 Markdown 并包含样式
        
        Args:
            markdown_text: Markdown 文本
            include_css: 是否包含 CSS 样式
            
        Returns:
            包含样式的完整 HTML
        """
        html = self.render(markdown_text)
        
        if include_css:
            css = self.get_css_styles()
            html = f'<style>{css}</style><div class="markdown-content">{html}</div>'
        else:
            html = f'<div class="markdown-content">{html}</div>'
        
        return html
