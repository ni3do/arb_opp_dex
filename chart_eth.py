import os
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd

from utils.block_data_conversion import bn_to_date

data_dir = "../data"


def price(start_block, end_block):
    values = []
    blocks = []

    counter = 0
    start_date = bn_to_date(start_block, data_dir)
    print(f"Start date: {start_date}")
    end_date = bn_to_date(end_block, data_dir)
    print(f"End date: {end_date}")

    files = sorted(os.listdir(f"../data/ETHUSDC/1d"))

    for file in files:
        if (
            int(file.split("-")[2]) > int(start_date.year)
            and int(file.split("-")[2]) < int(end_date.year)
        ) or (
            int(file.split("-")[2]) == int(start_date.year)
            and int(file.split("-")[3].split(".")[0]) >= int(start_date.month)
            and int(file.split("-")[2]) == int(end_date.year)
            and int(file.split("-")[3].split(".")[0]) <= int(end_date.month)
        ):
            print(file)
            df = pd.read_csv(f"../data/ETHUSDC/1d/{file}")
            for idx, row in df.iterrows():
                if row["close"] > 0:
                    values.append(row["open"])
                    blocks.append(datetime.fromtimestamp(row["timestamp_close"] / 1000))
                    counter += 1

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax = plt.subplots()

    # add labels
    ax.set_xlabel("Date")
    ax.set_ylabel("ETH price in USD")

    ax.plot(blocks, values)

    tl = [f"{d.strftime('%H:00-%d/%m')}" for d in blocks]
    ax.set_xticklabels(tl)
    # Axis formatting.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)

    fig.tight_layout()

    plt.savefig("../charts/eth_price_line.png")


def price_change(start_block, end_block):
    values = []
    blocks = []

    counter = 0
    start_date = bn_to_date(start_block, data_dir)
    print(f"Start date: {start_date}")
    end_date = bn_to_date(end_block, data_dir)
    print(f"End date: {end_date}")

    files = sorted(os.listdir(f"../data/ETHUSDC/1d"))

    for file in files:
        if (
            int(file.split("-")[2]) > int(start_date.year)
            and int(file.split("-")[2]) < int(end_date.year)
        ) or (
            int(file.split("-")[2]) == int(start_date.year)
            and int(file.split("-")[3].split(".")[0]) > int(start_date.month)
            and int(file.split("-")[2]) == int(end_date.year)
            and int(file.split("-")[3].split(".")[0]) < int(end_date.month)
        ):
            print(file)
            df = pd.read_csv(f"../data/ETHUSDC/1d/{file}")
            for idx, row in df.iterrows():
                values.append((row["high"] - row["low"]) / row["close"])
                blocks.append(datetime.fromtimestamp(row["timestamp_close"] / 1000))
                counter += 1
        elif int(file.split("-")[2]) == int(start_date.year) and int(
            file.split("-")[3].split(".")[0]
        ) == int(start_date.month):
            print(file)
            df = pd.read_csv(f"../data/ETHUSDC/1d/{file}")
            for idx, row in df.iterrows():
                if row["timestamp_close"] > start_date.timestamp() * 1000:
                    values.append((row["high"] - row["low"]) / row["close"])
                    blocks.append(datetime.fromtimestamp(row["timestamp_close"] / 1000))
                    counter += 1

        elif int(file.split("-")[2]) == int(end_date.year) and int(
            file.split("-")[3].split(".")[0]
        ) == int(end_date.month):
            print(file)
            df = pd.read_csv(f"../data/ETHUSDC/1d/{file}")
            for idx, row in df.iterrows():
                print(row["timestamp_close"])
                print(start_date.timestamp())
                if row["timestamp_close"] < start_date.timestamp() * 1000:
                    values.append((row["high"] - row["low"]) / row["close"])
                    blocks.append(datetime.fromtimestamp(row["timestamp_close"] / 1000))
                    counter += 1
    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax = plt.subplots()

    # add labels
    ax.set_xlabel("Date")
    ax.set_ylabel("ETH price change in %")

    ax.plot(blocks, values)

    tl = [f"{d.strftime('%H:00-%d/%m')}" for d in blocks]
    ax.set_xticklabels(tl)

    # Axis formatting.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)

    fig.tight_layout()

    plt.savefig("../charts/eth_price_change_line.png")


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


if __name__ == "__main__":
    price(12_400_000, 12_550_000)
    price_change(12_400_000, 12_550_000)
