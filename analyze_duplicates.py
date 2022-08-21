import bisect
import os
from datetime import datetime

import pandas as pd

from optimal_swap import ternary_search
from pool_info.decimals import decimals
from utils.data_loader import load_all_swap_base, load_block, load_state, load_ticks
from utils.tx_cost_estimator import tx_cost
from utils.value_convertor import usd_value

DATA_DIR = f"../data"


def main():
    temp_file_name = f"temp_dupl_stats"
    analysis_stats = []

    last_block_routes = []
    block_routes = []

    try:
        stats = pd.read_csv(f"{DATA_DIR}/stats/{temp_file_name}.csv")
    except Exception as e:
        print(f"No temporary analysis stats file found: {e}")
        stats = pd.DataFrame(
            columns=[
                "base_block",
                "analysed_opps",
                "profitable_opps",
                "time",
                "total_time",
            ]
        )

    start_time = datetime.now().timestamp()

    if len(stats) > 0:
        for idx, row in stats.iterrows():
            analysis_stats.append(
                [
                    int(row["base_block"]),
                    int(row["analysed_opps"]),
                    int(row["profitable_opps"]),
                    round(float(row["time"]), 4),
                    round(float(row["total_time"]), 4),
                ]
            )
        print(f"Loaded {len(analysis_stats)} analysis stats")
        start_block = int(stats.iloc[-1]["base_block"] + 200)
        start_time -= stats.iloc[-1]["total_time"]

        temp_df = pd.read_csv(f"../data/trades_full/{start_block-200}_{start_block-1}.csv")
        temp_df = temp_df[temp_df["block_number"] == start_block - 1]
        for idx, row in temp_df.iterrows():
            route = eval(row["route"])
            last_block_routes.append(route)

        print(f"Starting analysis from block {start_block}")
        print(f"Time passed: {datetime.now().timestamp() - start_time}")

    else:
        start_block = 0

    files = sorted(os.listdir("../data/trades"))

    for file in files:
        file_profitable_opps = 0
        file_analyzed_opps = 0
        file_total_opps = 0
        start_file = datetime.now().timestamp()
        if int(file.split("_")[0]) < start_block:
            continue

        df = pd.read_csv(f"../data/trades/{file}")

        start_block = int(file.split("_")[0])
        end_block = int(file.split("_")[1].split(".")[0])

        state = load_state(start_block, DATA_DIR)
        ticks = load_ticks(start_block, DATA_DIR)

        new_trades = []

        start_50 = datetime.now().timestamp()
        for block_number in range(start_block, end_block + 1):
            block_routes = []
            if block_number % 50 == 0:
                print(
                    f"Working on {file}: {block_number % 200}/200: {datetime.now().timestamp() - start_50:.4f}s"
                )
                start_50 = datetime.now().timestamp()

            idx_left = bisect.bisect(df["block_number"], block_number - 1)
            idx_right = bisect.bisect(df["block_number"], block_number)
            current_rows = df.iloc[idx_left:idx_right]

            if len(current_rows) > 0:
                block, _ = load_block(block_number, DATA_DIR)
                swap_base, tick_dict = load_all_swap_base(block_number, state, ticks)

            for idx, row in current_rows.iterrows():
                file_total_opps += 1
                route = eval(row["route"])
                block_routes.append(route)
                current_block = row["block_number"]

                if route in last_block_routes:
                    start_ternary = datetime.now().timestamp()
                    file_analyzed_opps += 1
                    profit, opt_in, out, route_tuple = ternary_search(
                        current_block,
                        route,
                        swap_base,
                        tick_dict,
                        optimize_exchanges=True,
                    )
                    stop_ternary = datetime.now().timestamp()

                    if profit > 0:
                        file_profitable_opps += 1
                        cost_estimate = tx_cost(current_block, route_tuple, DATA_DIR, block=block)
                        cost_estimate_usd = usd_value(
                            current_block, "ETH", cost_estimate, swap_base
                        )
                        usd_profit = usd_value(current_block, route_tuple[0][0], profit, swap_base)
                        if usd_profit < 5:
                            continue
                        profit = profit * (10 ** -decimals[route_tuple[0][0]])

                        new_trades.append(
                            [
                                row[0],
                                stop_ternary - start_ternary,
                                usd_profit,
                                profit,
                                cost_estimate,
                                cost_estimate_usd,
                                int(opt_in),
                                int(out),
                                (row[1] * 100),
                                route_tuple,
                            ]
                        )
                else:
                    if row["usd_profit"] < 5:
                        continue
                    new_trades.append(row.values)

            last_block_routes = block_routes

        end_file = datetime.now().timestamp()
        if len(new_trades) > 0:
            new_trades = pd.DataFrame(new_trades, columns=df.columns)
            new_trades.to_csv(f"../data/trades_full/{file}", index=False)
        analysis_stats.append(
            [
                file.split("_")[0],
                file_analyzed_opps,
                file_profitable_opps,
                end_file - start_file,
                end_file - start_time,
            ]
        )
        pd.DataFrame(
            analysis_stats,
            columns=[
                "base_block",
                "analysed_opps",
                "profitable_opps",
                "time",
                "total_time",
            ],
        ).to_csv(f"{DATA_DIR}/stats/{temp_file_name}.csv", index=False)


if __name__ == "__main__":
    main()
