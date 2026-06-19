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

VO_AMOUNT_COLUMNS = [
    "submitted_amount",
    "approved_amount",
    "pending_amount",
]

VO_TEXT_COLUMNS = [
    "vo_no",
    "package",
    "description",
    "vo_status",
    "remarks",
]

CLAIM_AMOUNT_COLUMNS = [
    "submitted_amount",
    "certified_amount",
    "payment_amount",
]

CLAIM_TEXT_COLUMNS = [
    "claim_no",
    "period",
    "package",
    "contractor",
    "claim_status",
    "remarks",
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

VARIATION_REGISTER_COLUMNS = [
    "vo_no",
    "package",
    "description",
    "vo_status",
    "submitted_amount",
    "approved_amount",
    "pending_amount",
    "remarks",
]

CLAIM_REGISTER_COLUMNS = [
    "claim_no",
    "period",
    "package",
    "contractor",
    "claim_status",
    "submitted_amount",
    "certified_amount",
    "payment_amount",
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
    "vo_no": "VO No.",
    "description": "Description",
    "vo_status": "VO Status",
    "submitted_amount": "Submitted Amount",
    "approved_amount": "Approved Amount",
    "pending_amount": "Pending Amount",
    "claim_no": "Claim No.",
    "period": "Period",
    "claim_status": "Claim Status",
    "certified_amount": "Certified Amount",
    "payment_amount": "Payment Amount",
}


def build_package_frame(package_data: list[dict]) -> pd.DataFrame:
    """Create a package DataFrame from dummy data."""
    frame = pd.DataFrame(package_data)
    return calculate_package_metrics(frame)


def calculate_vo_summary_by_package(vo_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Summarize approved and pending VO amounts by package."""
    if vo_frame is None or vo_frame.empty:
        return pd.DataFrame(columns=["package", "approved_vo", "pending_vo"])

    variations = normalize_vo_data(vo_frame)
    summary = (
        variations.groupby("package", as_index=False)[
            ["approved_amount", "pending_amount"]
        ]
        .sum()
        .rename(
            columns={
                "approved_amount": "approved_vo",
                "pending_amount": "pending_vo",
            }
        )
    )
    return summary


def normalize_vo_data(vo_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Return VO records with required columns and numeric amount fields."""
    if vo_frame is None:
        variations = pd.DataFrame(columns=VARIATION_REGISTER_COLUMNS)
    else:
        variations = vo_frame.copy()

    for column in VO_TEXT_COLUMNS:
        if column not in variations:
            variations[column] = ""
        variations[column] = variations[column].fillna("").astype(str)

    for column in VO_AMOUNT_COLUMNS:
        if column not in variations:
            variations[column] = 0
        variations[column] = pd.to_numeric(
            variations[column],
            errors="coerce",
        ).fillna(0)

    return variations[VARIATION_REGISTER_COLUMNS]


def apply_vo_summary(frame: pd.DataFrame, vo_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Apply VO register totals to package-level approved and pending VO fields."""
    result = frame.copy()
    if vo_frame is None:
        return result

    vo_summary = calculate_vo_summary_by_package(vo_frame)
    result = result.drop(columns=["approved_vo", "pending_vo"], errors="ignore")
    result = result.merge(vo_summary, on="package", how="left")
    result["approved_vo"] = result["approved_vo"].fillna(0)
    result["pending_vo"] = result["pending_vo"].fillna(0)
    return result


def normalize_claim_data(claim_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Return claim records with required columns and numeric amount fields."""
    if claim_frame is None:
        claims = pd.DataFrame(columns=CLAIM_REGISTER_COLUMNS)
    else:
        claims = claim_frame.copy()

    for column in CLAIM_TEXT_COLUMNS:
        if column not in claims:
            claims[column] = ""
        claims[column] = claims[column].fillna("").astype(str)

    for column in CLAIM_AMOUNT_COLUMNS:
        if column not in claims:
            claims[column] = 0
        claims[column] = pd.to_numeric(
            claims[column],
            errors="coerce",
        ).fillna(0)

    return claims[CLAIM_REGISTER_COLUMNS]


def calculate_claim_summary_by_package(
    claim_frame: pd.DataFrame | None,
) -> pd.DataFrame:
    """Summarize certified and paid amounts by package."""
    if claim_frame is None or claim_frame.empty:
        return pd.DataFrame(columns=["package", "certified_payment", "payment_amount"])

    claims = normalize_claim_data(claim_frame)
    summary = (
        claims.groupby("package", as_index=False)[
            ["certified_amount", "payment_amount"]
        ]
        .sum()
        .rename(
            columns={
                "certified_amount": "certified_payment",
                "payment_amount": "payment_amount",
            }
        )
    )
    return summary


def apply_claim_summary(
    frame: pd.DataFrame,
    claim_frame: pd.DataFrame | None,
) -> pd.DataFrame:
    """Apply claim register totals to package-level certified payment fields."""
    result = frame.copy()
    if claim_frame is None:
        return result

    claim_summary = calculate_claim_summary_by_package(claim_frame)
    result = result.drop(columns=["certified_payment", "payment_amount"], errors="ignore")
    result = result.merge(claim_summary, on="package", how="left")
    result["certified_payment"] = result["certified_payment"].fillna(0)
    result["payment_amount"] = result["payment_amount"].fillna(0)
    return result


def calculate_package_metrics(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Return package data with QS cost-control metrics applied."""
    result = apply_vo_summary(frame, vo_frame)
    result = apply_claim_summary(result, claim_frame)

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


def calculate_project_totals(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> dict[str, float]:
    """Calculate dashboard totals from package-level values."""
    details = calculate_package_metrics(frame, vo_frame, claim_frame)
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


def calculate_dashboard_indicators(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> dict[str, float]:
    """Calculate dashboard-level package count and risk indicators."""
    details = calculate_package_metrics(frame, vo_frame, claim_frame)
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


def calculate_vo_indicators(vo_frame: pd.DataFrame | None) -> dict[str, float]:
    """Calculate dashboard-level VO register indicators."""
    variations = normalize_vo_data(vo_frame)
    review_statuses = {"Pending", "Under Review"}
    return {
        "submitted_vo_total": variations["submitted_amount"].sum(),
        "approved_vo_total": variations["approved_amount"].sum(),
        "pending_vo_total": variations["pending_amount"].sum(),
        "approved_vo_count": int((variations["vo_status"] == "Approved").sum()),
        "pending_review_vo_count": int(
            variations["vo_status"].isin(review_statuses).sum()
        ),
    }


def calculate_claim_indicators(claim_frame: pd.DataFrame | None) -> dict[str, float]:
    """Calculate dashboard-level progress claim indicators."""
    claims = normalize_claim_data(claim_frame)
    return {
        "submitted_claim_total": claims["submitted_amount"].sum(),
        "certified_claim_total": claims["certified_amount"].sum(),
        "paid_total": claims["payment_amount"].sum(),
        "certified_claim_count": int((claims["claim_status"] == "Certified").sum()),
        "under_review_claim_count": int(
            (claims["claim_status"] == "Under Review").sum()
        ),
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


def prepare_summary_dataframe(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Prepare project-level metrics for display and export."""
    totals = calculate_project_totals(frame, vo_frame, claim_frame)
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


def prepare_package_summary(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Prepare package-level metrics for display."""
    details = calculate_package_metrics(frame, vo_frame, claim_frame)[
        DASHBOARD_DISPLAY_COLUMNS
    ]
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


def prepare_package_register(
    frame: pd.DataFrame,
    vo_frame: pd.DataFrame | None = None,
    claim_frame: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Prepare package register metadata with calculated risk level."""
    details = calculate_package_metrics(frame, vo_frame, claim_frame)
    register = frame.copy()

    for column in TEXT_COLUMNS:
        if column not in register:
            register[column] = ""
        register[column] = register[column].fillna("").astype(str)
    register["risk_level"] = details["risk_level"].values

    return register[REGISTER_COLUMNS].rename(columns=DISPLAY_LABELS)


def prepare_variation_register(vo_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Prepare detailed VO records for display and export."""
    variations = normalize_vo_data(vo_frame).copy()
    display = variations.copy()

    for column in VO_AMOUNT_COLUMNS:
        display[column] = display[column].apply(format_idr)

    return display.rename(columns=DISPLAY_LABELS)


def prepare_claim_register(claim_frame: pd.DataFrame | None) -> pd.DataFrame:
    """Prepare detailed progress claim records for display and export."""
    claims = normalize_claim_data(claim_frame).copy()
    display = claims.copy()

    for column in CLAIM_AMOUNT_COLUMNS:
        display[column] = display[column].apply(format_idr)

    return display.rename(columns=DISPLAY_LABELS)


def display_table(frame: pd.DataFrame) -> pd.DataFrame:
    """Return a display-friendly copy with title-case column labels."""
    result = frame.copy()
    result.columns = [column.replace("_", " ").title() for column in result.columns]
    return result
