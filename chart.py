import os

import matplotlib.pyplot as plt
import pandas as pd

from utils.block_data_conversion import bn_to_date

data_dir = "../data"


def total_value_bar(bar_width):
    trades_dir = "../data/trades_full"
    files = os.listdir(trades_dir)
    files.sort()

    trade_counter = 1
    one_bar_gain = 0
    base_blocks = []
    usd_gains = []
    for file in files:
        df = pd.read_csv(f"{trades_dir}/{file}")
        for idx, row in df.iterrows():
            one_bar_gain += row["usd_profit"]
            trade_counter += 1

        base_blocks.append(file.split("_")[0])
        usd_gains.append(one_bar_gain)
        one_bar_gain = 0

    # print(usd_gains)
    # print(base_blocks)

    fig, ax = plt.subplots()
    # fig = plt.figure(figsize=(10, 5))
    plt.ylabel("USD gained")
    plt.yscale("log")

    plt.xlabel("Base Block 12M")
    bars = ax.bar(x=base_blocks, height=usd_gains, width=1)

    print(f"len(bars): {len(bars)}")
    bar_color = bars[0].get_facecolor()
    for bar in bars:
        print(bar.get_facecolor())
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() * 0.1,
            "test",
            horizontalalignment="center",
            color=bar_color,
            weight="bold",
        )
    plt.savefig("../test_res/total_value_bar.png")


def block_total_value_opps(start_block, end_block, bar_size):
    # trades_dir = f"../data/trades_full"
    trades_dir = f"../data/stats/block_stats"
    values = []
    blocks = []
    # bar_labels = []
    blob_gain = 0

    counter = 0
    for block in range(start_block, end_block, 200):
        if (counter * 200) % bar_size == 0:
            values.append(int(blob_gain))
            blocks.append(block)
            blob_gain = 0
        counter += 1

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                if row["profit"] > 10_000:
                    print(
                        f"{bn_to_date(int(row['block_number']), data_dir)}: {row['block_number']}: {row['profit']} on route {row['route']}"
                    )
                blob_gain += row["profit"]

    values.pop(0)
    blocks.pop(0)
    print(values)
    print(blocks)

    # plt.rcParams["figure.figsize"] = (10, 5)
    # fig, ax = plt.subplots()

    # # add labels
    # ax.set_xlabel("Date")
    # ax.set_ylabel("USD gained")
    # ax.set_title(f"USD gained per {human_format(bar_size)} blocks ({start_block} - {end_block})")

    # tl = [human_format(int(block) - 12_000_000) for block in blocks]
    # tl = [
    #     f"{bn_to_date(int(b) - bar_size, data_dir).strftime('%d/%m')}-{bn_to_date(int(b), data_dir).strftime('%d/%m')}"
    #     for b in blocks
    # ]

    # bars = ax.bar(
    #     x=blocks,
    #     height=values,
    #     tick_label=tl,
    #     width=1,
    # )

    # # Axis formatting.
    # ax.spines["top"].set_visible(False)
    # ax.spines["right"].set_visible(False)
    # ax.spines["left"].set_visible(False)
    # ax.spines["bottom"].set_color("#DDDDDD")
    # ax.tick_params(bottom=False, left=False)
    # ax.set_axisbelow(True)
    # ax.yaxis.grid(True, color="#EEEEEE")
    # ax.xaxis.grid(False)

    # bar_color = bars[0].get_facecolor()
    # # bar_color = (0, 0, 0, 1.0)

    # for bar in bars:
    #     ax.text(
    #         bar.get_x() + bar.get_width() / 2,
    #         bar.get_height() + 1000,
    #         human_format(bar.get_height()),
    #         horizontalalignment="center",
    #         color=bar_color,
    #         weight="bold",
    #     )

    # fig.tight_layout()
    # plt.savefig("../charts/total_value_bar.png")

    # blocks = np.arrange(start_block, end_block, bar_size)
    plt.rcParams["figure.figsize"] = (10, 5)

    plt.plot(
        blocks,
        values,
    )

    plt.savefig("../charts/total_value_line.png")


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:f}".format(num).rstrip("0").rstrip("."), ["", "K", "M", "B", "T"][magnitude]
    )


def biggest_trade(start_block, end_block, bar_size):
    # trades_dir = f"../data/trades_full"
    trades_dir = f"../data/stats/block_stats"
    values = []
    blocks = []
    # bar_labels = []

    biggest_opp = 0
    counter = 0
    for block in range(start_block, end_block, 200):
        if (counter * 200) % bar_size == 0:
            values.append(biggest_opp)
            blocks.append(f"{block}")
            biggest_opp = 0
        counter += 1

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                if row["profit"] > biggest_opp:
                    biggest_opp = row["profit"]

    print(values)
    print(blocks)

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax = plt.subplots()

    # add labels
    ax.set_xlabel("Date")
    ax.set_ylabel("USD gained")
    ax.set_title(f"USD gained per {human_format(bar_size)} blocks ({start_block} - {end_block})")

    tl = [
        f"{bn_to_date(int(b), data_dir).strftime('%d/%m')}-{bn_to_date(int(b)+bar_size, data_dir).strftime('%d/%m')}"
        for b in blocks
    ]
    tl = [human_format(int(block) - 12_000_000) for block in blocks]

    bars = ax.bar(
        x=blocks,
        height=values,
        tick_label=tl,
        width=1,
    )

    # Axis formatting.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)

    bar_color = bars[0].get_facecolor()
    # bar_color = (0, 0, 0, 1.0)

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1000,
            human_format(bar.get_height()),
            horizontalalignment="center",
            color=bar_color,
            weight="bold",
        )

    fig.tight_layout()
    plt.savefig("../charts/biggest_trades_bar.png")


def opp_lifetime(start_block, end_block, bar_size):
    trades_dir = f"../data/trades_full"
    # trades_dir = f"../data/stats/block_stats"
    values = []
    blocks = []
    # bar_labels = []

    last_block_routes = []
    block_routes = []

    biggest_opp = 0
    counter = 0

    for block in range(start_block, end_block, 200):
        if (counter * 200) % bar_size == 0:
            values.append(biggest_opp)
            blocks.append(f"{block}")
            biggest_opp = 0
        counter += 1

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                if row["profit"] > biggest_opp:
                    biggest_opp = row["profit"]

    print(values)
    print(blocks)

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax = plt.subplots()

    # add labels
    ax.set_xlabel("Date")
    ax.set_ylabel("USD gained")
    ax.set_title(f"USD gained per {human_format(bar_size)} blocks ({start_block} - {end_block})")

    tl = [
        f"{bn_to_date(int(b), data_dir).strftime('%d/%m')}-{bn_to_date(int(b)+bar_size, data_dir).strftime('%d/%m')}"
        for b in blocks
    ]
    tl = [human_format(int(block) - 12_000_000) for block in blocks]

    bars = ax.bar(
        x=blocks,
        height=values,
        tick_label=tl,
        width=1,
    )

    # Axis formatting.
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#DDDDDD")
    ax.tick_params(bottom=False, left=False)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color="#EEEEEE")
    ax.xaxis.grid(False)

    bar_color = bars[0].get_facecolor()
    # bar_color = (0, 0, 0, 1.0)

    for bar in bars:
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1000,
            human_format(bar.get_height()),
            horizontalalignment="center",
            color=bar_color,
            weight="bold",
        )

    fig.tight_layout()
    plt.savefig("../charts/opp_lifetime_bar.png")


if __name__ == "__main__":
    # total_value_bar(100_000)
    block_total_value_opps(12_300_000, 12_500_000, 10_000)
    biggest_trade(12_800_000, 13_100_000, 100_000)
