RCM_HSNS = {"9965"}


def is_reverse_charge(hsn_code: str) -> bool:
    return hsn_code in RCM_HSNS
