import random
import tkinter as tk

# Dit zorgt voor de visualisatie van het grid.
class GridUI(tk.Tk):
    def __init__(self, size, cell_size):
        super().__init__()
        self.size = size
        self.cell_size = cell_size
        self.canvas = tk.Canvas(self, width=size * cell_size, height=size * cell_size)
        self.canvas.pack()
        self.draw_grid()
        self.images = {}  # als dictionary initialiseren


    # aan de hand van deze methode voegen we fotos (png) naar de grid voor de visualisatie.
    # het zorgt er ook voor dat deze png files gescaled worden om in de vakjes van de grid te passen.
    def add_image_to_grid(self, row, col, image_path):

        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            print("Invalid grid position.")
            return
        x0 = col * self.cell_size
        y0 = row * self.cell_size
        if (row, col) in self.images:
            self.canvas.delete(self.images[(row, col)])
        self.images[(row, col)] = tk.PhotoImage(file=image_path)
        # tot nu toe kunnen we die afbeelding aan de grid toevoegen, maar we moeten die nog scalen tot een grid cell

        original_image = tk.PhotoImage(file=image_path)
        # Hier berekenen we de scaling factors om de afbeelding te fitten in de cell net zoals gedaan in OOP taak
        scale_x = self.cell_size / original_image.width()
        scale_y = self.cell_size / original_image.height()

        # De kleinste van de scales wordt gebruikt om een aspect ratio te behouden
        scale_factor = min(scale_x, scale_y)

        # Nu kan er gemakkelijk worden genormaliseerd
        resized_image = original_image.subsample(int(1 / scale_factor))
        self.images[(row, col)] = resized_image
        self.canvas.create_image(x0 + self.cell_size // 2, y0 + self.cell_size // 2, image=resized_image)

    def draw_grid(self, images=None):
        for i in range(self.size):
            for j in range(self.size):
                x0 = j * self.cell_size
                y0 = i * self.cell_size
                x1 = x0 + self.cell_size
                y1 = y0 + self.cell_size
                self.canvas.create_rectangle(x0, y0, x1, y1, outline="black")

    # deze methode zal een voor een elke cell inlezen van de logic grid en dit mappen op de logic grid.
    # Op deze manier zorgen we ervoor dat alle operaties op de logische grid plaatsvinden en dat dit automatisch
    # gemapt wordt op de visuele representatie van de grid.
    def update_ui(self, logic_grid):

        # Redraw grid
        self.draw_grid()
        dir = "pictures/"
        ext = ".png"

        for i in range(self.size):
            for j in range(self.size):
                pos = logic_grid[i][j]
                if pos.agent:
                    self.add_image_to_grid(i, j, dir+pos.agent.name+ext)
                elif pos.item:
                    self.add_image_to_grid(i, j, dir+pos.item.name+ext) #item.png
                elif pos.loading_dock:
                    self.add_image_to_grid(i, j, "pictures/loading_dock.png")
                else:
                    if (i, j) in self.images:
                        self.canvas.delete(self.images[(i, j)])
                        del self.images[(i, j)]