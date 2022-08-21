import time

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from web3 import Web3

# web3 setup
# key = "1984d43d-2a06-46a7-a92c-502328356b6f"
# NODE_URL = "https://api.archivenode.io/{}".format(key)
NODE_URL = "https://eth-mainnet.g.alchemy.com/v2/6RQq1fg909V_flXc1Ql4wKjoreoDLQrp"
# NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 10}))

TIMEOUT_AFTER_CALL = 0

# returns current state of the pool at the given block number, uses live data
def get_state(pool_name, block_number):
    if pool_name in uniswapV3.pool_names:
        contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)
        liquidity = contract.functions.liquidity().call(block_identifier=int(block_number))
        time.sleep(TIMEOUT_AFTER_CALL)
        slot0 = contract.functions.slot0().call(block_identifier=int(block_number))
        time.sleep(TIMEOUT_AFTER_CALL)
        return [block_number, liquidity, slot0[0], slot0[1]]
    elif pool_name in uniswapV2.pool_names:
        contract = w3.eth.contract(address=uniswapV2.pools[pool_name], abi=uniswapV2.ABI)
        reserves = contract.functions.getReserves().call(block_identifier=int(block_number))
        time.sleep(TIMEOUT_AFTER_CALL)
        return [block_number, reserves[0], reserves[1]]
    elif pool_name in sushiswap.pool_names:
        contract = w3.eth.contract(address=sushiswap.pools[pool_name], abi=sushiswap.ABI)
        reserves = contract.functions.getReserves().call(block_identifier=int(block_number))
        time.sleep(TIMEOUT_AFTER_CALL)
        return [block_number, reserves[0], reserves[1]]
