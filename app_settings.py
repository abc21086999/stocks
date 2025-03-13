from PyQt6.QtCore import QSettings

Organization = "StockMuffin"
Application = "Stocks"

class SettingsManager:

    def __init__(self):
        self.settings = QSettings(organization=Organization, application=Application)

    def save_stock_id(self, stock_id):
        self.settings.setValue("ID", stock_id)

    def load_stock_id(self):
        self.settings.value("ID", [])