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
        self.root.configure(bg="#f0f0f0")
        
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
        self.top_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        
        self.bottom_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Left and right sections of top frame
        self.left_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = tk.Frame(self.top_frame, bg="#f0f0f0")
        self.right_frame.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_plots(self):
        # ECG Plot
        self.ecg_fig, self.ecg_ax = plt.subplots(figsize=(10, 3))
        self.ecg_ax.set_title("ECG")
        self.ecg_ax.set_ylim(-0.5, 2)
        self.ecg_ax.set_facecolor("#e6f2ff")
        self.ecg_line, = self.ecg_ax.plot([], [], 'g-')
        self.ecg_canvas = FigureCanvasTkAgg(self.ecg_fig, master=self.left_frame)
        self.ecg_canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        
        # EEG Plot
        self.eeg_fig, self.eeg_ax = plt.subplots(figsize=(10, 3))
        self.eeg_ax.set_title("EEG")
        self.eeg_ax.set_ylim(-1, 1)
        self.eeg_ax.set_facecolor("#e6f2ff")
        self.eeg_line, = self.eeg_ax.plot([], [], 'b-')
        self.eeg_canvas = FigureCanvasTkAgg(self.eeg_fig, master=self.left_frame)
        self.eeg_canvas.get_tk_widget().pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
    
    def create_vital_signs(self):
        # Frame for vital signs
        self.vitals_frame = tk.Frame(self.right_frame, bg="#e6e6e6", bd=2, relief=tk.RAISED)
        self.vitals_frame.pack(padx=10, pady=10, fill=tk.BOTH)
        
        # Title
        tk.Label(self.vitals_frame, text="Vital Signs", font=("Arial", 14, "bold"), bg="#e6e6e6").pack(pady=5)
        
        # SPO2
        self.spo2_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.spo2_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.spo2_frame, text="SPO2:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.spo2_value = tk.Label(self.spo2_frame, text="98%", font=("Arial", 12, "bold"), fg="blue", bg="#e6e6e6")
        self.spo2_value.pack(side=tk.LEFT)
        
        # NIBP
        self.nibp_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.nibp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.nibp_frame, text="NIBP:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.nibp_value = tk.Label(self.nibp_frame, text="120/80 mmHg", font=("Arial", 12, "bold"), fg="green", bg="#e6e6e6")
        self.nibp_value.pack(side=tk.LEFT)
        
        # IBP
        self.ibp_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.ibp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.ibp_frame, text="IBP:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.ibp_value = tk.Label(self.ibp_frame, text="118/78 mmHg", font=("Arial", 12, "bold"), fg="purple", bg="#e6e6e6")
        self.ibp_value.pack(side=tk.LEFT)
        
        # Temperature
        self.temp_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.temp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.temp_frame, text="Temperature:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.temp_value = tk.Label(self.temp_frame, text="37.0°C", font=("Arial", 12, "bold"), fg="red", bg="#e6e6e6")
        self.temp_value.pack(side=tk.LEFT)
        
        # CO2
        self.co2_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.co2_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.co2_frame, text="CO2:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.co2_value = tk.Label(self.co2_frame, text="5.0%", font=("Arial", 12, "bold"), fg="brown", bg="#e6e6e6")
        self.co2_value.pack(side=tk.LEFT)
        
        # Respiration Rate
        self.resp_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.resp_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.resp_frame, text="Resp Rate:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.resp_value = tk.Label(self.resp_frame, text="16 BPM", font=("Arial", 12, "bold"), fg="orange", bg="#e6e6e6")
        self.resp_value.pack(side=tk.LEFT)
        
        # ECG Pattern
        self.pattern_frame = tk.Frame(self.vitals_frame, bg="#e6e6e6")
        self.pattern_frame.pack(fill=tk.X, padx=10, pady=5)
        tk.Label(self.pattern_frame, text="ECG Pattern:", font=("Arial", 12), width=15, anchor="w", bg="#e6e6e6").pack(side=tk.LEFT)
        self.pattern_value = tk.Label(self.pattern_frame, text="Normal", font=("Arial", 12, "bold"), fg="black", bg="#e6e6e6")
        self.pattern_value.pack(side=tk.LEFT)
    
    def create_alarm_section(self):
        # Frame for alarms
        self.alarm_frame = tk.Frame(self.right_frame, bg="#ffcccc", bd=2, relief=tk.RAISED)
        self.alarm_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Title
        tk.Label(self.alarm_frame, text="Arrhythmia Alarms", font=("Arial", 14, "bold"), bg="#ffcccc").pack(pady=5)
        
        # Alarm message
        self.alarm_label = tk.Label(self.alarm_frame, text="No alarms", font=("Arial", 12), bg="#ffcccc", wraplength=200)
        self.alarm_label.pack(pady=10, fill=tk.BOTH, expand=True)
        
        # Silence alarm button
        self.silence_button = tk.Button(self.alarm_frame, text="Silence Alarm", font=("Arial", 12), command=self.silence_alarm)
        self.silence_button.pack(pady=10)
        self.silence_button.config(state=tk.DISABLED)
    
    def create_demo_controls(self):
        # Frame for demo controls
        self.demo_frame = tk.Frame(self.bottom_frame, bg="#e6e6e6", bd=2, relief=tk.RAISED)
        self.demo_frame.pack(padx=10, pady=10, fill=tk.X)
        
        # Demo mode controls
        self.demo_label = tk.Label(self.demo_frame, text="Demo Mode: ON", font=("Arial", 12, "bold"), bg="#e6e6e6")
        self.demo_label.pack(side=tk.LEFT, padx=10)
        
        # Buttons to force specific arrhythmias immediately
        self.normal_btn = tk.Button(self.demo_frame, text="Normal", command=lambda: self.force_pattern("Normal"))
        self.normal_btn.pack(side=tk.LEFT, padx=5)
        
        self.tachy_btn = tk.Button(self.demo_frame, text="Tachycardia", command=lambda: self.force_pattern("Tachycardia"))
        self.tachy_btn.pack(side=tk.LEFT, padx=5)
        
        self.brady_btn = tk.Button(self.demo_frame, text="Bradycardia", command=lambda: self.force_pattern("Bradycardia"))
        self.brady_btn.pack(side=tk.LEFT, padx=5)
        
        self.afib_btn = tk.Button(self.demo_frame, text="A-Fib", command=lambda: self.force_pattern("Atrial Fibrillation"))
        self.afib_btn.pack(side=tk.LEFT, padx=5)
    
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
        self.alarm_frame.config(bg="#ffcccc")
        self.alarm_label.config(bg="#ffcccc")
        
        # Update the alarm label to indicate which arrhythmia was silenced
        if current_arrhythmia:
            self.alarm_label.config(text=f"{current_arrhythmia} alarm silenced")
        else:
            self.alarm_label.config(text="Alarm Silenced")
        
        self.silence_button.config(state=tk.DISABLED)
        
        # Add or update unsilence button
        if not hasattr(self, 'unsilence_button'):
            self.unsilence_button = tk.Button(self.alarm_frame, text="Unsilence All Alarms", 
                                            font=("Arial", 12), command=self.unsilence_alarms)
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
        # SPO2
        if self.patient_data.spo2 > 95:
            self.spo2_value.config(fg="blue")
        else:
            self.spo2_value.config(fg="red")
        
        # NIBP
        if 90 <= self.patient_data.nibp_systolic <= 140 and 60 <= self.patient_data.nibp_diastolic <= 90:
            self.nibp_value.config(fg="green")
        else:
            self.nibp_value.config(fg="red")
        
        # Temperature
        if 36.5 <= self.patient_data.temperature <= 37.5:
            self.temp_value.config(fg="green")
        else:
            self.temp_value.config(fg="red")
        
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
                self.alarm_frame.config(bg="#ffcccc")
                self.alarm_label.config(bg="#ffcccc")
                self.alarm_label.config(text=f"{arrhythmia_type} alarm silenced")
                self.silence_button.config(state=tk.DISABLED)
        else:
            # If no arrhythmia is detected
            if self.alarm_active:
                # Auto-silence any active alarm when pattern returns to normal
                self.alarm_active = False
                self.alarm_frame.config(bg="#ffcccc")
                self.alarm_label.config(bg="#ffcccc")
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
        self.alarm_frame.config(bg="#ff6666")
        self.alarm_label.config(bg="#ff6666")
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