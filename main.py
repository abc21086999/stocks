import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.main_ui import StockUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("icon.png"))
    window = StockUI()
    window.show()
    sys.exit(app.exec())
