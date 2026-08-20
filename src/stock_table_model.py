from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor


class StockTableModel(QAbstractTableModel):
    """Owns stock table data and tells Qt exactly which cells need repainting."""

    PRICE_COLUMN = 2
    CHANGE_COLUMN = 3
    PERCENTAGE_COLUMN = 4

    def __init__(self, headers, price_color_enabled=True, parent=None):
        super().__init__(parent)
        self.headers = headers
        self.price_color_enabled = price_color_enabled
        self.stock_order = []
        self.rows_by_id = {}

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.stock_order)

    def columnCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.headers)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        stock_id = self.stock_order[index.row()]
        stock_data = self.rows_by_id.get(stock_id, [stock_id])

        if role == Qt.ItemDataRole.DisplayRole:
            if index.column() < len(stock_data):
                return str(stock_data[index.column()])
            return ""

        if role == Qt.ItemDataRole.ForegroundRole and index.column() == self.PRICE_COLUMN:
            return self._price_color(stock_data)

        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole and orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

    def set_stock_ids(self, stock_ids):
        """Reset the displayed rows while retaining any data for unchanged stocks."""
        unique_ids = list(dict.fromkeys(stock_ids))
        old_rows = self.rows_by_id

        self.beginResetModel()
        self.stock_order = unique_ids
        self.rows_by_id = {
            stock_id: old_rows.get(stock_id, [stock_id])
            for stock_id in unique_ids
        }
        self.endResetModel()

    def add_stock(self, stock_id):
        if stock_id in self.rows_by_id:
            return

        row = len(self.stock_order)
        self.beginInsertRows(QModelIndex(), row, row)
        self.stock_order.append(stock_id)
        self.rows_by_id[stock_id] = [stock_id]
        self.endInsertRows()

    def remove_stock(self, stock_id):
        if stock_id not in self.rows_by_id:
            return

        row = self.stock_order.index(stock_id)
        self.beginRemoveRows(QModelIndex(), row, row)
        self.stock_order.pop(row)
        del self.rows_by_id[stock_id]
        self.endRemoveRows()

    def update_stock_data(self, stock_data):
        if not stock_data:
            return

        stock_id = stock_data[0]
        if stock_id not in self.rows_by_id:
            # A result from a removed stock or a previous reload.
            return

        self.rows_by_id[stock_id] = stock_data
        row = self.stock_order.index(stock_id)
        left = self.index(row, 0)
        right = self.index(row, len(self.headers) - 1)
        self.dataChanged.emit(
            left,
            right,
            [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.ForegroundRole],
        )

    def set_price_color_enabled(self, enabled):
        if self.price_color_enabled == enabled:
            return

        self.price_color_enabled = enabled
        if not self.stock_order:
            return

        self.dataChanged.emit(
            self.index(0, self.PRICE_COLUMN),
            self.index(len(self.stock_order) - 1, self.PRICE_COLUMN),
            [Qt.ItemDataRole.ForegroundRole],
        )

    def _price_color(self, stock_data):
        """Use the percentage column to color only the price column."""
        if not self.price_color_enabled or len(stock_data) <= self.PERCENTAGE_COLUMN:
            return None

        try:
            percentage = float(str(stock_data[self.PERCENTAGE_COLUMN]).strip("%"))
        except (ValueError, TypeError):
            return None

        if percentage > 0:
            return QColor("red")
        if percentage < 0:
            return QColor("green")
        return None
