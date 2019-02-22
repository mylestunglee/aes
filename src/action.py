import numpy as np

# Convert reasons to actions, where one reason may have multiple actions
def reason_to_actions(m, nfd, pfd, S, reason):
	actions = []

	key_reason, indices = reason

	# Problem
	if key_reason in ['allnfd', 'conflictfd', 'manypfd']:
		actions.append(reason)
	# Feasibility
	elif key_reason == 'unallocated':
		[j] = indices
		# If unallocated job must go to a pfd
		if np.any(pfd[:, j]):
			for i in range(m):
				if pfd[i, j]:
					actions.append((key_reason, [j, i]))
		else:
			# Can allocate to any machine not rejeceted by nfd
			for i in range(m):
				if not nfd[i, j]:
					actions.append((key_reason, [j, i]))
	elif key_reason == 'overallocated':
		[j, is_] = indices
		# Can remove any assignment not fixed by pfd
		for i in is_:
			if not pfd[i, j]:
				actions.append((key_reason, [j, i]))
	# Satisfaction
	elif key_reason == 'nfd' or key_reason == 'pfd':
		# Failed pfd does not say where it is currently allocated
		if key_reason == 'pfd':
			[j, _] = indices
			[i1] = np.flatnonzero(S[:, j])
		else:
			[j, i1] = indices

		if np.any(pfd[:, j]):
			for i2 in range(m):
				if pfd[i2, j]:
					actions.append(('move', [j, i1, i2]))
		else:
			for i2 in range(m):
				if not nfd[i2, j]:
					actions.append(('move', [j, i1, i2]))
	# Efficiency
	elif key_reason == 'move':
		[j, i1, i2, _] = indices
		actions.append((key_reason, [j, i1, i2]))
	elif key_reason == 'swap':
		[j1, j2, i1, i2, _] = indices
		actions.append((key_reason, [j1, j2, i1, i2]))

	return actions

def is_problem_action(key_action):
	return key_action in ['allnfd', 'conflictfd', 'manypfd']

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
	else:
		print('key_action is not problem related')

	return nfd_better, pfd_better

# Apply action modelled as action on schedule
def apply_schedule_action(S, action):
	key_action, indices = action
	S_better = S.copy()

	if key_action == 'unallocated':
		[j, i] = indices
		S_better[i, j] = True
	elif key_action == 'overallocated':
		[j, i] = indices
		S_better[i, j] = False
	elif key_action == 'move':
		[j, i1, i2] = indices
		S_better[i1, j] = False
		S_better[i2, j] = True
	elif key_action == 'swap':
		[j1, j2, i1, i2] = indices
		S_better[i1, j1] = False
		S_better[i2, j1] = True
		S_better[i2, j2] = False
		S_better[i1, j2] = True
	else:
		print('key_action was not processed')

	return S_better

