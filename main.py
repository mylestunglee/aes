import pyomo.environ as en
import pyomo.opt as opt

def create_model(p, m, nfd, pfd):
	J = range(len(p))
	M = range(m)

	model = en.ConcreteModel()
	model.x = en.Var(M, J, domain=en.Binary)
	model.C = en.Var()

	# C is the longest completion time
	model.optimality = en.ConstraintList()
	for i in M:
		model.optimality.add(
			model.C >= sum(model.x[i, j] * p[j] for j in J))

	# Every job must be assigned
	model.feasiblity = en.ConstraintList()
	for j in J:
		model.feasiblity.add(sum(model.x[i, j] for i in M) == 1)

	# Enforce negative fixed decisions
	model.nfd = en.ConstraintList()
	for i, j in nfd:
		model.nfd.add(model.x[i, j] == 0)

	# Enforce positive fixed decisions
	model.pfd = en.ConstraintList()
	for i, j in pfd:
		model.pfd.add(model.x[i, j] == 1)

	# Minimise completion time
	model.obj = en.Objective(expr = model.C)

	return model

def solve_model(model, n, m):
	solver = opt.SolverFactory('glpk')
	result = solver.solve(model)
	C = model.C.value
	# No solution
	if C == None:
		return None, None

	# Construct schedule
	return int(C), [[model.x[i, j].value != 0 for j in range(n)] for i in range(m)]

def print_solution(p, C, x):
	if C == None or x is None:
		print('No feasible solution')
		return

	J = range(len(p))
	M = range(len(x))

	width = 5

	# Print header
	print('{:>{fill}}|'.format('i', fill=width), end='')
	for k in range(C):
		print('{:{fill}}'.format(k + 1, fill=width), end='')
	print()

	# Print rows
	for i in M:
		print('{:{fill}}|'.format(i, fill=width), end='')

		for j in J:
			if x[i][j]:
				print('[{:{fill}}]'.format(j, fill=p[j] * width - 2), end='')
		print()

def calc_model():
	p = [1, 2, 3, 4]
	m = 2
	nfd = []
	pfd = []

	model = create_model(p, m, nfd, pfd)
	C, x = solve_model(model, len(p), m)
	print_solution(p, C, x)

calc_model()
