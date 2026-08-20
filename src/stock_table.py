from datetime import datetime, time
from PySide6.QtCore import QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import QAbstractItemView, QHeaderView, QSizePolicy, QTableView, QVBoxLayout, QWidget
from .data import FetchBatchStockData, FetchStockData
from .stock_table_model import StockTableModel


class StockTable(QWidget):
    data_signal = Signal(list)

    def __init__(self, setting_manager, thread_pool):
        super().__init__()

        self.setting_manager = setting_manager
        self.thread_pool = thread_pool
        self._initial_size_adjusted = False
        self._initial_size_adjustment_pending = False
        self._width_expansion_pending = False
        self._height_adjustment_pending = False
        self._initial_pending_stock_ids = set()
        self.headers = ["股票代號", "股票名稱", "現價", "漲跌幅", "盤中最高", "盤中最低", "開盤價", "成交量", "成交金額（億）"]

        self.model = StockTableModel(
            self.headers,
            self.setting_manager.load_enable_price_color(),
            self,
        )
        self.table_view = QTableView(self)
        self.table_view.setModel(self.model)
        self.table_view.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table_view.setAlternatingRowColors(False)
        self.table_view.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table_view.verticalHeader().setVisible(False)
        self.table_view.horizontalHeader().setStretchLastSection(False)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table_view.setStyleSheet("""
            QTableView {
                background-color: #292929;
                color: #f0f0f0;
                gridline-color: #505050;
                border: 1px solid #505050;
            }
            QTableView::item {
                background-color: #1e1e1e;
            }
            QHeaderView::section, QTableCornerButton::section {
                background-color: #333333;
                color: #f0f0f0;
                border: 1px solid #505050;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table_view)

        self.data_signal.connect(self.handle_stock_data)

        # Populate the initial rows before the first fetch, but size the window only
        # after its complete layout has been attached to the top-level widget.
        self.model.set_stock_ids(self.setting_manager.load_stock_id())

        # Let the window paint before starting the initial network requests.
        QTimer.singleShot(0, self.update_table_content)

    def update_table_content(self):
        stored_stock_id = self.setting_manager.load_stock_id()
        self.model.set_stock_ids(stored_stock_id)
        self.model.set_price_color_enabled(self.setting_manager.load_enable_price_color())
        if not self._initial_size_adjusted:
            self._initial_pending_stock_ids = set(stored_stock_id)
            if not self._initial_pending_stock_ids:
                self._fit_initial_window_size()

        if stored_stock_id:
            self.thread_pool.start(FetchBatchStockData(stored_stock_id, self.data_signal))

    def _fit_initial_window_size(self):
        """Make the first window large enough for every table column and row once."""
        if self._initial_size_adjusted or self._initial_size_adjustment_pending:
            return

        window = self.window()
        if not window.isVisible():
            QTimer.singleShot(0, self._fit_initial_window_size)
            return

        self.table_view.resizeColumnsToContents()
        self.table_view.resizeRowsToContents()
        self._initial_size_adjustment_pending = True
        QTimer.singleShot(0, self._finish_initial_window_size_adjustment)

    def _finish_initial_window_size_adjustment(self):
        """Fit the viewport after Qt has applied the table's final column widths."""
        self._initial_size_adjustment_pending = False
        if self._initial_size_adjusted:
            return

        window = self.window()
        if not window.isVisible():
            QTimer.singleShot(0, self._fit_initial_window_size)
            return

        view = self.table_view
        target_viewport_width = sum(
            view.columnWidth(column)
            for column in range(self.model.columnCount())
        )
        target_viewport_height = sum(
            view.rowHeight(row)
            for row in range(self.model.rowCount())
        ) or view.verticalHeader().defaultSectionSize()
        width_delta = target_viewport_width - view.viewport().width()
        height_delta = target_viewport_height - view.viewport().height()

        window.resize(
            max(window.minimumWidth(), window.width() + width_delta),
            max(window.minimumHeight(), window.height() + height_delta),
        )
        QTimer.singleShot(0, self._finalize_initial_window_size)

    def _finalize_initial_window_size(self):
        """Apply one final correction after Qt finishes relaying out the view."""
        if self._initial_size_adjusted:
            return

        window = self.window()
        if not window.isVisible():
            QTimer.singleShot(0, self._finalize_initial_window_size)
            return

        view = self.table_view
        width_delta = sum(
            view.columnWidth(column)
            for column in range(self.model.columnCount())
        ) - view.viewport().width()
        height_delta = (sum(
            view.rowHeight(row)
            for row in range(self.model.rowCount())
        ) or view.verticalHeader().defaultSectionSize()) - view.viewport().height()
        window.resize(
            max(window.minimumWidth(), window.width() + width_delta),
            max(window.minimumHeight(), window.height() + height_delta),
        )
        self._initial_size_adjusted = True
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

    def _expand_window_width_if_needed(self):
        """Expand the window width if the table columns grew wider than the viewport."""
        self._width_expansion_pending = False
        window = self.window()
        if not window.isVisible():
            return

        view = self.table_view
        required_width = sum(
            view.columnWidth(column)
            for column in range(self.model.columnCount())
        )
        width_delta = required_width - view.viewport().width()
        if width_delta > 0:
            window.resize(window.width() + width_delta, window.height())

    def _adjust_window_height(self):
        """Adjust the window height to fit the current row count."""
        self._height_adjustment_pending = False
        window = self.window()
        if not window.isVisible():
            return

        view = self.table_view
        target_viewport_height = sum(
            view.rowHeight(row)
            for row in range(self.model.rowCount())
        ) or view.verticalHeader().defaultSectionSize()
        height_delta = target_viewport_height - view.viewport().height()
        if height_delta != 0:
            window.resize(
                window.width(),
                max(window.minimumHeight(), window.height() + height_delta),
            )

    def _schedule_height_adjustment(self):
        if not self._initial_size_adjusted:
            return
        if not self._height_adjustment_pending:
            self._height_adjustment_pending = True
            QTimer.singleShot(0, self._adjust_window_height)

    @Slot(list)
    def handle_stock_data(self, stock_data):
        self.model.update_stock_data(stock_data)
        if not self._initial_size_adjusted and stock_data:
            self._initial_pending_stock_ids.discard(stock_data[0])
            if not self._initial_pending_stock_ids:
                QTimer.singleShot(0, self._fit_initial_window_size)
        elif self._initial_size_adjusted:
            if not self._width_expansion_pending:
                self._width_expansion_pending = True
                QTimer.singleShot(0, self._expand_window_width_if_needed)

    def is_market_open(self) -> bool:
        today_weekday = datetime.today().weekday()
        now_hour_min = datetime.now().time()
        market_open = time(hour=9, minute=0)
        market_close = time(hour=13, minute=40)
        return 0 <= today_weekday <= 4 and market_open <= now_hour_min <= market_close

    @Slot()
    def reload_table(self):
        self.update_table_content()
        self._schedule_height_adjustment()

    def decide_update(self):
        if not self.is_market_open():
            return

        if self.model.stock_order:
            self.thread_pool.start(FetchBatchStockData(self.model.stock_order, self.data_signal))

    @Slot(str)
    def add_stock(self, stock_id):
        self.model.add_stock(stock_id)
        self._schedule_height_adjustment()
        self.thread_pool.start(FetchStockData(stock_id, self.data_signal))

    @Slot(str)
    def remove_stock(self, stock_id):
        self.model.remove_stock(stock_id)
        self._schedule_height_adjustment()
