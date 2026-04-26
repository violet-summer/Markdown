import logging
from typing import List, Set

import numpy as np
from scipy.spatial import KDTree
from shapely.geometry import LineString, Point

from app.services.procgen_python.custom_struct import Vector


# 自定义向量类，对应原代码中的Vector


# 定义数据类型
class Segment:
    """表示一条线段"""

    def __init__(self, from_vec: Vector, to_vec: Vector):
        self.from_vec = from_vec
        self.to_vec = to_vec


class Intersection:
    """表示两条线段的交点"""

    def __init__(self, point: Vector, segments: List[Segment]):
        self.point = point
        self.segments = segments


class Node:
    """
    位于简化道路多段线上任意交点或点的节点
    """

    def __init__(self, value: Vector, neighbors: Set['Node'] = None):
        self.value = value
        self.segments = set()  # 与节点相关的线段
        self.neighbors = neighbors if neighbors is not None else set()
        self.adj = []  # 邻接节点列表

    def add_segment(self, segment: Segment) -> None:
        """添加与节点关联的线段"""
        self.segments.add(segment)

    def add_neighbor(self, node: 'Node') -> None:
        """添加邻接节点"""
        if node is not self:
            self.neighbors.add(node)
            node.neighbors.add(self)


class Graph:
    """
    从一组流线构建图
    查找所有交点，并创建节点列表
    """

    def __init__(self, streamlines: List[List[Vector]], dstep: float, delete_dangling=False):
        self.nodes = []
        self.intersections = []

        # 将所有流线转换为线段
        print("将所有流线转换为线段")
        segments = self.streamlines_to_segment(streamlines)

        # 计算所有线段的交点
        # print("计算所有线段的交点")
        intersections = self.find_intersections(segments)

        # 创建用于快速查找的KDTree
        nodes = []
        node_add_radius = 0.001

        # 添加所有线段的起点和终点
        # for streamline in streamlines:
        #     for i in range(len(streamline)):
        #         node = Node(streamline[i])
        #         if i > 0:
        #             node.add_segment(self.vectors_to_segment(streamline[i - 1], streamline[i]))
        #
        #         if i < len(streamline) - 1:
        #             node.add_segment(self.vectors_to_segment(streamline[i], streamline[i + 1]))
        #
        #         self.fuzzy_add_to_nodes(nodes, node, node_add_radius)
        from tqdm import tqdm  # 确保导入 tqdm

        # 添加所有线段的起点和终点
        for streamline in tqdm(streamlines, desc="Processing streamlines"):
            for i in range(len(streamline)):
                node = Node(streamline[i])
                if i > 0:
                    node.add_segment(self.vectors_to_segment(streamline[i - 1], streamline[i]))

                if i < len(streamline) - 1:
                    node.add_segment(self.vectors_to_segment(streamline[i], streamline[i + 1]))

                self.fuzzy_add_to_nodes(nodes, node, node_add_radius)
        # for streamline in tqdm(streamlines, desc="Processing streamlines"):
        #     segments = [self.vectors_to_segment(streamline[i], streamline[i + 1]) for i in range(len(streamline) - 1)]
        #     for i, point in enumerate(streamline):
        #         node = Node(point)
        #         if i > 0:
        #             segment = segments[i - 1]
        #             if segment.from_vec.x == segment.to_vec.x and segment.from_vec.y == segment.to_vec.y:
        #                 print(f"起点和终点相同的线段: {segment}")
        #             node.add_segment(segment)
        #         if i < len(streamline) - 1:
        #             segment = segments[i]
        #             if segment.from_vec.x == segment.to_vec.x and segment.from_vec.y == segment.to_vec.y:
        #                 print(f"起点和终点相同的线段: {segment}")
        #             node.add_segment(segment)
        #         self.fuzzy_add_to_nodes(nodes, node, node_add_radius)

        # 添加所有交点
        for intersection in tqdm(intersections,desc="添加所有交点"):
            node = Node(Vector(intersection.point.x, intersection.point.y))
            for s in intersection.segments:
                node.add_segment(s)
            self.fuzzy_add_to_nodes(nodes, node, node_add_radius)

        # 构建KDTree用于空间查询
        if nodes:
            points = np.array([[n.value.x, n.value.y] for n in nodes])
            kdtree = KDTree(points)

            # 对于每条简化的流线，沿着流线构建有序节点列表
            for streamline in tqdm(streamlines,desc="沿着流线构建有序节点列表"):
                for i in range(len(streamline) - 1):
                    segment = self.vectors_to_segment(streamline[i], streamline[i + 1])
                    nodes_along_segment = self.get_nodes_along_segment(
                        segment, nodes, kdtree, node_add_radius, dstep
                    )

                    if len(nodes_along_segment) > 1:
                        for j in range(len(nodes_along_segment) - 1):
                            nodes_along_segment[j].add_neighbor(nodes_along_segment[j + 1])
                    else:
                        logging.error("错误: 线段节点数少于2个")

            # 处理悬挂节点
            if delete_dangling:
                i = 0
                while i < len(nodes):
                    if self.delete_dangling_nodes(nodes[i], nodes):
                        continue  # 如果节点被删除，不增加索引
                    i += 1

            # 设置邻接列表
            for n in nodes:
                n.adj = list(n.neighbors)

            self.nodes = nodes
            self.intersections = [Vector(i.point.x, i.point.y) for i in intersections]

    @staticmethod
    def find_intersections(segments: List[Segment]) -> List[Intersection]:
        """使用shapely库查找线段的交点"""
        intersections = []
        # 创建所有线段的字典，便于后续查找
        lines = {}
        from tqdm import tqdm  # 确保导入 tqdm

        for i, segment in tqdm(enumerate(segments), desc="Processing segments", total=len(segments)):
            line = LineString([
                (segment.from_vec.x, segment.from_vec.y),
                (segment.to_vec.x, segment.to_vec.y)
            ])
            lines[i] = (line, segment)

        from rtree import index

        # 构建 R-Tree 索引
        idx = index.Index()
        for i, (line, segment) in enumerate(lines.values()):
            idx.insert(i, line.bounds)

        # 检查每对线段的交点
        for i, (line1, segment1) in tqdm(lines.items(), desc="Checking intersections"):
            possible_matches = list(idx.intersection(line1.bounds))
            for j in possible_matches:
                if i >= j:  # 避免重复计算
                    continue
                line2, segment2 = lines[j]
                if line1.intersects(line2):
                    intersection_point = line1.intersection(line2)
                    if isinstance(intersection_point, Point):
                        point = Vector(intersection_point.x, intersection_point.y)
                        intersections.append(Intersection(point, [segment1, segment2]))

        # 检查每对线段的交点
        # for i in tqdm(range(len(segments)), desc="Checking intersections"):
        #     line1, segment1 = lines[i]
        #     for j in range(i + 1, len(segments)):
        #         line2, segment2 = lines[j]
        #         if line1.intersects(line2):
        #             intersection_point = line1.intersection(line2)
        #             if isinstance(intersection_point, Point):
        #                 point = Vector(intersection_point.x, intersection_point.y)
        #                 intersections.append(Intersection(point, [segment1, segment2]))
        # for i, segment in enumerate(segments):
        #     line = LineString([
        #         (segment.from_vec.x, segment.from_vec.y),
        #         (segment.to_vec.x, segment.to_vec.y)
        #     ])
        #     lines[i] = (line, segment)
        #
        # # 检查每对线段的交点
        # for i in range(len(segments)):
        #     line1, segment1 = lines[i]
        #     for j in range(i + 1, len(segments)):
        #         line2, segment2 = lines[j]
        #         if line1.intersects(line2):
        #             intersection_point = line1.intersection(line2)
        #             if isinstance(intersection_point, Point):
        #                 point = Vector(intersection_point.x, intersection_point.y)
        #                 intersections.append(Intersection(point, [segment1, segment2]))

        return intersections

    def delete_dangling_nodes(self, n: Node, nodes: List[Node]) -> bool:
        """
        从图中删除悬挂边，以便于多边形查找
        返回True如果节点被删除
        """
        if len(n.neighbors) == 1:
            if n in nodes:
                nodes.remove(n)

            neighbor = list(n.neighbors)[0]
            neighbor.neighbors.remove(n)
            self.delete_dangling_nodes(neighbor, nodes)
            return True
        return False

    def get_nodes_along_segment(
            self,
            segment: Segment,
            nodes: List[Node],
            kdtree: KDTree,
            radius: float,
            step: float
    ) -> List[Node]:
        """
        沿着给定线段查找所有节点
        """
        nodes_along_segment = []

        start = Vector(segment.from_vec.x, segment.from_vec.y)
        end = Vector(segment.to_vec.x, segment.to_vec.y)

        difference_vector = end.clone().sub(start)
        step = min(step, difference_vector.length() / 2)  # 沿向量至少有2个步长
        if difference_vector.length() == 0:
            print("difference_vector.length() / 2)",difference_vector.length() / 2)
            raise ValueError("线段起点和终点相同，无法计算步长")
        steps = int(np.ceil(difference_vector.length() / step))

        for i in range(steps + 1):
            current_point = start.clone().add(difference_vector.clone().multiply_scalar(i / steps))

            # 查找当前点附近的节点
            points_idx = kdtree.query_ball_point([current_point.x, current_point.y], radius + step / 2)
            nodes_to_add = []

            for idx in points_idx:
                node = nodes[idx]

                # 检查节点是否在线段上
                node_on_segment = False
                for s in node.segments:
                    if self.fuzzy_segments_equal(s, segment):
                        node_on_segment = True
                        break

                if node_on_segment:
                    nodes_to_add.append(node)

            # 按照点积排序
            nodes_to_add.sort(
                key=lambda node_param: self.dot_product_to_segment(node_param, start, difference_vector)
            )
            nodes_along_segment.extend(nodes_to_add)

        return nodes_along_segment

    @staticmethod
    def fuzzy_segments_equal(s1: Segment, s2: Segment, tolerance=0.0001) -> bool:
        """检查两个线段是否近似相等"""
        # 检查起点
        if abs(s1.from_vec.x - s2.from_vec.x) > tolerance:
            return False
        if abs(s1.from_vec.y - s2.from_vec.y) > tolerance:
            return False

        # 检查终点
        if abs(s1.to_vec.x - s2.to_vec.x) > tolerance:
            return False
        if abs(s1.to_vec.y - s2.to_vec.y) > tolerance:
            return False

        return True

    @staticmethod
    def dot_product_to_segment(node: Node, start: Vector, difference_vector: Vector) -> float:
        """计算节点到线段起点向量与线段向量的点积"""
        dot_vector = node.value.clone().sub(start)
        return difference_vector.dot(dot_vector)

    @staticmethod
    def fuzzy_add_to_nodes(nodes: List[Node], node: Node, radius: float) -> None:
        """仅在半径范围内没有节点时添加新节点"""
        existing_node = None

        for n in nodes:
            dx = n.value.x - node.value.x
            dy = n.value.y - node.value.y
            if dx * dx + dy * dy < radius * radius:
                existing_node = n
                break

        if existing_node is None:
            nodes.append(node)
        else:
            for neighbor in node.neighbors:
                existing_node.add_neighbor(neighbor)
            for segment in node.segments:
                existing_node.add_segment(segment)

    def streamlines_to_segment(self, streamlines: List[List[Vector]]) -> List[Segment]:
        """将流线转换为线段列表"""
        # segments = []
        # for streamline in streamlines:
        #     for i in range(len(streamline) - 1):
        #         segments.append(self.vectors_to_segment(streamline[i], streamline[i + 1]))
        # return segments
        from tqdm import tqdm  # 确保导入 tqdm

        segments = []
        for streamline in streamlines:
            for i in range(len(streamline) - 1):
                segments.append(self.vectors_to_segment(streamline[i], streamline[i + 1]))
        return segments

    @staticmethod
    def vectors_to_segment(v1: Vector, v2: Vector) -> Segment:
        """从两个向量创建线段"""
        return Segment(v1, v2)
