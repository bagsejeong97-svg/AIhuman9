# sigmoid_ex

import numpy as np
from util.print_util import pp

# 넘파이배열
z = np.array([-4,-2,0,2,4])

# 시그모이드 식 (수치 데이터들을 0~1 확률로 출력)
p = 1 / (1 + np.exp(-z))

pp(p)





























