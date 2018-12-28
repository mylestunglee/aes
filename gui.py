import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import interface
matplotlib.use("TkAgg")

def main():
	root = tk.Tk()

	def quit():
		# Close matplotlib figure so program is not left hanging
		plt.close('all')
		root.quit()

	def random_problem():
		# Generate random problem
		m_text, p_text, nfd_text, pfd_text = interface.random_problem()

		# Set textboxes
		spinbox_replace(m_spinbox, m_text)
		textbox_replace(p_textbox, p_text)
		textbox_replace(nfd_textbox, nfd_text)
		textbox_replace(pfd_textbox, pfd_text)

	def load_problem():
		# Locate file
		filename = tk.filedialog.askopenfilename()

		# Handle closed dialog
		if not filename:
			return

		# Read file
		success, texts = interface.load_problem(filename)

		if success:
			[m_text, p_text, nfd_text, pfd_text] = texts

			spinbox_replace(m_spinbox, m_text)
			textbox_replace(p_textbox, p_text)
			textbox_replace(nfd_textbox, nfd_text)
			textbox_replace(pfd_textbox, pfd_text)
		else:
			textbox_replace(output_textbox, texts)

	def save_problem():
		# Locate file
		filename = tk.filedialog.asksaveasfilename()

		# Handle closed dialog
		if not filename:
			return

		# Write file
		success, error = interface.save_problem(
			filename,
			m_spinbox.get(),
			p_textbox.get('1.0', tk.END),
			nfd_textbox.get('1.0', tk.END),
			pfd_textbox.get('1.0', tk.END))

		if not success:
			textbox_replace(output_textbox, error)

	def optimise():
		pass

	def random_schedule():
		# Generate problem
		success, text = interface.random_schedule(
			m_spinbox.get(),
			p_textbox.get('1.0', tk.END),
			nfd_textbox.get('1.0', tk.END),
			pfd_textbox.get('1.0', tk.END))

		if success:
			textbox_replace(S_textbox, text)
		else:
			textbox_replace(output_textbox, text)

	def load_schedule():
		# Locate file
		filename = tk.filedialog.askopenfilename()

		# Handle closed dialog
		if not filename:
			return

		# Read file
		success, text = interface.load_text(filename)

		if success:
			textbox_replace(S_textbox, text)
		else:
			textbox_replace(output_textbox, text)

	def save_file(textbox):
		# Locate file
		filename = tk.filedialog.asksaveasfilename()

		# Handle closed dialog
		if not filename:
			return

		# Write file
		success, error = interface.save_text(
			filename,
			textbox.get('1.0', tk.END))

		if not success:
			textbox_replace(output_textbox, error)

	def save_schedule():
		save_file(S_textbox)

	def explain():
		text = interface.explain(
			m_spinbox.get(),
			p_textbox.get('1.0', tk.END),
			nfd_textbox.get('1.0', tk.END),
			pfd_textbox.get('1.0', tk.END),
			S_textbox.get('1.0', tk.END))

		textbox_replace(output_textbox, text)

		fig.canvas.draw()

	def save_output():
		save_file(output_textbox)

	root.protocol("WM_DELETE_WINDOW", quit)
	root.title('Argumentative Explainable Scheduler')

	# Create widgets
	left_frame = tk.Frame(root)

	problem_frame = tk.LabelFrame(left_frame, text='Problem')
	problem_command_frame = tk.Frame(problem_frame)
	load_problem_button = tk.Button(problem_command_frame, text='Load', command=load_problem)
	save_problem_button = tk.Button(problem_command_frame, text='Save', command=save_problem)
	random_problem_button = tk.Button(problem_command_frame, text='Randomise', command=random_problem)
	m_label = tk.Label(problem_frame, text='Number of machines', anchor=tk.E)
	m_spinbox = tk.Spinbox(problem_frame, from_=0, to_=tk.sys.maxsize)
	p_label = tk.Label(problem_frame, text='Processing times', anchor=tk.E)
	p_textbox = tk.Text(problem_frame, height=3, width=40)
	p_scrollbar = attach_scrollbar(problem_frame, p_textbox)
	nfd_label = tk.Label(problem_frame, text='Negative fixed decisions', anchor=tk.E)
	nfd_textbox = tk.Text(problem_frame, height=3, width=40)
	nfd_scrollbar = attach_scrollbar(problem_frame, nfd_textbox)
	pfd_label = tk.Label(problem_frame, text='Positive fixed decisions', anchor=tk.E)
	pfd_textbox = tk.Text(problem_frame, height=3, width=40)
	pfd_scrollbar = attach_scrollbar(problem_frame, pfd_textbox)

	S_frame = tk.LabelFrame(left_frame, text='Schedule')
	S_command_frame = tk.Frame(S_frame)
	S_optimise_button = tk.Button(S_command_frame, text='Optimise', command=optimise)
	S_random_button = tk.Button(S_command_frame, text='Randomise', command=random_schedule)
	load_S_button = tk.Button(S_command_frame, text='Load', command=load_schedule)
	save_S_button = tk.Button(S_command_frame, text='Save', command=save_schedule)
	S_textbox = tk.Text(S_frame, height=3, width=40)
	S_scrollbar = attach_scrollbar(S_frame, S_textbox)
	explain_button = tk.Button(S_frame, text='Explain', command=explain)

	right_frame = tk.Frame(root)
	fig = plt.figure(0)
	S_figure = FigureCanvasTkAgg(fig, master=right_frame).get_tk_widget()
	output_textbox = tk.Text(right_frame)
	output_scrollbar = attach_scrollbar(right_frame, output_textbox)
	save_output_button = tk.Button(right_frame, text='Save output', command=save_output)

	# Geometry
	padding = 8

	root.geometry("1024x768")
	root.rowconfigure(0, weight=1)
	root.columnconfigure(1, weight=1)

	left_frame.grid(row=0, column=0, sticky=tk.N+tk.S)
	left_frame.rowconfigure(0, weight=1)
	left_frame.rowconfigure(1, weight=1)

	problem_frame.grid(row=0, column=0, padx=padding, pady=padding, sticky=tk.N+tk.S)
	problem_command_frame.grid(row=0, column=0, columnspan=3, padx=padding, pady=padding, sticky=tk.W+tk.E)

	problem_command_frame.columnconfigure(0, weight=1)
	problem_command_frame.columnconfigure(1, weight=1)
	problem_command_frame.columnconfigure(2, weight=1)
	random_problem_button.grid(row=0, column=0, sticky=tk.W+tk.E)
	load_problem_button.grid(row=0, column=1, padx=padding, sticky=tk.W+tk.E)
	save_problem_button.grid(row=0, column=2, sticky=tk.W+tk.E)
	problem_frame.rowconfigure(2, weight=1)
	problem_frame.rowconfigure(3, weight=1)
	problem_frame.rowconfigure(4, weight=1)

	m_label.grid(row=1, column=0, padx=padding, sticky=tk.W+tk.E)
	m_spinbox.grid(row=1, column=1, columnspan=2, padx=(0, padding), sticky=tk.W+tk.E)
	p_label.grid(row=2, column=0, padx=padding, pady=padding, sticky=tk.W+tk.E)
	p_textbox.grid(row=2, column=1, pady=padding, sticky=tk.N+tk.S)
	p_scrollbar.grid(row=2, column=2, padx=(0, padding), pady=padding, sticky=tk.N+tk.S)
	nfd_label.grid(row=3, column=0, padx=padding, sticky=tk.W+tk.E)
	nfd_textbox.grid(row=3, column=1, sticky=tk.N+tk.S)
	nfd_scrollbar.grid(row=3, column=2, padx=(0, padding), sticky=tk.N+tk.S)
	pfd_label.grid(row=4, column=0, padx=padding, pady=padding, sticky=tk.W+tk.E)
	pfd_textbox.grid(row=4, column=1, pady=padding, sticky=tk.N+tk.S)
	pfd_scrollbar.grid(row=4, column=2, padx=(0, padding), pady=padding, sticky=tk.N+tk.S)

	S_frame.grid(row=1, column=0, padx=padding, pady=padding, ipadx=50, sticky=tk.N+tk.S+tk.W+tk.E)
	S_frame.rowconfigure(1, weight=1)
	S_frame.columnconfigure(0, weight=1)
	S_command_frame.grid(row=0, column=0, columnspan=2, padx=padding, pady=padding, sticky=tk.W+tk.E)
	S_command_frame.columnconfigure(0, weight=1)
	S_command_frame.columnconfigure(1, weight=1)
	S_command_frame.columnconfigure(2, weight=1)
	S_command_frame.columnconfigure(3, weight=1)
	S_optimise_button.grid(row=0, column=0, padx=(0, padding), sticky=tk.W+tk.E)
	S_random_button.grid(row=0, column=1, padx=(0, padding), sticky=tk.W+tk.E)
	load_S_button.grid(row=0, column=2, padx=(0, padding), sticky=tk.W+tk.E)
	save_S_button.grid(row=0, column=3, sticky=tk.W+tk.E)
	S_textbox.grid(row=1, column=0, padx=(padding, 0), sticky=tk.N+tk.S+tk.W+tk.E)
	S_scrollbar.grid(row=1, column=1, padx=(0, padding), sticky=tk.N+tk.S)
	explain_button.grid(row=2, column=0, columnspan=2, padx=padding, pady=padding, sticky=tk.W+tk.E)

	right_frame.grid(row=0, column=1, padx=padding, pady=padding, sticky=tk.N+tk.S+tk.W+tk.E)
	right_frame.rowconfigure(0, weight=1)
	right_frame.rowconfigure(1, weight=1)
	right_frame.columnconfigure(0, weight=1)
	S_figure.grid(row=0, column=0, columnspan=2, sticky=tk.N+tk.S+tk.W+tk.E)
	output_textbox.grid(row=1, column=0, sticky=tk.N+tk.S+tk.W+tk.E)
	output_scrollbar.grid(row=1, column=1, sticky=tk.N+tk.S)
	save_output_button.grid(row=2, column=0, columnspan=2, pady=padding, sticky=tk.W+tk.E)

	root.mainloop()

def attach_scrollbar(root, text):
	scrollbar = tk.Scrollbar(root)

	text.config(yscrollcommand=scrollbar.set)
	scrollbar.config(command=text.yview)

	return scrollbar

def textbox_replace(textbox, text):
	textbox.delete('1.0', tk.END)
	textbox.insert(tk.END, text)

def spinbox_replace(spinbox, text):
	spinbox.delete(0, tk.END)
	spinbox.insert(tk.END, text)

if __name__ == '__main__':
	main()

