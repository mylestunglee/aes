import math

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

def print_framework(framework, m, n):
	width_m = len(str(m))
	width_n = len(str(n))

	# print header
	print('j i ' + '_' * m * n)

	# print rows
	for j in range(n):
		for i in range(m):
			print('{:{fill_n}} {:{fill_m}}|'.format(j if i == 0 else '', i, fill_n=width_n, fill_m=width_m) +
				''.join('x' if cell else ' ' for cell in framework[i+m*j]))
