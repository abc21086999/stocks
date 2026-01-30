from PySide6.QtGui import QPalette
from PySide6.QtCore import Signal, Slot, QTimer
from PySide6.QtWidgets import QGridLayout, QWidget, QLabel, QApplication
from data import *
from datetime import datetime, time


class StockTable(QWidget):
    data_signal = Signal(list)

    def __init__(self, setting_manager, thread_pool):
        super().__init__()

        self.setting_manager = setting_manager
        self.thread_pool = thread_pool
        self.data_signal.connect(self.handle_stock_data)

        self.stock_table = QGridLayout()
        self.headers = ["股票代號", "股票名稱", "現價", "漲跌幅", "盤中最高", "盤中最低", "開盤價", "成交量"]
        self.create_table_header()
        self.stock_data_widgets = {}
        self.stock_order = []

        self.setLayout(self.stock_table)
        self.update_table_content()

    def create_table_header(self):
        for column, header in enumerate(self.headers):
            header_label = QLabel()
            header_label.setText(header)
            self.stock_table.addWidget(header_label, 0, column)

    def stock_text_color(self, percentage: str) -> str:
        default_palette = QApplication.instance().palette()
        default_text_color = default_palette.color(QPalette.ColorRole.Text)
        default_color_name = default_text_color.name()

        try:
            percentage_value = float(percentage.strip("%"))
        except ValueError:
            return default_color_name

        if percentage_value < 0:
            return "green"
        elif percentage_value > 0:
            return "red"
        else:
            return default_color_name

    def handle_stock_data(self, stock_data):
        """
        槽函數，用於接收 FetchStockData 發射的訊號和股票資料，並更新表格內容。
        """
        if not stock_data:
            return

        stock_id = stock_data[0]
        stock_price = stock_data[3]

        # 如果收到資料的股票已經不在清單中（可能剛被刪除），則忽略
        if stock_id not in self.stock_order:
            return

        if stock_id not in self.stock_data_widgets:
            # 新股票
            row_index = self.stock_order.index(stock_id) + 1
            self.stock_data_widgets[stock_id] = {}
            for column, header in enumerate(self.headers):
                data_label = QLabel()
                data_label.setText(str(stock_data[column]) if column < len(stock_data) else "")
                self.stock_table.addWidget(data_label, row_index, column)
                self.stock_data_widgets[stock_id][header] = data_label
            self.stock_data_widgets[stock_id]["現價"].setStyleSheet(f"color:{self.stock_text_color(stock_price)};")
        else:
            # 更新現有股票
            for column, header in enumerate(self.headers):
                if header != "股票代號" and header != "股票名稱":
                    self.stock_data_widgets[stock_id][header].setText(str(stock_data[column]) if column < len(stock_data) else "")
            self.stock_data_widgets[stock_id]["現價"].setStyleSheet(f"color:{self.stock_text_color(stock_price)};")

    def is_market_open(self) -> bool:
        today_weekday = datetime.today().weekday()
        now_hour_min = datetime.now().time()
        market_open = time(hour=9, minute=0)
        market_close = time(hour=13, minute=40)
        return 0 <= today_weekday <= 4 and market_open <= now_hour_min <= market_close

    def update_table_content(self):
        # 這是啟動時或全量更新時用的
        stored_stock_id = self.setting_manager.load_stock_id()
        # 確保 stock_order 與 settings 同步
        self.stock_order = stored_stock_id
        if stored_stock_id:
            for stock_id in stored_stock_id:
                self.thread_pool.start(FetchStockData(stock_id, self.data_signal))

    def decide_update(self):
        if self.is_market_open():
            # 盤中更新，我們重新抓取所有目前在 stock_order 中的股票
            for stock_id in self.stock_order:
                self.thread_pool.start(FetchStockData(stock_id, self.data_signal))
        else:
            pass

    @Slot(str)
    def add_stock(self, stock_id):
        """
        新增股票：加入順序清單，並啟動該股票的抓取線程。
        """
        if stock_id not in self.stock_order:
            self.stock_order.append(stock_id)
            self.thread_pool.start(FetchStockData(stock_id, self.data_signal))

    @Slot(str)
    def remove_stock(self, stock_id):
        """
        刪除股票：移除 UI 元件，更新內部資料，並將下方列往上移。
        """
        if stock_id not in self.stock_data_widgets:
            return

        # 1. 取得該股票目前的行數 (從 stock_order 判斷)
        try:
            row_index = self.stock_order.index(stock_id) + 1
        except ValueError:
            return  # Should not happen given check above, but safe guard

        # 2. 移除該股票的 UI 元件
        widgets = self.stock_data_widgets[stock_id]
        for widget in widgets.values():
            self.stock_table.removeWidget(widget)
            widget.deleteLater()
        
        # 3. 從資料結構中移除
        del self.stock_data_widgets[stock_id]
        self.stock_order.remove(stock_id)

        # 4. 將下方的列往上移動
        current_rows = self.stock_table.rowCount()
        # 從被刪除的行號開始，遍歷到最後一行
        # 注意：原本在 row_index 的被刪掉了，所以原本在 row_index + 1 的要搬到 row_index
        for row in range(row_index + 1, current_rows):
            for col in range(self.stock_table.columnCount()):
                item = self.stock_table.itemAtPosition(row, col)
                if item:
                    widget = item.widget()
                    if widget:
                        # 從目前位置移除
                        self.stock_table.removeWidget(widget)
                        # 加到上一行
                        self.stock_table.addWidget(widget, row - 1, col)

        # 5. 嘗試讓視窗縮小適應內容 (延後執行以確保佈局已更新)
        QTimer.singleShot(0, lambda: self.window().adjustSize())