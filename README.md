# GUI Image Selector

This project provides a Python-based graphical user interface (GUI) for visualizing, analyzing, and extracting data from TDMS files. The application allows users to select regions of an image, compute statistics, and save results, including calculated surface parameters.

![Model](https://github.com/CHILLQQ/cells_quadrants_extractor/blob/master/screenshot.png)

## Features

- Load and visualize data from `.tdms` files.
- Select channels and scan directions dynamically from dropdown menus.
- Manually select areas of interest on the image.
- Compute and display statistics for the selected region.
- Compute and save surface parameters to an Excel file.

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

1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_folder>
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python gui_image_selection.py
   ```

2. Use the GUI to:
   - Load `.tdms` files using the "Load Data File" button.
   - Select scan direction and channel from the dropdown menus.
   - Specify the size of the selection rectangle and physical dimensions.
   - Select a region on the image by dragging the mouse.
   - Compute statistics or surface parameters for the selected area.
   - Save the selected area or computed parameters to files.

## GUI Elements

### Buttons

- **Load Data File**: Opens a dialog to load a `.tdms` file.
- **Save Selected Area**: Saves the selected region as a `.npy` file.
- **Compute Stats**: Computes and displays mean and standard deviation for the selected region.
- **Compute Parameters**: Computes surface parameters and saves them as an Excel file.

### Dropdowns

- **Scan Direction**: Select scan direction (e.g., "Retrace (Frame 2)" or "Trace (Frame 1)").
- **Channel**: Select a channel from the loaded file.

### Inputs

- **Rectangle Size (px)**: Specify the size of the selection rectangle in pixels.
- **Physical Dimensions**: Specify the physical dimensions of the image in microns (default: 10).

## Example Workflow

1. Load a `.tdms` file containing data.
2. Select the desired scan direction and channel.
3. Use the mouse to select a region of interest on the image.
4. Compute statistics or surface parameters for the selected region.
5. Save results to a `.npy` or `.xlsx` file.


