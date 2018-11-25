import pyomo.environ as en
import pyomo.opt as opt
import numpy as np

# Model the problem using the pyomo interface library
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

# Calculate the optimal schedule given a problem and a solver such as 'cplex' or 'glpk'
def calc_optimal_schedule(p, m, nfd, pfd, name):
	solver = opt.SolverFactory(name)
	model = create_model(p, m, nfd, pfd)
	result = solver.solve(model)
	C = model.C.value
	# No solution
	if C == None:
		return None, None

	# Construct schedule
	n = len(p)
	S = np.zeros((m, n), dtype=bool)
	for i in range(m):
		for j in range(n):
			S[i, j] = model.x[i, j].value != 0

	return C, S
