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
public class Models implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private LocalDateTime createdAt;

    private String mtlUrl;

    private String objUrl;

    private Integer status;

    private LocalDateTime updatedAt;

    private Long layoutId;

    private Long userId;
}
