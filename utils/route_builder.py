import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block


# returns a route of the form: [(COIN0, COIN1, EXCHANGE), ...]
def build_route_tuple(path):
    route_tuple = []
    for i in range(len(path) - 1):
        if len(path[i].split("_")) == 1 or len(path[i + 1].split("_")) == 1:
            continue
        route_tuple.append(
            (path[i].split("_")[0], path[i + 1].split("_")[0], path[i].split("_")[1])
        )
    if len(path[-1].split("_")) != 1 and len(path[0].split("_")) != 1:
        route_tuple.append((path[-1].split("_")[0], path[0].split("_")[0], path[-1].split("_")[1]))

    return route_tuple


# returns a route of the form: [(COIN0, COIN1, [EXCHANGE0, EXCHANGE1, ...]), ...]
# with the exchanges being the ones that the coin is traded on
def get_multi_route(block_number, route):
    multi_route = []

    for swap in route:
        poss_exchanges = []

        variation0 = swap[0] + "_" + swap[1] + "_SUSHI"
        variation1 = swap[1] + "_" + swap[0] + "_SUSHI"

        if variation0 in sushiswap.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("SUSHI")
        if variation1 in sushiswap.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("SUSHI")

        variation0 = swap[0] + "_" + swap[1] + "_UNI"
        variation1 = swap[1] + "_" + swap[0] + "_UNI"

        if variation0 in uniswapV2.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("UNI")
        if variation1 in uniswapV2.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("UNI")

        variation0 = swap[0] + "_" + swap[1] + "_100"
        variation1 = swap[1] + "_" + swap[0] + "_100"

        if variation0 in uniswapV3.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("100")
        if variation1 in uniswapV3.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("100")

        variation0 = swap[0] + "_" + swap[1] + "_500"
        variation1 = swap[1] + "_" + swap[0] + "_500"

        if variation0 in uniswapV3.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("500")
        if variation1 in uniswapV3.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("500")

        variation0 = swap[0] + "_" + swap[1] + "_3000"
        variation1 = swap[1] + "_" + swap[0] + "_3000"

        if variation0 in uniswapV3.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("3000")
        if variation1 in uniswapV3.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("3000")

        variation0 = swap[0] + "_" + swap[1] + "_10000"
        variation1 = swap[1] + "_" + swap[0] + "_10000"

        if variation0 in uniswapV3.pool_names:
            if creation_block[variation0] <= block_number:
                poss_exchanges.append("10000")
        if variation1 in uniswapV3.pool_names:
            if creation_block[variation1] <= block_number:
                poss_exchanges.append("10000")

        multi_route.append((swap[0], swap[1], poss_exchanges))

    return multi_route
