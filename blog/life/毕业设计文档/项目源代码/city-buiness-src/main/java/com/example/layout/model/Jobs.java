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
public class Jobs implements Serializable {

    private static final long serialVersionUID = 1L;

    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    private LocalDateTime createdAt;

    private String payloadJson;

    private String resultJson;

    private Integer status;

    private String type;

    private LocalDateTime updatedAt;

    private Long userId;

    /**
     * 任务唯一ID
     */
    private String taskId;

    /**
     * 布局ID
     */
    private Long layoutId;
}
