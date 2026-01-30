from PySide6.QtCore import QSettings

Organization = "StockMuffin"
Application = "Stocks"

class SettingsManager:

    def __init__(self):
        self.settings = QSettings("StockMuffin", "Stocks")

    def save_stock_id(self, stock_id):
        self.settings.setValue("ID", stock_id)

    def load_stock_id(self) -> list:
        return self.settings.value("ID", defaultValue=[])