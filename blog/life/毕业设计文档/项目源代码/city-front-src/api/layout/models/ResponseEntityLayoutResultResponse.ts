/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LayoutParams } from './LayoutParams';
export type ResponseEntityLayoutResultResponse = {
    svg_content?: string;
    /**
     * 布局参数也要回写，便于前端复现参数。
     */
    params?: LayoutParams;
    layout_id?: number;
    status?: number;
};

