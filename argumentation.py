import numpy as np

# Creates a argumentation framework representing feasiblity as an adjacency matrix
def create_feasiblity_framework(m, n):
	f = np.zeros((m, n, m, n), dtype=bool)
	M = range(m)
	N = range(n)

	for j in N:
		for i1 in M:
			for i2 in M:
				f[i1, j, i2, j] = i1 != i2
	return f
