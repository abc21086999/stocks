import requests
from datetime import datetime
from PySide6.QtCore import QRunnable
from urllib.parse import urlencode
import json


class StockFetcher:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36 Edg/150.0.0.0",
            })

    def fetch(self, stock_id: str):
        if stock_id.startswith("^"):
            return self._fetch_index(stock_id)
        else:
            return self._fetch_stock(stock_id)

    def _fetch_index(self, stock_id):
        try:
            base_url = "https://tw.stock.yahoo.com"
            api_endpoint = "/_td-stock/api/resource/FinanceChartService.ApacLibraChartIndex"
            stock_symbol = f"{stock_id}"

            # 分成兩組參數：分號參數 和 & 參數
            semicolon_params = {
                "format": "true",
                "type": "tick",
                "symbols": f'{json.dumps([stock_symbol])}',
            }

            ampersand_params = {
                "device": "desktop",
                "ecma": "modern",
                "intl": "tw",
                "lang": "zh-Hant-TW",
                "partner": "none",
                "region": "TW",
                "site": "finance",
                "tz": "Asia/Taipei",
                "returnMeta": "true",
            }

            # 組建分號分隔的字串
            semicolon_string_parts = []
            for key, value in semicolon_params.items():
                semicolon_string_parts.append(f"{key}={value}")
            semicolon_string = ";".join(semicolon_string_parts)

            # 組建 & 分隔的 query string (使用 urllib.parse.urlencode)
            ampersand_query_string = urlencode(ampersand_params)

            # 組合完整的 URL
            full_url = f"{base_url}{api_endpoint};{semicolon_string}?{ampersand_query_string}"

            header = {"Referer": f"https://tw.stock.yahoo.com/s/tse.php"}
            resp = self.session.get(url=full_url, headers=header)

            resp.raise_for_status()

            resp_json = resp.json()
            # 股票名稱
            symbol_name = resp_json.get("data")[0].get("chart").get("meta").get("name")
            # 現在價格
            latest_price = resp_json.get("data")[0].get("chart").get("quote").get("price").get("sort")
            # 漲跌幅
            percentage = resp_json.get("data")[0].get("chart").get("quote").get("changePercent").get("sort")
            # 今日最高
            day_high = resp_json.get("data")[0].get("chart").get("quote").get("dayHighPrice").get("sort")
            # 今日最低
            day_low = resp_json.get("data")[0].get("chart").get("quote").get("dayLowPrice").get("sort")
            # 成交量
            volume = divmod(int(resp_json.get("data")[0].get("chart").get("quote").get("volume")), 1000)[0]
            # 開盤價格
            open_price = resp_json.get("data")[0].get("chart").get("quote").get("openPrice").get("sort")

            return [stock_id, symbol_name, latest_price, percentage, day_high, day_low, open_price, volume]
        except Exception as e:
            print(f'Exception: {e}')
            return [stock_id, "-", "-", "-", "-", "-", "-", "-", ]

    def _fetch_stock(self, stock_id):
        try:
            base_url = "https://tw.stock.yahoo.com"
            api_endpoint = "/_td-stock/api/resource/StockServices.stockList"
            stock_symbol = f"{stock_id}.TW"

            # 分成兩組參數：分號參數 和 & 參數
            semicolon_params = {
                "autoRefresh": int(datetime.now().timestamp() * 1000),
                "fields": "avgPrice,orderbook",
                "symbols": stock_symbol,
            }

            ampersand_params = {
                "device": "desktop",
                "ecma": "modern",
                "intl": "tw",
                "lang": "zh-Hant-TW",
                "partner": "none",
                "region": "TW",
                "site": "finance",
                "tz": "Asia/Taipei",
                "returnMeta": "true",
            }

            # 組建分號分隔的字串
            semicolon_string_parts = []
            for key, value in semicolon_params.items():
                semicolon_string_parts.append(f"{key}={value}")
            semicolon_string = ";".join(semicolon_string_parts)

            # 組建 & 分隔的 query string (使用 urllib.parse.urlencode)
            ampersand_query_string = urlencode(ampersand_params)

            # 組合完整的 URL
            full_url = f"{base_url}{api_endpoint};{semicolon_string}?{ampersand_query_string}"

            header = {"Referer": f"https://tw.stock.yahoo.com/quote/{stock_id}.TW"}
            resp = self.session.get(url=full_url, headers=header)
            resp.raise_for_status()

            resp_json = resp.json()
            # 股票名稱
            symbol_name = resp_json.get("data")[0].get("symbolName")
            # 現在價格
            latest_price = resp_json.get("data")[0].get("price").get("raw")
            # 漲跌幅
            percentage = resp_json.get("data")[0].get("changePercent")
            # 今日最高
            day_high = resp_json.get("data")[0].get("regularMarketDayHigh").get("raw")
            # 今日最低
            day_low = resp_json.get("data")[0].get("regularMarketDayLow").get("raw")
            # 成交量
            volume = divmod(int(resp_json.get("data")[0].get("volume")), 1000)[0]
            # 開盤價格
            open_price = resp_json.get("data")[0].get("regularMarketOpen").get("raw")

            return [stock_id, symbol_name, latest_price, percentage, day_high, day_low, open_price, volume]
        except Exception as e:
            print(f'Exception: {e}')
            return [stock_id, "-", "-", "-", "-", "-", "-", "-", ]

stock_fetcher = StockFetcher()

class FetchStockData(QRunnable):

    def __init__(self, stock_id, data_signal):
        super().__init__()
        self.stock_id: str = stock_id
        self.data_signal = data_signal

    def run(self):
        stock_data_resp = stock_fetcher.fetch(self.stock_id)
        self.data_signal.emit(stock_data_resp)


