from PyQt6 import QtWidgets
import sys

app = QtWidgets.QApplication(sys.argv)  # 視窗程式開始

Window = QtWidgets.QWidget()              # 建立基底元件
Window.setWindowTitle('股票偵測器')      # 設定標題
Window.resize(600, 600)                   # 設定長寬尺寸
Window.setStyleSheet('background:#fcfcfc;')  # 使用CSS樣式設定背景

label = QtWidgets.QLabel(Window)
label.setText("台股")
label.setStyleSheet('font-size:30px')

add_stock_input = QtWidgets.QLineEdit(Window)
add_stock_input.setGeometry(100, 100, 100, 20)

add_stock_button = QtWidgets.QPushButton(Window)
add_stock_button.setText("添加股票")

Window.show()                             # 顯示基底元件
sys.exit(app.exec())