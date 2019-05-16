import argparse
import graphical
import interface
import sys
import schedule
import solver

def eprint(str):
	print(str, file=sys.stderr)

def try_output(filename, text):
	if filename:
		success, error = interface.save_text(filename, text)
		if not success:
			eprint(error)
	else:
		print(text, end='')

# Construct command line interface
def get_arguments():
	parser = argparse.ArgumentParser(
		description='Explains makespan schedules using abstract argumentation frameworks')
	parser.add_argument(
		'-g',
		'--graphical',
		help='displays graphical user interface',
		action='store_true')
	parser.add_argument(
		'-e',
		'--explain',
		help='generate explanation',
		action='store_true')
	P_parser = parser.add_mutually_exclusive_group()
	P_parser.add_argument(
		'-p',
		'--problem')
	P_parser.add_argument(
		'-r',
		'--random_problem',
		nargs='?',
		type=int,
		metavar='M',
		const=schedule.default_m,
		help='creates random problem with jobs and fixed decisions where M is the number of machines',
		dest='m')
	S_parser = parser.add_mutually_exclusive_group()
	S_parser.add_argument(
		'-O',
		'--optimise',
		action='store_true',
		help='uses SOLVER_NAME to find most efficient schedule')
	S_parser.add_argument(
		'-s',
		'--schedule')
	S_parser.add_argument(
		'-R',
		'--random_schedule',
		action='store_true')
	parser.add_argument(
		'-o',
		'--output',
		help='output filename for selected problem, schedule or explanation')
	E_parser = parser.add_mutually_exclusive_group()
	E_parser.add_argument(
		'--partial',
		help='use partial framework construction to favour memory over CPU',
		action='store_true')
	E_parser.add_argument(
		'--naive',
		help='do not use argumentation',
		action='store_true')
	parser.add_argument(
		'-f',
		'--fixed_decision_aware',
		help='force efficiency to respect fixed decisions',
		action='store_true')
	parser.add_argument(
		'-t',
		'--time_limit',
		default=solver.default_time_limit,
		type=int,
		help='maximum time for optimisation in seconds, use negative time_limit for infinite limit, default is unlimited time')
	parser.add_argument(
		'-S',
		'--solver',
		default=solver.default_solver,
		help='optimisation solver for schedule, default is \'{}\''.
			format(solver.default_solver),
		dest='solver_name')
	return parser.parse_args()

def run_arguments(args):
	# Get problem
	if args.problem:
		success, problem = interface.load_problem(args.problem)
		if not success:
			eprint(problem)
			return
		[m_text, p_text, nfd_text, pfd_text] = problem
	elif args.m:
		if args.m <= 0:
			eprint('m must be positive')
			return
		m, p, nfd, pfd = schedule.random_problem(args.m)
		m_text = str(m)
		p_text = interface.format_processing_times(p)
		nfd_text = interface.format_schedule(nfd)
		pfd_text = interface.format_schedule(pfd)
	else:
		m_text = '0'
		p_text = ''
		nfd_text = ''
		pfd_text = ''

	# Output problem
	if (not args.optimise and not args.schedule and
		not args.random_schedule and not args.graphical and
		not args.explain):
		try_output(args.output,
			interface.format_problem(m_text, p_text, nfd_text, pfd_text))
		return

	# Get schedule
	success = True
	if args.schedule:
		success, S_text = interface.load_text(args.schedule)
	elif args.optimise:
		success, S_text = interface.optimal_schedule(m_text, p_text, nfd_text,
			pfd_text, args.solver_name, args.time_limit)
	elif args.random_schedule and (args.problem or args.m):
		success, S_text = interface.random_schedule(m_text, p_text, nfd_text,
			pfd_text)
	else:
		S_text = ''
	if not success:
		eprint(S_text)
		return

	options = {
		'graphical': args.graphical,
		'partial': args.partial,
		'naive': args.naive,
		'fixed': args.fixed_decision_aware
	}

	# Do something with a schedule
	if not args.graphical:
		if args.explain:
			success, result = interface.explain(m_text, p_text, nfd_text,
				pfd_text, S_text, options)
			if not success:
				eprint(result)
				return
			output_text = '\n'.join(reason for reason, _ in result) + '\n'
			try_output(args.output, output_text)
		else:
			try_output(args.output, S_text)
		return

	# Start graphical
	if args.graphical:
		graphical.start(m_text, p_text, nfd_text, pfd_text, S_text,
			args.explain, options, args.solver_name, args.time_limit)

def main():
	args = get_arguments()
	run_arguments(args)

if __name__ == '__main__':
	main()
