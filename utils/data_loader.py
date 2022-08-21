import bisect
import os

import pandas as pd
import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block

DATA_BLOCK_SIZE = 2_000


def load_state(block_number, data_dir):
    data_base_block = block_number - block_number % DATA_BLOCK_SIZE
    state = {}
    for pool_name in uniswapV2.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            temp = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
            state[pool_name] = temp
    for pool_name in sushiswap.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            temp = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
            state[pool_name] = temp
    for pool_name in uniswapV3.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            temp = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
            state[pool_name] = temp
    return state


def load_ticks(block_number, data_dir):
    data_base_block = block_number - block_number % DATA_BLOCK_SIZE
    ticks = {}
    for pool_name in uniswapV3.pool_names:
        if os.path.exists(
            f"{data_dir}/ticks/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            temp = pd.read_csv(
                f"{data_dir}/ticks/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv",
                low_memory=False,
            )
            ticks[pool_name] = temp

    return ticks


def load_pool_dict(block_number, data_dir):
    data_base_block = block_number - block_number % DATA_BLOCK_SIZE
    pool_dict = {}

    for pool_name in uniswapV3.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            pool_dict[pool_name] = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
        else:
            pool_dict[pool_name] = pd.DataFrame(
                columns=["block_number", "liquidity", "sqrt_price", "tick"]
            )
    for pool_name in uniswapV2.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            pool_dict[pool_name] = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
        else:
            pool_dict[pool_name] = pd.DataFrame(columns=["block_number", "reserve_0", "reserve_1"])
    for pool_name in sushiswap.pool_names:
        if os.path.exists(
            f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        ):
            pool_dict[pool_name] = pd.read_csv(
                f"{data_dir}/state/{pool_name}/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
            )
        else:
            pool_dict[pool_name] = pd.DataFrame(columns=["block_number", "reserve_0", "reserve_1"])

    return pool_dict


def build_state(block_number, pool_dict):
    state = {}

    # handle all V3 pools
    for pool_name in uniswapV3.pool_names:
        # do not consider pool that were not initialized at the current block
        if creation_block[pool_name] > block_number:
            continue
        idx = bisect.bisect(pool_dict[pool_name]["block_number"], block_number) - 1
        state[pool_name] = pool_dict[pool_name].iloc[idx]
    # handle uniswapV2 pools
    for pool_name in uniswapV2.pool_names:
        if creation_block[pool_name] > block_number:
            continue
        idx = bisect.bisect(pool_dict[pool_name]["block_number"], block_number) - 1
        state[pool_name] = pool_dict[pool_name].iloc[idx]
    # handle sushiswap pools
    for pool_name in sushiswap.pool_names:
        if creation_block[pool_name] > block_number:
            continue
        idx = bisect.bisect(pool_dict[pool_name]["block_number"], block_number) - 1
        state[pool_name] = pool_dict[pool_name].iloc[idx]
    return state


def load_swap_base_v3(pool_name, block_number, state, ticks):
    tick_dict = {}
    temp_state = state[pool_name]
    idx = bisect.bisect(temp_state["block_number"].values, block_number) - 1
    current_state = temp_state.iloc[idx]

    if ticks is not None:
        if len(ticks[pool_name]) != 0 and block_number >= creation_block[pool_name]:
            for t in ticks[pool_name][ticks[pool_name]["block_number"] <= block_number][
                -1:
            ].iterrows():
                row = t[1]
                if tick_dict.get(pool_name) is None:
                    tick_dict[pool_name] = {}
                tick_dict[pool_name][row["tick"]] = int(row["liquidity"])

    return current_state, tick_dict


def load_swap_base_v2(pool_name, block_number, state):
    temp_state = state[pool_name]
    idx = bisect.bisect(temp_state["block_number"].values, block_number) - 1
    current_state = temp_state.iloc[idx]

    return current_state


def load_all_swap_base(block_number, state, ticks):
    swap_base = {}
    tick_dict = {}
    for pool_name in uniswapV3.pool_names:
        if (
            block_number - (block_number % DATA_BLOCK_SIZE) + DATA_BLOCK_SIZE
            > creation_block[pool_name]
        ):
            swap_base[pool_name], tick_dict[pool_name] = load_swap_base_v3(
                pool_name, block_number, state, ticks
            )
    for pool_name in uniswapV2.pool_names:
        if (
            block_number - (block_number % DATA_BLOCK_SIZE) + DATA_BLOCK_SIZE
            > creation_block[pool_name]
        ):
            swap_base[pool_name] = load_swap_base_v2(pool_name, block_number, state)
    for pool_name in sushiswap.pool_names:
        if (
            block_number - (block_number % DATA_BLOCK_SIZE) + DATA_BLOCK_SIZE
            > creation_block[pool_name]
        ):
            swap_base[pool_name] = load_swap_base_v2(pool_name, block_number, state)
    return swap_base, tick_dict


def load_block(
    block_number,
    data_dir,
    from_data=False,
    blocks=None,
):
    if from_data:
        idx = bisect.bisect(blocks["block_number"].values, block_number) - 1
        block = blocks.iloc[idx]
        return block
    else:
        data_base_block = block_number - (block_number % DATA_BLOCK_SIZE)
        df = pd.read_csv(
            f"{data_dir}/blocks/{data_base_block}_{data_base_block+DATA_BLOCK_SIZE-1}.csv"
        )

        idx = bisect.bisect(df["block_number"].values, block_number) - 1
        block = df.iloc[idx]
        return block, df
