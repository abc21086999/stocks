import time

import requests
import urllib.parse
from datetime import datetime
from PyQt6.QtCore import pyqtSlot, QRunnable


class FetchStockData(QRunnable):

    def __init__(self, stock_id, data_signal):
        super().__init__()
        self.stock_id = stock_id
        self.data_signal = data_signal

    def fetch_data(self):
        try:
            base_url = "https://tw.stock.yahoo.com"
            api_endpoint = "/_td-stock/api/resource/StockServices.stockList"
            stock_symbol = f"{self.stock_id}.TW"

            # 分成兩組參數：分號參數 和 & 參數
            semicolon_params = {
                "autoRefresh": int(datetime.now().timestamp()),
                "fields": "avgPrice,orderbook",
                "symbols": stock_symbol,
            }

            ampersand_params = {
                # "bkt": '["TW-Stock-Desktop-NewTechCharts-Rampup","t3-tw-fp-trough-galaxy"]',
                "device": "desktop",
                "ecma": "modern",
                "intl": "tw",
                "lang": "zh-Hant-TW",
                "partner": "none",
                "region": "TW",
                "site": "finance",
                "tz": "Asia/Taipei",
                "ver": "1.4.483",
                "returnMeta": "true"
            }

            # 組建分號分隔的字串
            semicolon_string_parts = []
            for key, value in semicolon_params.items():
                semicolon_string_parts.append(f"{key}={value}")
            semicolon_string = ";".join(semicolon_string_parts)

            # 組建 & 分隔的 query string (使用 urllib.parse.urlencode)
            ampersand_query_string = urllib.parse.urlencode(ampersand_params)

            # 組合完整的 URL
            full_url = f"{base_url}{api_endpoint};{semicolon_string}?{ampersand_query_string}"

            resp = requests.get(full_url).json()
            symbol_id = resp.get("data")[0].get("symbol")
            symbol_name = resp.get("data")[0].get("symbolName")
            latest_price = resp.get("data")[0].get("price").get("raw")
            percentage = resp.get("data")[0].get("changePercent")
            day_high = resp.get("data")[0].get("regularMarketDayHigh").get("raw")
            day_low = resp.get("data")[0].get("regularMarketDayLow").get("raw")
            volume = str(int(int(resp.get("data")[0].get("volume")) / 1000))
            open_price = resp.get("data")[0].get("regularMarketOpen").get("raw")
            print(resp)
            return [self.stock_id, symbol_name, latest_price, percentage, day_high, day_low, open_price, volume]
        except:
            return [self.stock_id, self.stock_id, self.stock_id, self.stock_id, self.stock_id, self.stock_id, self.stock_id, self.stock_id]

    def run(self):
        stock_data_resp = self.fetch_data()
        self.data_signal.emit(stock_data_resp)


