import math
import time
from datetime import datetime

from web3 import Web3

from pool_info.tick_spacing import tick_spacings
from pool_info.uniswapV3 import uniswapV3
from utils.live_data_loader import get_state

# web3 setup
NODE_URL = "http://localhost:8545/"
w3 = Web3(Web3.HTTPProvider(NODE_URL, request_kwargs={"timeout": 10}))
LIVE_DATA = False
TIMEOUT_AFTER_CALL = 0


def calc_tick(p):
    return (math.log(p) * 2) / math.log(1.0001)


def calc_sqrt_price(i):
    sqrtPrice = 1.0001 ** (i / 2.0)
    if sqrtPrice > 1_000_000_000_000:
        return int(sqrtPrice)
    return sqrtPrice


def getAmountDelta(priceA, priceB, liquidity, zeroForOne):
    if zeroForOne:
        if priceA > priceB:
            priceA, priceB = priceB, priceA
        return int(liquidity * ((1 / priceA) - (1 / priceB)))
    else:
        if priceA < priceB:
            priceA, priceB = priceB, priceA
        return int(liquidity * (priceA - priceB))


def getNextSqrtPriceFromAmount(price, liquidity, amount, zeroForOne):
    if zeroForOne:
        return liquidity * price / (liquidity + amount * price)
    else:
        return price + (amount / liquidity)


def swap_V3(pool_name, block_number, amount_in, zeroForOne, current_state, tick_dict):
    start_swap = datetime.now().timestamp()
    # tick_dict = {}
    tick_spacing = tick_spacings[pool_name]

    if LIVE_DATA:
        contract = w3.eth.contract(address=uniswapV3.pools[pool_name], abi=uniswapV3.ABI)
        state = get_state(pool_name, block_number)
        liquidity = state[1]
        current_tick = state[3]
        current_price = state[2] / (2**96)
        current_tick = calc_tick(current_price)

    else:
        current_tick = int(current_state["tick"])
        current_price = (int(current_state["sqrt_price"])) / (2**96)
        liquidity = int(current_state["liquidity"])

        try:
            # get initialized tick to maybe skip some ticks
            initialized_ticks = list(tick_dict[pool_name].keys())
        except Exception as e:
            initialized_ticks = []

    # apply pool fee
    fee_perc = float(pool_name.split("_")[2]) / 1_000_000
    amount_in = float(amount_in) * (1.0 - fee_perc)
    # set amounts
    amount_remaining = amount_in
    amount_out = 0

    loop_counter = 0
    start_while = datetime.now().timestamp()
    # swap until no input is left
    while amount_remaining > 0:
        loop_counter += 1

        # get the next tick
        if current_tick % tick_spacing != 0:
            if zeroForOne:
                next_tick = current_tick - (current_tick % tick_spacing)
            else:
                next_tick = current_tick + tick_spacing - (current_tick % tick_spacing)
        else:
            if LIVE_DATA:
                if zeroForOne:
                    next_tick = current_tick - tick_spacing
                else:
                    next_tick = current_tick + tick_spacing
            else:
                if zeroForOne:
                    try:
                        idx = initialized_ticks.index(current_tick)
                        try:
                            next_tick = initialized_ticks[idx - 1]
                        except IndexError as ie:
                            # print(f"IndexError: {ie}")
                            next_tick = current_tick - tick_spacing
                    except ValueError as ve:
                        next_tick = current_tick - tick_spacing
                else:
                    try:
                        idx = initialized_ticks.index(current_tick)
                        try:
                            next_tick = initialized_ticks[idx + 1]
                        except IndexError as ie:
                            # print(f"IndexError: {ie}")
                            next_tick = current_tick + tick_spacing
                    except ValueError as ve:
                        next_tick = current_tick + tick_spacing
        # print(f"next_tick: {next_tick}")
        next_price = calc_sqrt_price(int(next_tick))
        amount_to_next_tick = getAmountDelta(next_price, current_price, liquidity, zeroForOne)
        if amount_to_next_tick == 0:
            # print(f"Stopping cause amount_to_next_tick is 0")
            return int(amount_out)

        if amount_to_next_tick > amount_remaining:
            final_price = getNextSqrtPriceFromAmount(
                current_price, liquidity, amount_remaining, zeroForOne
            )
            amount_out += getAmountDelta(final_price, current_price, liquidity, not zeroForOne)
            break
        else:
            temp_out = getAmountDelta(next_price, current_price, liquidity, not zeroForOne)
            # print(f"temp_out: {temp_out}")
            amount_out += temp_out
            amount_remaining -= int(amount_to_next_tick)
            current_tick = next_tick
            current_price = next_price

        # update liquidity if next tick is initiallized
        if LIVE_DATA:
            live_liq = contract.functions.ticks(int(next_tick)).call(
                block_identifier=int(block_number)
            )[1]
            time.sleep(TIMEOUT_AFTER_CALL)
            # liquidity += live_liq
        else:
            try:
                if zeroForOne:
                    liquidity += int(tick_dict[pool_name][int(next_tick)])
                else:
                    liquidity -= int(tick_dict[pool_name][int(next_tick)])
            except KeyError as ke:
                pass
    # print(f"Loops: {loop_counter}")
    while_time = datetime.now().timestamp() - start_swap
    # print(f"While time: {while_time}")
    # with open(f"../stats/v3_swap_time.txt", "a") as f:
    #     f.write(f"{while_time},\n")
    # with open(f"../stats/loop_counter.txt", "a") as f:
    #     f.write(f"{loop_counter},\n")
    return int(amount_out)
