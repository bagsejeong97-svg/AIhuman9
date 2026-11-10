# day23_basic.py
# 주제:
from idlelib import history

import numpy as np
import matplotlib.pyplot as plt
from tensorflow import keras
from tensorflow.keras import layers
from util.print_util import pp, pt, up
from include.graph_config import set_graph

set_graph(10, 8, 13)

X = np.array([
    [0.10, 0.20], [0.18, 0.30], [0.25, 0.25], [0.32, 0.40],
    [0.40, 0.35], [0.48, 0.50], [0.55, 0.45], [0.62, 0.60],
    [0.70, 0.55], [0.78, 0.70], [0.86, 0.75], [0.95, 0.85]
], dtype=np.float32)

y = np.array([
    0.18, 0.25, 0.27, 0.36, 0.40, 0.49,
    0.51, 0.62, 0.64, 0.76, 0.83, 0.93
], dtype=np.float32)

keras.utils.set_random_seed(42)
model=keras.models.Sequential([
    layers.Input(shape=(2,)),
    layers.Dense(6, activation='relu'),
    layers.Dense(1)
])

model.compile(optimizer='adam',loss='mse')

a = model.fit(X, y, epochs=200,verbose=0)

model.summary(print_fn=lambda s: pp(s))

result_parms = (2*6+6)+(6*1+1)
auto_parms = model.count_params()
pp(f'직접 계산:{result_parms}\n함수 계산:{auto_parms}')

new = np.array([[0.68,0.65]])
pred = model.predict(new, verbose=0)

first = a.history['loss'][0]
last = a.history['loss'][-1]
pp(f'첫번째 loss:{first:.3f}\n마지막 loss:{last:.3f}')













