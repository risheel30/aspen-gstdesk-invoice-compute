from decimal import Decimal, ROUND_HALF_UP


def compute_line_tax(taxable_paise: int, slab: int, intra_state: bool) -> dict:
    total_tax_paise = taxable_paise * slab // 100
    if intra_state:
        half = total_tax_paise // 2
        other_half = total_tax_paise - half
        return {
            "cgst_paise": half,
            "sgst_paise": other_half,
            "igst_paise": 0,
        }
    return {
        "cgst_paise": 0,
        "sgst_paise": 0,
        "igst_paise": total_tax_paise,
    }


def compute_cess(taxable_paise: int, cess_percent: int) -> int:
    return taxable_paise * cess_percent // 100


def round_invoice_total_paise(total_paise: int) -> int:
    rupees = Decimal(total_paise) / Decimal(100)
    rounded = rupees.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    return int(rounded) * 100


def paise_to_rupee_half_up(paise: int) -> int:
    rupees = Decimal(paise) / Decimal(100)
    return int(rupees.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
