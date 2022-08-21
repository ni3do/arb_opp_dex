import math
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

import pool_info.sushiswap as sushiswap
import pool_info.uniswapV2 as uniswapV2
import pool_info.uniswapV3 as uniswapV3
from pool_info.creation_blocks import creation_block
from pool_info.decimal_deltas import decimal_deltas
from utils.data_loader import build_state, load_pool_dict

thread_pool = ThreadPoolExecutor(max_workers=40)


def build_graph(block_number, state_dict):
    G = nx.DiGraph()
    best_connection = {}
    coins = []

    # handle all V3 pools
    for pool_name in uniswapV3.pool_names:
        # do not consider pool that were not initialized at the current block
        if creation_block[pool_name] > block_number:
            continue
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        # get state for current block
        state = state_dict[pool_name]
        if len(state) != 0:
            sqrt_P = int(state[2])
            # calculate price
            tick = math.log(math.pow(sqrt_P, 2) / math.pow(2, 192), 1.0001)

            onePerZero = (1.0001**tick) * (10 ** decimal_deltas[pool_name])
            zeroPerOne = 1 / onePerZero

            fee_perc = float(suffix) / 1_000_000
            # account for pool fee
            onePerZero *= 1 - fee_perc
            zeroPerOne *= 1 - fee_perc

            connection_name = f"{token0}_{token1}"
            if best_connection.get(connection_name) is None:
                best_connection[connection_name] = [
                    token0,
                    token1,
                    suffix,
                    onePerZero,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[connection_name][3]) < onePerZero:
                    best_connection[connection_name] = [
                        token0,
                        token1,
                        suffix,
                        onePerZero,
                    ]

            reverse_connection_name = f"{token1}_{token0}"
            if best_connection.get(reverse_connection_name) is None:
                best_connection[reverse_connection_name] = [
                    token1,
                    token0,
                    suffix,
                    zeroPerOne,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[reverse_connection_name][3]) < zeroPerOne:
                    best_connection[reverse_connection_name] = [
                        token1,
                        token0,
                        suffix,
                        zeroPerOne,
                    ]

    # handle uniswapV2 pools
    for pool_name in uniswapV2.pool_names:
        if creation_block[pool_name] > block_number:
            continue
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        # get state for current block
        state = state_dict[pool_name]
        if len(state) != 0:
            reserve_0 = int(state[1])
            reserve_1 = int(state[2])

            onePerZero = (reserve_1 / reserve_0) * (10 ** decimal_deltas[pool_name])
            zeroPerOne = (reserve_0 / reserve_1) * (10 ** -decimal_deltas[pool_name])

            # account for pool fee
            onePerZero *= 0.997
            zeroPerOne *= 0.997

            connection_name = f"{token0}_{token1}"
            if best_connection.get(connection_name) is None:
                best_connection[connection_name] = [
                    token0,
                    token1,
                    suffix,
                    onePerZero,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[connection_name][3]) < onePerZero:
                    best_connection[connection_name] = [
                        token0,
                        token1,
                        suffix,
                        onePerZero,
                    ]

            reverse_connection_name = f"{token1}_{token0}"
            if best_connection.get(reverse_connection_name) is None:
                best_connection[reverse_connection_name] = [
                    token1,
                    token0,
                    suffix,
                    zeroPerOne,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[reverse_connection_name][3]) < zeroPerOne:
                    best_connection[reverse_connection_name] = [
                        token1,
                        token0,
                        suffix,
                        zeroPerOne,
                    ]

    # handle sushiswap pools
    for pool_name in sushiswap.pool_names:
        if creation_block[pool_name] > block_number:
            continue
        # get both token names and suffix
        token0, sep, rest = pool_name.partition("_")
        token1, sep, suffix = rest.partition("_")

        # get state for current block
        state = state_dict[pool_name]
        if len(state) != 0:
            reserve_0 = int(state[1])
            reserve_1 = int(state[2])

            onePerZero = (reserve_1 / reserve_0) * (10 ** decimal_deltas[pool_name])
            zeroPerOne = (reserve_0 / reserve_1) * (10 ** -decimal_deltas[pool_name])

            # account for pool fee
            onePerZero *= 0.997
            zeroPerOne *= 0.997

            connection_name = f"{token0}_{token1}"
            if best_connection.get(connection_name) is None:
                best_connection[connection_name] = [
                    token0,
                    token1,
                    suffix,
                    onePerZero,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[connection_name][3]) < onePerZero:
                    best_connection[connection_name] = [
                        token0,
                        token1,
                        suffix,
                        onePerZero,
                    ]

            reverse_connection_name = f"{token1}_{token0}"
            if best_connection.get(reverse_connection_name) is None:
                best_connection[reverse_connection_name] = [
                    token1,
                    token0,
                    suffix,
                    zeroPerOne,
                ]
                if token0 not in coins:
                    coins.append(token0)
                if token1 not in coins:
                    coins.append(token1)
            else:
                if float(best_connection[reverse_connection_name][3]) < zeroPerOne:
                    best_connection[reverse_connection_name] = [
                        token1,
                        token0,
                        suffix,
                        zeroPerOne,
                    ]
    for pool_name in best_connection:
        token0 = best_connection[pool_name][0]
        token1 = best_connection[pool_name][1]
        suffix = best_connection[pool_name][2]
        price = best_connection[pool_name][3]
        G.add_weighted_edges_from(
            [
                (
                    token0,
                    token1,
                    {"exchange": suffix, "price": -math.log((price), 2)},
                )
            ]
        )
    return G


def draw_graph(G, block_number, path):

    pos = {
        "ETH": ([0, 3]),
        "USDC": [-1, 1],
        "USDT": ([1, 1]),
        "DAI": [1, 2],
        "WBTC": ([-1, 2]),
        "FRAX": ([-0.9, -1]),
        "SUSHI": ([-0.3, -2]),
        "UNI": ([-0.5, -3]),
    }

    edges = []
    for u, v, d in G.edges(data=True):
        if u not in nodes or v not in nodes:
            continue
        edges.append((u, v, d))

    labels = dict(
        [
            (
                (
                    v,
                    u,
                ),
                f'{(2 ** -d["weight"]["price"]):.6f} {v}/{u}',
            )
            for u, v, d in edges
        ]
    )

    with open(f"{path}_edges.txt", "w") as f:
        f.write(f"x -> y on exchange: price -math.log(price, 2)\n")
        for u, v, d in G.edges(data=True):
            f.write(
                f"{u} -> {v} on {d['weight']['exchange']}: {2**-d['weight']['price']} {d['weight']['price']}\n"
            )

    f, ax = plt.subplots(1)
    # nx.draw(G, pos, nodelist=nodes, connectionstyle="arc3,rad=0.1", with_labels=True, font_size=5)
    nodes = nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_size=1600, node_color="white")
    nodes.set_edgecolor("black")
    nx.draw_networkx_labels(G, pos)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=edges,
        connectionstyle="arc3,rad=0.1",
        arrowstyle="->",
        arrowsize=10,
        node_size=1600,
    )
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=6, label_pos=0.25)
    f.tight_layout()
    plt.savefig(f"{path}_graph.png", dpi=1000)


def cycle_cost(G, cycle):
    cost = 0
    route = []
    for i in range(len(cycle) - 1):
        if cycle[i + 1] in G[cycle[i]].keys():
            cost += G[cycle[i]][cycle[i + 1]]["weight"]["price"]
            route.append(G[cycle[i]][cycle[i + 1]]["weight"]["exchange"])
        else:
            print(f"Edge not found: {cycle[i]} -> {cycle[i+1]}")
            sys.exit()
    if cycle[-1] in G[cycle[0]].keys():
        cost += G[cycle[-1]][cycle[0]]["weight"]["price"]
        route.append(G[cycle[-1]][cycle[0]]["weight"]["exchange"])
    else:
        print(f"Edge not found: {cycle[-1]} -> {cycle[0]}")
        sys.exit()
    return cost, route


def sort_cycles(cycles):
    srt_cycles = []
    coins = ["ETH", "USDC", "USDT", "DAI", "WBTC", "UNI", "SUSHI"]

    for cycle in cycles:
        rotated_cycle = []
        for coin in coins:
            if len(rotated_cycle) != 0:
                break
            if coin in cycle:
                counter = 0
                for c in cycle:
                    if coin == c:
                        for i in range(len(cycle)):
                            rotated_cycle.append(cycle[(counter + i) % len(cycle)])
                        break
                    counter += 1
        srt_cycles.append(rotated_cycle)
    return sorted(srt_cycles)


def new_pools(pool_dict, block_number):
    new_pools = []
    for pool_name in pool_dict:
        if creation_block[pool_name] == block_number:
            new_pools.append(pool_name)
    return new_pools


def changing_pools(pool_dict, block_number):
    changing_pools = []
    for pool_name in pool_dict:
        if len(pool_dict[pool_name].loc[pool_dict[pool_name]["block_number"] == block_number]) != 0:
            changing_pools.append(pool_name)

    return changing_pools


def changing_coins(pool_arr):
    coin_arr = []
    for pool_name in pool_arr:
        coin_arr.append(pool_name.split("_")[0] + "_" + pool_name.split("_")[2])
        coin_arr.append(pool_name.split("_")[1] + "_" + pool_name.split("_")[2])
    return coin_arr


def find_opps(start_block, end_block, pool_dict):
    opps = []
    block_time_arr = []

    start_200 = datetime.now().timestamp()

    for block in range(start_block, end_block):

        block_start = datetime.now().timestamp()
        block_opps = []

        if block % 200 == 0:
            end_200 = datetime.now().timestamp()
            print(f"Block: {block}")
            print(f"Last 200 blocks: {end_200 - start_200}s")
            if len(block_time_arr) > 0:
                print(f"Block time: {sum(block_time_arr) / len(block_time_arr)}s")
                block_time_arr = []
            start_200 = datetime.now().timestamp()

            # save the data
            df = pd.DataFrame(opps, columns=["block_number", "gain", "cycle"])
            df.sort_values(by=["block_number"], inplace=True)
            df.to_csv(f"../data/opps/{block-200}_{block-1}.csv", index=False)
            opps = []
            print(f"Saved for {block-200}_{block-1}")

        state = build_state(start_block, pool_dict)

        G = build_graph(start_block, state)
        # sort simple cycles to get deterministic results
        cycles = sort_cycles(nx.simple_cycles(G))

        for cycle in cycles:
            gain, exchange_route = cycle_cost(G, cycle)
            if gain < -0.001:
                route_tuple = []
                for i in range(len(cycle) - 1):
                    route_tuple.append((cycle[i], cycle[i + 1], exchange_route[i]))
                route_tuple.append((cycle[-1], cycle[0], exchange_route[-1]))
                block_opps.append([int(block), gain * -1, route_tuple])

        opps += block_opps

        block_end = datetime.now().timestamp()
        block_time_arr.append(block_end - block_start)

    df = pd.DataFrame(opps, columns=["block_number", "gain", "cycle"])
    df.sort_values(by=["block_number"], inplace=True)
    df.to_csv(f"../data/opps/{block-(block % 200)}_{block}.csv", index=False)
    opps = []
    print(f"Saved for {block-(block % 200)}_{block}")


def one_thread_opps(start_block, end_block):
    step_size = 2_000
    for i in range(start_block, end_block, step_size):
        pool_dict = load_pool_dict(i, "../data/")
        print(f"Pool dict loaded for block {i}")

        start = datetime.now().timestamp()
        find_opps(i, i + step_size - 1, pool_dict)
        end = datetime.now().timestamp()

        print(f"Iteration finished in: {'{:.4f}'.format(end - start)}s")


def thread_opps(start_block, end_block):
    step_size = 2_000
    threads = 5

    for i in range(start_block, end_block, step_size * threads):
        futures = []
        start = datetime.now().timestamp()
        for j in range(i, i + (step_size * threads), step_size):
            pool_dict = load_pool_dict(j, "../data")
            futures.append(thread_pool.submit(find_opps, j, j + step_size, pool_dict.copy()))

        print(f"All {len(futures)} threads started: {i}-{i + step_size}")
        for f in futures:
            f.result()
        end = datetime.now().timestamp()
        print(f"Threads finished in: {'{:.4f}'.format(end - start)}s")


if __name__ == "__main__":
    thread_opps(12_420_000, 12_440_000)
