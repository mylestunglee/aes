import numpy as np
import sys
sys.path.append('../src/')
import schedule

def test_calc_completion_times():
	p = np.array([1, 2, 3])
	S = np.array(
		[[True, False, False],
		[False, True, True]])
	C = np.array([1, 5])

	assert np.array_equal(schedule.calc_completion_times(p, S), C)
