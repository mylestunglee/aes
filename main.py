import numpy as np
import solver
import visualiser
import argumentation

def main():
	p = np.array([1,1,1])
	n = np.size(p)
	m = 3
	nfd = []
	pfd = []

	C, S = solver.calc_optimal_schedule(p, m, nfd, pfd, 'glpk')
	visualiser.print_schedule(p, C, S)

	f = argumentation.create_feasiblity_framework(m, n)
	visualiser.print_framework(f, m, n)
	visualiser.draw_framework(f, m, n, 'graph')


if __name__ == '__main__':
	main()

