from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QColor
import sys
import numpy as np
import pyqtgraph as pg
import time
from patient_data import PatientData
from main import ArrhythmiaDetector


class MonitoringGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("monitoring.ui", self)  # Load the UI

        self.patient_data = PatientData()
        self.arrhythmia_detector = ArrhythmiaDetector()
        self.alarm_active = False
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

        # **Graph Placeholders**
        self.ecg_graph = self.findChild(QtWidgets.QWidget, "ecg_graph")
        self.eeg_graph = self.findChild(QtWidgets.QWidget, "eeg_graph")

        # **Replace QWidget with pyqtgraph**
        if self.ecg_graph:
            self.ecg_layout = QtWidgets.QVBoxLayout(self.ecg_graph)
            self.ecg_plot = pg.PlotWidget()
            self.ecg_layout.addWidget(self.ecg_plot)

        if self.eeg_graph:
            self.eeg_layout = QtWidgets.QVBoxLayout(self.eeg_graph)
            self.eeg_plot = pg.PlotWidget()
            self.eeg_layout.addWidget(self.eeg_plot)

        # **Create Graphs**
        self.ecg_curve = self.ecg_plot.plot([], [], pen='g')
        self.eeg_curve = self.eeg_plot.plot([], [], pen='b')

        self.ecg_plot.setBackground(QColor(26, 26, 26))
        self.eeg_plot.setBackground(QColor(26, 26, 26))


        # **Timers for Continuous Updates**
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)  # Update every 100ms

    def update_gui(self):
        """Update the GUI with new data"""
        self.patient_data.update_data()  # Update patient data randomly

        # **Update Labels**
        self.spo2_value.setText(f"{round(self.patient_data.spo2, 1)}%")
        self.nibp_value.setText(f"{int(round(self.patient_data.nibp_systolic))}/{int(round(self.patient_data.nibp_diastolic))} mmHg")
        self.ibp_value.setText(f"{int(round(self.patient_data.ibp_systolic))}/{int(round(self.patient_data.ibp_diastolic))} mmHg")
        self.temp_value.setText(f"{round(self.patient_data.temperature, 1)}°C")
        self.co2_value.setText(f"{round(self.patient_data.co2_percent, 1)}%")
        self.resp_value.setText(f"{int(round(self.patient_data.respiration_rate))} BPM")
        self.resp_value_2.setText(f"{int(round(self.patient_data.respiration_rate))}")
        self.pattern_value.setText(self.patient_data.pattern_name)

        # **Update Graphs**
        self.ecg_curve.setData(range(len(self.patient_data.ecg_data)), self.patient_data.ecg_data)
        self.eeg_curve.setData(range(len(self.patient_data.eeg_data)), self.patient_data.eeg_data)

    def silence_alarm(self):
        """Silence the alarm"""
        self.alarm_active = False
        self.alarm_label.setText("Alarm Silenced")
        self.silence_button.setEnabled(False)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonitoringGUI()
    window.show()
    sys.exit(app.exec_())
