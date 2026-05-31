from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Vendor


def current_vendor(
    x_vendor_gstin: str = Header(..., alias="X-Vendor-GSTIN"),
    db: Session = Depends(get_db),
) -> Vendor:
    vendor = db.query(Vendor).filter(Vendor.gstin == x_vendor_gstin).first()
    if not vendor:
        raise HTTPException(status_code=401, detail="unknown vendor gstin")
    return vendor
