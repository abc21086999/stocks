import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from src.main_ui import StockUI
import platform
from pathlib import Path

def icon():
    icon_file_path = None
    real_platform = platform.system()
    if real_platform == "Windows":
        icon_file_path = Path(__file__).parent / "icon.ico"
    else:
        icon_file_path = Path(__file__).parent / "icon.png"
    return icon_file_path

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(str(icon())))
    window = StockUI()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
