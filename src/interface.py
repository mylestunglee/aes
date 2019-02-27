import re
import matplotlib.pyplot as plt
import numpy as np
import schedule
import visualiser
import explainer
import action as act
import solver
import formatter

delimiter = ';\n'
integer_pattern = re.compile(r'^[0-9]+$')
float_pattern = re.compile(r'^([ \t]*[A-Z]+[ \t]*:([ \t]+[0-9]+(\.[0-9]+)?)*[ \t]*\n)*\n*$')
schedule_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[A-Z]+)*[ \t]*\n)*\n*$')

def random_problem():
	m, p, nfd, pfd = schedule.random_problem()
	n = p.shape[0]

	m_text = str(m)
	p_text = format_processing_times(p)
	nfd_text = format_schedule(nfd)
	pfd_text = format_schedule(pfd)

	return m_text, p_text, nfd_text, pfd_text

def load_text(filename):
	try:
		with open(filename, 'r') as file:
			text = file.read()

		return True, text
	except IOError:
		return False, 'Cannot read from file at {}'.format(filename)

def save_text(filename, text):
	try:
		with open(filename, 'w') as file:
			file.write(text)

		return True, None
	except IOError:
		return False, 'Cannot write to file at {}'.format(filename)

def load_problem(filename):
	success, problem = load_text(filename)

	if not success:
		return False, problem

	texts = problem.split(delimiter)

	if len(texts) != 4:
		return False, 'Invalid file format'

	return True, texts

def save_problem(filename, m_text, p_text, nfd_text, pfd_text):
	text = format_problem(m_text, p_text, nfd_text, pfd_text)
	return save_text(filename, text)

# Attempts to parse problem in text format into internal format
def parse_problem(m_text, p_text, nfd_text, pfd_text):
	if not integer_pattern.match(m_text):
		return False, 'Number of machines syntax error'
	if not float_pattern.match(p_text):
		return False, 'Proccessing times syntax error'
	if not schedule_pattern.match(nfd_text):
		return False, 'Negative fixed decisions syntax error'
	if not schedule_pattern.match(pfd_text):
		return False, 'Positive fixed decisions syntax error'

	m = int(m_text)
	p = parse_processing(p_text)
	n = p.shape[0]
	nfd = parse_schedule(nfd_text, m, n)
	pfd = parse_schedule(pfd_text, m, n)

	if m != nfd.shape[0]:
		return False, 'Negative fixed decisions refers to undefined machines'
	if m != pfd.shape[0]:
		return False, 'Positive fixed decisions refers to undefined machines'
	if n != nfd.shape[1]:
		return False, 'Negative fixed decisions refers to undefined processing times'
	if n != pfd.shape[1]:
		return False, 'Positive fixed decisions refers to undefined processing times'

	return True, (m, n, p, nfd, pfd)

# Attempts to parse problem and schedule
def parse_problem_schedule(m_text, p_text, nfd_text, pfd_text, S_text):
	success, result = parse_problem(m_text, p_text, nfd_text, pfd_text)
	if not success:
		return success, result

	(m, n, p, nfd, pfd) = result

	if not schedule_pattern.match(S_text):
		return False, 'Schedule syntax error'

	S = parse_schedule(S_text, m, n)

	if m != S.shape[0]:
		return False, 'Schedule refers to undefined machines'
	if n != S.shape[1]:
		return False, 'Schedule refers to undefined processing times'

	return True, (m, n, p, nfd, pfd, S)

def optimal_schedule(m_text, p_text, nfd_text, pfd_text, solver_name, time_limit):
	try:
		import pyomo
	except ImportError as error:
		return False, 'Pyomo is not installed'

	success, result = parse_problem(m_text, p_text, nfd_text, pfd_text)
	if not success:
		return success, result

	(m, n, p, nfd, pfd) = result

	success, result = solver.optimal_schedule(m, p, nfd, pfd, solver_name, time_limit)

	if success:
		return success, format_schedule(result)
	else:
		return success, result

def random_schedule(m_text, p_text, nfd_text, pfd_text):
	success, result = parse_problem(m_text, p_text, nfd_text, pfd_text)
	if not success:
		return success, result
	(m, n, _, nfd, pfd) = result
	S = schedule.random_schedule(m, n, nfd, pfd)
	return True, format_schedule(S)

def explain(m_text, p_text, nfd_text, pfd_text, S_text, options):
	success, result = parse_problem_schedule(m_text, p_text, nfd_text,
		pfd_text, S_text)
	if not success:
		return success, result

	(m, n, p, nfd, pfd, S) = result

	# Draw schedule
	if options['graphical']:
		plt.gcf().clear()
		visualiser.draw_schedule(p, S)

	return True, explainer.explain(m, n, p, nfd, pfd, S, options)

def apply(m_text, p_text, nfd_text, pfd_text, S_text, action, options):
	success, result = parse_problem_schedule(m_text, p_text, nfd_text,
		pfd_text, S_text)
	if not success:
		return success, result

	(m, n, p, nfd, pfd, S) = result

	# Decide to apply action to decisions or schedule
	key_action, indices = action
	if act.is_problem_action(key_action):
		nfd_better, pfd_better = act.apply_problem_action(nfd, pfd, action)
		nfd_text = format_schedule(nfd_better)
		pfd_text = format_schedule(pfd_better)
		S_better = None
	else:
		S_better = act.apply_schedule_action(S, action)
		S_text = format_schedule(S_better)

	# Draw schedule
	if options['graphical'] and not S_better is None:
		plt.gcf().clear()
		visualiser.draw_schedule(p, S_better, S)

	return True, (nfd_text, pfd_text, S_text)

# Parse colon space-delimited integer structure
def vectorise(text, parse_key):
	lines = text.splitlines()

	if not lines or text.isspace():
		return []

	# Split on colon but exclude empty lines
	rows = [line.split(':') for line in lines if line]
	positions = [parse_key(row[0]) for row in rows]

	max_position = max(positions)
	cells = [[] for _ in range(max_position)]
	for i, row in enumerate(rows):
		if not row[1].isspace():
			cells[positions[i] - 1] = row[1].split()

	return cells

# Convert text format of processing times into list of floats
def parse_processing(text):
	return np.array([float(row[0]) if row else 1
		for row in vectorise(text,
			lambda letters: formatter.letters_to_number(letters) + 1
		)])

# Convert text format for a schedule into assignment matrix
def parse_schedule(text, m, n):
	indices = [[formatter.letters_to_number(cell) for cell in row]
		for row in vectorise(text, int)]

	m_sparse = len(indices)
	m = max(m, m_sparse)
	n = max([i for row in indices for i in row] + [-1, n - 1]) + 1

	S = np.zeros((m, n), dtype=bool)
	for i in range(m_sparse):
		for j in indices[i]:
			S[i, j] = True

	return S

def format_problem(m_text, p_text, nfd_text, pfd_text):
	return delimiter.join([m_text, p_text, nfd_text, pfd_text])

def format_processing_times(p):
	n = p.shape[0]
	return ''.join('{}: {}\n'.format(formatter.number_to_letters(j), p[j]) for j in range(n))

def format_schedule(S):
	m, n = S.shape
	return ''.join('{}: {}\n'.format(i + 1,' '.join(
		[formatter.number_to_letters(j) for j in range(n) if S[i, j]]
		)) for i in range(m))
