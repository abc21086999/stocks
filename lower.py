from PyQt6.QtWidgets import QGridLayout, QWidget, QLabel
from data import *

class stockTable(QWidget):

    def __init__(self):
        super().__init__()

        self.stock_table = QGridLayout()
        self.create_table_header()

        self.setLayout(self.stock_table)


    def create_table_header(self):
        headers = ["股票代號", "股票名稱", "現價", "漲跌幅", "盤中最低", "盤中最高", "成交量"]
        for column, header in enumerate(headers):
            header_label = QLabel()
            header_label.setText(header)
            self.stock_table.addWidget(header_label, 0, column)

    def create_table_content(self, stock_resp: list):
        # stock_resp應該是一個包著一個一個list的list
        # ex. [[2330, 台積電, ....]]
        for row, single_stock_resp in enumerate(stock_resp):
            for column, data in enumerate(single_stock_resp):
                data_label = QLabel()
                data_label.setText(str(data))
                # 第一行是標頭，所以加在第一行以下
                self.stock_table.addWidget(data_label, row + 1, column)

    def clean_table_content(self):
        for row in range(1, self.stock_table.rowCount()):  # 從第 1 行開始迭代 (跳過第 0 行標題列)
            for column in range(self.stock_table.columnCount()):  # 迭代每一列
                item = self.stock_table.itemAtPosition(row, column)  # 獲取指定位置的 item
                if item is not None:  # 確保 item 存在
                    widget = item.widget()  # 獲取 item 包含的 Widget
                    if widget is not None:  # 確保 widget 存在
                        widget.deleteLater()  # 刪除 Widget
                        self.stock_table.removeItem(item)  # 從佈局中移除 item (雖然 deleteLater() 也會移除，但為了更明確，可以再次移除)

    def update_table_content(self):
        self.clean_table_content()
        stock_data = get_stock_data()
        if stock_data:
            self.create_table_content(stock_data)