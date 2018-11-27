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
	S_text = '\n'.join('{}: {}'.format(i + 1, ', '.join(str(x + 1) for x in np.flatnonzero(S[i, :]))) for i in range(m))

	return m_text, p_text, nfd_text, pfd_text, S_text

def explain(p_text, S_text):
	S = parse_schedule(S_text)

	p = parse_processing(p_text)

	# Draw schedule
	plt.gcf().clear()
	visualiser.draw_schedule(p, S)

def vectorise(text):
	lines = list(filter(None, text.split('\n')))
	columns = [line.split(':') for line in lines]
	positions = [int(row[0]) for row in columns]
	max_position = max(positions)
	cells = [[] for _ in range(max_position)]
	for i in range(len(lines)):
		if not columns[i][1].isspace():
			cells[positions[i] - 1] = columns[i][1].split(',')

	return cells

def parse_processing(text):
	return np.array([float(row[0]) for row in vectorise(text)])

def parse_schedule(text):
	cells = [[int(cell) - 1 for cell in row] for row in vectorise(text)]

	m = len(cells)
	n = max(max(row) for row in cells) + 1

	S = np.zeros((m, n), dtype=bool)
	for i in range(m):
		for j in cells[i]:
			S[i, j] = True

	return S
