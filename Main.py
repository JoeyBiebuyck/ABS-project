
import tkinter as tk

class GridUI(tk.Tk):
    def __init__(self, size, cell_size=30):
        super().__init__()
        self.size = size
        self.cell_size = cell_size
        self.canvas = tk.Canvas(self, width=size*cell_size, height=size*cell_size)
        self.canvas.pack()
        self.draw_grid()

    def draw_grid(self):
        for i in range(self.size):
            for j in range(self.size):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")

if __name__ == "__main__":
    grid_ui = GridUI(10)
    grid_ui.mainloop()