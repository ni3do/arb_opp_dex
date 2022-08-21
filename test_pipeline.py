import os
from datetime import datetime

import pandas as pd

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from graph import build_graph, draw_graph
from optimal_swap import opt_router, ternary_search
from pool_info.creation_blocks import creation_block
from pool_info.decimals import decimals
from utils.data_loader import (
    build_state,
    load_pool_dict,
    load_state,
    load_swap_base_v2,
    load_swap_base_v3,
    load_ticks,
)

DATA_DIR = os.path.abspath(f"../data")
SCORE_THRESHOLD = 0.7

DATA_BLOCK_SIZE = 2000


def analyze_block(block_number):
    pool_dict = load_pool_dict(block_number, DATA_DIR)
    state_dict = build_state(block_number, pool_dict)
    G = build_graph(block_number, state_dict)
    draw_graph(G, block_number, os.path.abspath(f"../test_res/graph/{block_number}"))


def analyze_coin_opps(block_number):
    start_analyze = datetime.now().timestamp()
    under = 0
    over = 0
    files = sorted(os.listdir(f"../test_res/opps/"))

    for file in files:
        if file.split(".")[0] != str(block_number):
            continue

        print(f"Working on {file}")
        opps = []

        df = pd.read_csv(f"../test_res/opps/{file}")
        counter = 1

        current_block = 0
        for idx, row in df.iterrows():
            if counter % 1 == 0:
                print(f"{counter}/{len(df)}")
                if len(opps) > 0:
                    opp_df = pd.DataFrame(
                        opps,
                        columns=[
                            "block_number",
                            "score",
                            "optimization_time",
                            "profit",
                            "input",
                            "output",
                            "perc_diff",
                            "route",
                        ],
                    )
                    opp_df.to_csv(f"../test_res/trades/{file}", index=False)
            if current_block != row[0]:
                start_state_load = datetime.now().timestamp()
                if current_block - (current_block % DATA_BLOCK_SIZE) != row[0] - (
                    row[0] % DATA_BLOCK_SIZE
                ):
                    state = load_state(row[0], DATA_DIR)
                    ticks = load_ticks(row[0], DATA_DIR)

                swap_base = {}
                tick_dict = {}
                for pool_name in uniswapV3.pool_names:
                    if row[0] > creation_block[pool_name]:
                        if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                            swap_base[pool_name], tick_dict[pool_name] = load_swap_base_v3(
                                pool_name, row[0], state, ticks
                            )

                for pool_name in uniswapV2.pool_names:
                    if row[0] > creation_block[pool_name]:
                        if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                            swap_base[pool_name] = load_swap_base_v2(pool_name, row[0], state)

                for pool_name in sushiswap.pool_names:
                    if row[0] > creation_block[pool_name]:
                        if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                            swap_base[pool_name] = load_swap_base_v2(pool_name, row[0], state)

                current_block = row[0]
                state_load_time = datetime.now().timestamp() - start_state_load
                print(f"State loaded in {state_load_time}")

            route_tuple = eval(row[2])
            over += 1
            sc = 1

            start_ternary = datetime.now().timestamp()
            profit, opt_in, out, route_tuple = ternary_search(
                row[0], route_tuple, swap_base, tick_dict, optimize_exchanges=True
            )
            stop_ternary = datetime.now().timestamp()
            with open(f"../stats/stats/ternary_time.txt", "a") as f:
                f.write(f"{stop_ternary - start_ternary},\n")

            if profit > 0:
                # get profit in full coins
                profit = profit * (10 ** -decimals[route_tuple[0][0]])
                opps.append(
                    [
                        row[0],
                        sc,
                        stop_ternary - start_ternary,
                        profit,
                        int(opt_in),
                        int(out),
                        (row[1] * 100),
                        route_tuple,
                    ]
                )
            counter += 1

        print(f"Opps over: {over}")
        print(f"Opps under: {under}")
        print(f"State loaded in {state_load_time}")
        print(f"Analyze took {datetime.now().timestamp() - start_analyze}")

        opp_df = pd.DataFrame(
            opps,
            columns=[
                "block_number",
                "score",
                "optimization_time",
                "profit",
                "input",
                "output",
                "perc_diff",
                "route",
            ],
        )
        opp_df.to_csv(f"../test_res/trades/{file}", index=False)


def route_inspector(block_number):
    df = pd.read_csv(f"../test_res/trades/{block_number}.csv")

    for idx, row in df.iterrows():
        if idx > 0:
            break
        block_number = row["block_number"]
        route = eval(row["route"])
        print(f"Block: {block_number}")
        amount_in = row["input"]
        amount_out = row["output"]
        state = load_state(block_number, DATA_DIR)
        ticks = load_ticks(block_number, DATA_DIR)
        swap_base = {}
        tick_dict = {}
        for pool_name in uniswapV3.pool_names:
            if block_number > creation_block[pool_name]:
                if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                    swap_base[pool_name], tick_dict[pool_name] = load_swap_base_v3(
                        pool_name, block_number, state, ticks
                    )

        for pool_name in uniswapV2.pool_names:
            if block_number > creation_block[pool_name]:
                if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                    swap_base[pool_name] = load_swap_base_v2(pool_name, block_number, state)

        for pool_name in sushiswap.pool_names:
            if block_number > creation_block[pool_name]:
                if swap_base.get(pool_name) is None or tick_dict.get(pool_name) is None:
                    swap_base[pool_name] = load_swap_base_v2(pool_name, block_number, state)
        for swap in route:
            print(f"Swap: {swap}")

            amount_out, exchange_route = opt_router(
                block_number, [(swap[0], swap[1], [swap[2]])], amount_in, swap_base, tick_dict
            )
            print(f"{swap[0]} -> {swap[1]}")
            print(
                f"{(float(amount_in) * (10**-decimals[swap[0]])):.8f} -> {(float(amount_out) * (10**-decimals[swap[1]])):.8f}"
            )
            amount_in = amount_out
        return amount_out


if __name__ == "__main__":
    block_number = 14700000
    analyze_block(block_number)
    # pool_dict = load_pool_dict(block_number, DATA_DIR)
    # # print(pool_dict)
    # find_opps(block_number, block_number + 1, pool_dict)
    # os.rename(
    #     f"../data/opps/{block_number-(block_number % 200)}_{block_number}.csv",
    #     f"../test_res/opps/{block_number}.csv",
    # )
    # start_analyze = datetime.now().timestamp()
    # analyze_coin_opps(block_number)
    # route_inspector(block_number)
