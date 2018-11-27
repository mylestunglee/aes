import numpy as np
import schedule

def random_problem():
	m, n, p, S = schedule.random_scheduled_problem()

	m_text = str(m)
	p_text = '\n'.join('{}: {}'.format(j + 1, p[j]) for j in range(n))
	nfd_text = ''
	pfd_text = ''
	S_text = '\n'.join('{}: {}'.format(i + 1, ', '.join(str(x + 1) for x in np.flatnonzero(S[i, :]))) for i in range(m))

	return m_text, p_text, nfd_text, pfd_text, S_text
