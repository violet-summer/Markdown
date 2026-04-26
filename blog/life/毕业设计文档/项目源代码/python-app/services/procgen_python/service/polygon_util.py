import logging
import random
from matplotlib import pyplot as plt
import open3d as o3d
from shapely import Point
import triangle as tr
from typing import List
import numpy as np
import trimesh
from shapely.geometry import Polygon, LineString
from shapely.ops import split, polygonize

from app.services.procgen_python.custom_struct import Vector


# 配置日志
# log = logging.getLogger(__name__)

class ExteriorInteriorPolygon:
    def __init__(self, exterior: List[Vector], interior: List[Vector]):
        self.exterior = exterior
        self.interior = interior

class PolygonUtil:
    """多边形工具类，提供多种几何操作方法"""

    @staticmethod
    def slice_rectangle(origin: Vector, world_dimensions: Vector, p1: Vector, p2: Vector) -> List[Vector]:
        """
        切割矩形，返回最小的多边形
        :param origin: 矩形的起点
        :param world_dimensions: 矩形的宽高
        :param p1: 切割线的起点
        :param p2: 切割线的终点
        :return: 最小多边形的顶点数组
        """
        rectangle = Polygon([
            (origin.x, origin.y),
            (origin.x + world_dimensions.x, origin.y),
            (origin.x + world_dimensions.x, origin.y + world_dimensions.y),
            (origin.x, origin.y + world_dimensions.y)
        ])
        line = LineString([(p1.x, p1.y), (p2.x, p2.y)])
        try:
            result = split(rectangle, line)
            # 使用 shapely 的面积计算直接排序
            smallest_polygon = min(result.geoms, key=lambda poly: poly.area)
            return PolygonUtil._shapely_to_vectors(smallest_polygon)
        except Exception as e:
            logging.error(f"切割矩形失败: {e}")
            return []

    @staticmethod
    def subdivide_polygon(p: List[Vector], min_area: float, max_depth: int = 20, current_depth: int = 0) -> List[List[Vector]]:
        """
        递归地将多边形按最长边分割，直到满足最小面积条件
        :param p: 多边形顶点数组
        :param min_area: 最小面积
        :param max_depth: 最大递归深度（防止卡死）
        :param current_depth: 当前递归深度
        :return: 分割后的多边形数组
        """
        # 防止递归过深导致卡死
        if current_depth >= max_depth:
            logging.warning(f"达到最大递归深度 {max_depth}，停止分割")
            return [p]
        
        polygon = Polygon([(v.x, v.y) for v in p])
        area = polygon.area
        if area < 0.5 * min_area:
            return []

        # 计算多边形的边界和最长边
        edges = list(zip(p, p[1:] + [p[0]]))
        longest_side = max(edges, key=lambda edge: LineString([(edge[0].x, edge[0].y), (edge[1].x, edge[1].y)]).length)
        # 直接省略，使用lambda函数进行edges长度比较即可
        # longest_side_length = LineString([(longest_side[0].x, longest_side[0].y),
        #                                   (longest_side[1].x, longest_side[1].y)]).length

        # 形状指数
        perimeter = polygon.length
        if area / (perimeter ** 2) < 0.04:
            return []

        if area < 2 * min_area:
            return [p]

        # 偏移量在 0.4 到 0.6 之间
        deviation = random.uniform(0.4, 0.6)
        average_point = longest_side[0].clone().add(longest_side[1]).multiply_scalar(deviation)
        difference_vector = longest_side[0].clone().sub(longest_side[1])
        perp_vector = Vector(difference_vector.y, -difference_vector.x).normalize().multiply_scalar(100)

        bisect = [average_point.clone().add(perp_vector), average_point.clone().sub(perp_vector)]

        try:
            line = LineString([(bisect[0].x, bisect[0].y), (bisect[1].x, bisect[1].y)])
            result = split(polygon, line)
            divided = []
            for poly in result.geoms:
                divided.extend(PolygonUtil.subdivide_polygon(
                    PolygonUtil._shapely_to_vectors(poly), 
                    min_area,
                    max_depth,
                    current_depth + 1
                ))
            return divided
        except Exception as e:
            logging.error(f"分割多边形失败: {e}")
            return []

    @staticmethod
    def resize_geometry(geometry: List[Vector], spacing: float, is_polygon: bool = True) -> List[Vector]:
        """
        缩放多边形
        :param geometry: 多边形顶点数组
        :param spacing: 缩放距离
        :param is_polygon: 是否为多边形
        :return: 缩放后的多边形顶点数组
        """
        try:
            if not geometry:
                logging.warning("几何体为空，无法缩放")
                logging.exception("几何体为空，无法缩放")
            shapely_geometry = Polygon([(v.x, v.y) for v in geometry]) if is_polygon else LineString([(v.x, v.y) for v in geometry])
            resized = shapely_geometry.buffer(spacing, cap_style="flat")  # CAP_FLAT = "flat"
            if not resized.is_simple:
                return []
            return [Vector(coord[0], coord[1]) for coord in resized.exterior.coords[:-1]]
        
        except Exception as e:
            logging.error(f"缩放几何失败: {e}")
            return []


    # @staticmethod
    # def resize_geometry_closed(geometry: List[Vector], spacing: float) -> ExteriorInteriorPolygon:
    #     """
    #     缩放道路几何
    #     :param geometry: 道路几何顶点数组
    #     :param spacing: 缩放距离
    #     :return: 缩放后的多边形顶点数组
    #     """
    #     try:
    #         if not geometry:
    #             logging.warning("几何体为空，无法缩放")
    #             logging.exception("几何体为空，无法缩放")
    #             return []
            
    #         # 检查是否为闭合曲线
    #         is_closed = False
    #         if len(geometry) > 2 and geometry[0].equals(geometry[-1]):
    #             print("闭合曲线")
    #             is_closed = True
            
    #         # 根据是否闭合选择不同的处理方式
    #         if is_closed:
    #             # 如果是闭合线段，则使用 buffer 方法创建圆环
    #             shapely_geometry = LineString([(v.x, v.y) for v in geometry])
    #             resized = shapely_geometry.buffer(spacing, cap_style="round")  # CAP_ROUND = "round"
    #             resized = resized.difference(shapely_geometry)
    #         else:
    #             # 如果是普通线段，则使用 buffer 方法创建胶囊
    #             shapely_geometry = LineString([(v.x, v.y) for v in geometry])
    #             resized = shapely_geometry.buffer(spacing, cap_style="round")  # CAP_ROUND = "round"
            
    #         if not resized.is_simple:
    #             logging.warning("缩放后的几何体不是简单几何体，返回空列表")
    #             return []
            
    #         # 提取所有多边形的顶点
    #         vectors = []
    #         if hasattr(resized, 'geoms'):
    #             # 如果 resized 是一个 GeometryCollection，则遍历所有几何对象
    #             for geom in resized.geoms:
    #                 if hasattr(geom, 'exterior') and geom.exterior is not None:
    #                     vectors.extend([Vector(coord[0], coord[1]) for coord in geom.exterior.coords[:-1]])
    #                 if hasattr(geom, 'interiors'):
    #                     for interior in geom.interiors:
    #                         vectors.extend([Vector(coord[0], coord[1]) for coord in interior.coords[:-1]])
    #         elif hasattr(resized, 'exterior') and resized.exterior is not None:
    #             # 如果 resized 是一个单独的多边形，则直接提取顶点
    #             vectors = [Vector(coord[0], coord[1]) for coord in resized.exterior.coords[:-1]]
    #             if hasattr(resized, 'interiors'):
    #                 for interior in resized.interiors:
    #                     vectors.extend([Vector(coord[0], coord[1]) for coord in interior.coords[:-1]])
            
            
    #         # 可视化结果
    #         if is_closed:
    #             # 提取外环和内环的坐标
    #             if hasattr(resized, 'exterior'):
    #                 exterior_coords = list(resized.exterior.coords)
    #             else:
    #                 exterior_coords = []
                
    #             if hasattr(resized, 'interiors') and resized.interiors:
    #                 interior_coords = []
    #                 for interior in resized.interiors:
    #                     interior_coords.extend(list(interior.coords))
    #             else:
    #                 interior_coords = []

    #             # 绘制外环
    #             if exterior_coords:
    #                 x_ext, y_ext = zip(*exterior_coords)
    #                 plt.plot(x_ext, y_ext, color='blue', label='Outer Ring')

    #             # 绘制内环
    #             if interior_coords:
    #                 x_int, y_int = zip(*interior_coords)
    #                 plt.plot(x_int, y_int, color='red', label='Inner Ring')

    #             # 设置图形属性
    #             plt.xlabel('X')
    #             plt.ylabel('Y')
    #             plt.title('Resized Closed LineString (Annulus)')
    #             plt.axis('equal')
    #             plt.legend()

    #             # 显示图形
    #             plt.show()
            
    #         return vectors
    #     except Exception as e:
    #         logging.error(f"缩放几何失败: {e}")
    #         return []    @staticmethod
    # def exterior_interior_polygon_to_mesh(exterior_interior_polygon: ExteriorInteriorPolygon, top: float, bottom: float = 0) -> o3d.geometry.TriangleMesh:
    #     """
    #     将一个带内外环的多边形数据挤出为3D网格。
    #     此函数处理一个外环和一个内环的圆环多边形。
    #     :param exterior_interior_polygon: 包含外环和内环的多边形对象
    #     :param top: 顶部高度
    #     :param bottom: 底部高度
    #     :return: Open3D 的 TriangleMesh 对象
    #     """
    #     logging.info(f"开始构建带内外环的多边形网格 - top: {top}, bottom: {bottom}")
        
    #     exterior = exterior_interior_polygon.exterior
    #     interior = exterior_interior_polygon.interior  
        
    #     logging.info(f"外环顶点数: {len(exterior) if exterior else 0}")
    #     logging.info(f"内环顶点数: {len(interior) if interior else 0}")

    #     if not exterior or len(exterior) < 3:
    #         logging.error("外环无效：顶点数少于3个或为空")
    #         return o3d.geometry.TriangleMesh()

    #     # --- 1. 准备三角剖分所需的所有顶点、段和孔 ---
    #     all_points_2d = []
    #     all_segments = []
    #     holes = []
        
    #     # 添加外环数据
    #     ext_points = exterior[:-1] if len(exterior) > 0 and exterior[0].equals(exterior[-1]) else exterior
    #     logging.info(f"处理后的外环顶点数: {len(ext_points)}")
        
    #     start_idx = len(all_points_2d)
    #     all_points_2d.extend([(p.x, p.y) for p in ext_points])
    #     for i in range(len(ext_points)):
    #         all_segments.append([start_idx + i, start_idx + (i + 1) % len(ext_points)])
        
    #     logging.info(f"外环添加完成 - 总顶点数: {len(all_points_2d)}, 总段数: {len(all_segments)}")

    #     # 添加内环数据（单个内环）
    #     interior_points = None
    #     if interior and len(interior) >= 3:
    #         int_points = interior[:-1] if interior[0].equals(interior[-1]) else interior
    #         interior_points = int_points
    #         logging.info(f"内环顶点数: {len(int_points)}")

    #         # 为孔洞找一个内部点，这是triangle库识别孔洞的方式
    #         try:
    #             shapely_interior = Polygon([(p.x, p.y) for p in int_points])
    #             hole_point = list(shapely_interior.representative_point().coords)[0]
    #             holes.append(hole_point)
    #             logging.info(f"内环孔洞点: {hole_point}")
    #         except Exception as e:
    #             logging.error(f"内环创建孔洞点失败: {e}")
    #             interior_points = None

    #         if interior_points:
    #             start_idx = len(all_points_2d)
    #             all_points_2d.extend([(p.x, p.y) for p in int_points])
    #             for i in range(len(int_points)):
    #                 all_segments.append([start_idx + i, start_idx + (i + 1) % len(int_points)])
                
    #             logging.info(f"内环添加完成 - 当前总顶点数: {len(all_points_2d)}, 总段数: {len(all_segments)}")
    #     else:
    #         logging.info("没有有效的内环")

    #     if not all_points_2d:
    #         logging.error("所有顶点数据为空")
    #         return o3d.geometry.TriangleMesh()

    #     logging.info(f"三角剖分输入准备完成 - 顶点数: {len(all_points_2d)}, 段数: {len(all_segments)}, 孔洞数: {len(holes)}")

    #     # --- 2. 执行带孔洞的三角剖分 ---
    #     tri_input = {'vertices': np.array(all_points_2d), 'segments': np.array(all_segments)}
    #     if holes:
    #         tri_input['holes'] = np.array(holes)
        
    #     try:
    #         # 'p' 用于处理PSLG（平面直线图），'q'用于保证质量
    #         triangulation = tr.triangulate(tri_input, 'pq')
    #         triangle_count = len(triangulation['triangles']) if 'triangles' in triangulation else 0
    #         logging.info(f"三角剖分成功 - 生成三角形数: {triangle_count}")
    #     except Exception as e:
    #         logging.error(f"带孔三角剖分失败: {e}")
    #         logging.error(f"输入数据: 顶点数={len(all_points_2d)}, 段数={len(all_segments)}, 孔洞数={len(holes)}")
    #         return o3d.geometry.TriangleMesh()

    #     # --- 3. 创建3D顶点和顶/底面 ---
    #     vertices_3d = []
    #     for p in all_points_2d:
    #         vertices_3d.append([p[0], p[1], bottom]) # 使用z轴作为高度
        
    #     offset = len(all_points_2d)
    #     for p in all_points_2d:
    #         vertices_3d.append([p[0], p[1], top])

    #     logging.info(f"3D顶点创建完成 - 总顶点数: {len(vertices_3d)} (底面: {offset}, 顶面: {offset})")

    #     faces = []
    #     # 添加底面和顶面
    #     for tri in triangulation['triangles']:
    #         faces.append([tri[0], tri[1], tri[2]]) # 底面
    #         faces.append([offset + tri[0], offset + tri[2], offset + tri[1]]) # 顶面，反转顺序

    #     logging.info(f"底面和顶面创建完成 - 当前面数: {len(faces)}")

    #     # --- 4. 创建侧面 ---
    #     # 外环侧面 (法线朝外)
    #     n_ext = len(ext_points)
    #     for i in range(n_ext):
    #         curr = i
    #         next = (i + 1) % n_ext
    #         faces.append([curr, next, offset + curr])
    #         faces.append([next, offset + next, offset + curr])

    #     logging.info(f"外环侧面创建完成 - 当前面数: {len(faces)}")

    #     # 内环侧面 (法线朝内) - 处理单个内环
    #     if interior_points:
    #         n_int = len(interior_points)
    #         current_vtx_idx_start = n_ext  # 内环顶点在外环顶点之后
    #         logging.info(f"处理内环侧面 - 顶点数: {n_int}, 起始索引: {current_vtx_idx_start}")
            
    #         for i in range(n_int):
    #             # 反转顶点顺序以使法线朝向孔洞内部
    #             curr = current_vtx_idx_start + i
    #             next = current_vtx_idx_start + (i + 1) % n_int
    #             faces.append([curr, offset + curr, next])
    #             faces.append([next, offset + curr, offset + next])

    #     logging.info(f"所有侧面创建完成 - 总面数: {len(faces)}")

    #     try:
    #         mesh = o3d.geometry.TriangleMesh()
    #         mesh.vertices = o3d.utility.Vector3dVector(np.array(vertices_3d))
    #         mesh.triangles = o3d.utility.Vector3iVector(np.array(faces))
    #         mesh.compute_vertex_normals()
    #         logging.info(f"网格创建成功 - 顶点数: {len(mesh.vertices)}, 面数: {len(mesh.triangles)}")
            
    #         # 详细检查网格有效性
    #         if mesh.is_empty():
    #             logging.error("生成的网格为空")
    #             return o3d.geometry.TriangleMesh()
            
    #         # 检查网格完整性
    #         is_watertight = mesh.is_watertight()
    #         is_orientable = mesh.is_orientable()
    #         is_edge_manifold = mesh.is_edge_manifold()
    #         is_vertex_manifold = mesh.is_vertex_manifold()
            
    #         logging.info(f"网格完整性检查:")
    #         logging.info(f"  - 水密性 (watertight): {is_watertight}")
    #         logging.info(f"  - 可定向 (orientable): {is_orientable}")
    #         logging.info(f"  - 边流形 (edge_manifold): {is_edge_manifold}")
    #         logging.info(f"  - 顶点流形 (vertex_manifold): {is_vertex_manifold}")
            
    #         # 获取网格的边界边数量
    #         boundary_edges = mesh.get_non_manifold_edges()
    #         logging.info(f"  - 非流形边数量: {len(boundary_edges)}")
            
    #         if not is_watertight:
    #             logging.warning("网格不是水密的，可能存在以下问题:")
    #             if not is_edge_manifold:
    #                 logging.warning("  - 存在非流形边（边被超过2个面共享）")
    #             if not is_vertex_manifold:
    #                 logging.warning("  - 存在非流形顶点")
    #             if len(boundary_edges) > 0:
    #                 logging.warning(f"  - 存在 {len(boundary_edges)} 条边界边（开放的边）")
                
    #             # 尝试修复网格
    #             logging.info("尝试修复网格...")
    #             mesh.remove_duplicated_vertices()
    #             mesh.remove_duplicated_triangles()
    #             mesh.remove_degenerate_triangles()
    #             mesh.remove_unreferenced_vertices()
                
    #             # 重新检查
    #             is_watertight_after = mesh.is_watertight()
    #             logging.info(f"修复后网格水密性: {is_watertight_after}")
                
    #             if not is_watertight_after:
    #                 logging.warning("网格修复失败，但将继续使用当前网格")
    #         else:
    #             logging.info("网格检查通过 - 水密性良好")
            
    #         # 显示网格统计信息
    #         bbox = mesh.get_axis_aligned_bounding_box()
    #         logging.info(f"网格边界框: min={bbox.min_bound}, max={bbox.max_bound}")
    #         logging.info(f"网格体积: {mesh.get_volume():.6f}")
    #         logging.info(f"网格表面积: {mesh.get_surface_area():.6f}")
            
    #         # 可视化网格
    #         o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True, mesh_show_wireframe=True)
    #         return mesh
            
    #     except Exception as e:
    #         logging.error(f"网格创建失败: {e}")
    #         logging.error(f"顶点数据形状: {np.array(vertices_3d).shape}")
    #         logging.error(f"面数据形状: {np.array(faces).shape}")
            
    #         # 检查面数据的有效性
    #         face_array = np.array(faces)
    #         if len(face_array) > 0:
    #             max_vertex_index = np.max(face_array)
    #             logging.error(f"面数据中最大顶点索引: {max_vertex_index}, 总顶点数: {len(vertices_3d)}")
    #             if max_vertex_index >= len(vertices_3d):
    #                 logging.error("面数据中存在超出顶点范围的索引！")
            
    #         return o3d.geometry.TriangleMesh()
    # 
   


    @staticmethod
    def exterior_interior_polygon_to_mesh(exterior_interior_polygon: ExteriorInteriorPolygon, top: float, bottom: float = 0) -> o3d.geometry.TriangleMesh:
        """
        将一个带内外环的多边形数据挤出为3D网格。
        简化版本：直接处理外环和内环，无需复杂的三角剖分。
        :param exterior_interior_polygon: 包含外环和内环的多边形对象
        :param top: 顶部高度
        :param bottom: 底部高度
        :return: Open3D 的 TriangleMesh 对象
        """
        logging.info(f"开始构建带内外环的多边形网格 - top: {top}, bottom: {bottom}")
        
        exterior = exterior_interior_polygon.exterior
        interior = exterior_interior_polygon.interior
        
        if not exterior or len(exterior) < 3:
            logging.error("外环无效：顶点数少于3个或为空")
            return o3d.geometry.TriangleMesh()
        if not interior or len(interior) < 3:
            logging.warning("内环无效或顶点数少于3个，将只处理外环。")
            return PolygonUtil.polygon_to_mesh(exterior, top, bottom, True)

        # --- 1. 准备顶点 ---
        ext_points = exterior[:-1] if exterior[0].equals(exterior[-1]) else exterior
        int_points = interior[:-1] if interior[0].equals(interior[-1]) else interior
        
        n_ext = len(ext_points)
        n_int = len(int_points)

        if n_ext == 0 or n_int == 0:
            logging.error("处理后外环或内环顶点为空")
            return o3d.geometry.TriangleMesh()

        # 使用 triangle 库进行高质量的带孔三角剖分
        all_points_2d = [(p.x, p.y) for p in ext_points] + [(p.x, p.y) for p in int_points]
        segments = []
        # 外环段
        for i in range(n_ext):
            segments.append([i, (i + 1) % n_ext])
        # 内环段
        for i in range(n_int):
            segments.append([n_ext + i, n_ext + (i + 1) % n_int])

        try:
            shapely_interior = Polygon([(p.x, p.y) for p in int_points])
            hole_point = list(shapely_interior.representative_point().coords)[0]
        except Exception as e:
            logging.error(f"无法计算内环孔洞点: {e}")
            return o3d.geometry.TriangleMesh()

        tri_input = {'vertices': np.array(all_points_2d), 'segments': np.array(segments), 'holes': np.array([hole_point])}
        
        try:
            triangulation = tr.triangulate(tri_input, 'p')
        except Exception as e:
            logging.error(f"带孔三角剖分失败: {e}")
            return o3d.geometry.TriangleMesh()

        # --- 2. 创建3D顶点和面 ---
        vertices_3d = []
        for p in all_points_2d:
            vertices_3d.append([p[0], bottom,p[1]])
        offset = len(all_points_2d)
        for p in all_points_2d:
            vertices_3d.append([p[0], top, p[1]])

        faces = []
        # 底面和顶面
        for tri in triangulation['triangles']:
            faces.append([tri[0], tri[1], tri[2]])
            faces.append([offset + tri[0], offset + tri[2], offset + tri[1]])

        # 外环侧面
        for i in range(n_ext):
            curr, next = i, (i + 1) % n_ext
            faces.append([curr, next, offset + curr])
            faces.append([next, offset + next, offset + curr])

        # 内环侧面
        for i in range(n_int):
            curr, next = n_ext + i, n_ext + (i + 1) % n_int
            faces.append([curr, offset + curr, next])
            faces.append([next, offset + curr, offset + next])

        # --- 3. 创建网格 ---
        try:
            mesh = o3d.geometry.TriangleMesh()
            mesh.vertices = o3d.utility.Vector3dVector(np.array(vertices_3d))
            mesh.triangles = o3d.utility.Vector3iVector(np.array(faces))
            mesh.compute_vertex_normals()
            
            if not mesh.is_watertight():
                logging.warning("生成的圆环网格不是水密的，可能在几何连接处存在问题。")

            logging.info(f"圆环网格创建成功 - 顶点数: {len(mesh.vertices)}, 面数: {len(mesh.triangles)}")
            return mesh
            
        except Exception as e:
            logging.error(f"最终网格创建失败: {e}")
            return o3d.geometry.TriangleMesh()


    @staticmethod
    def resize_geometry_closed(geometry: List[Vector], spacing: float) -> ExteriorInteriorPolygon:
        """
        缩放闭合的道路几何，生成一个带内外环的多边形（圆环）。
        对于环形流线，会生成一个外环（外边界）和一个内环（内边界）。
        :param geometry: 道路几何顶点数组 (必须是闭合的)
        :param spacing: 缩放距离
        :return: ExteriorInteriorPolygon 实例，包含一个外环和一个内环
        """
        logging.info(f"开始处理闭合几何体缩放 - 顶点数: {len(geometry)}, spacing: {spacing}")
        
        try:
            # 验证输入是否为有效的闭合曲线
            if not geometry or len(geometry) < 4:
                logging.error(f"输入几何体无效 - 顶点数: {len(geometry) if geometry else 0}")
                return ExteriorInteriorPolygon([], [])
                
            if not geometry[0].equals(geometry[-1]):
                logging.error("输入几何体不是闭合的")
                return ExteriorInteriorPolygon([], [])
            
            logging.info("验证通过：闭合曲线")

            # 创建 Shapely LineString
            shapely_geometry = LineString([(v.x, v.y) for v in geometry])
            logging.info(f"创建LineString成功 - 长度: {shapely_geometry.length:.2f}")
            
            # 对线段进行缓冲，生成圆环
            buffered = shapely_geometry.buffer(spacing, cap_style="round")
            logging.info(f"缓冲处理完成 - 面积: {buffered.area:.2f}")
            
            # 检查缓冲结果
            if buffered.is_empty:
                logging.error("缓冲结果为空")
                return ExteriorInteriorPolygon([], [])
                
            # 处理可能的 MultiPolygon 情况
            if hasattr(buffered, 'geoms'):
                polygons = [p for p in buffered.geoms if isinstance(p, Polygon)]
                if not polygons:
                    logging.error("缓冲结果不包含任何多边形")
                    return ExteriorInteriorPolygon([], [])
                buffered = max(polygons, key=lambda p: p.area)
                logging.info("从MultiPolygon中选择了最大的多边形")

            if not isinstance(buffered, Polygon):
                logging.error(f"缓冲结果不是多边形类型: {type(buffered)}")
                return ExteriorInteriorPolygon([], [])

            # 提取外环
            exterior_vectors = [Vector(coord[0], coord[1]) for coord in buffered.exterior.coords[:-1]]
            logging.info(f"外环提取完成 - 顶点数: {len(exterior_vectors)}")            # 提取内环 - 对于环形流线，应该有一个内环
            interior_vectors = []  # 直接作为单个内环，而不是列表
            if hasattr(buffered, 'interiors') and buffered.interiors:
                if len(buffered.interiors) > 0:
                    # 取一个内环（对于圆环应该只有一个）
                    interior_ring = buffered.interiors[0]
                    interior_vectors = [Vector(coord[0], coord[1]) for coord in interior_ring.coords[:-1]]
                    logging.info(f"内环提取完成 - 顶点数: {len(interior_vectors)}")
                    
                    if len(buffered.interiors) > 1:
                        logging.warning(f"检测到多个内环({len(buffered.interiors)}个)，只使用第一个")
            else:
                logging.warning("缓冲结果没有内环，这对于环形流线来说不正常")

            # 可视化结果
            plt.figure(figsize=(10, 8))
            
            # 绘制原始线段
            original_coords = [(v.x, v.y) for v in geometry]
            if original_coords:
                x_orig, y_orig = zip(*original_coords)
                plt.plot(x_orig, y_orig, color='green', linewidth=2, label='Original LineString')

            # 绘制外环
            if exterior_vectors:
                exterior_coords = [(v.x, v.y) for v in exterior_vectors] + [(exterior_vectors[0].x, exterior_vectors[0].y)]
                x_ext, y_ext = zip(*exterior_coords)
                plt.plot(x_ext, y_ext, color='blue', linewidth=2, label='Outer Ring')

            # 绘制内环
            if interior_vectors:
                interior_coords = [(v.x, v.y) for v in interior_vectors] + [(interior_vectors[0].x, interior_vectors[0].y)]
                x_int, y_int = zip(*interior_coords)
                plt.plot(x_int, y_int, color='red', linewidth=2, label='Inner Ring')

            plt.xlabel('X')
            plt.ylabel('Y')
            plt.title(f'Resized Closed LineString (Annulus) - Spacing: {spacing}')
            plt.axis('equal')
            plt.legend()
            plt.grid(True, alpha=0.3)
            # plt.show()
            
            logging.info(f"成功生成圆环 - 外环顶点数: {len(exterior_vectors)}, 内环顶点数: {len(interior_vectors)}")
            
            # 返回结构化对象 - interior_vectors 直接作为单个内环
            return ExteriorInteriorPolygon(exterior=exterior_vectors, interior=interior_vectors)
        
        except Exception as e:
            logging.error(f"缩放几何失败: {e}")
            logging.exception("详细错误信息:")
            return ExteriorInteriorPolygon([], [])

 
 
    @staticmethod
    def is_closed(polygon: List[Vector]) -> bool:
        """
        检查多边形是否闭合
        :param polygon: 多边形顶点数组
        :return: 如果多边形闭合返回True，否则返回False
        """
        if not polygon:
            return False
        return polygon[0].equals(polygon[-1])

    @staticmethod
    def line_rectangle_polygon_intersection(origin: Vector, world_dimensions: Vector, line: List[Vector]) -> List[Vector]:
        """
        用于创建海洋多边形
        :param origin: 矩形的起点
        :param world_dimensions: 矩形的宽高
        :param line: 切割线
        :return: 相交后的多边形顶点数组
        """
        try:
            # 将线转换为 Shapely 几何对象
            shapely_line = LineString([(v.x, v.y) for v in line])

            # 创建矩形的 Shapely 多边形
            bounds = [
                (origin.x, origin.y),
                (origin.x + world_dimensions.x, origin.y),
                (origin.x + world_dimensions.x, origin.y + world_dimensions.y),
                (origin.x, origin.y + world_dimensions.y),
            ]
            bounding_poly = Polygon(bounds)

            # 合并边界和线
            union = bounding_poly.exterior.union(shapely_line)

            # 创建多边形化器
            polys = list(polygonize(union))

            if not polys:
                return []

            # 找到面积最小的多边形
            smallest_poly = min(polys, key=lambda p: p.area)

            return [Vector(coord[0], coord[1]) for coord in smallest_poly.exterior.coords[:-1]]
        except Exception as e:
            logging.error(f"线与矩形相交失败: {e}")
            return []

    @staticmethod
    def calc_polygon_area(polygon: List[Vector]) -> float:
        """
        计算多边形的面积
        :param polygon: 多边形顶点数组
        :return: 多边形的面积
        """
        total = 0.0

        for i in range(len(polygon)):
            add_x = polygon[i].x
            add_y = polygon[i + 1].y if i < len(polygon) - 1 else polygon[0].y
            sub_x = polygon[i + 1].x if i < len(polygon) - 1 else polygon[0].x
            sub_y = polygon[i].y

            total += (add_x * add_y * 0.5)
            total -= (sub_x * sub_y * 0.5)

        return abs(total)

    @staticmethod
    def average_point(polygon: List[Vector]) -> Vector:
        """
        计算多边形的平均点
        :param polygon: 多边形顶点数组
        :return: 平均点向量
        """
        if not polygon:
            return Vector.zero_vector()

        sum_vector = Vector.zero_vector()
        for v in polygon:
            sum_vector.add(v)

        return sum_vector.divide_scalar(len(polygon))
    # @staticmethod
    # def inside_polygon_original(point: Vector, polygon: List[Vector]) -> bool:
    #     """原始射线法实现（备用）"""
    #     if not polygon:
    #         return False

    #     inside = False
    #     for i in range(len(polygon)):
    #         j = len(polygon) - 1 if i == 0 else i - 1
    #         xi, yi = polygon[i].x, polygon[i].y
    #         xj, yj = polygon[j].x, polygon[j].y
    #         intersect = ((yi > point.y) != (yj > point.y)) and \
    #                     (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi)
    #         if intersect:
    #             inside = not inside
    #     return inside
    # @staticmethod
    # def inside_polygon(point: Vector, polygon: List[Vector]) -> bool:
    #     """
    #     判断点是否在多边形内
    #     :param point: 点
    #     :param polygon: 多边形顶点数组
    #     :return: 如果点在多边形内返回True，否则返回False
    #     """
    #     if not polygon:
    #         return False

    #     inside = False
    #     for i in range(len(polygon)):
    #         j = len(polygon) - 1 if i == 0 else i - 1

    #         xi, yi = polygon[i].x, polygon[i].y
    #         xj, yj = polygon[j].x, polygon[j].y

    #         intersect = ((yi > point.y) != (yj > point.y)) and \
    #                     (point.x < (xj - xi) * (point.y - yi) / (yj - yi) + xi)

    #         if intersect:
    #             inside = not inside

    #     return inside
    @staticmethod
    def inside_polygon(point: Vector, polygon: List[Vector]) -> bool:
        """
        使用Shapely库判断点是否在多边形内（推荐）
        :param point: 点
        :param polygon: 多边形顶点数组
        :return: 如果点在多边形内返回True，否则返回False
        """
        if not polygon or len(polygon) < 3:
            return False
        
        try:
            # 转换为Shapely对象
            shapely_point = Point(point.x, point.y)
            shapely_polygon = Polygon([(v.x, v.y) for v in polygon])
            
            # 检查多边形是否有效
            if not shapely_polygon.is_valid:
                # 尝试修复无效多边形
                shapely_polygon = shapely_polygon.buffer(0)
                # if not shapely_polygon.is_valid:
                #     # 如果还是无效，回退到原始方法
                #     return PolygonUtil.inside_polygon_original(point, polygon)
            
            # 使用contains或intersects（根据需求选择）
            return shapely_polygon.contains(shapely_point) or \
                   shapely_polygon.touches(shapely_point)  # 包含边界点
            
        except Exception as e:
            # 如果Shapely出错，回退到原始方法
            print(f"Shapely处理失败，回退到原始方法: {e}")
            # return PolygonUtil.inside_polygon_original(point, polygon)
    @staticmethod
    def point_in_rectangle(point: Vector, origin: Vector, dimensions: Vector) -> bool:
        """
        判断点是否在矩形内
        :param point: 点
        :param origin: 矩形的起点
        :param dimensions: 矩形的宽高
        :return: 如果点在矩形内返回True，否则返回False
        """
        return (origin.x <= point.x <= origin.x + dimensions.x and
                origin.y <= point.y <= origin.y + dimensions.y)

    @staticmethod
    def _shapely_to_vectors(shapely_geometry) -> List[Vector]:
        """
        将 Shapely 几何对象转换为 Vector 数组
        :param shapely_geometry: Shapely 几何对象
        :return: Vector 数组
        """
        return [Vector(coord[0], coord[1]) for coord in shapely_geometry.exterior.coords[:-1]]

    @staticmethod
    def polygon_to_shape_to_mesh(polygon: list[Vector], height=30,bottom=1):

        """
        将多边形转换为网格，仅处理高度为 0 的情况
        :param polygon: 多边形顶点列表，每个顶点为 (x, y) 元组
        :param height: 挤出高度，默认为 0
        :return: Open3D 的 TriangleMesh 对象
        """

        if len(polygon) < 3:
            raise ValueError("尝试将空多边形导出为网格")

        polygon_2d = [[v.x, v.y] for v in polygon if hasattr(v, 'x') and hasattr(v, 'y')]

        # 创建底面三角形
        base_polygon = trimesh.path.polygons.Polygon(polygon_2d)
        base = trimesh.creation.extrude_polygon(base_polygon, height=height - bottom)
        #网格绕 X 轴旋转 -90 度
        # base.apply_transform(trimesh.transformations.rotation_matrix(
        #     angle=np.radians(90), direction=[1, 0, 0], point=[0, 0, 0]
        # ))
        base.apply_translation([0, 0, bottom])
        base.vertices[:, [1, 2]] = base.vertices[:, [2, 1]]  # 交换 y 和 z 坐标
        return base



    @staticmethod
    def polygon_to_mesh(polygon: List[Vector], top: float, bottom: float = 0,is_closed: bool = False) -> o3d.geometry.TriangleMesh:
        """
        将多边形挤出为 OBJ 网格
        """

        def ensure_clockwise(polygon_points: List[Vector]) -> List[Vector]:
            """
            确保多边形顶点按顺时针顺序排列。
            如果不是顺时针，则反转顶点顺序。
            """

            s_sum = 0
            for i in range(len(polygon_points)):
                current = polygon_points[i]
                next_point = polygon_points[(i + 1) % len(polygon_points)]
                s_sum += (next_point.x - current.x) * (next_point.y + current.y)
            if not s_sum > 0:
                polygon_points.reverse()

            return polygon_points

        if len(polygon) < 3:
            raise ValueError("多边形至少需要三个点")
        # 检查初始点的顺序，确保是顺时针，因为是先生成底部
        polygon = ensure_clockwise(polygon)
        # 创建底面顶点
        vertices = [[v.x, bottom, v.y] for v in polygon]
        # 创建顶面顶点
        top_vertices = [[v.x, top, v.y] for v in polygon]
        vertices.extend(top_vertices)


        points_2d = np.array([[v.x, v.y] for v in polygon])
        segments = [[i, (i + 1) % len(polygon)] for i in range(len(polygon))]  # 定义边界约束
        try:
            triangulation = tr.triangulate({'vertices': points_2d, 'segments': segments}, 'p')
            if 'triangles' not in triangulation:
                raise KeyError("'triangles' key not found in triangulation")
        except Exception as e:
            print(f"Error during triangulation: {e}")
            raise

        faces = []
        # 添加底面三角形
        try:
            for simplex in triangulation['triangles']:
                faces.append([simplex[0], simplex[1], simplex[2]])  # 底面，顺时针
        except KeyError as e:
            print(f"KeyError: {e}. 'triangles' key not found in triangulation")
            raise

        # 添加顶面三角形
        offset = len(points_2d)
        for simplex in triangulation['triangles']:
            faces.append([offset + simplex[0], offset + simplex[2], offset + simplex[1]])  # 顶面，逆时针

        # 创建侧面的三角形
        for i in range(len(polygon)):
            next_i = (i + 1) % len(polygon)
            faces.append([i, next_i, offset + i])  # 侧面三角形 1
            faces.append([offset + i, next_i, offset + next_i])  # 侧面三角形 2
        # if is_closed:
        #     # 添加首尾衔接的三角形
        #     faces.append([len(polygon) - 1, 0, offset + len(polygon) - 1])
        #     faces.append([offset + len(polygon) - 1, 0, offset + 0])
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(faces)
        if is_closed:
            mesh.compute_vertex_normals()
            o3d.visualization.draw_geometries([mesh], mesh_show_back_face=True, mesh_show_wireframe=True)
        return mesh
