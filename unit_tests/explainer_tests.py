import numpy as np
import sys
sys.path.append('../src/')
import explainer

def partial_vs_full(m, n, full, partial):
	ff = full(m, n)
	for i in range(m):
		for j in range(n):
			ff_partial = partial(m, n, i, j)
			assert np.array_equal(ff[i, j], ff_partial)


def test_feasibility_partial_vs_full():
	m = 10
	n = 5
	partial_vs_full(m, n, explainer.construct_feasibility_framework,
		explainer.construct_partial_feasibility_framework)
