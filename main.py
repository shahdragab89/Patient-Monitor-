class ArrhythmiaDetector:
    def __init__(self):
        # dif arrythmias 
        self.tachycardia_threshold = 100  
        self.bradycardia_threshold = 60   
        # irregularity detection based on RR intervals
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

