import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
import getpass

FILE_TYPE = ".txt"
FILE_PATH = "C:\\Users\\eric.weese\\Documents\\Projects\\Python Test\\FileTracker\\root"


class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python File Explorer")
        self.root.geometry("800x600")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Set Root Directory", command=self.set_directory)
        
        self.filePathText = StringVar()
        self.file_path_text = Label(self.frame, textvariable=self.filePathText)
        self.file_path_text.pack(side="top", anchor="w")

        self.back_button = ttk.Button(self.frame, text="Up Folder", command=self.navigate_up)
        self.back_button.pack(side="top",anchor="w")

        self.tree = ttk.Treeview(self.frame, columns=("Name", "Type", "Watched", "Total Watched", "Progress"))
        self.tree.pack(fill="both", expand=True, side="left")

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure('completed', background='#BEFFC2')
        self.tree.tag_configure('completedFolder', background='light green')
        self.tree.tag_configure('startedFolder', background='#FDFFBE')

        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("Name", anchor="w", width=400)
        self.tree.column("Type", anchor="w", width=50, stretch="no")
        self.tree.column("Watched", width=75, stretch="no")
        self.tree.column("Total Watched", width=100, stretch="no")
        self.tree.column("Progress", width=75, stretch="no")

        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("Name", text="Name", anchor="w")
        self.tree.heading("Type", text="Type", anchor="w")
        self.tree.heading("Watched", text="Watched?", anchor="w")
        self.tree.heading("Total Watched", text="Total Watched", anchor="w")
        self.tree.heading("Progress", text="Progress", anchor="w")

        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Check", command=self.check_item)
        self.context_menu.add_command(label="Uncheck", command=self.uncheck_item)

        

        self.watched_items_file = "watched_items.txt"
        self.watched_items = self.load_watched_items()

        self.config = "config.txt"

        self.filePathText.set(self.read_root_folder())

    
    def set_directory(self):
        try:
            folder_selected = filedialog.askdirectory()
            folder_selected = folder_selected.replace("/", "\\")
            if folder_selected == "":
                raise 
            with open('config.txt', 'w') as config_file:
                config_file.write(f'rootDirectory=\"{folder_selected}\"')
        except:
            folder_selected = self.current_folder
        finally:
            self.root_folder = folder_selected
            self.current_folder = folder_selected
            self.show_folder_contents(folder_selected)

    def load_watched_items(self):
        if os.path.exists(self.watched_items_file):
            with open(self.watched_items_file, 'r') as file:
                return set(file.read().splitlines())
        return set()

    def save_watched_items(self):
        with open(self.watched_items_file, 'w') as file:
            file.write('\n'.join(self.watched_items))

    def read_root_folder(self):
        try:
            
            with open(self.config, 'r') as file:
                path = file.read().split("\"")[1]
            if path == "":
                raise 
        except:
            # Sets default path to C:\Users\{current user}\Videos
            path = f"C:\\Users\\{getpass.getuser()}\\Videos"
        finally:
            self.root_folder = path
            self.current_folder = path
            self.show_folder_contents(path)
            return path

    def calculate_progress(self, path):
        total_files = 0
        watched_files = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(FILE_TYPE):
                    total_files += 1
                    if os.path.join(root, file) in self.watched_items:
                        watched_files += 1
        return watched_files, total_files, (watched_files / total_files) * 100 if total_files != 0 else 0

    def show_folder_contents(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.filePathText.set(path)
            for item_name in os.listdir(path):
                item_path = os.path.join(path, item_name)
                watched_value = "X" if item_path in self.watched_items else ""
                if os.path.isdir(item_path): # Folder
                    watched_files, total_files, progress = self.calculate_progress(item_path)
                    progress = f"{progress:.2f}%"
                    watched_value = "X" if progress == "100.00%" else ""
                    completed = ""
                    if progress != "0.00%":
                        completed = "startedFolder"
                        if watched_value == "X":
                            completed = "completedFolder"
                        
                    self.tree.insert("", "end", text="", values=(item_name, "Folder", watched_value, f"{watched_files}/{total_files}", progress), open=True, tags=completed)
                else: # File
                    completed = "completed" if watched_value == "X" else ""
                    if(item_name.endswith(FILE_TYPE)):
                        self.tree.insert("", "end", text="", values=(item_name, "File", watched_value, "", ""), open=True, tags=completed)
        except PermissionError:
            pass


    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        item_name, item_type = self.tree.item(item, "values")[:2]

        if item_type == "Folder":
            self.current_folder = os.path.join(self.current_folder, item_name)
            self.show_folder_contents(self.current_folder)
        elif item_type == "File":
            os.startfile(os.path.join(self.current_folder, item_name))

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return
        # if item not in self.tree.selection():
        #     self.tree.selection_set(item)

        # self.tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)

    def check_item(self):
        for item in self.tree.selection():
            item_name, item_type = self.tree.item(item, "values")[:2]
            item_path = os.path.join(self.current_folder, item_name)
            
            if item_type == "File":
                if item_name.endswith(FILE_TYPE):
                    self.watched_items.add(item_path)
                    self.tree.set(item, column="Watched", value="X")
            elif item_type == "Folder":
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith(FILE_TYPE):
                            file_path = os.path.join(root, file)
                            self.watched_items.add(file_path)
        
        self.save_watched_items()
        self.show_folder_contents(self.current_folder)  # Refresh the tree view to reflect changes


    def uncheck_item(self):
        for item in self.tree.selection():
            item_name, item_type = self.tree.item(item, "values")[:2]
            item_path = os.path.join(self.current_folder, item_name)
            
            if item_type == "File":
                if item_name.endswith(FILE_TYPE):
                    self.watched_items.discard(item_path)
                    self.tree.set(item, column="Watched", value="")
            elif item_type == "Folder":
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith(FILE_TYPE):
                            file_path = os.path.join(root, file)
                            self.watched_items.discard(file_path)
        self.save_watched_items()
        self.show_folder_contents(self.current_folder)  # Refresh the tree view to reflect changes

    def navigate_up(self):
        parent_folder = os.path.dirname(self.current_folder)
        self.current_folder = parent_folder
        self.show_folder_contents(self.current_folder)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
