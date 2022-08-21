import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from web3 import Web3

import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
import utils

NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL))

thread_pool = ThreadPoolExecutor(max_workers=16)

# Constants
LONDON_HARDFORK_BLOCK = 12_965_000
SWAP_TOPIC_V3 = "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"
BURN_TOPIC_V3 = "0x0c396cd989a39f4459b5fa1aed6a9a8dcdbc45908acfd67e028cd568da98982c"
MINT_TOPIC_V3 = "0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"
SWAP_TOPIC_V2 = "0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822"
BURN_TOPIC_V2 = "0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496"
MINT_TOPIC_V2 = "0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f"

# 01.06.21
START_BLOCK = 12_000_000
END_BLOCK = 14_800_000
STEP_SIZE = 1000
THREADS = 10
STEPS_UNTIL_SAFE = 2


def get_events_V3(start_block, end_block):
    events = []
    logs = w3.eth.get_logs(
        {
            "fromBlock": int(start_block),
            "toBlock": int(end_block),
            # fetch events for all topics
            "topics": [[SWAP_TOPIC_V3, MINT_TOPIC_V3, BURN_TOPIC_V3]],
        }
    )

    for log in logs:
        # compare topics to know which event we have
        if log.topics[0].hex() == SWAP_TOPIC_V3:
            func_abi = uniswapV3.ABI[9]
            event_name = "Swap"
        if log.topics[0].hex() == MINT_TOPIC_V3:
            func_abi = uniswapV3.ABI[7]
            event_name = "Mint"
        if log.topics[0].hex() == BURN_TOPIC_V3:
            func_abi = uniswapV3.ABI[1]
            event_name = "Burn"

        if len(bytes.fromhex(log["data"][2:])) == 0:
            # print(f"No data for {event_name}")
            # print(log)
            continue
        try:
            decoded_data = utils.decode_event_data(func_abi, log)
        except Exception as e:
            # print(f"decoding data failed: {e}")
            # print(log)
            continue

        # decode data field of event
        decoded_data = utils.decode_event_data(func_abi, log)

        events.append(
            [
                log.blockNumber,
                log.address,
                event_name,
                [topic.hex() for topic in log.topics],
                log.data,
                decoded_data,
                log.transactionHash,
                log.transactionIndex,
                log.logIndex,
            ]
        )
    return events


def get_events_V2(start_block, end_block):
    events = []
    logs = w3.eth.get_logs(
        {
            "fromBlock": int(start_block),
            "toBlock": int(end_block),
            # fetch events for all topics
            "topics": [[SWAP_TOPIC_V2, MINT_TOPIC_V2, BURN_TOPIC_V2]],
        }
    )

    for log in logs:
        # compare topics to know which event we have
        if log["topics"][0].hex() == SWAP_TOPIC_V2:
            func_abi = uniswapV2.ABI[4]
            event_name = "Swap"
        elif log["topics"][0].hex() == MINT_TOPIC_V2:
            func_abi = uniswapV2.ABI[3]
            event_name = "Mint"
        elif log["topics"][0].hex() == BURN_TOPIC_V2:
            func_abi = uniswapV2.ABI[2]
            event_name = "Burn"
        else:
            print("No topic match")
            print(log["topics"][0].hex())
            print(log)

        if len(bytes.fromhex(log["data"][2:])) == 0:
            # print(f"No data for {event_name}")
            # print(log)
            continue
        try:
            decoded_data = utils.decode_event_data(func_abi, log)
        except Exception as e:
            # print(f"decoding data failed: {e}")
            # print(log)
            continue

        events.append(
            [
                log.blockNumber,
                log.address,
                event_name,
                [topic.hex() for topic in log.topics],
                log.data,
                decoded_data,
                log.transactionHash,
                log.transactionIndex,
                log.logIndex,
            ]
        )

    return events


if __name__ == "__main__":

    events_V2 = []
    events_V3 = []

    saving_counter = 0

    if not os.path.exists("../data/uniswapV2"):
        os.makedirs("../data/uniswapV2")
    if not os.path.exists("../data/uniswapV3"):
        os.makedirs("../data/uniswapV3")

    for i in range(START_BLOCK, END_BLOCK, THREADS * STEP_SIZE):

        futures_V2 = []
        futures_V3 = []

        for j in range(THREADS):
            futures_V2.append(
                thread_pool.submit(
                    get_events_V2, i + j * STEP_SIZE, i + (((j + 1) * STEP_SIZE) - 1)
                )
            )
            futures_V3.append(
                thread_pool.submit(
                    get_events_V3, i + j * STEP_SIZE, i + (((j + 1) * STEP_SIZE) - 1)
                )
            )

        if saving_counter >= STEPS_UNTIL_SAFE:
            if len(events_V2) > 0:
                print(f"Saving blocks V2: {i - (STEPS_UNTIL_SAFE * THREADS * STEP_SIZE)} to {i-1}")
                df = pd.DataFrame(
                    events_V2,
                    columns=[
                        "block_number",
                        "address",
                        "event_name",
                        "topics",
                        "data",
                        "decoded_data",
                        "transaction_hash",
                        "transaction_index",
                        "log_index",
                    ],
                )
                df.sort_values(by=["block_number"], inplace=True)
                # df.drop_duplicates(subset=["block_number"], inplace=True)
                df.to_csv(
                    f"../data/uniswapV2/{i-(STEPS_UNTIL_SAFE * THREADS*STEP_SIZE)}_{i-1}.csv",
                    index=False,
                )
            else:
                print(f"No events V2: {i - (STEPS_UNTIL_SAFE * THREADS * STEP_SIZE)} to {i-1}")
            events_V2 = []

            if len(events_V3) > 0:
                print(f"Saving blocks V3: {i - (STEPS_UNTIL_SAFE * THREADS * STEP_SIZE)} to {i-1}")
                df = pd.DataFrame(
                    events_V3,
                    columns=[
                        "block_number",
                        "address",
                        "event_name",
                        "topics",
                        "data",
                        "decoded_data",
                        "transaction_hash",
                        "transaction_index",
                        "log_index",
                    ],
                )
                df.sort_values(by=["block_number"], inplace=True)
                # df.drop_duplicates(subset=["block_number", "address", "transaction_index"], inplace=True)
                df.to_csv(
                    f"../data/uniswapV3/{i-(STEPS_UNTIL_SAFE * THREADS * STEP_SIZE)}_{i-1}.csv",
                    index=False,
                )
            else:
                print(f"No events V3: {i - (STEPS_UNTIL_SAFE * THREADS * STEP_SIZE)} to {i-1}")
            events_V3 = []

            saving_counter = 0

        saving_counter += 1

        for future in futures_V2:
            events_V2 += future.result()

        for future in futures_V3:
            events_V3 += future.result()
