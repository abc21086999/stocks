from PySide6.QtWidgets import QLabel, QLineEdit, QPushButton, QWidget, QHBoxLayout
from PySide6.QtCore import Slot, Signal
import re


def create_header():
    header = QLabel()
    header.setText("台股")
    header.setStyleSheet("font-size:25px;")
    return header


class AddStocks(QWidget):
    stock_added = Signal(str)
    stock_removed = Signal(str)

    def __init__(self, setting_manager):
        super().__init__()
        # --- 儲存股票 ---
        self.setting_manager = setting_manager
        self.stock_list = self.setting_manager.load_stock_id()
        self._pattern = re.compile(r'^\d{4,6}(?:[A-Za-z]+(?:\d+)?)?$')

        self.input_line = QLineEdit()
        self.add_button = QPushButton()
        self.add_button.setText("添加股票")
        self.delete_button = QPushButton()
        self.delete_button.setText("刪除股票")

        # --- 填入東西並且點擊的行為 ---
        self.add_button.clicked.connect(self.add_new_stocks)
        self.delete_button.clicked.connect(self.delete_stocks)

        # --- 水平的布局管理器 ---
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.input_line)
        self.hbox_layout.addWidget(self.add_button)
        self.hbox_layout.addWidget(self.delete_button)

        # --- 設置布局管理器 ---
        self.setLayout(self.hbox_layout)

    def is_valid_stock_id(self, stock_id: str) -> bool:
        return bool(self._pattern.match(stock_id))

    @Slot()
    def add_new_stocks(self):
        stock_id = self.input_line.text().strip().upper()
        if self.is_valid_stock_id(stock_id) and stock_id not in self.stock_list:
            self.stock_list.append(stock_id)
            self.setting_manager.save_stock_id(self.stock_list)
            self.input_line.clear()
            self.stock_added.emit(stock_id)
        else:
            return None

    @Slot()
    def delete_stocks(self):
        stock_id = self.input_line.text().upper().strip()
        if stock_id in self.stock_list:
            self.stock_list.remove(stock_id)
            self.setting_manager.save_stock_id(self.stock_list)
            self.input_line.clear()
            self.stock_removed.emit(stock_id)
        else:
            return None