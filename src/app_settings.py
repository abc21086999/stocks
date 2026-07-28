from PySide6.QtCore import QSettings, QStandardPaths, QDir, QCoreApplication
import json
from pathlib import Path

Organization = "StockMuffin"
Application = "Stocks"


class SettingsManager:

    def __init__(self):
        if not QCoreApplication.organizationName():
            QCoreApplication.setOrganizationName(Organization)
        if not QCoreApplication.applicationName():
            QCoreApplication.setApplicationName(Application)

        config_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        QDir().mkpath(config_dir)
        self.filepath = Path(config_dir) / "settings.json"

        self.default_settings = {
            "stock_ids": [],
            "show_market_index": True,
            "enable_price_color": True
        }
        self.settings = self._load()

        # 自動資料遷移：如果舊有 QSettings 中存在股票 ID 且 JSON 尚未設定，寫入 JSON
        old_qsettings = QSettings(Organization, Application)
        old_ids = old_qsettings.value("ID", None)
        if old_ids and not self.settings["stock_ids"]:
            if isinstance(old_ids, list):
                self.settings["stock_ids"] = [str(x) for x in old_ids]
            elif isinstance(old_ids, str) and old_ids.strip():
                if "," in old_ids:
                    self.settings["stock_ids"] = [x.strip() for x in old_ids.split(",") if x.strip()]
                else:
                    self.settings["stock_ids"] = [old_ids.strip()]
            self._save()

    def _load(self) -> dict:
        if self.filepath.exists():
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {**self.default_settings, **data}
            except Exception:
                return self.default_settings.copy()
        return self.default_settings.copy()

    def _save(self):
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=4)

    def save_stock_id(self, stock_id):
        self.settings = self._load()
        self.settings["stock_ids"] = stock_id
        self._save()

    def load_stock_id(self) -> list:
        self.settings = self._load()
        return self.settings.get("stock_ids", [])

    def save_show_market_index(self, enabled: bool):
        self.settings = self._load()
        self.settings["show_market_index"] = enabled
        stock_ids = self.settings.get("stock_ids", [])
        market_symbol = "^TWII"

        if enabled:
            # 勾選：若原清單中已有，先移除，確保強制插入到第一個位置 (Index 0)
            if market_symbol in stock_ids:
                stock_ids.remove(market_symbol)
            stock_ids.insert(0, market_symbol)
        else:
            # 勾掉：從清單（尤其是第一個位置）中移除
            if stock_ids and stock_ids[0] == market_symbol:
                stock_ids.pop(0)
            elif market_symbol in stock_ids:
                stock_ids.remove(market_symbol)

        self.settings["stock_ids"] = stock_ids
        self._save()

    def load_show_market_index(self) -> bool:
        return self.settings.get("show_market_index", True)

    def save_enable_price_color(self, enabled: bool):
        self.settings["enable_price_color"] = enabled
        self._save()

    def load_enable_price_color(self) -> bool:
        return self.settings.get("enable_price_color", True)