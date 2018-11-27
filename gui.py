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
		m_textbox.delete('1.0', END)
		p_textbox.delete('1.0', END)
		nfd_textbox.delete('1.0', END)
		pfd_textbox.delete('1.0', END)
		S_textbox.delete('1.0', END)

		# Generate problem
		m_text, p_text, nfd_text, pfd_text, S_text = interface.random_problem()

		# Set textboxs
		m_textbox.insert(END, m_text)
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

	def explain():
		interface.explain(
			p_textbox.get('1.0', END),
			S_textbox.get('1.0', END))
		fig.canvas.draw()

	def optimise():
		pass

	root.protocol("WM_DELETE_WINDOW", quit)
	root.title('AES')

	# Create widgets
	left_frame = Frame(root)

	command_frame = Frame(left_frame)
	random_problem_button = Button(command_frame, text='Generate random problem', command=random_problem)
	load_problem_button = Button(command_frame, text='Load problem', command=load_problem)
	save_problem_button = Button(command_frame, text='Save problem', command=save_problem)
	save_output_button = Button(command_frame, text='Save output', command=save_output)
	explain_button = Button(command_frame, text='Explain', command=explain)
	optimise_button = Button(command_frame,  text='Optimise', command=optimise)

	problem_frame = Frame(left_frame)
	m_label = Label(problem_frame, text='Number of machines')
	m_textbox = Text(problem_frame, height=1, width=40)
	p_label = Label(problem_frame, text='Processing times')
	p_textbox = Text(problem_frame, height=3, width=40)
	p_scrollbar = attach_scrollbar(problem_frame, p_textbox)
	nfd_label = Label(problem_frame, text='Negative fixed decisions')
	nfd_textbox = Text(problem_frame, height=3, width=40)
	nfd_scrollbar = attach_scrollbar(problem_frame, nfd_textbox)
	pfd_label = Label(problem_frame, text='Positive fixed decisions')
	pfd_textbox = Text(problem_frame, height=3, width=40)
	pfd_scrollbar = attach_scrollbar(problem_frame, pfd_textbox)

	S_frame = Frame(left_frame)
	S_label = Label(S_frame, text='Schedule')
	S_textbox = Text(S_frame, height=3, width=40)
	S_scrollbar = attach_scrollbar(S_frame, S_textbox)

	right_frame = Frame(root)
	fig = plt.figure(0)
	S_figure = FigureCanvasTkAgg(fig, master=right_frame).get_tk_widget()
	output_textbox = Text(right_frame)
	output_scrollbar = attach_scrollbar(right_frame, output_textbox)

	# Geometry
	padding = 4

	root.rowconfigure(0, weight=1)
	root.columnconfigure(1, weight=1)

	left_frame.grid(row=0, column=0, sticky=N+S)
	left_frame.rowconfigure(1, weight=1)
	left_frame.rowconfigure(2, weight=1)

	command_frame.grid(row=0, column=0, padx=padding, pady=padding)
	random_problem_button.grid(row=0, column=0, padx=padding, pady=padding)
	load_problem_button.grid(row=0, column=1, padx=padding, pady=padding)
	save_problem_button.grid(row=0, column=2, padx=padding, pady=padding)
	save_output_button.grid(row=1, column=0, padx=padding, pady=padding)
	explain_button.grid(row=1, column=1, padx=padding, pady=padding)
	optimise_button.grid(row=1, column=2, padx=padding, pady=padding)

	problem_frame.grid(row=1, column=0, padx=padding, pady=padding, sticky=N+S)
	problem_frame.rowconfigure(1, weight=1)
	problem_frame.rowconfigure(2, weight=1)
	problem_frame.rowconfigure(3, weight=1)
	m_label.grid(row=0, column=0, pady=padding)
	m_textbox.grid(row=0, column=1, columnspan=2, pady=padding, sticky=E+W)
	p_label.grid(row=1, column=0, pady=padding)
	p_textbox.grid(row=1, column=1, pady=padding, sticky=N+S)
	p_scrollbar.grid(row=1, column=2, pady=padding, sticky=N+S)
	nfd_label.grid(row=2, column=0, pady=padding)
	nfd_textbox.grid(row=2, column=1, pady=padding, sticky=N+S)
	nfd_scrollbar.grid(row=2, column=2, pady=padding, sticky=N+S)
	pfd_label.grid(row=3, column=0, pady=padding)
	pfd_textbox.grid(row=3, column=1, pady=padding, sticky=N+S)
	pfd_scrollbar.grid(row=3, column=2, pady=padding, sticky=N+S)

	S_frame.grid(row=2, column=0, sticky=N+S+W+E)
	S_frame.rowconfigure(1, weight=1)
	S_frame.columnconfigure(0, weight=1)
	S_label.grid(row=0, column=0, columnspan=2)
	S_textbox.grid(row=1, column=0, sticky=N+S+W+E)
	S_scrollbar.grid(row=1, column=1, sticky=N+S)

	right_frame.grid(row=0, column=1, sticky=N+S+W+E)
	right_frame.rowconfigure(0, weight=1)
	right_frame.rowconfigure(1, weight=1)
	right_frame.columnconfigure(0, weight=1)
	S_figure.grid(row=0, column=0, columnspan=2, sticky=N+S+W+E)
	output_textbox.grid(row=1, column=0, sticky=N+S+W+E)
	output_scrollbar.grid(row=1, column=1, sticky=N+S)

	root.mainloop()

def attach_scrollbar(root, text):
	scrollbar = Scrollbar(root)

	text.config(yscrollcommand=scrollbar.set)
	scrollbar.config(command=text.yview)

	return scrollbar

if __name__ == '__main__':
	main()

