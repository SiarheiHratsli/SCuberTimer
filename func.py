from app import time_list_def
import numpy as np


def ao5():
    if len(time_list_def()) >= 5:
        time_ao5 = time_list_def()[-5:].copy()
        time_ao5 = [float(time) for time in time_ao5]
        time_ao5.remove(max(time_ao5))
        time_ao5.remove(min(time_ao5))
        ao5 = round(np.mean(time_ao5), 2)
    else:
        ao5 = '--'
    return ao5


def ao10():
    if len(time_list_def()) >= 10:
        time_ao10 = time_list_def()[-10:].copy()
        time_ao10 = [float(time) for time in time_ao10]
        print('time_ao10', time_ao10)
        time_ao10.remove(max(time_ao10))
        print('max', time_ao10)
        time_ao10.remove(min(time_ao10))
        print('min', time_ao10)
        ao10 = round(np.mean(time_ao10), 2)
    else:
        ao10 = '--'
    return ao10