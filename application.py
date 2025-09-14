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
# Load YOLO model
model = YOLO("weights/best.pt")

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PLCWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PLC Qt GUI")
        self.setGeometry(200, 200, 1000, 600)

        # ---- Global Stylesheet ----
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f4f8;
            }
            QTabWidget::pane {
                border: 2px solid #2980b9;
                background: #ecf0f1;
                border-radius: 6px;
            }
            QTabBar::tab {
                background: #3498db;
                color: white;
                padding: 8px 18px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #1abc9c;
            }
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
            }
            QLineEdit {
                border: 2px solid #3498db;
                border-radius: 4px;
                padding: 4px;
                background: white;
                font-size: 13px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1abc9c;
            }
        """)

        # ---- Tabs ----
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create two tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "PLC Control")
        self.tabs.addTab(self.tab2, "Tab 2 (Empty)")

        # ---- Main Tab 1 Layout ----
        main_layout = QHBoxLayout()

        # ---- Left panel (controls) ----
        left_layout = QVBoxLayout()

        title = QLabel("⚙ PLC Configuration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #e67e22; margin-bottom: 10px;")

        form_layout = QFormLayout()
        self.pcb_width = QLineEdit()
        self.conveyor_width = QLineEdit()
        self.plc_ip = QLineEdit()

        form_layout.addRow(QLabel("PCB Width (mm):"), self.pcb_width)
        form_layout.addRow(QLabel("Conveyor Width (mm):"), self.conveyor_width)
        form_layout.addRow(QLabel("PLC IP Address:"), self.plc_ip)

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
        left_layout.addStretch()

        # Add another layout below configuration for PLC operations
        plc_control_title = QLabel("🔌 PLC Control Panel")
        plc_control_title.setFont(QFont("Arial", 14, QFont.Bold))
        plc_control_title.setStyleSheet("color: #2980b9; margin-top: 20px; margin-bottom: 10px;")

        # New button row
        plc_button_row = QHBoxLayout()
        self.btn_connect = QPushButton("Connect PLC")
        self.btn_Wint = QPushButton("Write Int")
        self.btn_Rint = QPushButton("Read Int")

        plc_button_row.addWidget(self.btn_connect)
        plc_button_row.addWidget(self.btn_Wint)
        plc_button_row.addWidget(self.btn_Rint)

        # Add the new section to the left panel
        left_layout.addWidget(plc_control_title)
        left_layout.addLayout(plc_button_row)

        # Keep stretch at the very bottom (pushes everything up)
        left_layout.addStretch()

        # ---- Right panel (video) ----
        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet(
            "background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 8px;"
        )
        self.video_label.setMinimumSize(600, 400)

        main_layout.addLayout(left_layout, 2)
        main_layout.addWidget(self.video_label, 5)

        self.tab1.setLayout(main_layout)

        # ---- Detection Timer ----
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

    ######### Functionality #########
    def save_plc_configuration(self):
        pcb = self.pcb_width.text().strip()
        conveyor = self.conveyor_width.text().strip()
        plc_ip = self.plc_ip.text().strip()

        logger.info(f"Saving PLC Configuration: PCB Width={pcb}, Conveyor Width={conveyor}, PLC IP={plc_ip}")

        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "plc_config.log")

        with open(file_path, "w") as f:
            f.write(f"PCB Width: {pcb}\n")
            f.write(f"Conveyor Width: {conveyor}\n")
            f.write(f"PLC IP Address: {plc_ip}\n")

        QMessageBox.information(self, "Saved", f"Configuration saved to {file_path}")

    def start_detection(self):
        logger.info("Starting detection process...")
        QMessageBox.information(self, "Detection", "Detection process started.")

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Error", "Could not open webcam")
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
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(qt_image)

                self.video_label.setPixmap(pixmap)

    def stop_detection(self):
        logger.info("Stopping detection process...")
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.video_label.clear()
        self.video_label.setText("Video Stream")
        QMessageBox.information(self, "Stopped", "Detection process stopped.")

    def reset_configuration(self):
        self.pcb_width.clear()
        self.conveyor_width.clear()
        self.plc_ip.clear()
        QMessageBox.information(self, "Reset", "Configuration fields have been reset.")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        super().closeEvent(event)

    # def connect_plc(self):
    #     ip = self.txt_Ip.toPlainText()
    #     port = self.txt_port.toPlainText()
    #     self.plc = SiemensS7Net(SiemensPLCS.S1200,str(ip))
    #     self.btn_connect.setStyleSheet("background-color: lightgreen; color: black;")
    
    # def Write_Int(self):
    #     address = self.txt_Add_Wint.toPlainText()
    #     value = self.txt_Value_Wint.toPlainText()
    #     vl1  = self.str_to_uint16(value)
    #     vl2  = Array[UInt16]([vl1])
    #     self.plc.Write(str(address),vl2)
    #     print(vl1)
    
    # def Read_Int(self):
    #     address = self.txt_Add_Rint.toPlainText()
    #     value = self.plc.ReadInt16(str(address)).Content
    #     self.txt_Value_Rint.setText(str(value))

    # def Write_bit(self):
    #     address = self.txt_Add_Wbit.toPlainText()
    #     value = self.cb_Value_Wbit.currentText()
    #     vl1 = self.str_to_boolean_dotnet(value)
    #     print(address)
    #     print(vl1)
    #     self.plc.Write(address, vl1)

    # def Read_bit(self):
    #     address = self.txt_Add_Rbit.toPlainText()
    #     value = self.plc.ReadBool(str(address)).Content
    #     self.txt_Value_Rbit.setText(str(value))

    # def Write_Float(self):
    #     address = self.txt_Add_WFloat.toPlainText()
    #     value = self.txt_Value_WFloat.toPlainText()
    #     self.plc.Write(str(address), float(value))

    # def Read_Float(self):
    #     address = self.txt_Add_RFloat.toPlainText()
    #     value = self.plc.ReadFloat(str(address)).Content
    #     self.txt_Value_RFloat.setText(str(round(value, 3)))

    # @staticmethod
    # def str_to_boolean_dotnet(text: str) -> Boolean:
    #     text = text.strip().lower()
    #     return Boolean(text == "true")

    # @staticmethod
    # def str_to_uint16(input_str: str) -> UInt16:
    #     try:
    #         return UInt16.Parse(input_str)
    #     except Exception as e:
    #         raise ValueError(f"Không thể chuyển '{input_str}' sang UInt16: {e}")

def main():
    app = QApplication(sys.argv)
    main_window = PLCWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
