from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os, os.path
import cv2 as cv

# debug
border_size = 1
frame_xdim = 1600
frame_ydim = 1200

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.master = master
        self.content = Frame(self.master)
        self.master.title("LabelTool")
        self.master.resizable(width=FALSE, height=FALSE)
        # allowing the widget to take the full space of the root window
        self.content.pack(fill=BOTH, expand=1)

        # init canvas size
        self.image_x = 1
        self.image_y = 1
        self.scale_ratio = 1

        # other members
        self.images = []
        self.image_ind = 0
        self.tkimg = None
        self.valid_formats = [".jpg", ".gif", ".png", ".tga"]

        # label members
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.x = self.y = 0

        # If you want rid of border highlight, remove relief
        self.frame_top = Frame(self.master, borderwidth=border_size, relief="sunken", width=.8*frame_xdim, height=.05*frame_ydim)
        self.frame_image = Frame(self.master, borderwidth=border_size, relief="sunken", width=.8*frame_xdim, height=.95*frame_ydim)
        self.frame_right = Frame(self.master, borderwidth=border_size, relief="sunken", width=.2*frame_xdim, height=frame_ydim)
        self.frame_top.grid_propagate(False)
        self.frame_image.grid_propagate(False)
        self.frame_right.grid_propagate(False)

        self.content.grid(column=0, row=0)
        self.frame_top.grid(column=0, row=0, columnspan=3, rowspan=1)
        self.frame_image.grid(column=0, row=1, columnspan=3, rowspan=1)
        self.frame_right.grid(column=3, row=0, columnspan=1, rowspan=3)

        self.button_browse = Button(self.frame_top, text="Source", command=self.find_directory)
        self.button_browse.place(relx=.3, rely=.5, anchor="center")

        self.path_entry = Text(self.frame_top, height=1, width=60)
        self.path_entry.place(relx=.5, rely=.5, anchor="c")

        self.button_next = Button(self.frame_right, text="Done", width=10, height=4, command=self.next_image)
        self.button_next.place(relx=.5, rely=.95, anchor="center")

        self.image_canvas = Canvas(self.frame_image, width=self.image_x, height=self.image_y, cursor='tcross')
        self.image_canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W+N)

        # mouse interaction
        self.image_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.image_canvas.bind("<B1-Motion>", self.on_move_press)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.label_list = Listbox(self.frame_right, height=10, width=20)
        self.label_list.place(relx=.5, rely=.1, anchor="c")

    def show_image(self, path):
        img = Image.open(path)
        width, height = img.size
        print(width, height)

        # if the image is too large for the canvas, resize it accordingly
        if width > self.frame_image.winfo_width() or height > self.frame_image.winfo_height():
            print("scale")
            if width >= height:
                self.image_x = self.frame_image.winfo_width()
                self.scale_ratio = self.image_x / width
                self.image_y = int(self.scale_ratio * height)
            if height > width:
                self.image_y = self.frame_image.winfo_height()
                self.scale_ratio = self.image_y / height
                self.image_x = int(self.scale_ratio * width)
            print(self.image_x, self.image_y)
            img = img.resize((self.image_x, self.image_y), Image.ANTIALIAS)

        self.tkimg = ImageTk.PhotoImage(img)
        self.image_canvas.config(width=self.tkimg.width(), height=self.tkimg.height(), scrollregion=(0, 0, self.tkimg.width(), self.tkimg.height()))
        self.image_canvas.create_image(0, 0, image=self.tkimg, anchor=NW)
        print(self.tkimg.width(), self.tkimg.height())

    def show_text(self, content):
        self.path_entry.insert(INSERT, content)

    def find_directory(self):
        self.image_ind = 0
        self.images = []
        path = filedialog.askdirectory()

        if path != '':
            for f in os.listdir(path):
                ext = os.path.splitext(f)[1]
                if ext.lower() not in self.valid_formats:
                    continue
                self.images.append(os.path.join(path, f))
            self.show_image(self.images[self.image_ind])
            self.show_text(path)

    def next_image(self):
        self.image_ind = self.image_ind + 1
        if self.image_ind < len(self.images):
            self.show_image(self.images[self.image_ind])

    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.image_canvas.canvasx(event.x)
        self.start_y = self.image_canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.image_canvas.create_rectangle(self.x, self.y, 1, 1, outline='red')

    def on_move_press(self, event):
        curX = self.image_canvas.canvasx(event.x)
        curY = self.image_canvas.canvasy(event.y)

        w, h = self.image_canvas.winfo_width(), self.image_canvas.winfo_height()
        if event.x > 0.9*w:
            self.image_canvas.xview_scroll(1, 'units')
        elif event.x < 0.1*w:
            self.image_canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.image_canvas.yview_scroll(1, 'units')
        elif event.y < 0.1*h:
            self.image_canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.image_canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

    def on_button_release(self, event):
        pass


if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (frame_xdim/2)
    y = (hs/2) - (frame_ydim/2)

    # set the dimensions of the screen and where it is placed
    root.geometry('%dx%d+%d+%d' % (frame_xdim, frame_ydim, x, y))
    root.mainloop()
