"""Cost-control calculations for the demo dashboard."""

from __future__ import annotations

import pandas as pd


MONEY_COLUMNS = [
    "original_budget",
    "contract_award",
    "approved_vo",
    "pending_vo",
    "certified_payment",
]


DETAIL_COLUMNS = [
    "package",
    "original_budget",
    "contract_award",
    "approved_vo",
    "pending_vo",
    "forecast_final_cost",
    "budget_variance",
    "certified_payment",
    "remaining_contract_value",
    "status",
]


def build_package_frame(package_data: list[dict]) -> pd.DataFrame:
    """Create a package DataFrame from dummy data."""
    frame = pd.DataFrame(package_data)
    return calculate_package_metrics(frame)


def calculate_package_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Return package data with QS cost-control metrics applied."""
    result = frame.copy()

    for column in MONEY_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0)

    result["forecast_final_cost"] = (
        result["contract_award"] + result["approved_vo"] + result["pending_vo"]
    )
    result["budget_variance"] = (
        result["original_budget"] - result["forecast_final_cost"]
    )
    result["remaining_contract_value"] = (
        result["contract_award"] + result["approved_vo"] - result["certified_payment"]
    )
    result["status"] = result["budget_variance"].apply(package_status)

    return result[DETAIL_COLUMNS]


def package_status(variance: float) -> str:
    """Classify budget status from variance."""
    if variance > 0:
        return "Under Budget"
    if variance < 0:
        return "Over Budget"
    return "On Budget"


def summarize_totals(frame: pd.DataFrame) -> dict[str, float]:
    """Calculate dashboard totals from package-level values."""
    details = calculate_package_metrics(frame)
    return {
        "original_budget": details["original_budget"].sum(),
        "contract_award": details["contract_award"].sum(),
        "approved_vo": details["approved_vo"].sum(),
        "pending_vo": details["pending_vo"].sum(),
        "forecast_final_cost": details["forecast_final_cost"].sum(),
        "budget_variance": details["budget_variance"].sum(),
        "certified_payment": details["certified_payment"].sum(),
        "remaining_contract_value": details["remaining_contract_value"].sum(),
    }


def format_idr(value: float) -> str:
    """Format a number as compact Indonesian Rupiah."""
    sign = "-" if value < 0 else ""
    absolute_value = abs(value)

    if absolute_value >= 1_000_000_000:
        return f"{sign}Rp {absolute_value / 1_000_000_000:,.2f}B"
    if absolute_value >= 1_000_000:
        return f"{sign}Rp {absolute_value / 1_000_000:,.2f}M"
    return f"{sign}Rp {absolute_value:,.0f}"


def display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a display-friendly copy with title-case column labels."""
    result = frame.copy()
    result.columns = [column.replace("_", " ").title() for column in result.columns]
    return result
