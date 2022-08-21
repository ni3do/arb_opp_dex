import io
import zipfile

import pandas as pd
import requests


def getZippedDataForTicker(ticker, timeframe):
    base_url = f"https://data.binance.vision/data/spot/monthly/klines/{ticker}/{timeframe}/{ticker}-{timeframe}"
    for year in range(2017, 2023):
        for month in range(1, 13):
            print(f"{ticker} {timeframe} {year}_{month}")

            if month < 10:
                url = f"{base_url}-{year}-0{month}.zip"
            else:
                url = f"{base_url}-{year}-{month}.zip"
            print(url)
            try:
                r = requests.get(url)
                z = zipfile.ZipFile(io.BytesIO(r.content))
                z.extractall(f"../data/{ticker}/{timeframe}")
                if month < 10:
                    file_path = (
                        f"../data/{ticker}/{timeframe}/{ticker}-{timeframe}-{year}-0{month}.csv"
                    )
                else:
                    file_path = (
                        f"../data/{ticker}/{timeframe}/{ticker}-{timeframe}-{year}-{month}.csv"
                    )
                df = pd.read_csv(file_path)

                df.columns = [
                    "timestamp_open",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "timestamp_close",
                    "quote_asset_volume",
                    "number_of_trades",
                    "taker_buy_base_asset_volume",
                    "taker_buy_quote_asset_volume",
                    "ignore",
                ]

                df.to_csv(file_path, index=False)

            except zipfile.BadZipFile as e:
                print(e)


getZippedDataForTicker("ETHUSDT", "4h")
getZippedDataForTicker("ETHUSDT", "1d")
getZippedDataForTicker("ETHUSDT", "1w")
