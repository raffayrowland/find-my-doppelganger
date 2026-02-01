from populate_database import make_embedding_aligned
from database import get_nearest_neighbors_cosine
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import os

TOP_K = 5
photos = []
image = None  # selected file path
preview_label = None

root = tk.Tk()
root.title("Find my doppelgänger")

upload = tk.Frame(root)
results = tk.Frame(root)

path_label = tk.Label(upload, text="No file selected", wraplength=600)
path_label.pack(pady=8)

preview_label = tk.Label(upload)
preview_label.pack(pady=8)

find_btn = tk.Button(upload, text="Find faces", state="disabled")
find_btn.pack(pady=6)


def show_upload():
    results.pack_forget()
    upload.pack(padx=20, pady=20)


def show_results(nearest):
    upload.pack_forget()
    for w in results.winfo_children():
        w.destroy()
    photos.clear()

    tk.Button(results, text="Back", command=show_upload).pack(anchor="w", padx=10, pady=10)

    q = Image.open(image).convert("RGB")
    q.thumbnail((500, 500))
    qtk = ImageTk.PhotoImage(q)
    photos.append(qtk)
    tk.Label(results, image=qtk).pack(pady=10)

    row = tk.Frame(results)
    row.pack(pady=10)

    for path, *_ in nearest[:TOP_K]:
        img = Image.open(path).convert("RGB")
        img.thumbnail((180, 180))
        it = ImageTk.PhotoImage(img)
        photos.append(it)
        tk.Label(row, image=it).pack(side="left", padx=6)

    results.pack(padx=20, pady=20)


def choose_file():
    global image
    image = filedialog.askopenfilename(
        title="Choose an image",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.gif *.tiff"), ("All files", "*.*")]
    )
    if not image:
        return

    if os.path.splitext(image)[1].lower() not in {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff"}:
        messagebox.showerror("Invalid file", "Please select an image file.")
        image = None
        return

    try:
        im = Image.open(image).convert("RGB")
    except Exception:
        messagebox.showerror("Invalid image", "That file couldn't be opened as an image.")
        image = None
        return

    path_label.config(text=image)

    im.thumbnail((350, 350))  # preview size
    ptk = ImageTk.PhotoImage(im)
    photos.append(ptk)  # keep ref alive
    preview_label.config(image=ptk)

    find_btn.config(state="normal")


def run_query():
    try:
        nearest = get_nearest_neighbors_cosine(make_embedding_aligned(image))
        show_results(nearest)
    except Exception as e:
        messagebox.showerror("Error", str(e))


tk.Button(upload, text="Choose file...", command=choose_file).pack(pady=6)
find_btn.config(command=run_query)

show_upload()
root.mainloop()
