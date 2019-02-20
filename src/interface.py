import re
import matplotlib.pyplot as plt
import numpy as np
import schedule
import visualiser
import solver
import argumentation
import improver

delimiter = ';\n'
integer_pattern = re.compile(r'^[0-9]+$')
float_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[0-9]+(\.[0-9]+)?)*[ \t]*\n)*\n*$')
schedule_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[1-9][0-9]*)*[ \t]*\n)*\n*$')

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

def optimal_schedule(m_text, p_text, nfd_text, pfd_text, solver_name, time_limit):
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

	_, S = solver.optimal_schedule(m, p, nfd, pfd, solver_name, time_limit)

	if S is None:
		return False, 'Solver failed to find feasible schedule'

	S_text = format_schedule(S)

	return True, S_text

def random_schedule(m_text, p_text, nfd_text, pfd_text):
	if not integer_pattern.match(m_text):
		return False, 'Number of machines syntax error'
	if not float_pattern.match(p_text):
		return False, 'Processing times syntax error'
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

	S = schedule.random_schedule(m, n, nfd, pfd)
	S_text = format_schedule(S)

	return True, S_text

def explain(m_text, p_text, nfd_text, pfd_text, S_text, options):
	if not integer_pattern.match(m_text):
		return False, 'Number of machines syntax error'
	if not float_pattern.match(p_text):
		return False, 'Proccessing times syntax error'
	if not schedule_pattern.match(nfd_text):
		return False, 'Negative fixed decisions syntax error'
	if not schedule_pattern.match(pfd_text):
		return False, 'Positive fixed decisions syntax error'
	if not schedule_pattern.match(S_text):
		return False, 'Schedule syntax error'

	m = int(m_text)
	p = parse_processing(p_text)
	n = p.shape[0]
	nfd = parse_schedule(nfd_text, m, n)
	pfd = parse_schedule(pfd_text, m, n)
	S = parse_schedule(S_text, m, n)

	if m != S.shape[0]:
		return False, 'Schedule refers to undefined machines'
	if m != nfd.shape[0]:
		return False, 'Negative fixed decisions refers to undefined machines'
	if m != pfd.shape[0]:
		return False, 'Positive fixed decisions refers to undefined machines'
	if n != S.shape[1]:
		return False, 'Schedule refers to undefined processing times'
	if n != nfd.shape[1]:
		return False, 'Negative fixed decisions refers to undefined processing times'
	if n != pfd.shape[1]:
		return False, 'Positive fixed decisions refers to undefined processing times'

	# Draw schedule
	if options['graphical']:
		plt.gcf().clear()
		visualiser.draw_schedule(p, S)

	return True, argumentation.explain(m, n, p, nfd, pfd, S, options)

# Explain and optimise at the same time
def gen_improvement_report(m_text, p_text, nfd_text, pfd_text, S_text, filename):
	if not integer_pattern.match(m_text):
		return False, 'Number of machines syntax error'
	if not float_pattern.match(p_text):
		return False, 'Proccessing times syntax error'
	if not schedule_pattern.match(nfd_text):
		return False, 'Negative fixed decisions syntax error'
	if not schedule_pattern.match(pfd_text):
		return False, 'Positive fixed decisions syntax error'
	if not schedule_pattern.match(S_text):
		return False, 'Schedule syntax error'

	m = int(m_text)
	p = parse_processing(p_text)
	n = p.shape[0]
	nfd = parse_schedule(nfd_text, m, n)
	pfd = parse_schedule(pfd_text, m, n)
	S = parse_schedule(S_text, m, n)

	if m != S.shape[0]:
		return False, 'Schedule refers to undefined machines'
	if m != nfd.shape[0]:
		return False, 'Negative fixed decisions refers to undefined machines'
	if m != pfd.shape[0]:
		return False, 'Positive fixed decisions refers to undefined machines'
	if n != S.shape[1]:
		return False, 'Schedule refers to undefined processing times'
	if n != nfd.shape[1]:
		return False, 'Negative fixed decisions refers to undefined processing times'
	if n != pfd.shape[1]:
		return False, 'Positive fixed decisions refers to undefined processing times'

	improver.gen_improvement_report(m, n, p, nfd, pfd, S, filename)

	return True, ''

def vectorise(text):
	lines = list(filter(None, text.split('\n')))

	if not lines:
		return []

	columns = [line.split(':') for line in lines]
	positions = [int(row[0]) for row in columns]

	max_position = max(positions)
	cells = [[] for _ in range(max_position)]
	for i in range(len(lines)):
		if not columns[i][1].isspace():
			cells[positions[i] - 1] = columns[i][1].split()

	return cells

def parse_processing(text):
	return np.array([float(row[0]) if row else 1 for row in vectorise(text)])

def parse_schedule(text, m, n):
	indices = [[int(cell) - 1 for cell in row] for row in vectorise(text)]

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
	return ''.join('{}: {}\n'.format(j + 1, p[j]) for j in range(n))

def format_schedule(S):
	m, n = S.shape
	return ''.join('{}: {}\n'.format(i + 1,' '.join(
		[str(j + 1) for j in range(n) if S[i, j]]
		)) for i in range(m))
