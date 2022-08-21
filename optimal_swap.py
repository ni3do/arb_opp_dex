import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.decimals import decimals
from swap_v2 import swap_V2
from swap_v3 import swap_V3
from utils.route_builder import get_multi_route


def router(block_number, route, amount_in, swap_base, tick_dict):
    amount_out = 0
    for swap in route:
        variation0 = swap[0] + "_" + swap[1] + "_" + swap[2]
        variation1 = swap[1] + "_" + swap[0] + "_" + swap[2]

        if variation0 in uniswapV2.pool_names:
            zeroForOne = True
            pool_name = variation0
            amount_out = swap_V2(
                pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
            )
        elif variation1 in uniswapV2.pool_names:
            zeroForOne = False
            pool_name = variation1
            amount_out = swap_V2(
                pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
            )
        elif variation0 in sushiswap.pool_names:
            zeroForOne = True
            pool_name = variation0
            amount_out = swap_V2(
                pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
            )
        elif variation1 in sushiswap.pool_names:
            zeroForOne = False
            pool_name = variation1
            amount_out = swap_V2(
                pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
            )
        elif variation0 in uniswapV3.pool_names:
            zeroForOne = True
            pool_name = variation0
            amount_out = swap_V3(
                pool_name,
                block_number,
                amount_in,
                zeroForOne,
                swap_base[pool_name],
                tick_dict[pool_name],
            )
        elif variation1 in uniswapV3.pool_names:
            zeroForOne = False
            pool_name = variation1
            amount_out = swap_V3(
                pool_name,
                block_number,
                amount_in,
                zeroForOne,
                swap_base[pool_name],
                tick_dict[pool_name],
            )
        else:
            print(f"Pool not found: {variation0}, {variation1}")
            return 0
        amount_in = amount_out

    return amount_out


def opt_router(block_number, route, amount_in, swap_base, tick_dict):
    amount_out = 0
    exchange_route = []
    for swap in route:
        best_ex = ""
        best_ex_amount = 0

        for exchange in swap[2]:
            variation0 = swap[0] + "_" + swap[1] + "_" + exchange
            variation1 = swap[1] + "_" + swap[0] + "_" + exchange
            if variation0 in exchange_route or variation1 in exchange_route:
                print(f"Already used: {variation0}, {variation1}")
                continue
            if variation0 in uniswapV2.pool_names:
                zeroForOne = True
                pool_name = variation0
                amount_out = swap_V2(
                    pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
                )
            elif variation1 in uniswapV2.pool_names:
                zeroForOne = False
                pool_name = variation1
                amount_out = swap_V2(
                    pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
                )
            elif variation0 in sushiswap.pool_names:
                zeroForOne = True
                pool_name = variation0
                amount_out = swap_V2(
                    pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
                )
            elif variation1 in sushiswap.pool_names:
                zeroForOne = False
                pool_name = variation1
                amount_out = swap_V2(
                    pool_name, amount_in, zeroForOne, block_number, swap_base[pool_name]
                )
            elif variation0 in uniswapV3.pool_names:
                zeroForOne = True
                pool_name = variation0
                amount_out = swap_V3(
                    pool_name,
                    block_number,
                    amount_in,
                    zeroForOne,
                    swap_base[pool_name],
                    tick_dict[pool_name],
                )
            elif variation1 in uniswapV3.pool_names:
                zeroForOne = False
                pool_name = variation1
                amount_out = swap_V3(
                    pool_name,
                    block_number,
                    amount_in,
                    zeroForOne,
                    swap_base[pool_name],
                    tick_dict[pool_name],
                )
            else:
                pass
            if amount_out > best_ex_amount:
                best_ex = exchange
                best_ex_amount = amount_out
        amount_in = best_ex_amount
        exchange_route.append((swap[0], swap[1], best_ex))

    return best_ex_amount, exchange_route


def ternary_search(block_number, route, swap_base, tick_dict, optimize_exchanges=False):
    if optimize_exchanges:
        route = get_multi_route(block_number, route)

    outer_done = False
    starting_r = 0.1 * (10 ** decimals[route[0][0]])
    while not outer_done:
        l = 0
        r = starting_r

        done = False

        while not done:
            input0 = int((r - l) * (1 / 3) + l)
            input1 = int((r - l) * (2 / 3) + l)

            if optimize_exchanges:
                output0, exchange_route = opt_router(
                    block_number, route, input0, swap_base, tick_dict
                )
                output1, exchange_route = opt_router(
                    block_number, route, input1, swap_base, tick_dict
                )
            else:
                output0 = router(block_number, route, input0, swap_base, tick_dict)
                output1 = router(block_number, route, input1, swap_base, tick_dict)

            profit0 = output0 - input0
            profit1 = output1 - input1

            if profit0 < profit1:
                l = input0
            elif profit0 > profit1:
                r = input1
            else:
                l = input0
                r = input1

            if abs(r - l) < starting_r * 0.1:
                done = True

        if r > starting_r * 0.9:
            starting_r *= 10
        else:
            outer_done = True
    if optimize_exchanges:
        return profit1, input1, output1, exchange_route
    else:
        return profit1, input1, output1
