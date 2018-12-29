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
def create_optimality_framework(m, p, S, ff):
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

# Attempt to build arguments to explain why S is not a stable extension of f
def explain_stablity(S, f, ignore_unattacked=None, ignore_conflicts=None):
	m, n = S.shape
	unattacked = np.logical_not(S)
	conflicts = np.zeros((m, n, m, n), dtype=bool)

	for i in range(m):
		for j in range(n):
			if S[i, j]:
				unattacked = np.logical_and(unattacked, np.logical_not(f[i, j, :, :]))
				conflicts[i, j] = np.logical_and(f[i, j], S)

	if ignore_conflicts:
		conflicts = np.logical_and(conflicts, np.logical_not(ignore_conflicts))

	return unattacked, conflicts

# Compute reasons for feasibility using stablity
def explain_feasiblity(unattacked, conflicts):
	(m, n) = unattacked.shape
	N = range(n)

	if m == 0:
		return True, None

	# Summarise unallocated jobs
	unallocated = unattacked[0]

	# Summaries overallocated jobs
	overallocated = np.zeros(n, dtype=bool)
	job_conflicts = np.zeros((n, m), dtype=bool)
	for j in N:
		# Conflicts are symmetrical, count upper diagonal
		for i1 in range(m):
			for i2 in range(i1, m):
				if conflicts[i1, j, i2, j]:
					overallocated[j] = True
					job_conflicts[j, i1] = True
					job_conflicts[j, i2] = True

	# Generate natural language explainations
	if np.any(unallocated) or np.any(overallocated):
		# Exlain unallocated
		reasons = ['Job {} is not allocated by any machine'.format(j + 1) for j in range(n) if unallocated[j]]
		# Explain overallocations
		reasons += ['Job {} is over-allocated by multiple machines {{{}}}'.
			format(j + 1,', '.join([str(i + 1) for i in np.flatnonzero(job_conflicts[j])]))
			for j in N if overallocated[j]]
		return False, reasons
	else:
		reasons = ['All jobs are allocated by exactly one machine']
		return True, reasons

def explain(m, p, nfd, pfd, S):
	n = len(p)
	af = create_feasiblity_framework(m, n)
	unattacked, conflicts = explain_stablity(S, af)
	feasible, reasons = explain_feasiblity(unattacked, conflicts)
	return '\n'.join(reasons)
