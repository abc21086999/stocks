from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt, QTimer, QSettings
import sys
from upper import *
from lower import *
from data import *
from app_settings import *


class StockUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stocks")
        self.resize(600, 600)
        # self.setStyleSheet("background:#FFFFF0")

        # --- 記憶功能 ---
        self.memory = SettingsManager()
        self.stock_ids =  self.memory.load_stock_id()

        # --- Upper Box ---
        self.upper_box = QVBoxLayout()

        # --- 添加股票的輸入視窗和點擊按鈕 ---
        self.top_label = create_header()
        self.add_stock = create_input_area()
        self.confirm_button = create_add_button()
        self.upper_box.addWidget(self.top_label)
        self.upper_box.addWidget(self.add_stock)
        self.upper_box.addWidget(self.confirm_button)
        # 設置Header的對齊位置
        self.upper_box.setAlignment(self.top_label, Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)


        # --- Lower Box ---
        self.lower_box = QVBoxLayout()

        # --- 顯示股票的table ---
        self.stock_table = stockTable()
        self.stock_table.create_table_content(get_stock_data())
        self.lower_box.addWidget(self.stock_table)

        # --- 新增股票 ---

        # --- 定時更新股票資訊內容 ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.stock_table.update_table_content)
        self.timer.start(1000)

        # --- Main Layout ---
        self.main_layout = QVBoxLayout()  # 創建主佈局 (垂直排列)
        self.main_layout.addLayout(self.upper_box)  # 將 upper_frame 加入主佈局
        self.main_layout.addLayout(self.lower_box)  # 將 lower_frame 加入主佈局

        self.setLayout(self.main_layout)  # 設定主視窗的佈局為 main_layout


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockUI()
    window.show()
    app.exec()