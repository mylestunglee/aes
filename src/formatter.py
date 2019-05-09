def number_to_letters(x):
	x += 1
	letters = []
	while x > 0:
		x, remain = divmod(x - 1, 26)
		letters.append(chr(remain + ord('A')))
	return ''.join(reversed(letters))

def letters_to_number(letters):
	x = 0
	for letter in letters:
		x = x * 26 + ord(letter) - ord('A') + 1
	return x - 1

# Format nested lists into set notation
def format_list(x):
	if type(x) is list:
		# Wrap multiple args into sets
		return '{{{}}}'.format(', '.join(format_list(arg) for arg in x))

	# Return already formatted string
	if type(x) is str:
		return x

	# Assume integer
	return str(x + 1)

# Try to format index into letters
def format_as_job(j):
	if type(j) is list or type(j) is str:
		return None
	else:
		return number_to_letters(j)

# Format low-level, unformatted reasons into understandable reasons
def format_reason(reason):
	key_reason, args = reason

	reason_templates = {
		'nomachinejob': 'There are no machines or jobs',
		'nomachine': 'There are no machines to allocate to jobs',
		'nojob': 'There are no jobs',
		'unallocated': 'Job {1} is not allocated to any machine',
		'overallocated': 'Job {3} is allocated to multiple machines {0}',
		'feasible': 'All jobs are allocated to exactly one machine',
		'move': 'Job {6} can be allocated from machine {0} to {1} to reduce by {3}',
		'swap': 'Jobs {7} and {8} can be swapped with machines {0} and {1} to reduce by {4}',
		'efficient': 'All jobs satisfy single and pairwise exchange properties',
		'allnfd': 'Job {1} cannot be allocated to any machine',
		'conflictfd': 'Job {3} cannot be allocated and not be allocated to machines {0}',
		'manypfd': 'Job {3} cannot be allocated to multiple machines {0}',
		'nfd': 'Job {3} must not be allocated to machine {0}',
		'pfd': 'Job {3} must be allocated to machine {0}',
		'satisfies': 'All jobs satisfy all fixed decisions'
	}

	if key_reason in reason_templates:
		tokens = [format_list(arg) for arg in args] + [format_as_job(arg) for arg in args]
		return ' -  ' + reason_templates[key_reason].format(*tokens)
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
	if any(args for _, args in reasons):
		suffix = ' because:'
	else:
		suffix = ''

	lines.append(('{}{}'.format(claim, suffix), None))
	lines += reasons

	return lines

# Format an action so it is readable
def format_action(action):
	key_action, args = action

	tokens = [format_list(arg) for arg in args] + [format_as_job(arg) for arg in args]

	action_templates = {
		'allnfd': 'Remove all negative fixed decisions for job {1}',
		'conflictfd': 'Remove conflicting fixed decisions for job {2} on machines{0}',
		'manypfd': 'Relax conflicting positive to negative fixed decisions for job {2} on machines {0}',
		'unallocated': 'Assign job {3} to machine {0}',
		'overallocated': 'Unassign job {3} with machine {0}',
		'move': 'Move job {5} from machine {0} to {1}',
		'swap': 'Swap jobs {6} and {7} with machines {0} and {1}'
	}

	return action_templates[key_action].format(*tokens)
