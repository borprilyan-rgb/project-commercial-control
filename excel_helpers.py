"""Excel export helpers for the Aurora Residence dashboard."""

from __future__ import annotations

from io import BytesIO

import pandas as pd

from cost_helpers import calculate_package_metrics, summarize_totals


SUMMARY_LABELS = {
    "original_budget": "Original Budget",
    "contract_award": "Contract Award",
    "approved_vo": "Approved VO",
    "pending_vo": "Pending VO",
    "forecast_final_cost": "Forecast Final Cost",
    "budget_variance": "Budget Variance",
    "certified_payment": "Certified to Date",
    "remaining_contract_value": "Remaining Contract Value",
}


def create_excel_report(project_metadata: dict, package_frame: pd.DataFrame) -> bytes:
    """Create an in-memory Excel report with summary and package detail sheets."""
    output = BytesIO()
    package_details = calculate_package_metrics(package_frame)
    totals = summarize_totals(package_frame)

    summary_rows = [
        {"Item": "Project Name", "Value": project_metadata["name"]},
        {"Item": "Project Type", "Value": project_metadata["type"]},
        {"Item": "Location", "Value": project_metadata["location"]},
        {"Item": "", "Value": ""},
    ]
    summary_rows.extend(
        {"Item": SUMMARY_LABELS[key], "Value": value}
        for key, value in totals.items()
    )
    summary_frame = pd.DataFrame(summary_rows)

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary_frame.to_excel(writer, sheet_name="Summary", index=False)
        package_details.to_excel(writer, sheet_name="Package Details", index=False)

        workbook = writer.book
        money_format = workbook.add_format({"num_format": '"Rp" #,##0'})
        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#EAF2F8", "border": 1}
        )

        for sheet_name, frame in {
            "Summary": summary_frame,
            "Package Details": package_details,
        }.items():
            worksheet = writer.sheets[sheet_name]
            for column_index, column_name in enumerate(frame.columns):
                worksheet.write(0, column_index, column_name, header_format)
                width = max(16, min(32, len(str(column_name)) + 4))
                worksheet.set_column(column_index, column_index, width)

        summary_sheet = writer.sheets["Summary"]
        summary_sheet.set_column("B:B", 24, money_format)

        details_sheet = writer.sheets["Package Details"]
        money_columns = [
            package_details.columns.get_loc(column)
            for column in package_details.columns
            if column not in {"package", "status"}
        ]
        for column_index in money_columns:
            details_sheet.set_column(column_index, column_index, 20, money_format)

    output.seek(0)
    return output.getvalue()
