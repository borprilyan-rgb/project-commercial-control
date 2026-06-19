"""In-memory dummy data for Phase 1 of the commercial control app."""

from __future__ import annotations

from copy import deepcopy

PROJECT_METADATA = {
    "name": "Aurora Residence",
    "type": "Mixed-use Apartment",
    "location": "Jakarta",
    "client_type": "Property Developer",
    "currency": "IDR",
}


PACKAGE_DATA = [
    {
        "package": "Earthwork",
        "contractor": "PT Cipta Galian Nusantara",
        "contract_number": "AR-EW-001",
        "package_status": "Ongoing",
        "procurement_status": "Contract Signed",
        "remarks": "Bulk excavation and disposal progressing on main tower zone.",
        "original_budget": 12_500_000_000,
        "contract_award": 11_900_000_000,
        "approved_vo": 250_000_000,
        "pending_vo": 150_000_000,
        "certified_payment": 7_100_000_000,
    },
    {
        "package": "Foundation",
        "contractor": "PT Pondasi Prima Konstruksi",
        "contract_number": "AR-FDN-002",
        "package_status": "Ongoing",
        "procurement_status": "Contract Signed",
        "remarks": "Bored pile works substantially complete; pile cap works ongoing.",
        "original_budget": 38_000_000_000,
        "contract_award": 37_200_000_000,
        "approved_vo": 1_100_000_000,
        "pending_vo": 550_000_000,
        "certified_payment": 22_800_000_000,
    },
    {
        "package": "Structure",
        "contractor": "PT Beton Karya Utama",
        "contract_number": "AR-STR-003",
        "package_status": "Awarded",
        "procurement_status": "Contract Signed",
        "remarks": "Main contract awarded; mobilization and shop drawings in progress.",
        "original_budget": 95_000_000_000,
        "contract_award": 93_750_000_000,
        "approved_vo": 2_600_000_000,
        "pending_vo": 1_450_000_000,
        "certified_payment": 49_500_000_000,
    },
    {
        "package": "Architecture",
        "contractor": "PT Arsitek Finishing Mandiri",
        "contract_number": "AR-ARC-004",
        "package_status": "Tendering",
        "procurement_status": "Under Evaluation",
        "remarks": "Tender clarifications closed; commercial evaluation ongoing.",
        "original_budget": 58_000_000_000,
        "contract_award": 56_500_000_000,
        "approved_vo": 1_900_000_000,
        "pending_vo": 650_000_000,
        "certified_payment": 18_250_000_000,
    },
    {
        "package": "MEP",
        "contractor": "PT Prima Daya MEP",
        "contract_number": "AR-MEP-005",
        "package_status": "Tendering",
        "procurement_status": "Tender Issued",
        "remarks": "Tender issued to shortlisted MEP contractors.",
        "original_budget": 72_500_000_000,
        "contract_award": 70_800_000_000,
        "approved_vo": 1_250_000_000,
        "pending_vo": 2_100_000_000,
        "certified_payment": 21_700_000_000,
    },
    {
        "package": "External Works",
        "contractor": "PT Lanskap Kota Sejahtera",
        "contract_number": "AR-EXT-006",
        "package_status": "Not Started",
        "procurement_status": "Tender Preparation",
        "remarks": "Scope and drawings being coordinated with landscape consultant.",
        "original_budget": 24_000_000_000,
        "contract_award": 23_300_000_000,
        "approved_vo": 450_000_000,
        "pending_vo": 200_000_000,
        "certified_payment": 8_750_000_000,
    },
    {
        "package": "Preliminaries",
        "contractor": "PT Aurora Site Services",
        "contract_number": "AR-PREL-007",
        "package_status": "Ongoing",
        "procurement_status": "Awarded",
        "remarks": "Site facilities, security, and temporary utilities active.",
        "original_budget": 18_000_000_000,
        "contract_award": 17_500_000_000,
        "approved_vo": 800_000_000,
        "pending_vo": 300_000_000,
        "certified_payment": 11_200_000_000,
    },
]


def get_initial_package_data() -> list[dict]:
    """Return a fresh copy of the initial package data."""
    return deepcopy(PACKAGE_DATA)
