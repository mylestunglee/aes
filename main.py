import argparse
import gui
import interface
import sys
import schedule

def eprint(str):
	print(str, file=sys.stderr)

def main():
	default_solver = 'glpk'
	default_time_limit = -1
	default_size = 4

	# Construct command line interface
	parser = argparse.ArgumentParser(
		description='Explains make-shift schedules using abstract argumentation frameworks')
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
		const=default_size,
		help='Creates random problem with jobs and fixed decisions where m is the number of machines',
		dest='m')
	S_parser = parser.add_mutually_exclusive_group()
	S_parser.add_argument(
		'-O',
		'--optimise',
		action='store_true')
	S_parser.add_argument(
		'-s',
		'--schedule')
	S_parser.add_argument(
		'-R',
		'--random_schedule',
		action='store_true')
	parser.add_argument(
		'-o',
		'--output')
	parser.add_argument(
		'-v',
		'--verbose',
		help='explain schedules in more detail',
		action='store_true')
	parser.add_argument(
		'-t',
		'--time_limit',
		default=default_time_limit,
		type=int,
		help='maximum time for optimisation in seconds, use negative time_limit for infinite limit, default is unlimited')
	parser.add_argument(
		'-S',
		'--solver',
		default=default_solver,
		help='optimisation solver for schedule, default is \'{}\''.format(default_solver),
		dest='solver_name')
	args = parser.parse_args()

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
		if args.output:
			success, error = interface.save_problem(args.output, m_text,
				p_text, nfd_text, pfd_text)
			if not success:
				eprint(error)
		else:
			print(interface.format_problem(m_text, p_text, nfd_text,
				pfd_text), end='')
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

	# Output schedule
	if not args.graphical:
		if args.explain:
			success, output_text = interface.explain(m_text, p_text, nfd_text,
				pfd_text, S_text, args.verbose)
			if not success:
				eprint(output_text)
				return
			if args.output:
				success, error = interface.save_text(args.output,
					output_text)
				if not success:
					eprint(error)
			else:
				print(output_text, end='')
		else:
			if args.output:
				success, error = interface.save_text(args.output, S_text)
				if not success:
					eprint(error)
			else:
				print(S_text, end='')
		return

	# Start graphical
	if args.graphical:
		gui.start(m_text, p_text, nfd_text, pfd_text, S_text,
			args.explain, args.verbose, args.solver_name, args.time_limit)

if __name__ == '__main__':
	main()
