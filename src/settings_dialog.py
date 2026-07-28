from PySide6.QtWidgets import QDialog, QVBoxLayout, QCheckBox, QDialogButtonBox
from PySide6.QtCore import Signal


class SettingsDialog(QDialog):
    settings_changed = Signal()

    def __init__(self, setting_manager, parent=None):
        super().__init__(parent)
        self.setting_manager = setting_manager
        self.setWindowTitle("偏好設定")
        self.setMinimumWidth(260)

        layout = QVBoxLayout(self)

        # Checkbox 1: 顯示大盤
        self.cb_market_index = QCheckBox("顯示大盤")
        self.cb_market_index.setChecked(self.setting_manager.load_show_market_index())
        layout.addWidget(self.cb_market_index)

        # Checkbox 2: 啟用漲跌幅顏色
        self.cb_price_color = QCheckBox("啟用漲跌幅顏色")
        self.cb_price_color.setChecked(self.setting_manager.load_enable_price_color())
        layout.addWidget(self.cb_price_color)

        # 按鈕區 (確定 / 取消)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_settings)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept_settings(self):
        self.setting_manager.save_show_market_index(self.cb_market_index.isChecked())
        self.setting_manager.save_enable_price_color(self.cb_price_color.isChecked())
        self.settings_changed.emit()
        self.accept()
