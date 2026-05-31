from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.db import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    gstin = Column(String(15), unique=True, nullable=False)
    state_code = Column(String(2), nullable=False)
    pan = Column(String(10), nullable=False)
    is_composition = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="vendor")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    gstin = Column(String(15), nullable=True)
    billing_state = Column(String(2), nullable=False)
    place_of_supply = Column(String(2), nullable=True)
    is_b2b = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    invoices = relationship("Invoice", back_populates="customer")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True)
    number = Column(String(24), unique=True, nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    pos_override = Column(String(2), nullable=True)
    status = Column(String(16), default="draft", nullable=False)
    is_intra_state = Column(Boolean, nullable=True)
    subtotal_paise = Column(Integer, default=0, nullable=False)
    cgst_paise = Column(Integer, default=0, nullable=False)
    sgst_paise = Column(Integer, default=0, nullable=False)
    igst_paise = Column(Integer, default=0, nullable=False)
    cess_paise = Column(Integer, default=0, nullable=False)
    reverse_charge_paise = Column(Integer, default=0, nullable=False)
    total_paise = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    vendor = relationship("Vendor", back_populates="invoices")
    customer = relationship("Customer", back_populates="invoices")
    lines = relationship("LineItem", back_populates="invoice", cascade="all, delete-orphan")
    hsn_rows = relationship("HSNSummary", back_populates="invoice", cascade="all, delete-orphan")


class LineItem(Base):
    __tablename__ = "line_items"

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    hsn_code = Column(String(8), nullable=False)
    description = Column(String(200), nullable=False)
    qty = Column(Integer, nullable=False)
    unit_price_paise = Column(Integer, nullable=False)
    taxable_paise = Column(Integer, nullable=False)
    slab = Column(Integer, nullable=False)
    cgst_paise = Column(Integer, default=0, nullable=False)
    sgst_paise = Column(Integer, default=0, nullable=False)
    igst_paise = Column(Integer, default=0, nullable=False)
    cess_paise = Column(Integer, default=0, nullable=False)
    reverse_charge_paise = Column(Integer, default=0, nullable=False)
    reverse_charge = Column(Boolean, default=False, nullable=False)

    invoice = relationship("Invoice", back_populates="lines")


class HSNSummary(Base):
    __tablename__ = "hsn_summary"
    __table_args__ = (UniqueConstraint("invoice_id", "hsn_code", name="ux_hsn_per_invoice"),)

    id = Column(Integer, primary_key=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    hsn_code = Column(String(8), nullable=False)
    taxable_paise = Column(Integer, default=0, nullable=False)
    cgst_paise = Column(Integer, default=0, nullable=False)
    sgst_paise = Column(Integer, default=0, nullable=False)
    igst_paise = Column(Integer, default=0, nullable=False)
    cess_paise = Column(Integer, default=0, nullable=False)

    invoice = relationship("Invoice", back_populates="hsn_rows")
