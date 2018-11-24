import solver
import visualiser

def main():
	p = [1, 2, 3, 4]
	m = 2
	nfd = []
	pfd = []

	C, x = solver.calc_optimal_schedule(p, m, nfd, pfd, 'glpk')
	visualiser.print_schedule(p, C, x)

if __name__ == '__main__':
	main()

