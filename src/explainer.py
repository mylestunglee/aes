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
		'unallocated': 'Job {} is not allocated by any machine',
		'overallocated': 'Job {} is allocated to multiple machines {}',
		'feasible': 'All jobs are allocated by exactly one machine',
		'move': 'Job {} can be allocated from machine {} to {} to reduce by {}',
		'swap': 'Jobs {} and {} can be swapped with machines {} and {} to reduce by {}',
		'efficient': 'All jobs satisfy single and pairwise exchange properties',
		'allnfd': 'Job {} cannot be allocated to any machine',
		'conflictfd': 'Job {} cannot be allocated and not be allocated to machines {}',
		'manypfd': 'Job {} cannot be allocated to multiple machines {}',
		'nfd': 'Job {} must not be allocated to machine {}',
		'pfd': 'Job {} must be allocated to machine {}',
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
        'allnfd': 'Removing all negative fixed decisions for job {}',
        'conflictfd': 'Removing conflicting fixed decisions for job {}',
        'manypfd': 'Translating conflicting positive to negative fixed decisions for job {}'
,
        'unallocated': 'Assigning job {} to machine {}',
        'overallocated': 'Unassigning job {} with machine {}',
        'move': 'Moving job {} from machine {} to {}',
        'swap': 'Swapping jobs {} and {} with machines {} and {}'
    }

    return action_templates[key_action].format(*positions)

