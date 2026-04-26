package com.example.layout.service;

import com.baomidou.mybatisplus.extension.service.IService;
import com.example.citybusiness.contract.model.LayoutJson;
import com.example.citybusiness.contract.model.LayoutsListItem;
import com.example.layout.model.Layouts;
import java.util.List;

/**
 * <p>
 * 布局表 服务类
 * </p>
 *
 * @author city_business
 * @since 2026-02-21
 */
public interface ILayoutsService extends IService<Layouts> {
    /**
     * 更新布局 JSON 内容
     */
    void updateLayoutJsonContent(Layouts layout, LayoutJson layoutJson);

    /**
     * 读取布局 JSON 内容
     */
    String readLayoutJsonContent(Long layoutId);

    /**
     * 读取 SVG 内容
     */
    String readSvgContent(String svgUrl);

    /**
     * 查询用户布局列表，返回DTO
     */
    List<LayoutsListItem> listUserLayouts(Long userId);
}
