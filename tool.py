from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os, os.path
import cv2 as cv

# debug
border_size = 1
frame_xdim = 1600
frame_ydin = 1200

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.master = master
        self.content = Frame(self.master)
        self.master.title("LabelTool")
        self.master.resizable(width=FALSE, height=FALSE)
        # allowing the widget to take the full space of the root window
        self.content.pack(fill=BOTH, expand=1)

        self.image_x = 500
        self.image_y = 500

        # If you want rid of border highlight, remove relief
        self.frame_top = Frame(self.master, borderwidth=border_size, relief="sunken", width=1600, height=100)
        self.frame_image = Frame(self.master, borderwidth=border_size, relief="sunken", width=1600, height=1200)
        self.frame_right = Frame(self.master, borderwidth=border_size, relief="sunken", width=500, height=1300)

        self.content.grid(column=0, row=0)
        self.frame_top.grid(column=0, row=0, columnspan=3, rowspan=1)
        self.frame_image.grid(column=0, row=1, columnspan=3, rowspan=1)
        self.frame_right.grid(column=3, row=0, columnspan=1, rowspan=3)

        self.button_browse = Button(self.frame_top, text="Source")
        self.button_browse.grid(column=0, row=0)

        self.path_entry = Entry(self.frame_top)
        self.path_entry.grid(column=1, row=0)

        self.button_next = Button(self.frame_right, text="Done")
        self.button_next.grid(column=0, row=0)

        self.image_canvas = Canvas(self.frame_image, width=self.image_x, height=self.image_y, cursor='tcross')
        self.image_canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W+N)


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (frame_xdim/2)
    y = (hs/2) - (frame_ydin/2)

    # set the dimensions of the screen and where it is placed
    root.geometry('%dx%d+%d+%d' % (frame_xdim, frame_ydin, x, y))
    root.mainloop()