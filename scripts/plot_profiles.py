import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import csv

job_samples = []
full_cpu = []
full_memory = []
partial_cpu = []
partial_memory = []
naive_cpu = []
naive_memory = []

for filename in sys.argv[1:]:
	with open(filename, 'r') as csvfile:
		spamreader = csv.reader(csvfile, delimiter=' ')
		for row in spamreader:
			if row[0] == 'full':
				job_samples.append(int(row[1]))
				full_cpu.append(float(row[2]))
				full_memory.append(float(row[3]) / 1024)
			elif row[0] == 'partial':
				partial_cpu.append(float(row[2]))
				partial_memory.append(float(row[3]) / 1024)
			elif row[0] == 'naive':
				naive_cpu.append(float(row[2]))
				naive_memory.append(float(row[3]) / 1024)

small_scale = 8
big_scale = 0.2

alpha = 0.3

def draw_legend():
	legend = plt.legend(loc='upper left')
	for lh in legend.legendHandles:
		lh.set_alpha(1)
		lh._sizes = [30]

cpu_figure = plt.figure(1)
plt.scatter(job_samples, naive_cpu, label='naive', s=small_scale, alpha=alpha, marker='x', color='grey')
plt.scatter(job_samples, full_cpu, label='full precomputation', s=small_scale, alpha=alpha, marker='x')
plt.scatter(job_samples, partial_cpu, label='partial precomputation', s=small_scale, alpha=alpha, marker='x')
plt.xlabel('$n$')
plt.ylabel('elapsed time (s)')
plt.xlim([0, 100])
plt.ylim([0.3, 0.6])
draw_legend()
cpu_figure.savefig('precomputation_cpu_small.png', dpi=300)

cpu_figure = plt.figure(2)
plt.gca().add_patch(patches.Rectangle((0, 0.3), 100, 0.3, linewidth=1, linestyle=':', edgecolor='black', facecolor='none'))
plt.scatter(job_samples, naive_cpu, label='naive', s=big_scale, alpha=alpha, marker='x', color='grey')
plt.scatter(job_samples, full_cpu, label='full precomputation', s=big_scale, alpha=alpha, marker='x')
plt.scatter(job_samples, partial_cpu, label='partial precomputation', s=big_scale, alpha=alpha, marker='x')
plt.xlabel('$n$')
plt.ylabel('elapsed time (s)')
plt.xlim([0, 800])
plt.ylim([0, 6])
draw_legend()
cpu_figure.savefig('precomputation_cpu_big.png', dpi=300)

memory_figure = plt.figure(3)
plt.scatter(job_samples, naive_memory, label='naive', s=small_scale, alpha=alpha, marker='x', color='grey')
plt.scatter(job_samples, full_memory, label='full precomputation', s=small_scale, alpha=alpha, marker='x')
plt.scatter(job_samples, partial_memory, label='partial precomputation', s=small_scale, alpha=alpha, marker='x')
plt.xlabel('$n$')
plt.ylabel('maximum allocated memory (MiB)')
plt.xlim([0, 100])
plt.ylim([50, 60])
draw_legend()
memory_figure.savefig('precomputation_memory_small.png', dpi=300)

memory_figure = plt.figure(4)
plt.gca().add_patch(patches.Rectangle((0, 50), 100, 10, linewidth=1, linestyle=':', edgecolor='black', facecolor='none'))
plt.scatter(job_samples, naive_memory, label='naive', s=big_scale, alpha=alpha, marker='x', color='grey')
plt.scatter(job_samples, full_memory, label='full precomputation', s=big_scale, alpha=alpha, marker='x')
plt.scatter(job_samples, partial_memory, label='partial precomputation', s=big_scale, alpha=alpha, marker='x')
plt.xlabel('$n$')
plt.ylabel('maximum allocated memory (MiB)')
plt.xlim([0, 800])
plt.ylim([0, 400])
draw_legend()
memory_figure.savefig('precomputation_memory_big.png', dpi=300)

