package com.example.layout.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.example.citybusiness.contract.model.*;
import com.example.layout.mapper.LayoutsMapper;
import com.example.layout.model.Layouts;
import com.example.layout.service.ILayoutsService;
import com.example.layout.utils.Base62Util;
import com.example.layout.utils.FileUtil;
import com.example.layout.utils.ToSvg;
import jakarta.validation.Valid;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.util.List;
import java.util.stream.Collectors;

import static com.example.layout.utils.ToSvg.forceClockwise;
import static com.example.layout.utils.ToSvg.forceCounterClockwise;


/**
 * <p>
 * 布局表 服务实现类
 * </p>
 *
 * @author city_business
 * @since 2026-02-21
 */
@Service
public class LayoutsServiceImpl extends ServiceImpl<LayoutsMapper, Layouts> implements ILayoutsService {

    private final FileUtil fileUtil;

    public LayoutsServiceImpl(FileUtil fileUtil) {
        this.fileUtil = fileUtil;
    }

    @Override
    public void updateLayoutJsonContent(Layouts layout, LayoutJson layoutJson) {
        try {
            // 检查 layoutJson 的关键字段，避免 svgContent 为空
            if (layoutJson == null) {
                throw new IllegalArgumentException("layoutJson 为空");
            }
            if (layoutJson.getOrigin() == null) {
                throw new IllegalArgumentException("layoutJson.origin 为空");
            }
            if (layoutJson.getWorldDimensions() == null) {
                throw new IllegalArgumentException("layoutJson.worldDimensions 为空");
            }
            if (layoutJson.getGroundPolygon() == null || layoutJson.getGroundPolygon().size() < 3) {
                throw new IllegalArgumentException("layoutJson.groundPolygon 为空或点数不足");
            }
            String jsonContent = new ObjectMapper().writeValueAsString(layoutJson);
            String jsonPath = layout.getSvgUrl().replaceAll("\\.svg$", ".json"); // 将 svg 后缀替换为 json
            fileUtil.writeFile(jsonPath, jsonContent);
            // 主动修正方向，确保SVG环形填充正确（外环顺时针，内环逆时针）
//            System.out.println("修正前 layoutJson: " + jsonContent);
            String svgContent = ToSvg.toSvgContent(layoutJson);
//            System.out.println("修正后svgContent: " + svgContent);
            if (svgContent.trim().isEmpty()) {
                throw new IllegalStateException("svgContent 生成为空，请检查 layoutJson 内容");
            }
            fileUtil.writeFile(layout.getSvgUrl(), svgContent);
            layout.setUpdatedAt(java.time.LocalDateTime.now());
            this.updateById(layout);
        } catch (IOException e) {
            throw new RuntimeException("写入布局 JSON 文件失败", e);
        }
    }

    /**
     * 主动修正所有内外环方向，确保外环顺时针、内环逆时针
     */
    private LayoutJson fixAllAnnulusDirection(LayoutJson layoutJson) {
        if (layoutJson.getMainExteriorInteriorRoadPolygon() != null) {
            for (LayoutJsonMainExteriorInteriorRoadPolygonInner road : layoutJson.getMainExteriorInteriorRoadPolygon()) {
                road.setExterior(forceClockwise(road.getExterior()));
                road.setInterior(forceCounterClockwise(road.getInterior()));
            }
        }
        if (layoutJson.getMajorExteriorInteriorRoadPolygon() != null) {
            for (LayoutJsonMajorExteriorInteriorRoadPolygonInner road : layoutJson.getMajorExteriorInteriorRoadPolygon()) {
                road.setExterior(forceClockwise(road.getExterior()));
                road.setInterior(forceCounterClockwise(road.getInterior()));
            }
        }
        if (layoutJson.getMinorExteriorInteriorRoadPolygon() != null) {
            for (LayoutJsonMinorExteriorInteriorRoadPolygonInner road : layoutJson.getMinorExteriorInteriorRoadPolygon()) {
                road.setExterior(forceClockwise(road.getExterior()));
                road.setInterior(forceCounterClockwise(road.getInterior()));
            }
        }
        return layoutJson;
    }

    @Override
    public String readLayoutJsonContent(Long layoutId) {
        Layouts layout = this.getById(layoutId);
        if (layout == null) {
            throw new RuntimeException("未找到对应布局");
        }
        String jsonPath = layout.getSvgUrl(); // 假设 svgUrl 字段存储 JSON 相对路径
        try {
            return fileUtil.readFile(jsonPath);
        } catch (IOException e) {
            throw new RuntimeException("读取布局 JSON 文件失败", e);
        }
    }

    @Override
    public String readSvgContent(String svgUrl) {
        try {
            return fileUtil.readFile(svgUrl);
        } catch (IOException e) {
            throw new RuntimeException("读取 SVG 文件失败", e);
        }
    }

    @Override
    public List<LayoutsListItem> listUserLayouts(Long userId) {
        List<Layouts> layouts = this.lambdaQuery()
            .eq(Layouts::getUserId, userId)
            .ne(Layouts::getStatus, -1) // 过滤掉已逻辑删除的布局
            .list();
        return layouts.stream().map(layout -> {
            LayoutsListItem dto = new LayoutsListItem();
            dto.setLayoutId(Base62Util.encode(layout.getId())); // base62编码
            dto.setSvgUrl(layout.getSvgUrl());
            dto.setStatus(layout.getStatus());
            dto.setLayoutName(layout.getLayoutName());
            // 可补充更多字段
            return dto;
        }).collect(Collectors.toList());
    }
}
