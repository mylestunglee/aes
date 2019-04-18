import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
import interface

def start(m_text_initial, p_text_initial, nfd_text_initial, pfd_text_initial,
	S_text_initial, explain_initial, options, solver_name,
	time_limit):

	matplotlib.use("TkAgg")

	root = tk.Tk()
	actions_lookup = []

	def quit():
		# Close matplotlib figure so program is not left hanging
		plt.close('all')
		root.quit()

	def random_problem():
		# Generate random problem
		m_text, p_text, nfd_text, pfd_text = interface.random_problem()

		# Set textboxes
		spinbox_set(m_spinbox, m_text)
		textbox_set(p_textbox, p_text)
		textbox_set(nfd_textbox, nfd_text)
		textbox_set(pfd_textbox, pfd_text)

	def load_problem():
		# Locate file
		filename = tk.filedialog.askopenfilename(title='Open problem',
			filetypes=[('Problem files', '*.problem'), ('Any files', '*')])

		# Handle closed dialog
		if not filename:
			return

		# Read file
		success, texts = interface.load_problem(filename)

		if success:
			[m_text, p_text, nfd_text, pfd_text] = texts

			spinbox_set(m_spinbox, m_text)
			textbox_set(p_textbox, p_text)
			textbox_set(nfd_textbox, nfd_text)
			textbox_set(pfd_textbox, pfd_text)
		else:
			E_listbox_set(texts)

	def save_problem():
		# Locate file
		filename = tk.filedialog.asksaveasfilename(title='Save problem as',
			filetypes=[('Problem files', '*.problem'), ('Any files', '*')])

		# Handle closed dialog
		if not filename:
			return

		# Write file
		success, error = interface.save_problem(
			filename,
			m_spinbox.get(),
			textbox_get(p_textbox),
			textbox_get(nfd_textbox),
			textbox_get(pfd_textbox))

		if not success:
			E_listbox_set(error)

	def optimal_schedule():
		# Generate schedule
		success, text = interface.optimal_schedule(
			m_spinbox.get(),
			textbox_get(p_textbox),
			textbox_get(nfd_textbox),
			textbox_get(pfd_textbox),
			solver_name,
			time_limit)

		if success:
			textbox_set(S_textbox, text)
		else:
			E_listbox_set(text)

	def random_schedule():
		# Generate schedule
		success, text = interface.random_schedule(
			m_spinbox.get(),
			textbox_get(p_textbox),
			textbox_get(nfd_textbox),
			textbox_get(pfd_textbox))

		if success:
			textbox_set(S_textbox, text)
		else:
			E_listbox_set(text)

	def load_schedule():
		# Locate file
		filename = tk.filedialog.askopenfilename(title='Open schedule',
			filetypes=[('Schedule files', '*.schedule'), ('Any files', '*')])

		# Handle closed dialog
		if not filename:
			return

		# Read file
		success, text = interface.load_text(filename)

		if success:
			textbox_set(S_textbox, text)
		else:
			E_listbox_set(text)

	def save_file(text, title, filetypes):
		# Locate file
		filename = tk.filedialog.asksaveasfilename(title=title,
			filetypes=filetypes)

		# Handle closed dialog
		if not filename:
			return

		# Write file
		success, error = interface.save_text(filename, text)

		if not success:
			E_listbox_set(error)

	def save_schedule():
		save_file(textbox_get(S_textbox), 'Save schedule as',
			[('Schedule files', '*.schedule'), ('Any files', '*')])

	def explain(options=options):
		success, result = interface.explain(
			m_spinbox.get(),
			textbox_get(p_textbox),
			textbox_get(nfd_textbox),
			textbox_get(pfd_textbox),
			textbox_get(S_textbox),
			options)

		if success:
			# Setup reasons
			E_listbox_set([reason for reason, _ in result])
			# Updates actions
			nonlocal actions_lookup
			actions_lookup = [actions for _, actions in result]
			# Select first appliable reason
			for index, (_, actions) in enumerate(result):
				if actions:
					E_listbox.select_set(index)
					on_select_reason()
					break

			fig.canvas.draw()
		else:
			E_listbox_set(result)

	def save_explanation():
		save_file(listbox_get(E_listbox), 'Save output as',
			[('Text files', '*.txt'), ('Any files', '*')])

	# Set E_listbox's items while clearing actions
	def E_listbox_set(lines):
		actions_lookup = []
		listbox_set(E_listbox, lines)
		listbox_set(action_listbox, [])

	# Shows suggested actions for a selected reason
	def on_select_reason(_=None):
		# If anything has been explained
		if actions_lookup:
			# Show suggested actions
			readable_actions = actions_lookup[E_listbox.curselection()[0]]
			actions = [action for action, _ in readable_actions]
			listbox_set(action_listbox, actions)
			# Select if possible
			if actions:
				action_listbox.select_set(0)

	# Apply selected action to schedule
	def apply(_=None):
		# If action is selected
		indices = list(action_listbox.curselection())
		if indices:
			# Find internal representation of action
			action_index = indices[0]
			reason_index = E_listbox.curselection()[0]
			_, action = actions_lookup[reason_index][action_index]

			# Apply action
			success, result = interface.apply(
				m_spinbox.get(),
				textbox_get(p_textbox),
				textbox_get(nfd_textbox),
				textbox_get(pfd_textbox),
				textbox_get(S_textbox),
				action,
				options)

			if success:
				# Unpack results
				nfd_text, pfd_text, S_text = result

				# Update textboxes
				textbox_set(nfd_textbox, nfd_text)
				textbox_set(pfd_textbox, pfd_text)
				textbox_set(S_textbox, S_text)

				# Automate next step, but do not draw again for explanation
				draw_options = dict(options)
				draw_options['graphical'] = False
				explain(draw_options)
			else:
				E_listbox_set([result])

	# When tab is pressed
	def focus_next_window(event):
	    event.widget.tk_focusNext().focus()
	    return('break')

	root.protocol('WM_DELETE_WINDOW', quit)
	root.title('Schedule Explainer')
	input_textbox_width = 30

	# Create widgets
	left_frame = tk.Frame(root)

	problem_frame = tk.LabelFrame(left_frame, text='Problem')
	problem_command_frame = tk.Frame(problem_frame)
	random_problem_button = tk.Button(problem_command_frame, text='Randomise', command=random_problem)
	load_problem_button = tk.Button(problem_command_frame, text='Load', command=load_problem)
	save_problem_button = tk.Button(problem_command_frame, text='Save', command=save_problem)
	m_label = tk.Label(problem_frame, text='Number of machines', anchor=tk.E)
	m_spinbox = tk.Spinbox(problem_frame, from_=0, to_=tk.sys.maxsize)
	p_label = tk.Label(problem_frame, text='Processing times', anchor=tk.E)
	p_textbox = tk.Text(problem_frame, height=3, width=input_textbox_width)
	p_scrollbar = attach_scrollbar(problem_frame, p_textbox)
	p_textbox.bind('<Tab>', focus_next_window)
	nfd_label = tk.Label(problem_frame, text='Negative fixed decisions', anchor=tk.E)
	nfd_textbox = tk.Text(problem_frame, height=3, width=input_textbox_width)
	nfd_scrollbar = attach_scrollbar(problem_frame, nfd_textbox)
	nfd_textbox.bind('<Tab>', focus_next_window)
	pfd_label = tk.Label(problem_frame, text='Positive fixed decisions', anchor=tk.E)
	pfd_textbox = tk.Text(problem_frame, height=3, width=input_textbox_width)
	pfd_scrollbar = attach_scrollbar(problem_frame, pfd_textbox)
	pfd_textbox.bind('<Tab>', focus_next_window)

	S_frame = tk.LabelFrame(left_frame, text='Schedule')
	S_command_frame = tk.Frame(S_frame)
	S_optimal_schedule_button = tk.Button(S_command_frame, text='Optimise', command=optimal_schedule)
	S_random_button = tk.Button(S_command_frame, text='Randomise', command=random_schedule)
	load_S_button = tk.Button(S_command_frame, text='Load', command=load_schedule)
	save_S_button = tk.Button(S_command_frame, text='Save', command=save_schedule)
	S_textbox = tk.Text(S_frame, height=3, width=input_textbox_width)
	S_textbox.bind('<Tab>', focus_next_window)
	S_scrollbar = attach_scrollbar(S_frame, S_textbox)
	explain_button = tk.Button(S_frame, text='Explain', command=explain)

	right_frame = tk.Frame(root)
	fig = plt.figure(0)
	S_figure = FigureCanvasTkAgg(fig, master=right_frame).get_tk_widget()
	E_frame = tk.LabelFrame(right_frame, text='Explanation')
	E_listbox = tk.Listbox(E_frame, exportselection=False)
	E_listbox.bind('<<ListboxSelect>>', on_select_reason)
	E_listbox.bind('<Return>', apply)
	E_scrollbar = attach_scrollbar(E_frame, E_listbox)
	save_E_button = tk.Button(E_frame, text='Save', command=save_explanation)
	action_frame = tk.LabelFrame(right_frame, text='Actions')
	action_listbox = tk.Listbox(action_frame)
	action_listbox.bind('<Return>', apply)
	action_scrollbar = attach_scrollbar(action_frame, action_listbox)
	apply_action_button = tk.Button(action_frame, text='Apply', command=apply)

	# Geometry
	padding = 8
	h_fill = tk.W + tk.E
	v_fill = tk.N + tk.S
	fill = h_fill + v_fill

	root.geometry("1280x720")
	root.rowconfigure(0, weight=1)
	root.columnconfigure(1, weight=1)

	left_frame.grid(row=0, column=0, sticky=v_fill)
	left_frame.rowconfigure(0, weight=1)
	left_frame.rowconfigure(1, weight=1)

	problem_frame.grid(row=0, column=0, padx=padding, pady=padding, sticky=v_fill)
	problem_command_frame.grid(row=0, column=0, columnspan=3, padx=padding, pady=padding, sticky=h_fill)

	problem_command_frame.columnconfigure(0, weight=1)
	problem_command_frame.columnconfigure(1, weight=1)
	problem_command_frame.columnconfigure(2, weight=1)
	random_problem_button.grid(row=0, column=0, sticky=h_fill)
	load_problem_button.grid(row=0, column=1, padx=padding, sticky=h_fill)
	save_problem_button.grid(row=0, column=2, sticky=h_fill)
	problem_frame.rowconfigure(2, weight=1)
	problem_frame.rowconfigure(3, weight=1)
	problem_frame.rowconfigure(4, weight=1)

	m_label.grid(row=1, column=0, padx=padding, sticky=h_fill)
	m_spinbox.grid(row=1, column=1, columnspan=2, padx=(0, padding), sticky=h_fill)
	p_label.grid(row=2, column=0, padx=padding, pady=padding, sticky=h_fill)
	p_textbox.grid(row=2, column=1, pady=padding, sticky=v_fill)
	p_scrollbar.grid(row=2, column=2, padx=(0, padding), pady=padding, sticky=v_fill)
	nfd_label.grid(row=3, column=0, padx=padding, sticky=h_fill)
	nfd_textbox.grid(row=3, column=1, sticky=v_fill)
	nfd_scrollbar.grid(row=3, column=2, padx=(0, padding), sticky=v_fill)
	pfd_label.grid(row=4, column=0, padx=padding, pady=padding, sticky=h_fill)
	pfd_textbox.grid(row=4, column=1, pady=padding, sticky=v_fill)
	pfd_scrollbar.grid(row=4, column=2, padx=(0, padding), pady=padding, sticky=v_fill)

	S_frame.grid(row=1, column=0, padx=padding, pady=(0, padding), ipadx=50, sticky=fill)
	S_frame.rowconfigure(1, weight=1)
	S_frame.columnconfigure(0, weight=1)
	S_command_frame.grid(row=0, column=0, columnspan=2, padx=padding, pady=padding, sticky=h_fill)
	S_command_frame.columnconfigure(0, weight=1)
	S_command_frame.columnconfigure(1, weight=1)
	S_command_frame.columnconfigure(2, weight=1)
	S_command_frame.columnconfigure(3, weight=1)
	S_optimal_schedule_button.grid(row=0, column=0, padx=(0, padding), sticky=h_fill)
	S_random_button.grid(row=0, column=1, padx=(0, padding), sticky=h_fill)
	load_S_button.grid(row=0, column=2, padx=(0, padding), sticky=h_fill)
	save_S_button.grid(row=0, column=3, sticky=h_fill)
	S_textbox.grid(row=1, column=0, padx=(padding, 0), sticky=fill)
	S_scrollbar.grid(row=1, column=1, padx=(0, padding), sticky=v_fill)
	explain_button.grid(row=2, column=0, columnspan=2, padx=padding, pady=padding, sticky=h_fill)

	right_frame.grid(row=0, column=1, sticky=fill)
	right_frame.rowconfigure(1, weight=1)
	right_frame.columnconfigure(0, weight=1)
	right_frame.columnconfigure(1, weight=1)
	S_figure.grid(row=0, column=0, columnspan=2, sticky=h_fill, padx=padding, pady=padding)
	E_frame.grid(row=1, column=0, sticky=fill, padx=padding, pady=(0, padding))
	E_frame.rowconfigure(0, weight=1)
	E_frame.columnconfigure(0, weight=1)
	E_listbox.grid(row=0, column=0, sticky=fill, padx=(padding, 0), pady=(padding, 0))
	E_scrollbar.grid(row=0, column=1, sticky=v_fill, padx=(0, padding), pady=(padding, 0))
	save_E_button.grid(row=1, column=0, columnspan=2, padx=padding, pady=padding, sticky=h_fill)
	action_frame.grid(row=1, column=1, sticky=fill, padx=padding, pady=(0, padding))
	action_frame.rowconfigure(0, weight=1)
	action_frame.columnconfigure(0, weight=1)
	action_frame.rowconfigure(0, weight=1)
	action_listbox.grid(row=0, column=0, sticky=fill, padx=(padding, 0), pady=(padding, 0))
	action_scrollbar.grid(row=0, column=1, sticky=v_fill, padx=(0, padding), pady=(padding, 0))
	apply_action_button.grid(row=1, column=0, columnspan=2, padx=padding, pady=padding, sticky=h_fill)

	# Initial state from command line
	spinbox_set(m_spinbox, m_text_initial)
	textbox_set(p_textbox, p_text_initial)
	textbox_set(nfd_textbox, nfd_text_initial)
	textbox_set(pfd_textbox, pfd_text_initial)
	textbox_set(S_textbox, S_text_initial)

	if explain_initial:
		explain()

	root.mainloop()

def attach_scrollbar(root, text):
	scrollbar = tk.Scrollbar(root)

	text.config(yscrollcommand=scrollbar.set)
	scrollbar.config(command=text.yview)

	return scrollbar

def textbox_set(textbox, text):
	textbox.delete('1.0', tk.END)
	textbox.insert(tk.END, text)

# Get textbox's value, endline appends '\n'
def textbox_get(textbox):
	return textbox.get('1.0', tk.END).strip() + '\n'

def spinbox_set(spinbox, text):
	spinbox.delete(0, tk.END)
	spinbox.insert(tk.END, text)

def listbox_set(listbox, lines):
	listbox.delete(0, tk.END)
	if type(lines) == str:
		listbox.insert(tk.END, lines)
	else:
		for line in lines:
			listbox.insert(tk.END, line)

def listbox_get(listbox):
	return '\n'.join(list(listbox.get(0, tk.END)))
