import type { ApiEnvelope } from "@/models/api-contract";
import { apiRequest } from "./http";

/** 登录请求体。 */
export type LoginRequest = {
  identifier: string;
  password: string;
};

/** 登录返回数据。 */
export type LoginResponse = {
  token: string;
  user_id: string;
  username: string;
  email: string;
};

/** 注册请求体。 */
export type RegisterRequest = {
  user_name: string;
  email: string;
  password: string;
};

/** 注册返回数据。 */
export type RegisterResponse = {
  token: string;
  user_id: string;
  username: string;
  email: string;
};

/**
 * 用户登录。
 * POST /api/auth/login
 */
export function login(payload: LoginRequest) {
  return apiRequest<ApiEnvelope<LoginResponse>>("/api/auth/login", {
    method: "POST",
    data: payload,
  });
}

/**
 * 用户注册。
 * POST /api/auth/register
 */
export function register(payload: RegisterRequest) {
  return apiRequest<ApiEnvelope<RegisterResponse>>("/api/auth/register", {
    method: "POST",
    data: payload,
  });
}
