from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class VendorIn(BaseModel):
    name: str
    gstin: str
    state_code: str
    pan: str
    is_composition: bool = False


class VendorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    gstin: str
    state_code: str
    pan: str
    is_composition: bool


class CustomerIn(BaseModel):
    name: str
    gstin: Optional[str] = None
    billing_state: str
    place_of_supply: Optional[str] = None
    is_b2b: bool = True


class CustomerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    gstin: Optional[str]
    billing_state: str
    place_of_supply: Optional[str]
    is_b2b: bool


class LineItemIn(BaseModel):
    hsn_code: str
    description: str
    qty: int
    unit_price_paise: int


class LineItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    hsn_code: str
    description: str
    qty: int
    unit_price_paise: int
    taxable_paise: int
    slab: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    reverse_charge_paise: int
    reverse_charge: bool


class InvoiceCreate(BaseModel):
    number: str
    customer_id: int
    pos_override: Optional[str] = None


class InvoicePatch(BaseModel):
    customer_id: Optional[int] = None
    pos_override: Optional[str] = None


class InvoiceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: str
    vendor_id: int
    customer_id: int
    pos_override: Optional[str]
    status: str
    is_intra_state: Optional[bool]
    subtotal_paise: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
    reverse_charge_paise: int
    total_paise: int
    lines: List[LineItemOut] = []


class HSNSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    hsn_code: str
    taxable_paise: int
    cgst_paise: int
    sgst_paise: int
    igst_paise: int
    cess_paise: int
