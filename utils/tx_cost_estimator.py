from web3 import Web3

from utils.data_loader import load_block

LONDON_HARDFORK_BLOCK = 12_965_000

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 120}))

LIVE_DATA = False

DATA_BLOCK_SIZE = 2000

TX_BASE_COST = 60_000
SWAP_COST = 60_000


def tx_cost(block_number, route, data_dir, block=None):
    if block is not None:
        gas_price = block["gas_price"]
    elif LIVE_DATA:
        if block_number < LONDON_HARDFORK_BLOCK:
            block = w3.eth.get_block(block_number)

            gas_price = 0
            samples = 2
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
            gas_price = w3.eth.get_block(block_number)["baseFeePerGas"]
    else:
        block, df = load_block(block_number, data_dir)
        gas_price = block["gas_price"]
    # print(f"Gas Price: {gas_price}")
    cost_estimate = gas_price * (len(route) * SWAP_COST + TX_BASE_COST)
    return cost_estimate
