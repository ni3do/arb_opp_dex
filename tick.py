import os

import pandas as pd
from web3 import Web3

import pool_info.uniswapV3
from analyze_opps import NODE_URL

NODE_URL = "http://localhost:8545/"
# NODE_URL = "https://api.archivenode.io/1984d43d-2a06-46a7-a92c-502328356b6f"
w3 = Web3(Web3.HTTPProvider(NODE_URL))


def save_init_ticks():
    files = os.listdir(f"../data/uniswapV3")
    files.sort()
    liq_dict = {}
    for file in files:
        for pool_name in sorted(pool_info.uniswapV3.pool_names):
            if not os.path.exists(f"../data/ticks/{pool_name}"):
                os.mkdir(f"../data/ticks/{pool_name}")

            if os.path.exists(f"../data/ticks/{pool_name}/{file}"):
                continue

            print(f"Working on {pool_name}: {file}")

            contract = w3.eth.contract(
                address=pool_info.uniswapV3.pools[pool_name], abi=pool_info.uniswapV3.ABI
            )

            block_before = int(file.split("_")[0])

            block_after = int(file.split("_")[1].split(".")[0])

            liqArr = []
            block_liq = {}
            if liq_dict.get(pool_name) is not None:
                for tick in liq_dict[pool_name]:
                    # print(f"Fetching tick {tick} on block {block_before}")
                    liq = contract.functions.ticks(int(tick)).call(
                        block_identifier=int(block_before)
                    )[1]
                    block_liq[tick] = liq
                    liqArr.append([block_before, tick, liq])

            mentioned_ticks = []
            current_block = 0

            state = pd.read_csv(f"../data/uniswapV3/{file}")
            state.sort_values(by=["block_number", "transaction_index"], inplace=True)
            state.reset_index(drop=True, inplace=True)

            for idx, row in state.iterrows():
                if row["address"] == pool_info.uniswapV3.pools[pool_name]:
                    if current_block == 0:
                        current_block = row["block_number"]
                    if current_block != row["block_number"]:
                        for tick in mentioned_ticks:
                            # print(f"Fetching tick {tick} on block {current_block}")
                            liq = contract.functions.ticks(int(tick)).call(
                                block_identifier=int(current_block)
                            )[1]
                            block_liq[tick] = liq
                        for tick in block_liq:
                            liqArr.append([current_block, tick, block_liq[tick]])

                        mentioned_ticks = []
                        current_block = row["block_number"]

                    decoded_data = eval(row["decoded_data"])
                    if row["event_name"] == "Mint":
                        if decoded_data["tickLower"] not in mentioned_ticks:
                            mentioned_ticks.append(decoded_data["tickLower"])
                        if decoded_data["tickUpper"] not in mentioned_ticks:
                            mentioned_ticks.append(decoded_data["tickUpper"])
                    elif row["event_name"] == "Burn":
                        if decoded_data["tickLower"] not in mentioned_ticks:
                            mentioned_ticks.append(decoded_data["tickLower"])
                        if decoded_data["tickUpper"] not in mentioned_ticks:
                            mentioned_ticks.append(decoded_data["tickUpper"])

            for tick in mentioned_ticks:
                liq = contract.functions.ticks(tick).call(block_identifier=int(current_block))[1]
                if liq != 0:
                    block_liq[tick] = liq
            for tick in block_liq:
                liqArr.append([current_block, tick, block_liq[tick]])

            df = pd.DataFrame(liqArr, columns=["block_number", "tick", "liquidity"])
            df.sort_values(by=["block_number", "tick"], inplace=True)
            df.drop_duplicates(subset=["block_number", "tick"], keep="first", inplace=True)
            df.to_csv(f"../data/ticks/{pool_name}/{file}", index=False)

            liq_dict[pool_name] = block_liq


if __name__ == "__main__":
    save_init_ticks()
