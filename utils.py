import tkinter as tk
from tkinter import filedialog, ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from nptdms import TdmsFile
import os
import pySPM
#### to extract bruker channel names
import contextlib
import re
import pandas as pd

def extract_channel_names_bruker(self, Scan):
        chans = []
        for layer in Scan.layers:
            with contextlib.suppress(KeyError):
                temp = layer[b"@2:Image Data"][0].decode("latin1")
                pattern = r'"(.*?)"'
                match = re.search(pattern, temp)
                extracted_channel_name = match.group(1)
                chans.append(extracted_channel_name)
        return chans

def load_bruker(file_path):
    blend = pySPM.Bruker(file_path)
    channels = []
    for layer in blend.layers:
        with contextlib.suppress(KeyError):
            temp = layer[b"@2:Image Data"][0].decode("latin1")
            pattern = r'"(.*?)"'
            match = re.search(pattern, temp)
            extracted_channel_name = match.group(1)
            channels.append(extracted_channel_name)
    return blend, channels


