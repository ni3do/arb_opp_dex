from web3 import Web3

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 10}))

LIVE_DATA = False


def swap_V2(pool_name, amount_in, zeroForOne, block_number, current_state):
    # start_swap = datetime.now().timestamp()
    if LIVE_DATA:
        if pool_name in uniswapV2.pool_names:
            contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)
        elif pool_name in sushiswap.pool_names:
            contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)
        chain_current_state = contract.functions.getReserves().call(
            block_identifier=int(block_number)
        )

        reserves = [chain_current_state[0], chain_current_state[1]]
    else:
        reserves = [
            int(current_state["reserve_0"]),
            int(current_state["reserve_1"]),
        ]

    # calculate constant for CMM function
    k = reserves[0] * reserves[1]
    # apply pool fee
    amount_in *= 1 - 0.003
    # calculate amount out
    if zeroForOne:
        amount_out = reserves[1] - (k / (reserves[0] + amount_in))
    else:
        amount_out = reserves[0] - (k / (reserves[1] + amount_in))

    # with open(f"../stats/v2_swap_time.txt", "a") as f:
    #     f.write(f"{datetime.now().timestamp() - start_swap},\n")
    return amount_out
