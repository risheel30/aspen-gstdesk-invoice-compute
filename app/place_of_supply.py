from typing import Optional

from app.models import Customer, Vendor


def resolve_pos(
    vendor: Vendor,
    customer: Customer,
    invoice_pos_override: Optional[str] = None,
) -> str:
    if invoice_pos_override:
        return invoice_pos_override
    return customer.billing_state


def is_intra_state(vendor_state: str, pos_state: str) -> bool:
    return vendor_state == pos_state
