import json
import os
import random

import pandas as pd
from numpy import median, std

import pool_info.uniswapV3 as uniswapV3
from optimal_swap import router
from utils.data_loader import load_state, load_ticks

DATA_DIR = os.path.abspath(f"../data")


def simulate_swaps(simulations):
    # df = pd.read_csv(f"../swap_tests/swaps.csv")
    diff_arr = []

    files = sorted(os.listdir(f"{DATA_DIR}/uniswapV3"))

    sim_counter = 0
    while sim_counter < simulations:
        file = random.choice(files)
        df = pd.read_csv(f"{DATA_DIR}/uniswapV3/{file}")
        pool_name = random.choice(uniswapV3.pool_names)
        pool_address = uniswapV3.pools[pool_name]
        idx = random.randint(0, len(df) - 1)
        event = df.iloc[idx]

        # for idx, row in df.iterrows():
        # event = row
        if event["event_name"] == "Swap":
            block_number = event["block_number"]
            pool_address = event["address"]
            if pool_address in uniswapV3.pools.values():
                pool_name = ""
                for pn in uniswapV3.pool_names:
                    if uniswapV3.pools[pn] == pool_address:
                        pool_name = pn
                        break
                decoded_data = eval(event["decoded_data"])
                if decoded_data["amount0"] > 0:
                    amount_in = int(decoded_data["amount0"])
                    chain_out = int(decoded_data["amount1"]) * -1
                    route = [
                        (
                            pool_name.split("_")[0],
                            pool_name.split("_")[1],
                            pool_name.split("_")[2],
                        )
                    ]
                else:
                    amount_in = int(decoded_data["amount1"])
                    chain_out = int(decoded_data["amount0"]) * -1
                    route = [
                        (
                            pool_name.split("_")[1],
                            pool_name.split("_")[0],
                            pool_name.split("_")[2],
                        )
                    ]

                state = load_state(block_number, DATA_DIR)
                ticks = load_ticks(block_number, DATA_DIR)
                sim_out = router(block_number, route, amount_in, state, ticks)
                perc_diff = abs(sim_out - chain_out) / chain_out
                diff_arr.append(perc_diff)
                sim_counter += 1

                if perc_diff > 0.01:
                    with open(f"../swap_tests/bidg_diff.txt", "a") as f:
                        f.write(f"---------------------------------------\n")
                        f.write(f"{pool_name} Block: {block_number}\n")
                        f.write(
                            f"Tx: https://etherscan.io/tx/0x{eval(event['transaction_hash']).hex()}\n"
                        )
                        f.write(f"dec data:\n{json.dumps(decoded_data)}\n")
                        f.write(f"amount_in:    {amount_in}\n")
                        f.write(f"chain out:    {chain_out}\n")
                        f.write(f"sim out:      {sim_out}\n")
                        f.write(f"diff:         {perc_diff}\n")
                if sim_counter % 1 == 0:
                    if len(diff_arr) > 0:
                        # print(diff_arr)
                        print(f"---------------------------------")
                        print(f"Simulation {sim_counter}/{simulations}")
                        print(f"Median difference:  {median(diff_arr):.8f}")
                        print(f"Std deviation:      {std(diff_arr):.8f}")
                        print(f"Average difference: {sum(diff_arr) / len(diff_arr):.8f}")
                        print(f"Max difference:     {max(diff_arr):.8f}")
                        print(f"Min difference:     {min(diff_arr):.8f}")

                        with open(f"../swap_tests/swap_sim_temp.txt", "w") as f:
                            f.write(f"Simulation {sim_counter}/{simulations}\n")
                            f.write(f"Median difference:  {median(diff_arr):.8f}\n")
                            f.write(f"Std deviation:      {std(diff_arr):.8f}\n")
                            f.write(f"Average difference: {sum(diff_arr) / len(diff_arr):.8f}\n")
                            f.write(f"Max difference:     {max(diff_arr):.8f}\n")
                            f.write(f"Min difference:     {min(diff_arr):.8f}\n")
                            f.write(f"Diff_arr:\n{json.dumps(diff_arr, indent=2)}")
        # sim_counter = simulations

    with open(f"../swap_tests/bidg_diff.txt", "a") as f:
        f.write(
            f"---------------------------------------------------------------------------------------------------------------------\n"
        )
        f.write(
            f"---------------------------------------------------------------------------------------------------------------------\n"
        )
    with open(f"../swap_tests/swap_sim{simulations}.txt", "w") as f:
        f.write(f"Simulation {sim_counter}/{simulations}\n")
        f.write(f"Median difference:  {median(diff_arr):.8f}\n")
        f.write(f"Std deviation:      {std(diff_arr):.8f}\n")
        f.write(f"Average difference: {sum(diff_arr) / len(diff_arr):.8f}\n")
        f.write(f"Max difference:     {max(diff_arr):.8f}\n")
        f.write(f"Min difference:     {min(diff_arr):.8f}\n")
        f.write(f"Diff_arr:\n{json.dumps(diff_arr, indent=2)}")


if __name__ == "__main__":
    simulate_swaps(1001)
