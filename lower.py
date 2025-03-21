import time

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QGridLayout, QWidget, QLabel
from data import *


class StockTable(QWidget):
    data_signal = pyqtSignal(list)

    def __init__(self, setting_manager, thread_pool, delete_stock_signal):
        super().__init__()

        self.setting_manager = setting_manager
        self.thread_pool = thread_pool
        self.data_signal.connect(self.handle_stock_data)
        self.stock_delete_signal = delete_stock_signal
        self.stock_delete_signal.connect(self.on_stock_list_changed)

        self.stock_table = QGridLayout()
        self.headers = ["股票代號", "股票名稱", "現價", "漲跌幅", "盤中最高", "盤中最低", "開盤價", "成交量"]
        self.create_table_header()
        self.stock_data_widgets = {}
        self.stock_order = []

        self.setLayout(self.stock_table)


    def create_table_header(self):
        for column, header in enumerate(self.headers):
            header_label = QLabel()
            header_label.setText(header)
            self.stock_table.addWidget(header_label, 0, column)

    def stock_text_color(self, percentage: str) -> str:
        if percentage.strip("%").startswith("-"):
            return "green"
        elif float(percentage.strip("%")) > 0:
            return "red"
        else:
            return "default"

    def clean_table_content(self):
        self.stock_data_widgets = {}
        self.stock_order = []
        for row in range(1, self.stock_table.rowCount()):  # 從第 1 行開始迭代 (跳過第 0 行標題列)
            for column in range(self.stock_table.columnCount()):  # 迭代每一列
                item = self.stock_table.itemAtPosition(row, column)  # 獲取指定位置的 item
                if item is not None:  # 確保 item 存在
                    widget = item.widget()  # 獲取 item 包含的 Widget
                    if widget is not None:  # 確保 widget 存在
                        widget.deleteLater()  # 刪除 Widget
                        self.stock_table.removeItem(item)  # 從佈局中移除 item (雖然 deleteLater() 也會移除，但為了更明確，可以再次移除)


    def handle_stock_data(self, stock_data):
        """
        槽函數，用於接收 FetchStockData 發射的訊號和股票資料，並更新表格內容。
        stock_data: 從 FetchStockData 傳來的股票資料 list (例如: ['2330', '台積電', 600, ...])
        """
        if not stock_data: # 檢查資料是否為空
            print("接收到的股票資料為空")
            return

        stock_id = stock_data[0] # 假設股票代號在 list 的第一個位置
        stock_price = stock_data[3]

        if stock_id not in self.stock_data_widgets:
            # 如果 stock_id 不在字典中，表示是新的股票，需要新增一行
            row_index = self.stock_order.index(stock_id) + 1 # 計算新的列索引 (從第 1 列開始，第 0 列是表頭)
            self.stock_data_widgets[stock_id] = {} # 初始化 stock_id 對應的 widget 字典
            for column, header in enumerate(self.headers):
                data_label = QLabel() # 建立 QLabel
                data_label.setText(str(stock_data[column]) if column < len(stock_data) else "") # 設定文字，避免 indexError
                self.stock_table.addWidget(data_label, row_index, column) # 將 QLabel 加入表格
                self.stock_data_widgets[stock_id][header] = data_label # 將 QLabel 存入字典，方便後續更新
            self.stock_data_widgets[stock_id]["現價"].setStyleSheet(f"color:{self.stock_text_color(stock_price)};")
        else:
            # 如果 stock_id 已在字典中，表示是已存在的股票，只需要更新資料
            for column, header in enumerate(self.headers):
                if header != "股票代號" and header != "股票名稱": # 股票代號和名稱不更新
                    self.stock_data_widgets[stock_id][header].setText(str(stock_data[column]) if column < len(stock_data) else "") # 更新 QLabel 的文字
            self.stock_data_widgets[stock_id]["現價"].setStyleSheet(f"color:{self.stock_text_color(stock_price)};")


    def update_table_content(self):
        stored_stock_id = self.setting_manager.load_stock_id()
        self.stock_order = stored_stock_id
        if stored_stock_id:
            for stock_id in stored_stock_id:
                self.thread_pool.start(FetchStockData(stock_id, self.data_signal))

    @pyqtSlot()
    def on_stock_list_changed(self):
        """
        槽函數，當股票列表變更時被調用，精細化更新表格內容。
        """
        self.clean_table_content()
        self.update_table_content()
