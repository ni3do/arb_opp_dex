import os

import pandas as pd
from web3 import Web3

LONDON_HARDFORK_BLOCK = 12_965_000
DATA_DIR = "../data"

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 120}))


def gas_prices(start_block, end_block):
    base_block = start_block - (start_block % 20_000)

    rows = []
    print(f"Working on {start_block}_{start_block-(start_block%20_000) + 19_999}")
    for current_block in range(start_block, end_block):
        if os.path.exists(
            f"{DATA_DIR}/blocks/{current_block - (current_block % 20_000)}_{current_block - (current_block % 20_000) + 19_999}.csv"
        ):
            print(
                f"Skipping, already existing file: {current_block - (current_block % 20_000)}_{current_block - (current_block % 20_000) + 19_999}.csv"
            )
            continue
        if current_block % 5_000 == 0:
            print(f"{current_block}/{current_block-(current_block%20_000)+19_999}")
        if base_block != current_block - (current_block % 20_000):

            df = pd.DataFrame(
                rows,
                columns=[
                    "block_number",
                    "gas_price",
                    "gas_limit",
                    "gas_used",
                    "transactions",
                    "timestamp",
                    "miner",
                ],
            )
            df.sort_values(by=["block_number"], inplace=True)
            df.drop_duplicates(subset=["block_number"], keep="first", inplace=True)
            df.to_csv(f"{DATA_DIR}/blocks/{base_block}_{base_block+19_999}.csv", index=False)

            base_block = current_block - (current_block % 20_000)
            print(f"Working on {base_block}_{base_block+19_999}")

            rows = []

        if current_block < LONDON_HARDFORK_BLOCK:
            block = w3.eth.get_block(current_block)

            gas_price = 0
            samples = 4
            for i in range(0, samples):
                try:
                    tx = w3.eth.getTransaction(block.transactions[i])
                    gas_price += tx.gasPrice
                except IndexError as IE:
                    # print(f"Error: {IE}")
                    if samples != 1:
                        samples -= 1
                    continue
            gas_price /= samples
        else:
            block = w3.eth.get_block(current_block)
            gas_price = block["baseFeePerGas"]
        rows.append(
            [
                block["number"],
                gas_price,
                block["gasLimit"],
                block["gasUsed"],
                len(block["transactions"]),
                block["timestamp"],
                block["miner"],
            ]
        )


if __name__ == "__main__":
    gas_prices(start_block=12_000_000, end_block=14_600_000)
