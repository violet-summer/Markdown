import type { ApiEnvelope } from "@/models/api-contract";
import { apiRequest } from "./http";

/** 当前用户资料。 */
export type UserProfile = {
  userId: string;
  username: string;
  email: string;
};

/** 更新用户资料请求体。 */
export type UpdateUserProfileRequest = {
  username?: string;
  email?: string;
};

/**
 * 获取当前登录用户信息。
 * GET /api/users/me
 */
export function getMe() {
  return apiRequest<ApiEnvelope<UserProfile>>("/api/users/me");
}

/**
 * 更新当前登录用户信息。
 * PATCH /api/users/me
 */
export function updateMe(payload: UpdateUserProfileRequest) {
  return apiRequest<ApiEnvelope<UserProfile>>("/api/users/me", {
    method: "PATCH",
    data: payload,
  });
}
