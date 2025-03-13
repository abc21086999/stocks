from PyQt6.QtCore import QSettings

class SettingsManager:

    def __init__(self):
        self.settings = QSettings()