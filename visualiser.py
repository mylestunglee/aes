def print_schedule(p, C, x):
	if C == None or x == None or not all(isinstance(p_j, int) for p_j in p):
		raise TypeError('schedule must have integer processing times')

	J = range(len(p))
	M = range(len(x))

	width = 5

	# Print header
	print('{:>{fill}}|'.format('i', fill=width), end='')
	for k in range(int(C)):
		print('{:{fill}}'.format(k + 1, fill=width), end='')
	print()

	# Print rows
	for i in M:
		print('{:{fill}}|'.format(i, fill=width), end='')

		for j in J:
			if x[i][j]:
				print('[{:{fill}}]'.format(j, fill=p[j] * width - 2), end='')
		print()
