from itertools import chain

import eth_abi


# decodes data value from an event according to the provided function abi
def decode_event_data(func_abi, log_entry):
    # print(json.dumps(func_abi, indent=4))
    types = [i["type"] for i in func_abi["inputs"] if not i["indexed"]]
    # print(types)
    names = [i["name"] for i in func_abi["inputs"] if not i["indexed"]]
    # print(names)
    values = eth_abi.decode_abi(types, bytes.fromhex(log_entry["data"][2:]))
    # print(values)
    indexed_types = [i["type"] for i in func_abi["inputs"] if i["indexed"]]
    # print(indexed_types)
    indexed_names = [i["name"] for i in func_abi["inputs"] if i["indexed"]]
    # print(indexed_names)
    indexed_values = [
        eth_abi.decode_single(t, v) for t, v in zip(indexed_types, log_entry["topics"][1:])
    ]
    # print(indexed_values)
    decoded_data = dict(chain(zip(names, values), zip(indexed_names, indexed_values)))

    return decoded_data
