import sys
from PySide6.QtWidgets import QApplication
from src.main_ui import StockUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StockUI()
    window.show()
    sys.exit(app.exec())
