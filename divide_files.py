import os

import pandas as pd

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block

OLD_SIZE = 20_000
NEW_SIZE = 2_000

# make new files for state
for pool_name in uniswapV2.pool_names:
    if not os.path.exists(f"../data/state/{pool_name}"):
        os.mkdir(f"../data/state/{pool_name}")

    for file in sorted(os.listdir(f"../data/state_{OLD_SIZE}/{pool_name}")):
        print(f"Working on {pool_name}: {file}")
        file_start_block = int(file.split("_")[0])
        for base_block in range(file_start_block, file_start_block + OLD_SIZE, NEW_SIZE):
            df = pd.read_csv(f"../data/state_{OLD_SIZE}/{pool_name}/{file}")
            df = df[df["block_number"] >= base_block]
            df = df[df["block_number"] < base_block + NEW_SIZE]
            if len(df) > 0:
                df.to_csv(
                    f"../data/state/{pool_name}/{base_block}_{base_block + NEW_SIZE - 1}.csv",
                    index=False,
                )
                
# make new files for ticks
for pool_name in uniswapV3.pool_names:
    if not os.path.exists(f"../data/ticks/{pool_name}"):
        os.mkdir(f"../data/ticks/{pool_name}")

    for file in sorted(os.listdir(f"../data/ticks_{OLD_SIZE}/{pool_name}")):
        print(f"Working on {pool_name}: {file}")
        file_start_block = int(file.split("_")[0])
        for base_block in range(file_start_block, file_start_block + OLD_SIZE, NEW_SIZE):
            if os.path.exists(
                f"../data/ticks/{pool_name}/{base_block}_{base_block + NEW_SIZE - 1}.csv"
            ):
                continue

            state = pd.read_csv(f"../data/ticks_{OLD_SIZE}/{pool_name}/{file}", low_memory=False)

            if len(state[state["block_number"] <= base_block + NEW_SIZE]) > 0:
                highest_block = state[state["block_number"] <= base_block + NEW_SIZE].iloc[-1][
                    "block_number"
                ]
                base_ticks = state[state["block_number"] == highest_block]

            df = state[state["block_number"] >= base_block]
            df = df[df["block_number"] < base_block + NEW_SIZE]
            if len(df) > 0:
                df.to_csv(
                    f"../data/ticks/{pool_name}/{base_block}_{base_block + NEW_SIZE - 1}.csv",
                    index=False,
                )
            else:
                if base_block + NEW_SIZE - 1 > creation_block[pool_name]:
                    new_ticks = []
                    for idx, row in base_ticks.iterrows():
                        new_ticks.append([base_block, row[1], row[2]])

                    new_df = pd.DataFrame(new_ticks, columns=["block_number", "tick", "liquidity"])
                    new_df.to_csv(
                        f"../data/ticks/{pool_name}/{base_block}_{base_block + NEW_SIZE - 1}.csv",
                        index=False,
                    )

# make new files for blocks
for file in sorted(os.listdir(f"../data/blocks_{OLD_SIZE}")):
    print(f"Working on {file}")
    file_start_block = int(file.split("_")[0])
    for base_block in range(file_start_block, file_start_block + OLD_SIZE, NEW_SIZE):
        df = pd.read_csv(f"../data/blocks_{OLD_SIZE}/{file}", low_memory=False)
        df = df[df["block_number"] >= base_block]
        df = df[df["block_number"] < base_block + NEW_SIZE]
        if len(df) > 0:
            df.to_csv(
                f"../data/blocks/{base_block}_{base_block + NEW_SIZE - 1}.csv",
                index=False,
            )
