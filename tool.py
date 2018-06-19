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

        # current image
        self.current_image_w = None
        self.current_image_h = None

        # other members
        self.images = []
        self.image_ind = 0
        self.tkimg = None
        self.valid_formats = [".jpg", ".gif", ".png", ".tga"]

        # label members
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.x = self.y = 0
        self.selected_label = None
        self.rects = []

        self.format_yolo = IntVar()

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

        self.labels_label = Label(self.frame_right, text="Annotations")
        self.labels_label.place(relx=.5, rely=.12, anchor="c")
        self.label_list = Listbox(self.frame_right, height=20, width=30)
        self.label_list.place(relx=.5, rely=.2, anchor="c")
        self.label_list.bind("<<ListboxSelect>>", self.get_annotation)

        self.button_delete = Button(self.frame_right, text="Delete", command=self.delete_annotation)
        self.button_delete.place(relx=.5, rely=.35, anchor="center")

        self.class_label = Label(self.frame_right, text="Class")
        self.class_label.place(relx=.38, rely=.05, anchor="c")
        self.class_entry = Text(self.frame_right, height=1, width=4)
        self.class_entry.place(relx=.5, rely=.05, anchor="c")

        # Checkboxes for annotation format
        self.check_yolo_label = Label(self.frame_top, text="Format")
        self.check_yolo_label.place(relx=.05, rely=.5, anchor="c")
        self.check_yolo = Checkbutton(self.frame_top, text="YOLOv2", variable=self.format_yolo, onvalue=1, offvalue=0)
        self.check_yolo.place(relx=.1, rely=.5, anchor="c")
        self.check_yolo.select()

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

        # set current image size for annotation calculations
        self.current_image_w = self.tkimg.width()
        self.current_image_h = self.tkimg.height()

        # initialize label stuff
        self.selected_label = None
        self.rects = []
        self.label_list.delete(0, END)

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
        # always start a new rectangle on button press
        self.rect = None
        # save mouse drag start position
        self.start_x = self.image_canvas.canvasx(event.x)
        self.start_y = self.image_canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.image_canvas.create_rectangle(self.x, self.y, 1, 1, outline='red', width=2)

    def on_move_press(self, event):
        self.end_x = self.image_canvas.canvasx(event.x)
        self.end_y = self.image_canvas.canvasy(event.y)

        # expand rectangle as you drag the mouse
        self.image_canvas.coords(self.rect, self.start_x, self.start_y, self.end_x, self.end_y)

    def on_button_release(self, event):
        print(self.start_x, self.start_y, self.end_x, self.end_y)
        label_string = str(int(self.start_x)) + ", " + str(int(self.start_y)) + ", " + str(int(self.end_x)) + ", " + str(int(self.end_y))
        self.label_list.insert(END, label_string)
        self.rects.append(self.rect)
        self.get_yolo_format()

    def get_annotation(self, event):
        w = event.widget
        self.selected_label = int(w.curselection()[0])

    def delete_annotation(self):
        if self.selected_label is None:
            return
        # remove from the listbox
        self.label_list.delete(self.selected_label)
        # remove from canvas
        self.image_canvas.delete(self.rects[self.selected_label])
        # remove from the list
        self.rects.remove(self.rects[self.selected_label])
        self.selected_label = None

    def get_yolo_format(self):
        length_x = self.end_x - self.start_x
        length_y = self.end_y - self.start_y
        center_x = (self.start_x + length_x / 2) / self.current_image_w
        center_y = (self.start_y + length_y / 2) / self.current_image_h
        length_x_per = length_x / self.current_image_w
        length_y_per = length_y / self.current_image_h
        yolo_string = str(center_x) + ", " + str(center_y) + ", " + str(length_x_per) + ", " + str(length_y_per)
        print(yolo_string)
        return yolo_string


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
