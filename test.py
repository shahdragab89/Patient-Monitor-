import tkinter as tk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import time
import threading
from patient_data import PatientData
from  main import ArrhythmiaDetector


class MonitoringGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Patient Monitoring System")
        self.root.geometry("1000x700")
        self.root.configure(bg="black")
        
        self.alarm_active = False
        self.alarm_message = ""
        self.silenced_arrhythmias = set()  # Track silenced arrhythmia types

        self.patient_data = PatientData()
        self.arrhythmia_detector = ArrhythmiaDetector()
        
        self.alarm_active = False
        self.alarm_message = ""
        
        # Create main frames
        self.create_frames()
        
        # Create plots
        self.create_plots()
        
        # Create vital signs display
        self.create_vital_signs()
        
        # Create alarm section
        self.create_alarm_section()
        
        # Create demo controls
        self.create_demo_controls()
        
        # Start the update loop
        self.update_thread = threading.Thread(target=self.update_data_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        # Update GUI periodically
        self.update_gui()
    
    def create_frames(self):
        # Main frames
        self.top_frame = tk.Frame(self.root, bg="black")
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(self.root, bg="black")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        # Left and right sections of top frame
        self.left_frame = tk.Frame(self.top_frame, bg="black")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.top_frame, bg="black")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_plots(self):
        # ECG Plot
        self.ecg_fig = plt.Figure(figsize=(10, 3), facecolor='black')
        self.ecg_ax = self.ecg_fig.add_subplot(111)
        self.ecg_ax.set_title("ECG", color="white")
        self.ecg_ax.set_ylim(-0.5, 2)
        self.ecg_ax.set_facecolor("black")
        self.ecg_ax.tick_params(axis='x', colors='white')
        self.ecg_ax.tick_params(axis='y', colors='white')
        self.ecg_ax.spines['bottom'].set_color('white')
        self.ecg_ax.spines['top'].set_color('white') 
        self.ecg_ax.spines['left'].set_color('white')
        self.ecg_ax.spines['right'].set_color('white')
        self.ecg_line, = self.ecg_ax.plot([], [], 'g-')  # White line
        self.ecg_canvas = FigureCanvasTkAgg(self.ecg_fig, master=self.left_frame)
        self.ecg_canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # EEG Plot
        self.eeg_fig = plt.Figure(figsize=(10, 3), facecolor='black')
        self.eeg_ax = self.eeg_fig.add_subplot(111)
        self.eeg_ax.set_title("EEG", color="white")
        self.eeg_ax.set_ylim(-1, 1)
        self.eeg_ax.set_facecolor("black")
        self.eeg_ax.tick_params(axis='x', colors='white')
        self.eeg_ax.tick_params(axis='y', colors='white')
        self.eeg_ax.spines['bottom'].set_color('white')
        self.eeg_ax.spines['top'].set_color('white') 
        self.eeg_ax.spines['left'].set_color('white')
        self.eeg_ax.spines['right'].set_color('white')
        self.eeg_line, = self.eeg_ax.plot([], [], 'b-')  # White line
        self.eeg_canvas = FigureCanvasTkAgg(self.eeg_fig, master=self.left_frame)
        self.eeg_canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def create_vital_signs(self):
        # Frame for vital signs
        self.vitals_frame = tk.Frame(self.right_frame, bg="black", bd=2, relief=tk.RAISED)
        self.vitals_frame.pack(padx=10, pady=10, fill=tk.BOTH)
        
        # Title
        tk.Label(self.vitals_frame, text="Vital Signs", font=("Arial", 14, "bold"), bg="black", fg="white").pack(pady=5)
        
        # SPO2
        self.spo2_frame = tk.Frame(self.vitals_frame, bg="black")
        self.spo2_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.spo2_frame, text="SPO2:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.spo2_value = tk.Label(self.spo2_frame, text="98%", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.spo2_value.pack(side=tk.LEFT)
        
        # NIBP
        self.nibp_frame = tk.Frame(self.vitals_frame, bg="black")
        self.nibp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.nibp_frame, text="NIBP:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.nibp_value = tk.Label(self.nibp_frame, text="120/80 mmHg", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.nibp_value.pack(side=tk.LEFT)
        
        # IBP
        self.ibp_frame = tk.Frame(self.vitals_frame, bg="black")
        self.ibp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.ibp_frame, text="IBP:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.ibp_value = tk.Label(self.ibp_frame, text="118/78 mmHg", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.ibp_value.pack(side=tk.LEFT)
        
        # Temperature
        self.temp_frame = tk.Frame(self.vitals_frame, bg="black")
        self.temp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.temp_frame, text="Temperature:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.temp_value = tk.Label(self.temp_frame, text="37.0°C", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.temp_value.pack(side=tk.LEFT)
        
        # CO2
        self.co2_frame = tk.Frame(self.vitals_frame, bg="black")
        self.co2_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.co2_frame, text="CO2:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.co2_value = tk.Label(self.co2_frame, text="5.0%", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.co2_value.pack(side=tk.LEFT)
        
        # Respiration Rate
        self.resp_frame = tk.Frame(self.vitals_frame, bg="black")
        self.resp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.resp_frame, text="Resp Rate:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.resp_value = tk.Label(self.resp_frame, text="16 BPM", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.resp_value.pack(side=tk.LEFT)
        
        # ECG Pattern
        self.pattern_frame = tk.Frame(self.vitals_frame, bg="black")
        self.pattern_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.pattern_frame, text="ECG Pattern:", font=("Arial", 12), width=15, anchor="w", bg="black", fg="white").pack(side=tk.LEFT)
        self.pattern_value = tk.Label(self.pattern_frame, text="Normal", font=("Arial", 12, "bold"), fg="green", bg="black")
        self.pattern_value.pack(side=tk.LEFT)
    
    def create_alarm_section(self):
        # Frame for alarms
        self.alarm_frame = tk.Frame(self.right_frame, bg="black", bd=2, relief=tk.RAISED)
        self.alarm_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(self.alarm_frame, text="Arrhythmia Alarms", font=("Arial", 14, "bold"), bg="black", fg="white").pack(pady=5)
        
        # Alarm message
        self.alarm_label = tk.Label(self.alarm_frame, text="No alarms", font=("Arial", 12), bg="black", fg="white", wraplength=200)
        self.alarm_label.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Silence alarm button
        self.silence_button = tk.Button(self.alarm_frame, text="Silence Alarm", font=("Arial", 12), command=self.silence_alarm, bg="black", fg="white")
        self.silence_button.pack(pady=10)
        self.silence_button.config(state=tk.DISABLED)
    
    def create_demo_controls(self):
        # Frame for demo controls - now takes full width with padding
        self.demo_frame = tk.Frame(self.bottom_frame, bg="black", bd=2, relief=tk.RAISED)
        self.demo_frame.pack(fill=tk.X, padx=10, pady=10, ipady=10)
        
        # Demo mode controls
        self.demo_label = tk.Label(self.demo_frame, text="Demo Mode Controls:", 
                                 font=("Arial", 12, "bold"), bg="black", fg="white")
        self.demo_label.pack(side=tk.LEFT, padx=20)
        
        # Container frame for buttons to better control spacing
        self.button_frame = tk.Frame(self.demo_frame, bg="black")
        self.button_frame.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # Buttons with white background and black text
        button_style = {
            'font': ("Arial", 12, "bold"),
            'width': 12,
            'height': 1,
            'bg': "white",
            'fg': "black",
            'activebackground': "#dddddd",
            'activeforeground': "black",
            'bd': 2,
            'relief': tk.RAISED
        }
        
        self.normal_btn = tk.Button(self.button_frame, text="Normal", 
                                   command=lambda: self.force_pattern("Normal"), 
                                   **button_style)
        self.normal_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.tachy_btn = tk.Button(self.button_frame, text="Tachycardia", 
                                  command=lambda: self.force_pattern("Tachycardia"), 
                                  **button_style)
        self.tachy_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.brady_btn = tk.Button(self.button_frame, text="Bradycardia", 
                                  command=lambda: self.force_pattern("Bradycardia"), 
                                  **button_style)
        self.brady_btn.pack(side=tk.LEFT, padx=10, expand=True)
        
        self.afib_btn = tk.Button(self.button_frame, text="A-Fib", 
                                 command=lambda: self.force_pattern("Atrial Fibrillation"), 
                                 **button_style)
        self.afib_btn.pack(side=tk.LEFT, padx=10, expand=True)
    
    def force_pattern(self, pattern):
        """Force a specific ECG pattern for demo purposes"""
        for i, state in enumerate(self.patient_data.demo_states):
            if state == pattern:
                self.patient_data.demo_state = i
                self.patient_data.state_start_time = time.time()
                self.patient_data.pattern_start_time = time.time()
                break
    
    def silence_alarm(self):
        """Silence the current alarm"""
        # Get the current arrhythmia type from the alarm message
        current_arrhythmia = None
        if self.alarm_active and self.alarm_message:
            # Extract arrhythmia type from the message
            # Message format is typically "ALERT: {arrhythmia_type} detected!\n{alarm_msg}"
            parts = self.alarm_message.split(":")
            if len(parts) > 1:
                # Extract the arrhythmia type more robustly by looking for word before "detected"
                message_text = parts[1].strip()
                if "detected" in message_text:
                    arrhythmia_part = message_text.split("detected")[0].strip()
                    current_arrhythmia = arrhythmia_part
        
        # Add current arrhythmia to silenced list if it exists
        if current_arrhythmia:
            self.silenced_arrhythmias.add(current_arrhythmia)
        
        # Reset alarm UI
        self.alarm_active = False
        self.alarm_frame.config(bg="black")
        self.alarm_label.config(bg="black")
        
        # Update the alarm label to indicate which arrhythmia was silenced
        if current_arrhythmia:
            self.alarm_label.config(text=f"{current_arrhythmia} alarm silenced")
        else:
            self.alarm_label.config(text="Alarm Silenced")
        
        self.silence_button.config(state=tk.DISABLED)
        
        # Add or update unsilence button
        if not hasattr(self, 'unsilence_button'):
            self.unsilence_button = tk.Button(self.alarm_frame, text="Unsilence All Alarms", 
                                            font=("Arial", 12), command=self.unsilence_alarms,
                                            bg="black", fg="white")
            self.unsilence_button.pack(pady=5)
        
        # Only enable the unsilence button if we have silenced alarms
        if self.silenced_arrhythmias:
            self.unsilence_button.config(state=tk.NORMAL)
        else:
            self.unsilence_button.config(state=tk.DISABLED)

    def unsilence_alarms(self):
        """Reset all silenced alarms"""
        self.silenced_arrhythmias.clear()
        self.alarm_label.config(text="No alarms")
        if hasattr(self, 'unsilence_button'):
            self.unsilence_button.config(state=tk.DISABLED)

    def update_gui(self):
        """Update the GUI with current data"""
        # Update ECG plot
        self.ecg_line.set_data(range(len(self.patient_data.ecg_data)), self.patient_data.ecg_data)
        self.ecg_ax.set_xlim(0, len(self.patient_data.ecg_data))
        
        # Update EEG plot
        self.eeg_line.set_data(range(len(self.patient_data.eeg_data)), self.patient_data.eeg_data)
        self.eeg_ax.set_xlim(0, len(self.patient_data.eeg_data))
        
        # Update canvases
        self.ecg_canvas.draw()
        self.eeg_canvas.draw()
        
        # Update vital signs - round values for more stable display
        self.spo2_value.config(text=f"{round(self.patient_data.spo2, 1):.1f}%")
        self.nibp_value.config(text=f"{int(round(self.patient_data.nibp_systolic))}/{int(round(self.patient_data.nibp_diastolic))} mmHg")
        self.ibp_value.config(text=f"{int(round(self.patient_data.ibp_systolic))}/{int(round(self.patient_data.ibp_diastolic))} mmHg")
        self.temp_value.config(text=f"{round(self.patient_data.temperature, 1):.1f}°C")
        self.co2_value.config(text=f"{round(self.patient_data.co2_percent, 1):.1f}%")
        self.resp_value.config(text=f"{int(round(self.patient_data.respiration_rate))} BPM")
        self.pattern_value.config(text=self.patient_data.pattern_name)
        
        # Change vital sign colors based on values
        # SPO2 (Normal: 95-100%)
        if 95 <= self.patient_data.spo2 <= 100:
            self.spo2_value.config(fg="green")
        elif 90 <= self.patient_data.spo2 < 95:
            self.spo2_value.config(fg="yellow")
        else:
            self.spo2_value.config(fg="red")
        
        # NIBP (Normal: 90-140/60-90)
        if (90 <= self.patient_data.nibp_systolic <= 140 and 
            60 <= self.patient_data.nibp_diastolic <= 90):
            self.nibp_value.config(fg="green")
        else:
            self.nibp_value.config(fg="red")
        
        # Temperature (Normal: 36.5-37.5°C)
        if 36.5 <= self.patient_data.temperature <= 37.5:
            self.temp_value.config(fg="green")
        elif 35.0 <= self.patient_data.temperature < 36.5 or 37.5 < self.patient_data.temperature <= 38.5:
            self.temp_value.config(fg="yellow")
        else:
            self.temp_value.config(fg="red")
        
        # CO2 (Normal: 4.0-6.0%)
        if 4.0 <= self.patient_data.co2_percent <= 6.0:
            self.co2_value.config(fg="green")
        else:
            self.co2_value.config(fg="red")
        
        # Respiration Rate (Normal: 12-20 BPM)
        if 12 <= self.patient_data.respiration_rate <= 20:
            self.resp_value.config(fg="green")
        elif 8 <= self.patient_data.respiration_rate < 12 or 20 < self.patient_data.respiration_rate <= 25:
            self.resp_value.config(fg="yellow")
        else:
            self.resp_value.config(fg="red")
        
        # Update pattern label color based on pattern
        if self.patient_data.pattern_name == "Normal":
            self.pattern_value.config(fg="green")
        else:
            self.pattern_value.config(fg="red")
        
        # Check for arrhythmia and update alarm - Only do this once
        arrhythmia_type, alarm_msg = self.arrhythmia_detector.detect_arrhythmia(
            self.patient_data.ecg_data, self.patient_data.pattern_name)
        
        # Alarm handling logic
        if arrhythmia_type:
            # If arrhythmia is detected
            if arrhythmia_type not in self.silenced_arrhythmias:
                # Only trigger alarm if this specific arrhythmia is not silenced
                if not self.alarm_active or self.alarm_message.split(":")[1].strip().split(" ")[0] != arrhythmia_type:
                    # Only trigger a new alarm if we don't have an active alarm OR
                    # if the current alarm is for a different arrhythmia type
                    self.trigger_alarm(f"ALERT: {arrhythmia_type} detected!\n{alarm_msg}")
            # If alarm is active but the arrhythmia type has been silenced, silence it
            elif self.alarm_active and arrhythmia_type in self.silenced_arrhythmias:
                # Update alarm UI to show it's silenced but don't clear silenced status
                self.alarm_active = False
                self.alarm_frame.config(bg="black")
                self.alarm_label.config(bg="black")
                self.alarm_label.config(text=f"{arrhythmia_type} alarm silenced")
                self.silence_button.config(state=tk.DISABLED)
        else:
            # If no arrhythmia is detected
            if self.alarm_active:
                # Auto-silence any active alarm when pattern returns to normal
                self.alarm_active = False
                self.alarm_frame.config(bg="black")
                self.alarm_label.config(bg="black")
                self.alarm_label.config(text="No alarms")
                self.silence_button.config(state=tk.DISABLED)
            
            # When returning to normal rhythm, clear all silenced arrhythmias
            if self.silenced_arrhythmias:
                self.silenced_arrhythmias.clear()
                if hasattr(self, 'unsilence_button'):
                    self.unsilence_button.config(state=tk.DISABLED)
        
        # Schedule the next update
        self.root.after(100, self.update_gui)
    
    def trigger_alarm(self, message):
        self.alarm_active = True
        self.alarm_message = message
        self.alarm_frame.config(bg="red")
        self.alarm_label.config(bg="red", fg="white")
        self.alarm_label.config(text=message)
        self.silence_button.config(state=tk.NORMAL)
    
    def update_data_loop(self):
        """Background thread for data updates"""
        while True:
            arrhythmia_detected = self.patient_data.update_data()
            time.sleep(0.1)  # Update every 100ms

if __name__ == "__main__":
    root = tk.Tk()
    app = MonitoringGUI(root)
    root.mainloop()