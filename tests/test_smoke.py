def test_seed_loaded(client, db):
    from app.models import Vendor, Customer
    assert db.query(Vendor).count() == 8
    assert db.query(Customer).count() == 8


def test_create_vendor_then_fetch(client):
    payload = {
        "name": "Sahil Khanna Logistics",
        "gstin": "27ASKPL5566R1Z9",
        "state_code": "27",
        "pan": "ASKPL5566R",
        "is_composition": False,
    }
    r = client.post("/vendors", json=payload)
    assert r.status_code == 201
    vid = r.json()["id"]
    g = client.get(f"/vendors/{vid}")
    assert g.status_code == 200
    assert g.json()["name"] == "Sahil Khanna Logistics"


def test_create_customer_then_fetch(client):
    payload = {
        "name": "Tanvi Reddy",
        "gstin": "29ATRPK6677S1Z0",
        "billing_state": "29",
        "place_of_supply": "29",
        "is_b2b": True,
    }
    r = client.post("/customers", json=payload)
    assert r.status_code == 201
    cid = r.json()["id"]
    g = client.get(f"/customers/{cid}")
    assert g.status_code == 200
    assert g.json()["billing_state"] == "29"


def test_draft_invoice_with_one_line(client, auth_risheel):
    inv = client.post(
        "/invoices",
        json={"number": "INV-001", "customer_id": 1, "pos_override": None},
        headers=auth_risheel,
    )
    assert inv.status_code == 201
    iid = inv.json()["id"]
    line = client.post(
        f"/invoices/{iid}/lines",
        json={"hsn_code": "8517", "description": "Mobile phone", "qty": 2, "unit_price_paise": 50000},
        headers=auth_risheel,
    )
    assert line.status_code == 201
    body = line.json()
    assert body["taxable_paise"] == 100000
    assert body["slab"] == 18


def test_finalize_intra_state_invoice(client, auth_risheel):
    inv = client.post(
        "/invoices",
        json={"number": "INV-002", "customer_id": 1, "pos_override": None},
        headers=auth_risheel,
    )
    iid = inv.json()["id"]
    client.post(
        f"/invoices/{iid}/lines",
        json={"hsn_code": "8517", "description": "Mobile phone", "qty": 1, "unit_price_paise": 100000},
        headers=auth_risheel,
    )
    client.post(
        f"/invoices/{iid}/lines",
        json={"hsn_code": "9983", "description": "Consulting", "qty": 1, "unit_price_paise": 50000},
        headers=auth_risheel,
    )
    fin = client.post(f"/invoices/{iid}/finalize", headers=auth_risheel)
    assert fin.status_code == 200
    body = fin.json()
    assert body["status"] == "finalized"
    assert body["total_paise"] % 100 == 0


def test_hsn_summary_after_finalize(client, auth_risheel):
    inv = client.post(
        "/invoices",
        json={"number": "INV-003", "customer_id": 1, "pos_override": None},
        headers=auth_risheel,
    )
    iid = inv.json()["id"]
    client.post(
        f"/invoices/{iid}/lines",
        json={"hsn_code": "8517", "description": "Mobile A", "qty": 1, "unit_price_paise": 100000},
        headers=auth_risheel,
    )
    client.post(
        f"/invoices/{iid}/lines",
        json={"hsn_code": "9983", "description": "Consulting", "qty": 1, "unit_price_paise": 50000},
        headers=auth_risheel,
    )
    client.post(f"/invoices/{iid}/finalize", headers=auth_risheel)
    s = client.get(f"/invoices/{iid}/hsn-summary")
    assert s.status_code == 200
    hsns = {row["hsn_code"] for row in s.json()}
    assert "8517" in hsns
    assert "9983" in hsns
