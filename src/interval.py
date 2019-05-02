import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import formatter

# m: number of machines
# n: number of jobs
# T: number of time indices
# S: schedule
# p: integer processing times
# s: inclusive integer earlest starting times
# f: exclusive itneger latest finishing times

def new_schedule(m, n, T):
	return np.zeros((m, n, T), dtype=bool)

def new_framework(m, n, T, relation):
	framework = np.zeros((m, n, T, m, n, T), dtype=bool)
	for i1 in range(m):
		for i2 in range(m):
			for j1 in range(n):
				for j2 in range(n):
					for t1 in range(T):
						for t2 in range(T):
							if relation(i1, j1, t1, i2, j2, t2):
								framework[i1, j1, t1, i2, j2, t2] = True
	return framework

def alpha_relation(i1, j1, t1, i2, j2, t2):
	return i1 == i2 and j1 != j2 or t1 != t2

def new_set_relation(S):
	def relation(i1, j1, t1, i2, j2, t2):
		return i1 == i2 and j1 == j2 and t1 == t2 and S[i1, j1, t1]

def draw_schedule(m, n, T, p, s, f, nfd, pfd, S):
	M = np.arange(m)
	N = np.arange(n)
	Tee = np.arange(T)
	MN = np.arange(m * n)

	fig = plt.figure()

	# hatch parameters
	mpl.rcParams['hatch.linewidth'] = 5
	mpl.rcParams['hatch.color'] = 'grey'

	# Setup axis
	subplot = fig.add_subplot(111)
	right_axis = subplot.twinx()
	subplot.set_xlabel('time')
	subplot.set_ylabel('machine')
	right_axis.set_ylabel('job')
	subplot.xaxis.set_ticks(np.arange(T + 1))
	subplot.set_xlim(0, T)
	subplot.set_ylim(-0.5, m*n - 0.5)
	subplot.yaxis.set_ticks(MN)
	subplot.yaxis.set_ticklabels(reversed([str(i + 1) for i in M] * n))
	right_axis.yaxis.set_ticks(np.arange(n))
	right_axis.yaxis.set_ticklabels(reversed([formatter.number_to_letters(j) for j in N]))
	right_axis.set_ylim(-0.5, n - 0.5)
	# Align right axis with left
	right_axis.barh(N, np.zeros(n))

	X = nfd.copy()

	# Set ignores
	for i in M:
		for j in N:
			# gamma
			X[i, j, :s[i, j]] = True
			# delta
			X[i, j, f[i, j]:] = True
			# eta
			for t1 in Tee:
				if pfd[i, j, t1]:
					for t2 in Tee:
						if t2 <= t1 - p[j] or t2 >= t1 + p[j]:
							X[i, j, t2] = True
	# zeta
	for i1 in M:
		for j in N:
			if np.any(pfd[i1, j, :]):
				# clear all machines that are not i1
				for i2 in M:
					if i1 != i2:
						X[i2, j, :] = True

	# Draw banded
	subplot.barh(MN, [((k // m) % 2) * T for k in MN], facecolor='whitesmoke', height=1)

	widths = np.repeat(p, m)[::-1]

	# Draw assigments on over jobs
	S2 = S.astype(int) # compute MxNxTee matrix where non-zeros are processing times
	for j in N:
		S2[:, j, :] *= p[j]
	assigned = np.sum(S2, axis=1) # aggregate over job assignments
	S3 = new_schedule(m, n, T).astype(int) # copy aggregate to each job to display
	for j in N:
		S3[:, j, :] = assigned

	for t in Tee:
		linewidths = S3[:, :, t].T.flatten().astype(int)[::-1]

		bars = subplot.barh(MN, linewidths, hatch='/',
			facecolor='None', left=t)
	# Draw ignores
	for t in Tee:
		# transpose: order is MN, not NM; convert from boolean to int; reverse y axis
		subplot.barh(MN, X[:, :, t].T.flatten().astype(int)[::-1],
			left=t, facecolor='grey')

	# Draw assigments
	for t in Tee:
		linewidths = S[:, :, t].T.flatten().astype(int)[::-1]

		bars = subplot.barh(MN, np.multiply(widths, linewidths), facecolor='black', left=t)

	plt.show()

m = 2
n = 3
T = 6
p = np.array([2,3,2])
s = np.array([[0,1,0],[1,0,0]])
f = np.array([[4,6,6],[5,6,6]])

S = new_schedule(m, n, T)
S[0, 0, 0] = True
S[0, 2, 2] = True
S[1, 1, 3] = True

nfd = new_schedule(m, n, T)
nfd[1, 1, 2] = True
pfd = new_schedule(m, n, T)
pfd[0, 2, 2] = True

draw_schedule(m, n, T, p, s, f, nfd, pfd, S)
