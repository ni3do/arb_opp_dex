import math

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3


def score(block_number, perc_gain, route_tuple, state):
    smallest_liq = 10**100
    smallest_liq_pool = ""
    for coin0, coin1, exchange in route_tuple:
        variation0 = coin0 + "_" + coin1 + "_" + exchange
        variation1 = coin1 + "_" + coin0 + "_" + exchange

        if variation0 in uniswapV2.pool_names or variation1 in uniswapV2.pool_names:
            if variation0 in uniswapV2.pool_names:
                pool_name = variation0
            else:
                pool_name = variation1

            pool_state = state[pool_name]
            current_state = pool_state[pool_state["block_number"] <= block_number][-1:]

            if smallest_liq > int(current_state["reserve_0"]) * int(current_state["reserve_1"]):
                smallest_liq = int(current_state["reserve_0"]) * int(current_state["reserve_1"])
                smallest_liq_pool = pool_name
        elif variation0 in sushiswap.pool_names or variation1 in sushiswap.pool_names:
            if variation0 in sushiswap.pool_names:
                pool_name = variation0
            else:
                pool_name = variation1

            pool_state = state[pool_name]
            current_state = pool_state[pool_state["block_number"] <= block_number][-1:]

            if smallest_liq > int(current_state["reserve_0"]) * int(current_state["reserve_1"]):
                smallest_liq = int(current_state["reserve_0"]) * int(current_state["reserve_1"])
                smallest_liq_pool = pool_name
        elif variation0 in uniswapV3.pool_names or variation1 in uniswapV3.pool_names:
            if variation0 in uniswapV3.pool_names:
                pool_name = variation0
            else:
                pool_name = variation1

            pool_state = state[pool_name]
            current_state = pool_state[pool_state["block_number"] <= block_number][-1:]

            if smallest_liq > int(current_state["liquidity"].iloc[0]) ** 2:
                smallest_liq = int(current_state["liquidity"].iloc[0]) ** 2
                smallest_liq_pool = pool_name
        else:
            print(f"Pool not found: {variation0}, {variation1}")
            return 0
    # print(f"Sm Pool: {smallest_liq_pool}")
    # print(f"Smallest Liq: {float(smallest_liq)}")
    if smallest_liq == 0:
        return 0
    # print(f"Sqrt liq: {math.log(float(smallest_liq))}")
    # print(f"Perc Gain: {perc_gain}")
    print(f"Pecrt Gain: {perc_gain}")
    print(f"LiqScore:   {float(math.log(float(smallest_liq))) / 116.0}")
    score = (float(perc_gain)) + (float(math.log(smallest_liq)) / 116.0) * 2.0
    score /= 3.0
    return score
