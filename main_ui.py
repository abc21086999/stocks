from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6.QtCore import Qt
import sys
from upper import *


class StockUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stocks")
        self.resize(600, 600)
        # self.setStyleSheet("background:#FFFFF0")

        self.upper_frame = QFrame()  # 創建 QFrame 作為 upper_box 的容器
        self.upper_frame.setFrameShape(QFrame.Shape.Box)  # 設定邊框形狀為 Box (矩形)
        self.upper_frame.setFrameShadow(QFrame.Shadow.Plain)  # 設定邊框陰影為 Plain (平面)
        self.upper_frame.setLineWidth(5)  # 設定邊框線寬 (可選)
        self.upper_frame.setStyleSheet("border-color: red;")  # 設定邊框顏色 (可選，使用 stylesheet)

        self.upper_box = QVBoxLayout()


        self.top_label = create_header()
        self.add_stock = create_input_area()
        self.confirm_button = create_add_button()
        self.upper_box.addWidget(self.top_label)
        self.upper_box.addWidget(self.add_stock)
        self.upper_box.addWidget(self.confirm_button)

        self.upper_frame.setLayout(self.upper_box)
        self.upper_box.setAlignment(self.top_label, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)


        # --- Lower Box 及其 Frame ---
        self.lower_frame = QFrame()  # 創建 QFrame 作為 lower_box 的容器
        self.lower_frame.setFrameShape(QFrame.Shape.Box)       # 設定邊框形狀為 Box
        self.lower_frame.setFrameShadow(QFrame.Shadow.Plain)    # 設定邊框陰影為 Plain
        self.lower_frame.setLineWidth(5)                       # 設定邊框線寬 (可選)
        self.lower_frame.setStyleSheet("border-color: blue;")  # 設定邊框顏色 (可選，使用 stylesheet)

        # 你可以在 lower_box 裡面也加入一些元件，方便觀察邊框效果
        self.lower_box = QVBoxLayout()
        self.lower_frame.setLayout(self.lower_box)  # 將 lower_box 設定為 lower_frame 的佈局

        # --- Main Layout ---
        self.main_layout = QVBoxLayout()  # 創建主佈局 (垂直排列)
        self.main_layout.addWidget(self.upper_frame)  # 將 upper_frame 加入主佈局
        self.main_layout.addWidget(self.lower_frame)  # 將 lower_frame 加入主佈局

        self.setLayout(self.main_layout)  # 設定主視窗的佈局為 main_layout

#
# label = QtWidgets.QLabel(Window)
# label.setText("台股")
# label.setStyleSheet('')
#
# add_stock_input = QtWidgets.QLineEdit(Window)
# add_stock_input.move(100, 100)
#
# add_stock_button = QtWidgets.QPushButton(Window)
# add_stock_button.setText("添加股票")
# add_stock_button.setStyleSheet("color:black;")
# add_stock_button.move(200, 100)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockUI()
    window.show()
    app.exec()