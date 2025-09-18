import sys
import os
import logging
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QTabWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage, QFont
import cv2
from ultralytics import YOLO
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
            QMainWindow { background-color: #f0f4f8; }
            QTabWidget::pane { border: 2px solid #2980b9; background: #ecf0f1; border-radius: 6px; }
            QTabBar::tab { background: #3498db; color: white; padding: 8px 18px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background: #1abc9c; }
            QLabel { font-size: 14px; font-weight: bold; color: #2c3e50; }
            QLineEdit { border: 2px solid #3498db; border-radius: 4px; padding: 4px; background: white; font-size: 13px; }
            QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 6px 12px; border-radius: 6px; }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1abc9c; }
        """)

        # ---- Tabs ----
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create two tabs
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1, "PLC Control")
        self.tabs.addTab(self.tab2, "Tab 2 (Empty)")

        # ---- Main Tab 2 Layout (Capture Images) ----
        # tab2_layout = QVBoxLayout()

        # # Webcam preview on tab 2
        # self.tab2_video_label = QLabel("Webcam Preview")
        # self.tab2_video_label.setAlignment(Qt.AlignCenter)
        # self.tab2_video_label.setStyleSheet(
        #     "background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 8px;"
        # )
        # self.tab2_video_label.setMinimumSize(640, 480)

        # # Capture button row (centered)
        # button_row = QHBoxLayout()
        # self.capture_btn = QPushButton("📸 Capture Image")
        # self.capture_btn.setFixedWidth(180)
        # self.capture_btn.clicked.connect(self.capture_image)
        # button_row.addStretch()
        # button_row.addWidget(self.capture_btn)
        # button_row.addStretch()

        # # Add widgets to tab2 layout
        # tab2_layout.addWidget(self.tab2_video_label, alignment=Qt.AlignCenter)
        # tab2_layout.addLayout(button_row)
        # tab2_layout.addStretch()

        # self.tab2.setLayout(tab2_layout)

        # # ---- Detection Timer for tab2 ----
        # self.tab2_cap = cv2.VideoCapture(0)  # webcam
        # self.tab2_timer = QTimer()
        # self.tab2_timer.timeout.connect(self.update_tab2_frame)
        # self.tab2_timer.start(30)

        # ---- Main Tab 2 Layout (Capture Images + Crop Section) ----
        # ---- Main Tab 2 Layout (Capture Images + Crop Section) ----
        tab2_main_layout = QHBoxLayout()   # horizontal split (left controls, right video)

        # ---------------- LEFT SIDE (controls) ----------------
        controls_layout = QVBoxLayout()

        # Capture button row
        button_row = QHBoxLayout()
        self.capture_btn = QPushButton("📸 Capture Image")
        self.capture_btn.setFixedWidth(180)
        self.capture_btn.clicked.connect(self.capture_image)
        button_row.addStretch()
        button_row.addWidget(self.capture_btn)
        button_row.addStretch()

        # Crop Section
        crop_title = QLabel("✂️ Crop Captured Images")
        crop_title.setStyleSheet("color: #2980b9; font-weight: bold; margin-top: 15px;")

        # Input fields
        crop_input_row = QHBoxLayout()
        self.crop_width_input = QLineEdit()
        self.crop_width_input.setPlaceholderText("Width")
        self.crop_width_input.setFixedWidth(100)

        self.crop_height_input = QLineEdit()
        self.crop_height_input.setPlaceholderText("Height")
        self.crop_height_input.setFixedWidth(100)

        crop_input_row.addWidget(QLabel("Width:"))
        crop_input_row.addWidget(self.crop_width_input)
        crop_input_row.addWidget(QLabel("Height:"))
        crop_input_row.addWidget(self.crop_height_input)
        crop_input_row.addStretch()

        # Crop button row
        crop_button_row = QHBoxLayout()
        self.crop_btn = QPushButton("Crop All Images")
        self.crop_btn.clicked.connect(self.crop_images)
        crop_button_row.addStretch()
        crop_button_row.addWidget(self.crop_btn)
        crop_button_row.addStretch()

        # Auto crop button row
        auto_crop_button_row = QHBoxLayout()
        self.auto_crop_btn = QPushButton("Auto Crop from Webcam")
        self.auto_crop_btn.clicked.connect(self.auto_crop_btn_clicked)  # real function
        auto_crop_button_row.addStretch()
        auto_crop_button_row.addWidget(self.auto_crop_btn)
        auto_crop_button_row.addStretch()

        # Stop Auto Crop button (future use)
        stop_auto_crop_button_row = QHBoxLayout()
        self.stop_auto_crop_btn = QPushButton("Stop Auto Crop")
        self.stop_auto_crop_btn.clicked.connect(self.stop_auto_crop_btn_clicked)  # stub
        stop_auto_crop_button_row.addStretch()
        stop_auto_crop_button_row.addWidget(self.stop_auto_crop_btn)
        stop_auto_crop_button_row.addStretch()

        # Add everything to controls layout
        controls_layout.addLayout(button_row)
        controls_layout.addWidget(crop_title)
        controls_layout.addLayout(crop_input_row)
        controls_layout.addLayout(crop_button_row)
        controls_layout.addLayout(auto_crop_button_row)
        controls_layout.addLayout(stop_auto_crop_button_row)
        controls_layout.addStretch()

        # Add widgets to controls_layout
        controls_layout.addLayout(button_row)
        controls_layout.addWidget(crop_title)
        controls_layout.addLayout(crop_input_row)
        controls_layout.addLayout(crop_button_row)
        controls_layout.addStretch()

        # ---------------- RIGHT SIDE (video) ----------------
        self.tab2_video_label = QLabel("Webcam Preview")
        self.tab2_video_label.setAlignment(Qt.AlignCenter)
        self.tab2_video_label.setStyleSheet(
            "background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 8px;"
        )
        self.tab2_video_label.setMinimumSize(640, 480)

        # ---------------- COMBINE ----------------
        tab2_main_layout.addLayout(controls_layout, 2)   # left panel (narrower)
        tab2_main_layout.addWidget(self.tab2_video_label, 5)  # right video (wider)

        self.tab2.setLayout(tab2_main_layout)

        # ---- Detection Timer for tab2 ----
        self.tab2_cap = cv2.VideoCapture(0)  # webcam
        self.tab2_timer = QTimer()
        self.tab2_timer.timeout.connect(self.update_tab2_frame)
        self.tab2_timer.start(30)
        # ========================================
        # ---- Main Tab 1 Layout ----
        main_layout = QHBoxLayout()
        # ---- Left panel (controls) ----
        left_layout = QVBoxLayout()

        # Configuration section
        title = QLabel("⚙ PLC Configuration")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #e67e22; margin-bottom: 10px;")

        form_layout = QFormLayout()
        self.pcb_width = QLineEdit()
        self.conveyor_width = QLineEdit()
        self.pcb_length = QLineEdit()

        form_layout.addRow(QLabel("PCB Width (mm):"), self.pcb_width)
        form_layout.addRow(QLabel("PCB Length (mm):"), self.pcb_length)   
        form_layout.addRow(QLabel("Conveyor Width (mm):"), self.conveyor_width)

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

        # Add configuration widgets
        left_layout.addWidget(title)
        left_layout.addLayout(form_layout)
        left_layout.addLayout(button_layout)
        left_layout.addLayout(button_row2)

        # Add testing PLC section
        plc_testing_title = QLabel("🧪 PLC Testing Section (Dummy)")
        plc_testing_title.setFont(QFont("Arial", 14, QFont.Bold))
        plc_testing_title.setStyleSheet("color: #27ae60; margin-top: 20px; margin-bottom: 10px;")
        left_layout.addWidget(plc_testing_title)

        # --- Select configuration file ---
        file_layout = QHBoxLayout()
        self.file_path_display = QLineEdit()
        self.file_path_display.setReadOnly(True)
        btn_browse = QPushButton("Browse Config File")
        btn_browse.clicked.connect(self.browse_config_file)
        file_layout.addWidget(self.file_path_display)
        file_layout.addWidget(btn_browse)
        left_layout.addLayout(file_layout)

        # --- Start and Stop Test Buttons ---
        self.start_test_btn = QPushButton("Start PLC Test (HMH luan van)")
        self.start_test_btn.clicked.connect(self.start_test_plc)

        self.stop_test_btn = QPushButton("Stop PLC Test")
        self.stop_test_btn.clicked.connect(self.stop_test_plc)

        self.interrupt_btn = QPushButton("Interrupt PLC Test")
        self.interrupt_btn.clicked.connect(self.force_test_plc)

        # Put both buttons in a row
        test_btn_layout = QHBoxLayout()
        test_btn_layout.addWidget(self.start_test_btn)
        test_btn_layout.addWidget(self.stop_test_btn)
        test_btn_layout.addWidget(self.interrupt_btn)
        test_btn_layout.addStretch()  

        # Add to main layout
        left_layout.addLayout(test_btn_layout)

        # ---- PLC Control Section ----
        plc_control_title = QLabel("🔌 PLC Control Panel")
        plc_control_title.setFont(QFont("Arial", 14, QFont.Bold))
        plc_control_title.setStyleSheet("color: #2980b9; margin-top: 20px; margin-bottom: 10px;")
        left_layout.addWidget(plc_control_title)

        # PLC IP Address here
        plc_form_layout = QFormLayout()
        self.plc_ip = QLineEdit()
        plc_form_layout.addRow(QLabel("PLC IP Address:"), self.plc_ip)
        left_layout.addLayout(plc_form_layout)

        # PLC buttons
        plc_button_row = QHBoxLayout()
        self.btn_connect = QPushButton("Connect PLC")
        self.btn_connect.clicked.connect(self.connect_plc)
        self.btn_Wint = QPushButton("Write Int")
        self.btn_Wint.clicked.connect(self.write_int)
        self.btn_Rint = QPushButton("Read Int")
        self.btn_Rint.clicked.connect(self.read_int)
        self.btn_stop_connect = QPushButton("Disconnect PLC")
        self.btn_stop_connect.clicked.connect(self.stop_connect_plc)

        plc_button_row.addWidget(self.btn_connect)
        plc_button_row.addWidget(self.btn_Wint)
        plc_button_row.addWidget(self.btn_Rint)
        plc_button_row.addWidget(self.btn_stop_connect)
        left_layout.addLayout(plc_button_row)
        left_layout.addStretch()

        #=============== Add config session step =========#
        plc_step_label = QLabel("🔌 Camera Step Configuration")
        plc_step_label.setFont(QFont("Arial", 14, QFont.Bold))
        plc_step_label.setStyleSheet("color: #2980b9; margin-top: 20px; margin-bottom: 10px;")
        left_layout.addWidget(plc_step_label)

        # PLC step scan input
        plc_step_layout = QFormLayout()
        self.num_step_scan = QLineEdit()
        plc_step_layout.addRow(QLabel("Number of Steps:"), self.num_step_scan)
        left_layout.addLayout(plc_step_layout)

        # PLC up/down/left/right buttons
        plc_button_step = QHBoxLayout()
        self.btn_up = QPushButton("⬆ Up")
        self.btn_up.clicked.connect(self.button_step_up)

        self.btn_down = QPushButton("⬇ Down")
        self.btn_down.clicked.connect(self.button_step_down)

        self.btn_left = QPushButton("⬅ Left")
        self.btn_left.clicked.connect(self.button_step_left)

        self.btn_right = QPushButton("➡ Right")
        self.btn_right.clicked.connect(self.button_step_right)

        self.btn_load_step = QPushButton("Load Step")   # ✅ fixed name
        self.btn_load_step.clicked.connect(self.load_step)  # ✅ fixed connection

        plc_button_step.addWidget(self.btn_up)
        plc_button_step.addWidget(self.btn_down)
        plc_button_step.addWidget(self.btn_left)
        plc_button_step.addWidget(self.btn_right)
        plc_button_step.addWidget(self.btn_load_step)
        plc_button_step.addStretch()
        left_layout.addLayout(plc_button_step)

        # PLC connection status
        status_led_layout = QHBoxLayout()
        status_label_text = QLabel("PLC Status:")
        self.status_led = QLabel()
        self.status_led.setFixedSize(20, 20)
        self.set_status_led(False)
        status_led_layout.addWidget(status_label_text)
        status_led_layout.addWidget(self.status_led)
        status_led_layout.addStretch()
        left_layout.addLayout(status_led_layout)

        # ---- Right panel (video) ----
        self.video_label = QLabel("Video Stream")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #bdc3c7; border: 2px solid #7f8c8d; border-radius: 8px;")
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
        logger.info(f"Saving PLC Configuration: PCB={pcb}, Conveyor={conveyor}, PLC IP={plc_ip}, Length={self.pcb_length.text().strip()}")

        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "plc_config.log")
        with open(file_path, "w") as f:
            f.write(f"PCB Width: {pcb}\nConveyor Width: {conveyor}\nPLC IP Address: {plc_ip}\nPCB Length: {self.pcb_length.text().strip()}\n")

        QMessageBox.information(self, "Saved", f"Configuration saved to {file_path}")

    def start_detection(self):
        logger.info("Starting detection process...")
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
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def stop_detection(self):
        logger.info("Stopping detection process...")
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()
        self.video_label.clear()
        self.video_label.setText("Video Stream")
        QMessageBox.information(self, "Stopped", "Detection process stopped.")

    def start_test_plc(self):
        logger.info("Starting PLC test (dummy action)")
        QMessageBox.information(self, "PLC", "PLC Test Started (dummy action)")
        self.set_status_led(True)
    
    def stop_test_plc(self):
        logger.info("Stopping PLC test (dummy action)")
        QMessageBox.information(self, "PLC", "PLC Test Stopped (dummy action)")
        self.set_status_led(False)

    def force_test_plc(self):
        logger.info("Forcing PLC test interruption (dummy action)")
        QMessageBox.warning(self, "PLC", "PLC Test Interrupted (dummy action)")
        self.set_status_led(False)

    def stop_connect_plc(self):
        logger.info("Disconnecting from PLC (dummy action)")
        QMessageBox.information(self, "PLC", "Disconnected from PLC (dummy action)")
        self.set_status_led(False)

    def reset_configuration(self):
        self.pcb_width.clear()
        self.conveyor_width.clear()
        self.plc_ip.clear()
        QMessageBox.information(self, "Reset", "Configuration fields have been reset.")

    def browse_config_file(self):
        file_name,_ = QFileDialog.getOpenFileName(self, "Select Configuration File", "", "Config Files (*.cfg *.txt);;All Files (*)")
        if file_name:
            self.file_path_display.setText(file_name)
            logger.info(f"Selected configuration file: {file_name}")

    def set_status_led(self, connected: bool):
        if connected:
            self.status_led.setStyleSheet("background-color: green; border-radius: 10px;")
        else:
            self.status_led.setStyleSheet("background-color: red; border-radius: 10px;")

    def button_step_up(self):
        logger.info("Step Up button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Step Up function not implemented")
    
    def button_step_down(self):
        logger.info("Step Down button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Step Down function not implemented")

    def button_step_left(self):
        logger.info("Step Left button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Step Left function not implemented")

    def button_step_right(self):
        logger.info("Step Right button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Step Right function not implemented")
            
    def connect_plc(self):
        ip = self.plc_ip.text().strip()
        if not ip:
            QMessageBox.warning(self, "PLC", "Please enter a PLC IP address")
            return
        logger.info(f"Connecting to PLC at {ip}...")
        QMessageBox.information(self, "PLC", f"Connected to PLC at {ip} (dummy connection)")

    def btn_add(self):
        logger.info("Load Step button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Load Step function not implemented")

    def write_int(self):
        logger.info("Write Int clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Write Int function not implemented")

    def read_int(self):
        logger.info("Read Int clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Read Int function not implemented")

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        self.timer.stop()
        super().closeEvent(event)

    def load_step(self):
        logger.info("Load Step button clicked (not implemented)")
        QMessageBox.information(self, "PLC", "Load Step function not implemented")

    # ===== TAB2 ===== #
    def tab2_btn_up(self):
        logger.info("Tab2 Step Up button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Up function not implemented")
    
    def tab2_btn_down(self):
        logger.info("Tab2 Step Down button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Down function not implemented")

    def tab2_btn_left(self):
        logger.info("Tab2 Step Left button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Left function not implemented")

    def tab2_btn_right(self):
        logger.info("Tab2 Step Right button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Right function not implemented")

    def button_step_up_tab2(self):
        logger.info("Tab2 Step Up button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Up function not implemented")

    def button_step_down_tab2(self):
        logger.info("Tab2 Step Down button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Down function not implemented")

    def button_step_left_tab2(self):
        logger.info("Tab2 Step Left button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Left function not implemented")

    def button_step_right_tab2(self):
        logger.info("Tab2 Step Right button clicked (not implemented)")
        QMessageBox.information(self, "Tab2", "Step Right function not implemented")
    
    # def update_tab2_frame(self):
    #     """Show live video on Tab 2"""
    #     if self.tab2_cap:
    #         ret, frame = self.tab2_cap.read()
    #         if ret:
    #             rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #             h, w, ch = rgb_image.shape
    #             bytes_per_line = ch * w
    #             qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
    #             self.tab2_video_label.setPixmap(QPixmap.fromImage(qt_image))
    #             self.last_frame = frame.copy()  # keep latest frame for saving

    # def capture_image(self):
    #     """Capture current frame and save to /data with incrementing filenames"""
    #     os.makedirs("data", exist_ok=True)

    #     if not hasattr(self, "capture_counter"):
    #         self.capture_counter = 0   # initialize counter

    #     if hasattr(self, "last_frame"):
    #         file_name = os.path.join("data", f"capture_{self.capture_counter}.jpg")
    #         cv2.imwrite(file_name, self.last_frame)
    #         QMessageBox.information(self, "Saved", f"Image saved to {file_name}")
    #         self.capture_counter += 1   # increment for next save
    #     else:
    #         QMessageBox.warning(self, "Error", "No frame captured yet!")

    # def closeEvent(self, event):
    #     if self.cap:
    #         self.cap.release()
    #     if self.tab2_cap:
    #         self.tab2_cap.release()
    #     self.timer.stop()
    #     self.tab2_timer.stop()
    #     super().closeEvent(event)

    # def crop_images(self):
    #     """Crop all images in data/ and save to cropped/"""
    #     try:
    #         width = int(self.crop_width_input.text())
    #         height = int(self.crop_height_input.text())
    #     except ValueError:
    #         QMessageBox.warning(self, "Invalid Input", "Width and Height must be integers.")
    #         return

    #     input_dir = "data"
    #     output_dir = "cropped"
    #     os.makedirs(output_dir, exist_ok=True)

    #     processed = 0
    #     for file in os.listdir(input_dir):
    #         if file.lower().endswith((".jpg", ".png", ".jpeg")):
    #             img_path = os.path.join(input_dir, file)
    #             img = cv2.imread(img_path)
    #             if img is None:
    #                 continue

    #             h, w, _ = img.shape
    #             crop = img[0:min(height, h), 0:min(width, w)]
    #             save_path = os.path.join(output_dir, f"cropped_{file}")
    #             cv2.imwrite(save_path, crop)
    #             processed += 1

    #     QMessageBox.information(self, "Done", f"Cropped {processed} images into {output_dir}/")

    # def auto_crop_btn(self):
    #     """Capture one webcam frame and crop into tiles based on user input size"""
    #     try:
    #         crop_w = int(self.crop_width_input.text())
    #         crop_h = int(self.crop_height_input.text())
    #     except ValueError:
    #         QMessageBox.warning(self, "Invalid Input", "Width and Height must be integers.")
    #         return

    #     output_dir = "auto_cropped"
    #     os.makedirs(output_dir, exist_ok=True)

    #     cap = cv2.VideoCapture(0)
    #     if not cap.isOpened():
    #         QMessageBox.warning(self, "Error", "Cannot access webcam.")
    #         return

    #     ret, frame = cap.read()
    #     cap.release()

    #     if not ret:
    #         QMessageBox.warning(self, "Error", "Failed to capture webcam frame.")
    #         return

    #     h, w, _ = frame.shape

    #     # number of crops along width and height
    #     cols = w // crop_w
    #     rows = h // crop_h
    #     crop_count = 0

    #     for r in range(rows):
    #         for c in range(cols):
    #             x = c * crop_w
    #             y = r * crop_h
    #             crop = frame[y:y+crop_h, x:x+crop_w]
    #             save_path = os.path.join(output_dir, f"crop_{r}_{c}.jpg")
    #             cv2.imwrite(save_path, crop)
    #             crop_count += 1

    #     QMessageBox.information(
    #         self, "Auto Crop",
    #         f"Saved {crop_count} crops of size {crop_w}x{crop_h} into {output_dir}/"
    #     )



    # def _capture_and_crop(self):
    #     """Internal: grab webcam frame and crop"""
    #     ret, frame = self.cap.read()
    #     if not ret:
    #         return

    #     h, w, _ = frame.shape
    #     crop = frame[0:min(self.crop_h, h), 0:min(self.crop_w, w)]

    #     save_path = os.path.join(self.auto_crop_dir, f"frame_{self.frame_index:04d}.jpg")
    #     cv2.imwrite(save_path, crop)
    #     self.frame_index += 1


    # def stop_auto_crop_btn(self):
    #     """Stop auto cropping webcam frames"""
    #     if hasattr(self, "auto_crop_timer") and self.auto_crop_timer.isActive():
    #         self.auto_crop_timer.stop()
    #         QMessageBox.information(self, "Auto Crop", "Auto cropping stopped.")

    #     if hasattr(self, "cap") and self.cap is not None:
    #         self.cap.release()
    #         self.cap = None

    def update_tab2_frame(self):
        """Show live video on Tab 2"""
        if self.tab2_cap:
            ret, frame = self.tab2_cap.read()
            if ret:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.tab2_video_label.setPixmap(QPixmap.fromImage(qt_image))
                self.last_frame = frame.copy()

    def capture_image(self):
        """Capture current frame and save"""
        os.makedirs("data", exist_ok=True)
        if not hasattr(self, "capture_counter"):
            self.capture_counter = 0

        if hasattr(self, "last_frame"):
            file_name = os.path.join("data", f"capture_{self.capture_counter}.jpg")
            cv2.imwrite(file_name, self.last_frame)
            QMessageBox.information(self, "Saved", f"Image saved to {file_name}")
            self.capture_counter += 1
        else:
            QMessageBox.warning(self, "Error", "No frame captured yet!")

    def crop_images(self):
        """Crop all images in data/ into smaller crops of user-defined size"""
        try:
            width = int(self.crop_width_input.text())
            height = int(self.crop_height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Width and Height must be integers.")
            return

        input_dir = "data"
        output_dir = "cropped"
        os.makedirs(output_dir, exist_ok=True)

        processed = 0
        for file in os.listdir(input_dir):
            if file.lower().endswith((".jpg", ".png", ".jpeg")):
                img_path = os.path.join(input_dir, file)
                img = cv2.imread(img_path)
                if img is None:
                    continue

                h, w, _ = img.shape
                for r in range(0, h, height):
                    for c in range(0, w, width):
                        crop = img[r:r+height, c:c+width]
                        save_path = os.path.join(output_dir, f"crop_{processed}_{r}_{c}.jpg")
                        cv2.imwrite(save_path, crop)
                        processed += 1

        QMessageBox.information(self, "Done", f"Cropped {processed} images into {output_dir}/")

    def auto_crop_btn_clicked(self):
        """Auto crop live webcam frame into N tiles"""
        try:
            crop_w = int(self.crop_width_input.text())
            crop_h = int(self.crop_height_input.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Width and Height must be integers.")
            return

        if not hasattr(self, "last_frame"):
            QMessageBox.warning(self, "Error", "No webcam frame available yet.")
            return

        output_dir = "auto_cropped"
        os.makedirs(output_dir, exist_ok=True)

        frame = self.last_frame
        h, w, _ = frame.shape
        cols = w // crop_w
        rows = h // crop_h
        crop_count = 0

        for r in range(rows):
            for c in range(cols):
                x = c * crop_w
                y = r * crop_h
                crop = frame[y:y+crop_h, x:x+crop_w]
                save_path = os.path.join(output_dir, f"crop_{r}_{c}.jpg")
                cv2.imwrite(save_path, crop)
                crop_count += 1

        QMessageBox.information(
            self, "Auto Crop",
            f"Saved {crop_count} crops ({rows}x{cols}) of size {crop_w}x{crop_h} into {output_dir}/"
        )

    def stop_auto_crop_btn_clicked(self):
        """Stop auto crop (if it was running in loop mode)"""
        QMessageBox.information(self, "Auto Crop", "Stop button pressed (no loop active).")

    ######### TAB1 (short detection demo) #########
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
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))

    def closeEvent(self, event):
        if self.cap:
            self.cap.release()
        if self.tab2_cap:
            self.tab2_cap.release()
        self.timer.stop()
        self.tab2_timer.stop()
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    main_window = PLCWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
