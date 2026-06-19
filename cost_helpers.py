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

TEXT_COLUMNS = [
    "package",
    "contractor",
    "contract_number",
    "package_status",
    "procurement_status",
    "remarks",
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
    "risk_level",
]

REGISTER_COLUMNS = [
    "package",
    "contractor",
    "contract_number",
    "package_status",
    "procurement_status",
    "risk_level",
    "remarks",
]

DASHBOARD_DISPLAY_COLUMNS = [
    "package",
    "original_budget",
    "contract_award",
    "approved_vo",
    "pending_vo",
    "forecast_final_cost",
    "budget_variance",
    "certified_percent",
    "remaining_contract_value",
    "status",
    "risk_level",
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

DISPLAY_LABELS = {
    "package": "Package",
    "original_budget": "Original Budget",
    "contract_award": "Contract Award",
    "approved_vo": "Approved VO",
    "pending_vo": "Pending VO",
    "forecast_final_cost": "Forecast Final Cost",
    "budget_variance": "Budget Variance",
    "certified_percent": "Certified %",
    "remaining_contract_value": "Remaining Contract Value",
    "status": "Status",
    "risk_level": "Risk Level",
    "contractor": "Contractor",
    "contract_number": "Contract Number",
    "package_status": "Package Status",
    "procurement_status": "Procurement Status",
    "remarks": "Remarks",
}


def build_package_frame(package_data: list[dict]) -> pd.DataFrame:
    """Create a package DataFrame from dummy data."""
    frame = pd.DataFrame(package_data)
    return calculate_package_metrics(frame)


def calculate_package_metrics(frame: pd.DataFrame) -> pd.DataFrame:
    """Return package data with QS cost-control metrics applied."""
    result = frame.copy()

    for column in TEXT_COLUMNS:
        if column not in result:
            result[column] = ""
        result[column] = result[column].fillna("").astype(str)

    for column in MONEY_COLUMNS:
        if column not in result:
            result[column] = 0
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
    contract_value = result["contract_award"] + result["approved_vo"]
    result["certified_percent"] = result["certified_payment"].where(
        contract_value > 0, 0
    ) / contract_value.where(contract_value > 0, 1)
    result["status"] = result["budget_variance"].apply(package_status)
    result["risk_level"] = result.apply(
        lambda row: package_risk_level(
            row["original_budget"],
            row["budget_variance"],
        ),
        axis=1,
    )

    return result[DETAIL_COLUMNS]


def package_status(variance: float) -> str:
    """Classify budget status from variance."""
    if variance > 0:
        return "Under Budget"
    if variance < 0:
        return "Over Budget"
    return "On Budget"


def package_risk_level(original_budget: float, budget_variance: float) -> str:
    """Classify package risk from budget headroom."""
    if original_budget <= 0:
        return "No Budget"
    if budget_variance < 0:
        return "High Risk"
    if budget_variance <= original_budget * 0.05:
        return "Medium Risk"
    return "Low Risk"


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


def calculate_dashboard_indicators(frame: pd.DataFrame) -> dict[str, float]:
    """Calculate dashboard-level package count and risk indicators."""
    details = calculate_package_metrics(frame)
    return {
        "package_count": len(details),
        "under_budget_count": int((details["status"] == "Under Budget").sum()),
        "over_budget_count": int((details["status"] == "Over Budget").sum()),
        "high_risk_count": int((details["risk_level"] == "High Risk").sum()),
        "average_certified_percent": details["certified_percent"].mean()
        if len(details) > 0
        else 0,
    }


def calculate_package_status_indicators(frame: pd.DataFrame) -> dict[str, int]:
    """Calculate package register status indicators."""
    working = frame.copy()
    if "package_status" not in working:
        working["package_status"] = ""
    if "procurement_status" not in working:
        working["procurement_status"] = ""

    package_status = working["package_status"].fillna("").astype(str)
    procurement_status = working["procurement_status"].fillna("").astype(str)
    tender_statuses = {
        "Budget Only",
        "Tender Preparation",
        "Tender Issued",
        "Under Evaluation",
    }

    return {
        "awarded_count": int((package_status == "Awarded").sum()),
        "ongoing_count": int((package_status == "Ongoing").sum()),
        "completed_closed_count": int(
            package_status.isin(["Completed", "Closed"]).sum()
        ),
        "in_procurement_count": int(procurement_status.isin(tender_statuses).sum()),
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
    details = calculate_package_metrics(frame)[DASHBOARD_DISPLAY_COLUMNS]
    display = details.copy()

    for column in [
        "original_budget",
        "contract_award",
        "approved_vo",
        "pending_vo",
        "forecast_final_cost",
        "budget_variance",
        "remaining_contract_value",
    ]:
        display[column] = display[column].apply(format_idr)
    display["certified_percent"] = display["certified_percent"].apply(format_percent)

    return display.rename(columns=DISPLAY_LABELS)


def prepare_package_register(frame: pd.DataFrame) -> pd.DataFrame:
    """Prepare package register metadata with calculated risk level."""
    details = calculate_package_metrics(frame)
    register = frame.copy()

    for column in TEXT_COLUMNS:
        if column not in register:
            register[column] = ""
        register[column] = register[column].fillna("").astype(str)
    register["risk_level"] = details["risk_level"].values

    return register[REGISTER_COLUMNS].rename(columns=DISPLAY_LABELS)


def display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a display-friendly copy with title-case column labels."""
    result = frame.copy()
    result.columns = [column.replace("_", " ").title() for column in result.columns]
    return result
