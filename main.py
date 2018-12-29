import argparse
import gui
import interface
import sys

def explain(problem_filename, schedule_filename, explanation_filename, verbose):
	success, problem = interface.load_problem(problem_filename)
	if not success:
		print(problem, file=sys.stderr)
		return
	[m_text, p_text, nfd_text, pfd_text] = problem
	success, S_text = interface.load_text(schedule_filename)
	if not success:
		print(S_text, file=sys.stderr)
		return
	success, explanation = interface.explain(m_text, p_text, nfd_text, pfd_text,
		S_text, verbose)
	if not success:
		print(explanation, file=sys.stderr)
		return
	success, error = interface.save_text(explanation_filename, explanation)
	if not success:
		print(error, file=sys.stderr)

def main():
	default_solver='glpk'

	# Construct command line interface
	parser = argparse.ArgumentParser(
		description='Explains schedules using abstract argumentation frameworks')
	parser.add_argument(
		'-v',
		'--verbose',
		help='explain schedules in more detail',
		action='store_true')
	exclusive_parser = parser.add_mutually_exclusive_group(required=True)
	exclusive_parser.add_argument(
		'-g',
		'--gui',
		nargs='?',
		metavar='solver',
		const=default_solver,
		help='displays graphical user interface where the default solver is \'{}\''.format(default_solver),
		dest='solver_name')
	exclusive_parser.add_argument(
		'-e',
		'--explain',
		help='command line interface for explanation',
		nargs=3,
		metavar=('problem', 'schedule', 'explanation'))
	args = parser.parse_args()

	# Select interface mode
	if args.explain:
		explain(args.explain[0], args.explain[1], args.explain[2], args.verbose)
	else:
		gui.start(args.verbose, args.solver_name)

if __name__ == '__main__':
	main()
