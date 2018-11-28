import re
import matplotlib.pyplot as plt
import numpy as np
import schedule
import visualiser

def random_problem():
	m, n, p, S = schedule.random_scheduled_problem()

	m_text = str(m)
	p_text = '\n'.join('{}: {}'.format(j + 1, p[j]) for j in range(n))
	nfd_text = ''
	pfd_text = ''
	S_text = '\n'.join('{}: {}'.format(i + 1, ' '.join(str(x + 1) for x in np.flatnonzero(S[i, :]))) for i in range(m))

	return m_text, p_text, nfd_text, pfd_text, S_text

def explain(m_text, p_text, S_text, nfd_text, pfd_text):
	integer_pattern = re.compile(r'^[0-9]+$')
	float_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[0-9]+(\.[0-9]+)?)*[ \t]*\n)*$')
	positions_pattern = re.compile(r'^([ \t]*[1-9][0-9]*[ \t]*:([ \t]+[1-9][0-9]*)*[ \t]*\n)*$')

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
	S = parse_schedule(S_text)

	if m != S.shape[0]:
		return 'number of machines does not match schedule'

	n = p.shape[0]

	if n < S.shape[1]:
		return 'schedule refers to undefined processing times'
	# There unschedued jobs, extend S to explictly non-allocate these jobs
	elif n > S.shape[1]:
		S = np.hstack((S, np.zeros((m, n - S.shape[1]), dtype=bool)))

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
	return np.array([float(row[0]) for row in vectorise(text)])

def parse_schedule(text):
	indices = [[int(cell) - 1 for cell in row] for row in vectorise(text)]

	m = len(indices)
	n = max(max(row) for row in indices) + 1 if any(indices) else 0

	S = np.zeros((m, n), dtype=bool)
	for i in range(m):
		for j in indices[i]:
			S[i, j] = True

	return S
