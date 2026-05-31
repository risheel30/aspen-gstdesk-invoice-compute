from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.auth import current_vendor
from app.db import Base, engine, get_db
from app.invoice_service import add_line, create_invoice, finalize_invoice, remove_line
from app.models import Customer, HSNSummary, Invoice, LineItem, Vendor
from app.schemas import (
    CustomerIn,
    CustomerOut,
    HSNSummaryOut,
    InvoiceCreate,
    InvoiceOut,
    InvoicePatch,
    LineItemIn,
    LineItemOut,
    VendorIn,
    VendorOut,
)
from app.seed import load_seed


app = FastAPI(title="gstdesk")


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        load_seed(db)
    finally:
        db.close()


@app.post("/vendors", response_model=VendorOut, status_code=201)
def create_vendor(payload: VendorIn, db: Session = Depends(get_db)):
    vendor = Vendor(**payload.model_dump())
    db.add(vendor)
    db.commit()
    db.refresh(vendor)
    return vendor


@app.get("/vendors/{vendor_id}", response_model=VendorOut)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="vendor not found")
    return vendor


@app.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(payload: CustomerIn, db: Session = Depends(get_db)):
    customer = Customer(**payload.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="customer not found")
    return customer


@app.post("/invoices", response_model=InvoiceOut, status_code=201)
def create_invoice_route(
    payload: InvoiceCreate,
    vendor: Vendor = Depends(current_vendor),
    db: Session = Depends(get_db),
):
    invoice = create_invoice(db, vendor, payload.number, payload.customer_id, payload.pos_override)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.get("/invoices/{invoice_id}", response_model=InvoiceOut)
def get_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    return invoice


@app.patch("/invoices/{invoice_id}", response_model=InvoiceOut)
def patch_invoice(
    invoice_id: int,
    payload: InvoicePatch,
    vendor: Vendor = Depends(current_vendor),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.vendor_id == vendor.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    if invoice.status != "draft":
        raise HTTPException(status_code=409, detail="cannot patch a finalized invoice")
    if payload.customer_id is not None:
        invoice.customer_id = payload.customer_id
    if payload.pos_override is not None:
        invoice.pos_override = payload.pos_override
    db.flush()
    from app.place_of_supply import is_intra_state, resolve_pos
    customer = db.query(Customer).filter(Customer.id == invoice.customer_id).first()
    pos = resolve_pos(vendor, customer, invoice.pos_override)
    invoice.is_intra_state = is_intra_state(vendor.state_code, pos)
    db.commit()
    db.refresh(invoice)
    return invoice


@app.post("/invoices/{invoice_id}/lines", response_model=LineItemOut, status_code=201)
def add_line_route(
    invoice_id: int,
    payload: LineItemIn,
    vendor: Vendor = Depends(current_vendor),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.vendor_id == vendor.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    try:
        line = add_line(db, invoice, payload.hsn_code, payload.description, payload.qty, payload.unit_price_paise)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(line)
    return line


@app.delete("/invoices/{invoice_id}/lines/{line_id}", response_model=InvoiceOut)
def remove_line_route(
    invoice_id: int,
    line_id: int,
    vendor: Vendor = Depends(current_vendor),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.vendor_id == vendor.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    try:
        invoice = remove_line(db, invoice, line_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    db.commit()
    db.refresh(invoice)
    return invoice


@app.post("/invoices/{invoice_id}/finalize", response_model=InvoiceOut)
def finalize_invoice_route(
    invoice_id: int,
    vendor: Vendor = Depends(current_vendor),
    db: Session = Depends(get_db),
):
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id, Invoice.vendor_id == vendor.id).first()
    if not invoice:
        raise HTTPException(status_code=404, detail="invoice not found")
    invoice = finalize_invoice(db, invoice)
    return invoice


@app.get("/invoices/{invoice_id}/hsn-summary", response_model=list[HSNSummaryOut])
def get_hsn_summary(invoice_id: int, db: Session = Depends(get_db)):
    rows = db.query(HSNSummary).filter(HSNSummary.invoice_id == invoice_id).all()
    return rows
