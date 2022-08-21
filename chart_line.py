import bisect
import os

import matplotlib.pyplot as plt
import pandas as pd

from utils.block_data_conversion import bn_to_date

data_dir = "../data"


def blob_total_value(start_block, end_block):
    timeframe = "1d"
    # trades_dir = f"../data/trades_full"
    trades_dir = f"../data/stats/block_stats"
    values = []
    blocks = []
    dates = []
    dates_nh = []
    # bar_labels = []
    blob_gain = 0
    total_gain = 0

    start_date = bn_to_date(start_block, data_dir)
    print(f"Start date: {start_date}")
    end_date = bn_to_date(end_block, data_dir)
    print(f"End date: {end_date}")
    klines = pd.read_csv(
        f"{data_dir}/ETHUSDT/{timeframe}/ETHUSDT-{timeframe}-{start_date.year}-{start_date.month:02}.csv"
    )
    curr_idx = bisect.bisect(klines["timestamp_close"], start_date.timestamp() * 1000)

    for block in range(start_block, end_block, 200):
        date = bn_to_date(block, data_dir)
        # curr_idx = bisect.bisect(klines["timestamp_close"], start_date.timestamp() * 1000)
        if curr_idx < len(klines):
            if klines["timestamp_close"].loc[curr_idx] < date.timestamp() * 1000:
                # print(f"{date}: {klines['timestamp_close'].loc[curr_idx]}")
                blocks.append(block)
                dates.append(date.strftime("%H:00-%d/%m/%y"))
                dates_nh.append(date.strftime("%d/%m/%y"))
                values.append(int(blob_gain) / 100_000)

                curr_idx += 1
                blob_gain = 0
        else:
            klines = pd.read_csv(
                f"{data_dir}/ETHUSDT/{timeframe}/ETHUSDT-{timeframe}-{date.year}-{date.month:02}.csv"
            )
            curr_idx = 0
            if klines["timestamp_close"].loc[curr_idx] < date.timestamp() * 1000:
                blocks.append(block)
                dates.append(date.strftime("%H:00-%d/%m/%y"))
                dates_nh.append(date.strftime("%d/%m/%y"))
                values.append(int(blob_gain) / 100_000)

        # if (counter * 200) % blob_size == 0:
        #     values.append(int(blob_gain) / 100_000)
        #     blocks.append(block)
        #     total_gain += blob_gain
        #     blob_gain = 0
        # counter += 1

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                # if row["profit"] > 10_000:
                #     print(
                #         f"{bn_to_date(int(row['block_number']), data_dir)}: {row['block_number']}: {row['profit']} on route {row['route']}"
                #     )
                blob_gain += row["profit"]

    # values.pop(0)
    # blocks.pop(0)
    # print(values)
    # print(blocks)

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax = plt.subplots()

    # add labels
    ax.set_xlabel("Date")
    ax.set_ylabel("USD gained (100K USD)")
    ax.set_title(f"USD gained per {timeframe}")

    # tl = [
    #     f"{bn_to_date(int(b) - blob_size, data_dir).strftime('%d/%m/%y')}-{bn_to_date(int(b), data_dir).strftime('%d/%m')}"
    #     for b in blocks
    # ]
    # tl = [human_format(int(block) - 12_000_000) for block in blocks]
    # tl = [f"{bn_to_date(int(b) - blob_size, data_dir).strftime('%d/%m/%y')}" for b in blocks]

    ax.plot(dates, values, label="USD gained", color="blue")

    # Axis formatting.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    # ax.set_ylim(0, 20)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)

    ax.set_xticks(dates)
    ax.set_xticklabels(dates_nh)
    max_ticks = 8
    ax.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    fig.tight_layout()

    plt.savefig("../charts/total_value_line.png", dpi=1000)

    print(f"Total gain: {human_format(total_gain)}")


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
    # total_value_bar(100_000)
    blob_total_value(12_000_000, 13_000_000)
