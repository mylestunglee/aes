# Format nested lists into set notation
def format_list(x):
	if type(x) is list:
		# Wrap multiple indices into sets
		return '{{{}}}'.format(', '.join(format_list(i) for i in x))

	# Return already formatted string
	if type(x) is str:
		return x

	# Assume integer
	return str(x + 1)


# Format low-level, unformatted reasons into understandable reasons
def format_reason(reason):
	key_reason, indices = reason

	reason_templates = {
		'nomachinejob': 'There are no machines or jobs',
		'nomachine': 'There are no machines to allocate to jobs',
		'unallocated': 'Job {0} is not allocated by any machine',
		'overallocated': 'Job {1} is allocated to multiple machines {0}',
		'feasible': 'All jobs are allocated by exactly one machine',
		'move': 'Job {2} can be allocated from machine {0} to {1} to reduce by {3}',
		'swap': 'Jobs {2} and {3} can be swapped with machines {0} and {1} to reduce by {4}',
		'efficient': 'All jobs satisfy single and pairwise exchange properties',
		'allnfd': 'Job {0} cannot be allocated to any machine',
		'conflictfd': 'Job {1} cannot be allocated and not be allocated to machines {0}',
		'manypfd': 'Job {1} cannot be allocated to multiple machines {0}',
		'nfd': 'Job {1} must not be allocated to machine {0}',
		'pfd': 'Job {1} must be allocated to machine {0}',
		'satisfies': 'All jobs satisfy all fixed decisions'
	}

	if key_reason in reason_templates:
		positions = [format_list(i) for i in indices]
		return ' -  ' + reason_templates[key_reason].format(*positions)
	else:
		return key_reason

# Use templates to construct natural language argument to explain property of schedule
def format_argument(property_template, explained_property):
	satisfied, reasons = explained_property
	lines = []

	if satisfied:
		claim = property_template.format('')
	else:
		claim = property_template.format('not ')

	# If possible action
	if any(indices for _, indices in reasons):
		suffix = ' because:'
	else:
		suffix = ''

	lines.append(('{}{}'.format(claim, suffix), None))
	lines += reasons

	return lines

# Format an action so it is readable
def format_action(action):
	key_action, indices = action
	positions = [format_list(i) for i in indices]

	action_templates = {
		'allnfd': 'Remove all negative fixed decisions for job {0}',
		'conflictfd': 'Remove conflicting fixed decisions for job {0}',
		'manypfd': 'Relax conflicting positive to negative fixed decisions for jobs {0}',
		'unallocated': 'Assign job {1} to machine {0}',
		'overallocated': 'Unassign job {1} with machine {0}',
		'move': 'Move job {2} from machine {0} to {1}',
		'swap': 'Swap jobs {2} and {3} with machines {0} and {1}'
	}

	return action_templates[key_action].format(*positions)

