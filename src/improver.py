import textwrap
from argumentation import *
from visualiser import *

# Given multiple local options, greedy select best action
def select_action(actions):
	if actions:
		return actions[0]

# Fix user decisions based on action
def apply_problem_action(action, nfd, pfd):
	key_action, indices, _ = action

	better_nfd = nfd.copy()
	better_pfd = pfd.copy()

	if key_action == 'allnfd':
		[j] = indices
		better_nfd[:, j] = False
	elif key_action == 'conflictfd':
		[j, is_] = indices
		for i in is_:
			better_nfd[i, j] = False
			better_pfd[i, j] = False
	elif key_action == 'manypfd':
		[j, is_] = indices
		better_pfd[:, j] = False
		better_nfd[:, j] = True
		for i in is_:
			better_nfd[i, j] = False
	else:
		print('key_action is not problem related')

	return better_nfd, better_pfd

# Convert reasons to actions, by appending source reason index
def problem_reasons_to_actions(reasons):
	return [(key_reason, indices, k) for k, (key_reason, indices) in enumerate(reasons)]

# Convert reasons to actions, where one reason may have multiple actions
def feasibility_reasons_to_actions(m, nfd, pfd, reasons):
	actions = []

	for k, (key_reason, indices) in enumerate(reasons):
		if key_reason == 'unallocated':
			[j] = indices
			# If unallocated job must go to a pfd
			if np.any(pfd[:, j]):
				for i in range(m):
					if pfd[i, j]:
						actions.append((key_reason, [j, i], k))
			else:
				# Can allocate to any machine not rejeceted by nfd
				for i in range(m):
					if not nfd[i, j]:
						actions.append((key_reason, [j, i], k))
		elif key_reason == 'overallocated':
			[j, is_] = indices
			# Can remove any assignment not fixed by pfd
			for i in is_:
				if not pfd[i, j]:
					actions.append((key_reason, [j, i], k))

	return actions

# Apply action modelled as action on schedule
def apply_schedule_action(S, action):
	key_action, indices, _ = action
	better_S = S.copy()

	if key_action == 'unallocated':
		[j, i] = indices
		better_S[i, j] = True
	elif key_action == 'overallocated':
		[j, i] = indices
		better_S[i, j] = False
	else:
		print('key_action was not processed')

	return better_S

def format_action(action):
	key_action, indices, _ = action
	positions = [format_list(i) for i in indices]

	action_templates = {
		'allnfd': 'Removing all negative fixed decisions for job {}',
		'conflictfd': 'Removing conflicting fixed decisions for job {}',
		'manypfd': 'Translating conflicting positive to negative fixed decisions for job {}',
		'unallocated': 'Assigning job {} to machine {}',
		'overallocated': 'Unassigning job {} with machine {}'
	}

	return action_templates[key_action].format(*positions)

# One-step improvement of D and S
def improve_once(m, n, p, nfd, pfd, S, all_actions=False):
	# Verify problem can be improved
	_, reasons = explain_problem_satisfaction(nfd, pfd)

	# Find a fix and apply
	if reasons:
		actions = problem_reasons_to_actions(reasons)
		if all_actions:
			return 'problem', reasons, [(action, apply_problem_action(action, nfd, pfd))
				for action in actions]
		else:
			action = select_action(actions)
			better_nfd, better_pfd = apply_problem_action(action, nfd, pfd)
			return 'problem', reasons, [(action, (better_nfd, better_pfd))]

	# Fix unfeasible schedules
	def ff_partial(i, j):
		return construct_partial_feasibility_framework(m, n, i, j)

	def fc_partial(i, j):
		return compute_partial_conflicts(S, ff_partial, None, i, j, False)

	feasibility_unattacked = compute_unattacked(S, ff_partial, None, False)
	feasible, reasons = explain_feasibility(feasibility_unattacked, fc_partial, False)

	if not feasible:
		actions = feasibility_reasons_to_actions(m, nfd, pfd, reasons)
		if all_actions:
			return 'feasibility', reasons, [(action, apply_schedule_action(S, action))
				for action in actions]
		else:
			action = select_action(actions)
			better_S = apply_schedule_action(S, action)
			return 'feasibility', reasons, [(action, better_S)]

	# feasible
	return 'none', [], []

# Depth-first search of makeshift schedule improvement tree
def improve_recursive(m, n, p, nfd, pfd, S, all_actions, generate_latex, prefix='1', S_old=None):
	# Generate plot for latex
	if generate_latex:
		# Replace accumated prefix with a more human-readable index
		if prefix == '1':
			used_prefix = 'Initial'
		else:
			used_prefix = prefix[2:]

		explanation = '\subsection*{{{}}}'.format(used_prefix.replace('_', '.'))
		filename = '{}.png'.format(used_prefix)
		draw_schedule(p, S, S_old, filename)
		explanation += '\includegraphics[width=0.5\\textwidth]{{{}}}\n'.format(filename)
	else:
		# Skip plots and headers
		explanation = ''

	# Find future improvements
	action_class, reasons, nexts = improve_once(m, n, p, nfd, pfd, S, all_actions)

	if len(nexts) == 1:
		print(nexts, len(nexts))
		[((_, _, selected_reason), _)] = nexts
		print(selected_reason)
	else:
		selected_reason = None

	# Format main action_class
	if action_class == 'problem':
		explanation += format_argument('Problem is {}satisfiable',
			(False, reasons), selected_reason)
	elif action_class == 'feasibility':
		explanation += format_argument('Schedule is {}feasible',
			(False, reasons), selected_reason)
	elif action_class == 'none':
		explanation += format_argument('Schedule is {}feasible',
			(True, []), selected_reason)
	else:
		print('Unknown action_class')

	next_explanations = []

	# Loop over each possible actions, if not all_actions then go to next action
	for k, next in enumerate(nexts):
		if action_class == 'problem':
			action, (better_nfd, better_pfd) = next
			next_explanations.append(format_action(action))
			next_explanations.append(
				improve_recursive(m, n, p, better_nfd, better_pfd, S,
					all_actions, generate_latex, '{}_{}'.format(prefix, k), S))
		elif action_class == 'feasibility':
			action, better_S = next
			next_explanations.append(format_action(action))
			next_explanations.append(
				improve_recursive(m, n, p, nfd, pfd, better_S, all_actions,
					generate_latex, '{}_{}'.format(prefix, k + 1), S))

	# Nested explanations have nested indentation if there are multiple next actions
	if next_explanations:
		next_explanation = '\n'.join(next_explanations)
		if all_actions:
			next_explanation = textwrawp.indent(next_explanation, '\t')

		return '{}{}'.format(explanation, next_explanation)
	else:
		return explanation.rstrip('\n')

# Wrapper for improvement with latex
def improve(m, n, p, nfd, pfd, S):
	# Get bulk explanation
	explanation = improve_recursive(m, n, p, nfd, pfd, S, False, True)
	# Force new lines in latex
	explanation = explanation.replace('\n', '\n\n')
	# Remove indentation
	explanation = explanation.replace('\t', '')
	template = '''\\documentclass[10pt, a4paper]{{report}}
\\usepackage{{graphicx}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{multicol}}
\\setlength\\parindent{{0pt}}
\\setlength\\parskip{{0pt}}
\\begin{{document}}
	\\begin{{multicols*}}{{2}}
	 	{}
 	\\end{{multicols*}}
\\end{{document}}
'''
	report = template.format(explanation)
	with open('report.tex', 'w') as file:
		file.write(report)

# Wrapper for improvement without latex
def improve_internal(m, n, p, nfd, pfd, S):
	explanation = improve_recursive(m, n, p, nfd, pfd, S, True, True)
	return explanation + '\n'

def main():
	pass

if __name__ == '__main__':
	main()
