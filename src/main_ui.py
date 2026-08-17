from PySide6.QtWidgets import QApplication, QVBoxLayout
from PySide6.QtCore import QTimer, QThreadPool
import sys
from .upper import *
from .stock_table import StockTable
from .app_settings import *


class StockUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Stocks")

        # --- 記憶功能 ---
        self.setting_manager = SettingsManager()

        # --- Upper Box ---
        self.upper_box = QVBoxLayout()

        # --- 添加股票的輸入視窗和點擊按鈕 ---
        self.add_stocks = AddStocks(self.setting_manager)
        self.upper_box.addWidget(self.add_stocks)


        # --- Lower Box ---
        self.lower_box = QVBoxLayout()

        # --- 顯示股票的table ---
        self.threadpool = QThreadPool()
        self.stock_table = StockTable(self.setting_manager, self.threadpool)
        self.add_stocks.stock_added.connect(self.stock_table.add_stock)
        self.add_stocks.stock_removed.connect(self.stock_table.remove_stock)
        self.add_stocks.settings_changed.connect(self.stock_table.reload_table)
        self.lower_box.addWidget(self.stock_table)

        # --- 在開盤時更新股票資訊內容 ---
        self.timer = QTimer()
        self.timer.timeout.connect(self.stock_table.decide_update)
        self.timer.start(30000)

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
