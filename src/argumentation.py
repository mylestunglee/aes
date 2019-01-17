import numpy as np
import schedule

# Creates an argumentation framework representing feasiblity as an adjacency matrix
def create_feasiblity_framework(m, n):
	N = range(n)
	ff = np.zeros((m, n, m, n), dtype=bool)

	for j in N:
		ff[:, j, :, j] = np.logical_not(np.identity(m))
	return ff

# Creates an efficiency framework from a feasiblity framework
def create_efficiency_framework(m, p, S, ff):
	ef = np.copy(ff)

	if m == 0:
		return ef

	C = schedule.calc_completion_times(p, S)
	M = range(m)
	J = [np.flatnonzero(S[i,:]) for i in M]

	C_max = np.argmax(C)
	# If feasible assigment (i1, j1)
	for i1 in M:
		if C[i1] != C_max:
			for j1 in J[i1]:
				for i2 in M:
					# Single exchange propertry
					if C[i1] > C[i2] + p[j1]:
						ef[i1, j1, i2, j1] = False
					# If feasible assigment (i2, j2)
					for j2 in J[i2]:
						#  Pairwise exchange property
						if (i1 != i2 and j1 != j2 and
							p[j1] > p[j2] and
							C[i1] + p[j2] > C[i2] + p[j1]):
							ef[i1, j1, i2, j2] = True
	return ef

# Creates a fixed decision framework from a feasiblity framework
def create_fixed_decision_framework(nfd, pfd, ff, copy=True):
	if copy:
		df = np.copy(ff)
	else:
		df = ff
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
			return False, ['There are no machines to allocate to jobs']

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

	# Generate natural language explanations
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

# Compute reasons for efficiency using stablity
def explain_efficiency(p, S, unattacked, conflicts):
	(m, n) = unattacked.shape

	pairs = []

	if m > 0:
		M = range(m)
		N = range(n)

		C = schedule.calc_completion_times(p, S)
		C_max = np.max(C)

		def round(x):
			if x == 0:
				return 0
			return np.round(x, -int(np.floor(np.log10(x))) + 2)


		S_reduced = np.copy(S)
		i1 = np.argmax(C)
		for j1 in N:
			for i2 in M:
				if unattacked[i2, j1]:
					allocated = S_reduced[:, j1].copy()
					S_reduced[:, j1] = False
					S_reduced[i2, j1] = True
					C_max_reduced = np.max(schedule.calc_completion_times(p, S_reduced))
					reduction = C_max - C_max_reduced
					pairs.append((
						(-reduction, j1, i2),
						'Job {} can be allocated to machine {} to reduce by {}'.format(
						j1 + 1, i2 + 1, round(reduction))))
					S_reduced[:, j1] = allocated

				for j2 in N:
					if conflicts[i1, j1, i2, j2]:
						S_reduced[i1, j1] = False
						S_reduced[i2, j2] = False
						S_reduced[i1, j2] = True
						S_reduced[i2, j1] = True
						C_max_reduced = np.max(schedule.calc_completion_times(
							p, S_reduced))
						reduction = C_max - C_max_reduced
						reduction = 1
						pairs.append((
							(-reduction, j1, j2, i1, i2),
							'Jobs {} and {} can be swapped with machines {} and {} to reduce by {}'.format(
							j1 + 1, j2 + 1, i1 + 1, i2 + 1, round(reduction))))
						S_reduced[i1, j1] = True
						S_reduced[i2, j2] = True
						S_reduced[i1, j2] = False
						S_reduced[i2, j1] = False

		# Order by most reducible first
		pairs.sort()
	if pairs:
		_, reasons = zip(*pairs)
		return False, reasons
	else:
		reasons = ['All jobs satisfy single and pairwise exchange properties']
	return True, reasons

# Compute reasons for satisfaction of fixed decisions usng stabilty
def explain_satisfaction(nfd, pfd, unattacked, conflicts):
	(m, n) = unattacked.shape
	M = range(m)
	N = range(n)
	reasons = []

	# Summarise fixed decision self-conflicts
	satisfiable = np.ones(n, dtype=bool)
	for j in N:
		if np.all(nfd[:, j]):
			satisfiable[j] = False
			reasons.append('Job {} cannot be allocated to any machine'.format(j + 1))

		incompatible = np.flatnonzero(np.logical_and(nfd[:, j], pfd[:, j]))
		if np.any(incompatible):
			satisfiable[j] = False
			reasons.append('Job {} cannot be allocated and not be allocated to machines {{{}}}'.format(
				j + 1, ', '.join([str(i + 1) for i in incompatible])))

		if np.count_nonzero(pfd[:, j]) > 1:
			satisfiable[j] = False
			reasons.append('Job {} cannot be allocated to muliple machines {{{}}}'.format(
				j + 1, ', '.join([str(i + 1) for i in M if pfd[i, j]])))

	# Summarise fixed decision conflicts with schedule
	pfd_conflicts = unattacked
	nfd_conflicts = np.zeros((m, n), dtype=bool)

	for i in M:
		for j in N:
			nfd_conflicts = np.logical_or(nfd_conflicts, conflicts[i, j])

	# Generate natural language explanations
	if reasons or np.any(nfd_conflicts) or np.any(pfd_conflicts):
		for j in N:
			if satisfiable[j]:
				for i in M:
					if nfd_conflicts[i, j]:
						reasons.append('Job {} must not be allocated to machine {}'.format(j + 1, i + 1))
					if pfd_conflicts[i, j]:
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
		argument = '{} because:\n - {}\n'.format(claim, '\n - '.join(reasons))
	else:
		argument = '{}\n'.format(claim)

	return argument

# Generate explanations
def explain(m, p, nfd, pfd, S, verbose):
	explanation = ''
	n = len(p)

	ff = create_feasiblity_framework(m, n)
	feasiblity_unattacked, feasiblity_conflicts = explain_stability(S, ff)
	explanation += format_argument('Schedule is {}feasible',
		explain_feasiblity(feasiblity_unattacked, feasiblity_conflicts))
	explanation += '\n'

	ef = create_efficiency_framework(m, p, S, ff)

	efficiency_unattacked, efficiency_conflicts = explain_stability(S, ef,
		feasiblity_unattacked, feasiblity_conflicts)
	explanation += format_argument('Schedule is {}efficient',
		explain_efficiency(p, S, efficiency_unattacked, efficiency_conflicts))
	explanation += '\n'

	df = create_fixed_decision_framework(nfd, pfd, ff, False)
	decisions_unattacked, decisions_conflicts = explain_stability(S, df,
		feasiblity_unattacked, feasiblity_conflicts)
	explanation += format_argument('Schedule does {}satisify fixed decisions',
		explain_satisfaction(nfd, pfd, decisions_unattacked, decisions_conflicts))

	if verbose:
		# debug purposes
		pass

	return explanation
