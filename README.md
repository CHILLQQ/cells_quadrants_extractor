# GUI Image Selector

This project provides a Python-based graphical user interface (GUI) for visualizing, analyzing, and extracting data from TDMS files. The application allows users to select regions of an image, compute statistics, and save results.

![Model](https://github.com/CHILLQQ/cells_quadrants_extractor/blob/master/screenshot.png)

## Features

- Load and visualize data from `.tdms` files.
- Select channels and scan directions dynamically from dropdown menus.
- Manually select areas of interest on the image.
- Compute and display statistics for the selected region.

## Requirements

The following Python packages are required to run the application:

```plaintext
numpy
pandas
matplotlib
tk
nptdms
openpyxl
```

## Installation
*All the commands below are executed in the terminal*

1. Clone the repository:
   ```bash
   git clone https://github.com/CHILLQQ/cells_quadrants_extractor
   cd cells_quadrants_extractor
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```

2. Use the GUI to:
   - Load `.tdms` files using the "Load Data File" button.
   - Select scan direction and channel from the dropdown menus.
   - Specify the size of the selection rectangle and physical dimensions.
   - Select a region on the image by dragging the mouse.
   - Compute statistics for the selected area.
   - Save the selected area to files.

## GUI Elements

### Buttons

- **Load Data File**: Opens a dialog to load a `.tdms` file.
- **Save Selected Area**: Saves the selected region as a `.npy` file.
- **Compute Stats**: Computes and displays mean and standard deviation for the selected region.
- **Add New Area**: Creates a new area selection object that is plotted on top of the previously plotted ones.
- **Save Coordinates**: Saves coordinates of all selected areas of the current file into a `.txt` file.
- **Save Im**: Save the current image with all selected areas plotted as a `.png` file.
- **Drop**: Drop the current selections and start over.

### Dropdowns

- **Scan Direction**: Select scan direction (e.g., "Retrace (Frame 2)" or "Trace (Frame 1)").
- **Channel**: Select an AFM channel from the loaded file.

### Inputs

- **Rectangle Size (px)**: Specify the size of the selection rectangle in pixels (default: 256).

## Example Workflow

1. Load a `.tdms` file containing data.
2. Select the desired scan direction and channel.
3. Use the mouse to select a region of interest on the image by pressing **Add new area** button. 
4. Press **Save Selected Area** button to export all the channels for the selected area.
5. Keep repeeting steps 3 and 4 until enough areas are selected.
6. Press **Save Im** to save the image of the file with all the selected areas.
7. Press **Add New Area** one more time to save the coordinates of the latest selected area.
8. Press **Save Coordinates** to save a list of coordinates of all selected areas.


