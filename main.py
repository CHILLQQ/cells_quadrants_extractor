import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nptdms import TdmsFile
import os

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

        self.add_area_button = tk.Button(button_frame, text="Add New Area", command=self.enable_add_area)
        self.add_area_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_area_button = tk.Button(button_frame, text="Save Coordinates", command=self.save_coordinates)
        self.add_area_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_area_button = tk.Button(button_frame, text="Save Im", command=self.save_image)
        self.add_area_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.add_area_button = tk.Button(button_frame, text="Drop", command=self.drop_selection)
        self.add_area_button.pack(side=tk.LEFT, padx=5, pady=5)

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
        self.size_entry.insert(0, "256")

        self.info_label = tk.Label(root, text="Load an image file to start.")
        self.info_label.pack()

        self.stats_label = tk.Label(root, text="")
        self.stats_label.pack()

        self.figure, (self.ax, self.ax_sub) = plt.subplots(1, 2, figsize=(10, 5))
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
        self.tdms_blend = None  # Store the TDMS file object
        self.sh = None
        self.add_area_mode = False
        self.directory = None
        self.file_name = None
        self.last_rectangle = None
        self.rectangles = []
        self.rectangles_coord = []
        self.area_counter = 0
        self.colors = ['red', 'blue', 'green', 'purple', 'black']


    def load_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("TDMS files", "*.tdms"), ("All files", "*.*")])
        ### Reinitialize the rectangles data if a new image is loaded
        self.rectangles = []
        self.last_rectangle = None
        self.rectangles_coord = []
        self.directory, self.file_name = os.path.split(file_path)
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
            #print(np.amin(self.image_data),np.amax(self.image_data))
            #print(np.percentile(self.image_data, 10),np.percentile(self.image_data, 90))
            vmin = np.percentile(self.image_data, 10)
            vmax = np.percentile(self.image_data, 90)
            self.ax.clear()
            self.ax.imshow(self.image_data, vmin=vmin, vmax=vmax, cmap='YlOrBr_r')
            self.ax.set_title("Drag to select an area")
            self.ax_sub.clear()
            self.ax_sub.set_title("Selected Area")
            self.canvas.draw()

            ## Draws the previously saved areas if we change channel
            if self.rectangles:
                for rect in self.rectangles:
                    self.ax.add_patch(rect)

            self.canvas.mpl_connect("button_press_event", self.on_press)
            self.canvas.mpl_connect("motion_notify_event", self.on_drag)
            self.canvas.mpl_connect("button_release_event", self.on_release)

    def enable_add_area(self):
        self.add_area_mode = True
        if self.last_rectangle:
            # Keep the last rectangle plotted
            self.rectangles.append(self.last_rectangle)
            self.rectangles_coord.append([self.start_x - self.rect_size // 2, self.start_y - self.rect_size // 2])
            self.last_rectangle = None  # Clear the last rectangle reference
        print(self.rectangles)
        # Draw all saved rectangles
        for rect in self.rectangles:
            #print("Drawing rectangles",len(self.rectangles))
            self.ax.add_patch(rect)
        self.area_counter += 1  # Increment color index for the next rectangle
        self.info_label.config(text="Add new area mode enabled. Drag to select a new area.")

    def on_press(self, event):
        if self.add_area_mode and event.inaxes == self.ax:
            self.is_dragging = True

            img_height, img_width = self.image_data.shape

            # Clamp initial rectangle position within bounds
            x = int(event.xdata)
            y = int(event.ydata)
            self.start_x = max(self.rect_size // 2, min(x, img_width - self.rect_size // 2))
            self.start_y = max(self.rect_size // 2, min(y, img_height - self.rect_size // 2))

            # Update rectangle size from entry
            try:
                self.rect_size = int(self.size_entry.get())
            except ValueError:
                self.info_label.config(text="Invalid rectangle size! Using default 256px.")
                self.rect_size = 256

            if self.rect:
                self.rect.remove()

            # Draw initial rectangle
            self.rect = self.ax.add_patch(
                plt.Rectangle(
                    (self.start_x - self.rect_size // 2, self.start_y - self.rect_size // 2),
                    self.rect_size,
                    self.rect_size,
                    edgecolor=self.colors[self.area_counter % len(self.colors)],  # Assign color,
                    facecolor="none",
                )
            )
            self.canvas.draw()

    def on_drag(self, event):
        if self.add_area_mode and self.is_dragging and event.inaxes == self.ax:

            # Get image dimensions
            img_height, img_width = self.image_data.shape
            x = int(event.xdata)
            y = int(event.ydata)

            # Clamp the rectangle's position within image bounds
            x_clamped = max(self.rect_size // 2, min(x, img_width - self.rect_size // 2))
            y_clamped = max(self.rect_size // 2, min(y, img_height - self.rect_size // 2))

            # Update the rectangle position
            self.start_x, self.start_y = x_clamped, y_clamped

            if self.rect:
                self.rect.set_xy((self.start_x - self.rect_size // 2, self.start_y - self.rect_size // 2))
            self.canvas.draw()

    def on_release(self, event):
        if self.add_area_mode and self.is_dragging:
            self.is_dragging = False

            # Finalize the rectangle
            self.last_rectangle = self.rect  # Keep track of the last selected rectangle


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
                vmin = np.percentile(self.extracted_area, 10)
                vmax = np.percentile(self.extracted_area, 90)
                self.ax_sub.imshow(self.extracted_area, vmin=vmin, vmax=vmax, cmap='YlOrBr_r')
                self.ax_sub.set_title("Selected Area")
                self.canvas.draw()
            else:
                self.info_label.config(text="Selected area is out of bounds!")

    def save_area(self):
        if self.image_data is not None and self.tdms_blend is not None:
            directory_path = filedialog.askdirectory(initialdir=self.directory,title="Select Directory to Save Areas")
            if directory_path:
                scan_dir = self.scan_dir_var.get()
                channels = list(self.tdms_blend[scan_dir]._channels.keys())

                for channel in channels:
                    try:
                        # Extract data for the channel
                        channel_data = self.tdms_blend[scan_dir][channel].data
                        sh = int(np.sqrt(channel_data.shape[0]))
                        channel_image = channel_data.reshape(sh, sh)

                        # Extract selected area for the channel
                        x_start = max(self.start_x - self.rect_size // 2, 0)
                        y_start = max(self.start_y - self.rect_size // 2, 0)
                        x_end = min(x_start + self.rect_size, channel_image.shape[1])
                        y_end = min(y_start + self.rect_size, channel_image.shape[0])

                        extracted_area = channel_image[y_start:y_end, x_start:x_end]

                        if extracted_area.shape == (self.rect_size, self.rect_size):
                            # Save the extracted area to a file
                            file_name = f"{self.file_name}_AREA{self.area_counter}_{channel}_selected_area.npy"
                            file_path = f"{directory_path}/{file_name}"
                            np.save(file_path, extracted_area)
                        else:
                            self.info_label.config(text=f"Selected area out of bounds for channel: {channel}")
                    except Exception as e:
                        self.info_label.config(text=f"Error processing channel {channel}: {e}")

                self.info_label.config(text="Selected areas saved for all channels!")
            else:
                self.info_label.config(text="Save operation canceled.")
        else:
            self.info_label.config(text="No area selected or no data loaded to save.")

    def compute_stats(self):
        if self.extracted_area is not None:
            mean_value = np.mean(self.extracted_area)
            std_dev = np.std(self.extracted_area)
            self.info_label.config(text=f"Selected area: Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
            print(f"Mean: {mean_value:.2f}, Std Dev: {std_dev:.2f}")
        else:
            self.info_label.config(text="No area selected to compute stats.")

    def save_coordinates(self):
        if self.rectangles_coord:
            # File path to save the coordinates
            file_path = f"{self.directory}/{self.file_name}_selected_areas_coordinates.txt"
            # Save the list to a text file
            with open(file_path, "w") as file:
                for pair in self.rectangles_coord:
                    file.write(f"{pair[0]}, {pair[1]}\n")

            print(f"Coordinates saved to {file_path}")
        else:
            self.info_label.config(text="No areas selected to for saving.")

    def save_image(self):
        extent = self.ax.get_window_extent().transformed(self.figure.dpi_scale_trans.inverted())
        #fig.savefig('subplot_0.png', )
        self.figure.savefig(f"{self.directory}/{self.file_name}.png",bbox_inches=extent)
        self.info_label.config(text="Current image is saved.")

    def drop_selection(self):
        self.area_counter = 0
        self.rectangles = []
        self.rectangles_coord = []
        self.last_rectangle = None
        self.show_image() 

        


if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSelectorApp(root)
    root.mainloop()
