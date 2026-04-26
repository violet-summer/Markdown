import random
import re

class Util:
    @staticmethod
    def random_range(max_val, min_val=0):
        """
        生成指定范围内的随机数
        :param max_val: 最大值
        :param min_val: 最小值
        :return: 随机数
        """
        return random.uniform(min_val, max_val)




