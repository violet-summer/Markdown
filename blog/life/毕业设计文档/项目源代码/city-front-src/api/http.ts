import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig } from 'axios';

// 基于 Vite 的环境变量（可在 .env 中配置 VITE_API_BASE_URL），默认为空（相对路径）
const baseURL = (import.meta as any)?.env?.VITE_API_BASE_URL ?? '';

export const axiosInstance: AxiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
  // 你可以在这里设置其他 axios 默认项，如 timeout
});

// 请求拦截器（可扩展，如注入 token）
axiosInstance.interceptors.request.use(
  (config) => {
    // 例如：从 localStorage 注入认证 token
    try {
      const token = window.localStorage.getItem('auth_token');
      if (token) {
        config.headers = config.headers || {};
        config.headers['Authorization'] = `Bearer ${token}`;
        console.log(token)
      }
    } catch (e) {
      console.error("没有token可以获取");
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器：可统一处理错误格式
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // 你可以在这里对错误做统一包装或日志
    return Promise.reject(error);
  }
);

export async function apiRequest<T = any>(url: string, config?: AxiosRequestConfig): Promise<T> {
  const res = await axiosInstance.request<T>({ url, ...(config || {}) });
  return res.data;
}

