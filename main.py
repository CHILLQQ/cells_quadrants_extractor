import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nptdms import TdmsFile
from dr_pnas.extraction import *

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

        self.stats_button = tk.Button(button_frame, text="Compute Parameters", command=self.compute_surf_params)
        self.stats_button.pack(side=tk.LEFT, padx=5, pady=5)

        # Dropdown for scan direction
        self.scan_dir_label = tk.Label(root, text="Select Scan Direction:")
        self.scan_dir_label.pack()
        self.scan_dir_var = tk.StringVar(value="Retrace (Frame 2)")
        self.scan_dir_dropdown = ttk.Combobox(root, textvariable=self.scan_dir_var, state="readonly")
        self.scan_dir_dropdown['values'] = ['Retrace (Frame 2)', 'Trace (Frame 1)']
        self.scan_dir_dropdown.pack()
        self.scan_dir_dropdown.bind("<<ComboboxSelected>>", self.update_image)

        # Dropdown for channel selection
        self.channel_label = tk.Label(root, text="Select Channel:")
        self.channel_label.pack()
        self.channel_var = tk.StringVar()
        self.channel_dropdown = ttk.Combobox(root, textvariable=self.channel_var, state="readonly")
        self.channel_dropdown.pack()
        self.channel_dropdown.bind("<<ComboboxSelected>>", self.update_image)

        # Entry for rectangle size
        size_frame = tk.Frame(root)
        size_frame.pack()
        tk.Label(size_frame, text="Rectangle Size (px):").pack(side=tk.LEFT, padx=5)
        self.size_entry = tk.Entry(size_frame, width=5)
        self.size_entry.pack(side=tk.LEFT, padx=5)
        self.size_entry.insert(0, "20")

        # Entry for physical dimensions
        dimensions_frame = tk.Frame(root)
        dimensions_frame.pack()
        tk.Label(dimensions_frame, text="Physical Dimensions, um:").pack(side=tk.LEFT, padx=5)
        self.dimensions_var = tk.DoubleVar(value=10)
        self.dimensions_entry = tk.Entry(dimensions_frame, textvariable=self.dimensions_var, width=5)
        self.dimensions_entry.pack(side=tk.LEFT, padx=5)
        self.dimensions_var.trace_add("write", self.update_physical_dimensions)

        self.info_label = tk.Label(root, text="Load an image file to start.")
        self.info_label.pack()

        self.stats_label = tk.Label(root, text="")
        self.stats_label.pack()

        self.figure, (self.ax, self.ax_sub) = plt.subplots(1, 2, figsize=(10, 5))
        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack()

        self.image_data = None
        self.physical_dimensions = 10  # Default physical dimensions
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.rect_size = 20  # Fixed size of the rectangle
        self.is_dragging = False
        self.extracted_area = None
        self.tdms_blend = None  # Store the TDMS file object
        self.sh = None

    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("TDMS files", "*.tdms"), ("All files", "*.*")])
        if file_path:
            try:
                self.tdms_blend = TdmsFile.read(file_path)
                scan_dir = self.scan_dir_var.get()
                channels = list(self.tdms_blend[scan_dir]._channels.keys())

                # Populate channel dropdown
                self.channel_dropdown['values'] = channels
                if not self.channel_var.get():
                    self.channel_var.set(channels[0])

                self.update_image()
            except Exception as e:
                self.info_label.config(text=f"Error loading file: {e}")

    def update_physical_dimensions(self, *args):
        try:
            self.physical_dimensions = self.dimensions_var.get()
            self.info_label.config(text=f"Physical Dimensions updated to {self.physical_dimensions}")
        except ValueError:
            self.info_label.config(text="Invalid physical dimensions value!")

    def update_image(self, event=None):
        if self.tdms_blend is not None:
            try:
                scan_dir = self.scan_dir_var.get()
                channel = self.channel_var.get()
                if scan_dir and channel:
                    tmp = self.tdms_blend[scan_dir][channel].data
                    self.sh = int(np.sqrt(tmp.shape[0]))
                    self.image_data = tmp.reshape(self.sh, self.sh)

                    self.show_image()

                    # Compute and display stats for the entire image
                    mean_value = np.mean(self.image_data)
                    std_dev = np.std(self.image_data)
                    self.stats_label.config(text=f"Full Image Stats - Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
            except Exception as e:
                self.info_label.config(text=f"Error updating image: {e}")

    def show_image(self):
        if self.image_data is not None:
            self.ax.clear()
            self.ax.imshow(self.image_data, cmap='YlOrBr_r')
            self.ax.set_title("Drag to select an area")
            self.ax_sub.clear()
            self.ax_sub.set_title("Selected Area")
            self.canvas.draw()

            self.canvas.mpl_connect("button_press_event", self.on_press)
            self.canvas.mpl_connect("motion_notify_event", self.on_drag)
            self.canvas.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event):
        if event.inaxes == self.ax:
            self.is_dragging = True
            self.start_x = int(event.xdata)
            self.start_y = int(event.ydata)

            # Update rectangle size from entry
            try:
                self.rect_size = int(self.size_entry.get())
            except ValueError:
                self.info_label.config(text="Invalid rectangle size! Using default 20px.")
                self.rect_size = 20

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

                # Plot selected area in the subplot
                self.ax_sub.clear()
                self.ax_sub.imshow(self.extracted_area, cmap='YlOrBr_r')
                self.ax_sub.set_title("Selected Area")
                self.canvas.draw()
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

    def compute_surf_params(self):
        if self.extracted_area is not None:
            dx = (self.physical_dimensions*1000)/self.sh
            #print(dx, self.physical_dimensions, self.sh)
            params = extract_parameters(self.extracted_area,dx,dx,self.rect_size,fitted=False)
            #print("Params:", params)
            # Convert parameters to a DataFrame for saving
            params_df = pd.DataFrame.from_dict(params, orient='index', columns=['Value'])

            # Save to an Excel file
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
            if file_path:
                params_df.to_excel(file_path, index=True)
                self.info_label.config(text="Surface parameters saved successfully!")
            else:
                self.info_label.config(text="Save operation canceled.")
        else:
            self.info_label.config(text="No area selected to compute surface parameters.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
