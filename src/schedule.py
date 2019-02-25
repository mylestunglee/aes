import numpy as np

default_m = 4

def random_problem(m=default_m, n=None):
	if n is None:
		n = np.random.poisson(m * 2)

	p = np.round(np.random.lognormal(1, 0.5, n), 3)

	pr = 1 / n if n > 0 else 0
	nfd = np.random.choice(a=[True, False], size=(m, n), p=[pr, 1 - pr])

	pfd = np.random.choice(a=[True, False], size=(m, n), p=[pr, 1 - pr])

	for j in range(n):
		if np.all(nfd[:, j]):
			nfd[:, j] = False
		if np.count_nonzero(pfd[:, j]) > 1:
			pfd[:, j] = False
		if np.any(np.logical_and(nfd[:, j], pfd[:, j])):
			nfd[:, j] = False
			pfd[:, j] = False

	return m, p, nfd, pfd

def random_schedule(m, n, nfd, pfd):
	S = np.zeros((m, n), dtype=bool)
	if m > 0:
		for j in range(n):
			i = np.random.randint(m)
			S[i, j] = True
	return S

# Calculates completion time vector [C_i for i in M]
def calc_completion_times(p, S):
	return S.astype(int).dot(p)

