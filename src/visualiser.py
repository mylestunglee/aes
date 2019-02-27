import numpy as np
import matplotlib.pyplot as plt
import schedule
import formatter

# Generates a column chart of jobs against machines
def draw_schedule(p, S, S_old=None):
	(m, n) = S.shape
	if S_old is None:
		S_old = S

	max_jobs = np.max(np.sum(S, axis=1)) if m > 0 and n > 0 else 0
	if max_jobs > 10 or m >= 30:
		draw_schedule_undetailed(p, S)
	else:
		draw_schedule_detailed(p, S, S_old)

	plt.xlabel('time')
	plt.ylabel('machine')
	plt.gca().invert_yaxis()
	# Plot fills exactly to axis boundaries
	plt.margins(0, 0)
	# Trim top and right border of image
	plt.subplots_adjust(top = 1)

def draw_schedule_undetailed(p, S):
	(m, _) = S.shape

	C = schedule.calc_completion_times(p, S)
	plt.barh(np.arange(m), C, color='grey')

	plt.yticks([])

# Draw cascade chart in detail, but may take long time for large charts
def draw_schedule_detailed(p, S, S_old):
	(m, n) = S.shape

	N = np.arange(n)
	M = np.arange(m)

	accum = np.zeros(m)
	thicklinewidth = 3

	# Draw currently assigned jobs
	for j in N:
		widths = S[:, j].astype(float) * p[j]

		# Plot main boxes
		bars = plt.barh(M, widths, left=accum, facecolor='lightgrey',
			edgecolor='grey', linewidth=S[:, j].astype(int))

		# Next jobs
		accum += widths

		for bar in bars:
			# Set job label
			if bar.get_width() > 0:
				plt.text(
					bar.get_x() + bar.get_width() / 2,
					bar.get_y() + bar.get_height() / 2,
					formatter.number_to_letters(j),
					ha='center',
					va='center')

	# Draw newly assigned jobs
	accum = np.zeros(m)
	for j in N:
		widths = S[:, j].astype(float) * p[j]

		plt.barh(M, widths, left=accum, facecolor='none',
			edgecolor='black', linewidth=thicklinewidth*
			np.logical_and(S[:, j], np.logical_not(S_old[:, j])).astype(int),
			linestyle=':')

		# Next jobs
		accum += widths

	# Draw previously assigned jobs
	for j in N:
		draw = np.logical_and(np.logical_not(S[:, j]), S_old[:, j])
		widths = draw.astype(float) * p[j]

		# Thicker dashes for removed jobs
		bars = plt.barh(M, widths, left=accum, facecolor='none', edgecolor='black',
			linewidth=thicklinewidth*draw.astype(int), linestyle=':')
		accum += widths

		for bar in bars:
			# Set job label
			if bar.get_width() > 0:
				plt.text(
					bar.get_x() + bar.get_width() / 2,
					bar.get_y() + bar.get_height() / 2,
					formatter.number_to_letters(j),
					ha='center',
					va='center')

	plt.yticks(M, M + 1)
