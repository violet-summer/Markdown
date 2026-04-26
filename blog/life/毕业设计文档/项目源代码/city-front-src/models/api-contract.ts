/**
 * 统一 API 包装结构。
 * 后端大部分接口都返回该包裹格式：code/message/data。
 */
export interface ApiEnvelope<T> {
  code: number;
  message: string;
  data: T;
}

/**
 * 接口响应模式：
 * - url: 返回资源地址（如 svgUrl/objUrl）
 * - inline: 返回内联内容（如 svg_content/objContent）
 */
export type ApiResponseMode = "url" | "inline";
