from PyQt6.QtWidgets import QLabel, QLineEdit, QPushButton


def create_header():
    header = QLabel()
    header.setText("台股")
    header.setStyleSheet("font-size:25px;color:#F0FFFF;")
    return header

def create_input_area():
    input_area = QLineEdit()
    return input_area

def create_add_button():
    add_button = QPushButton()
    add_button.setText("添加股票")
    return add_button