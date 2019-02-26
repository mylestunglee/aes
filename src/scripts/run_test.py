import os
import subprocess
import filecmp

test_dir = '../tests/'

for filename in os.listdir('../tests/'):
	if filename.endswith('.expected'):
		casename = os.path.splitext(filename)[0]
		subprocess.run([
			'python3',
			'../main.py',
			'-p', '{}{}.problem'.format(test_dir, casename),
			'-s', '{}{}.schedule'.format(test_dir, casename),
			'-e',
			'-o', '{}{}.actual_fp'.format(test_dir, casename)])
		subprocess.run([
			'python3',
			'../main.py',
			'-p', '{}{}.problem'.format(test_dir, casename),
			'-s', '{}{}.schedule'.format(test_dir, casename),
			'-e',
			'--partial',
			'-o', '{}{}.actual_pp'.format(test_dir, casename)])

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

		if pass_fp and pass_pp:
			print('Passed: {}'.format(casename))
			os.remove('{}{}.actual_fp'.format(test_dir, casename))
			os.remove('{}{}.actual_pp'.format(test_dir, casename))
		else:
			print('Failed: {}'.format(casename))
