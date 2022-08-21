import bisect
import os

import matplotlib.pyplot as plt
import pandas as pd

from utils.block_data_conversion import bn_to_date

data_dir = "../data"


def chart(start_block, end_block):
    timeframe = "1d"
    trades_dir = f"../data/stats/block_stats"

    blocks = []
    dates = []
    dates_nh = []
    values = []
    prices = []
    price_changes = []
    biggest_opps = []
    volume = []
    blob_gain = 0
    biggest_opp = 0

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
        if curr_idx < len(klines):
            if klines["timestamp_close"].loc[curr_idx] < date.timestamp() * 1000:
                # print(f"{date}: {klines['timestamp_close'].loc[curr_idx]}")
                blocks.append(block)
                dates.append(date.strftime("%H:00-%d/%m/%y"))
                dates_nh.append(date.strftime("%d/%m/%y"))
                values.append(blob_gain / 100_000)
                volume.append(klines["volume"].loc[curr_idx])
                price_changes.append(
                    (klines["high"].loc[curr_idx] - klines["low"].loc[curr_idx])
                    / klines["close"].loc[curr_idx]
                )
                prices.append(klines["close"].loc[curr_idx])
                biggest_opps.append(biggest_opp)
                biggest_opp = 0

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
                values.append(blob_gain / 100_000)
                volume.append(klines["volume"].loc[curr_idx])
                price_changes.append(
                    (klines["high"].loc[curr_idx] - klines["low"].loc[curr_idx])
                    / klines["close"].loc[curr_idx]
                )
                prices.append(klines["close"].loc[curr_idx])
                biggest_opps.append(biggest_opp)
                biggest_opp = 0

                curr_idx += 1
                blob_gain = 0

        if os.path.exists(f"{trades_dir}/{block}_{block+199}.csv"):
            df = pd.read_csv(f"{trades_dir}/{block}_{block+199}.csv")
            for idx, row in df.iterrows():
                blob_gain += row["profit"]
                if row["profit"] > biggest_opp:
                    biggest_opp = row["profit"]

    s1 = pd.Series(price_changes, index=blocks)
    s2 = pd.Series(values, index=blocks)
    corr = s1.corr(s2)
    print(f"Correlation: {s1.corr(s2)}")

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    # ax1.set_title(f"Total arbitrage value and ETH price changes per {timeframe} (corr: {corr:.2f})")
    ax1.set_title(f"Total arbitrage value and ETH price changes per {timeframe}")
    ax2 = ax1.twinx()

    ax1.plot(dates, values, label="USD gained", color="blue")
    ax2.plot(dates, price_changes, label="Price change", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates_nh)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates_nh)

    max_ticks = 10
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    ax1.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Arbitrage value (100K USD)")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)
    ax1.set_ylim(0, max(values) + max(values) / 10)

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
    ax2.set_ylim(0, 0.16 + 0.1)
    ax2.set_yticklabels([x / 100.0 for x in range(0, 18, 2)])
    # ax2.set_yticks(np.linspace(ax2.get_yticks()[0], ax2.get_yticks()[-1], len(ax1.get_yticks())))
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    # fig.legend()
    plt.savefig(
        f"../charts/price_change_arb_value/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png",
        dpi=1000,
    )
    plt.close()
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    s1 = pd.Series(prices, index=blocks)
    s2 = pd.Series(values, index=blocks)
    corr = s1.corr(s2)
    print(f"Correlation: {s1.corr(s2)}")

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"USD gained with ETH price per {timeframe}")
    ax2 = ax1.twinx()

    ax1.plot(dates, values, label="USD gained", color="blue")
    ax2.plot(dates, prices, label="ETH price", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates_nh)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates_nh)
    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    ax1.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Arbitrage value (100K USD)")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.set_ylim(0, 16)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    # add labels
    ax2.set_xlabel("Date")
    ax2.set_ylabel("ETH price")
    # Axis formatting.
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_color("#DDDDDD")
    ax2.tick_params(bottom=False, left=False, right=False)
    ax2.set_axisbelow(True)
    ax2.set_ylim(0, 4200)
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/price_arb_value/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png",
        dpi=1000,
    )
    plt.close()
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"Biggest trade per {timeframe} with ETH price swings")
    ax2 = ax1.twinx()

    ax1.plot(dates, biggest_opps, label="Biggest trade value", color="blue")
    ax2.plot(dates, price_changes, label="Price change", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates_nh)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates_nh)
    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax1.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Biggest trade value (USD)")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
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
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/biggest_trades/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png",
        dpi=1000,
    )
    plt.close()
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------

    plt.rcParams["figure.figsize"] = (10, 5)
    fig, ax1 = plt.subplots()

    ax1.set_title(f"USD gained per {timeframe} with trading volume")
    ax2 = ax1.twinx()

    ax1.plot(dates, values, label="USD gained", color="blue")
    ax2.plot(dates, volume, label="Trading volume", color="orange")

    ax1.set_xticks(dates)
    ax1.set_xticklabels(dates_nh)
    ax2.set_xticks(dates)
    ax2.set_xticklabels(dates_nh)
    max_ticks = 8
    ax1.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.xaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax1.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))
    ax2.yaxis.set_major_locator(plt.MaxNLocator(max_ticks))

    # add labels
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Arbitrage value (100K USD)")
    # Axis formatting.
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.spines["left"].set_visible(False)
    ax1.spines["bottom"].set_color("#DDDDDD")
    ax1.tick_params(bottom=False, left=False)
    ax1.set_axisbelow(True)
    ax1.yaxis.grid(True, color="#EEEEEE")
    ax1.xaxis.grid(False)

    # add labels
    ax2.set_xlabel("Date")
    ax2.set_ylabel("ETH trading volume (USD")
    # Axis formatting.
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.spines["left"].set_visible(False)
    ax2.spines["bottom"].set_color("#DDDDDD")
    ax2.tick_params(bottom=False, left=False, right=False)
    ax2.set_axisbelow(True)
    # ax2.yaxis.grid(True, color="#EEEEEE")
    # ax2.xaxis.grid(False)

    fig.tight_layout()
    fig.legend()
    plt.savefig(
        f"../charts/volume_arb_value/{int(start_block/100_000)}_{int(end_block/100_000)}_{timeframe}.png",
        dpi=1000,
    )
    plt.close()
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------
    # ----------------------------------------------------------------------------------------------------------------------


# chart(12_000_000, 14_000_000)
chart(12_000_000, 13_000_000)
chart(13_000_000, 14_000_000)
# chart(12_400_000, 12_500_000)
# chart(13_100_000, 13_200_000)
# chart(13_700_000, 13_800_000)
# for i in range(0, 12):
#     base = 12_000_000
#     chart(base + (i * 100_000), base + ((i + 1) * 100_000))
# chart(12_000_000, 13_200_000)
