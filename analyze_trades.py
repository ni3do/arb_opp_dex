import bisect
import os

import numpy as np
import pandas as pd
from web3 import Web3

DATA_DIR = f"../data"

# Constants
LONDON_HARDFORK_BLOCK = 12_965_000

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 120}))


def optimization_stats():
    files = os.listdir("../data/trades")
    files.sort()

    opt_times = []
    for file in files:
        print(f"Working on {file}")
        df = pd.read_csv(f"../data/trades/{file}")
        for idx, row in df.iterrows():
            opt_times.append(row["optimization_time"])

    opt_times = np.array(opt_times)
    print(f"---------------------------------")
    print(f"Optimization Stats:")
    print(f"Mean:   {opt_times.mean():.4f}s")
    print(f"Std:    {opt_times.std():.4f}s")
    print(f"Max:    {opt_times.max():.4f}s")
    print(f"Min:    {opt_times.min():.4f}s")


def best_trades():
    files = os.listdir("../data/trades")
    files.sort()

    last_block_routes = []
    block_routes = []
    counter_dict = {}
    last_block_number = 0

    final_lengths = []

    file_counter = 0
    for file in files:
        file_counter += 1
        print(f"File {file_counter}/{len(files)}: {file}")
        print(f"Counter: {len(counter_dict)}")
        if len(counter_dict) > 0:
            route_block_live = []
            longest_length = 0
            if len(final_lengths) > 0:
                route_block_live = final_lengths
                with open(f"../stats/best_trades.txt", "w") as f:
                    f.write(f"Opps: {len(route_block_live)}\n")
                    f.write(f"Mean len: {np.mean(route_block_live)}\n")
                    f.write(f"Max len: {np.max(route_block_live)}\n")
                    f.write(f"Min len: {np.min(route_block_live)}\n")

        df = pd.read_csv(f"../data/trades/{file}")
        for idx, row in df.iterrows():
            if idx + 1 % 10 == 0:
                print(f"{idx+1}/{len(df)}")
            block_number = int(row["block_number"])
            route = eval(row["route"])

            if block_number != last_block_number:
                last_block_number = block_number
                last_block_routes = block_routes
                block_routes = []

            if route in last_block_routes:
                already_in_dict = False
                to_remove = []
                for key in counter_dict:

                    if str(route) == key[1] and block_number - 1 == counter_dict[key]["last_block"]:
                        already_in_dict = True
                        counter_dict[key]["length"] += 1
                        counter_dict[key]["last_block"] = block_number
                    if counter_dict[key]["last_block"] < block_number - 1:
                        to_remove.append(key)

                for key in to_remove:
                    final_lengths.append(counter_dict[key]["length"])
                    counter_dict.pop(key)

                if not already_in_dict:
                    counter_dict[(block_number, str(route))] = {
                        "usd_profit": row["usd_profit"],
                        "length": 1,
                        "starting_block": block_number,
                        "last_block": block_number,
                    }

            block_routes.append(route)

    route_block_live = []
    longest_length = 0
    for key in counter_dict:
        route_block_live.append(counter_dict[key]["length"])
        if counter_dict[key]["length"] > longest_length:
            longest_length = counter_dict[key]["length"]

    with open(f"../data/stats/best_trades.txt", "w") as f:
        f.write(f"Opps: {len(route_block_live)}\n")
        f.write(f"Mean len: {np.mean(route_block_live)}\n")
        f.write(f"Max len: {np.max(route_block_live)}\n")
        f.write(f"Min len: {np.min(route_block_live)}\n")


def profit_stats():
    files = os.listdir("../data/trades")
    files.sort()

    file_counter = 0

    last_block_routes = []
    block_routes = []
    last_block_number = 0
    usd_gains = []
    ternary_time = []
    for file in files:
        file_counter += 1
        if file_counter % 20 == 0:
            print(f"File {file_counter}/{len(files)}: {file}")
        if file_counter % 100 == 0:
            temp_usd_gains = np.array(usd_gains)

            print(f"---------------------------------")
            print(f"Profit Stats:")
            print(f"Trades:             {len(temp_usd_gains)}")
            print(f"Mean USD gain:      {sum(temp_usd_gains) / len(temp_usd_gains):.4f}")
            print(f"Median USD gain:    {temp_usd_gains[int(len(temp_usd_gains) / 2)]:.4f}")
            print(f"Max USD gain:       {max(temp_usd_gains):.4f}")
            print(f"Min USD gain:       {min(temp_usd_gains):.4f}")

        df = pd.read_csv(f"../data/trades/{file}")

        for idx, row in df.iterrows():
            if idx + 1 % 10 == 0:
                print(f"{idx+1}/{len(df)}")
            block_number = int(row["block_number"])
            route = eval(row["route"])
            if route in last_block_routes:
                block_routes.append(route)
                continue
            profit = row["profit"]

            if row["tx_cost"] < row["profit"]:
                profit_fee = row["profit"] - row["tx_cost"]
                block_routes.append(route)
                usd_gains.append(row["usd_profit"])
                ternary_time.append(row["optimization_time"])

            if block_number != last_block_number:
                last_block_number = block_number
                last_block_routes = block_routes
                block_routes = []

    usd_gains = np.array(usd_gains)
    ternary_time = np.array(ternary_time)

    print(f"---------------------------------")
    print(f"Profit Stats:")
    print(f"Trades:             {len(usd_gains)}")
    print(f"Mean USD gain:      {sum(usd_gains) / len(usd_gains):.4f}")
    print(f"Median USD gain:    {usd_gains[int(len(usd_gains) / 2)]:.4f}")
    print(f"Max USD gain:       {max(usd_gains):.4f}")
    print(f"Min USD gain:       {min(usd_gains):.4f}")

    with open(f"../stats/profit_stats.txt", "w") as f:
        f.write(f"---------------------------------\n")
        f.write(f"Profit Stats:\n")
        f.write(f"Trades:             {len(usd_gains)}\n")
        f.write(f"Mean USD gain:      {sum(usd_gains) / len(usd_gains):.4f}\n")
        f.write(f"Median USD gain:    {usd_gains[int(len(usd_gains) / 2)]:.4f}\n")
        f.write(f"Max USD gain:       {max(usd_gains):.4f}\n")
        f.write(f"Min USD gain:       {min(usd_gains):.4f}\n")


def analysed_perc_stats():
    df = pd.read_csv("../data/stats/temp_analysis_stats.csv")

    analysed_opps = 0
    total_opps = 0
    duplicate_opps = 0
    profitable_opps = 0
    total_time = 0

    for idx, row in df.iterrows():
        analysed_opps += row["analysed_opps"]
        total_opps += row["total_opps"]
        duplicate_opps += row["duplicate_opps"]
        profitable_opps += row["profitable_opps"]

    total_time += df.iloc[-1]["total_time"]
    print(f"Total Opps:         {int(total_opps)}")
    print(f"Analysed Opps:      {int(analysed_opps)}")
    print(f"Duplicate Opps:     {int(duplicate_opps)}")
    print(f"Profitable Opps:    {int(profitable_opps)}")
    print(f"Total Time:         {total_time/3600:.2f} h")


def blocks_stats():
    trades_dir = "../data/trades"
    files = os.listdir(f"{trades_dir}")
    files.sort()

    used_routes = []

    last_block_rows = pd.DataFrame(
        columns=[
            "block_number",
            "route",
            "profit",
            "tx_cost",
            "tx_cost_usd",
            "input",
            "output",
            "perc_diff",
            "optimization_time",
        ]
    )
    for file in files:
        df = pd.read_csv(f"{trades_dir}/{file}")
        if len(df) == 0:
            continue

        print(f"Working on {file}")

        results = []
        amount_opps = 0
        acc_profit = 0

        start_block = int(file.split("_")[0])
        end_block = int(file.split("_")[1].split(".")[0])

        for block_number in range(start_block, end_block + 1):
            idx_left = bisect.bisect(df["block_number"], block_number - 1)
            idx_right = bisect.bisect(df["block_number"], block_number)
            current_rows = df.iloc[idx_left:idx_right]

            if len(current_rows) == 0:
                continue

            best_route, best_profit, different_routes = get_best_trade(
                current_rows, used_routes, last_block_rows
            )

            acc_profit += best_profit
            amount_opps += different_routes

            if best_route != "":
                used_routes.append(best_route)

            for route in used_routes:
                if (
                    route in last_block_rows["route"].values
                    and route not in current_rows["route"].values
                ):
                    idx = used_routes.index(route)
                    used_routes.pop(idx)

            if best_profit > 0:
                results.append([block_number, best_profit, best_route])

            last_block_rows = current_rows

        if len(results) > 0:
            pd.DataFrame(results, columns=["block_number", "profit", "route"]).to_csv(
                f"../data/stats/block_stats/{file}", index=False
            )


def get_best_trade(df, used_routes, last_block_rows):
    best_profit = 0
    best_route = ""
    routes = 0

    for idx, row in df.iterrows():
        if best_profit < row["usd_profit"] and row["route"] not in used_routes:
            best_profit = row["usd_profit"]
            best_route = row["route"]

        if row["route"] not in last_block_rows["route"].values:
            routes += 1

    return best_route, best_profit, routes


if __name__ == "__main__":
    blocks_stats()
