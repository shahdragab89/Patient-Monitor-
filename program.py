from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtGui import QColor
import sys
import numpy as np
import pyqtgraph as pg
from patient_data import PatientData
from main import ArrhythmiaDetector


class MonitoringGUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("monitoring.ui", self) 

        self.patient_data = PatientData()
        self.arrhythmia_detector = ArrhythmiaDetector()
        self.alarm_active = True
        self.silenced_arrhythmias = set()

        #vital signs labels
        self.spo2_value = self.findChild(QtWidgets.QLabel, "spo2_value")
        self.nibp_value = self.findChild(QtWidgets.QLabel, "nibp_value")
        self.ibp_value = self.findChild(QtWidgets.QLabel, "ibp_value")
        self.temp_value = self.findChild(QtWidgets.QLabel, "temp_value")
        self.co2_value = self.findChild(QtWidgets.QLabel, "co2_value")
        self.resp_value = self.findChild(QtWidgets.QLabel, "resp_value")
        self.resp_value_2 = self.findChild(QtWidgets.QLabel, "resp_value_2")
        self.pattern_value = self.findChild(QtWidgets.QLabel, "pattern_value")
        self.heart_rate_label_14 = self.findChild(QtWidgets.QLabel, "label_14") 
        self.heart_rate_label = self.findChild(QtWidgets.QLabel, "label")


        #alarm section
        self.alarm_label = self.findChild(QtWidgets.QLabel, "alarm_label")
        self.silence_button = self.findChild(QtWidgets.QPushButton, "silence_button")
        self.silence_button.clicked.connect(self.silence_alarm)
        self.unsilence_button.clicked.connect(self.alarm_reset)
    

        #GRAPHS:
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

        self.ecg_curve = self.ecg_plot.plot([], [], pen='g')
        self.eeg_curve = self.eeg_plot.plot([], [], pen='b')

        self.ecg_plot.setBackground(QColor(26, 26, 26))
        self.eeg_plot.setBackground(QColor(26, 26, 26))


        #cont. updating timers each 0.1s:
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_gui)
        self.timer.start(100)  

    def calculate_heart_rate(self):
        ecg_data = self.patient_data.ecg_data
        if len(ecg_data) < 2:
            return 0
        threshold = max(ecg_data) * 0.7     
        peaks = []
        for i in range(1, len(ecg_data)-1):
            if ecg_data[i] > threshold and ecg_data[i] > ecg_data[i-1] and ecg_data[i] > ecg_data[i+1]:
                peaks.append(i)
                
        if len(peaks) < 2:
            return 0
            
        #calculate average distance between peaks in samples
        avg_peak_distance = np.mean(np.diff(peaks))

        sampling_rate = 35  
        heart_rate = (sampling_rate * 60) / avg_peak_distance
        
        return int(round(heart_rate))

    def update_gui(self):
        self.patient_data.update_data()  
        # SPO2
        if  not self.patient_data.spo2 > 95:
            self.spo2_value.setStyleSheet("color: red;font-size:80pt;")  
        else:
            self.spo2_value.setStyleSheet("color: rgb(15, 255, 255);font-size:80pt;")  

        # NIBP
        if 90 <= self.patient_data.ibp_systolic <= 120 and 60 <= self.patient_data.ibp_diastolic <= 80:
            self.ibp_value.setStyleSheet("color: rgb(110, 110, 110);font-size: 16pt;")  
        else:
            self.ibp_value.setStyleSheet("color: red;font-size: 16pt;")  
        
        # Temperature
        if 36.5 <= self.patient_data.temperature <= 37.5:
            self.temp_value.setStyleSheet("color: white;font-size: 30pt;") 
 
        else:
            self.temp_value.setStyleSheet("color: red;font-size: 30pt;")
  
        # CO2
        if not 4.7 <= self.patient_data.co2_percent <= 6:
            self.co2_value.setStyleSheet("color: red;font-size: 16pt;")  
        else:
            self.co2_value.setStyleSheet("color: rgb(15, 255, 255);font-size: 16pt;")  

        # IBP
        if 90 <= self.patient_data.nibp_systolic <= 140 and 60 <= self.patient_data.nibp_diastolic <= 90:
            self.ibp_value.setStyleSheet("color: rgb(204, 0, 204);font-size: 16pt;")  
        else:
            self.ibp_value.setStyleSheet("color: red;font-size: 16pt;")  

        # RR
        if not 12 <= self.patient_data.respiration_rate <= 20:
            self.resp_value.setStyleSheet("color: red;font-size: 16pt;") 
            self.resp_value_2.setStyleSheet("color: red;font-size: 80pt;")  
        else:
            self.resp_value.setStyleSheet("color: rgb(255, 255, 13);font-size: 16pt;")
            self.resp_value_2.setStyleSheet("color: rgb(255, 255, 13);font-size: 80pt;")   
        
        # HR Calculaation:
        heart_rate = self.calculate_heart_rate()
        self.heart_rate_label_14.setText(f"{heart_rate} BPM")
        self.heart_rate_label.setText(f"{heart_rate}") 
        if 60 <= heart_rate <= 100:
            color = "green"
        else:
            color = "red"
        
        self.heart_rate_label_14.setStyleSheet(f"color: {color}; font-size: 16pt;")
        self.heart_rate_label.setStyleSheet(f"color: {color}; font-size: 80pt;")
        
        self.spo2_value.setText(f"{round(self.patient_data.spo2, 1)}%")
        self.nibp_value.setText(f"{int(round(self.patient_data.nibp_systolic))}/{int(round(self.patient_data.nibp_diastolic))} mmHg")
        self.ibp_value.setText(f"{int(round(self.patient_data.ibp_systolic))}/{int(round(self.patient_data.ibp_diastolic))} mmHg")
        self.temp_value.setText(f"{round(self.patient_data.temperature, 1)}°C")
        self.co2_value.setText(f"{round(self.patient_data.co2_percent, 1)}%")
        self.resp_value.setText(f"{int(round(self.patient_data.respiration_rate))} BPM")
        self.resp_value_2.setText(f"{int(round(self.patient_data.respiration_rate))}")
        if self.patient_data.pattern_name == "Normal":
            self.pattern_value.setText(self.patient_data.pattern_name)
            self.pattern_value.setStyleSheet("color: green;font-size: 30px;")
            self.alarm_label.setStyleSheet("color: green;font-size: 30px;")  
            if self.alarm_active ==False:
                self.alarm_label.setText("Alarm paused")
            else :
                self.alarm_label.setText("Normal")
  
        else:
            self.pattern_value.setText(self.patient_data.pattern_name)
            self.pattern_value.setStyleSheet("color: red;font-size: 30px;") 
            self.alarm_label.setStyleSheet("color: red;font-size: 30px;")
            if self.alarm_active ==False:
                self.alarm_label.setText("Alarm paused")
                self.alarm_label.setStyleSheet("color: green;font-size: 30px;")
            else :
                self.alarm_label.setText("ALARM")
                self.alarm_label.setStyleSheet("color: red;font-size: 30px;")


        #Updating graphs
        self.ecg_curve.setData(range(len(self.patient_data.ecg_data)), self.patient_data.ecg_data)
        self.eeg_curve.setData(range(len(self.patient_data.eeg_data)), self.patient_data.eeg_data)

    def silence_alarm(self):
        self.alarm_active = False
        self.alarm_label.setText("Alarm  paused")
        self.silence_button.setEnabled(False)

    def alarm_reset(self):
        self.alarm_active = True
        self.alarm_label.setText("Normal ")
        self.silence_button.setEnabled(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MonitoringGUI()
    window.show()
    sys.exit(app.exec_())
