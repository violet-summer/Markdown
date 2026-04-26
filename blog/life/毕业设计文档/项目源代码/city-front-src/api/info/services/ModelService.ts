/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ModelInfoGetReq } from '../models/ModelInfoGetReq';
import type { ModelInfoGetRes } from '../models/ModelInfoGetRes';
import type { ModelInfoPostReq } from '../models/ModelInfoPostReq';
import type { ModelInfoPostRes } from '../models/ModelInfoPostRes';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class ModelService {
    /**
     * 获取模型元信息，根据模型id获取对应的模型元信息和数据
     * @param requestBody
     * @returns ModelInfoGetRes 成功获取模型元信息
     * @throws ApiError
     */
    public static getModelInfo(
        requestBody?: ModelInfoGetReq,
    ): CancelablePromise<ModelInfoGetRes> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/model/info',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * 存储模型元信息，包括模型id和模型的数据，返回模型元信息id
     * @param requestBody
     * @returns ModelInfoPostRes 成功存储模型元信息
     * @throws ApiError
     */
    public static postModelInfo(
        requestBody?: ModelInfoPostReq,
    ): CancelablePromise<ModelInfoPostRes> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/model/info',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
}
