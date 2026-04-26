import { LayoutParams } from "./layout-generate-request";

/**
 * 布局结果相关响应结构定义。
 * 对应布局结果查询、布局列表等接口的数据体。
 */

/**
 * ResponseEntityLayoutResultResponse
 */
export interface LayoutResultResponse {
    layout_id?: string;
    /**
     * 布局参数也要回写，便于前端复现参数。
     */
    params?: LayoutParams;
    status?: number;
    svg_content?: string;
    [property: string]: any;
}


/**
 * ResponseEntityApiResponseListLayoutsDTO
 */
// export interface LayoutsListResponse {
//     code?: number;
//     data?: LayoutsListItem[];
//     message?: string;
//     [property: string]: any;
// }

/**
 * com.example.citybusiness.dto.LayoutsDTO
 *
 * LayoutsDTO
 */
export interface LayoutsListItem {
    /**
     * base62编码字符串
     */
    layout_id: string;
    status: number;
    svg_url: string;
    layout_name: string;
    [property: string]: any;
}