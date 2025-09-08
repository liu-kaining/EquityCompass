// 智策股析 - 主要JavaScript功能（从原项目复用）

// 文档加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 初始化所有功能
    initializeApp();
});

// 应用初始化
function initializeApp() {
    // 自动关闭Alert消息
    autoCloseAlerts();
    
    // 初始化工具提示
    initializeTooltips();
    
    // 初始化卡片悬停效果
    initializeCardHovers();
}

// 自动关闭Alert消息
function autoCloseAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // 5秒后自动关闭
    });
}

// 初始化Bootstrap工具提示
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// 初始化卡片悬停效果
function initializeCardHovers() {
    const cards = document.querySelectorAll('.card-hover');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

// 显示加载状态
function showLoading(element, text = '加载中...') {
    if (element) {
        element.innerHTML = `<span class="loading-spinner me-2"></span>${text}`;
        element.disabled = true;
    }
}

// 隐藏加载状态
function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

// 显示成功消息
function showSuccess(message) {
    showAlert(message, 'success');
}

// 显示错误消息
function showError(message) {
    showAlert(message, 'danger');
}

// 显示信息消息
function showInfo(message) {
    showAlert(message, 'info');
}

// 通用显示Alert函数
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (alertContainer) {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // 插入到容器顶部
        alertContainer.insertBefore(alertElement, alertContainer.firstChild);
        
        // 5秒后自动关闭
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alertElement);
            bsAlert.close();
        }, 5000);
    }
}

// 确认对话框
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

// 格式化数字
function formatNumber(num) {
    return new Intl.NumberFormat('zh-CN').format(num);
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// AJAX请求封装
async function makeRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || '请求失败');
        }
        
        return data;
    } catch (error) {
        console.error('请求错误:', error);
        showError(error.message || '网络请求失败');
        throw error;
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// 节流函数
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// 复制到剪贴板
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showSuccess('已复制到剪贴板');
    } catch (err) {
        console.error('复制失败:', err);
        showError('复制失败');
    }
}

// 下载文件
function downloadFile(url, filename) {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Toast 提示函数
function showToast(type, message, duration = 3000) {
    // 创建 toast 容器（如果不存在）
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '1055';
        document.body.appendChild(toastContainer);
    }
    
    // 创建 toast 元素
    const toastId = 'toast-' + Date.now();
    const toastElement = document.createElement('div');
    toastElement.id = toastId;
    toastElement.className = 'toast';
    toastElement.setAttribute('role', 'alert');
    toastElement.setAttribute('aria-live', 'assertive');
    toastElement.setAttribute('aria-atomic', 'true');
    
    // 设置 toast 内容
    const iconMap = {
        'success': 'fas fa-check-circle text-success',
        'error': 'fas fa-times-circle text-danger',
        'warning': 'fas fa-exclamation-triangle text-warning',
        'info': 'fas fa-info-circle text-info'
    };
    
    const iconClass = iconMap[type] || iconMap['info'];
    
    toastElement.innerHTML = `
        <div class="toast-header">
            <i class="${iconClass} me-2"></i>
            <strong class="me-auto">${type === 'success' ? '成功' : type === 'error' ? '错误' : type === 'warning' ? '警告' : '提示'}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // 添加到容器
    toastContainer.appendChild(toastElement);
    
    // 初始化并显示 toast
    const toast = new bootstrap.Toast(toastElement, {
        autohide: true,
        delay: duration
    });
    
    toast.show();
    
    // 自动移除元素
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
    
    return toast;
}
