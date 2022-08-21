import os

import matplotlib.pyplot as plt
import pandas as pd

data_dir = "../data"


def biggest_trade(start_block, end_block, blob_size):
    # trades_dir = f"../data/trades_full"
    trades_dir = f"../data/stats/block_stats"
    values = []
    blocks = []
    # bar_labels = []

    biggest_opp = 0
    counter = 0
    for block in range(start_block, end_block, 200):
        if (counter * 200) % blob_size == 0:
            values.append(biggest_opp)
            blocks.append(block)
            biggest_opp = 0
        counter += 1

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                if row["profit"] > biggest_opp:
                    biggest_opp = row["profit"]

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"Biggest arbitrage opportunity in USD per {human_format(blob_size)} blocks")

    h_blocks = [human_format(x) for x in blocks]

    ax1.set_xticks(blocks)
    ax1.set_xticklabels(h_blocks)
    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Arbitrage value (100K $USD)")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    ax1.plot(blocks, values, label="Biggest trade value")

    fig.tight_layout()
    plt.savefig(
        f"../charts/biggest_trades/{int(start_block/100_000)}_{int(end_block/100_000)}_{int(blob_size/1000)}.png"
    )


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


biggest_trade(13_200_000, 14_000_000, 10_000)
