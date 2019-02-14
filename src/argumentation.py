import numpy as np
import schedule

# Creates an argumentation framework representing feasibility as an adjacency matrix
def construct_feasibility_framework(m, n):
	ff = np.zeros((m, n, m, n), dtype=bool)

	for j in range(n):
		ff[:, j, :, j] = np.logical_not(np.identity(m))
	return ff

def construct_partial_feasibility_framework(m, n, i1, j):
	ff = np.zeros((m, n), dtype=bool)

	for i2 in range(m):
		if i1 != i2:
			ff[i2, j] = True

	return ff

# Creates an efficiency framework from a feasibility framework
def construct_efficiency_framework(m, p, nfd, pfd, S, ff):
	ef = np.copy(ff)
	C = schedule.calc_completion_times(p, S)
	C_max = np.max(C) if m > 0 else 0

	if m == 0:
		return ef, C, C_max

	M = range(m)
	J = [np.flatnonzero(S[i,:]) for i in M]

	# If feasible assignment (i1, j1)
	for i1 in M:
		if C[i1] == C_max:
			for j1 in J[i1]:
				for i2 in M:
					# Single exchange property
					if C[i1] > C[i2] + p[j1] and not pfd[i1, j1] and not nfd[i2, j1]:
						ef[i1, j1, i2, j1] = False
					# If feasible assignment (i2, j2)
					for j2 in J[i2]:
						#  Pairwise exchange property
						if (i1 != i2 and j1 != j2 and
							p[j1] > p[j2] and
							C[i1] + p[j2] > C[i2] + p[j1] and
							not pfd[i1, j1] and not pfd[i2, j2] and
							not nfd[i2, j1] and not nfd[i1, j2]):
							ef[i1, j1, i2, j2] = True
	return ef, C, C_max

def construct_partial_efficiency_framework(m, p, nfd, pfd, S, C, C_max, i1, j1):
	_, n = S.shape
	ef = construct_partial_feasibility_framework(m, n, i1, j1)
	J = [np.flatnonzero(S[i,:]) for i in range(m)]

	if C[i1] == C_max:
		for i2 in range(m):
			# Single exchange property
			if C[i1] > C[i2] + p[j1] and not pfd[i1, j1] and not nfd[i2, j1]:
				ef[i2, j1] = False
			# If feasible assignment (i2, j2)
			for j2 in J[i2]:
				#  Pairwise exchange property
				if (i1 != i2 and j1 != j2 and
					p[j1] > p[j2] and
					C[i1] + p[j2] > C[i2] + p[j1] and
					not pfd[i1, j1] and not pfd[i2, j2] and
					not nfd[i2, j1] and not nfd[i1, j2]):
					ef[i2, j2] = True

	return ef

# Creates a fixed decision framework from a feasibility framework
def construct_satisfaction_framework(nfd, pfd, ff, copy=True):
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
				df[:, j, i, j] = False

	return df

def construct_partial_satisfaction_framework(nfd, pfd, i1, j):
	m, n = nfd.shape
	df = construct_partial_feasibility_framework(m, n, i1, j)

	if nfd[i1, j]:
		df[i1, j] = True

	for i2 in range(m):
		if pfd[i2, j]:
			df[i2, j] = False

	return df

# Attempt to build arguments to explain why S is not a stable extension of f
def compute_unattacked(S, f, ignore_unattacked, precomputed=True):
	m, n = S.shape
	unattacked = np.logical_not(S)
	for i in range(m):
		for j in range(n):
			if S[i, j]:
				if precomputed:
					f_partial = f[i, j, :, :]
				else:
					f_partial = f(i, j)
				unattacked = np.logical_and(unattacked, np.logical_not(f_partial))

	if not ignore_unattacked is None:
		unattacked = np.logical_and(unattacked, np.logical_not(ignore_unattacked))

	return unattacked


def compute_partial_conflicts(S, f, ignore_conflicts, i, j, precomputed=True):
	m, n = S.shape
	conflicts = np.zeros((m, n), dtype=bool)

	if S[i, j]:
		if precomputed:
			f_partial = f[i, j]
		else:
			f_partial = f(i, j)

		conflicts = np.logical_and(f_partial, S)

	if not ignore_conflicts is None:
		if precomputed:
			ignore_conflicts_partial = ignore_conflicts[i, j]
		else:
			ignore_conflicts_partial = ignore_conflicts(i, j)

		conflicts = np.logical_and(conflicts, np.logical_not(ignore_conflicts_partial))

	return conflicts

def explain_stability(S, f, ignore_unattacked=None, ignore_conflicts=None):
	unattacked = compute_unattacked(S, f, ignore_unattacked)

	m, n = S.shape
	conflicts = np.zeros((m, n, m, n), dtype=bool)

	for i in range(m):
		for j in range(n):
			conflicts[i, j] = compute_partial_conflicts(S, f,
				None if ignore_conflicts is None else ignore_conflicts,
				i, j)
	return unattacked, conflicts

# Compute reasons for feasibility using stability
def explain_feasibility(unattacked, conflicts, precomputed=True):
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
			if precomputed:
				conflicts_partial = conflicts[i1, j]
			else:
				conflicts_partial = conflicts(i1, j)

			for i2 in range(i1, m):
				if conflicts_partial[i2, j]:
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

# Compute reasons for efficiency using stability
def explain_efficiency(p, S, C, C_max, unattacked, conflicts, precomputed=True):
	(m, n) = unattacked.shape

	pairs = []

	if m > 0:
		M = range(m)
		N = range(n)

		def round(x):
			if x == 0:
				return 0
			return np.round(x, -int(np.floor(np.log10(abs(x)))) + 2)

		S_reduced = np.copy(S)
		i1 = np.argmax(C)
		for j1 in N:
			if precomputed:
				conflicts_partial = conflicts[i1, j1]
			else:
				conflicts_partial = conflicts(i1, j1)

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
					if conflicts_partial[i2, j2]:
						S_reduced[i1, j1] = False
						S_reduced[i2, j2] = False
						S_reduced[i1, j2] = True
						S_reduced[i2, j1] = True
						C_max_reduced = np.max(schedule.calc_completion_times(
							p, S_reduced))
						reduction = C_max - C_max_reduced
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

# Compute reasons for satisfaction of fixed decisions using stability
def explain_satisfaction(nfd, pfd, unattacked, conflicts, precompute=True):
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
			reasons.append('Job {} cannot be allocated to multiple machines {{{}}}'.format(
				j + 1, ', '.join([str(i + 1) for i in M if pfd[i, j]])))

	# Summarise fixed decision conflicts with schedule
	pfd_conflicts = unattacked
	nfd_conflicts = np.zeros((m, n), dtype=bool)

	for i in M:
		for j in N:
			if precompute:
				conflicts_partial = conflicts[i, j]
			else:
				conflicts_partial = conflicts(i, j)

			nfd_conflicts = np.logical_or(nfd_conflicts, conflicts_partial)

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

# Generate explanations using naive implementation
def full_precomputation_explain(m, n, p, nfd, pfd, S, options):
	explanations = []

	ff = construct_feasibility_framework(m, n)
	feasibility_unattacked, feasibility_conflicts = explain_stability(S, ff)
	explanations.append(format_argument('Schedule is {}feasible',
		explain_feasibility(feasibility_unattacked, feasibility_conflicts)))

	ef, C, C_max = construct_efficiency_framework(m, p, nfd, pfd, S, ff)

	efficiency_unattacked, efficiency_conflicts = explain_stability(S, ef,
		feasibility_unattacked, feasibility_conflicts)
	explanations.append(format_argument('Schedule is {}efficient',
		explain_efficiency(p, S, C, C_max, efficiency_unattacked, efficiency_conflicts)))

	df = construct_satisfaction_framework(nfd, pfd, ff, False)
	decisions_unattacked, decisions_conflicts = explain_stability(S, df,
		feasibility_unattacked, feasibility_conflicts)
	explanations.append(format_argument('Schedule does {}satisfies user fixed decisions',
		explain_satisfaction(nfd, pfd, decisions_unattacked, decisions_conflicts)))

	if options['verbose']:
		pass

	return '\n'.join(explanations)

# Favour memory over CPU resource consumption
def partial_precomputation_explain(m, n, p, nfd, pfd, S, options):
	explanations = []
	C = schedule.calc_completion_times(p, S)
	C_max = np.max(C) if m > 0 else 0

	def ff_partial(i, j):
		return construct_partial_feasibility_framework(m, n, i, j)

	def fc_partial(i, j):
		return compute_partial_conflicts(S, ff_partial, None, i, j, False)

	def ef_partial(i, j):
		return construct_partial_efficiency_framework(m, p, nfd, pfd, S, C, C_max, i, j)

	def ec_partial(i, j):
		return compute_partial_conflicts(S, ef_partial, fc_partial, i, j, False)

	def df_partial(i, j):
		return construct_partial_satisfaction_framework(nfd, pfd, i, j)

	def dc_partial(i, j):
		return compute_partial_conflicts(S, df_partial, fc_partial, i, j, False)

	feasibility_unattacked = compute_unattacked(S, ff_partial, None, False)
	explanations.append(format_argument('Schedule is {}feasible',
		explain_feasibility(feasibility_unattacked, fc_partial, False)))

	efficiency_unattacked = compute_unattacked(S, ef_partial,
		feasibility_unattacked, False)
	explanations.append(format_argument('Schedule is {}efficient',
		explain_efficiency(p, S, C, C_max, efficiency_unattacked, ec_partial, False)))

	satisfaction_unattacked = compute_unattacked(S, df_partial,
		feasibility_unattacked, False)
	explanations.append(format_argument('Schedule does {}satisfies user fixed decisions',
		explain_satisfaction(nfd, pfd, satisfaction_unattacked, dc_partial, False)))

	return '\n'.join(explanations)

# Switch between different explanation methods
def explain(m, n, p, nfd, pfd, S, options):
	if not options['partial']:
		return full_precomputation_explain(m, n, p, nfd, pfd, S, options)
	else:
		return partial_precomputation_explain(m, n, p, nfd, pfd, S, options)
