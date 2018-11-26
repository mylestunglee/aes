import math
import graphviz
import numpy as np
import matplotlib.pyplot as plt

# Prints ASCII representation of a schedule
def print_schedule(p, C, S):
	if C == None or S is None:
		raise TypeError('no schedule')

	J = range(len(p))
	M = range(np.shape(S)[0])

	width = len(str(C)) + 2

	# Print header
	print('{:>{fill}}|'.format('i', fill=width), end='')
	for k in range(int(C)):
		print('{:{fill}}'.format(k + 1, fill=width), end='')
	print()

	# Print rows
	for i in M:
		print('{:{fill}}|'.format(i, fill=width), end='')

		for j in J:
			if S[i, j]:
				print('[{:{fill}}]'.format(j, fill=p[j] * width - 2), end='')
		print()

# Prints ASCII representation of a framework
def print_framework(f, m, n):
	width_m = len(str(m))
	width_n = len(str(n))
	M = range(m)
	N = range(n)

	# Print header
	print('j i ' + '_' * m * n)

	# Print rows
	for j1 in N:
		for i1 in M:
			print('{:{fill_n}} {:{fill_m}}|'.format(
				j1 if i1 == 0 else '', i1, fill_n=width_n, fill_m=width_m), end='')

			for j2 in N:
				for i2 in M:
					if f[i1, j1, i2, j2]:
						print('x', end='')
					else:
						print(' ', end='')
			print()

# Generates an image of a framework
def draw_framework(f, m, n, filename):
	M = range(m)
	N = range(n)

	def label(i, j):
		return '{},{}'.format(i, j)

	def create_edge(graph, i1, j1, i2, j2):
		k1 = i1+m*j1
		k2 = i2+m*j2
		# Bi-directional edges
		if f[i1, j1, i2, j2] and f[i2, j2, i1, j1] and k1 < k2:
			graph.edge(label(i1, j1), label(i2, j2), dir='both')
		# Uni-directional edges
		elif f[i1, j1, i2, j2] and not f[i2, j2, i1, j1]:
			graph.edge(label(i1, j1), label(i2, j2))
		# Loops
		elif f[i1, j1, i2, j2] and k1 == k2:
			graph.edge(label(i1, j1), label(i2, j2))

	graph = graphviz.Digraph(format='png')

	# Construct nodes
	for i in M:
		for j in N:
			graph.node(label(i, j))

	# Construct edges
	for i1 in M:
		for j1 in N:
			for i2 in M:
				for j2 in N:
					create_edge(graph, i1, j1, i2, j2)

	#print(graph.source)
	graph.render(filename)

# Generates a column chart of jobs against machines
def draw_schedule(p, S):
#	S = np.random.choice(a=[False, True], size=(m, n), p=[0.5, 0.5])
#	p = np.random.exponential(0.5, n)
	(m, n) = S.shape

	N = np.arange(n)
	M = np.arange(m)

	accum = np.zeros(m)

	for j in N:
	    widths = S[:, j].astype(float) * p[j]
	    bars = plt.barh(M, widths, left=accum)
	    accum += widths

	    for bar in bars:
	        if bar.get_width() > 0:
	            plt.text(
	                bar.get_x() + bar.get_width() / 2,
	                bar.get_y() + bar.get_height() / 2,
	                j,
	                ha='center',
	                va='center')

	plt.yticks(M, M)
	plt.xlabel('time')
	plt.ylabel('machine')

	plt.gca().invert_yaxis()

	plt.show()
