import type { ApiEnvelope } from "@/models/api-contract";
import { apiRequest } from "./http";

/** 创建异步任务请求体。 */
export type CreateJobRequest = {
  type: "layout" | "model";
  payload: Record<string, unknown>;
};

/** 异步任务详情。 */
export type JobDetail = {
  jobId: number;
  type: "layout" | "model";
  status: string;
  payload?: Record<string, unknown>;
  result?: Record<string, unknown>;
};

/**
 * 创建任务。
 * POST /api/jobs
 */
export function createJob(payload: CreateJobRequest) {
  return apiRequest<ApiEnvelope<JobDetail>>("/api/jobs", {
    method: "POST",
    data: payload,
  });
}

/**
 * 查询任务详情。
 * GET /api/jobs/{jobId}
 */
export function getJob(jobId: number) {
  return apiRequest<ApiEnvelope<JobDetail>>(`/api/jobs/${jobId}`);
}
