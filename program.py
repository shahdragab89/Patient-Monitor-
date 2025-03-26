from PyQt5 import QtWidgets, uic
import sys
import time
import threading
from patient_data import PatientData
from main import ArrhythmiaDetector
import pyqtgraph as pg


class MonitoringGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("monitoring.ui", self)  # Load the UI

        self.patient_data = PatientData()
        self.arrhythmia_detector = ArrhythmiaDetector()
        self.alarm_active = False
        self.alarm_message = ""
        self.silenced_arrhythmias = set()

        # **Vital Signs Labels**
        self.spo2_value = self.findChild(QtWidgets.QLabel, "spo2_value")
        self.nibp_value = self.findChild(QtWidgets.QLabel, "nibp_value")
        self.ibp_value = self.findChild(QtWidgets.QLabel, "ibp_value")
        self.temp_value = self.findChild(QtWidgets.QLabel, "temp_value")
        self.co2_value = self.findChild(QtWidgets.QLabel, "co2_value")
        self.resp_value = self.findChild(QtWidgets.QLabel, "resp_value")
        self.pattern_value = self.findChild(QtWidgets.QLabel, "pattern_value")

        # **Alarm Section**
        self.alarm_label = self.findChild(QtWidgets.QLabel, "alarm_label")
        self.silence_button = self.findChild(QtWidgets.QPushButton, "silence_button")
        self.silence_button.clicked.connect(self.silence_alarm)

        # **Graphs (Replace Placeholder QWidget with PlotWidget)**
        self.ecg_graph = self.findChild(QtWidgets.QWidget, "ecg_graph")
        self.eeg_graph = self.findChild(QtWidgets.QWidget, "eeg_graph")

        if self.ecg_graph:
            self.ecg_layout = QtWidgets.QVBoxLayout(self.ecg_graph)
            self.ecg_plot = pg.PlotWidget()
            self.ecg_layout.addWidget(self.ecg_plot)

        if self.eeg_graph:
            self.eeg_layout = QtWidgets.QVBoxLayout(self.eeg_graph)
            self.eeg_plot = pg.PlotWidget()
            self.eeg_layout.addWidget(self.eeg_plot)

        # **Demo Control Buttons**
        self.normal_btn = self.findChild(QtWidgets.QPushButton, "normal_btn")
        self.tachy_btn = self.findChild(QtWidgets.QPushButton, "tachy_btn")
        self.brady_btn = self.findChild(QtWidgets.QPushButton, "brady_btn")
        self.afib_btn = self.findChild(QtWidgets.QPushButton, "afib_btn")

        self.normal_btn.clicked.connect(lambda: self.force_pattern("Normal"))
        self.tachy_btn.clicked.connect(lambda: self.force_pattern("Tachycardia"))
        self.brady_btn.clicked.connect(lambda: self.force_pattern("Bradycardia"))
        self.afib_btn.clicked.connect(lambda: self.force_pattern("Atrial Fibrillation"))

        # Start background update
        self.update_thread = threading.Thread(target=self.update_data_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

        self.update_gui()

    def update_gui(self):
        """Update the GUI with current data"""
        self.spo2_value.setText(f"{round(self.patient_data.spo2, 1)}%")
        self.nibp_value.setText(f"{int(round(self.patient_data.nibp_systolic))}/{int(round(self.patient_data.nibp_diastolic))} mmHg")
        self.ibp_value.setText(f"{int(round(self.patient_data.ibp_systolic))}/{int(round(self.patient_data.ibp_diastolic))} mmHg")
        self.temp_value.setText(f"{round(self.patient_data.temperature, 1)}°C")
        self.co2_value.setText(f"{round(self.patient_data.co2_percent, 1)}%")
        self.resp_value.setText(f"{int(round(self.patient_data.respiration_rate))} BPM")
        self.pattern_value.setText(self.patient_data.pattern_name)

        # **Update ECG and EEG Graphs**
        self.ecg_plot.plot(self.patient_data.ecg_data, clear=True, pen='g')
        self.eeg_plot.plot(self.patient_data.eeg_data, clear=True, pen='b')

        # **Check for Arrhythmia**
        arrhythmia_type, alarm_msg = self.arrhythmia_detector.detect_arrhythmia(
            self.patient_data.ecg_data, self.patient_data.pattern_name
        )

        if arrhythmia_type:
            if arrhythmia_type not in self.silenced_arrhythmias:
                self.trigger_alarm(f"ALERT: {arrhythmia_type} detected!\n{alarm_msg}")

        self.timer = self.startTimer(100)  # Update every 100ms

    def force_pattern(self, pattern):
        """Force a specific ECG pattern for demo"""
        for i, state in enumerate(self.patient_data.demo_states):
            if state == pattern:
                self.patient_data.demo_state = i
                self.patient_data.state_start_time = time.time()
                self.patient_data.pattern_start_time = time.time()
                break

    def silence_alarm(self):
        """Silence the current alarm"""
        self.alarm_active = False
        self.alarm_label.setText("Alarm Silenced")
        self.silence_button.setEnabled(False)

    def trigger_alarm(self, message):
        """Trigger an alarm"""
        self.alarm_active = True
        self.alarm_label.setText(message)
        self.silence_button.setEnabled(True)

    def update_data_loop(self):
        """Background thread for data updates"""
        while True:
            self.patient_data.update_data()
            time.sleep(0.1)  # Update every 100ms


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonitoringGUI()
    window.show()
    sys.exit(app.exec_())
