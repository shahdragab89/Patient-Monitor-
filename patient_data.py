import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import threading

class PatientData:
    def __init__(self):
        self.ecg_data = []
        self.eeg_data = []
        self.spo2 = 98
        self.nibp_systolic = 120
        self.nibp_diastolic = 80
        self.ibp_systolic = 118
        self.ibp_diastolic = 78
        self.temperature = 37.0
        self.co2_percent = 5.0
        self.respiration_rate = 16
        
        self.pattern_repeat = {
            "Normal": 1,
            "Tachycardia": 0.6,  # Display more beats (faster)
            "Bradycardia": 1.5,  # Display fewer beats (slower)
            "Atrial Fibrillation": 0.8
        }
        
        # ECG patterns for normal and arrhythmias
        self.ecg_normal = [
            0, 0.1, 0.15, 0.1, 0, -0.05, -0.1, 0,      # P wave
            0, 0.1, -0.1, -0.05, 0,                   # PR segment
            0, -0.2, 1.8, -0.2, 0,                     # QRS complex
            0, 0.1, 0.3, 0.2, 0.1, 0, -0.1, 0          # T wave
        ]

        # Tachycardia: Same shape but compressed (for faster rate)
        self.ecg_tachycardia = [
            0, 0.1, 0.15, 0.1, 0,                     # P wave (shorter)
            -0.05, -0.1, 0, 0,                        # PR segment (shorter)
            -0.2, 1.5, -0.2, 0,                       # QRS complex (slightly smaller amplitude)
            0.1, 0.25, 0.1, 0, -0.1, 0                # T wave (shorter)
        ]

        # Bradycardia: Same shape but stretched (for slower rate)
        self.ecg_bradycardia = [
            0, 0.05, 0.1, 0.15, 0.1, 0.05, 0,         # P wave (longer)
            -0.05, -0.1, -0.05, 0, 0, 0,              # PR segment (longer)
            0, -0.2, -0.1, 1.8, -0.1, -0.2, 0, 0,     # QRS complex
            0, 0.1, 0.2, 0.3, 0.25, 0.2, 0.1, 0, -0.1, -0.05, 0  # T wave (longer)
        ]
        self.ecg_afib = [0, 0.1, -0.1, 0.2, -0.2, 0.1, 0.3, -0.3, 0.5, -0.2, 1.0, 0.5, 0.2, -0.3, 0.2, -0.1, 0.1, 0]
        
        # Current ECG pattern
        self.current_pattern = self.ecg_normal
        self.pattern_name = "Normal"
        
        # Pattern tracking
        self.pattern_start_time = time.time()
        self.afib_duration = 2  # Duration in seconds for A-fib
        
        # Rapid demo mode
        self.demo_mode = True
        self.demo_state = 0
        self.demo_states = ["Normal", "Tachycardia", "Normal", "Bradycardia", "Normal", "Atrial Fibrillation", "Normal"]
        self.state_duration = 10  # Increased from 5 to 10 seconds per state for more stability
        self.state_start_time = time.time()
        
        # Vital sign target values (for smoother transitions)
        self.target_spo2 = 98
        self.target_nibp_systolic = 120
        self.target_nibp_diastolic = 80
        self.target_ibp_systolic = 118
        self.target_ibp_diastolic = 78
        self.target_temperature = 37.0
        self.target_co2_percent = 5.0
        self.target_respiration_rate = 16
        
        # Transition rate (lower = more stable, gradual changes)
        self.transition_rate = 0.05  # Reduced for more stability
        
        # Initialize with some data
        for _ in range(100):
            self.ecg_data.extend(self.add_noise(self.current_pattern.copy(), 0.02))  # Reduced noise
            self.eeg_data.extend(self.add_noise([random.uniform(-0.4, 0.4) for _ in range(10)], 0.05))  # Reduced noise
    
    def add_noise(self, data, noise_level):
        return [d + random.uniform(-noise_level, noise_level) for d in data]
    
    def update_data(self):
        # Rapid change to vitals for demonstration
        if self.demo_mode:
            current_time = time.time()
            
            # Update target values based on current demo state
            if self.demo_states[self.demo_state] == "Normal":
                self.target_spo2 = 98
                self.target_nibp_systolic = 120
                self.target_nibp_diastolic = 80
                self.target_ibp_systolic = 118
                self.target_ibp_diastolic = 78
                self.target_temperature = 37.0
                self.target_co2_percent = 5.0
                self.target_respiration_rate = 16
            elif self.demo_states[self.demo_state] == "Tachycardia":
                self.target_spo2 = 94
                self.target_nibp_systolic = 135
                self.target_nibp_diastolic = 90
                self.target_ibp_systolic = 133
                self.target_ibp_diastolic = 88
                self.target_temperature = 37.8
                self.target_co2_percent = 5.8
                self.target_respiration_rate = 22
            elif self.demo_states[self.demo_state] == "Bradycardia":
                self.target_spo2 = 92
                self.target_nibp_systolic = 100
                self.target_nibp_diastolic = 65
                self.target_ibp_systolic = 98
                self.target_ibp_diastolic = 63
                self.target_temperature = 36.2
                self.target_co2_percent = 4.2
                self.target_respiration_rate = 12
            elif self.demo_states[self.demo_state] == "Atrial Fibrillation":
                self.target_spo2 = 90
                self.target_nibp_systolic = 145
                self.target_nibp_diastolic = 95
                self.target_ibp_systolic = 143
                self.target_ibp_diastolic = 93
                self.target_temperature = 38.5
                self.target_co2_percent = 6.5
                self.target_respiration_rate = 24
            
            # Move to next state if time is up
            if current_time - self.state_start_time > self.state_duration:
                if self.pattern_name != "Atrial Fibrillation" or (self.pattern_name == "Atrial Fibrillation" and current_time - self.pattern_start_time > self.afib_duration):
                    self.demo_state = (self.demo_state + 1) % len(self.demo_states)
                    self.state_start_time = current_time
                    self.pattern_start_time = current_time
        
        # Gradually transition vital signs toward target values (for stability)
        self.spo2 += (self.target_spo2 - self.spo2) * self.transition_rate
        self.nibp_systolic += (self.target_nibp_systolic - self.nibp_systolic) * self.transition_rate
        self.nibp_diastolic += (self.target_nibp_diastolic - self.nibp_diastolic) * self.transition_rate
        self.ibp_systolic += (self.target_ibp_systolic - self.ibp_systolic) * self.transition_rate
        self.ibp_diastolic += (self.target_ibp_diastolic - self.ibp_diastolic) * self.transition_rate
        self.temperature += (self.target_temperature - self.temperature) * self.transition_rate
        self.co2_percent += (self.target_co2_percent - self.co2_percent) * self.transition_rate
        self.respiration_rate += (self.target_respiration_rate - self.respiration_rate) * self.transition_rate
        
        # Add minimal random fluctuation (much reduced from original)
        self.spo2 += random.uniform(-0.05, 0.05)
        self.nibp_systolic += random.uniform(-0.2, 0.2)
        self.nibp_diastolic += random.uniform(-0.2, 0.2)
        self.ibp_systolic += random.uniform(-0.2, 0.2)
        self.ibp_diastolic += random.uniform(-0.2, 0.2)
        self.temperature += random.uniform(-0.02, 0.02)
        self.co2_percent += random.uniform(-0.02, 0.02)
        self.respiration_rate += random.uniform(-0.1, 0.1)
        
        # Keep all values in reasonable ranges
        self.spo2 = max(min(self.spo2, 100), 85)
        self.nibp_systolic = max(min(self.nibp_systolic, 160), 90)
        self.nibp_diastolic = max(min(self.nibp_diastolic, 110), 50)
        self.ibp_systolic = max(min(self.ibp_systolic, 160), 85)
        self.ibp_diastolic = max(min(self.ibp_diastolic, 110), 45)
        self.temperature = max(min(self.temperature, 39.5), 35.0)
        self.co2_percent = max(min(self.co2_percent, 8.0), 3.0)
        self.respiration_rate = max(min(self.respiration_rate, 30), 8)
        
        # Update ECG pattern based on demo state
        self.pattern_name = self.demo_states[self.demo_state]
        if self.pattern_name == "Normal":
            self.current_pattern = self.ecg_normal
        elif self.pattern_name == "Tachycardia":
            self.current_pattern = self.ecg_tachycardia
        elif self.pattern_name == "Bradycardia":
            self.current_pattern = self.ecg_bradycardia
        elif self.pattern_name == "Atrial Fibrillation":
            self.current_pattern = self.ecg_afib
        
        # Add new data points with reduced noise
        # With:
        repeat = self.pattern_repeat.get(self.pattern_name, 1)
        if repeat == 1:
            new_ecg = self.add_noise(self.current_pattern.copy(), 0.02)
        else:
            # For tachycardia, sample fewer points (makes pattern appear more frequent)
            # For bradycardia, sample more points (makes pattern appear less frequent)
            sample_rate = max(1, int(len(self.current_pattern) * repeat))
            sampled_pattern = []
            for i in range(sample_rate):
                idx = min(int(i * len(self.current_pattern) / sample_rate), len(self.current_pattern) - 1)
                sampled_pattern.append(self.current_pattern[idx])
            new_ecg = self.add_noise(sampled_pattern, 0.02)
        new_eeg = self.add_noise([random.uniform(-0.4, 0.4) for _ in range(10)], 0.05)  # Reduced noise
        
        self.ecg_data.extend(new_ecg)
        self.eeg_data.extend(new_eeg)
        
        # Keep only the last 500 points
        if len(self.ecg_data) > 500:
            self.ecg_data = self.ecg_data[-500:]
        if len(self.eeg_data) > 500:
            self.eeg_data = self.eeg_data[-500:]
        
        return self.pattern_name != "Normal"  # Return True if there's an arrhythmia

