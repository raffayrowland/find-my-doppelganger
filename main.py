from populate_database import make_embedding_aligned, populate_database, generate_attributes
from database import get_nearest_neighbors_cosine
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from get_image import drive_image_url_to_b64
import base64
import io
import threading
import queue

TOP_K = 5
photos = []
image = None  # selected file path
preview_label = None

status_queue = queue.Queue()
worker_thread = None

# populate_database()

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

choose_btn = tk.Button(upload, text="Choose file...")
choose_btn.pack(pady=6)

# --- Loading popup (spinner + status text) ---
loading_win = tk.Toplevel(root)
loading_win.title("Working")
loading_win.resizable(False, False)
loading_win.withdraw()
loading_win.protocol("WM_DELETE_WINDOW", lambda: None)

loading_label = tk.Label(loading_win, text="Starting...", wraplength=340, justify="left")
loading_label.pack(padx=20, pady=(18, 10))

loading_bar = ttk.Progressbar(loading_win, mode="indeterminate", length=280)
loading_bar.pack(padx=20, pady=(0, 18))

def _center_loading_window():
    loading_win.update_idletasks()
    rw = root.winfo_width()
    rh = root.winfo_height()
    rx = root.winfo_rootx()
    ry = root.winfo_rooty()

    ww = loading_win.winfo_width()
    wh = loading_win.winfo_height()

    x = rx + (rw // 2) - (ww // 2)
    y = ry + (rh // 2) - (wh // 2)
    loading_win.geometry(f"+{max(x, 0)}+{max(y, 0)}")

def show_loading(text: str):
    loading_label.config(text=text)
    loading_win.deiconify()
    loading_win.transient(root)
    loading_win.grab_set()
    _center_loading_window()
    loading_bar.start(10)

def set_loading_text(text: str):
    loading_label.config(text=text)
    loading_win.update_idletasks()

def hide_loading():
    loading_bar.stop()
    try:
        loading_win.grab_release()
    except Exception:
        pass
    loading_win.withdraw()
# --- end loading popup ---


def open_image_source(src: str) -> Image.Image:
    """
    Supports:
      - local file paths
      - Google Drive links (downloaded via get_image.py -> base64)
    """
    if src.startswith("http://") or src.startswith("https://"):
        b64 = drive_image_url_to_b64(src)
        data = base64.b64decode(b64)
        return Image.open(io.BytesIO(data)).convert("RGB")
    return Image.open(src).convert("RGB")


def show_upload():
    results.pack_forget()
    upload.pack(padx=20, pady=20)


def show_results(nearest, q_img=None, result_imgs=None):
    upload.pack_forget()
    for w in results.winfo_children():
        w.destroy()
    photos.clear()

    tk.Button(results, text="Back", command=show_upload).pack(anchor="w", padx=10, pady=10)

    if q_img is None:
        q_img = open_image_source(image)
        q_img.thumbnail((500, 500))

    qtk = ImageTk.PhotoImage(q_img)
    photos.append(qtk)
    tk.Label(results, image=qtk).pack(pady=10)

    row = tk.Frame(results)
    row.pack(pady=10)

    if result_imgs is None:
        result_imgs = []
        for path, *_ in nearest[:TOP_K]:
            try:
                img = open_image_source(path)
                img.thumbnail((180, 180))
                result_imgs.append(img)
            except Exception:
                result_imgs.append(None)

    for idx, img in enumerate(result_imgs[:TOP_K], 1):
        if img is None:
            tk.Label(row, text=f"Failed to load\n{idx}", width=18, height=6).pack(side="left", padx=6)
            continue
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
        im = open_image_source(image)
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


def _run_query_worker(img_path: str):
    try:
        status_queue.put(("status", "Creating embedding..."))
        emb = make_embedding_aligned(img_path)

        status_queue.put(("status", "Getting closest matches..."))
        nearest = get_nearest_neighbors_cosine(emb)

        status_queue.put(("status", "Loading query image..."))
        q_img = open_image_source(img_path)
        q_img.thumbnail((500, 500))

        result_imgs = []
        for idx, (path, *_rest) in enumerate(nearest[:TOP_K], 1):
            status_queue.put(("status", f"Loading image {idx}/{TOP_K}..."))
            try:
                img = open_image_source(path)
                img.thumbnail((180, 180))
                result_imgs.append(img)
            except Exception:
                result_imgs.append(None)

        status_queue.put(("done", nearest, q_img, result_imgs))
    except Exception as e:
        status_queue.put(("error", str(e)))


def _poll_status_queue():
    global worker_thread
    while True:
        try:
            msg = status_queue.get_nowait()
        except queue.Empty:
            break

        kind = msg[0]
        if kind == "status":
            set_loading_text(msg[1])

        elif kind == "done":
            nearest, q_img, result_imgs = msg[1], msg[2], msg[3]
            hide_loading()
            choose_btn.config(state="normal")
            find_btn.config(state="normal")
            show_results(nearest, q_img=q_img, result_imgs=result_imgs)
            worker_thread = None
            return

        elif kind == "error":
            hide_loading()
            choose_btn.config(state="normal")
            find_btn.config(state="normal")
            messagebox.showerror("Error", msg[1])
            worker_thread = None
            return

    if worker_thread is not None and worker_thread.is_alive():
        root.after(60, _poll_status_queue)


def run_query():
    global worker_thread
    if not image:
        return

    choose_btn.config(state="disabled")
    find_btn.config(state="disabled")

    show_loading("Starting...")

    worker_thread = threading.Thread(target=_run_query_worker, args=(image,), daemon=True)
    worker_thread.start()
    root.after(60, _poll_status_queue)


choose_btn.config(command=choose_file)
find_btn.config(command=run_query)

show_upload()
root.mainloop()
