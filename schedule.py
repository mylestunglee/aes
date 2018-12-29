import numpy as np
import solver
import visualiser
import argumentation

def main():
#	p = np.array([1,1,3])
#	n = 3
#	m = 3
#	nfd = [(0,0)]
#	pfd = [(0,2)]
#	C_max, S = solver.calc_optimal_schedule(m, p, nfd, pfd, 'glpk')

#	ff = argumentation.create_feasiblity_framework(m, n)
#	of = argumentation.create_optimality_framework(m, p, S, ff)
#	fdf = argumentation.create_fixed_decision_framework(ff, nfd, pfd)

	_, _, p, S = random_scheduled_problem()
	visualiser.draw_schedule(p, S)

def random_problem():
	m = np.random.poisson(5)
	n = np.random.poisson(10)
	p = np.random.exponential(3, n) + 0.5
	return m, n, p

def random_schedule(m, n, nfd, pfd):
	pr = 1 / m if m > 0 else 0
	S = np.random.choice(a=[False, True], size=(m, n), p=[1 - pr, pr])
	return S

# Calculates completion time vector [C_i for i in M]
def calc_completion_times(p, S):
	return S.astype(int).dot(p)

if __name__ == '__main__':
	main()
