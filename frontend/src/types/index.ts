// 智策股析 - 类型定义

// 用户相关类型
export interface User {
  id: number;
  email: string;
  nickname?: string;
  created_at: string;
  plan?: UserPlan;
}

export interface UserPlan {
  type: 'TRIAL' | 'FREE' | 'SUBSCRIPTION' | 'PAY_PER_USE';
  remaining_quota: number;
  expires_at?: string;
}

// 股票相关类型
export interface Stock {
  id: number;
  code: string;
  name: string;
  market: 'US' | 'HK';
  exchange: string;
  industry: string;
  stock_type: 'BUILT_IN' | 'USER_CUSTOM';
  created_by_user_id?: number;
}

// 关注列表类型
export interface WatchlistItem {
  id: number;
  stock: Stock;
  added_at: string;
}

// 分析任务类型
export interface AnalysisTask {
  id: number;
  task_id: string;
  stock: Stock;
  status: 'PENDING' | 'PROCESSING' | 'SUCCESS' | 'FAILED';
  analysis_date: string;
  created_at: string;
  completed_at?: string;
  error_message?: string;
}

// 报告相关类型
export interface Report {
  id: number;
  stock_code: string;
  company_name: string;
  market: 'US' | 'HK';
  analysis_date: string;
  content: string;
  summary: string;
  generated_at: string;
  metadata?: {
    prompt_version: string;
    llm_model: string;
    analysis_time_ms: number;
  };
}

// 支付相关类型
export interface PaymentPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  quota: number; // -1 表示无限制
  features: string[];
}

export interface PaymentTransaction {
  id: number;
  transaction_id: string;
  amount: number;
  currency: string;
  status: 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
  created_at: string;
}

// API响应类型
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  message: string;
  timestamp: string;
  error?: string;
}

export interface PaginatedResponse<T = any> {
  success: boolean;
  data: {
    items: T[];
    pagination: {
      page: number;
      per_page: number;
      total: number;
      pages: number;
    };
  };
  timestamp: string;
}

// 表单相关类型
export interface LoginForm {
  email: string;
}

export interface VerificationForm {
  email: string;
  code: string;
}

export interface AddStockForm {
  market: 'US' | 'HK';
  name: string;
  code: string;
}

export interface ExportOptions {
  report_ids: number[];
  format: 'MD' | 'PDF' | 'ZIP';
  email_result: boolean;
}

// 系统状态类型
export interface SystemHealth {
  status: 'healthy' | 'unhealthy';
  timestamp: number;
  services: {
    database: 'healthy' | 'unhealthy';
    redis: 'healthy' | 'unhealthy';
    celery: 'healthy' | 'unhealthy';
  };
}
