import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from numpy import median
from pool_info.decimals import decimals
from web3 import Web3

from utils.route_builder import get_multi_route

NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 10}))
# if True makes direct requests to ETH Archive Node
LIVE_DATA = False

DATA_BLOCK_SIZE = 2000


def eth_value(block_number, coin, amount, swap_base):
    if coin == "ETH":
        return amount
    amount *= 10 ** decimals[coin]
    route = get_multi_route(block_number, [(coin, "ETH", "")])

    amounts = []
    for exchange in route[0][2]:
        if exchange in ["UNI", "SUSHI"]:
            variation0 = f"{coin}_ETH_{exchange}"
            variation1 = f"ETH_{coin}_{exchange}"

            if variation0 in sushiswap.pool_names:
                pool_name = variation0
            elif variation1 in sushiswap.pool_names:
                pool_name = variation1
            elif variation0 in uniswapV2.pool_names:
                pool_name = variation0
            elif variation1 in uniswapV2.pool_names:
                pool_name = variation1

            if LIVE_DATA:
                if pool_name in sushiswap.pool_names:
                    contract = w3.eth.contract(
                        address=sushiswap.pools[pool_name], abi=sushiswap.ABI
                    )
                else:
                    contract = w3.eth.contract(
                        address=uniswapV2.pools[pool_name],
                        abi=uniswapV2.ABI,
                    )

                chain_current_state = contract.functions.getReserves().call(
                    block_identifier=int(block_number)
                )
                current_price = chain_current_state[1] / chain_current_state[0]

                if pool_name == variation0:
                    amounts.append(current_price * amount)
                else:
                    amounts.append(amount / current_price)

            else:
                current_state = swap_base[pool_name]
                current_price = int(current_state["reserve_1"]) / int(current_state["reserve_0"])

                if pool_name == variation0:
                    amounts.append(amount * current_price)
                else:
                    amounts.append(amount / current_price)
        else:
            variation0 = f"{coin}_ETH_{exchange}"
            variation1 = f"ETH_{coin}_{exchange}"

            if variation0 in uniswapV3.pool_names:
                pool_name = variation0
            elif variation1 in uniswapV3.pool_names:
                pool_name = variation1

            if LIVE_DATA:
                contract = w3.eth.contract(
                    address=uniswapV3.pools[pool_name],
                    abi=uniswapV3.ABI,
                )

                slot0 = contract.functions.slot0().call(block_identifier=int(block_number))
                current_price = slot0[0] / (2**96)

                if pool_name == variation0:
                    amounts.append(amount * current_price)
                else:
                    amounts.append(amount / current_price)

            else:
                current_state = swap_base[pool_name]
                current_price = int(current_state["sqrt_price"]) / (2**96)
                current_price = current_price**2

                if pool_name == variation0:
                    amounts.append(amount * current_price)
                else:
                    amounts.append(amount / current_price)
    if len(amounts) == 0:
        print(f"No data for {coin}/ETH")
        return 0
    else:
        return median(amounts) * (10**-18)


# assume all stable coins keep peg
def usd_value(block_number, coin, amount, swap_base):
    if coin == "ETH":
        eth_amount = amount
    else:
        eth_amount = eth_value(block_number, coin, amount, swap_base)

    stable_coins = ["DAI", "USDC", "USDT"]
    for stable_coin in stable_coins:
        route = get_multi_route(block_number, [(stable_coin, "ETH", "")])
        amount = eth_amount
        amounts = []
        for exchange in route[0][2]:
            if exchange in ["UNI", "SUSHI"]:

                variation0 = f"ETH_{stable_coin}_{exchange}"
                variation1 = f"{stable_coin}_ETH_{exchange}"

                if variation0 in sushiswap.pool_names:
                    pool_name = variation0
                elif variation1 in sushiswap.pool_names:
                    pool_name = variation1
                elif variation0 in uniswapV2.pool_names:
                    pool_name = variation0
                elif variation1 in uniswapV2.pool_names:
                    pool_name = variation1

                if LIVE_DATA:
                    if pool_name in sushiswap.pool_names:
                        contract = w3.eth.contract(
                            address=sushiswap.pools[pool_name], abi=sushiswap.ABI
                        )
                    else:
                        contract = w3.eth.contract(
                            address=uniswapV2.pools[pool_name],
                            abi=uniswapV2.ABI,
                        )

                    chain_current_state = contract.functions.getReserves().call(
                        block_identifier=int(block_number)
                    )
                    current_price = float(chain_current_state[1] / chain_current_state[0])

                    if pool_name == variation0:
                        amounts.append(
                            float(current_price * amount * (10 ** -decimals[stable_coin]))
                        )
                    else:
                        amounts.append(
                            float(amount / current_price) * (10 ** -decimals[stable_coin])
                        )

                else:
                    current_state = swap_base[pool_name]
                    current_price = int(current_state["reserve_1"]) / int(
                        current_state["reserve_0"]
                    )

                    if pool_name == variation0:
                        amounts.append(amount * current_price * (10 ** -decimals[stable_coin]))
                    else:
                        amounts.append((amount / current_price) * (10 ** -decimals[stable_coin]))
            else:
                variation0 = f"ETH_{stable_coin}_{exchange}"
                variation1 = f"{stable_coin}_ETH_{exchange}"

                if variation0 in uniswapV3.pool_names:
                    pool_name = variation0
                elif variation1 in uniswapV3.pool_names:
                    pool_name = variation1

                if LIVE_DATA:
                    contract = w3.eth.contract(
                        address=uniswapV3.pools[pool_name],
                        abi=uniswapV3.ABI,
                    )

                    slot0 = contract.functions.slot0().call(block_identifier=int(block_number))
                    current_price = slot0[0] / (2**96)

                    if pool_name == variation0:
                        amounts.append(
                            float(amount * current_price * (10 ** -decimals[stable_coin]))
                        )
                    else:
                        amounts.append(
                            float((amount / current_price) * (10 ** -decimals[stable_coin]))
                        )

                else:
                    current_state = swap_base[pool_name]
                    current_price = int(current_state["sqrt_price"]) / (2**96)
                    current_price = current_price**2

                    if pool_name == variation0:
                        amounts.append(amount * current_price * (10 ** -decimals[stable_coin]))
                    else:
                        amounts.append((amount / current_price) * (10 ** -decimals[stable_coin]))

    if len(amounts) == 0:
        return 0
    else:
        return median(amounts)
