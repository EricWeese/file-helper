import os
import tkinter as tk
from tkinter import ttk

FILE_TYPE = ".txt"

class FileExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("Python File Explorer")
        self.root.geometry("800x600")

        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(self.frame, columns=("Name", "Type", "Checked", "Progress"))
        self.tree.pack(fill="both", expand=True, side="left")

        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")

        self.tree.column("#0", width=0, stretch="no")
        self.tree.column("Name", anchor="w", width=400)
        self.tree.column("Type", anchor="w", width=100)
        self.tree.column("Checked", width=100)
        self.tree.column("Progress", width=100)

        self.tree.heading("#0", text="", anchor="w")
        self.tree.heading("Name", text="Name", anchor="w")
        self.tree.heading("Type", text="Type", anchor="w")
        self.tree.heading("Checked", text="Checked", anchor="w")
        self.tree.heading("Progress", text="Progress", anchor="w")

        self.tree.bind("<Double-1>", self.on_item_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        self.back_button = ttk.Button(self.root, text="Back", command=self.navigate_up)
        self.back_button.pack(side="top")

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Check", command=self.check_item)
        self.context_menu.add_command(label="Uncheck", command=self.uncheck_item)

        self.checked_items_file = "checked_items.txt"
        self.checked_items = self.load_checked_items()

        self.set_root_folder("C:\\Users\\eric.weese\\Documents\\Projects\\Python Test\\FileTracker\\root")

    def load_checked_items(self):
        if os.path.exists(self.checked_items_file):
            with open(self.checked_items_file, 'r') as file:
                return set(file.read().splitlines())
        return set()

    def save_checked_items(self):
        with open(self.checked_items_file, 'w') as file:
            file.write('\n'.join(self.checked_items))

    def set_root_folder(self, path):
        self.root_folder = path
        self.current_folder = path
        self.show_folder_contents(path)

    def set_root_folder(self, path):
        self.root_folder = path
        self.current_folder = path
        self.show_folder_contents(path)

    def calculate_progress(self, path):
        total_files = 0
        checked_files = 0
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(FILE_TYPE):
                    total_files += 1
                    if os.path.join(root, file) in self.checked_items:
                        checked_files += 1
        return (checked_files / total_files) * 100 if total_files != 0 else 0

    def show_folder_contents(self, path):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            for item_name in os.listdir(path):
                item_path = os.path.join(path, item_name)
                checked_value = "X" if item_path in self.checked_items else ""
                if os.path.isdir(item_path):
                    progress = f"{self.calculate_progress(item_path):.2f}%"
                    self.tree.insert("", "end", text="", values=(item_name, "Folder", checked_value, progress), open=True)
                else:
                    self.tree.insert("", "end", text="", values=(item_name, "File", checked_value, ""), open=True)
        except PermissionError:
            pass


    def on_item_double_click(self, event):
        item = self.tree.selection()[0]
        item_name, item_type = self.tree.item(item, "values")[:2]

        if item_type == "Folder":
            self.current_folder = os.path.join(self.current_folder, item_name)
            self.show_folder_contents(self.current_folder)

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if not item:
            return

        self.tree.selection_set(item)
        self.context_menu.post(event.x_root, event.y_root)

    def check_item(self):
        item = self.tree.selection()[0]
        item_path = os.path.join(self.current_folder, self.tree.item(item, "values")[0])
        self.checked_items.add(item_path)
        self.save_checked_items()
        self.tree.set(item, column="Checked", value="X")

    def uncheck_item(self):
        item = self.tree.selection()[0]
        item_path = os.path.join(self.current_folder, self.tree.item(item, "values")[0])
        self.checked_items.discard(item_path)
        self.save_checked_items()
        self.tree.set(item, column="Checked", value="")

    def navigate_up(self):
        parent_folder = os.path.dirname(self.current_folder)
        self.current_folder = parent_folder
        self.show_folder_contents(self.current_folder)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileExplorer(root)
    root.mainloop()
