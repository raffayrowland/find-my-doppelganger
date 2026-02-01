from populate_database import populate_database, make_embedding, \
    make_embedding_aligned
from database import get_nearest_neighbors_cosine, get_nearest_neighbors_l2
from PIL import Image, ImageTk
import tkinter as tk

image = "Pasted image (7).png"

populate_database()
nearest = get_nearest_neighbors_cosine(make_embedding_aligned(image))

root = tk.Tk()
root.title("Nearest neighbors")

photos = []

# top image (query)
q = Image.open(image).convert("RGB")
q.thumbnail((500, 500))
qtk = ImageTk.PhotoImage(q)
photos.append(qtk)
tk.Label(root, image=qtk).pack(pady=10)

# bottom row (results)
row = tk.Frame(root)
row.pack(pady=10)

for path, *_ in nearest:
    img = Image.open(path).convert("RGB")
    img.thumbnail((180, 180))
    it = ImageTk.PhotoImage(img)
    photos.append(it)
    tk.Label(row, image=it).pack(side="left", padx=6)

root.mainloop()
