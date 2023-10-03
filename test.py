from tkintertable import TableCanvas, TableModel
import tkinter as tk

def get_color(percentage):
    red = int((100 - percentage) * 255 / 100)
    green = int(percentage * 255 / 100)
    return f"#{red:02x}{green:02x}00"

root = tk.Tk()
root.geometry("800x600")

table = TableCanvas(root)
table.show()

for i in range(1, 11):
    percentage = i * 10
    table.model.setValueAt(f"{percentage}%", i, 1)
    color = get_color(percentage)
    table.setCellColor(i, 1, color)

root.mainloop()
