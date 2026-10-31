"""Generate 10 fictional PDFs (20-100 pages) with planted facts, a few scanned pages, and questions.tsv.

Run from the project root:  python scripts/generate_dummy_pdfs.py
"""
import random
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "pdfs"
PAGE_COUNTS = [50, 100, 20, 30, 50, 50, 20, 100, 30, 100]  # one per document, in DOCS order
FACT_BASE = 210  # facts below are written for a 210-page document and rescaled

# (title, topic nouns, [(page, planted fact, question, scanned)])
DOCS = [
    ("Zephyr X200 Router Manual", ["antenna", "firmware image", "LAN port", "WiFi channel", "power adapter", "status light", "DHCP table", "firewall rule", "guest network", "QoS profile"], [
        (14, "The Zephyr X200 router carries a warranty of 24 months from the date of purchase.", "How long is the warranty on the Zephyr X200 router?", False),
        (77, "To factory reset the Zephyr X200, hold the recessed reset button for ten seconds until the amber light blinks.", "How do I factory reset the Zephyr X200?", False),
        (150, "The default admin address of the Zephyr X200 is 192.168.77.1 and it supports a maximum of 64 WiFi devices.", "What is the default admin address of the Zephyr X200?", False),
        (121, "Firmware version 4.2.9 introduced WPA3 support for the Zephyr X200.", "Which firmware version introduced WPA3 support on the Zephyr X200?", True),
    ]),
    ("Northwind HR Policy Handbook", ["leave request", "payroll cycle", "performance review", "onboarding plan", "expense claim", "training budget", "shift roster", "grievance form", "benefits portal", "probation period"], [
        (20, "Full-time employees at Northwind receive 28 days of paid annual leave per calendar year.", "How many days of annual leave do Northwind employees get?", False),
        (88, "Employees may carry forward a maximum of 5 unused leave days into the next year.", "How many unused leave days can be carried forward at Northwind?", False),
        (160, "Parental leave at Northwind is 26 weeks at full pay for the primary caregiver.", "How long is parental leave at Northwind?", False),
        (51, "Expense claims above 500 euros require written approval from the department director.", "Who must approve Northwind expense claims above 500 euros?", True),
    ]),
    ("Helios Cloud Security Guide", ["access token", "audit log", "key vault", "network segment", "identity provider", "backup snapshot", "container image", "alert rule", "service account", "patch window"], [
        (30, "Helios requires all administrator passwords to be rotated every 60 days.", "How often must Helios administrator passwords be rotated?", False),
        (95, "Security incidents classified Severity 1 must be acknowledged within 15 minutes.", "Within what time must Severity 1 incidents be acknowledged at Helios?", False),
        (180, "Helios encrypts data at rest with AES-256 and data in transit with TLS 1.3.", "What encryption does Helios use for data at rest and in transit?", False),
    ]),
    ("Aegis Card Data Compliance Manual", ["cardholder record", "tokenization service", "scan report", "access review", "log archive", "firewall ruleset", "vendor assessment", "change ticket", "segmentation test", "incident drill"], [
        (25, "Aegis retains transaction logs for 12 months, with the most recent 3 months immediately available for analysis.", "How long does Aegis retain transaction logs?", False),
        (110, "Vulnerability scans of the Aegis cardholder data environment must run at least once every quarter.", "How often must Aegis run vulnerability scans?", False),
        (190, "Access to the Aegis vault requires two-person approval and multi-factor authentication.", "What is required to access the Aegis vault?", False),
    ]),
    ("SolarArc Panel Installation Manual", ["mounting rail", "inverter", "junction box", "string cable", "roof anchor", "grounding lug", "monitoring gateway", "tilt bracket", "isolator switch", "cleaning cycle"], [
        (18, "SolarArc SA-440 panels must be mounted at a tilt angle of 32 degrees in the northern hemisphere.", "What tilt angle is required for SolarArc SA-440 panels?", False),
        (99, "The maximum string voltage for a SolarArc array is 1000 volts DC.", "What is the maximum string voltage for a SolarArc array?", False),
        (170, "SolarArc panels carry a 25-year performance warranty guaranteeing at least 87 percent of rated output.", "What performance warranty do SolarArc panels have?", False),
    ]),
    ("Meridian Hospital Care Protocols", ["triage nurse", "ward round", "medication chart", "sterile kit", "discharge summary", "isolation room", "blood sample", "handover note", "visiting hour", "infusion pump"], [
        (40, "Meridian Hospital requires hand hygiene checks at every patient room entry, audited weekly by the infection control team.", "How are hand hygiene checks audited at Meridian Hospital?", False),
        (120, "Adult patients triaged as Category 2 must be seen by a physician within 10 minutes.", "How quickly must Category 2 adult patients be seen at Meridian?", False),
        (200, "The Meridian pharmacy stores insulin at a temperature between 2 and 8 degrees Celsius.", "At what temperature does the Meridian pharmacy store insulin?", False),
    ]),
    ("VoltWay EV Charging Network Guide", ["charging bay", "payment kiosk", "load balancer", "connector cable", "session record", "tariff plan", "station controller", "cooling unit", "reservation slot", "fault code"], [
        (35, "VoltWay fast chargers deliver up to 150 kilowatts and charge a typical vehicle from 10 to 80 percent in 28 minutes.", "How fast do VoltWay fast chargers charge a typical vehicle?", False),
        (105, "A VoltWay charging session is automatically stopped after 90 minutes of idle time.", "When is a VoltWay charging session automatically stopped?", False),
        (175, "The VoltWay station uptime target is 99.2 percent measured monthly.", "What is the VoltWay station uptime target?", False),
    ]),
    ("GreenField Soil and Crop Handbook", ["seed drill", "irrigation line", "compost heap", "field plot", "harvest crew", "soil sample", "pest trap", "storage silo", "weather log", "nutrient plan"], [
        (22, "GreenField recommends a soil pH between 6.0 and 6.8 for wheat cultivation.", "What soil pH does GreenField recommend for wheat?", False),
        (92, "Wheat seed should be sown at a depth of 4 centimetres with 20 centimetres row spacing.", "At what depth should wheat seed be sown according to GreenField?", False),
        (185, "Crop rotation at GreenField follows a four-year cycle: wheat, legumes, maize, fallow.", "What crop rotation cycle does GreenField follow?", False),
    ]),
    ("Orion-7 Mission Operations Manual", ["flight controller", "thruster burn", "telemetry frame", "docking port", "life support loop", "star tracker", "ground station", "fuel tank", "solar wing", "navigation fix"], [
        (28, "The Orion-7 spacecraft has a nominal crew of four and a mission duration of 210 days.", "What is the nominal crew size and mission duration of Orion-7?", False),
        (115, "Orion-7 mission control declares a communications blackout if no signal is received for 45 minutes.", "When does Orion-7 mission control declare a communications blackout?", False),
        (195, "The Orion-7 main engine produces 33 kilonewtons of thrust.", "How much thrust does the Orion-7 main engine produce?", False),
    ]),
    ("Atlas Warehouse Logistics SOP", ["pallet", "dock door", "forklift", "pick list", "barcode scanner", "cycle count", "returns bay", "carrier manifest", "storage rack", "dispatch lane"], [
        (32, "Atlas warehouses must complete inbound goods inspection within 4 hours of truck arrival.", "Within how many hours must Atlas complete inbound goods inspection?", False),
        (108, "Forklift operators at Atlas must hold a valid certification renewed every 24 months.", "How often must Atlas forklift certification be renewed?", False),
        (178, "The Atlas picking accuracy target is 99.7 percent, measured per 10000 order lines.", "What is the Atlas picking accuracy target?", False),
    ]),
]

ROLES = ["shift supervisor", "site manager", "quality lead", "compliance officer", "operations director"]
UNITS = ["days", "weeks", "months", "hours"]
TEMPLATES = [
    "The {a} must be inspected every {n} {u} to ensure the {b} remains within tolerance.",
    "Operators should record the {a} reading in the {b} log before starting any maintenance task.",
    "If the {a} exceeds {n} percent of its rated value, the {b} should be isolated and reported to the {r}.",
    "A qualified person reviews the {a} procedure together with the {b} checklist during each audit cycle.",
    "Section {s} describes how the {a} interacts with the {b} under normal operating conditions.",
    "Replacement of the {a} requires approval from the {r} and a written note in the {b} record.",
    "Training on the {a} is repeated every {n} {u} and signed off by the {r}.",
    "When the {a} is unavailable, the team falls back to the {b} and informs the {r} immediately.",
    "Documentation for the {a} is stored alongside the {b} and reviewed after every {n} {u}.",
    "The {r} verifies that each {a} change is reflected in the {b} before sign-off.",
]


def slug(title: str) -> str:
    return title.replace(" ", "_").replace("-", "") + ".pdf"


def page_text(rnd: random.Random, title: str, nouns: list[str], p: int, planted: str | None) -> str:
    chapter, section = (p - 1) // 15 + 1, (p - 1) % 15 + 1
    sentences = []
    for _ in range(22):
        sentences.append(rnd.choice(TEMPLATES).format(
            a=rnd.choice(nouns), b=rnd.choice(nouns), r=rnd.choice(ROLES),
            u=rnd.choice(UNITS), n=rnd.randint(2, 90), s=f"{chapter}.{section}"))
    ref = f"Reference code {title[:3].upper()}-{p:03d}-{rnd.randint(1000, 9999)} applies to this page."
    sentences.insert(rnd.randint(5, 15), ref)
    if planted:
        sentences.insert(rnd.randint(6, 14), planted)
    paras = [" ".join(sentences[i:i + 6]) for i in range(0, len(sentences), 6)]
    return f"Chapter {chapter}, Section {section}\n\n" + "\n\n".join(paras)


def draw(page, title: str, p: int, body: str) -> None:
    page.insert_text((50, 36), f"{title} - Internal Use", fontsize=8)
    page.insert_text((270, 820), f"Page {p}", fontsize=8)
    rc = page.insert_textbox(pymupdf.Rect(50, 55, 545, 805), body, fontsize=10)
    assert rc >= 0, f"text overflow on page {p}"


def build(title: str, nouns: list[str], facts: list, doc_idx: int) -> list[str]:
    rnd = random.Random(1000 + doc_idx)
    pages = PAGE_COUNTS[doc_idx]
    used, scaled = set(), []
    for pg, f, q, sc in facts:  # rescale to this document's length, keeping pages distinct
        new = max(2, min(pages - 2, round(pg * pages / FACT_BASE)))
        while new in used or new + 1 in used or new - 1 in used:
            new = new + 3 if new + 3 <= pages - 1 else new - 3
        used.add(new)
        scaled.append((new, f, q, sc))
    facts = scaled
    planted = {pg: f for pg, f, _, _ in facts}
    scanned = {pg + k for pg, _, _, sc in facts if sc for k in (0, 1)}
    doc = pymupdf.open()
    for p in range(1, pages + 1):
        body = page_text(rnd, title, nouns, p, planted.get(p))
        if p in scanned:  # render to an image so only OCR can read it
            tmp = pymupdf.open()
            draw(tmp.new_page(), title, p, body)
            pix = tmp[0].get_pixmap(dpi=150)
            tmp.close()
            page = doc.new_page()
            page.insert_image(page.rect, pixmap=pix)
        else:
            draw(doc.new_page(), title, p, body)
    doc.save(OUT / slug(title), deflate=True)
    doc.close()
    return [f"{q}\t{slug(title)}\t{pg}" for pg, _, q, _ in facts]


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (title, nouns, facts) in enumerate(DOCS):
        rows += build(title, nouns, facts, i)
        print(f"wrote {slug(title)} ({PAGE_COUNTS[i]} pages)")
    (ROOT / "questions.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"wrote questions.tsv ({len(rows)} questions)")
