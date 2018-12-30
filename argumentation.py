import numpy as np
import schedule

# Creates an argumentation framework representing feasiblity as an adjacency matrix
def create_feasiblity_framework(m, n):
	N = range(n)
	ff = np.zeros((m, n, m, n), dtype=bool)

	for j in N:
		ff[:, j, :, j] = np.logical_not(np.identity(m))
	return ff

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
	df = np.copy(ff)
	(m, n) = nfd.shape

	for i in range(m):
		for j in range(n):
			if nfd[i, j]:
				df[i, j, i, j] = True
			if pfd[i, j]:
				df[:, :, i, j] = False

	return df

# Attempt to build arguments to explain why S is not a stable extension of f
def explain_stability(S, f, ignore_unattacked=None, ignore_conflicts=None):
	m, n = S.shape
	unattacked = np.logical_not(S)
	conflicts = np.zeros((m, n, m, n), dtype=bool)

	for i in range(m):
		for j in range(n):
			if S[i, j]:
				unattacked = np.logical_and(unattacked, np.logical_not(f[i, j, :, :]))
				conflicts[i, j] = np.logical_and(f[i, j], S)

	if not ignore_unattacked is None:
		unattacked = np.logical_and(unattacked, np.logical_not(ignore_unattacked))
	if not ignore_conflicts is None:
		conflicts = np.logical_and(conflicts, np.logical_not(ignore_conflicts))

	return unattacked, conflicts

# Compute reasons for feasibility using stability
def explain_feasiblity(unattacked, conflicts):
	(m, n) = unattacked.shape
	N = range(n)

	if m == 0:
		if n == 0:
			return True, ['There are no machines or jobs']
		else:
			return False, ['There are no macihnes to allocate to jobs']

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
		# Explain unallocated
		reasons = ['Job {} is not allocated by any machine'.format(j + 1) for j in range(n) if unallocated[j]]
		# Explain overallocations
		reasons += ['Job {} is over-allocated by multiple machines {{{}}}'.
			format(j + 1,', '.join([str(i + 1) for i in np.flatnonzero(job_conflicts[j])]))
			for j in N if overallocated[j]]
		return False, reasons
	else:
		reasons = ['All jobs are allocated by exactly one machine']
		return True, reasons

# Compute reasons for satisfication of fixed decisions usng stabilty
def explain_satisfaction(unattacked, conflicts):
	(m, n) = unattacked.shape
	M = range(m)
	N = range(n)

	conflicts_pfd = unattacked
	conflicts_nfd = np.zeros((m, n), dtype=bool)

	for i in M:
		for j in N:
			conflicts_nfd = np.logical_or(conflicts_nfd, conflicts[i, j])

	# Generate natural language explainations
	if np.any(conflicts_nfd) or np.any(conflicts_pfd):
		reasons = []
		for i in M:
			for j in N:
				if conflicts_nfd[i, j]:
					reasons.append('Job {} must not be allocated to machine {}'.format(j + 1, i + 1))
				if conflicts_pfd[i, j]:
					reasons.append('Job {} must be allocated to machine {}'.format(j + 1, i + 1))
		return False, reasons
	else:
		reasons = ['All jobs satisfy all fixed decisions']
		return True, reasons

# Use templates to construct natural language argument to explain property of schedule
def format_argument(template, pair):
	satisfied, reasons = pair

	if satisfied:
		claim = template.format('')
	else:
		claim = template.format('not ')

	if reasons:
		argument = '{} because:\n  - {}\n'.format(claim, '\n  - '.join(reasons))
	else:
		argument = '{}\n'.format(claim)

	return argument

# Generate explainations
def explain(m, p, nfd, pfd, S, verbose):
	explanation = ''
	n = len(p)

	ff = create_feasiblity_framework(m, n)
	feasiblity_unattacked, feasiblity_conflicts = explain_stability(S, ff)
	explanation += format_argument('Schedule is {}feasible',
		explain_feasiblity(feasiblity_unattacked, feasiblity_conflicts))

	df = create_fixed_decision_framework(ff, nfd, pfd)
	decisions_unattacked, decisions_conflicts = explain_stability(S, df,
		feasiblity_unattacked, feasiblity_conflicts)
	explanation += format_argument('Schedule does {}satisifies fixed decisions',
		explain_satisfaction(decisions_unattacked, decisions_conflicts))

	if verbose:
		# debug purposes
		pass

	return explanation
