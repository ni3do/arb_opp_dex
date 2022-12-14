pools = {
    "DAI_USDT_500": "0x6f48ECa74B38d2936B02ab603FF4e36A6C0E3A77",
    "DAI_USDC_100": "0x5777d92f208679DB4b9778590Fa3CAB3aC9e2168",
    "DAI_USDC_500": "0x6c6Bc977E13Df9b0de53b251522280BB72383700",
    "ETH_USDT_10000": "0xC5aF84701f98Fa483eCe78aF83F11b6C38ACA71D",
    "ETH_USDT_3000": "0x4e68Ccd3E89f51C3074ca5072bbAC773960dFa36",
    "ETH_USDT_500": "0x11b815efB8f581194ae79006d24E0d814B7697F6",
    "SUSHI_ETH_10000": "0x19E286157200418d6A1f7D1df834b82E65C920AA",
    "SUSHI_ETH_3000": "0x73A6a761FE483bA19DeBb8f56aC5bbF14c0cdad1",
    "SUSHI_USDC_1000": "0x184C33b7B1089747440057e46B4E2Bb61F09Bc8D",
    "SUSHI_USDT_3000": "0x206c9f6aD08a8f2A3Cc05BD3939Cd49287560096",
    "UNI_ETH_3000": "0x1d42064Fc4Beb5F8aAF85F4617AE8b3b5B8Bd801",
    "UNI_SUSHI_10000": "0x9C3e0e151a495C4921a5412241d29520eb5786C0",
    "UNI_USDC_3000": "0xD0fC8bA7E267f2bc56044A7715A489d851dC6D78",
    "UNI_USDT_3000": "0x3470447f3CecfFAc709D3e783A307790b0208d60",
    "UNI_ETH_10000": "0x360b9726186C0F62cc719450685ce70280774Dc8",
    "USDC_ETH_10000": "0x7BeA39867e4169DBe237d55C8242a8f2fcDcc387",
    "USDC_ETH_3000": "0x8ad599c3A0ff1De082011EFDDc58f1908eb6e6D8",
    "USDC_ETH_500": "0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640",
    "USDC_USDT_100": "0x3416cF6C708Da44DB2624D63ea0AAef7113527C6",
    "WBTC_DAI_3000": "0x391E8501b626C623d39474AfcA6f9e46c2686649",
    "WBTC_ETH_3000": "0xCBCdF9626bC03E24f779434178A73a0B4bad62eD",
    "WBTC_ETH_500": "0x4585FE77225b41b697C938B018E2Ac67Ac5a20c0",
    "WBTC_USDC_3000": "0x99ac8cA7087fA4A2A1FB6357269965A2014ABc35",
    "WBTC_USDT_3000": "0x9Db9e0e53058C89e5B94e29621a205198648425B",
}
pool_names = [
    "DAI_USDT_500",
    "DAI_USDC_100",
    "DAI_USDC_500",
    "ETH_USDT_10000",
    "ETH_USDT_3000",
    "ETH_USDT_500",
    "SUSHI_ETH_10000",
    "SUSHI_ETH_3000",
    "SUSHI_USDC_1000",
    "SUSHI_USDT_3000",
    "UNI_ETH_3000",
    "UNI_SUSHI_10000",
    "UNI_USDC_3000",
    "UNI_USDT_3000",
    "UNI_ETH_10000",
    "USDC_ETH_10000",
    "USDC_ETH_3000",
    "USDC_ETH_500",
    "USDC_USDT_100",
    "WBTC_DAI_3000",
    "WBTC_ETH_3000",
    "WBTC_ETH_500",
    "WBTC_USDC_3000",
    "WBTC_USDT_3000",
]
ABI = [
    {"inputs": [], "stateMutability": "nonpayable", "type": "constructor"},
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"},
            {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"},
            {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "name": "Burn",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": False, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"},
            {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"},
            {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"},
        ],
        "name": "Collect",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "sender", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": False, "internalType": "uint128", "name": "amount0", "type": "uint128"},
            {"indexed": False, "internalType": "uint128", "name": "amount1", "type": "uint128"},
        ],
        "name": "CollectProtocol",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "sender", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "paid0", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "paid1", "type": "uint256"},
        ],
        "name": "Flash",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "observationCardinalityNextOld",
                "type": "uint16",
            },
            {
                "indexed": False,
                "internalType": "uint16",
                "name": "observationCardinalityNextNew",
                "type": "uint16",
            },
        ],
        "name": "IncreaseObservationCardinalityNext",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": False,
                "internalType": "uint160",
                "name": "sqrtPriceX96",
                "type": "uint160",
            },
            {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"},
        ],
        "name": "Initialize",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "address", "name": "sender", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "owner", "type": "address"},
            {"indexed": True, "internalType": "int24", "name": "tickLower", "type": "int24"},
            {"indexed": True, "internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"indexed": False, "internalType": "uint128", "name": "amount", "type": "uint128"},
            {"indexed": False, "internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"indexed": False, "internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "name": "Mint",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": False, "internalType": "uint8", "name": "feeProtocol0Old", "type": "uint8"},
            {"indexed": False, "internalType": "uint8", "name": "feeProtocol1Old", "type": "uint8"},
            {"indexed": False, "internalType": "uint8", "name": "feeProtocol0New", "type": "uint8"},
            {"indexed": False, "internalType": "uint8", "name": "feeProtocol1New", "type": "uint8"},
        ],
        "name": "SetFeeProtocol",
        "type": "event",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "sender", "type": "address"},
            {"indexed": True, "internalType": "address", "name": "recipient", "type": "address"},
            {"indexed": False, "internalType": "int256", "name": "amount0", "type": "int256"},
            {"indexed": False, "internalType": "int256", "name": "amount1", "type": "int256"},
            {
                "indexed": False,
                "internalType": "uint160",
                "name": "sqrtPriceX96",
                "type": "uint160",
            },
            {"indexed": False, "internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"indexed": False, "internalType": "int24", "name": "tick", "type": "int24"},
        ],
        "name": "Swap",
        "type": "event",
    },
    {
        "inputs": [
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"internalType": "uint128", "name": "amount", "type": "uint128"},
        ],
        "name": "burn",
        "outputs": [
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"internalType": "uint128", "name": "amount0Requested", "type": "uint128"},
            {"internalType": "uint128", "name": "amount1Requested", "type": "uint128"},
        ],
        "name": "collect",
        "outputs": [
            {"internalType": "uint128", "name": "amount0", "type": "uint128"},
            {"internalType": "uint128", "name": "amount1", "type": "uint128"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint128", "name": "amount0Requested", "type": "uint128"},
            {"internalType": "uint128", "name": "amount1Requested", "type": "uint128"},
        ],
        "name": "collectProtocol",
        "outputs": [
            {"internalType": "uint128", "name": "amount0", "type": "uint128"},
            {"internalType": "uint128", "name": "amount1", "type": "uint128"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "factory",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "fee",
        "outputs": [{"internalType": "uint24", "name": "", "type": "uint24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal0X128",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "feeGrowthGlobal1X128",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "flash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"}
        ],
        "name": "increaseObservationCardinalityNext",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"}],
        "name": "initialize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "liquidity",
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "maxLiquidityPerTick",
        "outputs": [{"internalType": "uint128", "name": "", "type": "uint128"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
            {"internalType": "uint128", "name": "amount", "type": "uint128"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "mint",
        "outputs": [
            {"internalType": "uint256", "name": "amount0", "type": "uint256"},
            {"internalType": "uint256", "name": "amount1", "type": "uint256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "observations",
        "outputs": [
            {"internalType": "uint32", "name": "blockTimestamp", "type": "uint32"},
            {"internalType": "int56", "name": "tickCumulative", "type": "int56"},
            {
                "internalType": "uint160",
                "name": "secondsPerLiquidityCumulativeX128",
                "type": "uint160",
            },
            {"internalType": "bool", "name": "initialized", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint32[]", "name": "secondsAgos", "type": "uint32[]"}],
        "name": "observe",
        "outputs": [
            {"internalType": "int56[]", "name": "tickCumulatives", "type": "int56[]"},
            {
                "internalType": "uint160[]",
                "name": "secondsPerLiquidityCumulativeX128s",
                "type": "uint160[]",
            },
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "positions",
        "outputs": [
            {"internalType": "uint128", "name": "liquidity", "type": "uint128"},
            {"internalType": "uint256", "name": "feeGrowthInside0LastX128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthInside1LastX128", "type": "uint256"},
            {"internalType": "uint128", "name": "tokensOwed0", "type": "uint128"},
            {"internalType": "uint128", "name": "tokensOwed1", "type": "uint128"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "protocolFees",
        "outputs": [
            {"internalType": "uint128", "name": "token0", "type": "uint128"},
            {"internalType": "uint128", "name": "token1", "type": "uint128"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "uint8", "name": "feeProtocol0", "type": "uint8"},
            {"internalType": "uint8", "name": "feeProtocol1", "type": "uint8"},
        ],
        "name": "setFeeProtocol",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "slot0",
        "outputs": [
            {"internalType": "uint160", "name": "sqrtPriceX96", "type": "uint160"},
            {"internalType": "int24", "name": "tick", "type": "int24"},
            {"internalType": "uint16", "name": "observationIndex", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinality", "type": "uint16"},
            {"internalType": "uint16", "name": "observationCardinalityNext", "type": "uint16"},
            {"internalType": "uint8", "name": "feeProtocol", "type": "uint8"},
            {"internalType": "bool", "name": "unlocked", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "int24", "name": "tickLower", "type": "int24"},
            {"internalType": "int24", "name": "tickUpper", "type": "int24"},
        ],
        "name": "snapshotCumulativesInside",
        "outputs": [
            {"internalType": "int56", "name": "tickCumulativeInside", "type": "int56"},
            {"internalType": "uint160", "name": "secondsPerLiquidityInsideX128", "type": "uint160"},
            {"internalType": "uint32", "name": "secondsInside", "type": "uint32"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [
            {"internalType": "address", "name": "recipient", "type": "address"},
            {"internalType": "bool", "name": "zeroForOne", "type": "bool"},
            {"internalType": "int256", "name": "amountSpecified", "type": "int256"},
            {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"},
            {"internalType": "bytes", "name": "data", "type": "bytes"},
        ],
        "name": "swap",
        "outputs": [
            {"internalType": "int256", "name": "amount0", "type": "int256"},
            {"internalType": "int256", "name": "amount1", "type": "int256"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "int16", "name": "", "type": "int16"}],
        "name": "tickBitmap",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "tickSpacing",
        "outputs": [{"internalType": "int24", "name": "", "type": "int24"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "int24", "name": "", "type": "int24"}],
        "name": "ticks",
        "outputs": [
            {"internalType": "uint128", "name": "liquidityGross", "type": "uint128"},
            {"internalType": "int128", "name": "liquidityNet", "type": "int128"},
            {"internalType": "uint256", "name": "feeGrowthOutside0X128", "type": "uint256"},
            {"internalType": "uint256", "name": "feeGrowthOutside1X128", "type": "uint256"},
            {"internalType": "int56", "name": "tickCumulativeOutside", "type": "int56"},
            {
                "internalType": "uint160",
                "name": "secondsPerLiquidityOutsideX128",
                "type": "uint160",
            },
            {"internalType": "uint32", "name": "secondsOutside", "type": "uint32"},
            {"internalType": "bool", "name": "initialized", "type": "bool"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function",
    },
]
