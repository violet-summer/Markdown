import logging
import math
import random

import tqdm

from app.services.procgen_python.custom_struct.params import PolygonParams
from app.services.procgen_python.custom_struct.vector import Vector
from .graph import Node
from .polygon_util import PolygonUtil
from .tensor_field import TensorField


class PolygonFinder:
    def __init__(self, nodes: list[Node], params: PolygonParams, tensor_field: TensorField):
        """
        初始化 PolygonFinder 类
        :param nodes: 节点列表
        :param params: 多边形参数，包括 maxLength, minArea, shrinkSpacing, chanceNoDivide
        :param tensor_field: 张量场，用于判断地形
        """
        self.nodes = nodes
        self.params = params
        self.tensor_field = tensor_field
        self.polygons = []
        self._shrunk_polygons = []
        self._divided_polygons = []
        self.to_shrink = []
        self.resolve_shrink = None
        self.to_divide = []
        self.resolve_divide = None
        # self._shrunk_polygons = []
        # self._divided_polygons = []

   
    def get_polygons(self):
        """
        获取多边形列表，优先返回分割后的多边形，其次是收缩后的多边形，最后是原始多边形
        # """
        # if self._divided_polygons:
        #     logging.info(f"返回切分后的多边形")
        #     return self._divided_polygons
        # if self._shrunk_polygons:
        #     logging.info(f"返回收缩后的多边形")
        #     return self._shrunk_polygons
        return self.polygons
    def get_divided_polygons(self):
        """
        获取分割后的多边形列表
        :return: 分割后的多边形列表
        """
        return self._divided_polygons
    def get_shrunk_polygons(self):
        """
        获取收缩后的多边形列表
        :return: 收缩后的多边形列表
        """
        return self._shrunk_polygons
    def reset(self):
        """
        重置所有多边形数据
        """
        self.to_shrink = []
        self.to_divide = []
        self.polygons = []
        self._shrunk_polygons = []
        self._divided_polygons = []

    def update(self):
        """
        更新收缩和分割操作
        :return: 是否有变化
        """
        change = False
        if self.to_shrink:
            resolve = len(self.to_shrink) == 1
            if self.step_shrink(self.to_shrink.pop()):
                change = True
            if resolve and self.resolve_shrink:
                self.resolve_shrink()

        if self.to_divide:
            resolve = len(self.to_divide) == 1
            if self.step_divide(self.to_divide.pop()):
                change = True
            if resolve and self.resolve_divide:
                self.resolve_divide()

        return change

    def shrink(self, animate=False):
        """
        收缩多边形
        :param animate: 是否启用动画
        """
        if not self.polygons:
            self.find_polygons()

        if animate:
            if not self.polygons:
                return
            self.to_shrink = self.polygons[:]
        else:
            self._shrunk_polygons = []
            for polygon in self.polygons:
                self.step_shrink(polygon)

    def step_shrink(self, polygon):
        """
        收缩单个多边形
        :param polygon: 多边形顶点列表
        :return: 是否成功收缩
        """
        shrunk = PolygonUtil.resize_geometry(polygon, -self.params.shrink_spacing)
        if shrunk:
            self._shrunk_polygons.append(shrunk)
            return True
        return False

    def divide(self, animate=False):
        from tqdm import tqdm
        """
        分割多边形
        :param animate: 是否启用动画
        """
        if not self.polygons:
            self.find_polygons()

        polygons = self._shrunk_polygons.copy() if self._shrunk_polygons else self.polygons.copy()

        if animate:
            if not polygons:
                return
            self.to_divide = polygons[:].copy()
        else:
            self._divided_polygons = []
            polygons = self._shrunk_polygons.copy() if self._shrunk_polygons else self.polygons.copy()
            for polygon in tqdm(polygons, desc="Dividing polygons"):
                self.step_divide(polygon)

    def step_divide(self, polygon):
        """
        分割单个多边形
        :param polygon: 多边形顶点列表
        :return: 是否成功分割
        """
        if self.params.chance_no_divide > 0 and random.random() < self.params.chance_no_divide:
            self._divided_polygons.append(polygon)
            return True

        divided = PolygonUtil.subdivide_polygon(polygon, self.params.min_area)
        if divided:
            self._divided_polygons.extend(divided)
            return True
        return False

    def find_polygons(self):
        """
        查找多边形
        """
        
        polygons = []

        # replace lines 147 to 156

        from tqdm import tqdm
        import logging

        # logging.basicConfig(level=logging.INFO)
        # 这里只限制最大长度，不限制最小面积，最小面积限制用于递归切分
        for node in tqdm(self.nodes, desc="Processing nodes"):
            try:
                if len(node.adj) < 2:
                    continue
                for next_node in node.adj:
                    polygon = self.recursive_walk([node, next_node])
                    if polygon and len(polygon) < self.params.max_length:
                        self.remove_polygon_adjacencies(polygon)
                        polygons.append([n.value.clone() for n in polygon])
            except Exception as e:
                logging.error(f"Error processing node {node}: {e}")

        self.polygons = self.filter_polygons_by_water(polygons)

        # self._polygons = self.filter_polygons_by_water(polygons)

   
    def is_polygon_in_river(self,polygon:list[Vector])-> bool:
        """
        使用 Shapely 检查一个多边形是否与任何河流/水域多边形相交。
        :param polygon: 待检查的多边形（一个 Vector 点列表）
        :return: 如果相交则返回 True，否则返回 False
        """
        from shapely.geometry import Polygon
        import logging

        # 1. 检查输入多边形是否有效，并创建 Shapely 对象
        try:
            if len(polygon) < 3:
                return False # 点或线无法构成有效的区域
            test_poly = Polygon([(p.x, p.y) for p in polygon])
            if not test_poly.is_valid:
                test_poly = test_poly.buffer(0) # 尝试修复
                if not test_poly.is_valid:
                    return False # 无法处理无效的多边形
        except Exception as e:
            logging.warning(f"创建测试多边形时出错: {e}")
            return False

        # 2. 获取水域多边形列表
        #    假设水域数据存储在 self.tensor_field.river
        river_polygon =self.tensor_field.river
        if not river_polygon:
            return False # 没有水域可以相交

        # 3. 遍历所有水域，检查相交情况
        
        try:
           
            river_poly = Polygon([(p.x, p.y) for p in river_polygon])
            
            # 检查相交
            if river_poly.is_valid and test_poly.intersects(river_poly):
                return True # 发现相交，立即返回 True
        except Exception as e:
            logging.warning(f"处理水域几何图形时出错: {e}")
            

        # 4. 如果没有发现任何相交，则返回 False
        return False
    
    
    
    def filter_polygons_by_water(self, polygons):
        """
        过滤掉水域中的多边形
        :param polygons: 多边形列表
        :return: 过滤后的多边形列表
        """
        out = []
        for polygon in polygons:
            average_point = PolygonUtil.average_point(polygon)
            # logging.info("进行是否位于水域的测验")
            is_onland = self.tensor_field.on_land(average_point)
            is_on_river = self.is_polygon_in_river(polygon)
            is_inparks = self.tensor_field.in_parks(average_point)
            if is_onland and not is_inparks and not is_on_river:
                out.append(polygon)
        return out

    @staticmethod
    def remove_polygon_adjacencies(polygon):
        """
        移除多边形的邻接关系
        :param polygon: 多边形节点列表
        """
        for i in range(len(polygon)):
            current = polygon[i]
            next_node = polygon[(i + 1) % len(polygon)]

            if next_node in current.adj:
                current.adj.remove(next_node)
            else:
                print("PolygonFinder - node not in adj")

    def recursive_walk(self, visited, count=0):
        """
        递归遍历节点以查找多边形
        :param visited: 已访问的节点列表
        :param count: 当前递归深度
        :return: 多边形节点列表或 None
        """
        if count >= self.params.max_length:
            return None

        next_node = self.get_rightmost_node(visited[-2], visited[-1])
        if not next_node:
            return None

        if next_node in visited:
            return visited[visited.index(next_node):]
        else:
            visited.append(next_node)
            return self.recursive_walk(visited, count + 1)

    @staticmethod
    def get_rightmost_node(node_from, node_to):
        """
        获取右转方向的下一个节点
        :param node_from: 当前节点
        :param node_to: 下一个节点
        :return: 右转方向的节点
        """
        if not node_to.adj:
            return None

        backwards_diff = node_from.value.clone().sub(node_to.value)
        transform_angle = math.atan2(backwards_diff.y, backwards_diff.x)

        rightmost_node = None
        smallest_theta = math.pi * 2

        for next_node in node_to.adj:
            if next_node != node_from:
                next_vector = next_node.value.clone().sub(node_to.value)
                next_angle = math.atan2(next_vector.y, next_vector.x) - transform_angle
                if next_angle < 0:
                    next_angle += math.pi * 2

                if next_angle < smallest_theta:
                    smallest_theta = next_angle
                    rightmost_node = next_node

        return rightmost_node
