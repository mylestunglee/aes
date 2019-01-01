import argparse
import gui
import interface
import sys

def eprint(str):
	print(str, file=sys.stderr)

def optimise(problem_filename, output_filename, solver_name, time_limit):
	# Load problem
	success, problem = interface.load_problem(problem_filename)
	if not success:
		eprint(problem)
		return
	[m_text, p_text, nfd_text, pfd_text] = problem

	# Get schedule
	success, S_text = interface.optimal_schedule(m_text, p_text, nfd_text,
		pfd_text, solver_name, time_limit)
	if not success:
		eprint(S_text)
		return

	# Output schedule
	if output_filename:
		success, error = interface.save_text(output_filename, S_text)
		if not success:
			eprint(error)
	else:
		print(S_text, end='')

def explain(problem_filename, schedule_filename, explanation_filename, verbose,
		solver_name, time_limit):
	# Load problem
	success, problem = interface.load_problem(problem_filename)
	if not success:
		eprint(problem)
		return
	[m_text, p_text, nfd_text, pfd_text] = problem

	# Get schedule
	if schedule_filename:
		success, S_text = interface.load_text(schedule_filename)
	else:
		success, S_text = interface.optimal_schedule(m_text, p_text, nfd_text,
			pfd_text, solver_name, time_limit)
	if not success:
		eprint(S_text)
		return

	# Output explanation
	success, explanation = interface.explain(m_text, p_text, nfd_text, pfd_text,
		S_text, verbose)
	if not success:
		eprint(explanation)
		return
	if explanation_filename:
		success, error = interface.save_text(explanation_filename, explanation)
		if not success:
			eprint(error)
	else:
		print(explanation, end='')

def main():
	default_solver = 'glpk'
	default_time_limit = -1

	# Construct command line interface
	parser = argparse.ArgumentParser(
		description='Explains make-shift schedules using abstract argumentation frameworks')
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
		'-g',
		'--graphical',
		help='displays graphical user interface',
		action='store_true')
	parser.add_argument(
		'-S',
		'--solver',
		default=default_solver,
		help='optimisation solver for schedule, default is \'{}\''.format(default_solver),
		dest='solver_name')
	parser.add_argument(
		'-e',
		'--explain',
		help='generate explanation',
		action='store_true')
	parser.add_argument(
		'-p',
		'--problem')
	parser.add_argument(
		'-s',
		'--schedule')
	parser.add_argument(
		'-o',
		'--output')
	parser.add_argument(
		'-O',
		'--optimise',
		action='store_true')
	args = parser.parse_args()

	if args.optimise and args.schedule:
		eprint('Optimise and schedule cannot selected together')

	if args.graphical:
		gui.start(args.verbose, args.solver_name, args.time_limit)
	elif args.explain:
		if not args.problem:
			eprint('Problem required')
			return
		if not args.optimise and not args.schedule:
			eprint('Optimise or schedule required')
			return
		explain(args.problem, args.schedule, args.output, args.verbose,
			args.solver_name, args.time_limit)
	elif args.optimise:
		if not args.problem:
			eprint('Problem required')
		optimise(args.problem, args.output, args.solver_name, args.time_limit)

if __name__ == '__main__':
	main()
