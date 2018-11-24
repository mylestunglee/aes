import solver
import visualiser
import argumentation

def main():
	p = [1, 2, 3, 4]
	n = len(p)
	m = 3
	nfd = []
	pfd = []

	#C, x = solver.calc_optimal_schedule(p, m, nfd, pfd, 'glpk')
	#visualiser.print_schedule(p, C, x)
	f = argumentation.create_feasiblity_framework(m, n)
	#visualiser.print_framework(f, m, n)
	visualiser.draw_framework(f, m, n, 'graph')
	

if __name__ == '__main__':
	main()

