class StreamlineIntegration:
    """
    流线积分接口
    """
    def __init__(self, seed, original_dir, streamline, previous_direction, previous_point, valid):
        """
        初始化流线积分对象

        参数:
            seed: 种子点 (Vector)
            original_dir: 初始方向 (Vector)
            streamline: 流线 (List[Vector])
            previous_direction: 上一个方向 (Vector)
            previous_point: 上一个点 (Vector)
            valid: 是否有效 (bool)
        """
        self.seed = seed
        self.original_dir = original_dir
        self.streamline = streamline
        self.previous_direction = previous_direction
        self.previous_point = previous_point
        self.valid = valid


class StreamlineParams:
    """
    流线参数
    """
    def __init__(self, collide_early,dsep, dtest, dstep, dcircle_join, dlookahead, join_angle,
                 path_iterations, seed_tries, simplify_tolerance,degeneracy_threshold=0.0001):
        """
        初始化流线参数对象

        参数:
            dsep: 种子点分离距离
            dtest: 积分分离距离
            dstep: 步长
            dcircle_join: 圆连接的搜索距离 (例如 2 x dstep)
            dlookahead: 向前搜索的距离
            join_angle: 连接角度 (弧度)
            path_iterations: 路径流线积分迭代限制
            seed_tries: 最大失败种子尝试次数
            simplify_tolerance: 简化容差
        """
        self.collide_early =  collide_early
        self.dsep = dsep
        self.dtest = dtest
        self.dstep = dstep
        self.dcircle_join = dcircle_join
        self.dlookahead = dlookahead
        self.join_angle = join_angle
        self.path_iterations = path_iterations
        self.seed_tries = seed_tries
        self.simplify_tolerance = simplify_tolerance
        self.degeneracy_threshold=degeneracy_threshold


class NoiseStreamlineParams:
    """噪声流线参数类"""
    def __init__(self, noise_enabled: bool = False, noise_size: float = 0, noise_angle: float = 0):
        self.noise_enabled = noise_enabled
        self.noise_size = noise_size
        self.noise_angle = noise_angle


class WaterParams(StreamlineParams):
    """水生成参数类，继承自StreamlineParams"""
    def __init__(self, **kwargs):

        self.coast_noise = kwargs.pop('coast_noise', NoiseStreamlineParams())
        self.river_noise = kwargs.pop('river_noise', NoiseStreamlineParams())
        self.river_bank_size = kwargs.pop('river_bank_size', 0)
        self.river_size = kwargs.pop('river_size', 0)
        super().__init__(**kwargs)

class MainMajorMinorStreamlineParams(StreamlineParams):
    def __init__(self, **kwargs):
        """
        动态初始化参数
        """
        # 将剩余的参数传递给父类初始化
        super().__init__(**kwargs)