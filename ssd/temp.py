import numpy as np

a = [38, 19, 10, 5, 3, 1]

a_np = np.array(a)
print((a_np[:] < 0).any())
