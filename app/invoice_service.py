from sqlalchemy.orm import Session

from app.hsn_catalog import get_cess, get_slab
from app.hsn_summary import rebuild_hsn_summary
from app.models import Customer, Invoice, LineItem, Vendor
from app.place_of_supply import is_intra_state, resolve_pos
from app.reverse_charge import is_reverse_charge
from app.tax import compute_cess, compute_line_tax, round_invoice_total_paise


def create_invoice(
    db: Session, vendor: Vendor, number: str, customer_id: int, pos_override: str | None
) -> Invoice:
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise ValueError("customer not found")
    pos = resolve_pos(vendor, customer, pos_override)
    intra = is_intra_state(vendor.state_code, pos)
    invoice = Invoice(
        number=number,
        vendor_id=vendor.id,
        customer_id=customer.id,
        pos_override=pos_override,
        status="draft",
        is_intra_state=intra,
    )
    db.add(invoice)
    db.flush()
    return invoice


def add_line(db: Session, invoice: Invoice, hsn_code: str, description: str, qty: int, unit_price_paise: int) -> LineItem:
    if invoice.status != "draft":
        raise ValueError("cannot add line to a finalized invoice")
    slab = get_slab(hsn_code)
    taxable_paise = qty * unit_price_paise
    vendor = invoice.vendor
    customer = invoice.customer
    pos = resolve_pos(vendor, customer, invoice.pos_override)
    intra = is_intra_state(vendor.state_code, pos)
    rcm = is_reverse_charge(hsn_code)
    if rcm:
        tax = {"cgst_paise": 0, "sgst_paise": 0, "igst_paise": 0}
        rcm_amount = taxable_paise * slab // 100
    else:
        tax = compute_line_tax(taxable_paise, slab, intra)
        rcm_amount = 0
    cess_percent = get_cess(hsn_code)
    inclusive_base = taxable_paise + tax["cgst_paise"] + tax["sgst_paise"] + tax["igst_paise"]
    cess = compute_cess(inclusive_base, cess_percent)
    line = LineItem(
        invoice_id=invoice.id,
        hsn_code=hsn_code,
        description=description,
        qty=qty,
        unit_price_paise=unit_price_paise,
        taxable_paise=taxable_paise,
        slab=slab,
        cgst_paise=tax["cgst_paise"],
        sgst_paise=tax["sgst_paise"],
        igst_paise=tax["igst_paise"],
        cess_paise=cess,
        reverse_charge_paise=rcm_amount,
        reverse_charge=rcm,
    )
    db.add(line)
    invoice.is_intra_state = intra
    db.flush()
    _recompute_totals(db, invoice)
    return line


def remove_line(db: Session, invoice: Invoice, line_id: int) -> Invoice:
    if invoice.status != "draft":
        raise ValueError("cannot remove line from a finalized invoice")
    line = db.query(LineItem).filter(LineItem.id == line_id, LineItem.invoice_id == invoice.id).first()
    if not line:
        raise ValueError("line not found")
    db.delete(line)
    db.flush()
    db.refresh(invoice)
    _recompute_totals(db, invoice)
    return invoice


def finalize_invoice(db: Session, invoice: Invoice) -> Invoice:
    if invoice.status == "finalized":
        return invoice
    _recompute_totals(db, invoice)
    invoice.total_paise = round_invoice_total_paise(invoice.total_paise)
    invoice.status = "finalized"
    db.flush()
    rebuild_hsn_summary(db, invoice.id)
    db.commit()
    db.refresh(invoice)
    return invoice


def _recompute_totals(db: Session, invoice: Invoice) -> None:
    subtotal = 0
    cgst = 0
    sgst = 0
    igst = 0
    cess = 0
    rcm = 0
    for line in invoice.lines:
        subtotal += line.taxable_paise
        cgst += line.cgst_paise
        sgst += line.sgst_paise
        igst += line.igst_paise
        cess += line.cess_paise
        rcm += line.reverse_charge_paise
    invoice.subtotal_paise = subtotal
    invoice.cgst_paise = cgst
    invoice.sgst_paise = sgst
    invoice.igst_paise = igst
    invoice.cess_paise = cess
    invoice.reverse_charge_paise = rcm
    invoice.total_paise = subtotal + cgst + sgst + igst + cess
    db.flush()
