import os
import shutil
import hashlib
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import webbrowser

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

#Categories
types = {
    "Images": [".jpg", ".png", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".tiff", ".tif", ".heic", ".ico", ".avif"],
    "Documents": [".pdf", ".docx", ".txt", ".doc", ".pptx", ".xlsx", ".xls", ".ppt", ".rtf", ".csv", ".pages", ".key", ".numbers", ".epub", ".odt", ".ods", ".odp"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Music": [".mp3", ".wav", ".aac", ".m4a", ".flac", ".wma", ".ogg"],
    "Programs": [".exe", ".msi", ".bat", ".cmd", ".apk"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".iso"],
    "Development": [".html", ".css", ".js", ".ts", ".py", ".json", ".java", ".cpp", ".cs", ".xml", ".md", ".sh", ".sql", ".yaml", ".yml"],
    "Torrents": [".torrent"],
    "Shortcuts" : [".lnk", ".url"]
    
}

#Undo
last_moves = []

#Theme 
current_theme = "dark"

#FUNCTIONS
def browse():
    path = filedialog.askdirectory()
    if path:
        folder.set(path)

def get_category(filename):
    ext = os.path.splitext(filename)[1].lower()

    for category, exts in types.items():
        if ext in exts:
            return category

    return "Others"

def preview():

    path = folder.get()

    if not os.path.exists(path):
        messagebox.showerror("Error", "Folder not found")
        return

    log.delete("1.0", "end")

    count = 0

    for file in os.listdir(path):

        file_path = os.path.join(path, file)

        if os.path.isdir(file_path):
            continue

        category = get_category(file)

        log.insert(
            "end",
            f"PREVIEW: {file} → {category}\n"
        )

        count += 1

    log.insert(
        "end",
        f"\nTotal files to organize: {count}"
    )

def organize():
    

    path = folder.get()

    if not os.path.exists(path):
        messagebox.showerror("Error", "Folder not found")
        return

    log.delete("1.0", "end")
    last_moves.clear()

    moved = 0

    files = [
        file
        for file in os.listdir(path)
        if not os.path.isdir(
            os.path.join(path, file)
        )
    ]
    progress.set(0)
    total_files = len(files)
    if total_files == 0:

        messagebox.showinfo(
            "Info",
            "No files found to organize."
        )

        return
    
    category_count = {}

    for index, file in enumerate(files, start=1):

        file_path = os.path.join(path, file)

        category = get_category(file)
        category_count[category] = (
            category_count.get(category, 0) + 1
        )

        dest_folder = os.path.join(path, category)
        os.makedirs(dest_folder, exist_ok=True)

        destination = os.path.join(dest_folder, file)

        try:

            shutil.move(file_path, destination)

            last_moves.append(
                (destination, file_path)
            )

            log.insert(
                "end",
                f"✓ {file} → {category}\n"
            )

            moved += 1
            progress.set(
                index / total_files
            )

            root.update_idletasks()

        except Exception as e:

            log.insert(
                "end",
                f"✗ Error moving {file}: {e}\n"
            )
    if category_count:

        log.insert(
            "end",
            "\n\nSummary:\n"
        )

        for category, count in category_count.items():

            log.insert(
                "end",
                f"\n{category}: {count}"
            )

    progress.set(1)

    messagebox.showinfo(
        "Done",
        f"{moved} files organized successfully."
    )

    progress.set(0)

def undo():

    if not last_moves:
        messagebox.showinfo(
            "Undo",
            "Nothing to undo."
        )
        return

    restored = 0

    for moved_path, original_path in reversed(last_moves):

        try:

            if os.path.exists(moved_path):

                shutil.move(
                    moved_path,
                    original_path
                )

                restored += 1

        except Exception as e:

            log.insert(
                "end",
                f"\nUndo error: {e}"
            )
    log.insert(
        "end",
        f"\n\nUNDO COMPLETE ({restored} files restored)\n"
    )

    messagebox.showinfo(
        "Undo",
        f"{restored} files restored."
)
    last_moves.clear()
    # Remove empty category folders
    for category in list(types.keys()) + ["Others"]:

        category_folder = os.path.join(
           folder.get(),
           category
         )

        if (
            os.path.exists(category_folder)
            and not os.listdir(category_folder)
         ):
            os.rmdir(category_folder)

    last_moves.clear()

def file_hash(filepath):

    hasher = hashlib.sha256()

    with open(filepath, "rb") as f:

        while chunk := f.read(8192):
            hasher.update(chunk)

    return hasher.hexdigest()

def find_duplicates():

    path = folder.get()

    if not os.path.exists(path):
        messagebox.showerror(
            "Error",
            "Folder not found"
        )
        return

    log.delete("1.0", "end")

    hashes = {}
    duplicates_found = False

    for root, dirs, files in os.walk(path):
        progress.set(0)
        for file in files:

            file_path = os.path.join(root, file)

            try:

                h = file_hash(file_path)

                if h in hashes:

                    duplicates_found = True

                    log.insert(
                        "end",
                        f"DUPLICATE:\n"
                        f"{file_path}\n"
                        f"Matches: {hashes[h]}\n\n"
                    )

                else:
                    hashes[h] = file_path

            except Exception as e:

                log.insert(
                    "end",
                    f"Error reading {file_path}: {e}\n"
                )

    if not duplicates_found:

        log.insert(
            "end",
            "No duplicate files found."
        )

def toggle_theme():

    global current_theme, COLORS

    if current_theme == "dark":

        ctk.set_appearance_mode("light")

        COLORS = LIGHT_COLORS

        current_theme = "light"
        theme_btn.configure(text="🌙")
        font=("Segoe UI Emoji", 13),

    else:

        ctk.set_appearance_mode("dark")

        COLORS = DARK_COLORS

        current_theme = "dark"
        theme_btn.configure(text="☀️")
        font=("Segoe UI Emoji", 13),
        
    apply_theme()

def apply_theme():

    root.configure(
        fg_color=COLORS["window_bg"]
    )

    header_frame.configure(
        fg_color=COLORS["header_bg"]
    )

    main_frame.configure(
        fg_color=COLORS["main_bg"]
    )

    folder_frame.configure(
        fg_color=COLORS["card_bg"]
    )

    button_frame.configure(
        fg_color=COLORS["card_bg"]
    )

    entry.configure(
        fg_color=COLORS["entry_bg"],
        text_color=COLORS["textbrowse"]
    )

    log.configure(
        fg_color=COLORS["textbox_bg"],
        text_color=COLORS["textlog"]
    )

    browse_btn.configure(
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    preview_btn.configure(
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    organize_btn.configure(
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    undo_btn.configure(
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    duplicate_btn.configure(
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    git_btn.configure(
        fg_color=COLORS["button_bg"],
        text_color=COLORS["text"],
        hover_color=COLORS["button_hover"]
    )

    theme_btn.configure(
        width=50,
        text_color=COLORS["text"],
        fg_color=COLORS["button_bg"],
        hover_color=COLORS["button_hover"]
    )

    title.configure(
        text_color=COLORS["textfileflow"]
    )

    version.configure(
        text_color=COLORS["textfileflow"]
    )

    footer.configure(
        text_color=COLORS["textfileflow"]
    )
    
    progress.configure(
    progress_color=COLORS["button_bg"]
)
    
def open_github():
    webbrowser.open("https://github.com/K-SuhasM")

#UI
DARK_COLORS = {
    "window_bg": "#101620",
    "header_bg": "#101620",
    "main_bg": "#101620",
    "card_bg": "#161F2E",
    "button_bg": "#111825",
    "button_hover": "#0C111B",
    "textbox_bg": "#161F2E",
    "entry_bg": "#141C2B",
    "text": "#FFFFFF",
    "textbrowse": "#FFFFFF",
    "textlog": "#FFFFFF",
    "textfileflow": "#ffffff"
}

LIGHT_COLORS = {
    "window_bg": "#FFFFFF",
    "header_bg": "#FFFFFF",
    "main_bg": "#FFFFFF",
    "card_bg": "#D1E7D3",
    "button_bg": "#2A4937",
    "button_hover": "#93D698",
    "textbox_bg": "#D1E7D3",
    "entry_bg": "#FFFFFF",
    "text": "#FFFFFF",
    "textbrowse": "#3F3F3F",
    "textlog": "#3F3F3F",
    "textfileflow": "#2A4937"
}

COLORS = DARK_COLORS

root = ctk.CTk()
root.title("FileFlow 2.0")
root.geometry("800x750" \
"")
root.configure(fg_color=COLORS["header_bg"])
root.minsize(700, 550)

folder = tk.StringVar()



#Header
header_frame = ctk.CTkFrame(
root,
fg_color=COLORS["header_bg"],
)
header_frame.pack(fill="x", padx=25, pady=(30, 20))

theme_btn = ctk.CTkButton(
    header_frame,
    text="☀",
    width=20,
    anchor="center",
    font=("Segoe UI", 15,),
    command=toggle_theme,
    fg_color=COLORS["button_bg"],
)
theme_btn.pack(side="right")
theme_btn.place(relx=1, rely=0, anchor="ne")

title = ctk.CTkLabel(
    header_frame,
    text="FileFlow",
    font=("Georgia", 30, "bold")
)
title.pack(side="left")

version = ctk.CTkLabel(
    header_frame,
    text="v2.0 2026",
    font=("Segoe UI", 11, "italic")
)
version.pack(side="left", padx=(5, 5))

#MainFrame
main_frame = ctk.CTkFrame(root,
fg_color=COLORS["main_bg"]
)
main_frame.pack(
    fill="both",
    expand=True,
    padx=5,
    pady=5,
    
)

#Folder Row
folder_frame = ctk.CTkFrame(
    main_frame,
    fg_color=COLORS["card_bg"]
)
folder_frame.pack(
    fill="x",
    padx=10,
    pady=10
)

entry = ctk.CTkEntry(
    folder_frame,
    textvariable=folder,
    fg_color=COLORS["entry_bg"],
    height=40
)
entry.pack(
    side="left",
    fill="x",
    expand=True,
    padx=(10, 10),
    pady=10
)

browse_btn = ctk.CTkButton(
    folder_frame,
    text="📂 Browse",
    font=("segoe UI", 13,),
    command=browse,
    fg_color=COLORS["button_bg"],
    width=100,
    height=40
)
browse_btn.pack(
    padx=10,
    pady=10
)

#Buttons
button_frame = ctk.CTkFrame(
    main_frame,
    fg_color=COLORS["card_bg"]
)

button_frame.pack(
    fill="x",
    padx=10,
    pady=10
)

preview_btn = ctk.CTkButton(
    button_frame,
    text="🔍 Preview",
    font=("Segoe UI Emoji", 13),
    command=preview,
    fg_color=COLORS["button_bg"],
    hover_color=COLORS["button_hover"],
)
preview_btn.pack(
    side="left",
    padx=10,
    pady=10
)

organize_btn = ctk.CTkButton(
    button_frame,
    text="🗂️ Organize",
    font=("Segoe UI Emoji", 13),
    command=organize,
    fg_color=COLORS["button_bg"],
    hover_color=COLORS["button_hover"],
)
organize_btn.pack(
    side="left",
    padx=5,
    pady=10
)

undo_btn = ctk.CTkButton(
    button_frame,
    text="↩ Undo",
    font=("Segoe UI Emoji", 13),
    command=undo,
    fg_color=COLORS["button_bg"],
    hover_color=COLORS["button_hover"],
)
undo_btn.pack(
    side="left",
    padx=5,
    pady=10
)

duplicate_btn = ctk.CTkButton(
    button_frame,
    text="⿻ Find Duplicates",
    font=("Segoe UI Emoji", 13),
    command=find_duplicates,
    fg_color=COLORS["button_bg"],
    hover_color=COLORS["button_hover"],
)
duplicate_btn.pack(
    side="left",
    padx=5,
    pady=10
)

git_btn = ctk.CTkButton(
    button_frame,
    text="👾 Github ",
    font=("Segoe UI Emoji", 13),
    command=open_github,
    fg_color=COLORS["button_bg"],
    hover_color=COLORS["button_hover"],
)

git_btn.pack(
    side="right",
    padx=10,
    pady=10
)
# Progress Bar
progress = ctk.CTkProgressBar(
    main_frame
)

progress.pack(
    fill="x",
    padx=11,
    pady=(0, 10)
)

progress.set(0)

#Log
log = ctk.CTkTextbox(
    main_frame,
    fg_color=COLORS["textbox_bg"],
    font=("Consolas", 12)
)

log.pack(
    fill="both",
    expand=True,
    padx=15,
    pady=15
)

#Footer
footer = ctk.CTkLabel(
    root,
    text="FileFlow • File Organizer",
    font=("Segoe UI", 11)
)
footer.pack(pady=(0, 10))

apply_theme()
root.mainloop()