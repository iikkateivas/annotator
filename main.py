from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os, os.path
import cv2 as cv


class Window(Frame):

    imgs = []
    ind = 0
    valid_images = [".jpg", ".gif", ".png", ".tga"]
    frame_xdim = 1600
    frame_ydin = 1200

    image_x = 500
    image_y = 500

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master
        # changing the title of our master widget
        self.master.title("YOLO labeling tool")
        # allowing the widget to take the full space of the root window
        self.pack(fill=BOTH, expand=1)

        self.path_entry = Entry(self)
        self.path_entry.grid(row=0, column=1, sticky=W+E)

        self.button_browse = Button(self, text="Search", command=self.find_directory)
        self.button_browse.grid(row=0, column=0)

        self.button_next = Button(self, text="Done", command=self.next_image)
        self.button_next.grid(row=6, column=6, sticky=N+S+E+W)

        self.image_canvas = Canvas(self, width=self.image_x, height=self.image_y, cursor='tcross')
        self.image_canvas.grid(row=1, column=0, columnspan=2, rowspan=2, sticky=W+N)
        # self.image_canvas.bind("<Button-1>", self.mouseClick)
        # self.image_canvas.bind("<Motion>", self.mouseMove)

        self.tkimg = None

    def exit_client(self):
        exit()

    def show_image(self, path):
        img = Image.open(path).resize((500, 500), Image.ANTIALIAS)
        self.tkimg = ImageTk.PhotoImage(img)
        # self.image_canvas.config(width=max(self.tkimg.width(), 400), height=max(self.tkimg.height(), 400))
        self.image_canvas.create_image(0, 0, image=self.tkimg, anchor=NW)
        # labels can be text or images

    def show_text(self, content):
        self.path_entry.insert(0, content)

    def find_directory(self):
        path = filedialog.askdirectory()

        if path != '':
            for f in os.listdir(path):
                ext = os.path.splitext(f)[1]
                if ext.lower() not in self.valid_images:
                    continue
                self.imgs.append(os.path.join(path,f))
            self.show_image(self.imgs[self.ind])
            self.show_text(path)

    def next_image(self):
        self.ind = self.ind + 1
        self.show_image(self.imgs[self.ind])


def main():
    root = Tk()

    # get screen width and height
    ws = root.winfo_screenwidth() # width of the screen
    hs = root.winfo_screenheight() # height of the screen

    # calculate x and y coordinates for the Tk root window
    x = (ws/2) - (Window.frame_xdim/2)
    y = (hs/2) - (Window.frame_ydin/2)

    # set the dimensions of the screen and where it is placed
    root.geometry('%dx%d+%d+%d' % (Window.frame_xdim, Window.frame_ydin, x, y))

    app = Window(root)
    root.mainloop()


if __name__ == "__main__":
    main()
