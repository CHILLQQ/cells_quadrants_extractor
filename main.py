import tkinter as tk
from tkinter import filedialog
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class ImageSelectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Selector GUI")

        # Button frame for horizontal layout
        button_frame = tk.Frame(root)
        button_frame.pack()

        # Buttons
        self.load_button = tk.Button(button_frame, text="Load Data File", command=self.load_data)
        self.load_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(button_frame, text="Save Selected Area", command=self.save_area)
        self.save_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.stats_button = tk.Button(button_frame, text="Compute Stats", command=self.compute_stats)
        self.stats_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.info_label = tk.Label(root, text="Load an image file to start.")
        self.info_label.pack()

        self.stats_label = tk.Label(root, text="")
        self.stats_label.pack()

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.image_data = None
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.rect_size = 20  # Fixed size of the rectangle
        self.is_dragging = False
        self.extracted_area = None

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy"), ("All files", "*.*")])
        if file_path:
            try:
                self.image_data = np.load(file_path)
                self.show_image()
                # Compute and display stats for the entire image
                mean_value = np.mean(self.image_data)
                std_dev = np.std(self.image_data)
                self.stats_label.config(text=f"Full Image Stats - Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
            except Exception as e:
                self.info_label.config(text=f"Error loading file: {e}")

    def show_image(self):
        if self.image_data is not None:
            self.ax.clear()
            self.ax.imshow(self.image_data, cmap='YlOrBr_r')
            self.ax.set_title("Drag to select a 20x20 area")
            self.canvas.draw()

            self.canvas.mpl_connect("button_press_event", self.on_press)
            self.canvas.mpl_connect("motion_notify_event", self.on_drag)
            self.canvas.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event):
        if event.inaxes == self.ax:
            self.is_dragging = True
            self.start_x = int(event.xdata)
            self.start_y = int(event.ydata)

            if self.rect:
                self.rect.remove()

            # Draw initial rectangle
            self.rect = self.ax.add_patch(
                plt.Rectangle(
                    (self.start_x - self.rect_size // 2, self.start_y - self.rect_size // 2),
                    self.rect_size,
                    self.rect_size,
                    edgecolor="red",
                    facecolor="none",
                )
            )
            self.canvas.draw()

    def on_drag(self, event):
        if self.is_dragging and event.inaxes == self.ax:
            self.start_x = int(event.xdata)
            self.start_y = int(event.ydata)

            if self.rect:
                self.rect.set_xy((self.start_x - self.rect_size // 2, self.start_y - self.rect_size // 2))
            self.canvas.draw()

    def on_release(self, event):
        if self.is_dragging:
            self.is_dragging = False
            self.extract_area()

    def extract_area(self):
        if self.image_data is not None:
            x_start = max(self.start_x - self.rect_size // 2, 0)
            y_start = max(self.start_y - self.rect_size // 2, 0)
            x_end = min(x_start + self.rect_size, self.image_data.shape[1])
            y_end = min(y_start + self.rect_size, self.image_data.shape[0])

            self.extracted_area = self.image_data[y_start:y_end, x_start:x_end]

            if self.extracted_area.shape == (self.rect_size, self.rect_size):
                self.info_label.config(text="Area extracted successfully!")
                print("Extracted Area:")
                print(self.extracted_area)
            else:
                self.info_label.config(text="Selected area is out of bounds!")

    def save_area(self):
        if self.extracted_area is not None:
            file_path = filedialog.asksaveasfilename(defaultextension=".npy", filetypes=[("Numpy files", "*.npy"), ("All files", "*.*")])
            if file_path:
                np.save(file_path, self.extracted_area)
                self.info_label.config(text="Selected area saved successfully!")
        else:
            self.info_label.config(text="No area selected to save.")

    def compute_stats(self):
        if self.extracted_area is not None:
            mean_value = np.mean(self.extracted_area)
            std_dev = np.std(self.extracted_area)
            self.info_label.config(text=f"Selected area: Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
            print(f"Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
        else:
            self.info_label.config(text="No area selected to compute stats.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
