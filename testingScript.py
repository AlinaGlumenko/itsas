import numpy as np

# 2d array to list
arr = np.array([1., 2., 3.])

print(f'NumPy Array:\n{arr}')

list1 = arr.tolist()

print(f'List: {list1}')

print(type(list1[0]))