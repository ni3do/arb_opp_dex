import json
import os
import time

from web3 import Web3

import pool_info.erc20 as erc20
import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block
from pool_info.decimal_deltas import decimal_deltas
from utils.decode import decode_event_data

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 20}))

TIMEOUT_AFTER_CALL = 0

V2_POOL_CREATION_TOPIC = "0x0d3648bd0f6ba80134a33ba9275ac585d9d315f0ad8355cddefde31afa28d0e9"
V3_POOL_CREATION_TOPIC = "0x783cca1c0412dd0d695e784568c96da2e9c22ff989357a2e8b1d9b2b4e6b7118"
SUSHI_FACTORY_ADDRESS = "0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac"
UNISWAP_V2_FACTORY = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
UNISWAP_V3_FACTORY = "0x1F98431c8aD98523631AE4a59f267346ea31F984"

pair_creation_abi = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "address", "name": "token0", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "token1", "type": "address"},
        {"indexed": False, "internalType": "address", "name": "pair", "type": "address"},
        {"indexed": False, "internalType": "uint256", "name": "", "type": "uint256"},
    ],
    "name": "PairCreated",
    "type": "event",
}
pool_creation_abi = {
    "anonymous": False,
    "inputs": [
        {"indexed": True, "internalType": "address", "name": "token0", "type": "address"},
        {"indexed": True, "internalType": "address", "name": "token1", "type": "address"},
        {"indexed": True, "internalType": "uint24", "name": "fee", "type": "uint24"},
        {"indexed": False, "internalType": "int24", "name": "tickSpacing", "type": "int24"},
        {"indexed": False, "internalType": "address", "name": "pool", "type": "address"},
    ],
    "name": "PoolCreated",
    "type": "event",
}


def decimals():
    decimals = {}
    decimal_dict = decimal_deltas

    for pool_name in uniswapV2.pool_names:
        pool_contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)
        token0 = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1 = w3.toChecksumAddress(pool_contract.functions.token1().call())

        token0_contract = w3.eth.contract(address=token0, abi=erc20.ABI)
        token1_contract = w3.eth.contract(address=token1, abi=erc20.ABI)

        decimals0 = token0_contract.functions.decimals().call()
        decimals1 = token1_contract.functions.decimals().call()

        ticker0 = token0_contract.functions.symbol().call()
        ticker1 = token1_contract.functions.symbol().call()

        decimals[ticker0] = decimals0
        decimals[ticker1] = decimals1

        decimal_delta = decimals0 - decimals1
        decimal_dict[pool_name] = decimal_delta

        time.sleep(TIMEOUT_AFTER_CALL)

    for pool_name in uniswapV3.pool_names:
        pool_contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)
        token0 = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1 = w3.toChecksumAddress(pool_contract.functions.token1().call())

        token0_contract = w3.eth.contract(address=token0, abi=erc20.ABI)
        token1_contract = w3.eth.contract(address=token1, abi=erc20.ABI)

        decimals0 = token0_contract.functions.decimals().call()
        decimals1 = token1_contract.functions.decimals().call()

        ticker0 = token0_contract.functions.symbol().call()
        ticker1 = token1_contract.functions.symbol().call()

        decimals[ticker0] = decimals0
        decimals[ticker1] = decimals1

        decimal_delta = decimals0 - decimals1
        decimal_dict[pool_name] = decimal_delta

        time.sleep(TIMEOUT_AFTER_CALL)

    for pool_name in sushiswap.pool_names:
        pool_contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)
        token0 = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1 = w3.toChecksumAddress(pool_contract.functions.token1().call())

        token0_contract = w3.eth.contract(address=token0, abi=erc20.ABI)
        token1_contract = w3.eth.contract(address=token1, abi=erc20.ABI)

        decimals0 = token0_contract.functions.decimals().call()
        decimals1 = token1_contract.functions.decimals().call()

        ticker0 = token0_contract.functions.symbol().call()
        ticker1 = token1_contract.functions.symbol().call()

        decimals[ticker0] = decimals0
        decimals[ticker1] = decimals1

        decimal_delta = decimals0 - decimals1
        decimal_dict[pool_name] = decimal_delta

        time.sleep(TIMEOUT_AFTER_CALL)

    with open("pool_info/decimal_deltas.py", "w") as f:
        f.write("decimal_deltas = ")
        f.write(json.dumps(decimal_dict, indent=4, sort_keys=True))

    decimals["ETH"] = 18
    with open("pool_info/decimals.py", "w") as f:
        f.write("decimals = ")
        f.write(json.dumps(decimals, indent=4, sort_keys=True))


def coin_list():
    coins = []
    coins_V3 = []
    coins_V2 = []
    coins_sushi = []
    coin_address = {}

    for pool_name in uniswapV3.pool_names:
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        pool_contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)
        token0_address = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1_address = w3.toChecksumAddress(pool_contract.functions.token1().call())

        coin_address[token0] = token0_address
        coin_address[token1] = token1_address

        if token0 not in coins_V3:
            coins_V3.append(token0)
        if token1 not in coins_V3:
            coins_V3.append(token1)
        if token0 not in coins:
            coins.append(token0)
        if token1 not in coins:
            coins.append(token1)

    for pool_name in uniswapV2.pool_names:
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        pool_contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)
        token0_address = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1_address = w3.toChecksumAddress(pool_contract.functions.token1().call())

        coin_address[token0] = token0_address
        coin_address[token1] = token1_address

        if token0 not in coins_V2:
            coins_V2.append(token0)
        if token1 not in coins_V2:
            coins_V2.append(token1)
        if token0 not in coins:
            coins.append(token0)
        if token1 not in coins:
            coins.append(token1)

    for pool_name in sushiswap.pool_names:
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        pool_contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)
        token0_address = w3.toChecksumAddress(pool_contract.functions.token0().call())
        token1_address = w3.toChecksumAddress(pool_contract.functions.token1().call())

        coin_address[token0] = token0_address
        coin_address[token1] = token1_address

        if token0 not in coins_sushi:
            coins_sushi.append(token0)
        if token1 not in coins_sushi:
            coins_sushi.append(token1)
        if token0 not in coins:
            coins.append(token0)
        if token1 not in coins:
            coins.append(token1)

    coins.sort()
    coins_sushi.sort()
    coins_V2.sort()
    coins_V3.sort()

    f = open("pool_info/coins.py", "w")
    f.write(
        "coins = "
        + json.dumps(coins, indent=4)
        + "\ncoins_V3 = "
        + json.dumps(coins_V3, indent=4)
        + "\ncoins_V2 = "
        + json.dumps(coins_V2, indent=4)
        + "\ncoins_sushi = "
        + json.dumps(coins_sushi, indent=4)
        + "\ncoin_address = "
        + json.dumps(coin_address, indent=4)
    )


def tick_spacing():
    spaces = {}
    for pool_name in uniswapV3.pool_names:
        contract = w3.eth.contract(abi=uniswapV3.ABI, address=uniswapV3.pools[pool_name])
        spaces[pool_name] = contract.functions.tickSpacing().call()
        time.sleep(0.2)

    with open("pool_info/tick_spacing.py", "w") as f:
        f.write("tick_spacings = " + json.dumps(spaces, indent=4))


def pool_creations():
    STEP_SIZE = 20000
    STARTING_BLOCK = 10000000

    for i in range(1000000):
        if (i + 1) * STEP_SIZE + STARTING_BLOCK > w3.eth.block_number:
            STARTING_BLOCK = w3.eth.block_number - ((i + 1) * STEP_SIZE)

        with open("pool_info/creation_blocks_temp.py", "w") as file:
            file.write("creation_block = ")
            file.write(json.dumps(creation_block, indent=4, sort_keys=True))
        print(f"Starting at block: {((i * STEP_SIZE) + STARTING_BLOCK)}")
        print(
            f"Pools left: {len(uniswapV2.pools) + len(sushiswap.pools) + len(uniswapV3.pools) - len(creation_block)}"
        )
        if (
            len(uniswapV2.pools) + len(sushiswap.pools) + len(uniswapV3.pools) - len(creation_block)
            == 0
        ):
            print(json.dumps(creation_block, indent=4, sort_keys=True))

            with open("pool_info/creation_blocks.py", "w") as file:
                file.write("creation_block = ")
                file.write(json.dumps(creation_block, indent=4, sort_keys=True))
            try:
                os.remove("pool_info/creation_blocks_temp.py")
            except Exception as e:
                print(e)
            return

        uniswap_pool_creations = w3.eth.get_logs(
            {
                "fromBlock": (i * STEP_SIZE) + STARTING_BLOCK,
                "toBlock": ((i + 1) * STEP_SIZE) + STARTING_BLOCK,
                "address": UNISWAP_V2_FACTORY,
                "topics": [V2_POOL_CREATION_TOPIC],
            }
        )

        for pool_created in uniswap_pool_creations:
            created_pool_address = w3.toChecksumAddress(
                decode_event_data(pair_creation_abi, pool_created)["pair"]
            )

            if created_pool_address in uniswapV2.pools.values():
                for pool_name in uniswapV2.pool_names:
                    if created_pool_address == uniswapV2.pools[pool_name]:
                        creation_block[pool_name] = pool_created["blockNumber"]

        sushiswap_pool_creations = w3.eth.get_logs(
            {
                "fromBlock": (i * STEP_SIZE) + STARTING_BLOCK,
                "toBlock": ((i + 1) * STEP_SIZE) + STARTING_BLOCK,
                "address": SUSHI_FACTORY_ADDRESS,
                "topics": [V2_POOL_CREATION_TOPIC],
            }
        )

        for pool_created in sushiswap_pool_creations:
            created_pool_address = w3.toChecksumAddress(
                decode_event_data(pair_creation_abi, pool_created)["pair"]
            )
            if created_pool_address in sushiswap.pools.values():
                for pool_name in sushiswap.pool_names:
                    if created_pool_address == sushiswap.pools[pool_name]:
                        creation_block[pool_name] = pool_created["blockNumber"]

        uniswapV3_pool_creations = w3.eth.get_logs(
            {
                "fromBlock": (i * STEP_SIZE) + STARTING_BLOCK,
                "toBlock": ((i + 1) * STEP_SIZE) + STARTING_BLOCK,
                "address": UNISWAP_V3_FACTORY,
                "topics": [V3_POOL_CREATION_TOPIC],
            }
        )

        for pool_created in uniswapV3_pool_creations:
            created_pool_address = w3.toChecksumAddress(
                decode_event_data(pool_creation_abi, pool_created)["pool"]
            )
            if created_pool_address in uniswapV3.pools.values():
                for pool_name in uniswapV3.pool_names:
                    if created_pool_address == uniswapV3.pools[pool_name]:
                        creation_block[pool_name] = pool_created["blockNumber"]


if __name__ == "__main__":
    tick_spacing()
    coin_list()
    decimals()
    pool_creations()
