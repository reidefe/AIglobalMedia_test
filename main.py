from src.preprocess import clean_data_with_logging
from src.edit_image import create_images_with_text

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import os


class CompoundApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Data Cleaner & Image Generator")
        self.root.geometry("800x600")
        self.file_path = None
        self.sample_image_path = None
        self.df = None
        self.row_limit = tk.IntVar(value=0)
        self.create_widgets()

    def create_widgets(self):
        # Frame for File Actions
        file_frame = ttk.LabelFrame(self.root, text="File Actions", padding=10)
        file_frame.pack(fill="x", padx=10, pady=5)
        self.load_button = ttk.Button(file_frame, text="Load File", command=self.load_file)
        self.load_button.grid(row=0, column=0, padx=10, pady=5)
        self.sample_image_button = ttk.Button(file_frame, text="Upload Sample Image", command=self.upload_sample_image)
        self.sample_image_button.grid(row=0, column=1, padx=10, pady=5)
        self.clean_button = ttk.Button(file_frame, text="Clean Data", command=self.clean_data, state=tk.DISABLED)
        self.clean_button.grid(row=0, column=2, padx=10, pady=5)
        self.generate_button = ttk.Button(file_frame, text="Generate Images", command=self.generate_images,
                                          state=tk.DISABLED)
        self.generate_button.grid(row=0, column=3, padx=10, pady=5)

        ttk.Label(file_frame, text="Rows for Image Editing:").grid(row=1, column=0, sticky="w", padx=10)
        self.row_limit_entry = ttk.Entry(file_frame, textvariable=self.row_limit, width=10)
        self.row_limit_entry.grid(row=1, column=1, sticky="w", padx=10)

        # Frame for Logs
        log_frame = ttk.LabelFrame(self.root, text="Logs", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_box = ScrolledText(log_frame, height=20, wrap=tk.WORD)
        self.log_box.pack(fill="both", expand=True)

    def log_message(self, message):
        """Logs a message to the log box."""
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")

    def load_file(self):
        """Handles loading the data file."""
        file_path = filedialog.askopenfilename(filetypes=[("Excel and CSV files", "*.xlsx *.csv")])
        if file_path:
            self.file_path = file_path
            self.clean_button.config(state=tk.NORMAL)
            self.log_message(f"Loaded file: {file_path}")
        else:
            self.log_message("No file selected.")

    def upload_sample_image(self):
        """Handles uploading the sample image."""
        sample_image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg")])
        if sample_image_path:
            self.sample_image_path = sample_image_path
            self.log_message(f"Uploaded sample image: {sample_image_path}")
        else:
            self.log_message("No sample image selected.")

    def clean_data(self):
        """Cleans the data and logs changes."""
        try:
            if not self.file_path:
                messagebox.showerror("Error", "No file loaded.")
                return

            if self.file_path.endswith(".xlsx"):
                self.df = clean_data_with_logging(self.file_path, self.log_box, sheet_name="Sheet1")
            elif self.file_path.endswith(".csv"):
                self.df = clean_data_with_logging(self.file_path, self.log_box)
            else:
                messagebox.showerror("Error", "Unsupported file format.")
                return

            self.generate_button.config(state=tk.NORMAL)
            self.log_message("Data cleaning complete.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_message(f"Error during cleaning: {e}")

    def generate_images(self):
        try:
            if self.df is None:
                messagebox.showerror("Error", "No cleaned data available.")
                return

            if not self.sample_image_path:
                messagebox.showerror("Error", "No sample image uploaded.")
                return

            output_dir = filedialog.askdirectory()
            if not output_dir:
                self.log_message("No output directory selected.")
                return

            create_images_with_text(
                data=self.df,
                sample_image_path=self.sample_image_path,
                output_dir=output_dir,
                row_limit=self.row_limit.get(),
                log_callback=self.log_message,
            )

            messagebox.showinfo("Success", "Images generated successfully.")
            self.log_message(f"Images generated and saved to {output_dir}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.log_message(f"Error during image generation: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CompoundApp(root)
    root.mainloop()
