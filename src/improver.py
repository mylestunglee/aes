import os
import subprocess
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
def schedule_reasons_to_actions(m, nfd, pfd, S, reasons):
	actions = []

	for k, (key_reason, indices) in enumerate(reasons):
		# Feasibility
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
						actions.append(('move', [j, i1, i2], k))
			else:
				for i2 in range(m):
					if not nfd[i2, j]:
						actions.append(('move', [j, i1, i2], k))
		# Efficiency
		elif key_reason == 'move':
			[j, i1, i2, _] = indices
			actions.append((key_reason, [j, i1, i2], k))
		elif key_reason == 'swap':
			[j1, j2, i1, i2, _] = indices
			actions.append((key_reason, [j1, j2, i1, i2], k))

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
	elif key_action == 'move':
		[j, i1, i2] = indices
		better_S[i1, j] = False
		better_S[i2, j] = True
	elif key_action == 'swap':
		[j1, j2, i1, i2] = indices
		better_S[i1, j1] = False
		better_S[i2, j1] = True
		better_S[i2, j2] = False
		better_S[i1, j2] = True
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
		'overallocated': 'Unassigning job {} with machine {}',
		'move': 'Moving job {} from machine {} to {}',
		'swap': 'Swapping jobs {} and {} with machines {} and {}'
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
	success, reasons = explain_feasibility(feasibility_unattacked, fc_partial, False)

	# Resolve
	if not success:
		actions = schedule_reasons_to_actions(m, nfd, pfd, S, reasons)
		if all_actions:
			return 'feasibility', reasons, [(action, apply_schedule_action(S, action))
				for action in actions]
		else:
			action = select_action(actions)
			better_S = apply_schedule_action(S, action)
			return 'feasibility', reasons, [(action, better_S)]

	# Fix unsatisfying job
	def df_partial(i, j):
		return construct_partial_satisfaction_framework(nfd, pfd, i, j)

	def dc_partial(i, j):
		return compute_partial_conflicts(S, df_partial, fc_partial, i, j, False)

	satisfaction_unattacked = compute_unattacked(S, df_partial,
		feasibility_unattacked, False)
	success, reasons = explain_schedule_satisfaction(nfd, pfd, satisfaction_unattacked,
		dc_partial, False)

	# Resolve
	if not success:
		actions = schedule_reasons_to_actions(m, nfd, pfd, S, reasons)
		if all_actions:
			return 'satisfaction', reasons, [(action, apply_schedule_action(S, action))
				for action in actions]
		else:
			action = select_action(actions)
			better_S = apply_schedule_action(S, action)
			return 'satisfaction', reasons, [(action, better_S)]

	# Fix inefficient job
	def ef_partial(i, j):
		return construct_partial_efficiency_framework(m, p, nfd, pfd, S, C, C_max, i, j)

	def ec_partial(i, j):
		return compute_partial_conflicts(S, ef_partial, fc_partial, i, j, False)

	C = schedule.calc_completion_times(p, S)
	C_max = np.max(C) if m > 0 else 0
	efficiency_unattacked = compute_unattacked(S, ef_partial,
		feasibility_unattacked, False)
	success, reasons = explain_efficiency(p, S, C, C_max, efficiency_unattacked,
		ec_partial, False)

	# Restrict the maximum number of efficiency suggestions
	max_reasons = 8
	reasons = reasons[:max_reasons]

	# Resolve
	if not success:
		actions = schedule_reasons_to_actions(m, nfd, pfd, S, reasons)
		if all_actions:
			return 'efficiency', reasons, [(action, apply_schedule_action(S, action))
				for action in actions]
		else:
			action = select_action(actions)
			better_S = apply_schedule_action(S, action)
			return 'efficiency', reasons, [(action, better_S)]

	return 'none', [], []


def next_label(accum, index, branch):
	if branch:
		return '{}_{}'.format(accum, index + 1)
	else:
		return '{}'.format(int(accum) + 1)

# Depth-first search of makeshift schedule improvement tree
#	all_actions: whether to visit all local improvements or select the best action
#	basename: prefix of all temporary saved files
#	prefix: used to uniquely identify recursion depth and index
#	S_old: holds the previous schedules, used to pretty draw diff charts
def improve_recursive(m, n, p, nfd, pfd, S, all_actions, basename=None, prefix='1', S_old=None):
	print(prefix)

	# Generate plot for Latex
	filename = '{}{}.png'.format(basename, prefix)
	draw_schedule(p, S, S_old, filename)
	explanation = '''
\\subsection*{{Step {}}}
\\begin{{center}}
	\\includegraphics[width=0.75\\textwidth]{{{}}}
\\end{{center}}
'''.format(prefix, filename)

	# Find future improvements
	action_class, reasons, nexts = improve_once(m, n, p, nfd, pfd, S, all_actions)

	if len(nexts) == 1:
		[((_, _, selected_reason), _)] = nexts
	else:
		selected_reason = None

	# Format main action_class
	if action_class == 'problem':
		explanation += format_argument('Problem is {}satisfiable',
			(False, reasons), selected_reason)
	elif action_class == 'feasibility':
		explanation += format_argument('Schedule is {}feasible',
			(False, reasons), selected_reason)
	elif action_class == 'satisfaction':
		explanation += format_argument('Schedule does {}satisfies user fixed decisions',
			(False, reasons), selected_reason)
	elif action_class == 'efficiency':
		explanation += format_argument('Schedule is {}efficient',
			(False, reasons), selected_reason)
	elif action_class == 'none':
		explanation += format_argument('Schedule is {}efficient',
			(True, []), selected_reason)
	else:
		print('Unknown action_class')

	next_explanations = []

	# Loop over each possible actions, if not all_actions then go to next action
	for k, next in enumerate(nexts):
		next_prefix = next_label(prefix, k, all_actions)

		if action_class == 'problem':
			action, (better_nfd, better_pfd) = next
			next_explanations.append(format_action(action))
			next_explanations.append(
				improve_recursive(m, n, p, better_nfd, better_pfd, S,
					all_actions, basename, next_prefix, S))
		else:
			action, better_S = next
			next_explanations.append(format_action(action))
			next_explanations.append(
				improve_recursive(m, n, p, nfd, pfd, better_S, all_actions,
					basename, next_prefix, S))

	# Nested explanations have nested indentation if there are multiple next actions
	return '{}{}'.format(explanation, '\n'.join(next_explanations))

# Remove text-based lists with Latex lists
def format_latex_lists(text):
	result = []
	in_list = False
	for line in text.splitlines():
		if line.startswith(bullet) or line.startswith(highlighted):
			item = line[len(bullet):]
			# Start of list
			if not in_list:
				result.append('\\begin{itemize}[noitemsep]')
				in_list = True
			# Standard bullet point
			if line.startswith(bullet):
				result.append('\\item {}'.format(item))
			else:
				result.append('\\item\\textbf{{{}}}'.format(item))
		else:
			if in_list:
				# End of list
				result.append('\\end{itemize}')
				in_list = False
			result.append(line)
	# Terminate itemize if not caught in lists
	if in_list:
		result.append('\\end{itemize}')
	return '\n'.join(result)

# Wrapper for improvement with Latex
def gen_improvement_report(m, n, p, nfd, pfd, S, filename):
	# Get name of the file without extensions or path
	if filename is None:
		basename = 'report'
	else:
		basename = os.path.splitext(filename)[0]
	# Get bulk explanation
	explanation = improve_recursive(m, n, p, nfd, pfd, S, False, basename)
	# Format lists
	explanation = format_latex_lists(explanation)
	report = '''\\documentclass[24pt, a4paper]{{report}}
\\usepackage{{graphicx}}
\\usepackage{{enumitem}}
\\usepackage[top=1in,bottom=1in]{{geometry}}
\\begin{{document}}
 	{}
\\end{{document}}
'''.format(explanation)
	report_filename = '{}.tex'.format(basename)
	# Save Latex file
	with open(report_filename, 'w') as file:
		file.write(report)

	# Compile report with no stdout
	with open(os.devnull, 'w') as devnull:
		subprocess.run(['pdflatex', report_filename], stdout=devnull)

# Wrapper for improvement without Latex
def improve_internal(m, n, p, nfd, pfd, S):
	explanation = improve_recursive(m, n, p, nfd, pfd, S, True, True)
	return explanation + '\n'

def main():
	pass

if __name__ == '__main__':
	main()
