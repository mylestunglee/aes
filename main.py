import numpy as np
import solver
import visualiser
import argumentation

def main():
	p = np.array([1,1,3])
	n = np.size(p)
	m = 3
	nfd = [(0,0)]
	pfd = [(0,2)]
	S = np.array([[True, False, True], [False, True, False], [False, False, False]])
	C_max = 5

#	C_max, S = solver.calc_optimal_schedule(p, m, nfd, pfd, 'glpk')

	visualiser.print_schedule(p, C_max, S)

	ff = argumentation.create_feasiblity_framework(m, n)
	of = argumentation.create_optimality_framework(p, m, S, ff)
	fdf = argumentation.create_fixed_decision_framework(ff, nfd, pfd)
#	visualiser.print_framework(ff, m, n)
#	visualiser.print_framework(of, m, n)

	visualiser.draw_framework(ff, m, n, 'graph1')
	visualiser.draw_framework(of, m, n, 'graph2')
	visualiser.draw_framework(fdf, m, n, 'graph3')


if __name__ == '__main__':
	main()

