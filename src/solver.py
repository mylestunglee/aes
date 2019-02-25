import numpy as np

default_solver = 'glpk'
default_time_limit = -1

# Model the problem using the pyomo interface library
def create_model(m, p, nfd, pfd):
	import pyomo.environ as en

	N = range(len(p))
	M = range(m)

	model = en.ConcreteModel()
	model.x = en.Var(M, N, domain=en.Binary)
	model.C_max = en.Var()

	# C is the longest completion time
	model.optimality = en.ConstraintList()
	for i in M:
		model.optimality.add(
			model.C_max >= sum(model.x[i, j] * p[j] for j in N))

	# Every job must be assigned
	if m > 0:
		model.feasiblity = en.ConstraintList()
		for j in N:
			model.feasiblity.add(sum(model.x[i, j] for i in M) == 1)

	# Enforce negative fixed decisions
	model.nfd = en.ConstraintList()
	for i in M:
		for j in N:
			if nfd[i, j]:
				model.nfd.add(model.x[i, j] == 0)

	# Enforce positive fixed decisions
	model.pfd = en.ConstraintList()
	for i in M:
		for j in N:
			if pfd[i, j]:
				model.pfd.add(model.x[i, j] == 1)

	# Minimise completion time
	model.obj = en.Objective(expr = model.C_max)

	return model

# Calculate the optimal schedule given a problem and a solver such as 'cplex' or 'glpk'
def optimal_schedule(m, p, nfd, pfd, solver_name, time_limit):
	import pyomo.opt as opt
	# This import is required for pyomo to recognise solvers
	import pyomo.environ as en

	solver = opt.SolverFactory(solver_name)
	model = create_model(m, p, nfd, pfd)

	if time_limit >= 0:
		if solver_name == 'cplex':
			solver.options['timelimit'] = time_limit
		elif solver_name == 'glpk':
			solver.options['tmlim'] = time_limit

	try:
		result = solver.solve(model)
	except Exception as error:
		return False, str(error)

	C_max = model.C_max.value

	# No solution
	if C_max == None:
		return False, 'No feasible solution found'

	# Construct schedule
	n = len(p)
	S = np.zeros((m, n), dtype=bool)
	for i in range(m):
		for j in range(n):
			S[i, j] = model.x[i, j].value != 0

	return True, S
