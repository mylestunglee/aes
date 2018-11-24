import math
import graphviz

# Prints ASCII representation of a schedule
def print_schedule(p, C, x):
	if C == None or x == None or not all(isinstance(p_j, int) for p_j in p):
		raise TypeError('schedule must have integer processing times')

	J = range(len(p))
	M = range(len(x))

	width = len(str(C))

	# print header
	print('{:>{fill}}|'.format('i', fill=width), end='')
	for k in range(int(C)):
		print('{:{fill}}'.format(k + 1, fill=width), end='')
	print()

	# print rows
	for i in M:
		print('{:{fill}}|'.format(i, fill=width), end='')

		for j in J:
			if x[i][j]:
				print('[{:{fill}}]'.format(j, fill=p[j] * width - 2), end='')
		print()

# Prints ASCII representation of a framework
def print_framework(framework, m, n):
	width_m = len(str(m))
	width_n = len(str(n))

	# print header
	print('j i ' + '_' * m * n)

	# print rows
	for j in range(n):
		for i in range(m):
			print('{:{fill_n}} {:{fill_m}}|'.format(
				j if i == 0 else '', i, fill_n=width_n, fill_m=width_m) +
				''.join('x' if cell else ' ' for cell in framework[i+m*j]))

# Generates an image of a framework
def draw_framework(framework, m, n, filename):
	M = range(m)
	N = range(n)

	def label(i, j):
		return '{},{}'.format(i, j)

	def create_edge(graph, i1, j1, i2, j2):
		k1 = i1+m*j1
		k2 = i2+m*j2
		# Bi-directional edges
		if framework[k1][k2] and framework[k2][k1] and k1 < k2:
			graph.edge(label(i1, j1), label(i2, j2), dir='both')
		# Uni-directional edges
		elif framework[k1][k2] and not framework[k2][k1]:
			graph.edge(label(i1, j1), label(i2, j2))
		# Loops
		elif framework[k1][k2] and k1 == k2:
			graph.edge(label(i1, j1), label(i2, j2))

	graph = graphviz.Digraph(format='svg')

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
