import fitz  # PyMuPDF for handling PDFs
from tkinter import *
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox


class PDFViewer:
    def __init__(self, master):
        self.path = None  # Path for the PDF document
        self.fileisopen = False  # Indicates whether a PDF is open
        self.current_page = 0  # Current page number
        self.numPages = 0
        self.history = []  # Stack to keep track of page history for undo
        self.redo_stack = []  # Stack to keep track of pages for redo

        self.master = master  # Main window
        self.master.title("One Word Viewer")
        self.master.geometry("580x520+440+180")
        self.is_fullscreen = False #Track if the window is in fullscreen mode
        
        # Bind keys to fullscreen
        self.master.bind("<Escape>", self.exit_fullscreen) #Bind the Escape key to exit fullscreen
        # self.master.resizable(width=0, height=0)
        self.master.bind("f", self.toggle_fullscreen) #Bind the f key to toggle fullscreen
        self.master.iconbitmap(r"C:\Users\Student\Desktop\MyConsoleApp\PDFVIEWER\Oficina_PDF_35460.ico")

        # Create menu
        self.menu = Menu(self.master)
        self.master.config(menu=self.menu)
        self.filemenu = Menu(self.menu, tearoff=0)
        self.menu.add_cascade(label="File", menu=self.filemenu)
        self.filemenu.add_command(label="Open File", command=self.open_file)
        self.filemenu.add_command(label="Open Recent Files", command=lambda: messagebox.showinfo("File", "Open Recent Files"))
        self.filemenu.add_command(label="Save", command=lambda: messagebox.showinfo("File", "Save"))
        self.filemenu.add_command(label="Save as", command=lambda: messagebox.showinfo("File", "Save as"))
        self.filemenu.add_command(label="Share", command=lambda: messagebox.showinfo("File", "Share"))
        self.filemenu.add_command(label="Print", command=lambda: messagebox.showinfo("File", "Print"))
        self.filemenu.add_command(label="Close file", command=lambda: messagebox.showinfo("File", "Close file"))
        self.filemenu.add_command(label="Exit", command=self.master.destroy)


            #creating 'view' menu and submenus
        self.viewmenu = Menu(self.menu, tearoff=0)
        self.viewmenu.add_command(label="zoom in", command=lambda: messagebox.showinfo("view", "Zoom in"))
        self.viewmenu.add_command(label="zoom out", command=lambda: messagebox.showinfo("view", "Zoom out"))
        self.menu.add_cascade(label="View", menu=self.viewmenu)
        #       adding page rotation 
        self.rotate = Menu(self.viewmenu, tearoff=0)
        self.rotate.add_command(label="Rotate left", command=lambda: messagebox.showinfo("view", "Rotate left"))
        self.rotate.add_command(label="Rotate right", command=lambda: messagebox.showinfo("view", "Rotate right"))
        self.viewmenu.add_cascade(label="Rotate", menu=self.rotate) 

       # adding page orientation
        self.page_view = Menu(self.viewmenu, tearoff=0)
        self.page_view.add_command(label="Single page", command=lambda: messagebox.showinfo("view", "Single page"))
        self.page_view.add_command(label="Two page", command=lambda: messagebox.showinfo("view", "Two page"))
        self.viewmenu.add_cascade(label="Page view", menu=self.page_view)

        # finding page
        self.findpage = Menu(self.viewmenu, tearoff=0)
        self.findpage.add_command(label="search page", command=lambda: messagebox.showinfo("view", "search page"))
        self.findpage.add_command(label="search by title", command=lambda: messagebox.showinfo("view", "search by title"))
        self.viewmenu.add_cascade(label="Find page", menu=self.findpage)

        #creating an 'edit' menu and submenus
       
        self.editmenu = Menu(self.menu, tearoff=0)
        self.editmenu.add_command(label="Undo", command=self.undo)
        self.editmenu.add_command(label="Re-do", command=self.redo)
        self.editmenu.add_command(label='Cut', command=lambda: messagebox.showinfo("edit", "Cut"))
        self.editmenu.add_command(label="Copy", command=lambda: messagebox.showinfo("edit", "Copy"))
        self.editmenu.add_command(label="Paste", command=lambda: messagebox.showinfo("edit", "Paste"))
        self.editmenu.add_command(label="Delete", command=lambda: messagebox.showinfo("edit", "Delete"))    
        self.menu.add_cascade(label="Edit", menu=self.editmenu)

        #creating a 'window' menu and submenus
        #self.menu = Menu(self.menu, tearoff=0)
        self.windowmenu = Menu(self.menu, tearoff=0)
        self.windowmenu.add_command(label="Minimize", command=lambda: messagebox.showinfo("window", "Minimize"))
        self.windowmenu.add_command(label="Maximize", command=lambda: messagebox.showinfo("window", "Maximize"))
        self.menu.add_cascade(label="Window", menu=self.windowmenu)



        # Create frames
        self.top_frame = ttk.Frame(self.master)
        self.top_frame.grid(row=0, column=0, sticky="nsew")
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        self.buttom_frame = ttk.Frame(self.master, height=50)
        self.buttom_frame.grid(row=1, column=0, sticky="ew")
        self.buttom_frame.grid_propagate(False)
        self.master.grid_rowconfigure(1, weight=0)
        self.master.grid_columnconfigure(0, weight=1)

        # Scrollbars
        self.scroll_y = Scrollbar(self.top_frame, orient=VERTICAL)
        self.scroll_y.grid(row=0, column=1, sticky=(N, S))
        self.scroll_x = Scrollbar(self.top_frame, orient=HORIZONTAL)
        self.scroll_x.grid(row=1, column=0, sticky=(W, E))

        # Canvas for displaying PDF pages
        self.output = Canvas(self.top_frame, bg="#ECE8F3")
        self.output.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)
        self.output.grid(row=0, column=0, sticky="nsew")
        self.top_frame.grid_rowconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.scroll_y.configure(command=self.output.yview)
        self.scroll_x.configure(command=self.output.xview)

        # Buttons and label
        self.uparrow_icon = PhotoImage(file=r"C:\Users\Student\Desktop\MyConsoleApp\PDFVIEWER\arrowup.png")
        self.downarrow_icon = PhotoImage(file=r"C:\Users\Student\Desktop\MyConsoleApp\PDFVIEWER\down-arrow.png")
        self.uparrow = self.uparrow_icon.subsample(40, 40)
        self.downarrow = self.downarrow_icon.subsample(40, 40)

        self.up_button = ttk.Button(self.buttom_frame, image=self.uparrow, command=self.previous_page)
        self.up_button.grid(row=0, column=1, padx=(5, 5), pady=8)

        self.down_button = ttk.Button(self.buttom_frame, image=self.downarrow, command=self.next_page)
        self.down_button.grid(row=0, column=2, padx=(5, 5), pady=8)

        self.page_label = ttk.Label(self.buttom_frame, text="Page")
        self.page_label.grid(row=0, column=3, padx=5)

        self.buttom_frame.grid_columnconfigure(0, weight=1)
        self.buttom_frame.grid_columnconfigure(4, weight=1)

    def exit_fullscreen(self, event=None):
        self.master.attributes("-fullscreen", False) #exit fullscreen
        self.is_fullscreen = False #update the fullscreen flag
        self.master.config(menu=self.menu) # ensure menu is visible

    def toggle_fullscreen(self, event=None):
        self.is_fullscreen = not self.is_fullscreen #toggle the fullscreen flag
        self.master.attributes("-fullscreen", self.is_fullscreen) #set the fullscreen attribute
        self.master.config(menu=self.menu) # ensure menu is visible
        self.master.update_idletasks()  # Update the window size
        self.display_page()  # Redisplay the current page to adjust to new size

    def open_file(self):
        file_path = fd.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if file_path:
            self.path = file_path
            self.load_pdf()

    # def save_file(self):
    #     if self.doc and self.path:
    #         try:
    #             self.doc.save(self.path)
    #             messagebox.showinfo("Save", "File saved successfully!")
    #         except Exception as e:
    #             messagebox.showerror("Error", f"Failed to save file: {e}")
    #     else:
    #         self.save_as()

    def load_pdf(self):
        try:
            self.doc = fitz.open(self.path)
            self.numPages = self.doc.page_count
            self.fileisopen = True
            self.current_page = 0
            self.display_page()
        except Exception as e:
            print(f"Error opening PDF: {e}")

    def display_page(self):
        if self.fileisopen and 0 <= self.current_page < self.numPages:
            page = self.doc[self.current_page]
            pix = page.get_pixmap()
            img_data = pix.tobytes("ppm")
            self.img = PhotoImage(data=img_data)
            self.output.delete("all")  # Clear the canvas
            self.output.create_image(self.output.winfo_width() // 2, self.output.winfo_height() // 2, image=self.img, anchor="center")
            self.page_label["text"] = f"{self.current_page + 1} of {self.numPages}"

            # Configure scroll region
            self.output.configure(scrollregion=self.output.bbox("all"))

    def next_page(self):
        if self.fileisopen and self.current_page < self.numPages - 1:
            self.history.append(self.current_page)
            self.current_page += 1
            self.redo_stack.clear()  # Clear redo stack on new action
            self.display_page()

    def previous_page(self):
        if self.fileisopen and self.current_page > 0:
            self.history.append(self.current_page)
            self.current_page -= 1
            self.redo_stack.clear()  # Clear redo stack on new action
            self.display_page()

    def undo(self):
        if self.history:
            self.redo_stack.append(self.current_page)
            self.current_page = self.history.pop()
            self.display_page()

    def redo(self):
        if self.redo_stack:
            self.history.append(self.current_page)
            self.current_page = self.redo_stack.pop()
            self.display_page()


# Create the main window
root = Tk()
app = PDFViewer(root)
root.mainloop()
