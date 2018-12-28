import re
import matplotlib.pyplot as plt
import numpy as np
import schedule
import visualiser

integer_pattern = re.compile(r'^[0-9]+$')
float_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[0-9]+(\.[0-9]+)?)*[ \t]*\n)*$')
positions_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[1-9][0-9]*)*[ \t]*\n)*$')


def random_problem():
	m, n, p = schedule.random_problem()

	m_text = str(m)
	p_text = '\n'.join('{}: {}'.format(j + 1, p[j]) for j in range(n))
	nfd_text = ''
	pfd_text = ''

	return m_text, p_text, nfd_text, pfd_text

def random_schedule(m_text, p_text, nfd_text, pfd_text):
	if not integer_pattern.match(m_text):
		return 'number of machines syntax error'
	if not float_pattern.match(p_text):
		return 'proccessing times syntax error'
	if not positions_pattern.match(nfd_text):
		return 'negative fixed decisions syntax error'
	if not positions_pattern.match(pfd_text):
		return 'positive fixed decisions syntax error'

	m = int(m_text)
	p = parse_processing(p_text)
	n = p.shape[0]
	nfd = parse_schedule(nfd_text, m, n)
	pfd = parse_schedule(pfd_text, m, n)

	if m != nfd.shape[0]:
		return 'negative fixed decisions refers to undefined machines'
	if m != pfd.shape[0]:
		return 'positive fixed decisions refers to undefined machines'
	if n != nfd.shape[1]:
		return 'negative fixed decisions refers to undefined processing times'
	if n != pfd.shape[1]:
		return 'positive fixed decisions refers to undefined processing times'

	S = schedule.random_schedule(m, n, nfd, pfd)
	S_text = format_schedule(S)

	return S_text

def explain(m_text, p_text, nfd_text, pfd_text, S_text):
	if not integer_pattern.match(m_text):
		return 'number of machines syntax error'
	if not float_pattern.match(p_text):
		return 'proccessing times syntax error'
	if not positions_pattern.match(nfd_text):
		return 'negative fixed decisions syntax error'
	if not positions_pattern.match(pfd_text):
		return 'positive fixed decisions syntax error'
	if not positions_pattern.match(S_text):
		return 'schedule syntax error'

	m = int(m_text)
	p = parse_processing(p_text)
	n = p.shape[0]
	nfd = parse_schedule(nfd_text, m, n)
	pfd = parse_schedule(pfd_text, m, n)
	S = parse_schedule(S_text, m, n)

	if m != S.shape[0]:
		return 'schedule refers to undefined machines'
	if m != nfd.shape[0]:
		return 'negative fixed decisions refers to undefined machines'
	if m != pfd.shape[0]:
		return 'positive fixed decisions refers to undefined machines'
	if n != S.shape[1]:
		return 'schedule refers to undefined processing times'
	if n != nfd.shape[1]:
		return 'negative fixed decisions refers to undefined processing times'
	if n != pfd.shape[1]:
		return 'positive fixed decisions refers to undefined processing times'

	# Draw schedule
	plt.gcf().clear()
	visualiser.draw_schedule(p, S)

	return 'hello'

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

def format_schedule(S):
	m = S.shape[0]
	n = S.shape[1]
	return '\n'.join(
		['{}: {}'.format(i + 1, ' '.join([str(j + 1) for j in range(n) if S[i, j]])) for i in range(m)])
