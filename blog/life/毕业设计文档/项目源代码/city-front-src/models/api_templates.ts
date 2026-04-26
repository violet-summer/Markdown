import { LayoutParams } from "@/models/layout-generate-request";

// 集中管理所有接口的模板对象

// 布局生成接口模板
export const templateParams: LayoutParams = {
  world_dimensions: { x: 100, y: 100 },
  origin: { x: 0, y: 0 },
  zoom: 0.1,
  tensor_field: {
    smooth: true,
    set_recommended: true,
    grids: [
      { x: 10, y: 5, size: 16, decay: 2, theta: 59 },
      { x: 24, y: 12, size: 12, decay: 2, theta: 89 },
      { x: 24, y: 5, size: 12, decay: 2, theta: 28 },
    ],
    radials: [{ x: 50, y: 50, size: 15, decay: 0 }],
  },
  map: {
    animate: true,
    animate_speed: 10,
    water: {
      river_bank_size: 0.25,
      river_size: 0.5,
      coastline_width: 2,
      coastline: {
        noise_enabled: true,
        noise_size: 0.5,
        noise_angle: 20,
      },
      river: {
        noise_enabled: true,
        noise_size: 0.5,
        noise_angle: 20,
      },
      simplify_tolerance: 0.125,
      dev_params: {
        dsep: 0.25,
        dtest: 0.25,
        path_iterations: 400,
        seed_tries: 75,
        dstep: 0.25,
        dlookahead: 0.5,
        dcircle_join: 0.25,
        join_angle: 0.1,
      },
    },
    main: {
      dsep: 4,
      dtest: 0.5,
      dev_params: {
        path_iterations: 400,
        seed_tries: 5,
        dstep: 0.25,
        dlookahead: 6.25,
        dcircle_join: 0.25,
        join_angle: 0.1,
        simplify_tolerance: 0.0125,
        collide_early: 0,
      },
    },
    major: {
      dsep: 1.25,
      dtest: 0.5,
      dev_params: {
        path_iterations: 400,
        seed_tries: 5,
        dstep: 0.25,
        dlookahead: 2.5,
        dcircle_join: 0.25,
        join_angle: 0.1,
        simplify_tolerance: 0.0125,
        collide_early: 0,
      },
    },
    minor: {
      dsep: 1.25,
      dtest: 0.25,
      dev_params: {
        path_iterations: 400,
        seed_tries: 5,
        dstep: 0.25,
        dlookahead: 0.5,
        dcircle_join: 0.25,
        join_angle: 0.1,
        simplify_tolerance: 0.0125,
        collide_early: 0,
      },
    },
    parks: {
      cluster_big_parks: true,
      num_big_parks: 1,
      num_small_parks: 0,
    },
    buildings: {
      min_area: 5,
      max_length: 20,
      shrink_spacing: 2,
      chance_no_divide: 0.05,
    },
  },
  style: {
    colour_scheme: "Default",
    zoom_buildings: true,
    building_models: true,
    show_frame: true,
    orthographic: true,
    camera_x: 0,
    camera_y: 0,
  },
  options: {
    draw_center: true,
    high_dpi: true,
  },
  download: {
    image_scale: 1,
    type: "",
  },
  park_polygons: {
    max_length: 0.25,
    min_area: 1,
    shrink_spacing: 0.75,
    chance_no_divide: 1,
  },
};

// 后续其它接口模板对象可继续添加
// export const xxxTemplate = {...}
