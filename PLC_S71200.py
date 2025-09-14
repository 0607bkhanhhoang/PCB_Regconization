from  pythonnet import load
load()
import clr
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import  QThread, pyqtSignal
from  PyQt6.uic import loadUi
import sys
from  pathlib import  Path
dll_path = Path(r"D:\Work\Course\C#\ALL PLC\Project")
sys.path.append(str(dll_path))
clr.AddReference("HslCommunication")
from  HslCommunication.Profinet.Siemens import SiemensS7Net, SiemensPLCS
from System import Array, UInt16, UInt32, Boolean, Byte, Int16
import ast

class Mainwindown(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi('S7_1200.ui',self)
        # khởi tạo plc
        self.btn_connect.clicked.connect(self.connect_plc)
        self.btn_Wint.clicked.connect(self.Write_Int)
        self.btn_Rint.clicked.connect(self.Read_Int)
        self.btn_Wbit.clicked.connect(self.Write_bit)
        self.btn_Rbit.clicked.connect(self.Read_bit)
        self.btn_WFloat.clicked.connect(self.Write_Float)
        self.btn_RFloat.clicked.connect(self.Read_Float)

    def connect_plc(self):
        ip = self.txt_Ip.toPlainText()
        port = self.txt_port.toPlainText()
        self.plc = SiemensS7Net(SiemensPLCS.S1200,str(ip))
        self.btn_connect.setStyleSheet("background-color: lightgreen; color: black;")

    def Write_Int(self):
        address = self.txt_Add_Wint.toPlainText()
        value = self.txt_Value_Wint.toPlainText()
        vl1  = self.str_to_uint16(value)
        vl2  = Array[UInt16]([vl1])
        self.plc.Write(str(address),vl2)
        print(vl1)

    def Read_Int(self):
        address = self.txt_Add_Rint.toPlainText()
        value = self.plc.ReadInt16(str(address)).Content
        self.txt_Value_Rint.setText(str(value))

    def Write_bit(self):
        address = self.txt_Add_Wbit.toPlainText()
        value = self.cb_Value_Wbit.currentText()
        vl1 = self.str_to_boolean_dotnet(value)
        print(address)
        print(vl1)
        self.plc.Write(address, vl1)

    def Read_bit(self):
        address = self.txt_Add_Rbit.toPlainText()
        value = self.plc.ReadBool(str(address)).Content
        self.txt_Value_Rbit.setText(str(value))

    def Write_Float(self):
        address = self.txt_Add_WFloat.toPlainText()
        value = self.txt_Value_WFloat.toPlainText()
        self.plc.Write(str(address), float(value))

    def Read_Float(self):
        address = self.txt_Add_RFloat.toPlainText()
        value = self.plc.ReadFloat(str(address)).Content
        self.txt_Value_RFloat.setText(str(round(value, 3)))

    @staticmethod
    def str_to_boolean_dotnet(text: str) -> Boolean:
        text = text.strip().lower()
        return Boolean(text == "true")

    @staticmethod
    def str_to_uint16(input_str: str) -> UInt16:
        try:
            return UInt16.Parse(input_str)
        except Exception as e:
            raise ValueError(f"Không thể chuyển '{input_str}' sang UInt16: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = Mainwindown()
    win.show()
    sys.exit(app.exec())
