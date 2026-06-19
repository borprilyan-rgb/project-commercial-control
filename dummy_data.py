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
        "original_budget": 12_500_000_000,
        "contract_award": 11_900_000_000,
        "approved_vo": 250_000_000,
        "pending_vo": 150_000_000,
        "certified_payment": 7_100_000_000,
    },
    {
        "package": "Foundation",
        "original_budget": 38_000_000_000,
        "contract_award": 37_200_000_000,
        "approved_vo": 1_100_000_000,
        "pending_vo": 550_000_000,
        "certified_payment": 22_800_000_000,
    },
    {
        "package": "Structure",
        "original_budget": 95_000_000_000,
        "contract_award": 93_750_000_000,
        "approved_vo": 2_600_000_000,
        "pending_vo": 1_450_000_000,
        "certified_payment": 49_500_000_000,
    },
    {
        "package": "Architecture",
        "original_budget": 58_000_000_000,
        "contract_award": 56_500_000_000,
        "approved_vo": 1_900_000_000,
        "pending_vo": 650_000_000,
        "certified_payment": 18_250_000_000,
    },
    {
        "package": "MEP",
        "original_budget": 72_500_000_000,
        "contract_award": 70_800_000_000,
        "approved_vo": 1_250_000_000,
        "pending_vo": 2_100_000_000,
        "certified_payment": 21_700_000_000,
    },
    {
        "package": "External Works",
        "original_budget": 24_000_000_000,
        "contract_award": 23_300_000_000,
        "approved_vo": 450_000_000,
        "pending_vo": 200_000_000,
        "certified_payment": 8_750_000_000,
    },
    {
        "package": "Preliminaries",
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
