HSN_SLABS = {
    "0902": 5,
    "1006": 5,
    "6109": 12,
    "8517": 18,
    "9983": 18,
    "9965": 5,
    "2403": 28,
    "8703": 28,
}

HSN_CESS = {
    "2403": 60,
    "8703": 17,
}


def get_slab(hsn_code: str) -> int:
    if hsn_code not in HSN_SLABS:
        raise ValueError(f"unknown hsn code {hsn_code}")
    return HSN_SLABS[hsn_code]


def get_cess(hsn_code: str) -> int:
    return HSN_CESS.get(hsn_code, 0)
