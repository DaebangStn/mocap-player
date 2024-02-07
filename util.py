import os
import inspect
from random import random

import numpy as np
from vpython import vec


def log(*texts):
    stack = inspect.stack()
    if len(stack) < 2:
        print(*texts)
        return
    else:
        file_full_path = stack[1].filename

    filename = os.path.basename(file_full_path)
    filename_without_extension = os.path.splitext(filename)[0]
    log_id = "[" + filename_without_extension.upper() + "]"

    print(log_id, *texts)


def random_color():
    while True:
        c = np.array([random() for _ in range(3)])
        c_n = np.linalg.norm(c)
        if c_n != 0:
            c = c / c_n
            return vec(c[0], c[1], c[2])
