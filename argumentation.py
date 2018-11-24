# Creates a argumentation framework representing feasiblity as an adjacency matrix
def create_feasiblity_framework(m, n):
	M = range(m)
	N = range(n)
	return [[i1 == i2 and j1 != j2 for i2 in M for j2 in N] for i1 in M for j1 in N]
