from sqlalchemy.orm import Session

from app.models import Customer, Vendor


VENDORS = [
    {"name": "Risheel Sharma Traders", "gstin": "27ABCPS1234A1Z5", "state_code": "27", "pan": "ABCPS1234A", "is_composition": False},
    {"name": "Vaibhav Iyer Exports", "gstin": "29AAFCV9876B1Z2", "state_code": "29", "pan": "AAFCV9876B", "is_composition": False},
    {"name": "Priya Menon Foods", "gstin": "33APMPM4567C2Z8", "state_code": "33", "pan": "APMPM4567C", "is_composition": False},
    {"name": "Anjali Reddy Logistics", "gstin": "36AARPR7788D1Z4", "state_code": "36", "pan": "AARPR7788D", "is_composition": False},
    {"name": "Karthik Nair Tech", "gstin": "07AKNPN1122E1Z9", "state_code": "07", "pan": "AKNPN1122E", "is_composition": False},
    {"name": "Meera Kapoor Textiles", "gstin": "09AMKPK3344F1Z1", "state_code": "09", "pan": "AMKPK3344F", "is_composition": True},
    {"name": "Aditya Joshi Spices", "gstin": "24AAJPJ5566G1Z6", "state_code": "24", "pan": "AAJPJ5566G", "is_composition": False},
    {"name": "Pooja Bhat Crafts", "gstin": "19APBPB7788H1Z3", "state_code": "19", "pan": "APBPB7788H", "is_composition": False},
]


CUSTOMERS = [
    {"name": "Ravi Deshmukh Retail", "gstin": "27ARDPM4455J1Z7", "billing_state": "27", "place_of_supply": "27", "is_b2b": True},
    {"name": "Sneha Pillai Foods", "gstin": "29ASPPF2233K1Z2", "billing_state": "29", "place_of_supply": "29", "is_b2b": True},
    {"name": "Arjun Rao Distributors", "gstin": "36AARPR9911L1Z8", "billing_state": "36", "place_of_supply": "27", "is_b2b": True},
    {"name": "Lakshmi Iyer Stores", "gstin": "33ALIPS8822M1Z5", "billing_state": "33", "place_of_supply": "33", "is_b2b": True},
    {"name": "Vikram Shetty Trading", "gstin": "29AVSPT1100N1Z9", "billing_state": "29", "place_of_supply": "07", "is_b2b": True},
    {"name": "Neha Bansal", "gstin": None, "billing_state": "07", "place_of_supply": None, "is_b2b": False},
    {"name": "Devika Krishnan Imports", "gstin": "32ADKPI3322P1Z4", "billing_state": "32", "place_of_supply": "29", "is_b2b": True},
    {"name": "Rohan Mehta Wholesale", "gstin": "24ARMPW4433Q1Z6", "billing_state": "24", "place_of_supply": "24", "is_b2b": True},
]


def load_seed(db: Session) -> None:
    if db.query(Vendor).count() > 0:
        return
    for v in VENDORS:
        db.add(Vendor(**v))
    for c in CUSTOMERS:
        db.add(Customer(**c))
    db.commit()
