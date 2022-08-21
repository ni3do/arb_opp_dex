from datetime import datetime

from utils.data_loader import load_block

HIGHEST_BLOCK = 14_800_000
DATA_BLOCK_SIZE = 2_000


def bn_to_ts(block_number, data_dir):
    block, df = load_block(block_number, data_dir)
    return block["timestamp"]


def bn_to_date(block_number, data_dir):
    block, df = load_block(block_number, data_dir)
    date = datetime.fromtimestamp(block["timestamp"])
    return date


def ts_to_bn(ts, data_dir, under=False):
    current_block = HIGHEST_BLOCK - DATA_BLOCK_SIZE
    block, df = load_block(current_block, data_dir)

    while block["timestamp"] > ts:
        current_block -= DATA_BLOCK_SIZE
        last_block = block
        block, df = load_block(current_block, data_dir)

    while block["timestamp"] < ts:
        current_block += 1
        last_block = block
        block = load_block(current_block, data_dir, from_data=True, df=df)

    if under:
        return last_block["block_number"]
    else:
        return block["block_number"]


def ts_to_block(ts, data_dir, under=False):
    current_block = HIGHEST_BLOCK - DATA_BLOCK_SIZE
    block, df = load_block(current_block, data_dir)

    while block["timestamp"] > ts:
        current_block -= DATA_BLOCK_SIZE
        block, df = load_block(current_block, data_dir)

    while block["timestamp"] < ts:
        current_block += 1
        last_block = block
        block = load_block(current_block, data_dir, from_data=True, df=df)

    if under:
        return last_block
    else:
        return block
