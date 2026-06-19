"""Cost-control calculations and display helpers."""

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
    "certified_percent",
    "status",
]

SUMMARY_LABELS = {
    "original_budget": "Original Budget",
    "contract_award": "Contract Award",
    "approved_vo": "Approved VO",
    "pending_vo": "Pending VO",
    "forecast_final_cost": "Forecast Final Cost",
    "budget_variance": "Budget Variance",
    "certified_payment": "Certified to Date",
    "remaining_contract_value": "Remaining Contract Value",
    "certified_percent": "Certified %",
}


def build_package_frame(package_data: list[dict]) -> pd.DataFrame:
    """Create a package DataFrame from dummy data."""
    frame = pd.DataFrame(package_data)
    return calculate_package_metrics(frame)


def calculate_package_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Return package data with QS cost-control metrics applied."""
    result = frame.copy()

    if "package" not in result:
        result["package"] = ""

    for column in MONEY_COLUMNS:
        if column not in result:
            result[column] = 0
        result[column] = pd.to_numeric(result[column], errors="coerce").fillna(0)
    result["package"] = result["package"].fillna("").astype(str)

    result["forecast_final_cost"] = (
        result["contract_award"] + result["approved_vo"] + result["pending_vo"]
    )
    result["budget_variance"] = (
        result["original_budget"] - result["forecast_final_cost"]
    )
    result["remaining_contract_value"] = (
        result["contract_award"] + result["approved_vo"] - result["certified_payment"]
    )
    contract_value = result["contract_award"] + result["approved_vo"]
    result["certified_percent"] = result["certified_payment"].where(
        contract_value > 0, 0
    ) / contract_value.where(contract_value > 0, 1)
    result["status"] = result["budget_variance"].apply(package_status)

    return result[DETAIL_COLUMNS]


def package_status(variance: float) -> str:
    """Classify budget status from variance."""
    if variance > 0:
        return "Under Budget"
    if variance < 0:
        return "Over Budget"
    return "On Budget"


def calculate_project_totals(frame: pd.DataFrame) -> dict[str, float]:
    """Calculate dashboard totals from package-level values."""
    details = calculate_package_metrics(frame)
    contract_value = details["contract_award"].sum() + details["approved_vo"].sum()
    certified_percent = (
        details["certified_payment"].sum() / contract_value
        if contract_value > 0
        else 0
    )
    return {
        "original_budget": details["original_budget"].sum(),
        "contract_award": details["contract_award"].sum(),
        "approved_vo": details["approved_vo"].sum(),
        "pending_vo": details["pending_vo"].sum(),
        "forecast_final_cost": details["forecast_final_cost"].sum(),
        "budget_variance": details["budget_variance"].sum(),
        "certified_payment": details["certified_payment"].sum(),
        "remaining_contract_value": details["remaining_contract_value"].sum(),
        "certified_percent": certified_percent,
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


def format_percent(value: float) -> str:
    """Format a decimal value as a percentage."""
    return f"{value:.1%}"


def prepare_summary_dataframe(frame: pd.DataFrame) -> pd.DataFrame:
    """Prepare project-level metrics for display and export."""
    totals = calculate_project_totals(frame)
    rows = []
    for key, label in SUMMARY_LABELS.items():
        value = totals[key]
        rows.append(
            {
                "Metric": label,
                "Value": format_percent(value)
                if key == "certified_percent"
                else format_idr(value),
            }
        )
    return pd.DataFrame(rows)


def prepare_package_summary(frame: pd.DataFrame) -> pd.DataFrame:
    """Prepare package-level metrics for display."""
    details = calculate_package_metrics(frame)
    display = details.copy()

    for column in [
        "original_budget",
        "contract_award",
        "approved_vo",
        "pending_vo",
        "forecast_final_cost",
        "budget_variance",
        "certified_payment",
        "remaining_contract_value",
    ]:
        display[column] = display[column].apply(format_idr)
    display["certified_percent"] = display["certified_percent"].apply(format_percent)

    return display_table(display)


def display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a display-friendly copy with title-case column labels."""
    result = frame.copy()
    result.columns = [column.replace("_", " ").title() for column in result.columns]
    return result
