import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import pandas as pd
from web3 import Web3

from optimal_swap import ternary_search
from pool_info.decimals import decimals
from score import score
from utils.data_loader import load_all_swap_base, load_state, load_ticks
from utils.tx_cost_estimator import tx_cost
from utils.value_convertor import usd_value

DATA_DIR = "../data"
SCORE_THRESHOLD = 0.7
DATA_BLOCK_SIZE = 2000

ANALYZE_DUPLICATE_OPPS = True
USE_SCORING = False
TIMING_RUN = False

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 120}))

# runs ternary search on all found opportunities in the given file
def analyze_opps_file(file):
    start_time = datetime.now().timestamp()
    analysed_opps = 0
    profitable_opps = 0
    duplicate_opps = 0

    print(f"Working on {file}")
    opps = []
    df = pd.read_csv(f"{DATA_DIR}/opps/{file}")
    counter = 1

    start_10 = datetime.now().timestamp()
    current_block = 0

    if not ANALYZE_DUPLICATE_OPPS:
        last_block_routes = []
        block_routes = []
        saved_opps = []
        last_saved_opps = []
        last_block_number = 0

    for idx, row in df.iterrows():
        start_row = datetime.now().timestamp()
        # save progress periodically
        if counter % 500 == 0:
            # print(f"Duplicates: {duplicate_opps}")
            stop_10 = datetime.now().timestamp()
            print(f"{counter}/{len(df)}: {stop_10 - start_10:.4f}s")
            if len(opps) > 0:
                opp_df = pd.DataFrame(
                    opps,
                    columns=[
                        "block_number",
                        "optimization_time",
                        "usd_profit",
                        "profit",
                        "tx_cost",
                        "tx_cost_usd",
                        "input",
                        "output",
                        "perc_diff",
                        "route",
                    ],
                )
                opp_df.to_csv(f"{DATA_DIR}/trades/{file}", index=False)
            start_10 = datetime.now().timestamp()

        if TIMING_RUN:
            start_state = datetime.now().timestamp()
        if current_block != row[0]:
            if current_block - (current_block % 20_00) != row[0] - (row[0] % 20_00):
                state = load_state(int(row[0]), DATA_DIR)
                ticks = load_ticks(int(row[0]), DATA_DIR)

            swap_base, tick_dict = load_all_swap_base(int(row[0]), state, ticks)
            current_block = row[0]
        if TIMING_RUN:
            state_load_time = datetime.now().timestamp() - start_state
            with open(f"../stats/state_load_time.txt", "a") as f:
                f.write(f"{state_load_time},\n")

        route_tuple = eval(row[2])
        base_route = route_tuple

        if not ANALYZE_DUPLICATE_OPPS:
            if TIMING_RUN:
                start_duplicate_scanner = datetime.now().timestamp()
            if route_tuple in last_block_routes:
                # print(f"Route {current_block}:\n{route_tuple}")
                for opp in last_saved_opps:
                    # print(f"{opp[9]}")
                    if opp[9] == route_tuple:
                        # print(f"Found duplicate opp: {opp}")
                        opps.append(
                            [
                                row[0],
                                opp[1],
                                opp[2],
                                opp[3],
                                opp[4],
                                opp[5],
                                opp[6],
                                opp[7],
                                opp[8],
                                opp[10],
                            ]
                        )
                        saved_opps.append(
                            [
                                row[0],
                                opp[1],
                                opp[2],
                                opp[3],
                                opp[4],
                                opp[5],
                                opp[6],
                                opp[7],
                                opp[8],
                                opp[9],
                                opp[10],
                            ]
                        )
                        block_routes.append(base_route)
                        analysed_opps += 1
                        break
                duplicate_opps += 1
                counter += 1
                if TIMING_RUN:
                    duplicate_scanner_time = datetime.now().timestamp() - start_duplicate_scanner
                    with open(f"../stats/duplicate_scanner_time.txt", "a") as f:
                        f.write(f"{duplicate_scanner_time},\n")
                continue

        if USE_SCORING:
            sc = score(current_block, row[1], route_tuple, state)
            if sc < SCORE_THRESHOLD:
                if not ANALYZE_DUPLICATE_OPPS:
                    block_routes.append(base_route)
                counter += 1
                continue

        analysed_opps += 1
        start_ternary = datetime.now().timestamp()
        profit, opt_in, out, route_tuple = ternary_search(
            current_block,
            route_tuple,
            swap_base,
            tick_dict,
            optimize_exchanges=True,
        )
        stop_ternary = datetime.now().timestamp()
        if TIMING_RUN:
            with open("../stats/ternary_times.txt", "a") as f:
                f.write(f"{stop_ternary - start_ternary:.4f},\n")

        if profit > 0:
            # get estimate for tx cost
            if TIMING_RUN:
                start_tx_cost = datetime.now().timestamp()
            cost_estimate = tx_cost(current_block, route_tuple, DATA_DIR)
            if TIMING_RUN:
                tx_cost_time = datetime.now().timestamp() - start_tx_cost
                with open(f"../stats/tx_cost_estimates.txt", "a") as f:
                    f.write(f"{tx_cost_time},\n")
            if TIMING_RUN:
                start_usd_est = datetime.now().timestamp()
            cost_estimate_usd = usd_value(current_block, "ETH", cost_estimate, swap_base)
            usd_profit = usd_value(current_block, route_tuple[0][0], profit, swap_base)
            if TIMING_RUN:
                usd_est_time = datetime.now().timestamp() - start_usd_est
                with open(f"../stats/usd_profit_estimates.txt", "a") as f:
                    f.write(f"{usd_est_time},\n")
            profit = profit * (10 ** -decimals[route_tuple[0][0]])
            profitable_opps += 1
            # get profit in full coins
            opps.append(
                [
                    row[0],
                    stop_ternary - start_ternary,
                    usd_profit,
                    profit,
                    # 0,
                    # 0,
                    cost_estimate,
                    cost_estimate_usd,
                    int(opt_in),
                    int(out),
                    (row[1] * 100),
                    route_tuple,
                ]
            )
            if not ANALYZE_DUPLICATE_OPPS:
                block_routes.append(base_route)
                # print(f"Appended route {current_block}: {route_tuple}")
                saved_opps.append(
                    [
                        row[0],
                        stop_ternary - start_ternary,
                        usd_profit,
                        profit,
                        # 0,
                        # 0,
                        cost_estimate,
                        cost_estimate_usd,
                        int(opt_in),
                        int(out),
                        (row[1] * 100),
                        base_route,
                        route_tuple,
                    ]
                )

        counter += 1

        if not ANALYZE_DUPLICATE_OPPS:
            if current_block != last_block_number:
                last_block_number = current_block
                last_block_routes = block_routes
                last_saved_opps = saved_opps
                saved_opps = []
                block_routes = []

        if TIMING_RUN:
            row_time = datetime.now().timestamp() - start_row
            with open(f"../stats/row_times.txt", "a") as f:
                f.write(f"{row_time},\n")

    if len(opps) > 0:
        opp_df = pd.DataFrame(
            opps,
            columns=[
                "block_number",
                "optimization_time",
                "usd_profit",
                "profit",
                "tx_cost",
                "tx_cost_usd",
                "input",
                "output",
                "perc_diff",
                "route",
            ],
        )
        opp_df.to_csv(f"{DATA_DIR}/trades/{file}", index=False)
    try:
        os.remove(f"{DATA_DIR}/trades/stats/0temp_{file}")
    except FileNotFoundError:
        pass

    stop_time = datetime.now().timestamp()
    return (
        analysed_opps,
        profitable_opps,
        duplicate_opps,
        counter - 1,
        int(file.split("_")[0]),
        stop_time - start_time,
    )


def analyze_opps_threaded():
    temp_file_name = f"temp_analysis_stats_1.csv"
    thread_pool = ThreadPoolExecutor(max_workers=8)
    THREADS = 2

    total_opps = 0
    analysed_opps = 0
    profitable_opps = 0
    duplicate_opps = 0
    analysis_stats = []

    try:
        stats = pd.read_csv(f"{DATA_DIR}/stats/{temp_file_name}")
    except Exception as e:
        print(f"No temporary analysis stats file found: {e}")
        stats = pd.DataFrame(
            columns=[
                "base_block",
                "analysed_opps",
                "profitable_opps",
                "duplicate_opps",
                "total_opps",
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
                    int(row["duplicate_opps"]),
                    int(row["total_opps"]),
                    round(float(row["time"]), 4),
                    round(float(row["total_time"]), 4),
                ]
            )
        print(f"Loaded {len(analysis_stats)} analysis stats")
        start_block = stats.iloc[-1]["base_block"] + 200
        start_time -= stats.iloc[-1]["total_time"]
        print(f"Starting analysis from block {start_block}")
        print(f"Time passed: {datetime.now().timestamp() - start_time}")
    else:
        start_block = 0

    files = sorted(os.listdir(f"{DATA_DIR}/opps"))

    for i in range(0, len(files), THREADS):

        futures = []
        start_threads = datetime.now().timestamp()
        for j in range(i, i + THREADS):
            if j >= len(files):
                break
            if int(files[j].split("_")[0]) < start_block:
                continue
            futures.append(thread_pool.submit(analyze_opps_file, files[j]))

        print(f"All threads submitted: {THREADS} working on {i}/{len(files)}")
        for f in futures:
            (
                temp_analysed_opps,
                temp_profitable_opps,
                temp_duplicate_opps,
                temp_total_opps,
                base_block,
                thread_time,
            ) = f.result()
            if temp_analysed_opps != -1:
                total_opps += temp_analysed_opps + temp_total_opps
                analysed_opps += temp_analysed_opps
                profitable_opps += temp_profitable_opps
                duplicate_opps += temp_duplicate_opps
                analysis_stats.append(
                    [
                        base_block,
                        temp_analysed_opps,
                        temp_profitable_opps,
                        temp_duplicate_opps,
                        temp_total_opps,
                        thread_time,
                        round(datetime.now().timestamp() - start_time, 4),
                    ]
                )
        stop_threads = datetime.now().timestamp()
        print(f"All threads finished in {stop_threads - start_threads}")
        pd.DataFrame(
            analysis_stats,
            columns=[
                "base_block",
                "analysed_opps",
                "profitable_opps",
                "duplicate_opps",
                "total_opps",
                "time",
                "total_time",
            ],
        ).to_csv(f"{DATA_DIR}/stats/{temp_file_name}", index=False)

    print(f"Total opps: {total_opps}")
    print(f"Analysed opps: {analysed_opps}")
    print(f"Total time: {datetime.now().timestamp() - start_time}")
    pd.DataFrame(
        analysis_stats,
        columns=[
            "base_block",
            "analysed_opps",
            "profitable_opps",
            "duplicate_opps",
            "total_opps",
            "time",
            "total_time",
        ],
    ).to_csv(
        f"{DATA_DIR}/stats/analysis_stats_{datetime.now().strftime('%H_%M_%S__%d_%m_%Y')}.csv",
        index=False,
    )


if __name__ == "__main__":
    analyze_opps_threaded()
