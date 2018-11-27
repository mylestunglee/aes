import numpy as np
import schedule

# Creates an argumentation framework representing feasiblity as an adjacency matrix
def create_feasiblity_framework(m, n):
	N = range(n)
	f = np.zeros((m, n, m, n), dtype=bool)

	for j in N:
		f[:, j, :, j] = np.logical_not(np.identity(m))
	return f

# Creates an optimality framework from a feasiblity framework
def create_optimality_framework(p, m, S, ff):
	C = schedule.calc_completion_times(p, S)
	C_max = np.max(C)
	M = range(m)
	J = [np.flatnonzero(S[i,:]) for i in M]
	of = np.copy(ff)

	i1 = np.argmax(C)
	# If feasible assigment (i1, j1)
	for j1 in J[i1]:
		for i2 in M:
			# Single exchange propertry
			if C[i1] > C[i2] + p[j1]:
				of[i1, j1, i2, j1] = False
			# If feasible assigment (i2, j2)
			for j2 in J[i2]:
				#  Pairwise exchange property
				if (i1 != i2 and j1 != j2 and
					p[j1] > p[j2] and
					C[i1] + p[j2] > C[i2] + p[j1]):
					of[i1, j1, i2, j2] = True
	return of

# Creates a fixed decision framework from a feasiblity framework
def create_fixed_decision_framework(ff, nfd, pfd):
	fdf = np.copy(ff)
	for i, j in nfd:
		fdf[i, j, i, j] = True
	for i, j in pfd:
		fdf[:, :, i, j] = False
	return fdf
