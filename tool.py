from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk
import os, os.path

# debug
border_size = 1
frame_xdim = 1600
frame_ydim = 1200

# pyinstaller packaging: pyinstaller tool.py --onefile --hidden-import='PIL._tkinter_finder'


class LabelTool:
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
        self.current_path = None
        self.fn = None

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
        self.current_class = StringVar(value="0")

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

        self.button_done = Button(self.frame_right, text="Done", width=10, height=4, command=self.next_image)
        self.button_done.place(relx=.5, rely=.80, anchor="center")
        self.button_done.focus_set()
        self.button_done.bind("<Return>", self.next_image)

        self.button_next = Button(self.frame_right, text="Next", width=5, height=2, command=self.next_image_nosave)
        self.button_next.place(relx=.7, rely=.95, anchor="center")

        self.button_prev = Button(self.frame_right, text="Prev", width=5, height=2, command=self.prev_image_nosave)
        self.button_prev.place(relx=.3, rely=.95, anchor="center")

        self.image_canvas = Canvas(self.frame_image, width=self.image_x, height=self.image_y, cursor='tcross')
        self.image_canvas.grid(row=0, column=0, columnspan=2, rowspan=2, sticky=W+N)

        # mouse interaction
        self.image_canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.image_canvas.bind("<B1-Motion>", self.on_move_press)
        self.image_canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.labels_label = Label(self.frame_right, text="Annotations")
        self.labels_label.place(relx=.5, rely=.12, anchor="c")
        self.label_list = Listbox(self.frame_right, height=20, width=35)
        self.label_list.place(relx=.5, rely=.2, anchor="c")
        self.label_list.bind("<<ListboxSelect>>", self.get_annotation)

        self.button_delete = Button(self.frame_right, text="Delete", command=self.delete_annotation)
        self.button_delete.place(relx=.5, rely=.35, anchor="center")

        self.class_label = Label(self.frame_right, text="Class")
        self.class_label.place(relx=.38, rely=.05, anchor="c")
        self.class_entry = Entry(self.frame_right, textvariable=self.current_class)
        self.class_entry.place(relx=.5, rely=.05, anchor="c", width=30)

        # self.no_images_label = Label(self.frame_image, text="No images left")
        # self.no_images_label.place(relx=.5, rely=.5, anchor="c")

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

        # create annotation file if it does not exist already
        path_string = path.split("/")
        filename = os.path.splitext(path_string[-1])[0]

        self.fn = self.current_path + "/" + filename + ".txt"
        if os.path.exists(self.fn):
            f = open(self.fn, "r")
            self.read_annotations(f)
        else:
            f = open(self.fn, "w")
        f.close()

        print(self.tkimg.width(), self.tkimg.height())

    def parse_yolo_annotation(self, line):
        cx, cy, lx, ly = 0, 0, 0, 0
        for i, coord in enumerate(line.split(" ")[1:]):
            print(str(i) + " " + str(coord))
            if i == 0:
                cx = float(coord) * self.current_image_w
            elif i == 1:
                cy = float(coord) * self.current_image_h
            elif i == 2:
                lx = float(coord) * self.current_image_w
            elif i == 3:
                ly = float(coord) * self.current_image_h

        start_x = cx - lx / 2
        start_y = cy - ly / 2
        end_x = start_x + lx
        end_y = start_y + ly
        self.rect = self.image_canvas.create_rectangle(start_x, start_y, end_x, end_y, outline='red', width=2)
        self.rects.append(self.rect)

    def read_annotations(self, file):
        for line in file:
            self.label_list.insert(END, line)
            self.parse_yolo_annotation(line)

    def save_annotations(self):
        if self.current_class.get() is None:
            return
        if os.path.exists(self.fn):
            os.remove(self.fn)
        f = open(self.fn, "w")
        for label in self.label_list.get(0, END):
            # if the label is previously inserted, don't add extra newline
            if label[-1:] == "\n":
                f.write(str(label))
                continue
            f.write(str(label + "\n"))
        f.close()

    def show_text(self, content):
        self.path_entry.insert(INSERT, content)

    def find_directory(self):
        self.image_ind = 0
        self.images = []
        self.current_path = filedialog.askdirectory()

        if self.current_path != '':
            for f in os.listdir(self.current_path):
                ext = os.path.splitext(f)[1]
                if ext.lower() not in self.valid_formats:
                    continue
                self.images.append(os.path.join(self.current_path, f))
            self.show_image(self.images[self.image_ind])
            self.show_text(self.current_path)

    def next_image(self, event=None):
        # save current annotations if any
        self.save_annotations()

        if self.image_ind < len(self.images) - 1:
            self.image_ind = self.image_ind + 1
            self.show_image(self.images[self.image_ind])
        #else:


    def next_image_nosave(self):
        if self.image_ind < len(self.images) - 1:
            self.image_ind = self.image_ind + 1
            self.show_image(self.images[self.image_ind])

    def prev_image_nosave(self):
        if self.image_ind > 0:
            self.image_ind = self.image_ind - 1
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
        # label_string = str(int(self.start_x)) + ", " + str(int(self.start_y)) + ", " + str(int(self.end_x)) + ", " + str(int(self.end_y))
        self.label_list.insert(END, self.get_yolo_format())
        self.rects.append(self.rect)
        self.get_yolo_format()

    def get_annotation(self, event):
        w = event.widget
        if len(w.curselection()) > 0:
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
        if self.end_x > self.start_x:
            length_x = self.end_x - self.start_x
            center_x = (self.start_x + length_x / 2) / self.current_image_w
        else:
            length_x = self.start_x - self.end_x
            center_x = (self.end_x + length_x / 2) / self.current_image_w

        if self.end_y > self.start_y:
            length_y = self.end_y - self.start_y
            center_y = (self.start_y + length_y / 2) / self.current_image_h
        else:
            length_y = self.start_y - self.end_y
            center_y = (self.end_y + length_y / 2) / self.current_image_h

        length_x_per = length_x / self.current_image_w
        length_y_per = length_y / self.current_image_h
        yolo_string = str(self.current_class.get()) + " " + str(center_x) + " " + str(center_y) + " " + str(length_x_per) + " " + str(length_y_per)
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
