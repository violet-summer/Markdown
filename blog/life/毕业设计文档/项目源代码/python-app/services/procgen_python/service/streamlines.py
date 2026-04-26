import logging
from typing import List

import numpy as np
from pydantic import BaseModel
from simplification.cutil import simplify_coords  # 替代simplify-js库

from .grid_storage import GridStorage
from .integrator import FieldIntegrator
from app.services.procgen_python.custom_struct import Vector, StreamlineParams, StreamlineIntegration, WaterParams, MainMajorMinorStreamlineParams

class StreamlineIntegrationConfig(BaseModel):
    """
    用于流线积分的参数模型
    包含种子点、原始方向、流线、前一个方向和前一个点
    """
    def __init__(self, seed: Vector, original_dir: Vector, streamline: List[Vector],
                 previous_direction: Vector, previous_point: Vector, valid: bool):
        self.seed = seed
        self.original_dir = original_dir
        self.streamline = streamline
        self.previous_direction = previous_direction
        self.previous_point = previous_point
        self.valid = valid


class StreamlineGenerator:
    """
    创建通过积分张量场形成的道路多段线
    参考论文 'Interactive Procedural Street Modeling' 获取详细解释
    """
    def __init__(self, integrator:FieldIntegrator, origin, world_dimensions, params:StreamlineParams):
        """
        使用世界坐标系

        参数:
            integrator (FieldIntegrator): 场积分器，用于计算张量场的积分。
            origin (Vector): 原点向量，表示世界的起始坐标。
            world_dimensions (Vector): 世界尺寸向量，表示世界的宽度和高度。
            params (StreamlineParams): 流线参数，包含流线生成的相关配置。
        """
        self.SEED_AT_ENDPOINTS = False
        self.NEAR_EDGE = 3  # 在边缘附近采样
        
        self.integrator = integrator
        self.origin = origin
        self.world_dimensions:Vector = world_dimensions
        self.params = params
        
        if params.dstep > params.dsep:
            logging.error("流线采样距离大于DSEP")
            
        # 强制 test < sep
        self.params.dtest = min(params.dtest, params.dsep)
        
        self.majorGrid = GridStorage(self.world_dimensions, self.origin, params.dsep)
        self.minorGrid = GridStorage(self.world_dimensions, self.origin, params.dsep)
        
        # 参数平方化 是在 setParamsSq() 方法中由 params 复制并处理得到的一个新对象。
        # paramsSq 中的所有数值参数都被平方（即 x^2），用于后续涉及“距离的平方”比较的算法（如碰撞检测、范围判断等）。
        # 这样做可以避免在大量距离比较时反复调用 Math.sqrt，提升性能。
        # 欠缺动态构造类的方法，这里需要检查参数列表决定使用哪一个子类进行初始化
        if isinstance(params, WaterParams):
            self.params_sq = WaterParams(**{k: v ** 2 if isinstance(v, (int, float)) else v
                                            for k, v in vars(params).items()})
        else:
            self.params_sq = MainMajorMinorStreamlineParams(**{k: v ** 2 if isinstance(v, (int, float)) else v
                                             for k, v in vars(params).items()})
        
        self.candidateSeedsMajor = []
        self.candidateSeedsMinor = []
        
        self.streamlinesDone = True
        self.resolve = None
        self.lastStreamlineMajor = True
        
        self.allStreamlines = []
        self.streamlinesMajor = []
        self.streamlinesMinor = []
        self.allStreamlinesSimple = []  # 减少顶点数量
    
    def clear_streamlines(self):
        """清除所有流线"""
        self.allStreamlinesSimple = []
        self.streamlinesMajor = []
        self.streamlinesMinor = []
        self.allStreamlines = []
    
    def join_dangling_streamlines(self):
        logging.info("连接悬空的流线")
        for major in [True, False]:
            for streamline in self.streamlines(major):
                # 忽略圆形
                if streamline[0].equals(streamline[-1]):
                    continue
                
                new_start = self.get_best_next_point(streamline[0], streamline[4])
                if new_start is not None:
                    # logging.info("连接悬空流线，起点")
                    for p in self.points_between(streamline[0], new_start, self.params.dstep):
                        streamline.insert(0, p)
                        self.grid(major).add_sample(p)
                
                new_end = self.get_best_next_point(streamline[-1], streamline[-4])
                if new_end is not None:
                    # logging.info("连接悬空流线，终点: %s, 旧的终点: %s", new_end, streamline[-1])
                    for p in self.points_between(streamline[-1], new_end, self.params.dstep):
                        streamline.append(p)
                        self.grid(major).add_sample(p)
        
        # 重置简化的流线
        self.allStreamlinesSimple = []
        for s in self.allStreamlines:
            self.allStreamlinesSimple.append(self.simplify_streamline(s))
    
    def points_between(self, v1, v2, dstep):
        """
        返回从v1到v2的点数组，使得它们最多相距dsep
        不包括v1
        """
        d = v1.distance_to(v2)
        n_points = int(d / dstep)
        if n_points == 0:
            return []
        
        step_vector = v2.clone().sub(v1)
        
        out = []
        for i in range(1, n_points + 1):
            next_point = v1.clone().add(step_vector.clone().multiply_scalar(i / n_points))
            if self.integrator.integrate(next_point, True).length_sq() > self.params.degeneracy_threshold:  # 测试退化点
                out.append(next_point)
            else:
                return out
        return out
    
    def get_best_next_point(self, point, previous_point):
        """
        获取连接流线的下一个最佳点
        如果没有好的候选点则返回None
        """
        nearby_points = self.majorGrid.get_nearby_points(point, self.params.dlookahead)
        nearby_points.extend(self.minorGrid.get_nearby_points(point, self.params.dlookahead))
        direction = point.clone().sub(previous_point)
        
        closest_sample = None
        closest_distance = float('inf')
        
        for sample in nearby_points:
            if not sample.equals(point) and not sample.equals(previous_point):
                difference_vector = sample.clone().sub(point)
                if difference_vector.dot(direction) < 0:
                    # 向后
                    continue
                
                # 向量之间的锐角(不考虑顺时针、逆时针)
                distance_to_sample = point.distance_to_squared(sample)
                if distance_to_sample < 2 * self.params_sq.dstep:
                    logging.info("找到接近的样本: %s,旧的点: %s, 距离: %f,二倍dstep: %f", sample, point, distance_to_sample, 2 * self.params_sq.dstep)
                    closest_sample = sample
                    break
                
                angle_between = abs(Vector.angle_between(direction, difference_vector))
                
                # 按角度过滤
                if angle_between < self.params.join_angle and distance_to_sample < closest_distance:
                    # logging.info("找到接近的样本: %s, 距离: %f, 角度: %f", sample, distance_to_sample, angle_between)
                    closest_distance = distance_to_sample
                    closest_sample = sample
        
        # 防止端点被简化线拉离
        if closest_sample is not None:
            closest_sample = closest_sample.clone().add(direction.set_length(self.params.simplify_tolerance ))
        
        return closest_sample
    
    def add_existing_streamlines(self, s):
        """添加已有流线"""
        self.majorGrid.add_all(s.majorGrid)
        self.minorGrid.add_all(s.minorGrid)
    
    def set_grid(self, s):
        """设置网格"""
        self.majorGrid = s.majorGrid
        self.minorGrid = s.minorGrid
    
    
    def create_all_streamlines(self, animate=False):
        """一次性创建所有流线 - 如果dsep很小可能会卡顿"""
        major = True
        while self.create_streamline(major):
            major = not major

        self.join_dangling_streamlines()
    
    def simplify_streamline(self, streamline:list[Vector]):
        """简化流线，减少点数"""
        points = [(point.x, point.y) for point in streamline]

        # 使用simplification库简化
        # print("简化容差", self.params.simplify_tolerance)
        simplified_points = simplify_coords(np.array(points), self.params.simplify_tolerance)
        # 将简化后的点转换回Vector对象
        logging.info("简化前点数: %d, 简化后点数: %d", len(points), len(simplified_points))

        return [Vector(x, y) for x, y in simplified_points]
    
    def create_streamline(self, major):
        """
        寻找种子并从该点创建流线
        将新的候选种子添加到队列
        如果在params.seedTries内找不到种子则返回False
        """
        seed = self.get_seed(major)
        if seed is None:
            return False
        # 一次性生成流线然后进行首尾种子点添加
        streamline = self.integrate_streamline(seed, major)
        if self.valid_streamline(streamline):
            self.grid(major).add_polyline(streamline)
            self.streamlines(major).append(streamline)
            self.allStreamlines.append(streamline)
            
            self.allStreamlinesSimple.append(self.simplify_streamline(streamline))
            
            # 添加候选种子
            # 如果一条流线的首尾不重合（即不是闭合曲线），就把它的起点和终点作为新的“候选种子”，用于后续生成更多的流线。 这样可以逐步填充整个流场，直到达到预期的覆盖度。
            # 但是避免继续延申导致重叠，会需要注册到垂直方向
            if not streamline[0].equals(streamline[-1]):
                self.candidate_seeds(not major).append(streamline[0])
                self.candidate_seeds(not major).append(streamline[-1])
                
        return True
    
    @staticmethod
    def valid_streamline(s):
        """判断流线是否有效"""
        return len(s) > 5
    
    def sample_point(self):
        """采样一个点"""
        # logging.info("参数信息: %s", self.world_dimensions)
        return Vector(
            np.random.random() * self.world_dimensions.x,
            np.random.random() * self.world_dimensions.y
        ).add(self.origin)
    
    def get_seed(self, major:bool):
        """
        先尝试self.candidateSeeds，然后使用self.samplePoint采样
        """
        logging.info("先使用候选种子")
        if self.SEED_AT_ENDPOINTS and len(self.candidate_seeds(major)) > 0:
            while len(self.candidate_seeds(major)) > 0:
                seed = self.candidate_seeds(major).pop()
                # 提取种子点进行dsep检查
                if self.is_valid_sample(major, seed, self.params_sq.dsep):
                    return seed
        # logging.info("使用样本候选种子")
        seed = self.sample_point()
        # logging.info("输出样本候选种子", seed)
        i = 0
        while not self.is_valid_sample(major, seed, self.params_sq.dsep):
            if i >= self.params.seed_tries:
                return None
            seed = self.sample_point()
            i += 1
            
        return seed
    
    def is_valid_sample(self, major, point, d_sq, both_grids=False):
        """检查样本是否有效"""
        grid_valid = self.grid(major).is_valid_sample(point, d_sq)
        if both_grids:
            grid_valid = grid_valid and self.grid(not major).is_valid_sample(point, d_sq)
        return self.integrator.on_land(point) and grid_valid
    
    def candidate_seeds(self, major):
        """获取候选种子列表"""
        return self.candidateSeedsMajor if major else self.candidateSeedsMinor
    
    def streamlines(self, major):
        """获取流线列表"""
        return self.streamlinesMajor if major else self.streamlinesMinor
    
    def grid(self, major):
        """获取网格"""
        return self.majorGrid if major else self.minorGrid
    
    def point_in_bounds(self, v):
        """检查点是否在边界内"""
        return (self.origin.x <= v.x < self.world_dimensions.x + self.origin.x and
                self.origin.y <= v.y < self.world_dimensions.y + self.origin.y)
    
    @staticmethod
    def streamline_turned(seed, original_dir, point, direction):
        """测试流线是否已经转过大于180度"""
        if original_dir.dot(direction) < 0:
            perpendicular_vector = Vector(original_dir.y, -original_dir.x)
            is_left = point.clone().sub(seed).dot(perpendicular_vector) < 0
            direction_up = direction.dot(perpendicular_vector) > 0
            return is_left == direction_up
        
        return False
    
    def streamline_integration_step(self, params: StreamlineIntegrationConfig, major, collide_both,degeneracy_threshold=0.0001):
        """流线积分过程的一步"""
        if params.valid:
            params.streamline.append(params.previous_point)
            next_direction = self.integrator.integrate(params.previous_point, major)
            
            # 在退化点停止
            # 退化点临界值，如果临界值太大，同时step太小，导致向量（来自张量权重积分）也很小，本来应该是一个有效的点，但由于精度问题被认为是退化点
            if next_direction.length_sq() < self.params.degeneracy_threshold:
                params.valid = False
                return
                
            # 确保我们沿着相同方向前进
            if next_direction.dot(params.previous_direction) < 0:
                # 重写逻辑
                next_direction.negate()
                
            next_point = params.previous_point.clone().add(next_direction)
            
            # 确保是否有效，会进行和别的点进行碰撞检测，避免进行相交，但是默认行为是只和同方向张量特征向量进行检测
            if (self.point_in_bounds(next_point) and 
                self.is_valid_sample(major, next_point, self.params_sq.dtest, collide_both) and
                not self.streamline_turned(params.seed, params.original_dir, next_point, next_direction)):
                params.previous_point = next_point
                params.previous_direction = next_direction
            else:
                # 再走一步
                params.streamline.append(next_point)
                params.valid = False
    
    def integrate_streamline(self, seed, major):
        """
        通过同时在两个方向上积分来减小圆不能连接的影响
        因为误差在连接处匹配
        """
        logging.info("流线积分")
        count = 0
        points_escaped = False  # 当两个积分前沿移动dlookahead距离后为True
        
        # 是否使用两个网格存储测试有效性（与主要和次要都碰撞）
        collide_both = np.random.random() < self.params.collide_early
        
        d = self.integrator.integrate(seed, major)
        
        forward_params = StreamlineIntegration(seed=seed,original_dir=d,streamline=[seed],previous_direction=d,previous_point=seed.clone().add(d),valid=True)

        forward_params.valid =self.point_in_bounds( forward_params.previous_point)
        neg_d = d.clone().negate()
        backward_params = StreamlineIntegration(seed=seed,original_dir=neg_d,streamline=[],previous_direction=neg_d,previous_point=seed.clone().add(neg_d),valid=True)
    
        backward_params.valid = self.point_in_bounds(backward_params.previous_point)
        
        while count < self.params.path_iterations and (forward_params.valid or backward_params.valid):
            self.streamline_integration_step(forward_params, major, collide_both)
            self.streamline_integration_step(backward_params, major, collide_both)

            # logging.info("连接圆形")
            sq_distance_between_points = forward_params.previous_point.distance_to_squared(backward_params.previous_point)
            
            if not points_escaped and sq_distance_between_points > self.params_sq.dcircle_join:
                points_escaped = True
                
            if points_escaped and sq_distance_between_points <= self.params_sq.dcircle_join:
                forward_params.streamline.append(forward_params.previous_point)
                forward_params.streamline.append(backward_params.previous_point)
                backward_params.streamline.append(backward_params.previous_point)
                break
                
            count += 1
        
        # 合并向前和向后的流线
        backward_params.streamline.reverse()
        backward_params.streamline.extend(forward_params.streamline)
        logging.info("流线积分完成，点数: %d", len(backward_params.streamline))
        return backward_params.streamline
