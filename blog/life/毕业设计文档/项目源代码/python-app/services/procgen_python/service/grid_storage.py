import math

from app.services.procgen_python.custom_struct import Vector


class GridStorage:
    """
    笛卡尔网格加速数据结构
    网格单元格，每个包含向量列表
    """
    
    def __init__(self, world_dimensions, origin, dsep):
        """
        构造函数
        
        参数:
            world_dimensions: 世界尺寸，假设原点为0,0
            origin: 原点坐标
            dsep: 样本之间的分离距离
        """
        self.world_dimensions = world_dimensions
        self.origin = origin
        # 格子间的分离距离
        self.dsep = dsep
        self.dsep_sq = self.dsep * self.dsep
        # 网格尺寸，单位为格子数，也是做为网格二维向量的索引
        self.grid_dimensions = world_dimensions.clone().divide_scalar(self.dsep)
        
        # 初始化网格
        # 网格是一个二维列表，每个单元格包含一个向量列表
        # 注意：网格坐标是整数
        # grid是一个二维列表，每个单元格包含一个向量列表，存储样本点
        self.grid = []
        for x in range(int(self.grid_dimensions.x)):
            self.grid.append([])
            for y in range(int(self.grid_dimensions.y)):
                self.grid[x].append([])
    
    def add_all(self, grid_storage):
        """添加另一个网格中的所有样本到本网格"""
        for row in grid_storage.grid:
            for cell in row:
                for sample in cell:
                    self.add_sample(sample)
    
    def add_polyline(self, line):
        """添加折线上的所有点"""
        for v in line:
            self.add_sample(v)
    
    def add_sample(self, v, coords=None):
        """
        添加样本点，不强制保持分离距离，不克隆
        
        参数:
            v: 要添加的向量
            coords: 可选的网格坐标，如果未提供将自动计算
        """
        if coords is None:
            coords = self.get_sample_coords(v)
        # 在网格中添加样本点 
        if not (coords.x % 1 == 0 and coords.y % 1 == 0):
            raise ValueError(f"网格坐标不是整数值: x={coords.x}, y={coords.y}")
        self.grid[int(coords.x)][int(coords.y)].append(v)
        # self.grid[int(coords.x)][int(coords.y)].append(v)
    
    def is_valid_sample(self, v, d_sq):
        """
        测试v是否至少距离样本d远
        性能非常重要 - 这在每个积���步骤都会被调用
        
        参数:
            v: 要测试的向量
            d_sq: 平方测试距离，默认为self.dsep_sq
        """
        # if d_sq is None:
        #     d_sq = self.dsep_sq
            
        coords = self.get_sample_coords(v)
        
        # 检查3x3网格中的9个单元格中的样本
        # 利用dsep进行种子点的间隔距离筛选，小于则不添加，大于才合法
        for x in range(-1, 2):
            for y in range(-1, 2):
                cell = coords.clone().add(Vector(x, y))
                if not self.vector_out_of_bounds(cell, self.grid_dimensions):
                    if not self.vector_far_from_vectors(v, self.grid[int(cell.x)][int(cell.y)], d_sq):
                        return False
        
        return True
    
    @staticmethod
    def vector_far_from_vectors(v, vectors, d_sq):
        """
        测试v是否至少距离vectors中的所有向量d远
        性能非常重要 - 这在每个积分步骤都会被调用
        
        参数:
            v: 要测试的向量
            vectors: 向量列表
            d_sq: 平方测试距离
        """
        for sample in vectors:
            if sample is not v:
                distance_sq = sample.distance_to_squared(v)
                if distance_sq < d_sq:
                    return False
        
        return True
    
    def get_nearby_points(self, v, distance):
        """
        返回v周围单元格中的点
        结果包括v（如果它存在于网格中）
        
        参数:
            v: 中心点
            distance: 距离，返回大约比这个距离近的样本
                    （返回单元格中所有样本，所以是近似值，用正方形近似圆）
        """
        radius = int(math.ceil((distance / self.dsep) - 0.5))
        coords = self.get_sample_coords(v)
        out = []
        
        for x in range(-radius, radius + 1):
            for y in range(-radius, radius + 1):
                cell = coords.clone().add(Vector(x, y))
                if not self.vector_out_of_bounds(cell, self.grid_dimensions):
                    for v2 in self.grid[int(cell.x)][int(cell.y)]:
                        out.append(v2)
        
        return out
    
    def world_to_grid(self, v):
        """将世界坐标转换为网格坐标"""
        return v.clone().sub(self.origin)
    
    def grid_to_world(self, v):
        """将网格坐标转换为世界坐标"""
        return v.clone().add(self.origin)
    
    @staticmethod
    def vector_out_of_bounds(grid_v, bounds):
        """检查向量是否超出边界"""
        return (grid_v.x < 0 or grid_v.y < 0 or
                grid_v.x >= bounds.x or grid_v.y >= bounds.y)
    
    def get_sample_coords(self, world_v):
        """
        获取与向量对应的单元格坐标
        性能重要 - 在每个积分步骤都会调用
        
        参数:
            world_v: 世界坐标中的向量
        """
        v = self.world_to_grid(world_v)
        if self.vector_out_of_bounds(v, self.world_dimensions):
            # 尝试访问网格中的越界样本
            return Vector.zero_vector()
        # 获取网格坐标，为离散化的整数坐标
        return Vector(
            int(v.x // self.dsep),
            int(v.y // self.dsep)
        )
