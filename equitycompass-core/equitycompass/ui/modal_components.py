"""
弹窗组件 - 提供确认弹窗、警告弹窗、加载弹窗等功能
"""

from typing import Callable, Optional, Dict, Any
import json


class ModalComponent:
    """弹窗组件基类"""
    
    def __init__(self, modal_id: str, title: str = "", message: str = ""):
        self.modal_id = modal_id
        self.title = title
        self.message = message
        self.on_confirm: Optional[Callable] = None
        self.on_cancel: Optional[Callable] = None
    
    def set_callbacks(self, on_confirm: Callable = None, on_cancel: Callable = None):
        """设置回调函数"""
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel
    
    def to_html(self) -> str:
        """转换为 HTML"""
        raise NotImplementedError
    
    def to_js(self) -> str:
        """转换为 JavaScript"""
        raise NotImplementedError


class ConfirmModal(ModalComponent):
    """确认弹窗组件"""
    
    def __init__(self, modal_id: str = "confirmModal", title: str = "确认操作", 
                 message: str = "确定要执行此操作吗？", confirm_text: str = "确认", 
                 cancel_text: str = "取消"):
        super().__init__(modal_id, title, message)
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_class = "btn-primary"
        self.cancel_class = "btn-outline-secondary"
    
    def to_html(self) -> str:
        """生成确认弹窗 HTML"""
        return f"""
        <!-- 自定义确认弹窗 -->
        <div class="modal fade" id="{self.modal_id}" tabindex="-1" aria-labelledby="{self.modal_id}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-effect border-0 shadow-lg">
                    <div class="modal-header border-0 bg-transparent">
                        <h5 class="modal-title text-primary" id="{self.modal_id}Title">
                            <i class="fas fa-question-circle text-warning me-2"></i>
                            <span id="{self.modal_id}TitleText">{self.title}</span>
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body">
                        <p id="{self.modal_id}Message" class="mb-0 text-dark">{self.message}</p>
                    </div>
                    <div class="modal-footer border-0 bg-transparent">
                        <button type="button" class="btn {self.cancel_class}" data-bs-dismiss="modal">
                            <i class="fas fa-times me-2"></i>{self.cancel_text}
                        </button>
                        <button type="button" class="btn {self.confirm_class}" id="{self.modal_id}Btn">
                            <i class="fas fa-check me-2"></i>{self.confirm_text}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def to_js(self) -> str:
        """生成确认弹窗 JavaScript"""
        return f"""
        // 自定义确认弹窗函数
        function show{self.modal_id.title()}Modal(title, message, onConfirm, onCancel = null) {{
            console.log('显示确认弹窗:', title, message);
            
            const modalElement = document.getElementById('{self.modal_id}');
            if (!modalElement) {{
                console.error('确认弹窗元素未找到，使用原生confirm');
                if (confirm(message)) {{
                    if (onConfirm) onConfirm();
                }}
                return;
            }}
            
            const modal = new bootstrap.Modal(modalElement);
            
            // 设置内容
            const titleElement = document.getElementById('{self.modal_id}TitleText');
            const messageElement = document.getElementById('{self.modal_id}Message');
            
            if (titleElement) titleElement.textContent = title;
            if (messageElement) messageElement.textContent = message;
            
            // 绑定确认事件
            const confirmBtn = document.getElementById('{self.modal_id}Btn');
            if (confirmBtn) {{
                const handleConfirm = () => {{
                    console.log('用户确认操作');
                    modal.hide();
                    confirmBtn.removeEventListener('click', handleConfirm);
                    if (onConfirm) onConfirm();
                }};
                confirmBtn.addEventListener('click', handleConfirm);
            }}
            
            // 绑定取消事件
            const handleCancel = () => {{
                console.log('用户取消操作');
                modal.hide();
                modalElement.removeEventListener('hidden.bs.modal', handleCancel);
                if (onCancel) onCancel();
            }};
            modalElement.addEventListener('hidden.bs.modal', handleCancel);
            
            // 显示弹窗
            modal.show();
        }}
        
        // 简化的确认函数
        function confirmAction(title, message, onConfirm) {{
            console.log('调用confirmAction:', title, message);
            show{self.modal_id.title()}Modal(title, message, onConfirm);
        }}
        
        // 确保函数在全局作用域可用
        window.confirmAction = confirmAction;
        window.show{self.modal_id.title()}Modal = show{self.modal_id.title()}Modal;
        """


class AlertModal(ModalComponent):
    """警告弹窗组件"""
    
    def __init__(self, modal_id: str = "alertModal", title: str = "提示", 
                 message: str = "", alert_type: str = "info"):
        super().__init__(modal_id, title, message)
        self.alert_type = alert_type
        self.button_text = "确定"
        self.button_class = "btn-primary"
        
        # 根据类型设置图标和颜色
        self.icon_map = {
            "info": ("fas fa-info-circle", "text-info"),
            "success": ("fas fa-check-circle", "text-success"),
            "warning": ("fas fa-exclamation-triangle", "text-warning"),
            "error": ("fas fa-times-circle", "text-danger"),
            "danger": ("fas fa-times-circle", "text-danger")
        }
    
    def to_html(self) -> str:
        """生成警告弹窗 HTML"""
        icon_class, text_class = self.icon_map.get(self.alert_type, self.icon_map["info"])
        
        return f"""
        <!-- 警告弹窗 -->
        <div class="modal fade" id="{self.modal_id}" tabindex="-1" aria-labelledby="{self.modal_id}Label" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-effect border-0 shadow-lg">
                    <div class="modal-header border-0 bg-transparent">
                        <h5 class="modal-title {text_class}" id="{self.modal_id}Title">
                            <i class="{icon_class} me-2"></i>
                            <span id="{self.modal_id}TitleText">{self.title}</span>
                        </h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="{icon_class} fa-3x {text_class}"></i>
                        </div>
                        <p id="{self.modal_id}Message" class="mb-0 text-dark">{self.message}</p>
                    </div>
                    <div class="modal-footer border-0 justify-content-center">
                        <button type="button" class="btn {self.button_class}" data-bs-dismiss="modal">
                            <i class="fas fa-check me-2"></i>{self.button_text}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        """
    
    def to_js(self) -> str:
        """生成警告弹窗 JavaScript"""
        return f"""
        // 警告弹窗函数
        function show{self.modal_id.title()}Modal(title, message, alertType = 'info') {{
            console.log('显示警告弹窗:', title, message, alertType);
            
            const modalElement = document.getElementById('{self.modal_id}');
            if (!modalElement) {{
                console.error('警告弹窗元素未找到，使用原生alert');
                alert(message);
                return;
            }}
            
            const modal = new bootstrap.Modal(modalElement);
            
            // 设置内容
            const titleElement = document.getElementById('{self.modal_id}TitleText');
            const messageElement = document.getElementById('{self.modal_id}Message');
            
            if (titleElement) titleElement.textContent = title;
            if (messageElement) messageElement.textContent = message;
            
            // 根据类型设置样式
            const iconMap = {{
                'info': ['fas fa-info-circle', 'text-info'],
                'success': ['fas fa-check-circle', 'text-success'],
                'warning': ['fas fa-exclamation-triangle', 'text-warning'],
                'error': ['fas fa-times-circle', 'text-danger'],
                'danger': ['fas fa-times-circle', 'text-danger']
            }};
            
            const [iconClass, textClass] = iconMap[alertType] || iconMap['info'];
            
            // 更新图标和颜色
            const iconElements = modalElement.querySelectorAll('i');
            iconElements.forEach(icon => {{
                icon.className = iconClass + ' me-2';
                if (icon.classList.contains('fa-3x')) {{
                    icon.className += ' fa-3x ' + textClass;
                }} else {{
                    icon.className += ' ' + textClass;
                }}
            }});
            
            const titleElement2 = document.getElementById('{self.modal_id}Title');
            if (titleElement2) {{
                titleElement2.className = 'modal-title ' + textClass;
            }}
            
            // 显示弹窗
            modal.show();
        }}
        
        // 确保函数在全局作用域可用
        window.show{self.modal_id.title()}Modal = show{self.modal_id.title()}Modal;
        """


class LoadingModal(ModalComponent):
    """加载弹窗组件"""
    
    def __init__(self, modal_id: str = "loadingModal", title: str = "处理中", 
                 message: str = "请稍候，正在处理您的请求..."):
        super().__init__(modal_id, title, message)
        self.show_progress = False
        self.progress_value = 0
    
    def set_progress(self, value: int):
        """设置进度值 (0-100)"""
        self.progress_value = max(0, min(100, value))
        self.show_progress = True
    
    def to_html(self) -> str:
        """生成加载弹窗 HTML"""
        progress_html = ""
        if self.show_progress:
            progress_html = f"""
            <div class="progress mt-3" style="height: 6px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated" 
                     role="progressbar" style="width: {self.progress_value}%" 
                     aria-valuenow="{self.progress_value}" aria-valuemin="0" aria-valuemax="100">
                </div>
            </div>
            """
        
        return f"""
        <!-- 加载弹窗 -->
        <div class="modal fade" id="{self.modal_id}" tabindex="-1" aria-labelledby="{self.modal_id}Label" aria-hidden="true" data-bs-backdrop="static" data-bs-keyboard="false">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content glass-effect border-0 shadow-lg">
                    <div class="modal-header border-0 bg-transparent">
                        <h5 class="modal-title text-primary" id="{self.modal_id}Title">
                            <i class="fas fa-spinner fa-spin me-2"></i>
                            <span id="{self.modal_id}TitleText">{self.title}</span>
                        </h5>
                    </div>
                    <div class="modal-body text-center">
                        <div class="mb-3">
                            <i class="fas fa-spinner fa-spin fa-3x text-primary"></i>
                        </div>
                        <p id="{self.modal_id}Message" class="mb-0 text-dark">{self.message}</p>
                        {progress_html}
                    </div>
                </div>
            </div>
        </div>
        """
    
    def to_js(self) -> str:
        """生成加载弹窗 JavaScript"""
        return f"""
        // 加载弹窗函数
        function show{self.modal_id.title()}Modal(title, message, showProgress = false) {{
            console.log('显示加载弹窗:', title, message);
            
            const modalElement = document.getElementById('{self.modal_id}');
            if (!modalElement) {{
                console.error('加载弹窗元素未找到');
                return;
            }}
            
            const modal = new bootstrap.Modal(modalElement, {{
                backdrop: 'static',
                keyboard: false
            }});
            
            // 设置内容
            const titleElement = document.getElementById('{self.modal_id}TitleText');
            const messageElement = document.getElementById('{self.modal_id}Message');
            
            if (titleElement) titleElement.textContent = title;
            if (messageElement) messageElement.textContent = message;
            
            // 显示弹窗
            modal.show();
            
            return modal;
        }}
        
        function hide{self.modal_id.title()}Modal() {{
            const modalElement = document.getElementById('{self.modal_id}');
            if (modalElement) {{
                const modal = bootstrap.Modal.getInstance(modalElement);
                if (modal) {{
                    modal.hide();
                }}
            }}
        }}
        
        function update{self.modal_id.title()}Progress(value) {{
            const progressBar = document.querySelector('#{self.modal_id} .progress-bar');
            if (progressBar) {{
                progressBar.style.width = value + '%';
                progressBar.setAttribute('aria-valuenow', value);
            }}
        }}
        
        // 确保函数在全局作用域可用
        window.show{self.modal_id.title()}Modal = show{self.modal_id.title()}Modal;
        window.hide{self.modal_id.title()}Modal = hide{self.modal_id.title()}Modal;
        window.update{self.modal_id.title()}Progress = update{self.modal_id.title()}Progress;
        """


class ModalManager:
    """弹窗管理器"""
    
    def __init__(self):
        self.modals: Dict[str, ModalComponent] = {}
    
    def register_modal(self, modal: ModalComponent):
        """注册弹窗"""
        self.modals[modal.modal_id] = modal
    
    def get_modal(self, modal_id: str) -> Optional[ModalComponent]:
        """获取弹窗"""
        return self.modals.get(modal_id)
    
    def generate_all_html(self) -> str:
        """生成所有弹窗的 HTML"""
        html_parts = []
        for modal in self.modals.values():
            html_parts.append(modal.to_html())
        return "\n".join(html_parts)
    
    def generate_all_js(self) -> str:
        """生成所有弹窗的 JavaScript"""
        js_parts = []
        for modal in self.modals.values():
            js_parts.append(modal.to_js())
        return "\n".join(js_parts)
    
    def create_confirm_modal(self, modal_id: str = "confirmModal", **kwargs) -> ConfirmModal:
        """创建确认弹窗"""
        modal = ConfirmModal(modal_id, **kwargs)
        self.register_modal(modal)
        return modal
    
    def create_alert_modal(self, modal_id: str = "alertModal", **kwargs) -> AlertModal:
        """创建警告弹窗"""
        modal = AlertModal(modal_id, **kwargs)
        self.register_modal(modal)
        return modal
    
    def create_loading_modal(self, modal_id: str = "loadingModal", **kwargs) -> LoadingModal:
        """创建加载弹窗"""
        modal = LoadingModal(modal_id, **kwargs)
        self.register_modal(modal)
        return modal
