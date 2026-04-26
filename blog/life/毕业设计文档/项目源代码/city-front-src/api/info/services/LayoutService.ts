/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { LayoutInfoGetReq } from '../models/LayoutInfoGetReq';
import type { LayoutInfoGetRes } from '../models/LayoutInfoGetRes';
import type { LayoutInfoPostReq } from '../models/LayoutInfoPostReq';
import type { LayoutInfoPostRes } from '../models/LayoutInfoPostRes';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class LayoutService {
    /**
     * 获取布局信息,根据布局id获取对应的布局信息元id和布局数据
     * @param requestBody
     * @returns LayoutInfoGetRes 成功获取布局信息
     * @throws ApiError
     */
    public static getLayoutInfo(
        requestBody?: LayoutInfoGetReq,
    ): CancelablePromise<LayoutInfoGetRes> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/layout/info',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 发送并构建存储布局信息,包括布局id和布局的数据,返回只接受一个布局对应的信息员元id
     * @param requestBody
     * @returns LayoutInfoPostRes 成功存储布局信息
     * @throws ApiError
     */
    public static postLayoutInfo(
        requestBody?: LayoutInfoPostReq,
    ): CancelablePromise<LayoutInfoPostRes> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/layout/info',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
