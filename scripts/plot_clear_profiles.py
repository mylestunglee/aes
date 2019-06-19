import numpy as np
import csv
import matplotlib.pyplot as plt

X = np.arange(1001)

def empty_lookup():
	return [[] for _ in X]

cpu = {
	'full': empty_lookup(),
	'partial': empty_lookup(),
	'naive': empty_lookup(),
}

memory = {
	'full': empty_lookup(),
	'partial': empty_lookup(),
	'naive': empty_lookup(),
}

with open('log.csv', 'r') as csvfile:
	spamreader = csv.reader(csvfile, delimiter=' ')
	for row in spamreader:
		type = row[0]

		if type in cpu:
			n = int(row[1])
			time = float(row[2])
			mem = int(row[3])

			cpu[type][n].append(time)
			memory[type][n].append(mem)

Y = np.arange(801)

def aggregate(data):
	return {
		key: [np.mean(values) for n, values in enumerate(data[key]) if n <= 800]
		for key in data
	}

def quad_fit(data):
	return {
		key: np.poly1d(np.polyfit(Y,
			[np.mean(values) for n, values in enumerate(data[key]) if n <= 800],
				3))
		for key in data
	}

"""
fit_cpu = quad_fit(memory)
#agg_mem = aggregate(memory)

plt.rcParams.update({'font.size': 16})
pattern = {
	'full': '-',
	'partial': '-',
	'naive': ':'
}

for key in fit_cpu:
	plt.plot(Y, fit_cpu[key](Y) / 1024, label=key, linewidth=3, ls=pattern[key])

plt.legend()
plt.ylabel('maximum memory allocated (MiB)')
plt.xlabel('$n$')
plt.show()
"""
