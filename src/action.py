import numpy as np

def is_problem_action(key_action):
	return key_action in ['allnfd', 'conflictfd', 'manypfd']

# Convert reasons to actions, where one reason may have multiple actions
def reason_to_actions(m, nfd, pfd, S, reason):
	actions = []

	key_reason, indices = reason

	# Problem
	if is_problem_action(key_reason):
		actions.append(reason)
	# Feasibility
	elif key_reason == 'unallocated':
		[j] = indices
		# If unallocated job must go to a pfd
		if np.any(pfd[:, j]):
			for i in range(m):
				if pfd[i, j]:
					actions.append((key_reason, [i, j]))
		else:
			# Can allocate to any machine not rejeceted by nfd
			for i in range(m):
				if not nfd[i, j]:
					actions.append((key_reason, [i, j]))
	elif key_reason == 'overallocated':
		[is_, j] = indices
		# Can remove any assignment not fixed by pfd
		for i in is_:
			if not pfd[i, j]:
				actions.append((key_reason, [i, j]))
	# Satisfaction
	elif key_reason == 'nfd' or key_reason == 'pfd':
		# Failed pfd does not say where it is currently allocated
		if key_reason == 'pfd':
			[_, j] = indices
			is_ = np.flatnonzero(S[:, j])
		else:
			# Job is known to be allocated at i1
			[i1, j] = indices
			is_ = [i1]

		for i1 in is_:
			if np.any(pfd[:, j]):
				for i2 in range(m):
					if pfd[i2, j]:
						actions.append(('move', [i1, i2, j]))
			else:
				for i2 in range(m):
					if not nfd[i2, j]:
						actions.append(('move', [i1, i2, j]))
	# Efficiency
	elif key_reason == 'move':
		[i1, i2, j, _] = indices
		actions.append((key_reason, [i1, i2, j]))
	elif key_reason == 'swap':
		[i1, i2, j1, j2, _] = indices
		actions.append((key_reason, [i1, i2, j1, j2]))

	return actions

# Fix user decisions based on action
def apply_problem_action(nfd, pfd, action):
	key_action, indices = action

	nfd_better = nfd.copy()
	pfd_better = pfd.copy()

	if key_action == 'allnfd':
		[j] = indices
		nfd_better[:, j] = False
	elif key_action == 'conflictfd':
		[j, is_] = indices
		for i in is_:
			nfd_better[i, j] = False
			pfd_better[i, j] = False
	elif key_action == 'manypfd':
		[j, is_] = indices
		pfd_better[:, j] = False
		nfd_better[:, j] = True
		for i in is_:
			nfd_better[i, j] = False

	return nfd_better, pfd_better

# Apply action modelled as action on schedule
def apply_schedule_action(S, action):
	key_action, indices = action
	S_better = S.copy()

	if key_action == 'unallocated':
		[i, j] = indices
		S_better[i, j] = True
	elif key_action == 'overallocated':
		[i, j] = indices
		S_better[i, j] = False
	elif key_action == 'move':
		[i1, i2, j] = indices
		S_better[i1, j] = False
		S_better[i2, j] = True
	elif key_action == 'swap':
		[i1, i2, j1, j2] = indices
		S_better[i1, j1] = False
		S_better[i2, j1] = True
		S_better[i2, j2] = False
		S_better[i1, j2] = True

	return S_better

