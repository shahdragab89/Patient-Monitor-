import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import threading

class ArrhythmiaDetector:
    def __init__(self):
        # Thresholds for different arrhythmias
        self.tachycardia_threshold = 100  # > 100 bpm
        self.bradycardia_threshold = 60   # < 60 bpm
        # For A-fib, we'll use irregularity detection based on RR intervals
        self.afib_irregularity_threshold = 0.15
    
    def detect_arrhythmia(self, ecg_data, pattern_name):
        if pattern_name == "Tachycardia":
            return "Tachycardia", "Heart rate too high (>100 BPM)"
        elif pattern_name == "Bradycardia":
            return "Bradycardia", "Heart rate too low (<60 BPM)"
        elif pattern_name == "Atrial Fibrillation":
            return "Atrial Fibrillation", "Irregular heart rhythm detected"
        else:
            return None, None

