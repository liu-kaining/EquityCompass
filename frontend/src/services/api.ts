import axios, { AxiosInstance, AxiosResponse, AxiosError } from 'axios';
import { ApiResponse } from '../types';

// 创建axios实例
const api: AxiosInstance = axios.create({
  baseURL: process.env.REACT_APP_API_URL || '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器 - 添加认证token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response;
  },
  (error: AxiosError<ApiResponse>) => {
    // 处理认证错误
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    
    // 处理网络错误
    if (!error.response) {
      console.error('Network Error:', error.message);
      return Promise.reject({
        message: '网络连接错误，请检查您的网络设置',
        code: 'NETWORK_ERROR'
      });
    }
    
    // 返回API错误信息
    const errorMessage = error.response.data?.message || '未知错误';
    const errorCode = error.response.data?.error || 'UNKNOWN_ERROR';
    
    return Promise.reject({
      message: errorMessage,
      code: errorCode,
      status: error.response.status
    });
  }
);

export default api;
