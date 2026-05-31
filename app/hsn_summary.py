from sqlalchemy.orm import Session

from app.models import HSNSummary, Invoice


def rebuild_hsn_summary(db: Session, invoice_id: int) -> None:
    db.query(HSNSummary).filter(HSNSummary.invoice_id == invoice_id).delete()
    db.flush()
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if not invoice:
        return
    summary = {}
    for line in invoice.lines:
        summary[line.hsn_code] = {
            "taxable_paise": line.taxable_paise,
            "cgst_paise": line.cgst_paise,
            "sgst_paise": line.sgst_paise,
            "igst_paise": line.igst_paise,
            "cess_paise": line.cess_paise,
        }
    for hsn_code, totals in summary.items():
        row = HSNSummary(
            invoice_id=invoice_id,
            hsn_code=hsn_code,
            taxable_paise=totals["taxable_paise"],
            cgst_paise=totals["cgst_paise"],
            sgst_paise=totals["sgst_paise"],
            igst_paise=totals["igst_paise"],
            cess_paise=totals["cess_paise"],
        )
        db.add(row)
    db.flush()
