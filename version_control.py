import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, \
    QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
from ultralytics import YOLO
import logging

# pythonnet
from pythonnet import load
load()
import clr
dll_path = Path(r"D:\Work\Course\C#\ALL PLC\Project")
sys.path.append(str(dll_path))
clr.AddReference("HslCommunication")
from HslCommunication.Profinet.Siemens import SiemensS7Net, SiemensPLCS
from System import Array, UInt16, Boolean

# Load YOLO model
model = YOLO("weights/best.pt")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class PLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PLC + YOLO GUI")
        self.setGeometry(200, 200, 1200, 700)

        # ---- Tabs ----
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "PLC Control")
        self.tabs.addTab(self.tab2, "Tab 2 (Empty)")

        # ---- Main layout for Tab 1 ----
        main_layout = QHBoxLayout()

        # ---- Left panel ----
        left_layout = QVBoxLayout()

        # PLC configuration section
        title = QLabel("⚙ PLC Configuration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #e67e22; margin-bottom: 10px;")
        form_layout = QFormLayout()
        self.pcb_width = QLineEdit()
        self.conveyor_width = QLineEdit()
        self.plc_ip = QLineEdit()
        form_layout.addRow("PCB Width (mm):", self.pcb_width)
        form_layout.addRow("Conveyor Width (mm):", self.conveyor_width)
        form_layout.addRow("PLC IP Address:", self.plc_ip)

        # Buttons row 1
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 Save Config")
        self.save_button.clicked.connect(self.save_plc_configuration)
        self.detect_trigger = QPushButton("▶ Start Detection")
        self.detect_trigger.clicked.connect(self.start_detection)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.detect_trigger)

        # Buttons row 2
        button_row2 = QHBoxLayout()
        self.stop_button = QPushButton("⏹ Stop Detection")
        self.stop_button.clicked.connect(self.stop_detection)
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.clicked.connect(self.reset_configuration)
        button_row2.addWidget(self.stop_button)
        button_row2.addWidget(self.reset_button)

        left_layout.addWidget(title)
        left_layout.addLayout(form_layout)
        left_layout.addLayout(button_layout)
        left_layout.addLayout(button_row2)

        # ---- PLC Control Panel ----
        plc_control_title = QLabel("🔌 PLC Control Panel")
        plc_control_title.setFont(QFont("Arial", 14, QFont.Bold))
        plc_control_title.setStyleSheet("color: #2980b9; margin-top: 20px; margin-bottom: 10px;")

        plc_form = QFormLayout()
        self.txt_ip = QLineEdit()
        self.txt_port = QLineEdit()
        self.txt_Add_Wint = QLineEdit()
        self.txt_Value_Wint = QLineEdit()
        self.txt_Add_Rint = QLineEdit()
        self.txt_Value_Rint = QLineEdit()
        plc_form.addRow("PLC IP:", self.txt_ip)
        plc_form.addRow("PLC Port:", self.txt_port)
        plc_form.addRow("Write Int Address:", self.txt_Add_Wint)
        plc_form.addRow("Write Int Value:", self.txt_Value_Wint)
        plc_form.addRow("Read Int Address:", self.txt_Add_Rint)
        plc_form.addRow("Read Int Value:", self.txt_Value_Rint)

        plc_button_row = QHBoxLayout()
        self.btn_connect = QPushButton("Connect PLC")
        self.btn_Wint = QPushButton("Write Int")
        self.btn_Rint = QPushButton("Read Int")
        plc_button_row.addWidget(self.btn_connect)
        plc_button_row.addWidget(self.btn_Wint)
        plc_button_row.addWidget(self.btn_Rint)

        self.btn_connect.clicked.connect(self.connect_plc)
        self.btn_Wint.clicked.connect(self.Write_Int)
        self.btn_Rint.clicked.connect(self.Read_Int)

        left_layout.addWidget(plc_control_title)
        left_layout.addLayout(plc_form)
        left_layout.addLayout(plc_button_row)
        left_layout.addStretch()

        # ---- Right panel (Video) ----
        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setMinimumSize(600, 400)
        self.video_label.setStyleSheet(
            "background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 8px;"
        )

        main_layout.addLayout(left_layout, 3)
        main_layout.addWidget(self.video_label, 5)
        self.tab1.setLayout(main_layout)

        # ---- Timer ----
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # PLC
        self.plc = None

    # ------------------ PLC Functions ------------------
    def connect_plc(self):
        try:
            ip = self.txt_ip.text().strip()
            self.plc = SiemensS7Net(SiemensPLCS.S1200, ip)
            self.btn_connect.setStyleSheet("background-color: lightgreen; color: black;")
            QMessageBox.information(self, "PLC", f"Connected to {ip}")
        except Exception as e:
            QMessageBox.critical(self, "PLC Error", str(e))

    def Write_Int(self):
        address = self.txt_Add_Wint.text().strip()
        value = self.txt_Value_Wint.text().strip()
        vl1 = self.str_to_uint16(value)
        vl2 = Array[UInt16]([vl1])
        self.plc.Write(str(address), vl2)

    def Read_Int(self):
        address = self.txt_Add_Rint.text().strip()
        value = self.plc.ReadInt16(str(address)).Content
        self.txt_Value_Rint.setText(str(value))

    @staticmethod
    def str_to_uint16(input_str: str) -> UInt16:
        try:
            return UInt16.Parse(input_str)
        except Exception as e:
            raise ValueError(f"Cannot convert '{input_str}' to UInt16: {e}")

    # ------------------ YOLO Functions ------------------
    def save_plc_configuration(self):
        pcb = self.pcb_width.text().strip()
        conveyor = self.conveyor_width.text().strip()
        plc_ip = self.plc_ip.text().strip()
        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "plc_config.log")
        with open(file_path, "w") as f:
            f.write(f"PCB Width: {pcb}\n")
            f.write(f"Conveyor Width: {conveyor}\n")
            f.write(f"PLC IP Address: {plc_ip}\n")
        QMessageBox.information(self, "Saved", f"Configuration saved to {file_path}")

    def start_detection(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Cannot open webcam")
            return
        self.timer.start(30)

    def update_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                results = model(frame, verbose=False)
                annotated_frame = results[0].plot()
                rgb_image = cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                qt_img = QImage(rgb_image.data, w, h, ch * w, QImage.Format_RGB888)
                self.video_label.setPixmap(QPixmap.fromImage(qt_img))

    def stop_detection(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.video_label.clear()
        self.video_label.setText("Video Stream")

    def reset_configuration(self):
        self.pcb_width.clear()
        self.conveyor_width.clear()
        self.plc_ip.clear()

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PLCWindow()
    window.show()
    sys.exit(app.exec_())
