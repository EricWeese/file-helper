import os
import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import *
from datetime import date
import getpass
import re
import numpy as np

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python File Explorer")
        self.root.geometry("900x600")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Set Root Directory", command=self.set_directory)
        self.file_menu.add_command(label="Add File Type", command=self.add_file_type_window)
        self.file_menu.add_command(label="Clear All File Types", command=self.clear_file_types)
        
        self.filePathText = StringVar()
        self.file_path_text = Label(self.frame, textvariable=self.filePathText)
        self.file_path_text.pack(side="top", anchor="w")

        self.back_button = ttk.Button(self.frame, text="Up Folder", command=self.navigate_up)
        self.back_button.pack(side="top",anchor="w")

        self.tree = ttk.Treeview(self.frame, columns=("Name", "Type", "Watched", "Total Watched", "Progress", "Date Completed"))
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
        self.tree.column("Date Completed", width=100, stretch="no")

        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("Name", text="Name", anchor="w")
        self.tree.heading("Type", text="Type", anchor="w")
        self.tree.heading("Watched", text="Watched?", anchor="w")
        self.tree.heading("Total Watched", text="Total Watched", anchor="w")
        self.tree.heading("Progress", text="Progress", anchor="w")
        self.tree.heading("Date Completed", text="Date Completed", anchor="w")

        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Check", command=self.check_item)
        self.context_menu.add_command(label="Uncheck", command=self.uncheck_item)

        self.file_types = ("",)

        self.watched_items_file = "watched_items.txt"

        self.config = "config.txt"
        self.root_folder = ""
        self.current_folder = ""

        self.watched_items = self.load_watched_items()
        self.read_file_types()
        
        self.filePathText.set(self.read_root_folder())

        

    def clear_file_types(self):
        try:
            self.file_types = (" ",)
            with open(self.config, 'a+') as file:
                file.seek(0)
                content = file.read()
            new_content = re.sub(r'fileTypes=\(.*\)', f'fileTypes=', content)
            with open(self.config, 'w+') as file:
                file.write(new_content)
        except Exception as e:
                print(f"Error: {e}")
        self.show_folder_contents(self.current_folder)
    def add_file_types(self):
        new_file_type = self.file_type_entry.get()
        if new_file_type:
            new_file_type = new_file_type if new_file_type.startswith('.') else '.' + new_file_type
            self.file_types += (new_file_type,)
            try:
                with open(self.config, 'a+') as file:
                    file.seek(0)
                    content = file.read()
                if re.search(r'fileTypes', content):
                    new_content = re.sub(r'fileTypes=.*', f'fileTypes={self.file_types}', content)
                else: 
                    new_content = content + (f'fileTypes={self.file_types}\n')
                with open(self.config, 'w') as file:
                    file.write(new_content)
            except Exception as e:
                print(f"Error: {e}")
        self.new_window.destroy()
        self.show_folder_contents(self.current_folder)

    
    def add_file_type_window(self):
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Add File Type")
        
        label = tk.Label(self.new_window, text=f"What file type would you like to add?\nAlready added: {self.file_types}")
        label.pack(pady=10)
        
        self.file_type_entry = tk.Entry(self.new_window)
        self.file_type_entry.pack(pady=10)
        
        add_button = tk.Button(self.new_window, text="Add", command=self.add_file_types)
        add_button.pack(pady=10)


    def set_directory(self):
        try:
            folder_selected = filedialog.askdirectory()
            folder_selected = folder_selected.replace("/", "\\")
            if folder_selected == "":
                raise 
            config_lines = []
            with open(self.config, 'a+') as file:
                file.seek(0)
                lines = file.readlines()
                config_lines = [line for line in lines if not line.startswith("rootDirectory=")]
            config_lines.append(f"rootDirectory={folder_selected}\n")
            with open(self.config, 'w') as config_file:
                config_file.writelines(config_lines)
        except:
            folder_selected = self.current_folder
        finally:
            self.root_folder = folder_selected
            self.current_folder = folder_selected
            self.show_folder_contents(folder_selected)

    def load_watched_items(self):
        if os.path.exists(self.watched_items_file):
            with open(self.watched_items_file, 'a+') as file:
                file.seek(0)
                itemList = list(file.read().splitlines())
                return itemList
        return list()

    def save_watched_items(self):
        with open(self.watched_items_file, 'w') as file:
            file.write('\n'.join(self.watched_items))

    def read_file_types(self):
        try:
            with open(self.config, 'a+') as file:
                file.seek(0)
                for line in file.read().split("\n"):
                    if line.startswith("fileTypes="):
                        types = line.split("=")[1]
                        types = re.findall(r"\.\w*", types)
            if types == "":
                raise 
        except:
            types = ()
        finally:
            self.file_types = tuple(types)

    def read_root_folder(self):
        try:
            with open(self.config, 'a+') as file:
                file.seek(0)
                for line in file.read().split("\n"):
                    if line.startswith("rootDirectory"):
                        path = line.split("=")[1]
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
                if file.endswith(self.file_types):
                    total_files += 1
                    for item in self.watched_items:
                        if os.path.join(root, file) in item[0:-10]:
                            watched_files += 1
        return watched_files, total_files, (watched_files / total_files) * 100 if total_files != 0 else 0

    def getItemDate(self, item_name):
        for item in reversed(self.watched_items): # Finds the item in the item+date self.watched_items list
            if item_name in item:
                print(item)
                return item[-10:] # Returns the date at the end of the string
        return ""
    
    def show_folder_contents(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.filePathText.set(path)
            for item_name in os.listdir(path):
                
                item_path = os.path.join(path, item_name)
                watched_value = ""
                itemDate = ""
                for item in self.watched_items:
                    if item_path in item[0:-10]:
                        watched_value = "X"
                        break
                if os.path.isdir(item_path): # Folder
                    watched_files, total_files, progress = self.calculate_progress(item_path)
                    progress = f"{progress:.2f}%"
                    watched_value = "X" if progress == "100.00%" else ""
                    completed = ""
                    if progress != "0.00%":
                        completed = "startedFolder"
                        if watched_value == "X":
                            completed = "completedFolder"
                    if progress == "100.00%":
                        itemDate = self.getItemDate(item_path)         
                    self.tree.insert("", "end", text="", values=(item_name, "Folder", watched_value, f"{watched_files}/{total_files}", progress, itemDate), open=True, tags=completed)
                else: # File
                    completed = "completed" if watched_value == "X" else ""
                    itemDate = self.getItemDate(item_name)
                    if(item_name.endswith(self.file_types)):
                        self.tree.insert("", "end", text="", values=(item_name, "File", watched_value, "", "", itemDate), open=True, tags=completed)
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
        self.context_menu.post(event.x_root, event.y_root)

    def check_item(self):
        for item in self.tree.selection():
            item_name, item_type = self.tree.item(item, "values")[:2]
            item_path = os.path.join(self.current_folder, item_name)
            
            if item_type == "File":
                if item_name.endswith(self.file_types):
                    currentDate = date.today().strftime("%m/%d/%Y")
                    item_path += currentDate
                    if(item_path not in self.watched_items):
                        self.watched_items.append(item_path)
                    self.tree.set(item, column="Watched", value="X")
                    self.tree.set(item, column="Date Completed", value=date.today().strftime("%m/%d/%Y"))
            elif item_type == "Folder":
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith(self.file_types):
                            file_path = os.path.join(root, file)
                            file_path += date.today().strftime("%m/%d/%Y")
                            if(file_path not in self.watched_items):
                                self.watched_items.append(file_path)
        
        self.save_watched_items()
        self.show_folder_contents(self.current_folder)  # Refresh the tree view to reflect changes


    def uncheck_item(self):
        for item in self.tree.selection():
            item_name, item_type = self.tree.item(item, "values")[:2]
            item_path = os.path.join(self.current_folder, item_name)
            
            if item_type == "File":
                if item_name.endswith(self.file_types):
                    itemIndex = [self.watched_items.index(l) for l in self.watched_items if l.startswith(item_path)]
                    if len(itemIndex) != 0:
                        self.watched_items.pop(itemIndex[0])
                    self.tree.set(item, column="Watched", value="")
            elif item_type == "Folder":
                for root, dirs, files in os.walk(item_path):
                    for file in files:
                        if file.endswith(self.file_types):
                            file_path = os.path.join(root, file)
                            itemIndex = [self.watched_items.index(l) for l in self.watched_items if l.startswith(item_path)]
                            if len(itemIndex) != 0:
                                self.watched_items.pop(itemIndex[0])
        self.save_watched_items()
        self.show_folder_contents(self.current_folder)  # Refresh the tree view to reflect changes

    def navigate_up(self):
        parent_folder = os.path.dirname(self.current_folder)
        self.current_folder = parent_folder
        self.show_folder_contents(self.current_folder)

root = tk.Tk()
app = FileExplorer(root)
root.mainloop()
