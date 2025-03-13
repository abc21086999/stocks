import requests
import urllib.parse
from datetime import datetime
from PyQt6.QtCore import pyqtSlot


@pyqtSlot()
def get_stock_data(stock_id_list: list = []):
    return_list = []
    for id in stock_id_list:
        base_url = "https://tw.stock.yahoo.com"
        api_endpoint = "/_td-stock/api/resource/StockServices.stockList"
        stock_symbol = f"{id}.TW"

        # 分成兩組參數：分號參數 和 & 參數
        semicolon_params = {
            "autoRefresh": int(datetime.now().timestamp()),
            "fields": "avgPrice,orderbook",
            "symbols": stock_symbol,
        }

        ampersand_params = {
            "bkt": '["TW-Stock-Desktop-NewTechCharts-Rampup","t3-tw-fp-trough-galaxy"]',
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

        return_list.append([symbol_id, symbol_name, latest_price, percentage, day_low, day_high, volume])
    return return_list
