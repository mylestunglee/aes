from tkinter import *
from PIL import ImageTk, Image

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np

def main():
	root = Tk()

	def quit():
		# Close matplotlib figure so program is not left hanging
		plt.close('all')
		root.quit()

	root.protocol("WM_DELETE_WINDOW", quit)
	root.title('aes demo')

	# Weightings
	root.rowconfigure(7, weight=1)
	root.columnconfigure(2, weight=1)

	# Left
	Label(text='Number of machines').grid(row=0, column=0)
	Text(height=1).grid(row=0, column=1)

	Label(text='Processing times').grid(row=1, column=0)
	Text(height=1).grid(row=1, column=1)

	Label(text='Negative fixed decisions').grid(row=2, column=0)
	Text(height=1).grid(row=2, column=1)

	Label(text='Positive fixed decisions').grid(row=3, column=0)
	Text(height=1).grid(row=3, column=1)

	Label(text='Schedule').grid(row=4, column=0, columnspan=2)
	Text().grid(row=5, column=0, rowspan=3, columnspan=2, sticky=NSEW)

	# Right
	fig = plt.figure(1)
	plt.ion()
	t = np.arange(0.0,3.0,0.01)
	s = np.sin(np.pi*t)
	plt.plot(t,s)

	FigureCanvasTkAgg(fig, master=root).get_tk_widget().grid(row=0, column=2, rowspan=6, sticky=NSEW)

	Label(text='Output').grid(row=6, column=2)

	Text().grid(row=7, column=2, sticky=NSEW)

	root.mainloop()

if __name__ == '__main__':
	main()
