import os
import subprocess
import filecmp

test_dir = '../regression_tests/'

for filename in os.listdir(test_dir):
	if filename.endswith('.expected'):
		casename = os.path.splitext(filename)[0]
		subprocess.run([
			'python3',
			'../src/main.py',
			'-p', '{}{}.problem'.format(test_dir, casename),
			'-s', '{}{}.schedule'.format(test_dir, casename),
			'-e',
			'-o', '{}{}.actual_fp'.format(test_dir, casename)])
		subprocess.run([
			'python3',
			'../src/main.py',
			'-p', '{}{}.problem'.format(test_dir, casename),
			'-s', '{}{}.schedule'.format(test_dir, casename),
			'-e',
			'--partial',
			'-o', '{}{}.actual_pp'.format(test_dir, casename)])
		subprocess.run([
			'python3',
			'../src/main.py',
			'-p', '{}{}.problem'.format(test_dir, casename),
			'-s', '{}{}.schedule'.format(test_dir, casename),
			'-e',
			'--naive',
			'-o', '{}{}.actual_n'.format(test_dir, casename)])

		try:
			pass_fp = filecmp.cmp('{}{}.expected'.format(test_dir, casename),
				'{}{}.actual_fp'.format(test_dir, casename))
		except FileNotFoundError:
			pass_fp = False

		try:
			pass_pp = filecmp.cmp('{}{}.expected'.format(test_dir, casename),
				'{}{}.actual_pp'.format(test_dir, casename))
		except FileNotFoundError:
			pass_pp = False
		try:
			pass_n = filecmp.cmp('{}{}.expected'.format(test_dir, casename),
				'{}{}.actual_n'.format(test_dir, casename))
		except FileNotFoundError:
			pass_n = False

		if pass_fp:
			os.remove('{}{}.actual_fp'.format(test_dir, casename))

		if pass_pp:
			os.remove('{}{}.actual_pp'.format(test_dir, casename))

		if pass_n:
			os.remove('{}{}.actual_n'.format(test_dir, casename))

		if pass_fp and pass_pp and pass_n:
			print('Passed: {}'.format(casename))
		else:
			print('Failed: {}'.format(casename))
