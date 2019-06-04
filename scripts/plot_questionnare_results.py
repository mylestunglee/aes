import matplotlib.pyplot as plt
import numpy as np

group_one_results = np.array([
	[0, 2, 0, 8],
	[2, 1, 2, 5],
	[3, 0, 0, 7],
	[2, 5, 0, 3],
	[2, 1, 3, 4]])

group_two_results = np.array([
	[0, 0, 0, 12],
	[0, 0, 3, 8],
	[1, 1, 1, 6],
	[1, 0, 0, 7],
	[0, 0, 7, 1]])

questions = np.arange(1, 6)

for name, results in [('one', group_one_results), ('two', group_two_results)]:
	bottom = np.zeros(5)
	plt.bar(questions, results[:, 0], color='red', bottom=bottom, label='Incorrect')
	bottom += results[:, 0]
	plt.bar(questions, results[:, 1], color='yellow', bottom=bottom, label='Incomplete')
	bottom += results[:, 1]
	plt.bar(questions, results[:, 2], color='lime', bottom=bottom, label='Complex')
	bottom += results[:, 2]
	plt.bar(questions, results[:, 3], color='green', bottom=bottom, label='Correct')

	plt.xlabel('Question')
	plt.ylabel('Frequency')

	plt.legend(bbox_to_anchor=(1,1), loc="upper left")

	plt.subplots_adjust(right=0.75)

	plt.savefig('questionnaire_results_group_{}.png'.format(name))
	plt.close()
