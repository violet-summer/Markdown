/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { ApiResponseRegisterResponse } from '../models/ApiResponseRegisterResponse';
import type { LayoutGenerateRequest } from '../models/LayoutGenerateRequest';
import type { LayoutJson } from '../models/LayoutJson';
import type { LoginRequest } from '../models/LoginRequest';
import type { ModelGenerateRequest } from '../models/ModelGenerateRequest';
import type { RegisterRequest } from '../models/RegisterRequest';
import type { ResponseEntityApiResponseLayoutIdResponse } from '../models/ResponseEntityApiResponseLayoutIdResponse';
import type { ResponseEntityApiResponseLayoutJson } from '../models/ResponseEntityApiResponseLayoutJson';
import type { ResponseEntityApiResponseListLayoutsListItem } from '../models/ResponseEntityApiResponseListLayoutsListItem';
import type { ResponseEntityDeleteResponse } from '../models/ResponseEntityDeleteResponse';
import type { ResponseEntityLayoutResultResponse } from '../models/ResponseEntityLayoutResultResponse';
import type { ResponseEntityModelResultResponse } from '../models/ResponseEntityModelResultResponse';
import type { ResponseEntityModelSingleResponse } from '../models/ResponseEntityModelSingleResponse';
import type { ResponseEntityModelsListResponse } from '../models/ResponseEntityModelsListResponse';
import type { ResponseEntityStatusResponse } from '../models/ResponseEntityStatusResponse';
import type { ResponseEntityUpdateResponse } from '../models/ResponseEntityUpdateResponse';
import type { CancelablePromise } from '../core/CancelablePromise';
import { OpenAPI } from '../core/OpenAPI';
import { request as __request } from '../core/request';
export class DefaultService {
    /**
     * login
     * @param requestBody
     * @returns ApiResponseRegisterResponse
     * @throws ApiError
     */
    public static postAuthLogin(
        requestBody?: LoginRequest,
    ): CancelablePromise<ApiResponseRegisterResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/login',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * register
     * @param requestBody
     * @returns ApiResponseRegisterResponse
     * @throws ApiError
     */
    public static postAuthRegister(
        requestBody?: RegisterRequest,
    ): CancelablePromise<ApiResponseRegisterResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/auth/register',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * generateLayout
     * @param authorization
     * @param requestBody
     * @returns ResponseEntityApiResponseLayoutIdResponse
     * @throws ApiError
     */
    public static postApiLayoutGenerate(
        authorization: string,
        requestBody?: LayoutGenerateRequest,
    ): CancelablePromise<ResponseEntityApiResponseLayoutIdResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/layout/generate',
            headers: {
                'Authorization': authorization,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * generateLayout
     * @param requestBody
     * @returns ResponseEntityApiResponseLayoutIdResponse
     * @throws ApiError
     */
    public static postLayoutGenerate(
        requestBody?: LayoutGenerateRequest,
    ): CancelablePromise<ResponseEntityApiResponseLayoutIdResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/layout/generate',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * getLayoutProgress
     * @param layoutId
     * @returns ResponseEntityStatusResponse
     * @throws ApiError
     */
    public static getApiLayoutProgress(
        layoutId: string,
    ): CancelablePromise<ResponseEntityStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/layout/progress/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * getLayoutResult
     * @param layoutId
     * @returns ResponseEntityLayoutResultResponse
     * @throws ApiError
     */
    public static getApiLayoutResult(
        layoutId: string,
    ): CancelablePromise<ResponseEntityLayoutResultResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/layout/result/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * deleteJob
     * @param layoutId
     * @returns ResponseEntityDeleteResponse
     * @throws ApiError
     */
    public static deleteApiLayoutJob(
        layoutId: string,
    ): CancelablePromise<ResponseEntityDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/layout/job/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * deleteLayout
     * @param layoutId
     * @returns ResponseEntityDeleteResponse
     * @throws ApiError
     */
    public static deleteApiLayoutDelete(
        layoutId: string,
    ): CancelablePromise<ResponseEntityDeleteResponse> {
        return __request(OpenAPI, {
            method: 'DELETE',
            url: '/api/layout/delete/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * updateLayoutStatus
     * @param layoutId
     * @param requestBody
     * @returns ResponseEntityUpdateResponse
     * @throws ApiError
     */
    public static putApiLayoutUpdate(
        layoutId: string,
        requestBody?: LayoutJson,
    ): CancelablePromise<ResponseEntityUpdateResponse> {
        return __request(OpenAPI, {
            method: 'PUT',
            url: '/api/layout/update/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * listUserLayouts
     * @returns ResponseEntityApiResponseListLayoutsListItem
     * @throws ApiError
     */
    public static getApiLayoutListLayouts(): CancelablePromise<ResponseEntityApiResponseListLayoutsListItem> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/layout/list_layouts',
        });
    }
    /**
     * getLayoutJson
     * @param layoutId
     * @returns ResponseEntityApiResponseLayoutJson
     * @throws ApiError
     */
    public static getApiLayoutLayoutJson(
        layoutId: string,
    ): CancelablePromise<ResponseEntityApiResponseLayoutJson> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/layout/layout_json/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * generate3DModel
     * @param requestBody
     * @returns ResponseEntityStatusResponse
     * @throws ApiError
     */
    public static postModelsGenerate3D(
        requestBody?: ModelGenerateRequest,
    ): CancelablePromise<ResponseEntityStatusResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/models/generate-3d',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * generate3DModel
     * @param requestBody
     * @returns ResponseEntityStatusResponse
     * @throws ApiError
     */
    public static postApiModelsGenerate(
        requestBody?: ModelGenerateRequest,
    ): CancelablePromise<ResponseEntityStatusResponse> {
        return __request(OpenAPI, {
            method: 'POST',
            url: '/api/models/generate',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * getModelProgress
     * @param layoutId
     * @returns ResponseEntityStatusResponse
     * @throws ApiError
     */
    public static getApiModelsProgress(
        layoutId: string,
    ): CancelablePromise<ResponseEntityStatusResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/models/progress/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * getModelResult
     * @param layoutId
     * @returns ResponseEntityModelResultResponse
     * @throws ApiError
     */
    public static getApiModelsResult(
        layoutId: string,
    ): CancelablePromise<ResponseEntityModelResultResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/models/result/{layoutId}',
            path: {
                'layoutId': layoutId,
            },
        });
    }
    /**
     * listModels
     * @returns ResponseEntityModelsListResponse
     * @throws ApiError
     */
    public static getApiModelsList(): CancelablePromise<ResponseEntityModelsListResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/models/list',
        });
    }
    /**
     * getModelIdMap
     * @param modelId
     * @returns ResponseEntityModelSingleResponse
     * @throws ApiError
     */
    public static getApiModelsModel(
        modelId: string,
    ): CancelablePromise<ResponseEntityModelSingleResponse> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/api/models/model/{modelId}',
            path: {
                'modelId': modelId,
            },
        });
    }
    /**
     * getUserConfig
     * @returns string
     * @throws ApiError
     */
    public static getUsersConfig(): CancelablePromise<string> {
        return __request(OpenAPI, {
            method: 'GET',
            url: '/users/config',
        });
    }
}
