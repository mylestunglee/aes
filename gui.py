from tkinter import *
from PIL import ImageTk, Image

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

import interface

def main():
	root = Tk()

	def quit():
		# Close matplotlib figure so program is not left hanging
		plt.close('all')
		root.quit()

	def random_problem():
		# Clear textboxs
		m_spinbox.delete(0, END)
		p_textbox.delete('1.0', END)
		nfd_textbox.delete('1.0', END)
		pfd_textbox.delete('1.0', END)
		S_textbox.delete('1.0', END)

		# Generate problem
		m_text, p_text, nfd_text, pfd_text, S_text = interface.random_problem()

		# Set textboxs
		m_spinbox.insert(END, m_text)
		p_textbox.insert(END, p_text)
		nfd_textbox.insert(END, nfd_text)
		pfd_textbox.insert(END, pfd_text)
		S_textbox.insert(END, S_text)

	def load_problem():
		pass

	def save_problem():
		pass

	def save_output():
		pass

	def optimise():
		pass

	def random_schedule():
		pass

	def load_schedule():
		pass

	def save_schedule():
		pass

	def explain():
		output_text = interface.explain(
			m_spinbox.get(),
			p_textbox.get('1.0', END),
			S_textbox.get('1.0', END),
			nfd_textbox.get('1.0', END),
			pfd_textbox.get('1.0', END))

		output_textbox.delete('1.0', END)
		output_textbox.insert(END, output_text)

		fig.canvas.draw()

	root.protocol("WM_DELETE_WINDOW", quit)
	root.title('Argumentative Explainable Scheduler')

	# Create widgets
	left_frame = Frame(root)

	problem_frame = LabelFrame(left_frame, text='Problem')
	problem_command_frame = Frame(problem_frame)
	load_problem_button = Button(problem_command_frame, text='Load', command=load_problem)
	save_problem_button = Button(problem_command_frame, text='Save', command=save_problem)
	random_problem_button = Button(problem_command_frame, text='Randomise', command=random_problem)
	m_label = Label(problem_frame, text='Number of machines', anchor=E)
	m_spinbox = Spinbox(problem_frame, from_=0, to_=sys.maxsize)
	p_label = Label(problem_frame, text='Processing times', anchor=E)
	p_textbox = Text(problem_frame, height=3, width=40)
	p_scrollbar = attach_scrollbar(problem_frame, p_textbox)
	nfd_label = Label(problem_frame, text='Negative fixed decisions', anchor=E)
	nfd_textbox = Text(problem_frame, height=3, width=40)
	nfd_scrollbar = attach_scrollbar(problem_frame, nfd_textbox)
	pfd_label = Label(problem_frame, text='Positive fixed decisions', anchor=E)
	pfd_textbox = Text(problem_frame, height=3, width=40)
	pfd_scrollbar = attach_scrollbar(problem_frame, pfd_textbox)

	S_frame = LabelFrame(left_frame, text='Schedule')
	S_command_frame = Frame(S_frame)
	S_optimise_button = Button(S_command_frame, text='Optimise', command=optimise)
	S_random_button = Button(S_command_frame, text='Randomise', command=random_schedule)
	load_S_button = Button(S_command_frame, text='Load', command=load_schedule)
	save_S_button = Button(S_command_frame, text='Save', command=save_schedule)
	S_textbox = Text(S_frame, height=3, width=40)
	S_scrollbar = attach_scrollbar(S_frame, S_textbox)
	explain_button = Button(S_frame, text='Explain', command=explain)

	right_frame = Frame(root)
	fig = plt.figure(0)
	S_figure = FigureCanvasTkAgg(fig, master=right_frame).get_tk_widget()
	output_textbox = Text(right_frame)
	output_scrollbar = attach_scrollbar(right_frame, output_textbox)
	save_output_button = Button(right_frame, text='Save output', command=save_output)

	# Geometry
	padding = 8

	root.geometry("1024x768")
	root.rowconfigure(0, weight=1)
	root.columnconfigure(1, weight=1)

	left_frame.grid(row=0, column=0, sticky=N+S)
	left_frame.rowconfigure(0, weight=1)
	left_frame.rowconfigure(1, weight=1)

	problem_frame.grid(row=0, column=0, padx=padding, pady=padding, sticky=N+S)
	problem_command_frame.grid(row=0, column=0, columnspan=3, padx=padding, pady=padding, sticky=W+E)

	problem_command_frame.columnconfigure(0, weight=1)
	problem_command_frame.columnconfigure(1, weight=1)
	problem_command_frame.columnconfigure(2, weight=1)
	random_problem_button.grid(row=0, column=0, sticky=W+E)
	load_problem_button.grid(row=0, column=1, padx=padding, sticky=W+E)
	save_problem_button.grid(row=0, column=2, sticky=W+E)
	problem_frame.rowconfigure(2, weight=1)
	problem_frame.rowconfigure(3, weight=1)
	problem_frame.rowconfigure(4, weight=1)

	m_label.grid(row=1, column=0, padx=padding, sticky=W+E)
	m_spinbox.grid(row=1, column=1, columnspan=2, padx=(0, padding), sticky=W+E)
	p_label.grid(row=2, column=0, padx=padding, pady=padding, sticky=W+E)
	p_textbox.grid(row=2, column=1, pady=padding, sticky=N+S)
	p_scrollbar.grid(row=2, column=2, padx=(0, padding), pady=padding, sticky=N+S)
	nfd_label.grid(row=3, column=0, padx=padding, sticky=W+E)
	nfd_textbox.grid(row=3, column=1, sticky=N+S)
	nfd_scrollbar.grid(row=3, column=2, padx=(0, padding), sticky=N+S)
	pfd_label.grid(row=4, column=0, padx=padding, pady=padding, sticky=W+E)
	pfd_textbox.grid(row=4, column=1, pady=padding, sticky=N+S)
	pfd_scrollbar.grid(row=4, column=2, padx=(0, padding), pady=padding, sticky=N+S)

	S_frame.grid(row=1, column=0, padx=padding, pady=padding, ipadx=50, sticky=N+S+W+E)
	S_frame.rowconfigure(1, weight=1)
	S_frame.columnconfigure(0, weight=1)
	S_command_frame.grid(row=0, column=0, columnspan=2, padx=padding, pady=padding, sticky=W+E)
	S_command_frame.columnconfigure(0, weight=1)
	S_command_frame.columnconfigure(1, weight=1)
	S_command_frame.columnconfigure(2, weight=1)
	S_command_frame.columnconfigure(3, weight=1)
	S_optimise_button.grid(row=0, column=0, padx=(0, padding), sticky=W+E)
	S_random_button.grid(row=0, column=1, padx=(0, padding), sticky=W+E)
	load_S_button.grid(row=0, column=2, padx=(0, padding), sticky=W+E)
	save_S_button.grid(row=0, column=3, sticky=W+E)
	S_textbox.grid(row=1, column=0, padx=(padding, 0), sticky=N+S+W+E)
	S_scrollbar.grid(row=1, column=1, padx=(0, padding), sticky=N+S)
	explain_button.grid(row=2, column=0, columnspan=2, padx=padding, pady=padding, sticky=W+E)

	right_frame.grid(row=0, column=1, padx=padding, pady=padding, sticky=N+S+W+E)
	right_frame.rowconfigure(0, weight=1)
	right_frame.rowconfigure(1, weight=1)
	right_frame.columnconfigure(0, weight=1)
	S_figure.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
	output_textbox.grid(row=1, column=0, sticky=N+S+W+E)
	output_scrollbar.grid(row=1, column=1, sticky=N+S)
	save_output_button.grid(row=2, column=0, columnspan=2, pady=padding, sticky=W+E)

	root.mainloop()

def attach_scrollbar(root, text):
	scrollbar = Scrollbar(root)

	text.config(yscrollcommand=scrollbar.set)
	scrollbar.config(command=text.yview)

	return scrollbar

if __name__ == '__main__':
	main()

