from tkinter import *
from PIL import ImageTk, Image

def main():
	root = Tk()
	root.geometry('480x360')

	root.title('aes demo')

	def quit_program(self):
		root.quit()

	quitButton = Button(root, text='Quit', command=quit_program)
	quitButton.place(x=0, y=0)

	img = ImageTk.PhotoImage(file='graph.png')

	panel = Label(root, image = img)
	panel.pack()

	root.mainloop()
	print('exit')

if __name__ == '__main__':
	main()
