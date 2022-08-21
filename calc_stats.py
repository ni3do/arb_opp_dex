import os

import numpy as np


def evaluate():
    for file in sorted(os.listdir("../stats")):
        with open(f"../stats/{file}", "r") as f:
            value_str = f"[{f.read()}]"
        values = np.array(eval(value_str))
        print(f"-----------------------")
        print(f"File:   {file}: {len(values)}")
        print(f"Total:  {np.sum(values):.4f}")
        print(f"Mean:   {np.mean(values):.4f}")
        print(f"Max:    {np.max(values):.4f}")


def reset():
    for file in sorted(os.listdir("../stats")):
        os.remove(f"../stats/{file}")


if __name__ == "__main__":
    reset()
    evaluate()
