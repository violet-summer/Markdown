package com.example.layout.model;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import java.io.Serializable;
import java.time.LocalDateTime;
import lombok.Getter;
import lombok.Setter;

/**
 * <p>
 * 
 * </p>
 *
 * @author city_business
 * @since 2026-02-27
 */
@Getter
@Setter
public class Layouts implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private LocalDateTime createdAt;

    private String paramsJson;

    private Integer status;

    private String svgUrl;

    private LocalDateTime updatedAt;

    private Long userId;

    private String layoutName;
}
