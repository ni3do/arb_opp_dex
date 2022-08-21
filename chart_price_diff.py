import bisect
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from utils.block_data_conversion import bn_to_date

data_dir = "../data"


def chart(start_block, end_block):
    timeframe = "1d"
    trades_dir = f"../data/stats/pd_cycle"
    # trades_dir = f"../data/stats/block_stats"

    blocks = []
    dates = []
    prices = []
    price_changes = []
    volume = []
    biggest_dprice_diffs = []
    mean_dprice_diffs = []
    blob_price_diffs = []
    biggest_dprice_diff = 0

    loaded_base_block = 0

    start_date = bn_to_date(start_block, data_dir)
    print(f"Start date:     {start_date}")
    end_date = bn_to_date(end_block, data_dir)
    print(f"End date:       {end_date}")
    klines = pd.read_csv(
        f"{data_dir}/ETHUSDT/{timeframe}/ETHUSDT-{timeframe}-{start_date.year}-{start_date.month:02}.csv"
    )
    curr_idx = bisect.bisect(klines["timestamp_close"], start_date.timestamp() * 1000)

    for block in range(start_block, end_block, 200):
        if block % 50_000 == 0:
            print(f"Block: {block}/{end_block}")

        date = bn_to_date(block, data_dir)
        # curr_idx = bisect.bisect(klines["timestamp_close"], start_date.timestamp() * 1000)
        if curr_idx < len(klines):
            if klines["timestamp_close"].loc[curr_idx] < date.timestamp() * 1000:
                # print(f"{date}: {klines['timestamp_close'].loc[curr_idx]}")
                blocks.append(block)
                dates.append(date.strftime("%H:00-%d/%m"))
                volume.append(klines["volume"].loc[curr_idx])
                price_changes.append(
                    (klines["high"].loc[curr_idx] - klines["low"].loc[curr_idx])
                    / klines["close"].loc[curr_idx]
                )
                prices.append(klines["close"].loc[curr_idx])
                biggest_dprice_diffs.append(biggest_dprice_diff)
                mean_dprice_diffs.append(np.array(blob_price_diffs).mean())
                biggest_dprice_diff = 0
                blob_price_diffs = []

                curr_idx += 1
        else:
            klines = pd.read_csv(
                f"{data_dir}/ETHUSDT/{timeframe}/ETHUSDT-{timeframe}-{date.year}-{date.month:02}.csv"
            )
            curr_idx = 0
            if klines["timestamp_close"].loc[curr_idx] < date.timestamp() * 1000:
                blocks.append(block)
                dates.append(date.strftime("%H:00-%d/%m"))
                volume.append(klines["volume"].loc[curr_idx])
                price_changes.append(
                    (klines["high"].loc[curr_idx] - klines["low"].loc[curr_idx])
                    / klines["close"].loc[curr_idx]
                )
                prices.append(klines["close"].loc[curr_idx])
                biggest_dprice_diffs.append(biggest_dprice_diff)
                mean_dprice_diffs.append(np.array(blob_price_diffs).mean())
                biggest_dprice_diff = 0
                blob_price_diffs = []

                curr_idx += 1
        if block - (block % 20_000) != loaded_base_block:
            if os.path.exists(f"{trades_dir}/{block - (block % 20_000)}.csv"):
                loaded_base_block = block - (block % 20_000)
                df = pd.read_csv(f"{trades_dir}/{block - (block % 20_000)}.csv")
                # temp_df = df.sort_values(by=["max_pd", "mean_pd"], ascending=False, inplace=False)
                # temp_df.to_csv(f"./test_pd/{block - (block % 20_000)}.csv", index=False)
            else:
                # print(f"{block - (block % 20_000)} not found")
                continue

        idx_left = bisect.bisect(df["block_number"], block - 1)
        # print(f"{block} {idx_left}")
        # print(df.iloc[idx_left])
        row = df.iloc[idx_left]
        # print(f"{row['block_number']}")
        # idx_right = bisect.bisect(df["block_number"], block + 199)
        # print(f"{block}: {idx_left} {idx_right}")
        # print(df.iloc[idx_left])
        # print(df.iloc[idx_right])
        # print(df.iloc[idx_left:idx_right])
        # current_rows = df.iloc[idx_left:idx_right]

        # for idx, row in current_rows.iterrows():
        # if row["max_pd"] > 10:
        #     # print(row)
        #     continue

        # if row["max_pd"] > 100:
        #     print(row)
        blob_price_diffs.append(row["mean_pd"] / 100)
        if row["max_pd"] > biggest_dprice_diff:
            biggest_dprice_diff = row["max_pd"] / 100

    # print(dates)
    # print(blocks)
    # print(values)
    # print(price_changes)
    print(biggest_dprice_diffs)

    mean_dprice_diffs = pd.Series(mean_dprice_diffs).fillna(0).values
    biggest_dprice_diffs = pd.Series(biggest_dprice_diffs).fillna(0).values

    # print(mean_dprice_diffs)
    # print(f"-----------------------------------------------")
    # print(biggest_dprice_diffs)

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    s1 = pd.Series(biggest_dprice_diffs, index=dates)
    s2 = pd.Series(price_changes, index=dates)
    corr = s1.corr(s2)

    ax1.set_title(
        f"Largest DEX price difference and ETH price change per {timeframe} (corr: {corr:.2f}"
    )
    ax2 = ax1.twinx()

    ax1.plot(dates, biggest_dprice_diffs, label="Biggest price differences DEX", color="blue")
    ax2.plot(dates, price_changes, label="ETH price change", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates)

    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price difference in %")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, max(biggest_dprice_diffs) + max(biggest_dprice_diffs) * 0.1)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    # add labels
    ax2.set_xlabel("Date")
    ax2.set_ylabel("ETH price change")
    # Axis formatting.
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_color("#DDDDDD")
    ax2.tick_params(bottom=False, left=False, right=False)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, max(price_changes) + max(price_changes) * 0.1)
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/price_change_max_dprice_diff/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png"
    )
    plt.close()
    # ------------------------------------------------------
    # ------------------------------------------------------
    # ------------------------------------------------------
    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    s1 = pd.Series(mean_dprice_diffs, index=dates)
    s2 = pd.Series(price_changes, index=dates)
    corr = s1.corr(s2)

    ax1.set_title(
        f"Mean DEX price difference and ETH price change per {timeframe} (corr: {corr:.2f})"
    )
    ax2 = ax1.twinx()

    ax1.plot(dates, mean_dprice_diffs, label="Mean price differences", color="blue")
    ax2.plot(dates, price_changes, label="Price change", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates)

    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price difference in %")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)
    ax1.set_ylim(0, max(mean_dprice_diffs) + (max(mean_dprice_diffs) * 0.1))

    # add labels
    ax2.set_xlabel("Date")
    ax2.set_ylabel("ETH price change")
    # Axis formatting.
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_color("#DDDDDD")
    ax2.tick_params(bottom=False, left=False, right=False)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, max(price_changes) + (max(price_changes) * 0.1))
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/price_change_mean_dprice_diff/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png"
    )
    plt.close()
    # ------------------------------------------------------
    # ------------------------------------------------------
    # ------------------------------------------------------

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    s1 = pd.Series(biggest_dprice_diffs, index=dates)
    s2 = pd.Series(volume, index=dates)
    corr = s1.corr(s2)

    ax1.set_title(
        f"Largest DEX price difference and trading volume per {timeframe} (corr: {corr:.2f}"
    )
    ax2 = ax1.twinx()

    ax1.plot(dates, biggest_dprice_diffs, label="Biggest price diff. DEX", color="blue")
    ax2.plot(dates, volume, label="ETH trading volume", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates)

    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Price difference in %")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, max(biggest_dprice_diffs) + max(biggest_dprice_diffs) * 0.1)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    # add labels
    ax2.set_xlabel("Date")
    ax2.set_ylabel("ETH trading volume")
    # Axis formatting.
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_color("#DDDDDD")
    ax2.tick_params(bottom=False, left=False, right=False)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, max(volume) + max(volume) * 0.1)
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/volume_max_dprice_diff/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png"
    )
    plt.close()
    # ------------------------------------------------------
    # ------------------------------------------------------
    # ------------------------------------------------------

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"Mean price difference across DEXs per {timeframe}")

    ax1.plot(dates, mean_dprice_diffs, label="Mean price diff. DEXs", color="blue")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates)

    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Mean price difference in %")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, max(mean_dprice_diffs) + max(mean_dprice_diffs) * 0.1)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/dprice_diff_mean/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png"
    )
    plt.close()
    # ------------------------------------------------------
    # ------------------------------------------------------
    # ------------------------------------------------------
    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"Maximal price difference across DEXs per {timeframe}")

    ax1.plot(dates, biggest_dprice_diffs, label="Maximal price diff. DEXs", color="blue")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates)

    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Maximal price difference in %")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, max(biggest_dprice_diffs) + max(biggest_dprice_diffs) * 0.1)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/dprice_diff_max/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png"
    )
    plt.close()
    # ------------------------------------------------------
    # ------------------------------------------------------
    # ------------------------------------------------------


# chart(12_600_000, 12_700_000)
chart(12_000_000, 14_000_000)
chart(12_000_000, 13_000_000)
chart(13_000_000, 14_000_000)
for i in range(0, 20):
    base = 12_000_000
    chart(base + (i * 100_000), base + ((i + 1) * 100_000))

# chart(12_000_000, 14_000_000)
