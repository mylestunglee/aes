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

group_three_results = np.array([
	[0, 0, 0, 7],
	[0, 1, 1, 5],
	[1, 4, 0, 2],
	[2, 0, 0, 5],
	[1, 0, 1, 5]])

questions = np.arange(5) + 1
groups = np.arange(3) + 1

# draw plot for each group
for name, results in [('one', group_one_results), ('two', group_two_results), ('three', group_three_results)]:
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

summary = np.array([
	group_one_results.sum(axis=0) / group_one_results.sum(),
	group_two_results.sum(axis=0) / group_two_results.sum(),
	group_three_results.sum(axis=0) / group_three_results.sum()])

# draw plot for summary plot
bottom = np.zeros(3)
plt.bar(groups, summary[:, 0], color='red', bottom=bottom, label='Incorrect')
bottom += summary[:, 0]
plt.bar(groups, summary[:, 1], color='yellow', bottom=bottom, label='Incomplete')
bottom += summary[:, 1]
plt.bar(groups, summary[:, 2], color='lime', bottom=bottom, label='Complex')
bottom += summary[:, 2]
plt.bar(groups, summary[:, 3], color='green', bottom=bottom, label='Correct')

plt.xticks(groups, ['No Explanations', 'Simple Explanations', 'Interactive Explanations'], rotation=-15)
plt.yticks(np.arange(0, 11, 2) / 10, ['{:.0%}'.format(x / 10) for x in range(0, 11, 2)])
plt.ylabel('Responses')

plt.legend(bbox_to_anchor=(1,1), loc="upper left")

plt.subplots_adjust(right=0.75, bottom=0.2)

plt.savefig('questionnaire_results_summary.png', dpi=300)
