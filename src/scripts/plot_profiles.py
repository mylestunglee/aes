import matplotlib.pyplot as plt
import sys
import csv

filename = sys.argv[1]
job_samples = []
full_cpu = []
full_memory = []
partial_cpu = []
partial_memory = []

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

cpu_figure = plt.figure(1)
plt.scatter(job_samples, full_cpu, label='full precomputation')
plt.scatter(job_samples, partial_cpu, label='partial precomputation')
plt.xlabel('$n$')
plt.ylabel('elapsed time (s)')
plt.xlim([0, 100])
plt.ylim([0.6, 1])
legend = plt.legend()

cpu_figure.savefig('precomputation_cpu_small.png')
cpu_figure = plt.figure(2)
plt.scatter(job_samples, full_cpu, label='full precomputation', s=1)
plt.scatter(job_samples, partial_cpu, label='partial precomputation', s=1)
plt.xlabel('$n$')
plt.ylabel('elapsed time (s)')
plt.xlim([0, 800])
plt.ylim([0, 6])
legend = plt.legend(markerscale=5)
cpu_figure.savefig('precomputation_cpu_big.png')

memory_figure = plt.figure(3)
plt.scatter(job_samples, full_memory, label='full precomputation')
plt.scatter(job_samples, partial_memory, label='partial precomputation')
plt.xlabel('$n$')
plt.ylabel('maximum allocated memory (MiB)')
plt.xlim([0, 100])
plt.ylim([70, 80])
legend = plt.legend()
memory_figure.savefig('precomputation_memory_small.png')

memory_figure = plt.figure(4)
plt.scatter(job_samples, full_memory, label='full precomputation', s=1)
plt.scatter(job_samples, partial_memory, label='partial precomputation', s=1)
plt.xlabel('$n$')
plt.ylabel('maximum allocated memory (MiB)')
plt.xlim([0, 800])
plt.ylim([0, 400])
legend = plt.legend(markerscale=5)
memory_figure.savefig('precomputation_memory_big.png')

