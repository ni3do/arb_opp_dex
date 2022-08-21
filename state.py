import os
import sys

import pandas as pd
from web3 import Web3

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block

NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 20}))


def v3_state():
    last_state = {}

    files = os.listdir(f"../data/uniswapV3")
    files.sort()

    for file in files:
        if file.endswith(".csv"):
            events = pd.read_csv(f"../data/uniswapV3/{file}")

            counter = 0
            for pool_name in uniswapV3.pool_names:
                if os.path.exists(f"../data/state/{pool_name}/{file}"):
                    continue

                counter += 1

                pool_events = events[events["address"] == uniswapV3.pools[pool_name]]
                contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)

                if int(file.split("_")[0]) < creation_block[pool_name]:
                    base_block = creation_block[pool_name]
                    if int(file.split("_")[1].split(".")[0]) < creation_block[pool_name]:
                        print(
                            f"{counter}/{len(uniswapV3.pool_names)} {pool_name} is not created yet"
                        )
                        continue
                else:
                    base_block = int(file.split("_")[0])
                state = [
                    [
                        base_block,
                        contract.functions.liquidity().call(block_identifier=base_block),
                        contract.functions.slot0().call(block_identifier=base_block)[0],
                        contract.functions.slot0().call(block_identifier=base_block)[1],
                    ]
                ]
                saved_blocks = []

                for idx, event in pool_events.iterrows():
                    if event["block_number"] not in saved_blocks:
                        saved_blocks.append(event["block_number"])

                        liquidity = contract.functions.liquidity().call(
                            block_identifier=event["block_number"]
                        )
                        slot0 = contract.functions.slot0().call(
                            block_identifier=event["block_number"]
                        )

                        state.append([event["block_number"], liquidity, slot0[0], slot0[1]])

                df = pd.DataFrame(
                    state, columns=["block_number", "liquidity", "sqrt_price", "tick"]
                )

                if not os.path.exists(f"../data/state/{pool_name}"):
                    os.makedirs(f"../data/state/{pool_name}")

                print(f"{counter}/{len(uniswapV3.pool_names)} {pool_name}: {file}")

                last_state[pool_name] = state[-1]

                df.to_csv(f"../data/state/{pool_name}/{file}", index=False)


def v2_state():
    last_state = {}
    files = os.listdir(f"../data/uniswapV2")
    files.sort()

    for file in files:
        if file.endswith(".csv"):
            events = pd.read_csv(f"../data/uniswapV2/{file}")

            counter = 0
            for pool_name in uniswapV2.pool_names:

                if os.path.exists(f"../data/state/{pool_name}/{file}"):
                    continue

                counter += 1
                pool_events = events[events["address"] == uniswapV2.pools[pool_name]]
                contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)

                if int(file.split("_")[0]) < creation_block[pool_name]:
                    base_block = creation_block[pool_name]
                    if int(file.split("_")[1].split(".")[0]) < creation_block[pool_name]:
                        print(
                            f"{counter}/{len(uniswapV3.pool_names)} {pool_name} is not created yet"
                        )
                        continue
                else:
                    base_block = int(file.split("_")[0])

                state = [
                    [
                        base_block,
                        contract.functions.getReserves().call(block_identifier=base_block)[0],
                        contract.functions.getReserves().call(block_identifier=base_block)[1],
                    ]
                ]
                saved_blocks = []

                for idx, event in pool_events.iterrows():
                    if event["block_number"] not in saved_blocks:
                        saved_blocks.append(event["block_number"])

                        reserves = contract.functions.getReserves().call(
                            block_identifier=event["block_number"]
                        )

                        state.append([event["block_number"], reserves[0], reserves[1]])

                df = pd.DataFrame(state, columns=["block_number", "reserve_0", "reserve_1"])

                if not os.path.exists(f"../data/state/{pool_name}"):
                    os.makedirs(f"../data/state/{pool_name}")

                print(f"{counter}/{len(uniswapV3.pool_names)} {pool_name}: {file}")

                last_state[pool_name] = state[-1]

                df.to_csv(f"../data/state/{pool_name}/{file}", index=False)

        counter = 0
        for pool_name in sushiswap.pool_names:
            counter += 1
            pool_events = events[events["address"] == sushiswap.pools[pool_name]]
            contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)

            if int(file.split("_")[0]) < creation_block[pool_name]:
                base_block = creation_block[pool_name]
                if int(file.split("_")[1].split(".")[0]) < creation_block[pool_name]:
                    print(f"{counter}/{len(uniswapV3.pool_names)} {pool_name} is not created yet")
                    continue
            else:
                base_block = int(file.split("_")[0])

            state = [
                [
                    base_block,
                    contract.functions.getReserves().call(block_identifier=base_block)[0],
                    contract.functions.getReserves().call(block_identifier=base_block)[1],
                ]
            ]
            saved_blocks = []

            for idx, event in pool_events.iterrows():
                if event["block_number"] not in saved_blocks:
                    saved_blocks.append(event["block_number"])

                    reserves = contract.functions.getReserves().call(
                        block_identifier=event["block_number"]
                    )

                    state.append([event["block_number"], reserves[0], reserves[1]])

            df = pd.DataFrame(state, columns=["block_number", "reserve_0", "reserve_1"])

            if not os.path.exists(f"../data/state/{pool_name}"):
                os.makedirs(f"../data/state/{pool_name}")

            print(f"{counter}/{len(uniswapV3.pool_names)} {pool_name}: {file}")

            last_state[pool_name] = state[-1]

            df.to_csv(f"../data/state/{pool_name}/{file}", index=False)


def fill_state_gaps():
    pools = os.listdir(f"../data/state")
    pools.sort()

    for pool_name in pools:
        if (
            pool_name not in uniswapV3.pool_names
            and pool_name not in sushiswap.pool_names
            and pool_name not in uniswapV2.pool_names
        ):
            continue

        print(f"Working on {pool_name}")
        if pool_name in uniswapV3.pool_names:
            contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)
        elif pool_name in uniswapV2.pool_names:
            contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)
        elif pool_name in sushiswap.pool_names:
            contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)

        files = os.listdir(f"../data/state/{pool_name}")
        files.sort()

        for file in files:
            print(f"Working on {file}")
            state = pd.read_csv(f"../data/state/{pool_name}/{file}")

            start_block = int(file.split("_")[0])
            end_block = int(file.split("_")[1].split(".")[0])

            if start_block < creation_block[pool_name]:
                start_block = creation_block[pool_name] + (100 - (creation_block[pool_name] % 100))
                print(f"Adjusted start block to {start_block}")
            add_state = []

            for block_number in range(start_block, end_block + 1, 100):
                if pool_name in uniswapV3.pool_names:
                    slot0 = contract.functions.slot0().call(block_identifier=block_number)
                    add_state.append(
                        [
                            block_number,
                            contract.functions.liquidity().call(block_identifier=block_number),
                            slot0[0],
                            slot0[1],
                        ]
                    )
                else:
                    reserves = contract.functions.getReserves().call(block_identifier=block_number)
                    add_state.append(
                        [
                            block_number,
                            reserves[0],
                            reserves[1],
                        ]
                    )
            print(f"Adding {len(add_state)} rows")
            if pool_name in uniswapV3.pool_names:
                df = pd.concat(
                    [
                        state,
                        pd.DataFrame(
                            add_state,
                            columns=["block_number", "liquidity", "sqrt_price", "tick"],
                        ),
                    ],
                    ignore_index=True,
                )
                df.sort_values(by=["block_number"], inplace=True)
                df.drop_duplicates(subset=["block_number"], keep="last", inplace=True)

                df.to_csv(f"../data/state/{pool_name}/{file}", index=False)
            else:
                df = pd.concat(
                    [
                        state,
                        pd.DataFrame(
                            add_state,
                            columns=["block_number", "reserve_0", "reserve_1"],
                        ),
                    ],
                    ignore_index=True,
                )
                df.sort_values(by=["block_number"], inplace=True)
                df.drop_duplicates(subset=["block_number"], keep="last", inplace=True)

                df.to_csv(f"../data/state/{pool_name}/{file}", index=False)


if __name__ == "__main__":
    # v2_state()
    # v3_state()
    fill_state_gaps()
